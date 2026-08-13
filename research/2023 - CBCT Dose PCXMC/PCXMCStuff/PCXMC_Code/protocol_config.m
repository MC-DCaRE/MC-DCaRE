% PCXMC Protocol Configuration File
% This file contains all configurable parameters for PCXMC dose calculation
% Copy this file and modify values to create custom protocols
%
% Usage:
%   config = load_protocol_config(); % Loads from this file
%   config = load_protocol_config('my_protocol.m'); % Loads from custom file

%% Phantom Position Configuration
% Position of isocentre relative to phantom center
iso = [-2.2; 1.2]; % [x; y] coordinates (cm) - isocentre position relative to phantom center
z = 0; % Sup-Inf offset (cm) - vertical displacement from isocentre
arms = 0; % Include arms in phantom (0 = no, 1 = yes)

%% Scan Parameters
% Technical parameters for the CT scan
kV = 125; % Tube voltage (kV) - affects beam quality and dose
FRD = 100; % Focus-to-reference distance (cm) - source to isocentre distance
headScan = true; % Scan type (true = head scan, false = body scan)
startingAngle = 0; % Starting gantry angle (degrees)
finalAngle = 360; % Final gantry angle (degrees)
numAnglesSimmed = 8; % Number of angles for simulation
numAnglesTrue = 360; % Number of angles in actual scan
oblique = 0; % Oblique angle flag (0 = no obliquity)

%% Sub-field Configuration
% Beam configuration parameters
% Format: [X1, X2, X3, ...; Y1, Y2, Y3, ...] - coordinates at gantry angle 0
subFieldCoords = [0, 0, 0, 0, 0, 0, 0; -15, -10, -5, 0, 5, 10, 15]; % Sub-field coordinates (cm)
subFieldWidths = [5, 5, 5, 5, 5, 5, 5]; % Width of each sub-field (cm)
width = 20.6; % Total field width at isocentre (cm)

%% Dose Parameters
% Air kerma values scaled by actual vs simulated projections
kerma = (numAnglesTrue/numAnglesSimmed) .* [0.1, 0.2, 0.5, 1, 0.5, 0.2, 0.1]; % Air kerma per projection (mGy)
filtration = [0.1, 0.2, 0.5, 1, 0.5, 0.2, 0.1]; % Total filtration (mm Al)

%% Phantom Geometry
% Patient/phantom dimensions
pWidth = 15; % Phantom width (cm) - anterior radius for head scans
pDepth = 15; % Phantom depth (cm)
pHeadRadii2 = 13; % Posterior head radius (cm) - only used for head scans
height = 172; % Patient height (cm)
mass = 95; % Patient mass (kg)
age = 30; % Patient age (years)

%% Processing Options
% Control processing behavior
plotting = true; % Enable diagnostic plots (true/false)
interpolation = false; % Enable kerma/filtration interpolation (true/false)
resolutionScaling = false; % Enable resolution scaling (true/false)
numSubFields = 11; % Target number of sub-fields for scaling (only if resolutionScaling=true)
