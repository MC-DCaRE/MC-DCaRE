%% PCXMC MATLAB Code - Refactored Version
% Aaron Fetin, Revised July 2022
% Refactored for improved readability and maintainability

%% Load Configuration
config = load_protocol_config('protocol_config.m');

%% Initialize Processing
[angles, subFieldCoords, subFieldWidths, kerma, filtration] = initialize_processing(config);

%% Calculate Sub-field Coordinates
Coords = calculate_subfield_coordinates(angles, subFieldCoords, config.iso, config.numSubFields);

%% Process Phantom Geometry
[XCoordsFinal, YCoordsFinal, FiltFinal, KermaFinal, sFWFinal, anglesFinal, nDI] = ...
    process_phantom_geometry(Coords, angles, subFieldWidths, kerma, filtration, config);

%% Generate Plots (if enabled)
if config.plotting
    generate_plots(XCoordsFinal, YCoordsFinal, sFWFinal, anglesFinal, nDI, ...
                  Coords, subFieldWidths, angles, config);
end

%% Generate PCXMC Output
PCXMCInput = generate_pcxmc_output(XCoordsFinal, YCoordsFinal, FiltFinal, ...
                                  KermaFinal, sFWFinal, anglesFinal, config);

%% Display Results
fprintf('Processing complete. %d valid sub-fields generated.\n', length(XCoordsFinal));
fprintf('Data ready for PCXMC input.\n');



%% Helper Functions

function [angles, subFieldCoords, subFieldWidths, kerma, filtration] = initialize_processing(config)
% Initialize processing parameters and scale resolution if needed
    
    % Calculate gantry angles
    angles = calculate_gantry_angles(config.startingAngle, config.finalAngle, ...
                                   config.numAnglesSimmed);
    
    % Apply resolution scaling if enabled
    if config.resolutionScaling
        [subFieldCoords, subFieldWidths, kerma, filtration] = ...
            resScale(config.subFieldCoords, config.subFieldWidths, ...
                    config.kerma, config.filtration, config.numSubFields);
    else
        subFieldCoords = config.subFieldCoords;
        subFieldWidths = config.subFieldWidths;
        kerma = config.kerma;
        filtration = config.filtration;
    end
end

function angles = calculate_gantry_angles(startAngle, endAngle, numAngles)
% Calculate gantry angles for simulation
    
    if mod(endAngle - startAngle, 360) == 0
        % Full rotation - exclude final angle
        dA = (endAngle - startAngle) / numAngles;
        angles = startAngle:dA:endAngle-dA;
    else
        % Partial arc - include final angle
        dA = (endAngle - startAngle) / (numAngles - 1);
        angles = startAngle:dA:endAngle;
    end
    
    angles = WrapTo360(angles);
end

function Coords = calculate_subfield_coordinates(angles, subFieldCoords, iso, numSubFields)
% Calculate sub-field coordinates for all angles
    
    Coords = zeros(2, length(angles) * numSubFields);
    
    idx = 1;
    for angle = angles
        rotationMatrix = [cosd(angle), -sind(angle); sind(angle), cosd(angle)];
        
        for i = 1:numSubFields
            Coords(:, idx) = rotationMatrix * subFieldCoords(:, i) + iso;
            idx = idx + 1;
        end
    end
end

function [XCoordsFinal, YCoordsFinal, FiltFinal, KermaFinal, sFWFinal, anglesFinal, nDI] = ...
    process_phantom_geometry(Coords, angles, subFieldWidths, kerma, filtration, config)
% Process phantom geometry and filter valid sub-fields
    
    % Preallocate arrays
    maxPoints = length(angles) * length(subFieldWidths);
    XCoordsFinal = zeros(maxPoints, 1);
    YCoordsFinal = zeros(maxPoints, 1);
    FiltFinal = zeros(maxPoints, 1);
    KermaFinal = zeros(maxPoints, 1);
    sFWFinal = zeros(maxPoints, 1);
    anglesFinal = zeros(maxPoints, 1);
    
    % Initialize counters
    nD = 0;
    nDI = [];
    angleIndex = 0;
    
    % Process each angle
    for angleStart = 1:length(subFieldWidths):length(angles)*length(subFieldWidths)
        angleIndex = angleIndex + 1;
        currentAngle = angles(angleIndex);
        
        % Process each sub-field for this angle
        for subFieldIdx = 1:length(subFieldWidths)
            globalIdx = angleStart + subFieldIdx - 1;
            
            % Get phantom dimensions based on scan type
            [pWidth, pDepth] = get_phantom_dimensions(config, Coords(2, globalIdx));
            
            % Check if coordinate is within phantom
            if withinEllipse(pWidth, pDepth, [Coords(1, globalIdx), Coords(2, globalIdx)])
                [nD, XCoordsFinal, YCoordsFinal, FiltFinal, KermaFinal, sFWFinal, anglesFinal] = ...
                    add_valid_subfield(nD, Coords(:, globalIdx), subFieldWidths(subFieldIdx), ...
                                      kerma(subFieldIdx), filtration(subFieldIdx), ...
                                      currentAngle, XCoordsFinal, YCoordsFinal, ...
                                      FiltFinal, KermaFinal, sFWFinal, anglesFinal);
            else
                % Check adjacent sub-fields for intersection
                [nD, XCoordsFinal, YCoordsFinal, FiltFinal, KermaFinal, sFWFinal, anglesFinal] = ...
                    process_subfield_intersection(nD, globalIdx, subFieldIdx, Coords, ...
                                                subFieldWidths, kerma, filtration, ...
                                                currentAngle, pWidth, pDepth, config, ...
                                                XCoordsFinal, YCoordsFinal, FiltFinal, ...
                                                KermaFinal, sFWFinal, anglesFinal);
            end
        end
        
        nDI = [nDI; nD - sum(nDI)];
    end
    
    % Truncate arrays to actual size
    nDI = nDI(2:end);
    XCoordsFinal = XCoordsFinal(1:nD);
    YCoordsFinal = YCoordsFinal(1:nD);
    FiltFinal = FiltFinal(1:nD);
    KermaFinal = KermaFinal(1:nD);
    sFWFinal = sFWFinal(1:nD);
    anglesFinal = anglesFinal(1:nD);
end

function [pWidth, pDepth] = get_phantom_dimensions(config, yCoord)
% Get appropriate phantom dimensions based on scan type and y-coordinate
    
    if config.headScan
        if yCoord > 0
            % Posterior head
            pWidth = config.pHeadRadii2;
            pDepth = config.pHeadRadii2;
        else
            % Anterior head
            pWidth = config.pWidth;
            pDepth = config.pDepth;
        end
    else
        % Body scan
        pWidth = config.pWidth;
        pDepth = config.pDepth;
    end
end

function [nD, XCoordsFinal, YCoordsFinal, FiltFinal, KermaFinal, sFWFinal, anglesFinal] = ...
    add_valid_subfield(nD, coord, width, kermaVal, filtVal, angle, ...
                      XCoordsFinal, YCoordsFinal, FiltFinal, KermaFinal, sFWFinal, anglesFinal)
% Add a valid sub-field to the final arrays
    
    nD = nD + 1;
    XCoordsFinal(nD) = coord(1);
    YCoordsFinal(nD) = coord(2);
    FiltFinal(nD) = filtVal;
    KermaFinal(nD) = kermaVal;
    sFWFinal(nD) = width;
    anglesFinal(nD) = angle;
end

function [nD, XCoordsFinal, YCoordsFinal, FiltFinal, KermaFinal, sFWFinal, anglesFinal] = ...
    process_subfield_intersection(nD, globalIdx, subFieldIdx, Coords, subFieldWidths, ...
                                kerma, filtration, currentAngle, pWidth, pDepth, config, ...
                                XCoordsFinal, YCoordsFinal, FiltFinal, KermaFinal, sFWFinal, anglesFinal)
% Process sub-field intersection with phantom boundary
    
    numSubFields = length(subFieldWidths);
    
    % Check adjacent sub-fields
    if subFieldIdx == 1
        % First sub-field - check next
        if globalIdx + 1 <= size(Coords, 2) && ...
           withinEllipse(pWidth, pDepth, [Coords(1, globalIdx+1), Coords(2, globalIdx+1)])
            [nD, XCoordsFinal, YCoordsFinal, FiltFinal, KermaFinal, sFWFinal, anglesFinal] = ...
                handle_boundary_intersection(nD, globalIdx, globalIdx+1, subFieldIdx, ...
                                           Coords, subFieldWidths, kerma, filtration, ...
                                           currentAngle, pWidth, pDepth, config, ...
                                           XCoordsFinal, YCoordsFinal, FiltFinal, ...
                                           KermaFinal, sFWFinal, anglesFinal, -1);
        end
    elseif subFieldIdx == numSubFields
        % Last sub-field - check previous
        if withinEllipse(pWidth, pDepth, [Coords(1, globalIdx-1), Coords(2, globalIdx-1)])
            [nD, XCoordsFinal, YCoordsFinal, FiltFinal, KermaFinal, sFWFinal, anglesFinal] = ...
                handle_boundary_intersection(nD, globalIdx, globalIdx-1, subFieldIdx, ...
                                           Coords, subFieldWidths, kerma, filtration, ...
                                           currentAngle, pWidth, pDepth, config, ...
                                           XCoordsFinal, YCoordsFinal, FiltFinal, ...
                                           KermaFinal, sFWFinal, anglesFinal, 1);
        end
    else
        % Middle sub-field - check both directions
        if withinEllipse(pWidth, pDepth, [Coords(1, globalIdx+1), Coords(2, globalIdx+1)])
            [nD, XCoordsFinal, YCoordsFinal, FiltFinal, KermaFinal, sFWFinal, anglesFinal] = ...
                handle_boundary_intersection(nD, globalIdx, globalIdx+1, subFieldIdx, ...
                                           Coords, subFieldWidths, kerma, filtration, ...
                                           currentAngle, pWidth, pDepth, config, ...
                                           XCoordsFinal, YCoordsFinal, FiltFinal, ...
                                           KermaFinal, sFWFinal, anglesFinal, -1);
        elseif withinEllipse(pWidth, pDepth, [Coords(1, globalIdx-1), Coords(2, globalIdx-1)])
            [nD, XCoordsFinal, YCoordsFinal, FiltFinal, KermaFinal, sFWFinal, anglesFinal] = ...
                handle_boundary_intersection(nD, globalIdx, globalIdx-1, subFieldIdx, ...
                                           Coords, subFieldWidths, kerma, filtration, ...
                                           currentAngle, pWidth, pDepth, config, ...
                                           XCoordsFinal, YCoordsFinal, FiltFinal, ...
                                           KermaFinal, sFWFinal, anglesFinal, 1);
        end
    end
end

function [nD, XCoordsFinal, YCoordsFinal, FiltFinal, KermaFinal, sFWFinal, anglesFinal] = ...
    handle_boundary_intersection(nD, currentIdx, adjacentIdx, subFieldIdx, Coords, ...
                               subFieldWidths, kerma, filtration, currentAngle, ...
                               pWidth, pDepth, config, XCoordsFinal, YCoordsFinal, ...
                               FiltFinal, KermaFinal, sFWFinal, anglesFinal, direction)
% Handle intersection with phantom boundary
    
    % Find boundary intersection
    x = subFieldIntersection([Coords(1, currentIdx), Coords(1, adjacentIdx)], ...
                           [Coords(2, currentIdx), Coords(2, adjacentIdx)], ...
                           subFieldWidths(subFieldIdx), currentAngle, direction);
    
    if withinEllipse(pWidth, pDepth, [x(1), x(2)])
        % Find intersection with phantom surface
        p = findIntersections(pWidth, pDepth, currentAngle, ...
                            [Coords(1, currentIdx), Coords(1, adjacentIdx)], ...
                            [Coords(2, currentIdx), Coords(2, adjacentIdx)]);
        
        nD = nD + 1;
        
        % Determine which intersection point to use
        if direction == -1
            XCoordsFinal(nD) = p(1,1);
            YCoordsFinal(nD) = p(2,1);
            newWidth = 2 * sqrt((p(1,1) - x(1))^2 + (p(2,1) - x(2))^2);
        else
            XCoordsFinal(nD) = p(1,2);
            YCoordsFinal(nD) = p(2,2);
            newWidth = 2 * sqrt((p(1,2) - x(1))^2 + (p(2,2) - x(2))^2);
        end
        
        sFWFinal(nD) = newWidth;
        anglesFinal(nD) = currentAngle;
        
        % Handle interpolation if enabled
        if config.interpolation
            [kermaVal, filtVal] = interpolate_values(currentIdx, adjacentIdx, subFieldIdx, ...
                                                   Coords, kerma, filtration, ...
                                                   p(1,:), p(2,:), direction);
            KermaFinal(nD) = kermaVal;
            FiltFinal(nD) = filtVal;
        else
            KermaFinal(nD) = kerma(subFieldIdx);
            FiltFinal(nD) = filtration(subFieldIdx);
        end
    end
end

function [kermaVal, filtVal] = interpolate_values(currentIdx, adjacentIdx, subFieldIdx, ...
                                                Coords, kerma, filtration, px, py, direction)
% Interpolate kerma and filtration values based on new position
    
    d1 = sqrt((Coords(1, adjacentIdx) - Coords(1, currentIdx))^2 + ...
              (Coords(2, adjacentIdx) - Coords(2, currentIdx))^2);
    
    if direction == -1
        d2 = sqrt((px(1) - Coords(1, currentIdx))^2 + ...
                  (py(1) - Coords(2, currentIdx))^2);
        m1 = (kerma(subFieldIdx + 1) - kerma(subFieldIdx)) / d1;
        m2 = (filtration(subFieldIdx + 1) - filtration(subFieldIdx)) / d1;
    else
        d2 = sqrt((px(2) - Coords(1, currentIdx))^2 + ...
                  (py(2) - Coords(2, currentIdx))^2);
        m1 = (kerma(subFieldIdx - 1) - kerma(subFieldIdx)) / d1;
        m2 = (filtration(subFieldIdx - 1) - filtration(subFieldIdx)) / d1;
    end
    
    kermaVal = kerma(subFieldIdx) + m1 * d2;
    filtVal = filtration(subFieldIdx) + m2 * d2;
end

function generate_plots(XCoordsFinal, YCoordsFinal, sFWFinal, anglesFinal, nDI, ...
                       Coords, subFieldWidths, angles, config)
% Generate diagnostic plots
    
    [Xs, Ys] = subFieldIntersections(Coords(1,:), Coords(2,:), subFieldWidths, ...
                                   angles, ones(length(angles), 1) * length(subFieldWidths));
    [Xfs, Yfs] = subFieldIntersections(XCoordsFinal, YCoordsFinal, sFWFinal, ...
                                     anglesFinal, nDI);
    
    % Plot phantom boundary
    [x, y] = generate_phantom_boundary(config);
    
    % Create plots
    figure(1);
    plot(x, y, 'k', 'LineWidth', 4);
    hold on;
    plot(Xfs, Yfs, '.', 'MarkerSize', 1, 'Color', [0.2, 0.2, 1]);
    plot(XCoordsFinal, YCoordsFinal, '.', 'MarkerSize', 4, 'Color', [1, 0.2, 0.2]);
    grid on;
    legend('Phantom Boundary', 'Sub-field boundary', 'Sub-field centre');
    axis([-25 25 -25 25]);
    title('Amended Sub-fields');
    xlabel('Position (cm)');
    ylabel('Position (cm)');
    
    figure(2);
    plot(x, y, 'k', 'LineWidth', 4);
    hold on;
    plot(Xs, Ys, '.', 'MarkerSize', 1, 'Color', [0.2, 0.2, 1]);
    plot(Coords(1,:), Coords(2,:), '.', 'MarkerSize', 4, 'Color', [1, 0.2, 0.2]);
    grid on;
    legend('Phantom Boundary', 'Sub-field boundary', 'Sub-field centre');
    axis([-25 25 -25 25]);
    title('Original Sub-fields');
    xlabel('Position (cm)');
    ylabel('Position (cm)');
end

function [x, y] = generate_phantom_boundary(config)
% Generate phantom boundary coordinates for plotting
    
    if ~config.headScan
        % Body scan - ellipse
        theta = 0:0.01:2*pi;
        r = sqrt(((config.pDepth^2) * (config.pWidth^2)) ./ ...
                (config.pDepth^2 * cos(theta).^2 + config.pWidth^2 * sin(theta).^2));
        x = r .* cos(theta);
        y = r .* sin(theta);
    else
        % Head scan - composite shape
        theta = 0.01:0.01:pi-0.01;
        r = sqrt(((config.pHeadRadii2^2) * (config.pHeadRadii2^2)) ./ ...
                (config.pHeadRadii2^2 * cos(theta).^2 + config.pHeadRadii2^2 * sin(theta).^2));
        x = r .* cos(theta);
        y = r .* sin(theta);
        
        theta2 = pi:0.01:2*pi;
        r2 = sqrt(((config.pDepth^2) * (config.pWidth^2)) ./ ...
                 (config.pDepth^2 * cos(theta2).^2 + config.pWidth^2 * sin(theta2).^2));
        x2 = r2 .* cos(theta2);
        y2 = r2 .* sin(theta2);
        
        x = [x, x2, x(1)];
        y = [y, y2, y(1)];
    end
end

function PCXMCInput = generate_pcxmc_output(XCoordsFinal, YCoordsFinal, FiltFinal, ...
                                           KermaFinal, sFWFinal, anglesFinal, config)
% Generate final PCXMC input data
    
    % Transpose arrays
    XCoordsFinal = XCoordsFinal';
    YCoordsFinal = YCoordsFinal';
    FiltFinal = FiltFinal';
    KermaFinal = KermaFinal';
    sFWFinal = sFWFinal';
    anglesFinal = round(anglesFinal', 12, 'significant');
    
    % Initialize output array
    PCXMCInput = zeros(length(XCoordsFinal), 20);
    
    % Map to PCXMC format
    PCXMCInput(:, 3) = anglesFinal;
    PCXMCInput(:, 4) = config.oblique;
    PCXMCInput(:, 5) = 1; % UID
    PCXMCInput(:, 6) = config.height;
    PCXMCInput(:, 7) = config.mass;
    PCXMCInput(:, 8) = config.age;
    PCXMCInput(:, 9) = config.kV;
    PCXMCInput(:, 10) = FiltFinal;
    PCXMCInput(:, 11) = 0;
    PCXMCInput(:, 12) = config.FRD;
    PCXMCInput(:, 13) = sFWFinal;
    PCXMCInput(:, 14) = config.width;
    PCXMCInput(:, 15) = XCoordsFinal;
    PCXMCInput(:, 16) = YCoordsFinal;
    PCXMCInput(:, 17) = config.z;
    PCXMCInput(:, 18) = config.arms;
    PCXMCInput(:, 20) = KermaFinal;
    PCXMCInput(:, 1) = 0;
    PCXMCInput(:, 2) = 0;
end
