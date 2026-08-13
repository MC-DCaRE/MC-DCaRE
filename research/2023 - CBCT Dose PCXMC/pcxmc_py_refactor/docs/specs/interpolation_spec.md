# Interpolation Module Specification

## Overview
The interpolation module provides resolution scaling and interpolation capabilities for dose calculations, allowing flexible adjustment of simulation resolution based on computational requirements.

## Function: res_scale

### Purpose
Rescale resolution for dose interpolation using linear interpolation to achieve target resolution.

### Function Signature
```python
def res_scale(x, y, z, num_subfields_target):
```

### Parameters
- **x** (array-like): Input x-coordinates or values to be rescaled
- **y** (array-like): Input y-coordinates or values to be rescaled  
- **z** (array-like): Input z-coordinates or dose values to be rescaled
- **num_subfields_target** (int): Target number of sub-fields for the rescaled output

### Returns
- **x_rescaled** (ndarray): Rescaled x-coordinates
- **y_rescaled** (ndarray): Rescaled y-coordinates
- **z_rescaled** (ndarray): Rescaled z-coordinates/dose values

### Algorithm
1. **Input Validation**: Ensure inputs are numpy arrays
2. **Original Resolution**: Determine original number of sub-fields from input length
3. **Interpolation Grid**: Create interpolation indices for target resolution
4. **Linear Interpolation**: Apply scipy's interp1d for smooth interpolation
5. **Output Generation**: Return rescaled arrays with target resolution

### Implementation Details
```python
# Core interpolation logic
original_indices = np.linspace(0, 1, len(x))
target_indices = np.linspace(0, 1, num_subfields_target)

# Linear interpolation
f_x = interp1d(original_indices, x, kind='linear')
f_y = interp1d(original_indices, y, kind='linear')
f_z = interp1d(original_indices, z, kind='linear')

x_rescaled = f_x(target_indices)
y_rescaled = f_y(target_indices)
z_rescaled = f_z(target_indices)
```

### Error Handling
- **ValueError**: Raised if num_subfields_target <= 0
- **TypeError**: Raised if inputs cannot be converted to arrays
- **ValueError**: Raised if input arrays have mismatched lengths

### Usage Examples

```python
import numpy as np
from src.interpolation import res_scale

# Basic usage
x = np.array([0, 1, 2, 3, 4])
y = np.array([0, 2, 4, 6, 8])
z = np.array([1, 1.5, 2, 2.5, 3])

# Rescale to 10 sub-fields
x_new, y_new, z_new = res_scale(x, y, z, 10)

# Verify output length
print(len(x_new))  # Output: 10
print(len(y_new))  # Output: 10
print(len(z_new))  # Output: 10
```

### Performance Considerations
- **Time Complexity**: O(n log n) where n is the original array length
- **Space Complexity**: O(n) for temporary arrays
- **Memory Usage**: Scales linearly with input array size

### Integration with PCXMC
The res_scale function is used to:
1. **Adjust Resolution**: Match simulation resolution to computational resources
2. **Standardize Output**: Ensure consistent output dimensions across different inputs
3. **Smooth Results**: Reduce artifacts from discrete sampling

### Dependencies
- **numpy**: Array operations and numerical computing
- **scipy.interpolate**: Linear interpolation via interp1d

### Testing Considerations
- Test with edge cases (empty arrays, single element arrays)
- Verify interpolation accuracy with known test cases
- Test performance with large arrays (>10,000 elements)
- Validate boundary conditions (first and last elements)
