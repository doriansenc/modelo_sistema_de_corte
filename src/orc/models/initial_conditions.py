"""
Initial condition utilities for rotary cutter simulations.

This module provides utilities for setting up initial conditions for
rotary cutter simulations, including various startup scenarios and
predefined initial states.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from enum import Enum
import logging


class InitialConditionType(Enum):
    """Available initial condition types."""
    
    STATIONARY = "stationary"
    FROM_RPM = "from_rpm"
    BLADE_ANGLE = "blade_angle"
    SPINNING = "spinning"
    CUSTOM = "custom"


class InitialConditionManager:
    """
    Manager for initial conditions in rotary cutter simulations.
    
    This class provides methods to create and manage initial conditions
    for different startup scenarios and operational states.
    """
    
    def __init__(self):
        """Initialize the initial condition manager."""
        self.logger = logging.getLogger(__name__)
    
    def create_conditions(self, condition_type: InitialConditionType,
                         parameters: Optional[Dict] = None) -> List[float]:
        """
        Create initial conditions based on type and parameters.
        
        Args:
            condition_type: Type of initial condition
            parameters: Parameters for the initial condition
            
        Returns:
            Initial state vector [angle, angular_velocity]
        """
        if parameters is None:
            parameters = {}
        
        try:
            if condition_type == InitialConditionType.STATIONARY:
                return self._stationary_conditions(**parameters)
            elif condition_type == InitialConditionType.FROM_RPM:
                return self._from_rpm_conditions(**parameters)
            elif condition_type == InitialConditionType.BLADE_ANGLE:
                return self._blade_angle_conditions(**parameters)
            elif condition_type == InitialConditionType.SPINNING:
                return self._spinning_conditions(**parameters)
            elif condition_type == InitialConditionType.CUSTOM:
                return self._custom_conditions(**parameters)
            else:
                self.logger.warning(f"Unknown initial condition type: {condition_type}")
                return self._stationary_conditions()
        
        except Exception as e:
            self.logger.error(f"Error creating initial conditions: {e}")
            return [0.0, 0.0]  # Default fallback
    
    def _stationary_conditions(self, angle: float = 0.0) -> List[float]:
        """
        Create stationary initial conditions.
        
        Args:
            angle: Initial angle [rad]
            
        Returns:
            [angle, 0.0] - stationary state
        """
        return [angle, 0.0]
    
    def _from_rpm_conditions(self, rpm: float = 100.0, angle: float = 0.0) -> List[float]:
        """
        Create initial conditions from RPM.
        
        Args:
            rpm: Initial rotational speed [RPM]
            angle: Initial angle [rad]
            
        Returns:
            [angle, angular_velocity] where angular_velocity is in rad/s
        """
        # Convert RPM to rad/s
        angular_velocity = rpm * 2 * np.pi / 60.0
        return [angle, angular_velocity]
    
    def _blade_angle_conditions(self, blade_angle_deg: float = 45.0,
                               angular_velocity: float = 0.0) -> List[float]:
        """
        Create initial conditions with specific blade angle.
        
        Args:
            blade_angle_deg: Blade angle in degrees
            angular_velocity: Initial angular velocity [rad/s]
            
        Returns:
            [angle, angular_velocity] where angle corresponds to blade position
        """
        # Convert degrees to radians
        angle = np.deg2rad(blade_angle_deg)
        return [angle, angular_velocity]
    
    def _spinning_conditions(self, target_rpm: float = 150.0,
                           startup_efficiency: float = 0.8,
                           angle: float = 0.0) -> List[float]:
        """
        Create initial conditions for spinning startup.
        
        Args:
            target_rpm: Target RPM for operation
            startup_efficiency: Efficiency of startup (0-1)
            angle: Initial angle [rad]
            
        Returns:
            [angle, angular_velocity] with reduced initial speed
        """
        # Calculate target angular velocity
        target_omega = target_rpm * 2 * np.pi / 60.0
        
        # Apply startup efficiency
        initial_omega = target_omega * startup_efficiency
        
        return [angle, initial_omega]
    
    def _custom_conditions(self, angle: float = 0.0,
                          angular_velocity: float = 0.0) -> List[float]:
        """
        Create custom initial conditions.
        
        Args:
            angle: Initial angle [rad]
            angular_velocity: Initial angular velocity [rad/s]
            
        Returns:
            [angle, angular_velocity]
        """
        return [angle, angular_velocity]
    
    def validate_conditions(self, conditions: List[float],
                           max_angle: float = 2 * np.pi,
                           max_angular_velocity: float = 1000.0) -> bool:
        """
        Validate initial conditions.
        
        Args:
            conditions: Initial conditions [angle, angular_velocity]
            max_angle: Maximum allowed angle [rad]
            max_angular_velocity: Maximum allowed angular velocity [rad/s]
            
        Returns:
            True if conditions are valid, False otherwise
        """
        if len(conditions) != 2:
            self.logger.error("Initial conditions must have exactly 2 elements")
            return False
        
        angle, angular_velocity = conditions
        
        # Check angle bounds
        if abs(angle) > max_angle:
            self.logger.warning(f"Initial angle {angle} exceeds maximum {max_angle}")
            return False
        
        # Check angular velocity bounds
        if abs(angular_velocity) > max_angular_velocity:
            self.logger.warning(f"Initial angular velocity {angular_velocity} exceeds maximum {max_angular_velocity}")
            return False
        
        # Check for NaN or infinite values
        if not np.isfinite(angle) or not np.isfinite(angular_velocity):
            self.logger.error("Initial conditions contain NaN or infinite values")
            return False
        
        return True
    
    def get_predefined_conditions(self) -> Dict[str, List[float]]:
        """
        Get a dictionary of predefined initial conditions.
        
        Returns:
            Dictionary mapping condition names to initial states
        """
        return {
            'stationary': self.create_conditions(InitialConditionType.STATIONARY),
            'slow_start': self.create_conditions(InitialConditionType.FROM_RPM, {'rpm': 50.0}),
            'normal_start': self.create_conditions(InitialConditionType.FROM_RPM, {'rpm': 100.0}),
            'fast_start': self.create_conditions(InitialConditionType.FROM_RPM, {'rpm': 200.0}),
            'blade_horizontal': self.create_conditions(InitialConditionType.BLADE_ANGLE, {'blade_angle_deg': 0.0}),
            'blade_vertical': self.create_conditions(InitialConditionType.BLADE_ANGLE, {'blade_angle_deg': 90.0}),
            'spinning_startup': self.create_conditions(InitialConditionType.SPINNING, {'target_rpm': 150.0})
        }


# Convenience functions for backward compatibility
def create_initial_conditions(condition_type: str = "stationary",
                            **kwargs) -> List[float]:
    """
    Create initial conditions (convenience function).
    
    Args:
        condition_type: Type of initial condition
        **kwargs: Parameters for the condition
        
    Returns:
        Initial state vector [angle, angular_velocity]
    """
    manager = InitialConditionManager()
    
    # Map string types to enum
    type_mapping = {
        'stationary': InitialConditionType.STATIONARY,
        'from_rpm': InitialConditionType.FROM_RPM,
        'blade_angle': InitialConditionType.BLADE_ANGLE,
        'spinning': InitialConditionType.SPINNING,
        'custom': InitialConditionType.CUSTOM
    }
    
    condition_enum = type_mapping.get(condition_type, InitialConditionType.STATIONARY)
    return manager.create_conditions(condition_enum, kwargs)


def initial_conditions_from_rpm(rpm: float = 100.0, angle: float = 0.0) -> List[float]:
    """
    Create initial conditions from RPM (convenience function).
    
    Args:
        rpm: Initial rotational speed [RPM]
        angle: Initial angle [rad]
        
    Returns:
        Initial state vector [angle, angular_velocity]
    """
    return create_initial_conditions('from_rpm', rpm=rpm, angle=angle)


def initial_conditions_blade_angle(blade_angle_deg: float = 45.0,
                                  angular_velocity: float = 0.0) -> List[float]:
    """
    Create initial conditions with specific blade angle (convenience function).
    
    Args:
        blade_angle_deg: Blade angle in degrees
        angular_velocity: Initial angular velocity [rad/s]
        
    Returns:
        Initial state vector [angle, angular_velocity]
    """
    return create_initial_conditions('blade_angle', 
                                   blade_angle_deg=blade_angle_deg,
                                   angular_velocity=angular_velocity)


def initial_conditions_spinning(target_rpm: float = 150.0,
                               startup_efficiency: float = 0.8,
                               angle: float = 0.0) -> List[float]:
    """
    Create initial conditions for spinning startup (convenience function).
    
    Args:
        target_rpm: Target RPM for operation
        startup_efficiency: Efficiency of startup (0-1)
        angle: Initial angle [rad]
        
    Returns:
        Initial state vector [angle, angular_velocity]
    """
    return create_initial_conditions('spinning',
                                   target_rpm=target_rpm,
                                   startup_efficiency=startup_efficiency,
                                   angle=angle)


def validate_initial_conditions(conditions: List[float]) -> bool:
    """
    Validate initial conditions (convenience function).
    
    Args:
        conditions: Initial conditions to validate
        
    Returns:
        True if valid, False otherwise
    """
    manager = InitialConditionManager()
    return manager.validate_conditions(conditions)


def get_common_initial_conditions() -> Dict[str, List[float]]:
    """
    Get common initial conditions (convenience function).
    
    Returns:
        Dictionary of common initial conditions
    """
    manager = InitialConditionManager()
    return manager.get_predefined_conditions()
