function [subFieldCoords, subFieldWidths, kerma, filtration] = resScale(subFieldCoordsTemp, subFieldWidthsTemp, kermaTemp, filtrationTemp, numSubFields)
%RESSCALE increases or decreases the resolution of the input subfield data
%by linearily interpolating extra values. The full field extent is divded into 
%evenly spaced points and the values determined by lineart interpolation. 
%The field extent is therefore maintained.

%% Code by Aaron Fetin. Revised July 2022.

X = subFieldCoordsTemp(2,:); 
Xmin = min(X)-subFieldWidthsTemp(1)/2;
Xmax = max(X)+subFieldWidthsTemp(numel(subFieldWidthsTemp))/2;

subFieldCoords = Xmin+(Xmax-Xmin)/(2*numSubFields):(Xmax-Xmin)/(numSubFields):Xmax-+(Xmax-Xmin)/(2*numSubFields);

subFieldWidths = ones(1,numSubFields)*abs(subFieldCoords(2)-subFieldCoords(1));

kerma = interp1(subFieldCoordsTemp(2,:), kermaTemp,subFieldCoords,"linear", "extrap");
filtration = interp1(subFieldCoordsTemp(2,:), filtrationTemp,subFieldCoords,"linear", "extrap");

subFieldCoords = [zeros(1, numel(subFieldCoords)); subFieldCoords];


end

