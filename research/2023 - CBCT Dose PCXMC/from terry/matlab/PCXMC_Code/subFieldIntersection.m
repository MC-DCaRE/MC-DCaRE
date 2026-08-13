function [ P ] = subFieldIntersection(X, Y, sFW, a, d)
%FINDDISTANCEPOINT finds the coordinate of the boundary between two
%sub-fields

%% Code by Aaron Fetin. Revised July 2022.

Yf(1, 1) = Y(1)-d*(sFW(1)/2)*sind(a(1)+90);
Xf(1, 1) = X(1)-d*(sFW(1)/2)*cosd(a(1)+90);

P=[Xf; Yf];

end

