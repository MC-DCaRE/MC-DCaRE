function [output] = WrapTo360(input)
%{
WrapTo360 takes vaules in degrees, both negative and positive, and maps the values such that they always lie within -360 to +360. 
E.g., 540 degrees is mapped to 180, and -540 degrees is mapped to -180.
%}

%% Code by Aaron Fetin. Revised July 2022.

temp = input/360; %Temporary array is assigned the input array normalised to 360 degrees.

temp(temp>=1 | temp<=-1) = (temp(temp>=1 | temp<=-1)-fix(temp(temp>=1 | temp<=-1))); % If values were >=1 or <=-1, they were outside of +-360. These are adjusted to be within +-1.

output = temp*360; % The output is given by temp values multiplied by 360 to yield values in degrees.

end

