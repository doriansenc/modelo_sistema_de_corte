"""
Unit tests for the physics module.

Tests the core physics calculations including:
- Moment of inertia calculations
- Torque component calculations
- Differential equation system
- Energy and power calculations
"""

import pytest
import numpy as np
from unittest.mock import Mock

from orc.core.physics import (
    RotaryCutterPhysics,
    PhysicsConstants,
    calculate_moment_of_inertia,
    calculate_kinetic_energy,
    calculate_power
)
from tests import DEFAULT_TEST_PARAMS, PHYSICS_TOLERANCE


class TestPhysicsConstants:
    """Test the PhysicsConstants dataclass."""
    
    def test_default_constants(self):
        """Test that default constants are reasonable."""
        constants = PhysicsConstants()
        
        assert constants.STEEL_DENSITY > 0
        assert constants.AIR_DENSITY > 0
        assert constants.MAX_ANGULAR_VELOCITY > 0
        assert constants.MAX_TORQUE > 0
        assert constants.MAX_RADIUS > 0
        assert constants.MAX_MASS > 0


class TestRotaryCutterPhysics:
    """Test the RotaryCutterPhysics class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.physics = RotaryCutterPhysics()
        self.test_params = DEFAULT_TEST_PARAMS.copy()
    
    def test_initialization(self):
        """Test physics engine initialization."""
        # Default initialization
        physics = RotaryCutterPhysics()
        assert physics.constants is not None
        
        # Custom constants
        custom_constants = PhysicsConstants()
        physics_custom = RotaryCutterPhysics(custom_constants)
        assert physics_custom.constants is custom_constants
    
    def test_calculate_total_moment_of_inertia(self):
        """Test total moment of inertia calculation."""
        I_total = self.physics.calculate_total_moment_of_inertia(self.test_params)
        
        # Should be positive
        assert I_total > 0
        
        # Should include both plate and blade contributions
        I_plate = self.test_params['I_plate']
        n_blades = self.test_params.get('n_blades', 2)
        m_c = self.test_params['m_c']
        R = self.test_params['R']
        L = self.test_params['L']
        
        expected_I_blades = n_blades * m_c * (R + L)**2
        expected_I_total = I_plate + expected_I_blades
        
        assert abs(I_total - expected_I_total) < PHYSICS_TOLERANCE
    
    def test_calculate_torque_components(self):
        """Test torque component calculations."""
        t = 1.0
        omega = 10.0
        
        torques = self.physics.calculate_torque_components(t, omega, self.test_params)
        
        # Check that all expected components are present
        expected_keys = ['input', 'friction', 'drag', 'grass', 'net']
        for key in expected_keys:
            assert key in torques
        
        # Check individual components
        assert torques['input'] == self.test_params['tau_input']
        assert torques['friction'] == self.test_params['b'] * omega
        assert torques['drag'] == self.test_params['c_drag'] * omega**2
        
        # Net torque should be the sum
        expected_net = (torques['input'] - torques['friction'] - 
                       torques['drag'] - torques['grass'])
        assert abs(torques['net'] - expected_net) < PHYSICS_TOLERANCE
    
    def test_torque_components_with_function(self):
        """Test torque components with custom torque function."""
        # Create a mock torque function
        tau_func = Mock(return_value=50.0)
        params_with_func = self.test_params.copy()
        params_with_func['tau_grass_func'] = tau_func
        
        t = 2.0
        omega = 5.0
        
        torques = self.physics.calculate_torque_components(t, omega, params_with_func)
        
        # Function should have been called with time
        tau_func.assert_called_once_with(t)
        
        # Grass torque should be function result
        assert torques['grass'] == 50.0
    
    def test_differential_equation_system(self):
        """Test the differential equation system."""
        t = 0.0
        y = np.array([0.0, 10.0])  # [theta, omega]
        
        dydt = self.physics.differential_equation_system(t, y, self.test_params)
        
        # Should return array of same length
        assert len(dydt) == len(y)
        
        # First derivative should be omega
        assert dydt[0] == y[1]
        
        # Second derivative should be angular acceleration
        I_total = self.physics.calculate_total_moment_of_inertia(self.test_params)
        torques = self.physics.calculate_torque_components(t, y[1], self.test_params)
        expected_alpha = torques['net'] / I_total
        
        assert abs(dydt[1] - expected_alpha) < PHYSICS_TOLERANCE
    
    def test_differential_equation_system_zero_omega(self):
        """Test differential equation system with zero angular velocity."""
        t = 0.0
        y = np.array([0.0, 0.0])  # [theta, omega]
        
        dydt = self.physics.differential_equation_system(t, y, self.test_params)
        
        # Should not raise any errors
        assert len(dydt) == 2
        assert dydt[0] == 0.0  # dtheta/dt = omega = 0
        assert isinstance(dydt[1], (int, float))  # dalpha/dt should be numeric


class TestUtilityFunctions:
    """Test utility functions in the physics module."""
    
    def test_calculate_moment_of_inertia(self):
        """Test moment of inertia calculation utility."""
        mass_plate = 5.0
        radius = 0.5
        mass_blade = 1.0
        blade_radius = 0.7
        n_blades = 2
        
        I_plate, I_blades, I_total = calculate_moment_of_inertia(
            mass_plate, radius, mass_blade, blade_radius, n_blades
        )
        
        # Check individual components
        expected_I_plate = 0.5 * mass_plate * radius**2
        expected_I_blades = n_blades * mass_blade * blade_radius**2
        expected_I_total = expected_I_plate + expected_I_blades
        
        assert abs(I_plate - expected_I_plate) < PHYSICS_TOLERANCE
        assert abs(I_blades - expected_I_blades) < PHYSICS_TOLERANCE
        assert abs(I_total - expected_I_total) < PHYSICS_TOLERANCE
    
    def test_calculate_kinetic_energy(self):
        """Test kinetic energy calculation."""
        I = 2.0
        omega = 10.0
        
        KE = calculate_kinetic_energy(I, omega)
        expected_KE = 0.5 * I * omega**2
        
        assert abs(KE - expected_KE) < PHYSICS_TOLERANCE
    
    def test_calculate_power(self):
        """Test power calculation."""
        torque = 100.0
        omega = 5.0
        
        power = calculate_power(torque, omega)
        expected_power = torque * omega
        
        assert abs(power - expected_power) < PHYSICS_TOLERANCE
    
    def test_calculate_power_zero_values(self):
        """Test power calculation with zero values."""
        assert calculate_power(0.0, 10.0) == 0.0
        assert calculate_power(100.0, 0.0) == 0.0
        assert calculate_power(0.0, 0.0) == 0.0
    
    def test_calculate_kinetic_energy_zero_values(self):
        """Test kinetic energy calculation with zero values."""
        assert calculate_kinetic_energy(0.0, 10.0) == 0.0
        assert calculate_kinetic_energy(2.0, 0.0) == 0.0
        assert calculate_kinetic_energy(0.0, 0.0) == 0.0


class TestPhysicsEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.physics = RotaryCutterPhysics()
    
    def test_negative_angular_velocity(self):
        """Test physics calculations with negative angular velocity."""
        params = DEFAULT_TEST_PARAMS.copy()
        t = 1.0
        omega = -10.0
        
        torques = self.physics.calculate_torque_components(t, omega, params)
        
        # Friction should be negative (opposing motion)
        assert torques['friction'] < 0
        
        # Drag should be negative (opposing motion)
        assert torques['drag'] < 0
    
    def test_very_small_inertia(self):
        """Test with very small moment of inertia."""
        params = DEFAULT_TEST_PARAMS.copy()
        params['I_plate'] = 1e-6
        params['m_c'] = 1e-6
        
        I_total = self.physics.calculate_total_moment_of_inertia(params)
        assert I_total > 0
        
        # Should still be able to calculate derivatives
        t = 0.0
        y = np.array([0.0, 1.0])
        dydt = self.physics.differential_equation_system(t, y, params)
        
        assert len(dydt) == 2
        assert np.isfinite(dydt).all()
    
    def test_missing_optional_parameters(self):
        """Test with missing optional parameters."""
        params = DEFAULT_TEST_PARAMS.copy()
        # Remove optional parameter
        if 'n_blades' in params:
            del params['n_blades']
        
        # Should use default value
        I_total = self.physics.calculate_total_moment_of_inertia(params)
        assert I_total > 0
