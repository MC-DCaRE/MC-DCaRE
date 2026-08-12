function [ Y ] = withinEllipse( a, b, X )
%withinEllipse checks if the provided coordinate X, is within an ellipse
%with radii of a in the x-axis and b in the y-axis. The function returns
%true if so, or false if not.

%% Code by Aaron Fetin. Revised July 2022.

Y = ((X(1)/a)^2)+((X(2)/b)^2)<=1;

end

