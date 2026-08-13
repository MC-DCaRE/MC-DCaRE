"""Main PCXMC runner for Python implementation.

This module provides the main functionality for generating PCXMC input data
based on scan parameters and phantom geometry.
"""

import numpy as np
from typing import Dict, Any, Tuple, Optional
from .utils import sind, cosd, wrap_to_360
from .geometry import find_intersections, within_ellipse, rotate_point
from .interpolation import res_scale
from .config_loader import ConfigLoader

class PCXMCRunner:
    """Main class for running PCXMC simulations."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize PCXMC runner with configuration.
        
        Parameters
        ----------
        config : dict
            Configuration dictionary containing all simulation parameters
        """
        self.config = config
        self._validate_config()
        
    def _validate_config(self):
        """Validate the configuration parameters."""
        required_keys = [
            'iso', 'z', 'arms', 'kV', 'FRD', 'headScan',
            'startingAngle', 'finalAngle', 'numAnglesSimmed',
            'numAnglesTrue', 'subFieldCoords', 'subFieldWidths',
            'width', 'kerma', 'filtration', 'pWidth', 'pDepth',
            'height', 'mass', 'age'
        ]
        
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required configuration key: {key}")
    
    def compute_gantry_angles(self) -> np.ndarray:
        """Compute gantry angles to be simulated."""
        starting_angle = self.config['startingAngle']
        final_angle = self.config['finalAngle']
        num_angles = self.config['numAnglesSimmed']
        
        if (final_angle - starting_angle) % 360 == 0:
            # Closed loop rotation
            dA = (final_angle - starting_angle) / num_angles
            angles = np.arange(starting_angle, final_angle, dA)
        else:
            # Partial arc rotation
            dA = (final_angle - starting_angle) / (num_angles - 1)
            angles = np.arange(starting_angle, final_angle + dA, dA)
        
        return wrap_to_360(angles)
    
    def scale_resolution(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
        """Scale resolution if enabled."""
        if self.config.get('resolutionScaling', False):
            sub_coords, sub_widths, kerma, filtration = res_scale(
                self.config['subFieldCoords'],
                self.config['subFieldWidths'],
                self.config['kerma'],
                self.config['filtration'],
                self.config['numSubFields']
            )
            num_sub_fields = self.config['numSubFields']
        else:
            sub_coords = self.config['subFieldCoords']
            sub_widths = self.config['subFieldWidths']
            kerma = self.config['kerma']
            filtration = self.config['filtration']
            num_sub_fields = sub_coords.shape[1]
        
        return sub_coords, sub_widths, kerma, filtration, num_sub_fields
    
    def calculate_subfield_coordinates(self, angles: np.ndarray, 
                                     sub_coords: np.ndarray) -> np.ndarray:
        """Calculate coordinates of sub-fields at gantry angles."""
        num_angles = len(angles)
        num_sub_fields = sub_coords.shape[1]
        
        Coords = np.zeros((2, num_angles * num_sub_fields))
        
        j = 0
        for angle in angles:
            cos_a = cosd(angle)
            sin_a = sind(angle)
            for i in range(num_sub_fields):
                # Apply rotation and translation
                rotated = np.array([
                    [cos_a, -sin_a],
                    [sin_a, cos_a]
                ]) @ sub_coords[:, i] + self.config['iso']
                Coords[:, j] = rotated
                j += 1
        
        return Coords
    
    def amend_subfields(self, Coords: np.ndarray, sub_widths: np.ndarray,
                       kerma: np.ndarray, filtration: np.ndarray,
                       angles: np.ndarray) -> Dict[str, Any]:
        """Process sub-fields to ensure they are within phantom boundaries."""
        
        # Initialize arrays
        num_angles = len(angles)
        num_sub_fields = len(sub_widths)
        total_points = num_angles * num_sub_fields
        
        XCoordsFinal = np.zeros(total_points)
        YCoordsFinal = np.zeros(total_points + 2 * num_angles)  # Buffer for edge cases
        FiltFinal = np.zeros(total_points)
        KermaFinal = np.zeros(total_points)
        sFWFinal = np.zeros(total_points)
        anglesFinal = np.zeros(total_points)
        anglesTemp = np.zeros(total_points)
        sF = np.zeros(total_points)
        
        # Initialize counters
        nD = 0  # Total valid data points
        nDI = [0]  # Points per angle (with leading zero)
        aC = 0  # Angle counter
        
        # Main processing loop
        for n in range(0, total_points, num_sub_fields):
            aC += 1
            for k in range(num_sub_fields):
                j = n + k
                
                # Adjust phantom dimensions for head scans
                pWidthTemp = self.config['pWidth']
                pDepthTemp = self.config['pDepth']
                
                if self.config['headScan']:
                    if Coords[1, j] > 0:  # Posterior head region
                        pWidthTemp = self.config.get('pHeadRadii2', self.config['pWidth'])
                        pDepthTemp = pWidthTemp
                    else:  # Anterior head region
                        pWidthTemp = self.config['pWidth']
                        pDepthTemp = self.config['pDepth']
                
                # Store temporary values
                anglesTemp[j] = angles[aC - 1]
                sF[j] = sub_widths[k]
                
                # Check if coordinate is within phantom ellipse
                if within_ellipse(pWidthTemp, pDepthTemp, Coords[0, j], Coords[1, j]):
                    # Coordinate is inside phantom
                    nD += 1
                    XCoordsFinal[nD - 1] = Coords[0, j]
                    YCoordsFinal[nD - 1] = Coords[1, j]
                    FiltFinal[nD - 1] = filtration[k]
                    KermaFinal[nD - 1] = kerma[k]
                    sFWFinal[nD - 1] = sub_widths[k]
                    anglesFinal[nD - 1] = angles[aC - 1]
                    
                else:
                    # Coordinate is outside phantom - check adjacent sub-fields
                    if k == 0:  # First sub-field
                        if j + 1 < total_points and within_ellipse(pWidthTemp, pDepthTemp, Coords[0, j + 1], Coords[1, j + 1]):
                            # Calculate intersection point
                            x = self._subfield_intersection(
                                np.array([Coords[0, j], Coords[0, j + 1]]),
                                np.array([Coords[1, j], Coords[1, j + 1]]),
                                sub_widths[k], angles[aC - 1], -1
                            )
                            
                            if within_ellipse(pWidthTemp, pDepthTemp, x[0], x[1]):
                                p = find_intersections(
                                    pWidthTemp, pDepthTemp, angles[aC - 1],
                                    np.array([Coords[0, j], Coords[0, j + 1]]),
                                    np.array([Coords[1, j], Coords[1, j + 1]])
                                )
                                
                                if p.size > 0:
                                    nD += 1
                                    XCoordsFinal[nD - 1] = p[0, 0]
                                    YCoordsFinal[nD - 1] = p[1, 0]
                                    
                                    # Calculate adjusted width
                                    sFWFinal[nD - 1] = 2 * np.sqrt(
                                        (p[0, 0] - x[0])**2 + (p[1, 0] - x[1])**2
                                    )
                                    anglesFinal[nD - 1] = angles[aC - 1]
                                    
                                    # Handle interpolation
                                    if self.config.get('interpolation', False):
                                        d1 = np.sqrt(
                                            (Coords[0, j + 1] - Coords[0, j])**2 +
                                            (Coords[1, j + 1] - Coords[1, j])**2
                                        )
                                        d2 = np.sqrt(
                                            (p[0, 0] - Coords[0, j])**2 +
                                            (p[1, 0] - Coords[1, j])**2
                                        )
                                        
                                        if d1 > 0:
                                            m1 = (kerma[k + 1] - kerma[k]) / d1
                                            m2 = (filtration[k + 1] - filtration[k]) / d1
                                            KermaFinal[nD - 1] = kerma[k] + m1 * d2
                                            FiltFinal[nD - 1] = filtration[k] + m2 * d2
                                        else:
                                            KermaFinal[nD - 1] = kerma[k]
                                            FiltFinal[nD - 1] = filtration[k]
                                    else:
                                        KermaFinal[nD - 1] = kerma[k]
                                        FiltFinal[nD - 1] = filtration[k]
                    
                    elif k == num_sub_fields - 1:  # Last sub-field
                        if within_ellipse(pWidthTemp, pDepthTemp, Coords[0, j - 1], Coords[1, j - 1]):
                            x = self._subfield_intersection(
                                np.array([Coords[0, j], Coords[0, j - 1]]),
                                np.array([Coords[1, j], Coords[1, j - 1]]),
                                sub_widths[k], angles[aC - 1], 1
                            )
                            
                            if within_ellipse(pWidthTemp, pDepthTemp, x[0], x[1]):
                                p = find_intersections(
                                    pWidthTemp, pDepthTemp, angles[aC - 1],
                                    np.array([Coords[0, j], Coords[0, j - 1]]),
                                    np.array([Coords[1, j], Coords[1, j - 1]])
                                )
                                
                                if p.size > 0 and p.shape[1] >= 2:
                                    nD += 1
                                    XCoordsFinal[nD - 1] = p[0, 1]
                                    YCoordsFinal[nD - 1] = p[1, 1]
                                    
                                    sFWFinal[nD - 1] = 2 * np.sqrt(
                                        (p[0, 1] - x[0])**2 + (p[1, 1] - x[1])**2
                                    )
                                    anglesFinal[nD - 1] = angles[aC - 1]
                                    
                                    if self.config.get('interpolation', False):
                                        d1 = np.sqrt(
                                            (Coords[0, j] - Coords[0, j - 1])**2 +
                                            (Coords[1, j] - Coords[1, j - 1])**2
                                        )
                                        d2 = np.sqrt(
                                            (p[0, 1] - Coords[0, j])**2 +
                                            (p[1, 1] - Coords[1, j])**2
                                        )
                                        
                                        if d1 > 0:
                                            m1 = (kerma[k - 1] - kerma[k]) / d1
                                            m2 = (filtration[k - 1] - filtration[k]) / d1
                                            KermaFinal[nD - 1] = kerma[k] + m1 * d2
                                            FiltFinal[nD - 1] = filtration[k] + m2 * d2
                                        else:
                                            KermaFinal[nD - 1] = kerma[k]
                                            FiltFinal[nD - 1] = filtration[k]
                                    else:
                                        KermaFinal[nD - 1] = kerma[k]
                                        FiltFinal[nD - 1] = filtration[k]
                    
                    else:  # Middle sub-fields
                        # Check next sub-field
                        if within_ellipse(pWidthTemp, pDepthTemp, Coords[0, j + 1], Coords[1, j + 1]):
                            x = self._subfield_intersection(
                                np.array([Coords[0, j], Coords[0, j + 1]]),
                                np.array([Coords[1, j], Coords[1, j + 1]]),
                                sub_widths[k], angles[aC - 1], -1
                            )
                            
                            if within_ellipse(pWidthTemp, pDepthTemp, x[0], x[1]):
                                p = find_intersections(
                                    pWidthTemp, pDepthTemp, angles[aC - 1],
                                    np.array([Coords[0, j], Coords[0, j + 1]]),
                                    np.array([Coords[1, j], Coords[1, j + 1]])
                                )
                                
                                if p.size > 0:
                                    nD += 1
                                    XCoordsFinal[nD - 1] = p[0, 0]
                                    YCoordsFinal[nD - 1] = p[1, 0]
                                    
                                    sFWFinal[nD - 1] = 2 * np.sqrt(
                                        (p[0, 0] - x[0])**2 + (p[1, 0] - x[1])**2
                                    )
                                    anglesFinal[nD - 1] = angles[aC - 1]
                                    
                                    if self.config.get('interpolation', False):
                                        d1 = np.sqrt(
                                            (Coords[0, j + 1] - Coords[0, j])**2 +
                                            (Coords[1, j + 1] - Coords[1, j])**2
                                        )
                                        d2 = np.sqrt(
                                            (p[0, 0] - Coords[0, j])**2 +
                                            (p[1, 0] - Coords[1, j])**2
                                        )
                                        
                                        if d1 > 0:
                                            m1 = (kerma[k + 1] - kerma[k]) / d1
                                            m2 = (filtration[k + 1] - filtration[k]) / d1
                                            KermaFinal[nD - 1] = kerma[k] + m1 * d2
                                            FiltFinal[nD - 1] = filtration[k] + m2 * d2
                                        else:
                                            KermaFinal[nD - 1] = kerma[k]
                                            FiltFinal[nD - 1] = filtration[k]
                                    else:
                                        KermaFinal[nD - 1] = kerma[k]
                                        FiltFinal[nD - 1] = filtration[k]
                                        
                        elif within_ellipse(pWidthTemp, pDepthTemp, Coords[0, j - 1], Coords[1, j - 1]):
                            x = self._subfield_intersection(
                                np.array([Coords[0, j], Coords[0, j - 1]]),
                                np.array([Coords[1, j], Coords[1, j - 1]]),
                                sub_widths[k], angles[aC - 1], 1
                            )
                            
                            if within_ellipse(pWidthTemp, pDepthTemp, x[0], x[1]):
                                p = find_intersections(
                                    pWidthTemp, pDepthTemp, angles[aC - 1],
                                    np.array([Coords[0, j], Coords[0, j - 1]]),
                                    np.array([Coords[1, j], Coords[1, j - 1]])
                                )
                                
                                if p.size > 0 and p.shape[1] >= 2:
                                    nD += 1
                                    XCoordsFinal[nD - 1] = p[0, 1]
                                    YCoordsFinal[nD - 1] = p[1, 1]
                                    
                                    sFWFinal[nD - 1] = 2 * np.sqrt(
                                        (p[0, 1] - x[0])**2 + (p[1, 1] - x[1])**2
                                    )
                                    anglesFinal[nD - 1] = angles[aC - 1]
                                    
                                    if self.config.get('interpolation', False):
                                        d1 = np.sqrt(
                                            (Coords[0, j] - Coords[0, j - 1])**2 +
                                            (Coords[1, j] - Coords[1, j - 1])**2
                                        )
                                        d2 = np.sqrt(
                                            (p[0, 1] - Coords[0, j])**2 +
                                            (p[1, 1] - Coords[1, j])**2
                                        )
                                        
                                        if d1 > 0:
                                            m1 = (kerma[k - 1] - kerma[k]) / d1
                                            m2 = (filtration[k - 1] - filtration[k]) / d1
                                            KermaFinal[nD - 1] = kerma[k] + m1 * d2
                                            FiltFinal[nD - 1] = filtration[k] + m2 * d2
                                        else:
                                            KermaFinal[nD - 1] = kerma[k]
                                            FiltFinal[nD - 1] = filtration[k]
                                    else:
                                        KermaFinal[nD - 1] = kerma[k]
                                        FiltFinal[nD - 1] = filtration[k]
            
            # Record number of points for this angle
            nDI.append(nD - sum(nDI))
        
        # Clean up arrays - remove unused elements
        nDI = np.array(nDI[1:])  # Remove leading zero
        XCoordsFinal = XCoordsFinal[:nD]
        YCoordsFinal = YCoordsFinal[:nD]
        FiltFinal = FiltFinal[:nD]
        KermaFinal = KermaFinal[:nD]
        sFWFinal = sFWFinal[:nD]
        anglesFinal = anglesFinal[:nD]
        
        return {
            'XCoordsFinal': XCoordsFinal,
            'YCoordsFinal': YCoordsFinal,
            'FiltFinal': FiltFinal,
            'KermaFinal': KermaFinal,
            'sFWFinal': sFWFinal,
            'anglesFinal': anglesFinal,
            'nDI': nDI,
            'nD': nD
        }
    
    def _subfield_intersection(self, x_coords: np.ndarray, y_coords: np.ndarray,
                             width: float, angle: float, direction: int) -> np.ndarray:
        """Calculate sub-field intersection point (MATLAB subFieldIntersection equivalent)."""
        # Calculate the intersection point based on direction
        dx = x_coords[1] - x_coords[0]
        dy = y_coords[1] - y_coords[0]
        
        # Calculate distance between points
        distance = np.sqrt(dx**2 + dy**2)
        
        if distance == 0:
            return np.array([x_coords[0], y_coords[0]])
        
        # Calculate unit vector
        ux = dx / distance
        uy = dy / distance
        
        # Calculate intersection point
        if direction == -1:  # Forward direction
            x = x_coords[0] + ux * width / 2
            y = y_coords[0] + uy * width / 2
        else:  # Backward direction
            x = x_coords[0] - ux * width / 2
            y = y_coords[0] - uy * width / 2
            
        return np.array([x, y])
    
    def generate_pcxmc_matrix(self, results: Dict[str, Any]) -> np.ndarray:
        """Generate the 20-column PCXMC input matrix."""
        
        # Extract results
        XCoordsFinal = results['XCoordsFinal']
        YCoordsFinal = results['YCoordsFinal']
        FiltFinal = results['FiltFinal']
        KermaFinal = results['KermaFinal']
        sFWFinal = results['sFWFinal']
        anglesFinal = results['anglesFinal']
        
        # Round angles to 12 significant digits to match MATLAB
        anglesFinal = np.round(anglesFinal, 12)
        
        # Create PCXMC input matrix
        n_points = len(XCoordsFinal)
        PCXMCInput = np.zeros((n_points, 20))
        
        # Map variables to PCXMC columns (matching MATLAB exactly)
        PCXMCInput[:, 2] = anglesFinal  # Column 3: Gantry angle
        PCXMCInput[:, 3] = self.config.get('oblique', 0)  # Column 4: Oblique angle
        PCXMCInput[:, 4] = 1  # Column 5: Patient ID (dummy value)
        PCXMCInput[:, 5] = self.config['height']  # Column 6: Patient height
        PCXMCInput[:, 6] = self.config['mass']  # Column 7: Patient mass
        PCXMCInput[:, 7] = self.config['age']  # Column 8: Patient age
        PCXMCInput[:, 8] = self.config['kV']  # Column 9: Tube voltage
        PCXMCInput[:, 9] = FiltFinal  # Column 10: Total filtration
        PCXMCInput[:, 10] = 0  # Column 11: Reserved
        PCXMCInput[:, 11] = self.config['FRD']  # Column 12: Focus-to-reference distance
        PCXMCInput[:, 12] = sFWFinal  # Column 13: Sub-field width
        PCXMCInput[:, 13] = self.config['width']  # Column 14: Field width at isocentre
        PCXMCInput[:, 14] = XCoordsFinal  # Column 15: X-coordinate
        PCXMCInput[:, 15] = YCoordsFinal  # Column 16: Y-coordinate
        PCXMCInput[:, 16] = self.config['z']  # Column 17: Z-coordinate
        PCXMCInput[:, 17] = self.config['arms']  # Column 18: Arms included
        PCXMCInput[:, 19] = KermaFinal  # Column 20: Air kerma per projection
        PCXMCInput[:, 0] = 0  # Column 1: Reserved
        PCXMCInput[:, 1] = 0  # Column 2: Reserved
        
        return PCXMCInput
    
    def run(self) -> Dict[str, Any]:
        """Run the complete PCXMC simulation."""
        
        # Compute gantry angles
        angles = self.compute_gantry_angles()
        
        # Scale resolution if needed
        sub_coords, sub_widths, kerma, filtration, num_sub_fields = self.scale_resolution()
        
        # Calculate sub-field coordinates
        Coords = self.calculate_subfield_coordinates(angles, sub_coords)
        
        # Amend sub-fields based on phantom geometry
        results = self.amend_subfields(Coords, sub_widths, kerma, filtration, angles)
        
        # Generate PCXMC matrix
        pcxmc_matrix = self.generate_pcxmc_matrix(results)
        
        # Package final results
        output = {
            'angles': angles,
            'num_angles': len(angles),
            'num_sub_fields': num_sub_fields,
            'pcxmc_matrix': pcxmc_matrix,
            'total_valid_subfields': results['nD'],
            'points_per_angle': results['nDI'],
            **results
        }
        
        return output
    
    def save_results(self, results: Dict[str, Any], filename: str):
        """Save results to file in PCXMC format."""
        pcxmc_matrix = results['pcxmc_matrix']
        np.savetxt(filename, pcxmc_matrix, fmt='%.12f', delimiter='\t')
    
    def plot_results(self, results: Dict[str, Any]):
        """Plot results if plotting is enabled."""
        if self.config.get('plotting', False):
            # Implementation for plotting (similar to MATLAB)
            pass


def run_pcxmc_simulation(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to run PCXMC simulation.
    
    Parameters
    ----------
    config : dict
        Configuration dictionary
        
    Returns
    -------
    dict
        Simulation results
    """
    runner = PCXMCRunner(config)
    return runner.run()

def main():
    # Create default configuration
    config = ConfigLoader("..\configs\demo_config.yaml")
    
    # Run simulation
    results = run_pcxmc_simulation(config)

if __name__ == "__main__":
    main()
