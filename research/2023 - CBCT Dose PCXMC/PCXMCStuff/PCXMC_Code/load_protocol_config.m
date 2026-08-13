function config = load_protocol_config(filepath)
% LOAD_PROTOCOL_CONFIG Loads and validates protocol configuration
%
%   config = LOAD_PROTOCOL_CONFIG() loads configuration from 'protocol_config.m'
%   config = LOAD_PROTOCOL_CONFIG(filepath) loads from specified file
%
%   Returns a struct containing all protocol parameters with validation
%
%   Example:
%       config = load_protocol_config();
%       config = load_protocol_config('my_protocol.m');
%
%   Configuration Structure Fields:
%       iso - Isocentre coordinates [x; y] (cm)
%       z - Sup-Inf offset (cm)
%       arms - Include arms flag (0/1)
%       kV - Tube voltage (kV)
%       FRD - Focus-to-reference distance (cm)
%       headScan - Head scan flag (1=true, 0=false)
%       startingAngle - Starting gantry angle (degrees)
%       finalAngle - Final gantry angle (degrees)
%       numAnglesSimmed - Number of projections in simulation
%       numAnglesTrue - Number of projections in actual scan
%       oblique - Oblique angle flag
%       subFieldCoords - 2xN matrix of sub-field coordinates
%       subFieldWidths - 1xN vector of sub-field widths (cm)
%       width - Field width at isocentre (cm)
%       kerma - 1xN vector of air kerma values (mGy)
%       filtration - 1xN vector of filtration values (mm Al)
%       pWidth - Phantom width (cm)
%       pDepth - Phantom depth (cm)
%       pHeadRadii2 - Posterior head radius (cm)
%       height - Phantom height (cm)
%       mass - Phantom mass (kg)
%       age - Phantom age (years)
%       plotting - Enable diagnostic plots (true/false)
%       interpolation - Enable interpolation for shifted points (true/false)
%       resolutionScaling - Enable resolution scaling (true/false)
%       numSubFields - Target number of sub-fields for scaling

% Default filepath
if nargin < 1
    filepath = 'protocol_config.m';
end

% Initialize config struct
config = struct();

% Load configuration file
try
    % Execute the config file which populates the config struct
    % The config file should define variables that will become fields of the config struct
    run(filepath);
catch ME
    error('Failed to load protocol config file "%s": %s', filepath, ME.message);
end

% Validate required fields
required_fields = {'iso', 'kV', 'FRD', 'subFieldCoords', 'subFieldWidths', ...
                  'width', 'kerma', 'filtration', 'pWidth', 'pDepth', ...
                  'height', 'mass', 'age', 'startingAngle', 'finalAngle', ...
                  'numAnglesSimmed', 'numAnglesTrue'};

missing_fields = {};
for i = 1:length(required_fields)
    if ~isfield(config, required_fields{i})
        missing_fields{end+1} = required_fields{i};
    end
end

if ~isempty(missing_fields)
    error('Missing required configuration fields: %s', strjoin(missing_fields, ', '));
end

% Validate data types and dimensions
validate_config(config);

end

function validate_config(config)
% VALIDATE_CONFIG Validates configuration parameters
%
%   validate_config(config) performs comprehensive validation of the
%   configuration structure to ensure all parameters are valid for PCXMC
%   processing. Checks include:
%   - Numeric type validation
%   - Matrix dimension consistency
%   - Logical value validation
%   - Angle range validation
%   - Physical parameter validation (positive values)

% Check numeric values - ensure all numeric fields contain valid numbers
numeric_fields = {'kV', 'FRD', 'width', 'pWidth', 'pDepth', ...
                 'height', 'mass', 'age', 'startingAngle', ...
                 'finalAngle', 'numAnglesSimmed', 'numAnglesTrue', ...
                 'z', 'oblique', 'arms'};

for i = 1:length(numeric_fields)
    if isfield(config, numeric_fields{i})
        if ~isnumeric(config.(numeric_fields{i}))
            error('Field %s must be numeric', numeric_fields{i});
        end
    end
end

% Check matrix dimensions - ensure consistency between related arrays
if size(config.subFieldCoords, 1) ~= 2
    error('subFieldCoords must be 2xN matrix [X; Y] coordinates');
end

if length(config.subFieldWidths) ~= size(config.subFieldCoords, 2)
    error('subFieldWidths length must match subFieldCoords columns (%d vs %d)', ...
          length(config.subFieldWidths), size(config.subFieldCoords, 2));
end

if length(config.kerma) ~= size(config.subFieldCoords, 2)
    error('kerma length must match subFieldCoords columns (%d vs %d)', ...
          length(config.kerma), size(config.subFieldCoords, 2));
end

if length(config.filtration) ~= size(config.subFieldCoords, 2)
    error('filtration length must match subFieldCoords columns (%d vs %d)', ...
          length(config.filtration), size(config.subFieldCoords, 2));
end

% Check logical values - handle both logical and numeric (0/1) inputs
logical_fields = {'plotting', 'interpolation', 'resolutionScaling', ...
                 'headScan'};
for i = 1:length(logical_fields)
    if isfield(config, logical_fields{i})
        if ~islogical(config.(logical_fields{i})) && ...
           ~isnumeric(config.(logical_fields{i}))
            error('Field %s must be logical or numeric (0/1)', logical_fields{i});
        end
    end
end

% Check angle ranges - wrap angles outside 0-360 range
if config.startingAngle < 0 || config.startingAngle > 360
    warning('startingAngle (%.1f) outside 0-360 range, will be wrapped to %.1f', ...
            config.startingAngle, mod(config.startingAngle, 360));
end

if config.finalAngle < 0 || config.finalAngle > 360
    warning('finalAngle (%.1f) outside 0-360 range, will be wrapped to %.1f', ...
            config.finalAngle, mod(config.finalAngle, 360));
end

% Additional validation for physical parameters
if config.kV <= 0
    error('Tube voltage (kV) must be positive');
end

if config.FRD <= 0
    error('Focus-to-reference distance (FRD) must be positive');
end

if any(config.subFieldWidths <= 0)
    error('All sub-field widths must be positive');
end

if any(config.kerma < 0)
    error('All kerma values must be non-negative');
end

if any(config.filtration < 0)
    error('All filtration values must be non-negative');
end

end
