function [P] = subFieldIntersection(X, Y, sFW, angle, direction)
% SUBFIELDINTERSECTION  Calculate boundary point for a single sub-field
%
%   [P] = SUBFIELDINTERSECTION(X, Y, sFW, angle, direction) calculates
%   the coordinate of a sub-field boundary point based on the sub-field
%   center, width, gantry angle, and direction.
%
%   Inputs:
%       X - x-coordinate of sub-field center (cm)
%       Y - y-coordinate of sub-field center (cm)
%       sFW - sub-field width (cm)
%       angle - gantry angle (degrees)
%       direction - direction multiplier (-1 for left boundary, +1 for right boundary)
%
%   Output:
%       P - 2x1 vector containing boundary coordinates [x; y]
%
%   Algorithm:
%   1. Calculate perpendicular offset from center based on sub-field width
%   2. Apply rotation transformation based on gantry angle
%   3. Return boundary coordinates
%
%   Example:
%       P = subFieldIntersection(0, 5, 2, 45, -1); % Left boundary at 45°

% Calculate perpendicular offset distance
% The boundary is offset by half the sub-field width in the direction
% perpendicular to the beam direction
offset_distance = direction * (sFW / 2);

% Calculate boundary coordinates using trigonometric rotation
% The offset is applied perpendicular to the beam direction (angle + 90°)
% This accounts for the beam's orientation at the given gantry angle
Y_boundary = Y + offset_distance * sind(angle + 90);
X_boundary = X + offset_distance * cosd(angle + 90);

% Return boundary point as column vector
P = [X_boundary; Y_boundary];

end
