"""Geometry operations for PCXMC Python implementation.

This module contains functions for calculating intersections between lines
and ellipses, and checking if points are within ellipses.
"""

import numpy as np
from .utils import sind, cosd


def find_intersections(a, b, angle, X, Y):
    """
    Find the intersection between the line of sub-field coordinates for a 
    given gantry angle and the phantom's surface.
    
    Parameters
    ----------
    a : float
        Semi-major axis of the ellipse
    b : float
        Semi-minor axis of the ellipse
    angle : float
        Gantry angle in degrees
    X : array-like
        X-coordinates of the line endpoints [x1, x2]
    Y : array-like
        Y-coordinates of the line endpoints [y1, y2]
        
    Returns
    -------
    P : ndarray
        2x2 array containing intersection points [x1, x2; y1, y2]
        
    Notes
    -----
    The ellipse equation is x²/a² + y²/b² = 1
    """
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    
    if Y[0] == Y[1]:  # if line is horizontal
        if -b < Y[0] < b:  # check horizontal line intersects ellipse
            x1 = np.sqrt((1 - (Y[0]/b)**2) * a**2)
            x2 = -x1
            y1 = Y[0]
            y2 = y1
        else:
            # No intersection - return empty array
            return np.array([[np.nan, np.nan], [np.nan, np.nan]])
            
    elif X[0] == X[1]:  # if line is vertical
        if -a < X[0] < a:  # check vertical line intersects ellipse
            y2 = np.sqrt((1 - (X[0]/a)**2) * b**2)
            y1 = -y2
            x1 = X[0]
            x2 = x1
        else:
            # No intersection - return empty array
            return np.array([[np.nan, np.nan], [np.nan, np.nan]])
            
    else:  # general case - line with slope
        m = (Y[1] - Y[0]) / (X[1] - X[0])  # slope of the line
        B = Y[0] - m * X[0]  # intercept of the line
        
        # Coefficients for quadratic equation: aQX*x² + bQX*x + cQX = 0
        aQX = m**2 + (b/a)**2
        bQX = 2 * m * B
        cQX = B**2 - b**2
        
        discriminant = bQX**2 - 4 * aQX * cQX
        
        if discriminant > 0:  # real intersections exist
            x2 = (-bQX - np.sqrt(discriminant)) / (2 * aQX)  # first x coordinate
            x1 = (-bQX + np.sqrt(discriminant)) / (2 * aQX)  # second x coordinate
            y2 = x2 * m + B  # first y coordinate
            y1 = x1 * m + B  # second y coordinate
        else:
            # No real intersections - return empty array
            return np.array([[np.nan, np.nan], [np.nan, np.nan]])
    
    # Order points based on angle
    if 180 <= angle < 360:
        P = np.array([[x2, x1], [y2, y1]])
    else:
        P = np.array([[x1, x2], [y1, y2]])
    
    return P


def within_ellipse(a, b, x, y):
    """
    Check if a point (x, y) is within an ellipse with semi-axes a and b.
    
    Parameters
    ----------
    a : float
        Semi-major axis of the ellipse
    b : float
        Semi-minor axis of the ellipse
    x : float or array-like
        X-coordinate(s) of the point(s)
    y : float or array-like
        Y-coordinate(s) of the point(s)
        
    Returns
    -------
    bool or ndarray
        True if point(s) are within the ellipse, False otherwise
        
    Notes
    -----
    The ellipse equation is x²/a² + y²/b² ≤ 1
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    
    return (x**2 / a**2 + y**2 / b**2) <= 1


def rotate_point(x, y, angle_deg, center_x=0, center_y=0):
    """
    Rotate a point around a center by a given angle.
    
    Parameters
    ----------
    x : float or array-like
        X-coordinate(s) of the point(s)
    y : float or array-like
        Y-coordinate(s) of the point(s)
    angle_deg : float
        Rotation angle in degrees (counter-clockwise)
    center_x : float, optional
        X-coordinate of rotation center (default: 0)
    center_y : float, optional
        Y-coordinate of rotation center (default: 0)
        
    Returns
    -------
    tuple
        (x_rotated, y_rotated) coordinates
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    
    # Translate to origin
    x_translated = x - center_x
    y_translated = y - center_y
    
    # Rotate
    cos_theta = cosd(angle_deg)
    sin_theta = sind(angle_deg)
    
    x_rotated = x_translated * cos_theta - y_translated * sin_theta
    y_rotated = x_translated * sin_theta + y_translated * cos_theta
    
    # Translate back
    x_final = x_rotated + center_x
    y_final = y_rotated + center_y
    
    return x_final, y_final


def sub_field_intersection(X, Y, sFW, a, d):
    """
    Find the coordinate of the boundary between two sub-fields.
    
    This function calculates the boundary point for a sub-field based on
    the sub-field width and gantry angle.
    
    Parameters
    ----------
    X : float
        X-coordinate of the sub-field center
    Y : float
        Y-coordinate of the sub-field center
    sFW : float
        Sub-field width
    a : float
        Gantry angle in degrees
    d : float
        Distance parameter (typically 1/2 for boundary calculation)
        
    Returns
    -------
    ndarray
        2x1 array containing [Xf; Yf] boundary coordinates
        
    Notes
    -----
    Based on MATLAB function subFieldIntersection by Aaron Fetin, revised July 2022.
    """
    Yf = Y - d * (sFW / 2) * sind(a + 90)
    Xf = X - d * (sFW / 2) * cosd(a + 90)
    
    return np.array([[Xf], [Yf]])


def sub_field_intersections(X, Y, sFW, a, nDI):
    """
    Find the coordinates of the boundaries of sub-fields.
    
    This function calculates boundary points for all sub-fields based on
    sub-field coordinates, widths, gantry angles, and number of data elements.
    
    Parameters
    ----------
    X : array-like
        X-coordinates of sub-field centers
    Y : array-like
        Y-coordinates of sub-field centers
    sFW : array-like
        Sub-field widths
    a : array-like
        Gantry angles in degrees
    nDI : array-like
        Number of data elements at each gantry angle
        
    Returns
    -------
    tuple
        (Xf, Yf) arrays containing boundary coordinates
        
    Notes
    -----
    Based on MATLAB function subFieldIntersections by Aaron Fetin, revised July 2022.
    """
    X = np.asarray(X, dtype=float).flatten()
    Y = np.asarray(Y, dtype=float).flatten()
    sFW = np.asarray(sFW, dtype=float).flatten()
    a = np.asarray(a, dtype=float).flatten()
    nDI = np.asarray(nDI, dtype=int).flatten()
    
    s = np.sum(nDI) + len(nDI)  # Total size of the array needed
    
    Yf = np.zeros(s)
    Xf = np.zeros(s)
    
    k = 0  # Iterate through the output array
    i = 0  # Iterate through the input array
    
    for n in range(len(nDI)):  # Iterate through gantry angles
        for j in range(nDI[n]):  # Iterate through sub-fields at each angle
            k += 1
            i += 1
            # Boundary 'behind' the current coordinate
            Yf[k-1] = Y[i-1] - (sFW[i-1] / 2) * sind(a[i-1] + 90)
            Xf[k-1] = X[i-1] - (sFW[i-1] / 2) * cosd(a[i-1] + 90)
        
        k += 1
        # Boundary 'after' the last coordinate at given gantry angle
        Yf[k-1] = Y[i-1] + (sFW[i-1] / 2) * sind(a[i-1] + 90)
        Xf[k-1] = X[i-1] + (sFW[i-1] / 2) * cosd(a[i-1] + 90)
    
    return Xf, Yf
