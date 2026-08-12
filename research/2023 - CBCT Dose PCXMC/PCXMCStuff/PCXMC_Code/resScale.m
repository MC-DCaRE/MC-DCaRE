function [subFieldCoords, subFieldWidths, kerma, filtration] = resScale(subFieldCoordsTemp, subFieldWidthsTemp, kermaTemp, filtrationTemp, numSubFields)
% RESCALE  Rescale sub-field data to different resolution using linear interpolation
%
%   [subFieldCoords, subFieldWidths, kerma, filtration] = RESCALE(...)
%   increases or decreases the resolution of sub-field data by linearly
%   interpolating values while maintaining the original field extent.
%
%   Inputs:
%       subFieldCoordsTemp - original sub-field coordinates [2xN matrix]
%       subFieldWidthsTemp - original sub-field widths [1xN vector]
%       kermaTemp - original air kerma values [1xN vector]
%       filtrationTemp - original filtration values [1xN vector]
%       numSubFields - desired number of sub-fields after scaling
%
%   Outputs:
%       subFieldCoords - rescaled sub-field coordinates [2xM matrix]
%       subFieldWidths - rescaled sub-field widths [1xM vector]
%       kerma - rescaled air kerma values [1xM vector]
%       filtration - rescaled filtration values [1xM vector]
%
%   Algorithm:
%   1. Determine original field extent from min/max coordinates
%   2. Create evenly spaced grid points across field extent
%   3. Use linear interpolation to calculate values at new points
%   4. Calculate uniform sub-field widths based on new spacing
%
%   Example:
%       [coords, widths, kerma, filt] = resScale(orig_coords, orig_widths, ...
%           orig_kerma, orig_filt, 15); % Scale to 15 sub-fields

% Extract X-coordinates from input matrix (row 2 contains X values)
X = subFieldCoordsTemp(2,:);

% Calculate field boundaries
% Field extends from min coordinate minus half of first width to
% max coordinate plus half of last width
Xmin = min(X) - subFieldWidthsTemp(1)/2;
Xmax = max(X) + subFieldWidthsTemp(end)/2;

% Create evenly spaced sub-field centers across the field extent
% The spacing is calculated to distribute numSubFields points evenly
subFieldCoords = Xmin + (Xmax - Xmin) * (0.5:numSubFields-0.5) / numSubFields;

% Calculate uniform sub-field width based on new spacing
% All sub-fields have equal width after scaling
subFieldWidths = ones(1, numSubFields) * abs(subFieldCoords(2) - subFieldCoords(1));

% Use linear interpolation to calculate kerma values at new coordinates
% "linear" method ensures smooth interpolation between original points
% "extrap" allows extrapolation beyond original range if needed
kerma = interp1(subFieldCoordsTemp(2,:), kermaTemp, subFieldCoords, "linear", "extrap");

% Use linear interpolation for filtration values
filtration = interp1(subFieldCoordsTemp(2,:), filtrationTemp, subFieldCoords, "linear", "extrap");

% Reconstruct final coordinate matrix
% Row 1: Y-coordinates (all zeros for 2D transverse plane)
% Row 2: X-coordinates (the interpolated positions)
subFieldCoords = [zeros(1, numel(subFieldCoords)); subFieldCoords];

end
