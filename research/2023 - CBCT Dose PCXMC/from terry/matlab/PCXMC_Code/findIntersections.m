function [ P ] = findIntersections( a, b, angle, X, Y )
%FINDINTERSECTIONS finds the intersection between the line of sub-field
%coordinates for a given gantry angle and the phantoms surface.

%% Code by Aaron Fetin. Revised July 2022.

if Y(1) == Y(2) %if line is horizontal
    
    if Y(1)>-b&&Y(1)<b %check horizontal line intersects ellipse
    else
    end
    x1 = sqrt((1-(Y(1)/b)^2)*a^2);
    x2 = -x1;
    y1 = Y(1);
    y2 = y1;
    
    %y1=y1, x1<x2
    
elseif X(1) == X(2) %if line is vertical
    
    if X(1)>-a&&X(1)<a %check vertical line intersects ellipse
    else
    end
    y2 = sqrt((1-(X(1)/a)^2)*b^2);
    y1 = -y2;
    x1 = X(1);
    x2 = x1;
    
    %x1=x2, y1<y1
    
else 
    
    m = (Y(2)-Y(1))/(X(2)-X(1)); %slope of the line
    B = Y(1)-m*X(1); %intercept of the line
    aQX = m^2+(b/a)^2; %a-term for x coordinate quadratic
    bQX = 2*m*B; %b-term for x coordinate quadratic
    cQX = B^2-b^2; %c-term for x coordinate quadratic
    if bQX^2-4*aQX*cQX>0 %check quadratic has real coordinates i.e intersections exist
    else
    end
    x2 = (-bQX-sqrt(bQX^2-4*aQX*cQX))/(2*aQX); %first x coordinate
    x1 = (-bQX+sqrt(bQX^2-4*aQX*cQX))/(2*aQX); %second x coordinate
    y2 = x2*m+B; %first y coordinate
    y1 = x1*m+B; %second y coordinate
    
    %if m>0, x1<x2, y1<y2
    %if m<0, x1<x2, y1>y2
    
end

if (angle>=180)&&(angle<360)
    P = [x2, x1; y2, y1];
else
    P = [x1, x2; y1, y2];
end

end

