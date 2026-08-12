"""Tests for geometry module."""

import pytest
import numpy as np
from src.geometry import (
    within_ellipse, rotate_point, find_intersections,
    sub_field_intersection, sub_field_intersections
)


class TestWithinEllipse:
    """Test cases for within_ellipse function."""
    
    def test_center_point(self):
        """Test that center point is within ellipse."""
        assert within_ellipse(10, 10, 0, 0)
    
    def test_boundary_point(self):
        """Test that boundary points are within ellipse."""
        assert within_ellipse(10, 10, 10, 0)
        assert within_ellipse(10, 10, 0, 10)
    
    def test_outside_point(self):
        """Test that points outside ellipse are correctly identified."""
        assert not within_ellipse(10, 10, 11, 0)


class TestRotatePoint:
    """Test cases for rotate_point function."""
    
    def test_zero_rotation(self):
        """Test rotation by 0 degrees."""
        x, y = rotate_point(1, 0, 0)
        assert abs(x - 1) < 1e-10
        assert abs(y - 0) < 1e-10
    
    def test_90_degree_rotation(self):
        """Test rotation by 90 degrees."""
        x, y = rotate_point(1, 0, 90)
        assert abs(x - 0) < 1e-10
        assert abs(y - 1) < 1e-10


class TestFindIntersections:
    """Test cases for find_intersections function."""
    
    def test_horizontal_line_intersection(self):
        """Test horizontal line intersecting ellipse."""
        intersections = find_intersections(5, 5, 0, [-5, 5], [0, 0])
        assert intersections.shape == (2, 2)
        # Should find intersections at x = ±5, y = 0
        # Check that we have valid intersection points
        assert not np.any(np.isnan(intersections))
        assert abs(intersections[1, 0] - 0) < 1e-10
        assert abs(intersections[1, 1] - 0) < 1e-10


class TestSubFieldIntersection:
    """Test cases for sub_field_intersection function."""
    
    def test_basic_calculation(self):
        """Test basic sub-field intersection calculation."""
        result = sub_field_intersection(10, 20, 5, 45, 0.5)
        assert result.shape == (2, 1)
        # Check the calculation produces reasonable values
        assert isinstance(result[0, 0], (int, float))
        assert isinstance(result[1, 0], (int, float))
    
    def test_zero_angle(self):
        """Test with zero angle."""
        result = sub_field_intersection(0, 10, 4, 0, 0.5)
        assert abs(result[0, 0] - 0.0) < 1e-10
        assert abs(result[1, 0] - 9.0) < 1e-10


class TestSubFieldIntersections:
    """Test cases for sub_field_intersections function."""
    
    def test_single_subfield(self):
        """Test with single sub-field."""
        X = np.array([10])
        Y = np.array([20])
        sFW = np.array([5])
        a = np.array([45])
        nDI = np.array([1])
        
        Xf, Yf = sub_field_intersections(X, Y, sFW, a, nDI)
        
        # Should have 2 points: before and after the single sub-field
        assert len(Xf) == 2
        assert len(Yf) == 2
    
    def test_multiple_subfields(self):
        """Test with multiple sub-fields."""
        X = np.array([10, 15])
        Y = np.array([20, 25])
        sFW = np.array([5, 6])
        a = np.array([45, 30])
        nDI = np.array([2])
        
        Xf, Yf = sub_field_intersections(X, Y, sFW, a, nDI)
        
        # Should have 3 points: before first, between, after second
        assert len(Xf) == 3
        assert len(Yf) == 3
    
    def test_empty_input(self):
        """Test with empty input arrays."""
        X = np.array([])
        Y = np.array([])
        sFW = np.array([])
        a = np.array([])
        nDI = np.array([])
        
        Xf, Yf = sub_field_intersections(X, Y, sFW, a, nDI)
        
        assert len(Xf) == 0
        assert len(Yf) == 0


if __name__ == "__main__":
    pytest.main([__file__])
