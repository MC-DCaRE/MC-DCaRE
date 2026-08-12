function [Xf, Yf] = subFieldIntersections(X, Y, sFW, angles, nDI)
% SUBFIELDINTERSECTIONS  Calculate boundary coordinates for all sub-fields
%
%   [Xf, Yf] = SUBFIELDINTERSECTIONS(X, Y, sFW, angles, nDI) calculates
%   the boundary coordinates for all sub-fields across all gantry angles.
%
%   Inputs:
%       X - x-coordinates of sub-field centers [1xN vector]
%       Y - y-coordinates of sub-field centers [1xN vector]
%       sFW - sub-field widths [1xN vector]
%       angles - gantry angles for each sub-field [1xN vector]
%       nDI - number of sub-fields at each gantry angle [1xM vector]
%
%   Outputs:
%       Xf - x-coordinates of all boundary points [1xK vector]
%       Yf - y-coordinates of all boundary points [1xK vector]
%
%   Algorithm:
%   1. Calculate total array size needed for all boundary points
%   2. Loop through each gantry angle
%   3. For each sub-field, calculate left and right boundaries
%   4. Add final boundary point for each angle
%   5. Return complete boundary coordinate arrays
%
%   Example:
%       [Xf, Yf] = subFieldIntersections(X, Y, widths, angles, [7,7,7]);

% Calculate total size needed for output arrays
% Each sub-field contributes 2 boundaries (left and right)
% Plus 1 additional boundary point per gantry angle
total_size = sum(nDI) + numel(nDI);

% Preallocate output arrays for efficiency
Yf = zeros(total_size, 1); % y-coordinates of boundary points
Xf = zeros(total_size, 1); % x-coordinates of boundary points

% Initialize counters
k = 0; % Counter for output array (boundary points)
i = 0; % Counter for input array (sub-field centers)

% Loop through each gantry angle
for n = 1:numel(nDI)
    % Process each sub-field for this gantry angle
    for j = 1:nDI(n)
        k = k + 1; % Increment boundary counter
        i = i + 1; % Increment sub-field counter
        
        % Calculate left boundary point (behind the beam direction)
        % Offset by half sub-field width perpendicular to beam
        Yf(k) = Y(i) - (sFW(i)/2) * sind(angles(i) + 90);
        Xf(k) = X(i) - (sFW(i)/2) * cosd(angles(i) + 90);
    end
    
    % Add final boundary point for this gantry angle
    % This is the right boundary of the last sub-field
    k = k + 1;
    Yf(k) = Y(i) + (sFW(i)/2) * sind(angles(i) + 90);
    Xf(k) = X(i) + (sFW(i)/2) * cosd(angles(i) + 90);
end

end
