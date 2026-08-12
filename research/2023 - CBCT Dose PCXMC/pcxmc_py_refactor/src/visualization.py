"""Visualization utilities for PCXMC Python implementation.

This module provides plotting functions for visualizing phantom geometry,
sub-fields, and other PCXMC-related data.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple, List
from .geometry import within_ellipse


def plot_phantom_boundary(p_width: float,
                          p_depth: float,
                          head_scan: bool = False,
                          p_head_radii2: Optional[float] = None,
                          ax: Optional[plt.Axes] = None) -> plt.Axes:
    """
    Plot the phantom boundary.
    
    Parameters
    ----------
    p_width : float
        Phantom width (cm)
    p_depth : float
        Phantom depth (cm)
    head_scan : bool, optional
        Whether this is a head scan, by default False
    p_head_radii2 : float, optional
        Posterior head radius for head scans, by default None
    ax : plt.Axes, optional
        Matplotlib axes to plot on, by default None
        
    Returns
    -------
    plt.Axes
        The axes with the plotted boundary
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
    
    if head_scan and p_head_radii2 is not None:
        # Head scan - plot anterior and posterior ellipses
        theta = np.linspace(0.01, np.pi - 0.01, 100)
        r_anterior = np.sqrt(((p_head_radii2**2) * (p_head_radii2**2)) /
                             (p_head_radii2**2 * np.cos(theta)**2 + p_head_radii2**2 * np.sin(theta)**2))
        x_anterior = r_anterior * np.cos(theta)
        y_anterior = r_anterior * np.sin(theta)
        
        theta2 = np.linspace(np.pi, 2*np.pi, 100)
        r_posterior = np.sqrt(((p_depth**2) * (p_width**2)) /
                              (p_depth**2 * np.cos(theta2)**2 + p_width**2 * np.sin(theta2)**2))
        x_posterior = r_posterior * np.cos(theta2)
        y_posterior = r_posterior * np.sin(theta2)
        
        x = np.concatenate([x_anterior, x_posterior, [x_anterior[0]]])
        y = np.concatenate([y_anterior, y_posterior, [y_anterior[0]]])
    else:
        # Body scan - single ellipse
        theta = np.linspace(0, 2*np.pi, 200)
        r = np.sqrt(((p_depth**2) * (p_width**2)) /
                    (p_depth**2 * np.cos(theta)**2 + p_width**2 * np.sin(theta)**2))
        x = r * np.cos(theta)
        y = r * np.sin(theta)
    
    ax.plot(x, y, 'k', linewidth=4, label='Phantom Boundary')
    return ax


def plot_subfields(X_coords: np.ndarray,
                   Y_coords: np.ndarray,
                   sub_field_widths: np.ndarray,
                   angles: np.ndarray,
                   nDI: np.ndarray,
                   ax: Optional[plt.Axes] = None,
                   title: str = "Sub-fields") -> plt.Axes:
    """
    Plot sub-fields with boundaries and centers.
    
    Parameters
    ----------
    X_coords : np.ndarray
        X-coordinates of sub-field centers
    Y_coords : np.ndarray
        Y-coordinates of sub-field centers
    sub_field_widths : np.ndarray
        Widths of sub-fields
    angles : np.ndarray
        Gantry angles for each sub-field
    nDI : np.ndarray
        Number of data points at each gantry angle
    ax : plt.Axes, optional
        Matplotlib axes to plot on, by default None
    title : str, optional
        Plot title, by default "Sub-fields"
        
    Returns
    -------
    plt.Axes
        The axes with the plotted sub-fields
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
    
    # Calculate sub-field boundaries
    from .geometry import sub_field_intersections
    Xs, Ys = sub_field_intersections(X_coords, Y_coords, sub_field_widths, angles, nDI)
    
    # Plot boundaries and centers
    ax.plot(Xs, Ys, '.', markersize=1, color=[0.2, 0.2, 1], label='Sub-field boundary')
    ax.plot(X_coords, Y_coords, '.', markersize=4, color=[1, 0.2, 0.2], label='Sub-field centre')
    
    ax.grid(True)
    ax.legend()
    ax.set_xlim([-25, 25])
    ax.set_ylim([-25, 25])
    ax.set_title(title)
    ax.set_xlabel('Position (cm)')
    ax.set_ylabel('Position (cm)')
    
    return ax


def plot_comparison(original_coords: np.ndarray,
                    original_widths: np.ndarray,
                    original_angles: np.ndarray,
                    original_nDI: np.ndarray,
                    final_coords: np.ndarray,
                    final_widths: np.ndarray,
                    final_angles: np.ndarray,
                    final_nDI: np.ndarray,
                    p_width: float,
                    p_depth: float,
                    head_scan: bool = False,
                    p_head_radii2: Optional[float] = None) -> Tuple[plt.Figure, List[plt.Axes]]:
    """
    Create a comparison plot of original vs final sub-fields.
    
    Parameters
    ----------
    original_coords : np.ndarray
        Original sub-field coordinates (2 x N)
    original_widths : np.ndarray
        Original sub-field widths
    original_angles : np.ndarray
        Original gantry angles
    original_nDI : np.ndarray
        Original number of data points per angle
    final_coords : np.ndarray
        Final sub-field coordinates (2 x N)
    final_widths : np.ndarray
        Final sub-field widths
    final_angles : np.ndarray
        Final gantry angles
    final_nDI : np.ndarray
        Final number of data points per angle
    p_width : float
        Phantom width
    p_depth : float
        Phantom depth
    head_scan : bool, optional
        Whether this is a head scan
    p_head_radii2 : float, optional
        Posterior head radius for head scans
        
    Returns
    -------
    tuple
        (figure, axes) tuple
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot original sub-fields
    plot_phantom_boundary(p_width, p_depth, head_scan, p_head_radii2, axes[0])
    plot_subfields(original_coords[0, :], original_coords[1, :],
                   original_widths, original_angles, original_nDI,
                   axes[0], "Original Sub-fields")
    
    # Plot final sub-fields
    plot_phantom_boundary(p_width, p_depth, head_scan, p_head_radii2, axes[1])
    plot_subfields(final_coords, final_coords,  # Note: final_coords is 1D
                   final_widths, final_angles, final_nDI,
                   axes[1], "Amended Sub-fields")
    
    plt.tight_layout()
    return fig, axes


def plot_kerma_distribution(X_coords: np.ndarray,
                            Y_coords: np.ndarray,
                            kerma_values: np.ndarray,
                            ax: Optional[plt.Axes] = None,
                            title: str = "Kerma Distribution") -> plt.Axes:
    """
    Plot kerma values as a heatmap.
    
    Parameters
    ----------
    X_coords : np.ndarray
        X-coordinates of points
    Y_coords : np.ndarray
        Y-coordinates of points
    kerma_values : np.ndarray
        Kerma values at each point
    ax : plt.Axes, optional
        Matplotlib axes to plot on, by default None
    title : str, optional
        Plot title, by default "Kerma Distribution"
        
    Returns
    -------
    plt.Axes
        The axes with the plotted heatmap
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
    
    # Create scatter plot with color based on kerma
    scatter = ax.scatter(X_coords, Y_coords, c=kerma_values, cmap='viridis',
                        s=50, alpha=0.7)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Kerma (mGy)')
    
    ax.grid(True)
    ax.set_title(title)
    ax.set_xlabel('Position (cm)')
    ax.set_ylabel('Position (cm)')
    
    return ax


def save_plots(filename_prefix: str,
               original_coords: np.ndarray,
               original_widths: np.ndarray,
               original_angles: np.ndarray,
               original_nDI: np.ndarray,
               final_coords: np.ndarray,
               final_widths: np.ndarray,
               final_angles: np.ndarray,
               final_nDI: np.ndarray,
               p_width: float,
               p_depth: float,
               head_scan: bool = False,
               p_head_radii2: Optional[float] = None) -> None:
    """
    Save comparison plots to files.
    
    Parameters
    ----------
    filename_prefix : str
        Prefix for output filenames
    original_coords : np.ndarray
        Original sub-field coordinates
    original_widths : np.ndarray
        Original sub-field widths
    original_angles : np.ndarray
        Original gantry angles
    original_nDI : np.ndarray
        Original number of data points per angle
    final_coords : np.ndarray
        Final sub-field coordinates
    final_widths : np.ndarray
        Final sub-field widths
    final_angles : np.ndarray
        Final gantry angles
    final_nDI : np.ndarray
        Final number of data points per angle
    p_width : float
        Phantom width
    p_depth : float
        Phantom depth
    head_scan : bool, optional
        Whether this is a head scan
    p_head_radii2 : float, optional
        Posterior head radius for head scans
    """
    fig, axes = plot_comparison(original_coords, original_widths, original_angles,
                               original_nDI, final_coords, final_widths,
                               final_angles, final_nDI, p_width, p_depth,
                               head_scan, p_head_radii2)
    
    fig.savefig(f"{filename_prefix}_comparison.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    # Save individual plots
    fig, ax = plt.subplots(figsize=(8, 8))
    plot_phantom_boundary(p_width, p_depth, head_scan, p_head_radii2, ax)
    plot_subfields(original_coords[0, :], original_coords[1, :],
                   original_widths, original_angles, original_nDI,
                   ax, "Original Sub-fields")
    fig.savefig(f"{filename_prefix}_original.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    plot_phantom_boundary(p_width, p_depth, head_scan, p_head_radii2, ax)
    plot_subfields(final_coords, final_coords, final_widths, final_angles,
                   final_nDI, ax, "Amended Sub-fields")
    fig.savefig(f"{filename_prefix}_amended.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
