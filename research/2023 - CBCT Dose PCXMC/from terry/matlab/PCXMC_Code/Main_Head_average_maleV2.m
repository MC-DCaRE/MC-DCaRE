%The following code produces the input data for PCXMC based on the input


%An note onthe coordinate system for this code from the PCXMC 2.0 user 
%guide 
%‘Xref’, ‘Yref’ and ‘Zref’ are the coordinates of an arbitrary point inside 
%the phantom, through which the central axis of the x-ray beam is directed: 
%these data are used for specifying the location of the x-ray beam with 
%respect to the phantom. Choosing any point along the intended beam 
%centre-line will give same calculation results. The origin of the 
%phantom’s coordinate system is located at the centre of the bottom of the 
%phantom trunk section. The positive z-axis is directed upwards, the 
%positive y-axis to the back of the phantom, and the positive X-axis to the 
%left-hand side of the phantom.


%% PCXMC MATLAB code by Aaron Fetin. Revised July 2022.

%%%%%%%%%%%%%%%%% INPUT DATA  %%%%%%%%%%%%%%%%%
%Phantom position details
%get these manually from the PCXMC program, the z-distance in particular
%needs to be taken from the program
iso = [0; 0]; %Isocentre coordinate (x,y), relative to the geometrical centre of the phantom in the transverse slice (cm)
z = 85; %Sup-Inf offset (cm)(for head 85 gave higher dose than 88cm
arms = 1; %Binary value used to represent if the arms are included in the phantom within PCXMC. 0 = no, 1 = yes.

%makes the gantry rotate in the opposite direction
gantry_direction_though_360 = 0;

%Scan parameters
%protocol details used, see TrueBeamCBCTmodes.xlsx spreadsheet from JB
%head, 200 degrees, startsource 90 - stopsource 290 on the linac only, this
%translates into startangle 0 - stopangle 200 on the PCXMC coordinate
%system. total of 500 projections

UID = 1; %Dummy value for patient ID
kV = 100; %Tube voltage
FRD = 100; %Distance from the source to the reference point (iso) (cm)
headScan = 1; %Used to alter computation for head scans. For head scans enter 1 or "true", else for body scans enter 0 or "false.
startingAngle = 200; %Starting gantry angle in degrees
finalAngle = 0; %Final gantry angle in degrees
numAnglesSimmed = 20; %Number of projections/angles to be used in the simulation
numAnglesTrue = 500; %Number of projections/angles in the actual scan
oblique = 0; %Used by PCXMC to simulate oblique angles.
subFieldCoords = [0, 0, 0, 0, 0, 0, 0 ; -15, -10, -5, 0, 5, 10, 15]; %Sub-field coordinates defined a gantry 0, eg. [0, 0, 0, ... ; y1, y2, y3, ...] (coordinates of centres of sub-fields)
subFieldWidths = [5,5,5,5,5,5,5]; %Width of each sub-field at each sub-field coordinate (cm) (X-direction blades, <<<<CHECK THIS>>>>>)
width = 21.4; %Width of the field at isocentre in the sup-inf direction (cm) this is Y-blades on the source <<<<CHECK THIS>>>>>
kerma = (numAnglesTrue/numAnglesSimmed).*[0.0017,0.0053,0.0208,0.0297,0.0208,0.0053,0.0017]; %Air kerma per projection at each sub-field coordinate (mGy).
filtration = [15.07,26.3,15.97,11.43,15.97,26.3,15.07]; %Total filtration at each sub-field coordinate (mm Al)

%Phantom geometry details
%average male
%for head, 1.8m tall, 88kg, anterior radius of head 11cm, posterior radius
%7cm. however the lateral profile of the larger radius of the head does
%reduce in size meaning chooisng 11cm will put reference points out of the
%phantom.
%body, 1.8m tall, 88kg, A/P dimensions of body 22cm, Lateral 44cm

pWidth = 8; %Dual variable: If headScan = false , this represents the phantom's body width (cm). If headScan = true, anterior radius of phantom's head (cm)
pDepth = 8; %Phantom's body depth (cm), need to make these both the same for head????
pWidthTemp = pWidth; % Value as above for destructive use.
pDepthTemp = pDepth; % Value as above for destructive use.
pHeadRadii2 = 6; %If headScan = true, posterior radius of phantoms head (cm).
height = 180; %Phantom's height (cm)
mass = 88; %Phantom's mass (kg)
age = 30; %Phantom's age (years)

%Other Options
plotting = true; %Setting false will disable graphs
interpolation = false; % Setting true will enable linear interpolation of kerma and filtration for points that have been shifted. I.e. value is updated based on new sub-field location, rather than just shifted
resolutionScaling = false; %Can be used to scale the resolution of the entered sub-field data up or down to a user defined number. Uses linear interpolation. 
numSubFields = 11; %The number of sub-field coordinates to scale to. Value is only used if resolution scaling is true. Odd numbers are recommended to ensure a point is calculated on CAX
%%%%%%%%%%%%%%%%% INPUT DATA END  %%%%%%%%%%%%%%%%%

%%

%%%%%%%%%%%%%%%%% COMPUTE GANTRY ANGLES AND INITIAL SUB-FIELD COORDINATES  %%%%%%%%%%%%%%%%%

%First compute gantry angles to be simulated
if mod(finalAngle-startingAngle,360) == 0 %If the rotation is a closed loop the final angle should not equal initial angle.
    dA = (finalAngle-startingAngle)/numAnglesSimmed; %Gantry angle interval
    angles = startingAngle:dA:finalAngle-dA; %Gantry angle array
else % Else if the rotation is a partial arc, no restriction is placed on final angle.
    dA = (finalAngle-startingAngle)/(numAnglesSimmed-1); %Gantry angle interval
    angles = startingAngle:dA:finalAngle; %Gantry angle array
end

angles = WrapTo360(angles); %Ensures that gantry angles lie numerically between -360 and +360 for calculation purposes. E.g., 540 would be mapped to 180 due to equivalency 

%Resolution is scaled here if enabled
if resolutionScaling == true
   [subFieldCoords, subFieldWidths, kerma, filtration] = resScale(subFieldCoords, subFieldWidths, kerma, filtration, numSubFields);
else
    numSubFields = size(subFieldCoords,2); %Number of sub-fields
end

Coords = zeros(2,numAnglesSimmed*numSubFields); %Preallocated matrix for sub-field coordinates at each angle to be simulated.

%Calculate coordinates of sub-fields at gantry angles using 2D rotational matrix.
j = 1; %index for iterating sub-field coordinates matrix
for n = angles %Loop for angles
   for i = 1:numSubFields %Loop for subfields
       Coords(:,j) = [cosd(n), -sind(n); sind(n), cosd(n)]*subFieldCoords(:,i)+iso; %rotate subfield coordinates for each angle
       j = j+1; %Iterate sub-field coordinate matrix
   end
end

%%%%%%%%%%%%%%%%% COMPUTE GANTRY ANGLES AND INITIAL SUB-FIELD COORDINATES END %%%%%%%%%%%%%%%%%

%%

%%%%%%%%%%%%%%%%% AMMEND SUB-FIELDS BASED ON PHANTOM GEOMETRY %%%%%%%%%%%%%%%%%

%Preallocation of arrays.
XCoordsFinal = zeros(numSubFields*numAnglesSimmed); %Preallocate array for final x-axis coordinate
YCoordsFinal = zeros(numSubFields*numAnglesSimmed+2*numAnglesSimmed); %Preallocate array for final y-axis coordinate
FiltFinal = zeros(numSubFields*numAnglesSimmed); %Preallocate array for final total filtration values (mm Al)
KermaFinal = zeros(numSubFields*numAnglesSimmed); %Preallocate array for final air kerma values (mGy)
sFWFinal = zeros(numSubFields*numAnglesSimmed); %Preallocate array for final sub-field widths (cm)
anglesFinal = zeros(numSubFields*numAnglesSimmed); %Preallocate array for final gantry angles (degrees)
anglesTemp = zeros(numSubFields*numAnglesSimmed); %Preallocate array for temp gantry angles.
sF = zeros(numSubFields*numAnglesSimmed); 

nD = 0; %Is used to track the number of total data points that are included after determining if the coordinates are valid.
nDI = 0; %Tracks the number of data points for each gantry angle (nD intermittent)
aC = 0; %Is used for indexing gantry angles.

% The following set of nested loops are used to ammend the sub-fields based
% on the phantom geometry. If a point is inside the the phantom, it is
% fine. If it is outside, but some of the field extent is incident on the
% phantom, the point is updated to the surface of phantom to avoid PCXMC errors. 
% The air kerma and filtration values used are either those of the original point, 
% of they may be based on the new location by using linear interpolation if
% enabled above.

for n = 1:numSubFields:numAnglesSimmed*numSubFields %Loop for angles
    aC = aC+1; %Index for angles
    for k = 1:numSubFields %Loop for sub-fields, with k used as the index for sub-fields
        j = n+k-1;
        
        if headScan == true %Ammend phantom dimensions for headscans depending upon if coord is anterior or posterior.
            %TP comment - looks like row 2 of Coords (y-coordinate) is  
            %being used to determine anterior and posterior. If this is
            %true, if coords is >0 should determine anterior????
            if Coords(2,j) > 0
                pWidthTemp = pHeadRadii2;
                pDepthTemp = pWidthTemp;
            else
                pWidthTemp = pWidth;
                pDepthTemp = pDepth;
            end
        end
        
        anglesTemp(j) = angles(aC);
        sF(j) = subFieldWidths(k);
        if withinEllipse(pWidthTemp, pDepthTemp, [Coords(1, j), Coords(2, j)])==true %Check if the coordinate is within the ellipse
            nD = nD + 1; %Increment the number of data points included
            XCoordsFinal(nD) = Coords(1,j); %Add the x-coordinate to the final array
            YCoordsFinal(nD) = Coords(2,j); %Add the y-coordinate to the final array
            FiltFinal(nD) = filtration(k); %Add the filtration value to the final array
            KermaFinal(nD) = kerma(k); %Add the air kerma per projection value to the final array
            sFWFinal(nD) = subFieldWidths(k); %Add the sub-field width to the final array
            anglesFinal(nD) = angles(aC); %Add the gantry angle to the final array
        else %If not in the ellipse
            if k==1 %Check if the sub-field coordinate is the first for this gantry angle
                if withinEllipse(pWidthTemp, pDepthTemp, [Coords(1, j+1), Coords(2, j+1)])==true %Check if the next coordinate is within the ellipse
                    x = subFieldIntersection([Coords(1, j), Coords(1, j+1)], [Coords(2, j), Coords(2, j+1)],subFieldWidths(k),angles(aC), -1); %If so, find the coordinate of the sub-field boundaries
                    if withinEllipse(pWidthTemp, pDepthTemp, [x(1), x(2)])==true %Check that the boundary between sub-fields is within the ellipse, if so field extent is within phantom
                        nD = nD + 1; %Increment the number of data points included
                        p = findIntersections(pWidthTemp, pDepthTemp, angles(aC), [Coords(1, j), Coords(1, j+1)], [Coords(2, j), Coords(2, j+1)]); %Find the point on the surface of the phantom to which the coordinate shall be updated to
                        XCoordsFinal(nD) = p(1,1); %Add the x-coordinate to the final array
                        YCoordsFinal(nD) = p(2,1); %Add the y-coordinate to the final array
                        sFWFinal(nD) = 2*sqrt((p(1,1)-x(1))^2+(p(2,1)-x(2))^2); %Add the sub-field width to the final array
                        anglesFinal(nD) = angles(aC); %Add the gantry angle to the final array
                        if interpolation == true %if enabled, kerma and filtration values are based on coordinate position via interpolation, if not they use the original value
                            d1 = sqrt((Coords(1, j+1)-Coords(1, j))^2+(Coords(2, j+1)-Coords(2, j))^2);
                            d2 = sqrt((p(1,1)-Coords(1, j))^2+(p(2,1)-Coords(2, j))^2);
                            m1 = (kerma(k+1)-kerma(k))/d1;
                            m2 = (filtration(k+1)-filtration(k))/d1;
                            KermaFinal(nD) = kerma(k)+m1*d2;
                            FiltFinal(nD) = filtration(k)+m2*d2;
                        else
                            FiltFinal(nD) = filtration(k); %Add the filtration value to the final array
                            KermaFinal(nD) = kerma(k); %Add the air kerma per projection value to the final array
                        end
                    end
                end
            elseif k==numSubFields %Check if the sub-field coordinate is the last for this gantry angle
                if withinEllipse(pWidthTemp, pDepthTemp, [Coords(1, j-1), Coords(2, j-1)])==true %Check if the previous coordinate is within the ellipse
                    x = subFieldIntersection([Coords(1, j), Coords(1, j-1)], [Coords(2, j), Coords(2, j-1)],subFieldWidths(k),angles(aC), 1); %If so, find the coordinate of the sub-field boundaries
                    if withinEllipse(pWidthTemp, pDepthTemp, [x(1), x(2)])==true %Check that the boundary between sub-fields is within the ellipse, if so field extent is within phantom
                        nD = nD + 1; %Increment the number of data points included
                        p = findIntersections(pWidthTemp, pDepthTemp, angles(aC), [Coords(1, j), Coords(1, j-1)], [Coords(2, j), Coords(2, j-1)]); %Find the point on the surface of the phantom to which the coordinate shall be updated to
                        XCoordsFinal(nD) = p(1,2); %Add the x-coordinate to the final array
                        YCoordsFinal(nD) = p(2,2); %Add the y-coordinate to the final array
                        FiltFinal(nD) = filtration(k); %Add the filtration value to the final array
                        KermaFinal(nD) = kerma(k); %Add the air kerma per projection value to the final array
                        sFWFinal(nD) = 2*sqrt((p(1,2)-x(1))^2+(p(2,2)-x(2))^2); %Add the sub-field width to the final array
                        anglesFinal(nD) = angles(aC); %Add the gantry angle to the final array
                        if interpolation == true %if enabled, kerma and filtration values are based on coordinate position via interpolation, if not they use the original value
                            d1 = sqrt((Coords(1, j)-Coords(1, j-1))^2+(Coords(2, j)-Coords(2, j-1))^2);
                            d2 = sqrt((p(1,2)-Coords(1, j))^2+(p(2,2)-Coords(2, j))^2);
                            m1 = (kerma(k-1)-kerma(k))/d1;
                            m2 = (filtration(k-1)-filtration(k))/d1;
                            KermaFinal(nD) = kerma(k)+m1*d2;
                            FiltFinal(nD) = filtration(k)+m2*d2;
                        else
                            FiltFinal(nD) = filtration(k); %Add the filtration value to the final array
                            KermaFinal(nD) = kerma(k); %Add the air kerma per projection value to the final array
                        end
                    end
                end
            else %Coordinate was neither the first or last for the gantry angle
                if withinEllipse(pWidthTemp, pDepthTemp, [Coords(1, j+1), Coords(2, j+1)])==true %Check if the next coordinate is within the ellipse
                    x = subFieldIntersection([Coords(1, j), Coords(1, j+1)], [Coords(2, j), Coords(2, j+1)],subFieldWidths(k),angles(aC),-1); %If so, find the coordinate of the sub-field boundaries
                    if withinEllipse(pWidthTemp, pDepthTemp, [x(1), x(2)])==true %Check that the boundary between sub-fields is within the ellipse, if so field extent is within phantom
                        nD = nD + 1; %Increment the number of data points included
                        p = findIntersections(pWidthTemp, pDepthTemp, angles(aC), [Coords(1, j), Coords(1, j+1)], [Coords(2, j), Coords(2, j+1)]); %Find the point on the surface of the phantom to which the coordinate shall be updated to
                        XCoordsFinal(nD) = p(1,1); %Add the x-coordinate to the final array
                        YCoordsFinal(nD) = p(2,1); %Add the y-coordinate to the final array
                        FiltFinal(nD) = filtration(k); %Add the filtration value to the final array
                        KermaFinal(nD) = kerma(k); %Add the air kerma per projection value to the final array
                        sFWFinal(nD) = 2*sqrt((p(1,1)-x(1))^2+(p(2,1)-x(2))^2); %Add the sub-field width to the final array
                        anglesFinal(nD) = angles(aC); %Add the gantry angle to the final array
                        if interpolation == true %if enabled, kerma and filtration values are based on coordinate position via interpolation, if not they use the original value
                            d1 = sqrt((Coords(1, j+1)-Coords(1, j))^2+(Coords(2, j+1)-Coords(2, j))^2);
                            d2 = sqrt((p(1,1)-Coords(1, j))^2+(p(2,1)-Coords(2, j))^2);
                            m1 = (kerma(k+1)-kerma(k))/d1;
                            m2 = (filtration(k+1)-filtration(k))/d1;
                            KermaFinal(nD) = kerma(k)+m1*d2;
                            FiltFinal(nD) = filtration(k)+m2*d2;
                        else
                            FiltFinal(nD) = filtration(k); %Add the filtration value to the final array
                            KermaFinal(nD) = kerma(k); %Add the air kerma per projection value to the final array
                        end
                    end
                elseif withinEllipse(pWidthTemp, pDepthTemp, [Coords(1, j-1), Coords(2, j-1)])==true %Check if the previous coordinate is within the ellipse
                    x = subFieldIntersection([Coords(1, j), Coords(1, j-1)], [Coords(2, j), Coords(2, j-1)],subFieldWidths(k),angles(aC),1); %If so, find the coordinate of the sub-field boundaries
                    if withinEllipse(pWidthTemp, pDepthTemp, [x(1), x(2)])==true %Check that the boundary between sub-fields is within the ellipse, if so field extent is within phantom
                        nD = nD + 1; %Increment the number of data points included
                        p = findIntersections(pWidthTemp, pDepthTemp, angles(aC), [Coords(1, j), Coords(1, j-1)], [Coords(2, j), Coords(2, j-1)]); %Find the point on the surface of the phantom to which the coordinate shall be updated to
                        XCoordsFinal(nD) = p(1,2); %Add the x-coordinate to the final array
                        YCoordsFinal(nD) = p(2,2); %Add the y-coordinate to the final array
                        FiltFinal(nD) = filtration(k); %Add the filtration value to the final array
                        KermaFinal(nD) = kerma(k); %Add the air kerma per projection value to the final array
                        sFWFinal(nD) = 2*sqrt((p(1,2)-x(1))^2+(p(2,2)-x(2))^2); %Add the sub-field width to the final array
                        anglesFinal(nD) = angles(aC); %Add the gantry angle to the final array
                        if interpolation == true %if enabled, kerma and filtration values are based on coordinate position via interpolation, if not they use the original value
                            d1 = sqrt((Coords(1, j)-Coords(1, j-1))^2+(Coords(2, j)-Coords(2, j-1))^2);
                            d2 = sqrt((p(1,2)-Coords(1, j))^2+(p(2,2)-Coords(2, j))^2);
                            m1 = (kerma(k-1)-kerma(k))/d1;
                            m2 = (filtration(k-1)-filtration(k))/d1;
                            KermaFinal(nD) = kerma(k)+m1*d2;
                            FiltFinal(nD) = filtration(k)+m2*d2;
                        else
                            FiltFinal(nD) = filtration(k); %Add the filtration value to the final array
                            KermaFinal(nD) = kerma(k); %Add the air kerma per projection value to the final array
                        end
                    end
                end
            end
        end 
    end
    nDI=[nDI; nD-sum(nDI)]; %Add the number of data points at this gantry angle to the array
end

nDI=nDI(2:numel(nDI)); %Removes leading 0
XCoordsFinal = XCoordsFinal(1:nD); %Truncate the final x-axis coordinate array based on the number of points found.
YCoordsFinal = YCoordsFinal(1:nD); %Truncate the final y-axis coordinate array based on the number of points found.
FiltFinal = FiltFinal(1:nD); %Truncate the final total filtration values array based on the number of points found.
KermaFinal = KermaFinal(1:nD); %Truncate the final air kerma pre projection values array based on the number of points found.
sFWFinal = sFWFinal(1:nD); %Truncate the final sub-field coordinate width array based on the number of points found.
anglesFinal = anglesFinal(1:nD); %Truncate the final gantry angle array based on the number of points found.

%%%%%%%%%%%%%%%%% AMMEND SUB-FIELDS BASED ON PHANTOM GEOMETRY END %%%%%%%%%%%%%%%%%

%%

%%%%%%%%%%%%%%%%% FOR PLOTTING  %%%%%%%%%%%%%%%%%

% nothing fancy. Just for graphs/debug

if plotting==true

    [Xs, Ys] = subFieldIntersections(Coords(1,:),Coords(2,:), sF, anglesTemp,ones(numAnglesSimmed, 1)*numel(subFieldWidths)); %Compute the coordinates of the sub-field intersections for the original dataset.
    [Xfs, Yfs] = subFieldIntersections(XCoordsFinal,YCoordsFinal,sFWFinal,anglesFinal, nDI); %Compute the coordinates of the sub-field intersections for the final dataset.

    %These functions plot the phantom shape
    if headScan == false
        theta = 0:0.01:2*pi;
        r = sqrt(((pDepth^2)*(pWidth^2))./(pDepth^2*cos(theta).^2+pWidth^2*sin(theta).^2));
        x = r.*cos(theta);
        y = r.*sin(theta);
    else
        theta = 0.01:0.01:pi-0.01;
        r = sqrt(((pHeadRadii2^2)*(pHeadRadii2^2))./(pHeadRadii2^2*cos(theta).^2+pHeadRadii2^2*sin(theta).^2));
        x = r.*cos(theta);
        y = r.*sin(theta);
        theta2 = pi:0.01:2*pi;
        r2 = sqrt(((pDepth^2)*(pWidth^2))./(pDepth^2*cos(theta2).^2+pWidth^2*sin(theta2).^2));
        x2 = r2.*cos(theta2);
        y2 = r2.*sin(theta2);
        x = [x, x2, x(1)];
        y = [y, y2, y(1)];
    end

    % These functions alter the figure options

    figure(1)
    plot(x,y, 'k', 'LineWidth', 4)
    hold on
    plot(Xfs,Yfs, '.', 'MarkerSize', 1, 'Color', [0.2, 0.2, 1])
    hold on
    plot(XCoordsFinal, YCoordsFinal, '.', 'MarkerSize', 4, 'Color', [1, 0.2, 0.2])
    grid on
    legend('Phantom Boundary', 'Sub-field boundary', 'Sub-field centre')
    axis([-25 25 -25 25])
    title('Ammended Sub-fields')
    xlabel('X-Position (cm)')
    ylabel('Y-Position (cm)')

    figure(2)
    plot(x,y, 'k', 'LineWidth', 4)
    hold on
    plot(Xs, Ys, '.', 'MarkerSize', 1, 'Color', [0.2, 0.2, 1])
    hold on
    plot(Coords(1,:),Coords(2,:), '.', 'MarkerSize', 4, 'Color', [1, 0.2, 0.2])
    grid on
    legend('Phantom Boundary', 'Sub-field boundary', 'Sub-field centre')
    axis([-25 25 -25 25])
    title('Original Sub-fields')
    xlabel('X-Position (cm)')
    ylabel('Y-Position (cm)')

end


%%%%%%%%%%%%%%%%% FOR PLOTTING END %%%%%%%%%%%%%%%%%

%%

%%%%%%%%%%%%%%%%% DATA OUTPUT %%%%%%%%%%%%%%%%%

%Transpose data
XCoordsFinal = XCoordsFinal';
YCoordsFinal = YCoordsFinal';
FiltFinal = FiltFinal';
KermaFinal = KermaFinal';
sFWFinal = sFWFinal';

anglesFinal = round(anglesFinal,12, 'significant')'; %Rounded angles to prevent PCXMC throwing errors for too many significant figures

clearvars PCXMCInput %Clear variable PCXMCInput to be used for final output to be copied to PCXMC excel sheet.

%Assign variables to columns of M to be consistent with input for PCXMC.
%TP comments added: spreadsheet variable is in comments after the assignment
PCXMCInput(:,3) = anglesFinal(:,1); %Projection (AP,PA,LATL,LATR or num.angle)
PCXMCInput(:,4) = oblique; %Oblique angle
PCXMCInput(:,5) = UID; %Patient number
PCXMCInput(:,6) = height; %Patient height (cm), (reference size=0)
PCXMCInput(:,7) = mass; %Patient weight (kg), (reference size=0))
PCXMCInput(:,8) = age; %Patient age (0,1,5,10,15,30)
PCXMCInput(:,9) = kV; %X-ray tube voltage (kV)
PCXMCInput(:,10) = FiltFinal(:,1); %Filtration (mm Al)
PCXMCInput(:,11) = 0; %Additional filter (mm Cu)
PCXMCInput(:,12) = FRD; %FRD (cm)
PCXMCInput(:,13) = sFWFinal(:,1); %X-ray beam width (cm, at FRD)
PCXMCInput(:,14) = width; %X-ray beam height (cm, at FRD)
PCXMCInput(:,15) = XCoordsFinal(:,1); %Xref
PCXMCInput(:,16) = YCoordsFinal(:,1); %Yref
PCXMCInput(:,17) = z; %Zref
PCXMCInput(:,18) = arms; %Arms in phantom (1 or 0)
PCXMCInput(:,20) = KermaFinal(:,1); %Input dose value
PCXMCInput(:,1) = 0; %Hospital
PCXMCInput(:,2) = 0; %Examination

%TP comments
%original code was missing the assignment of the input dose quantity
%Input dose quantity (EAK,EE,DAP,EAP or MAS)
%from PCXMC users guide
%      EAK Incident air kerma, in mGy – no backscatter
%      EE Entrance exposure, in mR – no backscatter
%      D dAP The product of air kerma and area (DAP or KAP), in units of mGy?cm2
%      EAP The exposure-area product, in R?cm2
%      MAS The current-time product, in mA?s

%PCXMCInput(:,19) = "EAK", but PCXMC input is defined as double and i can't
%be bothered fixing it.

%MAKE SURE YOU PUT "EAK" in the appropriate spreadsheet column
%Input dose quantity (EAK,EE,DAP,EAP or MAS)
%before running the spreadsheet macros.


%%%%%%%%%%%%%%%%% DATA OUTPUT END %%%%%%%%%%%%%%%%%
