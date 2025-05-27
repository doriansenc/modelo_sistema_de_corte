"""
Parameter and input validation for the ORC system.

This module provides comprehensive validation logic for all inputs to the
simulation system, including physical parameters, simulation configurations,
and user inputs.

The validation system ensures:
- Physical parameters are within realistic ranges
- Mathematical consistency of inputs
- Type safety and format validation
- Clear error messages for debugging
"""

import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass
import logging


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, parameter: Optional[str] = None, 
                 value: Optional[Any] = None):
        """
        Initialize validation error.
        
        Args:
            message: Error description
            parameter: Name of the parameter that failed validation
            value: Value that failed validation
        """
        self.parameter = parameter
        self.value = value
        super().__init__(message)


@dataclass
class ParameterLimits:
    """Physical limits for parameter validation."""
    
    # Geometric parameters
    MIN_RADIUS: float = 0.01        # m
    MAX_RADIUS: float = 5.0         # m
    MIN_LENGTH: float = 0.0         # m
    MAX_LENGTH_RATIO: float = 2.0   # L/R ratio
    
    # Mass and inertia parameters
    MIN_MASS: float = 0.1           # kg
    MAX_MASS: float = 1000.0        # kg
    MIN_INERTIA: float = 1e-6       # kg⋅m²
    MAX_INERTIA: float = 1000.0     # kg⋅m²
    
    # Torque parameters
    MIN_TORQUE: float = 0.1         # N⋅m
    MAX_TORQUE: float = 10000.0     # N⋅m
    
    # Velocity parameters
    MAX_ANGULAR_VELOCITY: float = 1000.0    # rad/s
    MAX_LINEAR_VELOCITY: float = 20.0       # m/s
    
    # Resistance parameters
    MIN_FRICTION: float = 0.0       # N⋅m⋅s/rad
    MAX_FRICTION: float = 100.0     # N⋅m⋅s/rad
    MIN_DRAG: float = 0.0           # N⋅m⋅s²/rad²
    MAX_DRAG: float = 10.0          # N⋅m⋅s²/rad²
    
    # Vegetation parameters
    MIN_DENSITY: float = 0.0        # kg/m²
    MAX_DENSITY: float = 10.0       # kg/m²
    MIN_RESISTANCE: float = 0.0     # N⋅s/m
    MAX_RESISTANCE: float = 1000.0  # N⋅s/m
    
    # Blade parameters
    MIN_BLADES: int = 1
    MAX_BLADES: int = 12
    
    # Cutting parameters
    MIN_WIDTH: float = 0.1          # m
    MAX_WIDTH: float = 10.0         # m


class ParameterValidator:
    """
    Comprehensive parameter validation for rotary cutter systems.
    
    This class provides methods to validate all types of parameters used
    in the simulation system, ensuring physical consistency and realistic values.
    """
    
    def __init__(self, limits: Optional[ParameterLimits] = None):
        """
        Initialize the parameter validator.
        
        Args:
            limits: Parameter limits to use. If None, defaults are used.
        """
        self.limits = limits or ParameterLimits()
        self.logger = logging.getLogger(__name__)
    
    def validate_parameters(self, params: Dict) -> None:
        """
        Validate a complete parameter dictionary.
        
        Args:
            params: Dictionary containing all physical parameters
            
        Raises:
            ValidationError: If any parameter is invalid
        """
        # Check for required parameters
        self._check_required_parameters(params)
        
        # Validate individual parameters
        self._validate_geometric_parameters(params)
        self._validate_mass_parameters(params)
        self._validate_torque_parameters(params)
        self._validate_resistance_parameters(params)
        self._validate_vegetation_parameters(params)
        self._validate_blade_parameters(params)
        
        # Validate parameter consistency
        self._validate_parameter_consistency(params)
        
        # Validate torque function if present
        if 'tau_grass_func' in params and params['tau_grass_func'] is not None:
            self._validate_torque_function(params['tau_grass_func'])
    
    def _check_required_parameters(self, params: Dict) -> None:
        """Check that all required parameters are present."""
        required_params = [
            'I_plate', 'm_c', 'R', 'L', 'tau_input', 'b', 'c_drag',
            'rho_veg', 'k_grass', 'v_avance'
        ]
        
        missing_params = [param for param in required_params if param not in params]
        
        if missing_params:
            raise ValidationError(
                f"Missing required parameters: {', '.join(missing_params)}"
            )
    
    def _validate_geometric_parameters(self, params: Dict) -> None:
        """Validate geometric parameters."""
        # Radius
        R = params['R']
        if not isinstance(R, (int, float)) or R <= 0:
            raise ValidationError(
                f"Radius must be positive, got: {R}", 'R', R
            )
        if R < self.limits.MIN_RADIUS or R > self.limits.MAX_RADIUS:
            raise ValidationError(
                f"Radius {R} outside valid range [{self.limits.MIN_RADIUS}, {self.limits.MAX_RADIUS}]",
                'R', R
            )
        
        # Length
        L = params['L']
        if not isinstance(L, (int, float)) or L < 0:
            raise ValidationError(
                f"Length must be non-negative, got: {L}", 'L', L
            )
        if L > self.limits.MAX_LENGTH_RATIO * R:
            raise ValidationError(
                f"Length {L} too large relative to radius {R} (max ratio: {self.limits.MAX_LENGTH_RATIO})",
                'L', L
            )
        
        # Width (if present)
        if 'w' in params:
            w = params['w']
            if not isinstance(w, (int, float)) or w <= 0:
                raise ValidationError(
                    f"Width must be positive, got: {w}", 'w', w
                )
            if w < self.limits.MIN_WIDTH or w > self.limits.MAX_WIDTH:
                raise ValidationError(
                    f"Width {w} outside valid range [{self.limits.MIN_WIDTH}, {self.limits.MAX_WIDTH}]",
                    'w', w
                )
    
    def _validate_mass_parameters(self, params: Dict) -> None:
        """Validate mass and inertia parameters."""
        # Plate moment of inertia
        I_plate = params['I_plate']
        if not isinstance(I_plate, (int, float)) or I_plate <= 0:
            raise ValidationError(
                f"Plate moment of inertia must be positive, got: {I_plate}",
                'I_plate', I_plate
            )
        if I_plate < self.limits.MIN_INERTIA or I_plate > self.limits.MAX_INERTIA:
            raise ValidationError(
                f"Plate inertia {I_plate} outside valid range [{self.limits.MIN_INERTIA}, {self.limits.MAX_INERTIA}]",
                'I_plate', I_plate
            )
        
        # Blade mass
        m_c = params['m_c']
        if not isinstance(m_c, (int, float)) or m_c <= 0:
            raise ValidationError(
                f"Blade mass must be positive, got: {m_c}", 'm_c', m_c
            )
        if m_c < self.limits.MIN_MASS or m_c > self.limits.MAX_MASS:
            raise ValidationError(
                f"Blade mass {m_c} outside valid range [{self.limits.MIN_MASS}, {self.limits.MAX_MASS}]",
                'm_c', m_c
            )
    
    def _validate_torque_parameters(self, params: Dict) -> None:
        """Validate torque parameters."""
        tau_input = params['tau_input']
        if not isinstance(tau_input, (int, float)) or tau_input <= 0:
            raise ValidationError(
                f"Input torque must be positive, got: {tau_input}",
                'tau_input', tau_input
            )
        if tau_input < self.limits.MIN_TORQUE or tau_input > self.limits.MAX_TORQUE:
            raise ValidationError(
                f"Input torque {tau_input} outside valid range [{self.limits.MIN_TORQUE}, {self.limits.MAX_TORQUE}]",
                'tau_input', tau_input
            )
    
    def _validate_resistance_parameters(self, params: Dict) -> None:
        """Validate resistance parameters."""
        # Viscous friction
        b = params['b']
        if not isinstance(b, (int, float)) or b < 0:
            raise ValidationError(
                f"Viscous friction must be non-negative, got: {b}", 'b', b
            )
        if b > self.limits.MAX_FRICTION:
            raise ValidationError(
                f"Viscous friction {b} exceeds maximum {self.limits.MAX_FRICTION}",
                'b', b
            )
        
        # Aerodynamic drag
        c_drag = params['c_drag']
        if not isinstance(c_drag, (int, float)) or c_drag < 0:
            raise ValidationError(
                f"Drag coefficient must be non-negative, got: {c_drag}",
                'c_drag', c_drag
            )
        if c_drag > self.limits.MAX_DRAG:
            raise ValidationError(
                f"Drag coefficient {c_drag} exceeds maximum {self.limits.MAX_DRAG}",
                'c_drag', c_drag
            )
    
    def _validate_vegetation_parameters(self, params: Dict) -> None:
        """Validate vegetation parameters."""
        # Vegetation density
        rho_veg = params['rho_veg']
        if not isinstance(rho_veg, (int, float)) or rho_veg < 0:
            raise ValidationError(
                f"Vegetation density must be non-negative, got: {rho_veg}",
                'rho_veg', rho_veg
            )
        if rho_veg > self.limits.MAX_DENSITY:
            raise ValidationError(
                f"Vegetation density {rho_veg} exceeds maximum {self.limits.MAX_DENSITY}",
                'rho_veg', rho_veg
            )
        
        # Grass resistance
        k_grass = params['k_grass']
        if not isinstance(k_grass, (int, float)) or k_grass < 0:
            raise ValidationError(
                f"Grass resistance must be non-negative, got: {k_grass}",
                'k_grass', k_grass
            )
        if k_grass > self.limits.MAX_RESISTANCE:
            raise ValidationError(
                f"Grass resistance {k_grass} exceeds maximum {self.limits.MAX_RESISTANCE}",
                'k_grass', k_grass
            )
        
        # Advance velocity
        v_avance = params['v_avance']
        if not isinstance(v_avance, (int, float)) or v_avance < 0:
            raise ValidationError(
                f"Advance velocity must be non-negative, got: {v_avance}",
                'v_avance', v_avance
            )
        if v_avance > self.limits.MAX_LINEAR_VELOCITY:
            raise ValidationError(
                f"Advance velocity {v_avance} exceeds maximum {self.limits.MAX_LINEAR_VELOCITY}",
                'v_avance', v_avance
            )
    
    def _validate_blade_parameters(self, params: Dict) -> None:
        """Validate blade parameters."""
        if 'n_blades' in params:
            n_blades = params['n_blades']
            if not isinstance(n_blades, int) or n_blades < self.limits.MIN_BLADES:
                raise ValidationError(
                    f"Number of blades must be integer >= {self.limits.MIN_BLADES}, got: {n_blades}",
                    'n_blades', n_blades
                )
            if n_blades > self.limits.MAX_BLADES:
                raise ValidationError(
                    f"Number of blades {n_blades} exceeds maximum {self.limits.MAX_BLADES}",
                    'n_blades', n_blades
                )
    
    def _validate_parameter_consistency(self, params: Dict) -> None:
        """Validate consistency between parameters."""
        # Check if moment of inertia is reasonable relative to mass and radius
        I_plate = params['I_plate']
        m_c = params['m_c']
        R = params['R']
        
        # Rough estimate of expected inertia order of magnitude
        expected_I_order = m_c * R**2
        if I_plate > 10 * expected_I_order:
            self.logger.warning(
                f"Plate inertia {I_plate:.3f} seems large relative to blade mass and radius "
                f"(expected order: {expected_I_order:.3f})"
            )
    
    def _validate_torque_function(self, tau_func: Callable) -> None:
        """Validate a torque function."""
        if not callable(tau_func):
            raise ValidationError("Torque function must be callable")
        
        # Test the function with sample inputs
        test_times = [0.0, 1.0, 5.0, 10.0]
        for t in test_times:
            try:
                result = tau_func(t)
                if not isinstance(result, (int, float)):
                    raise ValidationError(
                        f"Torque function must return numeric value, got {type(result)} for t={t}"
                    )
                if result < 0:
                    raise ValidationError(
                        f"Torque function returned negative value {result} for t={t}"
                    )
                if result > self.limits.MAX_TORQUE:
                    raise ValidationError(
                        f"Torque function returned excessive value {result} for t={t} "
                        f"(max: {self.limits.MAX_TORQUE})"
                    )
            except Exception as e:
                if isinstance(e, ValidationError):
                    raise
                raise ValidationError(f"Error evaluating torque function at t={t}: {str(e)}")


def validate_simulation_inputs(mass: float, radius: float, omega: Optional[float],
                             t_end: float, dt: float) -> None:
    """
    Validate basic simulation inputs.
    
    Args:
        mass: Total system mass [kg]
        radius: System radius [m]
        omega: Angular velocity [rad/s]
        t_end: End time [s]
        dt: Time step [s]
        
    Raises:
        ValidationError: If any input is invalid
    """
    limits = ParameterLimits()
    
    # Validate mass
    if not isinstance(mass, (int, float)) or mass <= 0:
        raise ValidationError(f"Mass must be positive, got: {mass}")
    if mass > limits.MAX_MASS:
        raise ValidationError(f"Mass {mass} exceeds maximum {limits.MAX_MASS}")
    
    # Validate radius
    if not isinstance(radius, (int, float)) or radius <= 0:
        raise ValidationError(f"Radius must be positive, got: {radius}")
    if radius > limits.MAX_RADIUS:
        raise ValidationError(f"Radius {radius} exceeds maximum {limits.MAX_RADIUS}")
    
    # Validate angular velocity if provided
    if omega is not None:
        if not isinstance(omega, (int, float)) or omega < 0:
            raise ValidationError(f"Angular velocity must be non-negative, got: {omega}")
        if omega > limits.MAX_ANGULAR_VELOCITY:
            raise ValidationError(f"Angular velocity {omega} exceeds maximum {limits.MAX_ANGULAR_VELOCITY}")
    
    # Validate time parameters
    if not isinstance(t_end, (int, float)) or t_end <= 0:
        raise ValidationError(f"End time must be positive, got: {t_end}")
    if t_end > 3600.0:  # 1 hour maximum
        raise ValidationError(f"End time {t_end} exceeds maximum 3600s")
    
    if not isinstance(dt, (int, float)) or dt <= 0:
        raise ValidationError(f"Time step must be positive, got: {dt}")
    if dt > t_end / 10:
        raise ValidationError(f"Time step {dt} too large relative to end time {t_end}")
    if dt < 1e-6:
        raise ValidationError(f"Time step {dt} too small (minimum: 1e-6)")
