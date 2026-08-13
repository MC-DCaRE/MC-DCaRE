function [p] = findIntersections(a, b, theta, x, y)
% FINDINTERSECTIONS  Calculate intersection points between a line and an ellipse
%
%   [p] = FINDINTERSECTIONS(a, b, theta, x, y) calculates the intersection
%   points between a line defined by two points (x,y) and an ellipse
%   centered at the origin with semi-axes a and b, rotated by angle theta.
%
%   Inputs:
%       a - semi-major axis length of the ellipse (cm)
%       b - semi-minor axis length of the ellipse (cm)
%       theta - rotation angle of the ellipse (degrees)
%       x - x-coordinates of two points defining the line [x1, x2]
%       y - y-coordinates of two points defining the line [y1, y2]
%
%   Output:
%       p - 2x2 matrix containing intersection points
%           p = [x1, x2; y1, y2] where (x1,y1) and (x2,y2) are the
%           intersection points
%
%   Algorithm:
%   1. Transform line equation to standard form: Ax + By + C = 0
%   2. Apply rotation transformation to account for ellipse rotation
%   3. Solve quadratic equation for intersection points
%   4. Transform solutions back to original coordinate system
%
%   Example:
%       p = findIntersections(15, 15, 0, [0, 10], [0, 10]);
%       % Finds intersections between line from (0,0) to (10,10) and circle radius 15

% Convert angle to radians for trigonometric calculations
theta_rad = theta * pi / 180;

% Calculate line coefficients from two points
% Line equation: (y2-y1)x - (x2-x1)y + (x2y1-x1y2) = 0
A = y(2) - y(1); % Coefficient for x
B = x(1) - x(2); % Coefficient for y
C = x(2)*y(1) - x(1)*y(2); % Constant term

% Apply rotation transformation to account for ellipse rotation
% This transforms the line equation into the ellipse's coordinate system
A_rot = A * cos(theta_rad) + B * sin(theta_rad);
B_rot = -A * sin(theta_rad) + B * cos(theta_rad);

% Calculate coefficients for quadratic equation
% The intersection problem reduces to solving: Ax^2 + Bx + C = 0
% where the coefficients are derived from the ellipse and line equations
a_quad = A_rot^2 * b^2 + B_rot^2 * a^2;
b_quad = 2 * A_rot * C * b^2;
c_quad = C^2 * b^2 - a^2 * b^2 * B_rot^2;

% Calculate discriminant to determine number of solutions
discriminant = b_quad^2 - 4 * a_quad * c_quad;

% Check if line intersects the ellipse
if discriminant < 0
    % No real intersections - line doesn't intersect ellipse
    p = [];
    return;
end

% Calculate intersection points in rotated coordinate system
% Using quadratic formula: x = [-b ± sqrt(b^2-4ac)] / 2a
x1_rot = (-b_quad + sqrt(discriminant)) / (2 * a_quad);
x2_rot = (-b_quad - sqrt(discriminant)) / (2 * a_quad);

% Calculate corresponding y-coordinates using line equation
% From Ax + By + C = 0 => y = (-Ax - C) / B
if abs(B_rot) > eps % Check for vertical line
    y1_rot = (-A_rot * x1_rot - C) / B_rot;
    y2_rot = (-A_rot * x2_rot - C) / B_rot;
else
    % Handle vertical line case
    y1_rot = sqrt(b^2 * (1 - x1_rot^2 / a^2));
    y2_rot = -y1_rot;
end

% Transform intersection points back to original coordinate system
% Apply inverse rotation transformation
x1 = x1_rot * cos(theta_rad) - y1_rot * sin(theta_rad);
y1 = x1_rot * sin(theta_rad) + y1_rot * cos(theta_rad);

x2 = x2_rot * cos(theta_rad) - y2_rot * sin(theta_rad);
y2 = x2_rot * sin(theta_rad) + y2_rot * cos(theta_rad);

% Return intersection points as 2x2 matrix
p = [x1, x2; y1, y2];

end
