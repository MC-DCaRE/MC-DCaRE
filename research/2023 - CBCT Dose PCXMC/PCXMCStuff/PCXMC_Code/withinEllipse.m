function [isInside] = withinEllipse(a, b, point)
% WITHINELLIPSE  Check if a point lies within an ellipse
%
%   [isInside] = WITHINELLIPSE(a, b, point) determines whether a given
%   2D point lies within an ellipse centered at the origin.
%
%   Inputs:
%       a - semi-major axis length along x-axis (cm)
%       b - semi-minor axis length along y-axis (cm)
%       point - 2D coordinate [x; y] to test (cm)
%
%   Output:
%       isInside - logical value (true if point is inside ellipse, false otherwise)
%
%   Algorithm:
%   Uses the standard ellipse equation: (x/a)^2 + (y/b)^2 <= 1
%   If the inequality holds, the point is inside the ellipse.
%
%   Example:
%       isInside = withinEllipse(10, 5, [3; 2]); % Returns true
%       isInside = withinEllipse(10, 5, [15; 0]); % Returns false

% Calculate the ellipse equation value
% This represents the normalized distance from the center
ellipse_value = (point(1)/a)^2 + (point(2)/b)^2;

% Check if the point satisfies the ellipse inequality
% Points on the boundary (ellipse_value == 1) are considered inside
isInside = ellipse_value <= 1;

end
