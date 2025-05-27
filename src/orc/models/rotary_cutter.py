"""
Main rotary cutter model and configuration management.

This module provides the high-level RotaryCutterModel class that encapsulates
the complete rotary cutter system, including physics, configuration, and
simulation capabilities.

The model provides a clean interface for:
- Parameter management and validation
- Simulation execution
- Result analysis
- Configuration persistence
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
import logging
from pathlib import Path

from ..core.simulation import SimulationEngine, SimulationConfig, SimulationResult
from ..core.physics import RotaryCutterPhysics
from ..core.validation import ParameterValidator, ValidationError
from ..analysis.metrics import PerformanceAnalyzer


@dataclass
class RotaryCutterConfig:
    """
    Configuration container for rotary cutter parameters.
    
    This class provides a structured way to manage all parameters
    needed for rotary cutter simulation, with built-in validation
    and serialization capabilities.
    """
    
    # Identification
    name: str = "Default Config"
    description: str = ""
    
    # Geometric parameters
    radius: float = 0.6                    # m - main radius
    blade_length_percent: float = 30.0     # % - blade length as percentage of radius
    cutting_width: float = 1.8             # m - cutting width
    
    # Mass and inertia parameters
    total_mass: float = 15.0               # kg - total system mass
    plate_mass_percent: float = 40.0       # % - plate mass as percentage of total
    n_blades: int = 2                      # number of blades
    
    # Motor parameters
    input_torque: float = 200.0            # N⋅m - motor torque
    
    # Resistance parameters
    viscous_friction: float = 0.1          # N⋅m⋅s/rad - viscous friction coefficient
    aerodynamic_drag: float = 0.01         # N⋅m⋅s²/rad² - drag coefficient
    
    # Vegetation parameters
    vegetation_density: float = 1.0        # kg/m² - vegetation density
    grass_resistance: float = 15.0         # N⋅s/m - grass resistance constant
    advance_velocity: float = 3.0          # m/s - forward velocity
    
    # Simulation parameters
    simulation_time: float = 10.0          # s - simulation duration
    time_points: int = 1000                # number of time points
    
    # Optional torque function
    torque_function: Optional[Any] = None
    
    # Metadata
    created_by: str = "ORC System"
    tags: List[str] = field(default_factory=list)
    
    def to_physics_parameters(self) -> Dict:
        """
        Convert configuration to physics parameters dictionary.
        
        Returns:
            Dictionary suitable for physics engine
        """
        # Calculate derived parameters
        blade_length = self.radius * (self.blade_length_percent / 100.0)
        plate_mass = self.total_mass * (self.plate_mass_percent / 100.0)
        blade_total_mass = self.total_mass - plate_mass
        blade_mass = blade_total_mass / self.n_blades if self.n_blades > 0 else 0.0
        
        # Plate moment of inertia (solid disk)
        plate_inertia = 0.5 * plate_mass * self.radius**2
        
        return {
            'I_plate': plate_inertia,
            'm_c': blade_mass,
            'R': self.radius,
            'L': blade_length,
            'n_blades': self.n_blades,
            'tau_input': self.input_torque,
            'b': self.viscous_friction,
            'c_drag': self.aerodynamic_drag,
            'rho_veg': self.vegetation_density,
            'k_grass': self.grass_resistance,
            'v_avance': self.advance_velocity,
            'w': self.cutting_width,
            'tau_grass_func': self.torque_function
        }
    
    def to_simulation_config(self) -> SimulationConfig:
        """
        Convert to simulation configuration.
        
        Returns:
            SimulationConfig object
        """
        return SimulationConfig(
            t_end=self.simulation_time,
            n_points=self.time_points
        )
    
    def validate(self) -> None:
        """
        Validate the configuration.
        
        Raises:
            ValidationError: If configuration is invalid
        """
        validator = ParameterValidator()
        physics_params = self.to_physics_parameters()
        validator.validate_parameters(physics_params)
    
    def copy(self) -> 'RotaryCutterConfig':
        """Create a deep copy of the configuration."""
        import copy
        return copy.deepcopy(self)
    
    def summary(self) -> Dict:
        """Get a summary of key parameters."""
        return {
            'name': self.name,
            'total_mass': self.total_mass,
            'radius': self.radius,
            'n_blades': self.n_blades,
            'input_torque': self.input_torque,
            'advance_velocity': self.advance_velocity,
            'simulation_time': self.simulation_time
        }


class RotaryCutterModel:
    """
    High-level rotary cutter model class.
    
    This class provides a complete interface for rotary cutter simulation,
    combining physics, configuration management, and analysis capabilities
    in a single, easy-to-use class.
    """
    
    def __init__(self, config: Optional[RotaryCutterConfig] = None):
        """
        Initialize the rotary cutter model.
        
        Args:
            config: Configuration to use. If None, default is created.
        """
        self.config = config or RotaryCutterConfig()
        self.physics = RotaryCutterPhysics()
        self.simulation_engine = SimulationEngine(self.physics)
        self.analyzer = PerformanceAnalyzer()
        self.logger = logging.getLogger(__name__)
        
        # Simulation history
        self.last_result: Optional[SimulationResult] = None
        self.simulation_history: List[SimulationResult] = []
    
    def update_config(self, **kwargs) -> None:
        """
        Update configuration parameters.
        
        Args:
            **kwargs: Parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                self.logger.warning(f"Unknown configuration parameter: {key}")
        
        # Validate updated configuration
        try:
            self.config.validate()
        except ValidationError as e:
            self.logger.error(f"Configuration validation failed: {e}")
            raise
    
    def run_simulation(self, store_history: bool = True) -> SimulationResult:
        """
        Run a simulation with the current configuration.
        
        Args:
            store_history: Whether to store result in simulation history
            
        Returns:
            SimulationResult object
        """
        try:
            # Validate configuration
            self.config.validate()
            
            # Convert to physics parameters
            physics_params = self.config.to_physics_parameters()
            sim_config = self.config.to_simulation_config()
            
            # Run simulation
            result = self.simulation_engine.run_simulation(physics_params, sim_config)
            
            # Store result
            self.last_result = result
            if store_history:
                self.simulation_history.append(result)
            
            self.logger.info(f"Simulation completed: {self.config.name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Simulation failed: {e}")
            raise
    
    def analyze_performance(self, result: Optional[SimulationResult] = None) -> Dict:
        """
        Analyze performance of a simulation result.
        
        Args:
            result: Result to analyze. If None, uses last result.
            
        Returns:
            Performance analysis dictionary
        """
        if result is None:
            result = self.last_result
        
        if result is None:
            raise ValueError("No simulation result available for analysis")
        
        return self.analyzer.analyze(result)
    
    def compare_configurations(self, other_configs: List[RotaryCutterConfig],
                             metric: str = 'efficiency') -> pd.DataFrame:
        """
        Compare current configuration with others.
        
        Args:
            other_configs: List of configurations to compare
            metric: Metric to use for comparison
            
        Returns:
            DataFrame with comparison results
        """
        results = []
        
        # Current configuration
        current_result = self.run_simulation(store_history=False)
        current_analysis = self.analyze_performance(current_result)
        results.append({
            'name': self.config.name,
            'config': self.config,
            'result': current_result,
            'analysis': current_analysis
        })
        
        # Other configurations
        for config in other_configs:
            temp_model = RotaryCutterModel(config)
            try:
                result = temp_model.run_simulation(store_history=False)
                analysis = temp_model.analyze_performance(result)
                results.append({
                    'name': config.name,
                    'config': config,
                    'result': result,
                    'analysis': analysis
                })
            except Exception as e:
                self.logger.error(f"Failed to simulate {config.name}: {e}")
                results.append({
                    'name': config.name,
                    'config': config,
                    'result': None,
                    'analysis': None,
                    'error': str(e)
                })
        
        # Create comparison DataFrame
        comparison_data = []
        for r in results:
            if r['analysis'] is not None:
                row = {
                    'Configuration': r['name'],
                    'Mass (kg)': r['config'].total_mass,
                    'Radius (m)': r['config'].radius,
                    'Blades': r['config'].n_blades,
                    'Torque (Nm)': r['config'].input_torque,
                    'Efficiency': r['analysis'].get('efficiency', 0),
                    'Max Power (W)': r['analysis'].get('max_power', 0),
                    'Stability': r['analysis'].get('stability', 0)
                }
                comparison_data.append(row)
        
        return pd.DataFrame(comparison_data)
    
    def export_config(self, filepath: Union[str, Path]) -> None:
        """
        Export configuration to file.
        
        Args:
            filepath: Path to save configuration
        """
        import json
        
        filepath = Path(filepath)
        
        # Convert config to serializable format
        config_dict = {
            'name': self.config.name,
            'description': self.config.description,
            'parameters': {
                'radius': self.config.radius,
                'blade_length_percent': self.config.blade_length_percent,
                'cutting_width': self.config.cutting_width,
                'total_mass': self.config.total_mass,
                'plate_mass_percent': self.config.plate_mass_percent,
                'n_blades': self.config.n_blades,
                'input_torque': self.config.input_torque,
                'viscous_friction': self.config.viscous_friction,
                'aerodynamic_drag': self.config.aerodynamic_drag,
                'vegetation_density': self.config.vegetation_density,
                'grass_resistance': self.config.grass_resistance,
                'advance_velocity': self.config.advance_velocity,
                'simulation_time': self.config.simulation_time,
                'time_points': self.config.time_points
            },
            'metadata': {
                'created_by': self.config.created_by,
                'tags': self.config.tags
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        self.logger.info(f"Configuration exported to {filepath}")
    
    @classmethod
    def from_config_file(cls, filepath: Union[str, Path]) -> 'RotaryCutterModel':
        """
        Create model from configuration file.
        
        Args:
            filepath: Path to configuration file
            
        Returns:
            RotaryCutterModel instance
        """
        import json
        
        filepath = Path(filepath)
        
        with open(filepath, 'r') as f:
            config_dict = json.load(f)
        
        # Create configuration
        config = RotaryCutterConfig(
            name=config_dict['name'],
            description=config_dict.get('description', ''),
            **config_dict['parameters']
        )
        
        if 'metadata' in config_dict:
            config.created_by = config_dict['metadata'].get('created_by', 'Unknown')
            config.tags = config_dict['metadata'].get('tags', [])
        
        return cls(config)
    
    def get_simulation_summary(self) -> Dict:
        """Get summary of all simulations run with this model."""
        if not self.simulation_history:
            return {'total_simulations': 0}
        
        successful = [r for r in self.simulation_history if r.success]
        failed = [r for r in self.simulation_history if not r.success]
        
        return {
            'total_simulations': len(self.simulation_history),
            'successful': len(successful),
            'failed': len(failed),
            'total_execution_time': sum(r.execution_time for r in self.simulation_history),
            'average_execution_time': np.mean([r.execution_time for r in self.simulation_history])
        }


class ConfigurationManager:
    """
    Manager for multiple rotary cutter configurations.
    
    This class provides utilities for managing collections of configurations,
    batch processing, and comparative analysis.
    """
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.configurations: Dict[str, RotaryCutterConfig] = {}
        self.logger = logging.getLogger(__name__)
    
    def add_config(self, config: RotaryCutterConfig) -> None:
        """Add a configuration to the manager."""
        self.configurations[config.name] = config
        self.logger.info(f"Added configuration: {config.name}")
    
    def remove_config(self, name: str) -> None:
        """Remove a configuration by name."""
        if name in self.configurations:
            del self.configurations[name]
            self.logger.info(f"Removed configuration: {name}")
        else:
            self.logger.warning(f"Configuration not found: {name}")
    
    def get_config(self, name: str) -> Optional[RotaryCutterConfig]:
        """Get a configuration by name."""
        return self.configurations.get(name)
    
    def list_configs(self) -> List[str]:
        """Get list of configuration names."""
        return list(self.configurations.keys())
    
    def batch_simulate(self, config_names: Optional[List[str]] = None) -> Dict[str, SimulationResult]:
        """
        Run simulations for multiple configurations.
        
        Args:
            config_names: Names of configurations to simulate. If None, simulates all.
            
        Returns:
            Dictionary mapping configuration names to results
        """
        if config_names is None:
            config_names = self.list_configs()
        
        results = {}
        
        for name in config_names:
            config = self.get_config(name)
            if config is None:
                self.logger.error(f"Configuration not found: {name}")
                continue
            
            try:
                model = RotaryCutterModel(config)
                result = model.run_simulation(store_history=False)
                results[name] = result
                self.logger.info(f"Simulated {name} successfully")
            except Exception as e:
                self.logger.error(f"Failed to simulate {name}: {e}")
        
        return results
    
    def export_all(self, directory: Union[str, Path]) -> None:
        """
        Export all configurations to a directory.
        
        Args:
            directory: Directory to save configurations
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        
        for name, config in self.configurations.items():
            model = RotaryCutterModel(config)
            filepath = directory / f"{name.replace(' ', '_')}.json"
            model.export_config(filepath)
        
        self.logger.info(f"Exported {len(self.configurations)} configurations to {directory}")
    
    def load_from_directory(self, directory: Union[str, Path]) -> None:
        """
        Load configurations from a directory.
        
        Args:
            directory: Directory containing configuration files
        """
        directory = Path(directory)
        
        for filepath in directory.glob("*.json"):
            try:
                model = RotaryCutterModel.from_config_file(filepath)
                self.add_config(model.config)
            except Exception as e:
                self.logger.error(f"Failed to load {filepath}: {e}")
        
        self.logger.info(f"Loaded configurations from {directory}")
    
    def __len__(self) -> int:
        """Get number of configurations."""
        return len(self.configurations)
    
    def __iter__(self):
        """Iterate over configurations."""
        return iter(self.configurations.values())
