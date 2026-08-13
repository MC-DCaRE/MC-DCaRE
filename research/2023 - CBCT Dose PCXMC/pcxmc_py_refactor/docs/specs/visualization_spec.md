# Visualization Module Specification

## Overview
The visualization module provides plotting and visualization utilities for dose distributions, phantom geometries, and simulation results. It supports both 2D and 3D visualization with customizable styling.

## Functions

### plot_dose_distribution
**Purpose**: Create 2D visualization of dose distribution with phantom overlay.

**Function Signature**:
```python
def plot_dose_distribution(dose_data, phantom_geometry, title=None, save_path=None):
```

**Parameters**:
- **dose_data** (ndarray): 2D array of dose values (shape: [height, width])
- **phantom_geometry** (dict): Phantom dimensions and positioning
  - Required keys: 'width', 'height', 'depth'
- **title** (str, optional): Plot title
- **save_path** (str, optional): Path to save the plot

**Returns**:
- matplotlib.figure.Figure: The generated figure object

**Features**:
- Heatmap visualization of dose distribution
- Phantom boundary overlay
- Color bar with dose units
- Customizable color schemes
- Automatic scaling

### plot_3d_dose
**Purpose**: Create 3D visualization of dose distribution.

**Function Signature**:
```python
def plot_3d_dose(dose_data, phantom_geometry, title=None, save_path=None):
```

**Parameters**:
- **dose_data** (ndarray): 3D array of dose values (shape: [depth, height, width])
- **phantom_geometry** (dict): Phantom dimensions and positioning
- **title** (str, optional): Plot title
- **save_path** (str, optional): Path to save the plot

**Features**:
- 3D surface/volume rendering
- Interactive rotation
- Isosurface visualization
- Transparency control

### plot_geometry
**Purpose**: Visualize phantom geometry and beam configuration.

**Function Signature**:
```python
def plot_geometry(phantom_geometry, beam_config, title=None, save_path=None):
```

**Parameters**:
- **phantom_geometry** (dict): Phantom dimensions and positioning
- **beam_config** (dict): Beam configuration parameters
- **title** (str, optional): Plot title
- **save_path** (str, optional): Path to save the plot

**Features**:
- Phantom outline visualization
- Beam position and orientation
- Sub-field visualization
- Coordinate system display

### save_plots
**Purpose**: Save multiple plots to specified directory.

**Function Signature**:
```python
def save_plots(plots_dict, output_dir, prefix="dose_plot"):
```

**Parameters**:
- **plots_dict** (dict): Dictionary of plot objects
- **output_dir** (str): Output directory path
- **prefix** (str, optional): Filename prefix

**Returns**:
- List[str]: List of saved file paths

## Styling and Customization

### Color Schemes
- **Default**: Viridis colormap
- **High contrast**: Plasma colormap
- **Grayscale**: Gray colormap
- **Custom**: User-defined colormaps

### Figure Settings
- **Default size**: 10x8 inches
- **DPI**: 300 for publication quality
- **Font size**: 12pt for labels
- **Color bar**: Always included

## Usage Examples

```python
import numpy as np
from src.visualization import plot_dose_distribution, save_plots

# Basic 2D dose plot
dose_data = np.random.rand(100, 50)
phantom = {'width': 40, 'height': 20, 'depth': 15}
fig = plot_dose_distribution(dose_data, phantom, 
                           title="Dose Distribution - Head Scan")

# Save plot
save_plots({'dose_2d': fig}, './outputs', prefix='head_scan')

# 3D visualization
dose_3d = np.random.rand(50, 100, 50)
fig_3d = plot_3d_dose(dose_3d, phantom, title="3D Dose Distribution")
```

## Dependencies
- **matplotlib**: 2D/3D plotting
- **numpy**: Array operations
- **mpl_toolkits.mplot3d**: 3D plotting support

## Output Formats
- **PNG**: Default format for quick viewing
- **PDF**: Vector format for publications
- **SVG**: Vector format for web use
- **JPG**: Compressed format for presentations

## Error Handling
- **ValueError**: Invalid data dimensions
- **TypeError**: Incorrect parameter types
- **IOError**: File save errors
- **MemoryError**: Large dataset handling

## Performance Considerations
- **Memory usage**: Scales with data size
- **Rendering time**: 3D plots slower than 2D
- **File size**: PNG ~1-5MB, PDF ~100KB-2MB
- **Batch processing**: Use save_plots for efficiency
