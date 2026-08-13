% Main PCXMC Input Generation Script
% The following code produces the input data for PCXMC based on scan parameters
%
% This script calculates sub-field coordinates, validates them against phantom
% geometry, and generates the final input format required by PCXMC software.
%
% PCXMC MATLAB code by Aaron Fetin. Revised July 2022.

%% INPUT DATA SECTION
% All scan parameters are defined in this section
% Modify these values according to your specific protocol requirements

%%%%%%%%%%%%%%%%% INPUT DATA  %%%%%%%%%%%%%%%%%
% Phantom position details
iso = [-2.2; 1.2]; % Isocentre coordinate (x,y), relative to the geometrical centre of the phantom in the transverse slice (cm)
z = 0; % Sup-Inf offset (cm) - vertical displacement from isocentre
arms = 0; % Binary value used to represent if the arms are included in the phantom within PCXMC. 0 = no, 1 = yes.

% Scan parameters
UID = 1; % Dummy value for patient ID (required by PCXMC format)
kV = 125; % Tube voltage (kV)
FRD = 100; % Distance from the source to the reference point (iso) (cm)
headScan = 1; % Used to alter computation for head scans. For head scans enter 1 or "true", else for body scans enter 0 or "false".
startingAngle = 0; % Starting gantry angle in degrees (0-360)
finalAngle = 360; % Final gantry angle in degrees (0-360)
numAnglesSimmed = 8; % Number of projections/angles to be used in the simulation
numAnglesTrue = 360; % Number of projections/angles in the actual scan
oblique = 0; % Used by PCXMC to simulate oblique angles (0 = no obliquity)

% Sub-field configuration
% Coordinates defined at gantry angle 0
% Format: [X1, X2, X3, ...; Y1, Y2, Y3, ...]
subFieldCoords = [0, 0, 0, 0, 0, 0, 0; -15, -10, -5, 0, 5, 10, 15]; % Sub-field coordinates (cm)
subFieldWidths = [5, 5, 5, 5, 5, 5, 5]; % Width of each sub-field at each sub-field coordinate (cm)
width = 20.6; % Width of the field at isocentre in the sup-inf direction (cm)

% Dose parameters
% Air kerma per projection scaled by actual vs simulated projections
kerma = (numAnglesTrue/numAnglesSimmed) .* [0.1, 0.2, 0.5, 1, 0.5, 0.2, 0.1]; % Air kerma per projection at each sub-field coordinate (mGy)
filtration = [0.1, 0.2, 0.5, 1, 0.5, 0.2, 0.1]; % Total filtration at each sub-field coordinate (mm Al)

% Phantom geometry details
pWidth = 15; % Dual variable: If headScan = false, this represents the phantom's body width (cm). If headScan = true, anterior radius of phantom's head (cm)
pDepth = 15; % Phantom's body depth (cm)
pWidthTemp = pWidth; % Temporary storage for destructive use
pDepthTemp = pDepth; % Temporary storage for destructive use
pHeadRadii2 = 13; % If headScan = true, posterior radius of phantom's head (cm)
height = 172; % Phantom's height (cm)
mass = 95; % Phantom's mass (kg)
age = 30; % Phantom's age (years)

% Processing options
plotting = true; % Setting false will disable diagnostic graphs
interpolation = false; % Setting true will enable linear interpolation of kerma and filtration for points that have been shifted
resolutionScaling = false; % Can be used to scale the resolution of the entered sub-field data up or down to a user defined number using linear interpolation
numSubFields = 11; % The number of sub-field coordinates to scale to. Value is only used if resolution scaling is true. Odd numbers are recommended to ensure a point is calculated on CAX
%%%%%%%%%%%%%%%%% INPUT DATA END  %%%%%%%%%%%%%%%%%

%% GANTRY ANGLE CALCULATION
% Calculate the gantry angles to be simulated based on scan parameters

% Determine angle step based on rotation type
if mod(finalAngle-startingAngle, 360) == 0
    % If the rotation is a closed loop (360 degrees), the final angle should not equal initial angle
    dA = (finalAngle-startingAngle)/numAnglesSimmed; % Gantry angle interval
    angles = startingAngle:dA:finalAngle-dA; % Gantry angle array
else
    % Else if the rotation is a partial arc, include the final angle
    dA = (finalAngle-startingAngle)/(numAnglesSimmed-1); % Gantry angle interval
    angles = startingAngle:dA:finalAngle; % Gantry angle array
end

% Ensure angles are within -360 to +360 range for calculation purposes
angles = WrapTo360(angles);

%% RESOLUTION SCALING
% Apply resolution scaling if enabled to increase/decrease sub-field density

if resolutionScaling == true
    % Use resScale function to interpolate sub-field data
    [subFieldCoords, subFieldWidths, kerma, filtration] = resScale(subFieldCoords, subFieldWidths, kerma, filtration, numSubFields);
else
    % Use original resolution
    numSubFields = size(subFieldCoords, 2); % Number of sub-fields
end

%% SUB-FIELD COORDINATE CALCULATION
% Calculate coordinates of sub-fields at all gantry angles using rotation

% Preallocate matrix for all sub-field coordinates
Coords = zeros(2, numAnglesSimmed*numSubFields); % 2xN matrix [X; Y]

% Calculate coordinates using 2D rotation matrix
% Rotation matrix: [cos(θ) -sin(θ); sin(θ) cos(θ)]
j = 1; % Index for iterating through Coords matrix
for n = angles % Loop through each gantry angle
    for i = 1:numSubFields % Loop through each sub-field
        % Apply rotation and translation (add isocentre offset)
        Coords(:, j) = [cosd(n), -sind(n); sind(n), cosd(n)] * subFieldCoords(:, i) + iso;
        j = j + 1; % Move to next coordinate slot
    end
end

%% PHANTOM GEOMETRY PROCESSING
% Process sub-fields to ensure they are within phantom boundaries
% This section handles cases where sub-fields extend beyond the phantom

% Preallocate arrays for final results
XCoordsFinal = zeros(numSubFields*numAnglesSimmed); % Final x-coordinates
YCoordsFinal = zeros(numSubFields*numAnglesSimmed + 2*numAnglesSimmed); % Final y-coordinates (with buffer)
FiltFinal = zeros(numSubFields*numAnglesSimmed); % Final filtration values
KermaFinal = zeros(numSubFields*numAnglesSimmed); % Final air kerma values
sFWFinal = zeros(numSubFields*numAnglesSimmed); % Final sub-field widths
anglesFinal = zeros(numSubFields*numAnglesSimmed); % Final gantry angles
anglesTemp = zeros(numSubFields*numAnglesSimmed); % Temporary angle storage
sF = zeros(numSubFields*numAnglesSimmed); % Temporary sub-field widths

% Initialize counters
nD = 0; % Total number of valid data points after processing
nDI = 0; % Number of data points per gantry angle (intermittent)
aC = 0; % Angle counter for indexing

% Main processing loop - check each sub-field against phantom geometry
for n = 1:numSubFields:numAnglesSimmed*numSubFields % Loop through angles
    aC = aC + 1; % Increment angle counter
    for k = 1:numSubFields % Loop through sub-fields for this angle
        j = n + k - 1; % Calculate global index
        
        % Adjust phantom dimensions for head scans based on y-coordinate
        if headScan == true
            if Coords(2, j) > 0
                % Posterior head region
                pWidthTemp = pHeadRadii2;
                pDepthTemp = pWidthTemp;
            else
                % Anterior head region
                pWidthTemp = pWidth;
                pDepthTemp = pDepth;
            end
        end
        
        % Store temporary values
        anglesTemp(j) = angles(aC);
        sF(j) = subFieldWidths(k);
        
        % Check if coordinate is within phantom ellipse
        if withinEllipse(pWidthTemp, pDepthTemp, [Coords(1, j), Coords(2, j)]) == true
            % Coordinate is inside phantom - use as-is
            nD = nD + 1;
            XCoordsFinal(nD) = Coords(1, j);
            YCoordsFinal(nD) = Coords(2, j);
            FiltFinal(nD) = filtration(k);
            KermaFinal(nD) = kerma(k);
            sFWFinal(nD) = subFieldWidths(k);
            anglesFinal(nD) = angles(aC);
            
        else
            % Coordinate is outside phantom - check if field edge intersects
            if k == 1
                % First sub-field - check next sub-field
                if withinEllipse(pWidthTemp, pDepthTemp, [Coords(1, j+1), Coords(2, j+1)]) == true
                    x = subFieldIntersection([Coords(1, j), Coords(1, j+1)], [Coords(2, j), Coords(2, j+1)], subFieldWidths(k), angles(aC), -1);
                    if withinEllipse(pWidthTemp, pDepthTemp, [x(1), x(2)]) == true
                        p = findIntersections(pWidthTemp, pDepthTemp, angles(aC), [Coords(1, j), Coords(1, j+1)], [Coords(2, j), Coords(2, j+1)]);
                        nD = nD + 1;
                        XCoordsFinal(nD) = p(1,1);
                        YCoordsFinal(nD) = p(2,1);
                        sFWFinal(nD) = 2*sqrt((p(1,1)-x(1))^2 + (p(2,1)-x(2))^2);
                        anglesFinal(nD) = angles(aC);
                        
                        if interpolation == true
                            d1 = sqrt((Coords(1, j+1)-Coords(1, j))^2 + (Coords(2, j+1)-Coords(2, j))^2);
                            d2 = sqrt((p(1,1)-Coords(1, j))^2 + (p(2,1)-Coords(2, j))^2);
                            m1 = (kerma(k+1)-kerma(k))/d1;
                            m2 = (filtration(k+1)-filtration(k))/d1;
                            KermaFinal(nD) = kerma(k) + m1*d2;
                            FiltFinal(nD) = filtration(k) + m2*d2;
                        else
                            FiltFinal(nD) = filtration(k);
                            KermaFinal(nD) = kerma(k);
                        end
                    end
                end
                
            elseif k == numSubFields
                % Last sub-field - check previous sub-field
                if withinEllipse(pWidthTemp, pDepthTemp, [Coords(1, j-1), Coords(2, j-1)]) == true
                    x = subFieldIntersection([Coords(1, j), Coords(1, j-1)], [Coords(2, j), Coords(2, j-1)], subFieldWidths(k), angles(aC), 1);
                    if withinEllipse(pWidthTemp, pDepthTemp, [x(1), x(2)]) == true
                        p = findIntersections(pWidthTemp, pDepthTemp, angles(aC), [Coords(1, j), Coords(1, j-1)], [Coords(2, j), Coords(2, j-1)]);
                        nD = nD + 1;
                        XCoordsFinal(nD) = p(1,2);
                        YCoordsFinal(nD) = p(2,2);
                        sFWFinal(nD) = 2*sqrt((p(1,2)-x(1))^2 + (p(2,2)-x(2))^2);
                        anglesFinal(nD) = angles(aC);
                        
                        if interpolation == true
                            d1 = sqrt((Coords(1, j)-Coords(1, j-1))^2 + (Coords(2, j)-Coords(2, j-1))^2);
                            d2 = sqrt((p(1,2)-Coords(1, j))^2 + (p(2,2)-Coords(2, j))^2);
                            m1 = (kerma(k-1)-kerma(k))/d1;
                            m2 = (filtration(k-1)-filtration(k))/d1;
                            KermaFinal(nD) = kerma(k) + m1*d2;
                            FiltFinal(nD) = filtration(k) + m2*d2;
                        else
                            FiltFinal(nD) = filtration(k);
                            KermaFinal(nD) = kerma(k);
                        end
                    end
                end
                
            else
                % Middle sub-field - check both adjacent sub-fields
                if withinEllipse(pWidthTemp, pDepthTemp, [Coords(1, j+1), Coords(2, j+1)]) == true
                    x = subFieldIntersection([Coords(1, j), Coords(1, j+1)], [Coords(2, j), Coords(2, j+1)], subFieldWidths(k), angles(aC), -1);
                    if withinEllipse(pWidthTemp, pDepthTemp, [x(1), x(2)]) == true
                        p = findIntersections(pWidthTemp, pDepthTemp, angles(aC), [Coords(1, j), Coords(1, j+1)], [Coords(2, j), Coords(2, j+1)]);
                        nD = nD + 1;
                        XCoordsFinal(nD) = p(1,1);
                        YCoordsFinal(nD) = p(2,1);
                        sFWFinal(nD) = 2*sqrt((p(1,1)-x(1))^2 + (p(2,1)-x(2))^2);
                        anglesFinal(nD) = angles(aC);
                        
                        if interpolation == true
                            d1 = sqrt((Coords(1, j+1)-Coords(1, j))^2 + (Coords(2, j+1)-Coords(2, j))^2);
                            d2 = sqrt((p(1,1)-Coords(1, j))^2 + (p(2,1)-Coords(2, j))^2);
                            m1 = (kerma(k+1)-kerma(k))/d1;
                            m2 = (filtration(k+1)-filtration(k))/d1;
                            KermaFinal(nD) = kerma(k) + m1*d2;
                            FiltFinal(nD) = filtration(k) + m2*d2;
                        else
                            FiltFinal(nD) = filtration(k);
                            KermaFinal(nD) = kerma(k);
                        end
                    end
                    
                elseif withinEllipse(pWidthTemp, pDepthTemp, [Coords(1, j-1), Coords(2, j-1)]) == true
                    x = subFieldIntersection([Coords(1, j), Coords(1, j-1)], [Coords(2, j), Coords(2, j-1)], subFieldWidths(k), angles(aC), 1);
                    if withinEllipse(pWidthTemp, pDepthTemp, [x(1), x(2)]) == true
                        p = findIntersections(pWidthTemp, pDepthTemp, angles(aC), [Coords(1, j), Coords(1, j-1)], [Coords(2, j), Coords(2, j-1)]);
                        nD = nD + 1;
                        XCoordsFinal(nD) = p(1,2);
                        YCoordsFinal(nD) = p(2,2);
                        sFWFinal(nD) = 2*sqrt((p(1,2)-x(1))^2 + (p(2,2)-x(2))^2);
                        anglesFinal(nD) = angles(aC);
                        
                        if interpolation == true
                            d1 = sqrt((Coords(1, j)-Coords(1, j-1))^2 + (Coords(2, j)-Coords(2, j-1))^2);
                            d2 = sqrt((p(1,2)-Coords(1, j))^2 + (p(2,2)-Coords(2, j))^2);
                            m1 = (kerma(k-1)-kerma(k))/d1;
                            m2 = (filtration(k-1)-filtration(k))/d1;
                            KermaFinal(nD) = kerma(k) + m1*d2;
                            FiltFinal(nD) = filtration(k) + m2*d2;
                        else
                            FiltFinal(nD) = filtration(k);
                            KermaFinal(nD) = kerma(k);
                        end
                    end
                end
            end
        end
    end
    
    % Record number of points for this angle
    nDI = [nDI; nD - sum(nDI)];
end

% Clean up arrays - remove unused elements
nDI = nDI(2:end); % Remove leading zero
XCoordsFinal = XCoordsFinal(1:nD); % Truncate to actual size
YCoordsFinal = YCoordsFinal(1:nD);
FiltFinal = FiltFinal(1:nD);
KermaFinal = KermaFinal(1:nD);
sFWFinal = sFWFinal(1:nD);
anglesFinal = anglesFinal(1:nD);

%% DIAGNOSTIC PLOTTING
% Generate visualization plots if enabled

if plotting == true
    % Calculate sub-field boundaries for visualization
    
    % Original sub-field boundaries
    [Xs, Ys] = subFieldIntersections(Coords(1,:), Coords(2,:), sF, anglesTemp, ones(numAnglesSimmed, 1)*numel(subFieldWidths));
    
    % Final processed sub-field boundaries
    [Xfs, Yfs] = subFieldIntersections(XCoordsFinal, YCoordsFinal, sFWFinal, anglesFinal, nDI);
    
    % Generate phantom boundary coordinates
    if headScan == false
        % Body scan - simple ellipse
        theta = 0:0.01:2*pi;
        r = sqrt(((pDepth^2)*(pWidth^2))./(pDepth^2*cos(theta).^2 + pWidth^2*sin(theta).^2));
        x = r.*cos(theta);
        y = r.*sin(theta);
    else
        % Head scan - composite shape (anterior and posterior ellipses)
        theta = 0.01:0.01:pi-0.01;
        r = sqrt(((pHeadRadii2^2)*(pHeadRadii2^2))./(pHeadRadii2^2*cos(theta).^2 + pHeadRadii2^2*sin(theta).^2));
        x = r.*cos(theta);
        y = r.*sin(theta);
        
        theta2 = pi:0.01:2*pi;
        r2 = sqrt(((pDepth^2)*(pWidth^2))./(pDepth^2*cos(theta2).^2 + pWidth^2*sin(theta2).^2));
        x2 = r2.*cos(theta2);
        y2 = r2.*sin(theta2);
        
        x = [x, x2, x(1)];
        y = [y, y2, y(1)];
    end
    
    % Create diagnostic plots
    figure(1);
    plot(x, y, 'k', 'LineWidth', 4); % Phantom boundary
    hold on;
    plot(Xfs, Yfs, '.', 'MarkerSize', 1, 'Color', [0.2, 0.2, 1]); % Final sub-field boundaries
    plot(XCoordsFinal, YCoordsFinal, '.', 'MarkerSize', 4, 'Color', [1, 0.2, 0.2]); % Final sub-field centers
    grid on;
    legend('Phantom Boundary', 'Sub-field boundary', 'Sub-field centre');
    axis([-25 25 -25 25]);
    title('Amended Sub-fields');
    xlabel('Position (cm)');
    ylabel('Position (cm)');
    
    figure(2);
    plot(x, y, 'k', 'LineWidth', 4); % Phantom boundary
    hold on;
    plot(Xs, Ys, '.', 'MarkerSize', 1, 'Color', [0.2, 0.2, 1]); % Original sub-field boundaries
    plot(Coords(1,:), Coords(2,:), '.', 'MarkerSize', 4, 'Color', [1, 0.2, 0.2]); % Original sub-field centers
    grid on;
    legend('Phantom Boundary', 'Sub-field boundary', 'Sub-field centre');
    axis([-25 25 -25 25]);
    title('Original Sub-fields');
    xlabel('Position (cm)');
    ylabel('Position (cm)');
end

%% PCXMC OUTPUT GENERATION
% Format data for PCXMC input file

% Transpose arrays to column vectors
XCoordsFinal = XCoordsFinal';
YCoordsFinal = YCoordsFinal';
FiltFinal = FiltFinal';
KermaFinal = KermaFinal';
sFWFinal = sFWFinal';
anglesFinal = round(anglesFinal', 12, 'significant'); % Round to prevent PCXMC errors

% Clear any existing PCXMCInput variable
clearvars PCXMCInput;

% Create PCXMC input matrix according to required format
% Column mapping follows PCXMC specification
PCXMCInput = zeros(length(XCoordsFinal), 20); % Initialize with zeros

% Map variables to PCXMC columns
PCXMCInput(:, 3) = anglesFinal; % Gantry angle (degrees)
PCXMCInput(:, 4) = oblique; % Oblique angle flag
PCXMCInput(:, 5) = UID; % Patient ID
PCXMCInput(:, 6) = height; % Patient height (cm)
PCXMCInput(:, 7) = mass; % Patient mass (kg)
PCXMCInput(:, 8) = age; % Patient age (years)
PCXMCInput(:, 9) = kV; % Tube voltage (kV)
PCXMCInput(:, 10) = FiltFinal; % Total filtration (mm Al)
PCXMCInput(:, 11) = 0; % Reserved field
PCXMCInput(:, 12) = FRD; % Focus-to-reference distance (cm)
PCXMCInput(:, 13) = sFWFinal; % Sub-field width (cm)
PCXMCInput(:, 14) = width; % Field width at isocentre (cm)
PCXMCInput(:, 15) = XCoordsFinal; % X-coordinate relative to phantom center (cm)
PCXMCInput(:, 16) = YCoordsFinal; % Y-coordinate relative to phantom center (cm)
PCXMCInput(:, 17) = z; % Z-coordinate (sup-inf offset) (cm)
PCXMCInput(:, 18) = arms; % Arms included flag (0/1)
PCXMCInput(:, 20) = KermaFinal; % Air kerma per projection (mGy)
PCXMCInput(:, 1) = 0; % Reserved field
PCXMCInput(:, 2) = 0; % Reserved field

% Display completion message
fprintf('PCXMC input generation complete.\n');
fprintf('Total valid sub-fields: %d\n', length(XCoordsFinal));
fprintf('Data ready for PCXMC input file.\n');
