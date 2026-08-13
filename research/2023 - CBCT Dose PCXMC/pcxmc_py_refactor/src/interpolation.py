"""Interpolation utilities for PCXMC Python implementation.

This module provides functions for scaling resolution and interpolating
values for sub-field data.
"""

import numpy as np
from typing import Tuple


def res_scale(sub_field_coords: np.ndarray,
              sub_field_widths: np.ndarray,
              kerma: np.ndarray,
              filtration: np.ndarray,
              num_sub_fields: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Scale the resolution of sub-field data using linear interpolation.
    
    This function increases or decreases the resolution of the input subfield data
    by linearly interpolating extra values. The full field extent is divided into
    evenly spaced points and the values determined by linear interpolation.
    The field extent is therefore maintained.
    
    Parameters
    ----------
    sub_field_coords : np.ndarray
        Original sub-field coordinates (2 x N array)
    sub_field_widths : np.ndarray
        Original sub-field widths (1 x N array)
    kerma : np.ndarray
        Original kerma values (1 x N array)
    filtration : np.ndarray
        Original filtration values (1 x N array)
    num_sub_fields : int
        Target number of sub-fields
        
    Returns
    -------
    tuple
        (sub_field_coords, sub_field_widths, kerma, filtration) with scaled resolution
    """
    # Extract Y coordinates (second row)
    X = sub_field_coords[1, :]
    
    # Calculate field extent
    Xmin = np.min(X) - sub_field_widths[0] / 2
    Xmax = np.max(X) + sub_field_widths[-1] / 2
    
    # Create evenly spaced points
    step = (Xmax - Xmin) / num_sub_fields
    new_coords = np.linspace(Xmin + step/2, Xmax - step/2, num_sub_fields)
    
    # Calculate new widths (all equal)
    new_widths = np.ones(num_sub_fields) * step
    
    # Interpolate kerma and filtration values
    new_kerma = np.interp(new_coords, sub_field_coords[1, :], kerma,
                          left=kerma[0], right=kerma[-1])
    new_filtration = np.interp(new_coords, sub_field_coords[1, :], filtration,
                               left=filtration[0], right=filtration[-1])
    
    # Create new coordinate array (X=0 for all points)
    new_coords_array = np.vstack([np.zeros(num_sub_fields), new_coords])
    
    return new_coords_array, new_widths, new_kerma, new_filtration


def linear_interpolate_1d(x_old: np.ndarray,
                          y_old: np.ndarray,
                          x_new: np.ndarray) -> np.ndarray:
    """
    Perform 1D linear interpolation.
    
    Parameters
    ----------
    x_old : np.ndarray
        Original x-coordinates
    y_old : np.ndarray
        Original y-values
    x_new : np.ndarray
        New x-coordinates for interpolation
        
    Returns
    -------
    np.ndarray
        Interpolated y-values at x_new
    """
    return np.interp(x_new, x_old, y_old, left=y_old[0], right=y_old[-1])


def bilinear_interpolate(x: float, y: float,
                         x1: float, x2: float,
                         y1: float, y2: float,
                         f11: float, f12: float,
                         f21: float, f22: float) -> float:
    """
    Perform bilinear interpolation.
    
    Parameters
    ----------
    x, y : float
        Point coordinates for interpolation
    x1, x2 : float
        X-coordinates of bounding rectangle
    y1, y2 : float
        Y-coordinates of bounding rectangle
    f11, f12, f21, f22 : float
        Function values at corners of bounding rectangle
        
    Returns
    -------
    float
        Interpolated value at (x, y)
    """
    # Ensure x1 <= x <= x2 and y1 <= y <= y2
    if x1 > x2:
        x1, x2 = x2, x1
        f11, f21 = f21, f11
        f12, f22 = f22, f12
    
    if y1 > y2:
        y1, y2 = y2, y1
        f11, f12 = f12, f11
        f21, f22 = f22, f21
    
    # Perform bilinear interpolation
    t = (x - x1) / (x2 - x1) if x2 != x1 else 0.0
    u = (y - y1) / (y2 - y1) if y2 != y1 else 0.0
    
    return (1 - t) * (1 - u) * f11 + \
           t * (1 - u) * f21 + \
           (1 - t) * u * f12 + \
           t * u * f22
