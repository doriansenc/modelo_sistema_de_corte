"""
Parameter management for the ORC system.

This module provides parameter management capabilities including
default parameter definitions, parameter loading/saving, and
parameter validation.
"""

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
import logging


@dataclass
class DefaultParameters:
    """Default parameter values for the ORC system."""

    # Geometric parameters
    radius: float = 0.6
    blade_length_percent: float = 30.0
    cutting_width: float = 1.8

    # Mass parameters
    total_mass: float = 15.0
    plate_mass_percent: float = 40.0
    n_blades: int = 2

    # Motor parameters
    input_torque: float = 200.0

    # Resistance parameters
    viscous_friction: float = 0.1
    aerodynamic_drag: float = 0.01

    # Vegetation parameters
    vegetation_density: float = 1.0
    grass_resistance: float = 15.0
    advance_velocity: float = 3.0

    # Simulation parameters
    simulation_time: float = 10.0
    time_points: int = 1000


class ParameterManager:
    """
    Manager for system parameters.

    This class provides methods to load, save, validate, and manage
    system parameters for the ORC system.
    """

    def __init__(self):
        """Initialize the parameter manager."""
        self.logger = logging.getLogger(__name__)
        self.defaults = DefaultParameters()

    def get_defaults(self) -> Dict[str, Any]:
        """
        Get default parameters as dictionary.

        Returns:
            Dictionary of default parameters
        """
        return asdict(self.defaults)

    def load_from_file(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """
        Load parameters from file.

        Args:
            filepath: Path to parameter file (YAML or JSON)

        Returns:
            Dictionary of parameters
        """
        filepath = Path(filepath)

        if not filepath.exists():
            self.logger.error(f"Parameter file not found: {filepath}")
            return self.get_defaults()

        try:
            with open(filepath, 'r') as f:
                if filepath.suffix.lower() in ['.yaml', '.yml']:
                    if YAML_AVAILABLE:
                        params = yaml.safe_load(f)
                    else:
                        self.logger.error("YAML support not available. Install PyYAML to load YAML files.")
                        return self.get_defaults()
                elif filepath.suffix.lower() == '.json':
                    params = json.load(f)
                else:
                    self.logger.error(f"Unsupported file format: {filepath.suffix}")
                    return self.get_defaults()

            self.logger.info(f"Loaded parameters from {filepath}")
            return params

        except Exception as e:
            self.logger.error(f"Error loading parameters from {filepath}: {e}")
            return self.get_defaults()

    def save_to_file(self, parameters: Dict[str, Any],
                    filepath: Union[str, Path]) -> bool:
        """
        Save parameters to file.

        Args:
            parameters: Parameters to save
            filepath: Output file path

        Returns:
            True if successful, False otherwise
        """
        filepath = Path(filepath)

        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, 'w') as f:
                if filepath.suffix.lower() in ['.yaml', '.yml']:
                    if YAML_AVAILABLE:
                        yaml.dump(parameters, f, default_flow_style=False, indent=2)
                    else:
                        self.logger.error("YAML support not available. Install PyYAML to save YAML files.")
                        return False
                elif filepath.suffix.lower() == '.json':
                    json.dump(parameters, f, indent=2)
                else:
                    self.logger.error(f"Unsupported file format: {filepath.suffix}")
                    return False

            self.logger.info(f"Saved parameters to {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving parameters to {filepath}: {e}")
            return False

    def merge_with_defaults(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge parameters with defaults.

        Args:
            parameters: Parameters to merge

        Returns:
            Merged parameters with defaults filled in
        """
        defaults = self.get_defaults()
        merged = defaults.copy()
        merged.update(parameters)
        return merged

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate parameters.

        Args:
            parameters: Parameters to validate

        Returns:
            True if valid, False otherwise
        """
        # Basic validation - can be extended
        required_keys = [
            'radius', 'total_mass', 'input_torque', 'simulation_time'
        ]

        for key in required_keys:
            if key not in parameters:
                self.logger.error(f"Missing required parameter: {key}")
                return False

            if not isinstance(parameters[key], (int, float)):
                self.logger.error(f"Parameter {key} must be numeric")
                return False

            if parameters[key] <= 0:
                self.logger.error(f"Parameter {key} must be positive")
                return False

        return True


def load_parameters(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Convenience function to load parameters.

    Args:
        filepath: Path to parameter file

    Returns:
        Dictionary of parameters
    """
    manager = ParameterManager()
    return manager.load_from_file(filepath)


def save_parameters(parameters: Dict[str, Any],
                   filepath: Union[str, Path]) -> bool:
    """
    Convenience function to save parameters.

    Args:
        parameters: Parameters to save
        filepath: Output file path

    Returns:
        True if successful, False otherwise
    """
    manager = ParameterManager()
    return manager.save_to_file(parameters, filepath)
