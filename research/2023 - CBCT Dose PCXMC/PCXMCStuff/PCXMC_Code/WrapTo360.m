function [wrappedAngles] = WrapTo360(inputAngles)
% WRAPTO360  Wrap angles to the range [-360, 360] degrees
%
%   [wrappedAngles] = WRAPTO360(inputAngles) takes input angles in degrees
%   (both positive and negative) and maps them to the range [-360, 360].
%
%   Input:
%       inputAngles - scalar or array of angles in degrees
%
%   Output:
%       wrappedAngles - angles wrapped to [-360, 360] range
%
%   Algorithm:
%   1. Normalize angles by dividing by 360
%   2. Remove integer multiples of 360 using fractional part
%   3. Scale back to degrees
%
%   Examples:
%       WrapTo360(540)    % Returns 180
%       WrapTo360(-540)   % Returns -180
%       WrapTo360(720)    % Returns 0
%       WrapTo360([450, -270, 1080]) % Returns [90, -270, 0]
%
%   Note:
%   This function preserves angles that are already within [-360, 360]
%   and handles both scalar and array inputs.

% Normalize angles to 360-degree units
% This converts angles to fractions of a full rotation
normalized = inputAngles / 360;

% Remove complete rotations by taking fractional part
% fix() returns the integer part toward zero
% This handles both positive and negative angles correctly
normalized(normalized >= 1 | normalized <= -1) = ...
    normalized(normalized >= 1 | normalized <= -1) - ...
    fix(normalized(normalized >= 1 | normalized <= -1));

% Scale back to degrees
wrappedAngles = normalized * 360;

end
