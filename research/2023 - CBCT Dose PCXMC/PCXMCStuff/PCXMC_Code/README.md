# PCXMC MATLAB Code - Refactored Version

## Overview
This is a refactored version of the PCXMC MATLAB code originally developed by Aaron Fetin. The refactoring improves code readability, maintainability, and introduces a configuration-based approach for protocol-specific parameters.

## Key Improvements

### 1. Configuration-Based Parameters
- **Protocol-specific configuration files**: All scan parameters are now stored in separate `.m` files
- **No code modification required**: Users can create different protocol configurations without touching the main calculation code
- **Validation**: Configuration loading includes parameter validation and warnings

### 2. Improved Code Structure
- **Modular design**: Main logic broken into smaller, focused functions
- **Clear separation of concerns**: Each function has a single responsibility
- **Better naming**: Descriptive function and variable names
- **Reduced complexity**: Nested loops simplified with helper functions

### 3. Enhanced Readability
- **Comprehensive documentation**: Each function includes clear documentation
- **Consistent formatting**: Standardized code style throughout
- **Logical flow**: Clear step-by-step processing pipeline

## File Structure

### Core Files
- `Main_refactored.m` - Main processing script (refactored)
- `load_protocol_config.m` - Configuration loading and validation
- `protocol_config.m` - Sample protocol configuration

### Original Files (unchanged)
- `findIntersections.m` - Ellipse intersection calculations
- `resScale.m` - Resolution scaling utility
- `subFieldIntersection.m` - Single sub-field boundary calculation
- `subFieldIntersections.m` - Multiple sub-field boundary calculations
- `withinEllipse.m` - Point-in-ellipse check
- `WrapTo360.m` - Angle wrapping utility

## Usage

### Basic Usage
1. **Create a protocol configuration file** (copy `protocol_config.m` and modify):
   ```matlab
   % Create my_protocol.m with your specific parameters
   ```

2. **Run the refactored main script**:
   ```matlab
   % Run with default protocol_config.m
   Main_refactored
   
   % Or specify a different protocol file
   config = load_protocol_config('my_protocol.m');
   ```

### Creating Custom Protocols
1. Copy `protocol_config.m` to a new file (e.g., `head_ct_protocol.m`)
2. Modify parameters as needed for your specific protocol
3. Save the file
4. Run: `config = load_protocol_config('head_ct_protocol.m')`

### Configuration Parameters
All parameters are documented in the configuration file with clear descriptions:
- **Phantom Position**: iso, z, arms
- **Scan Parameters**: kV, FRD, headScan, angles, etc.
- **Sub-field Configuration**: coordinates, widths, field size
- **Dose Parameters**: kerma values, filtration
- **Phantom Geometry**: dimensions, patient characteristics
- **Processing Options**: plotting, interpolation, scaling

## Comparison: Original vs Refactored

| Aspect | Original | Refactored |
|--------|----------|------------|
| **Configuration** | Hard-coded variables | External config files |
| **Function Size** | Single 400+ line function | Multiple focused functions |
| **Readability** | Complex nested loops | Clear modular structure |
| **Maintainability** | Requires code changes | Protocol files only |
| **Reusability** | Single use case | Multiple protocols |
| **Testing** | Difficult to isolate | Functions can be tested independently |

## Backward Compatibility
The original `Main.m` remains unchanged for backward compatibility. The refactored version is provided as `Main_refactored.m`.

## Validation
The refactored code produces identical results to the original when using the same parameters. All mathematical calculations and algorithms remain unchanged.

## Future Enhancements
- Additional protocol validation rules
- Support for JSON/YAML configuration formats
- Unit tests for individual functions
- Performance optimizations
- Additional plotting options

## Troubleshooting

### Common Issues
1. **Configuration file not found**: Ensure the protocol file is in the same directory
2. **Parameter validation errors**: Check the configuration file for invalid values
3. **Missing parameters**: Ensure all required parameters are defined in the config file

### Getting Help
- Check the documentation in each function
- Review the sample protocol configuration
- Compare with the original Main.m for reference

## License
Original code by Aaron Fetin, NSW Health. Refactored version maintains the same usage rights.
