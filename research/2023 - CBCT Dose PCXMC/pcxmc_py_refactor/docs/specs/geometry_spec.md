# Geometry Module Specification

## Overview
The geometry module provides essential geometric calculations for the PCXMC simulation, including line-ellipse intersections, point-in-ellipse checks, and coordinate transformations.

## Functions

### find_intersections(a, b, angle, X, Y)
**Purpose**: Calculate intersection points between a line and an ellipse.

**Mathematical Background**:
- Ellipse equation: x²/a² + y²/b² = 1
- Line equation: y = mx + B (where m is slope, B is y-intercept)

**Parameters**:
- `a` (float): Semi-major axis of the ellipse
- `b` (float): Semi-minor axis of the ellipse  
- `angle` (float): Gantry angle in degrees
- `X` (array-like): X-coordinates of line endpoints [x1, x2]
- `Y` (array-like): Y-coordinates of line endpoints [y1, y2]

**Returns**:
- `P` (ndarray): 2x2 array containing intersection points [[x1, x2], [y1, y2]]
- Returns [[nan, nan], [nan, nan]] if no intersections exist

**Algorithm**:
1. Handle special cases (horizontal/vertical lines)
2. Calculate line slope (m) and intercept (B)
3. Form quadratic equation: (m² + (b/a)²)x² + 2mBx + (B² - b²) = 0
4. Solve using quadratic formula
5. Order points based on angle (180-360° reverses order)

### within_ellipse(a, b, x, y)
**Purpose**: Check if a point lies within an ellipse.

**Parameters**:
- `a` (float): Semi-major axis of the ellipse
- `b` (float): Semi-minor axis of the ellipse
- `x` (float or array-like): X-coordinate(s) of point(s)
- `y` (float or array-like): Y-coordinate(s) of point(s)

**Returns**:
- bool or ndarray: True if point(s) are within ellipse, False otherwise

**Algorithm**:
Uses the ellipse equation: x²/a² + y²/b² ≤ 1

### rotate_point(x, y, angle_deg, center_x=0, center_y=0)
**Purpose**: Rotate a point around a specified center.

**Parameters**:
- `x` (float or array-like): X-coordinate(s) of point(s)
- `y` (float or array-like): Y-coordinate(s) of point(s)
- `angle_deg` (float): Rotation angle in degrees (counter-clockwise)
- `center_x` (float, optional): X-coordinate of rotation center (default: 0)
- `center_y` (float, optional): Y-coordinate of rotation center (default: 0)

**Returns**:
- tuple: (x_rotated, y_rotated) coordinates

**Algorithm**:
1. Translate point to origin: x' = x - center_x, y' = y - center_y
2. Apply rotation matrix:
   - x_rot = x'·cos(θ) - y'·sin(θ)
   - y_rot = x'·sin(θ) + y'·cos(θ)
3. Translate back: x_final = x_rot + center_x, y_final = y_rot + center_y

## Usage Examples

```python
from src.geometry import find_intersections, within_ellipse, rotate_point

# Find intersections
a, b = 10.0, 8.0  # Ellipse axes
angle = 45.0      # 45 degrees
X = [0, 5]        # Line from (0,0) to (5,0)
Y = [0, 0]
intersections = find_intersections(a, b, angle, X, Y)

# Check if point is within ellipse
x, y = 3.0, 2.0
is_inside = within_ellipse(a, b, x, y)

# Rotate a point
x, y = 5.0, 0.0
rotated = rotate_point(x, y, 90.0)  # Rotate 90 degrees around origin
```

## Error Handling
- All functions handle NaN inputs gracefully
- Division by zero is prevented in slope calculations
- Array inputs are automatically converted to numpy arrays
