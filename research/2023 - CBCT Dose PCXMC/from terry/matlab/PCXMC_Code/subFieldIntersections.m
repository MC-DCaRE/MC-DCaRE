function [ Xf, Yf ] = subFieldIntersections( X, Y, sFW, a, nDI )
%SUBFIELDINTERSECTION find the coordinates of the boundaries of sub-fields based on
%the coordinates of the sub-fields (X,Y), the sub-field widths (sFW), the
%gantry angles (a), and the number of data elements at each gantry angle
%(nDI)

%% Code by Aaron Fetin. Revised July 2022.

s= sum(nDI)+numel(nDI); %The total size of the array needed

Yf = zeros(sum(nDI)+numel(nDI), 1); %Preallocate the y-axis coordinates
Xf = zeros(sum(nDI)+numel(nDI), 1);%Preallocate the x-axis coordinates

k = 0; %Iterate through the output array
i = 0; %Iterate through the input array
for n= 1:numel(nDI) %iterate through the gantry angles
    for j = 1:nDI(n) %iterate through the number of sub-fields at each gantry angle
        k = k +1;
        i = i +1;
        Yf(k) = Y(i)-(sFW(i)/2)*sind(a(i)+90); %find the Y boundary 'behind' the current Y coordinate
        Xf(k) = X(i)-(sFW(i)/2)*cosd(a(i)+90); %find the X boundary 'behind' the current X coordinate
    end
    k = k + 1;
    Yf(k) = Y(i)+(sFW(i)/2)*sind(a(i)+90); %find the Y boundary 'after' the last coordinate at a given gantry angle
    Xf(k) = X(i)+(sFW(i)/2)*cosd(a(i)+90); %find the X boundary 'after' the last coordinate at a given gantry angle
end
end

