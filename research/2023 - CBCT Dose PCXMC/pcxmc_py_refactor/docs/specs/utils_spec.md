# Utils Module Specification

## Overview
The utils module provides utility functions for mathematical operations, angle handling, and common calculations used throughout the PCXMC simulation.

## Functions

### sind(angle)
**Purpose**: Calculate sine of angle in degrees.

**Parameters**:
- `angle` (float or array-like): Angle in degrees

**Returns**:
- float or ndarray: Sine of the angle(s)

**Implementation**:
```python
return np.sin(np.radians(angle))
```

### cosd(angle)
**Purpose**: Calculate cosine of angle in degrees.

**Parameters**:
- `angle` (float or array-like): Angle in degrees

**Returns**:
- float or ndarray: Cosine of the angle(s)

**Implementation**:
```python
return np.cos(np.radians(angle))
```

### wrap_to_360(angle)
**Purpose**: Wrap angle to 0-360 degree range.

**Parameters**:
- `angle` (float or array-like): Angle in degrees (can be any value)

**Returns**:
- float or ndarray: Angle wrapped to 0-360 degrees

**Algorithm**:
```python
return angle % 360
```

## Usage Examples

```python
from src.utils import sind, cosd, wrap_to_360

# Basic trigonometric functions
angle = 45.0
sin_val = sind(angle)  # Returns: 0.7071...
cos_val = cosd(angle)  # Returns: 0.7071...

# Angle wrapping
wrapped = wrap_to_360(400.0)  # Returns: 40.0
wrapped = wrap_to_360(-30.0)  # Returns: 330.0

# Array operations
angles = np.array([0, 90, 180, 270, 360])
sines = sind(angles)  # Returns: [0, 1, 0, -1, 0]
```

## Dependencies
- **numpy**: For array operations and mathematical functions

## Testing
- Test with edge cases (0°, 90°, 180°, 270°, 360°)
- Test with negative angles
- Test with array inputs
- Verify precision for small angles
