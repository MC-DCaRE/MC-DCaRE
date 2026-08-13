"""Utility functions for PCXMC Python implementation.

This module contains common utility functions used throughout the project,
particularly trigonometric functions that work with degrees.
"""

import numpy as np


def sind(angle_deg):
    """
    Sine function that takes angle in degrees.
    
    Parameters
    ----------
    angle_deg : float or array-like
        Angle in degrees
        
    Returns
    -------
    float or ndarray
        Sine of the angle
    """
    return np.sin(np.radians(angle_deg))


def cosd(angle_deg):
    """
    Cosine function that takes angle in degrees.
    
    Parameters
    ----------
    angle_deg : float or array-like
        Angle in degrees
        
    Returns
    -------
    float or ndarray
        Cosine of the angle
    """
    return np.cos(np.radians(angle_deg))


def tand(angle_deg):
    """
    Tangent function that takes angle in degrees.
    
    Parameters
    ----------
    angle_deg : float or array-like
        Angle in degrees
        
    Returns
    -------
    float or ndarray
        Tangent of the angle
    """
    return np.tan(np.radians(angle_deg))


def asind(x):
    """
    Arcsine function that returns angle in degrees.
    
    Parameters
    ----------
    x : float or array-like
        Input value(s) between -1 and 1
        
    Returns
    -------
    float or ndarray
        Angle in degrees
    """
    return np.degrees(np.arcsin(x))


def acosd(x):
    """
    Arccosine function that returns angle in degrees.
    
    Parameters
    ----------
    x : float or array-like
        Input value(s) between -1 and 1
        
    Returns
    -------
    float or ndarray
        Angle in degrees
    """
    return np.degrees(np.arccos(x))


def atand(x):
    """
    Arctangent function that returns angle in degrees.
    
    Parameters
    ----------
    x : float or array-like
        Input value(s)
        
    Returns
    -------
    float or ndarray
        Angle in degrees
    """
    return np.degrees(np.arctan(x))


def atan2d(y, x):
    """
    Four-quadrant arctangent function that returns angle in degrees.
    
    Parameters
    ----------
    y : float or array-like
        Y-coordinate(s)
    x : float or array-like
        X-coordinate(s)
        
    Returns
    -------
    float or ndarray
        Angle in degrees, in the range [-180, 180]
    """
    return np.degrees(np.arctan2(y, x))


def wrap_to_360(angle_deg):
    """
    Wrap angle to [0, 360) degrees.
    
    Parameters
    ----------
    angle_deg : float or array-like
        Angle in degrees
        
    Returns
    -------
    float or ndarray
        Wrapped angle in [0, 360) degrees
    """
    angle_deg = np.asarray(angle_deg, dtype=float)
    return angle_deg % 360
