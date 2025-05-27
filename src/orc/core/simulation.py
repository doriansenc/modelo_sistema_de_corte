"""
Simulation engine for rotary cutter systems.

This module provides the main simulation engine that orchestrates the numerical
integration of the differential equation system and manages simulation results.

The simulation engine supports:
- Multiple integration methods (RK45, RK23, DOP853, etc.)
- Adaptive time stepping
- Error control and validation
- Result post-processing
"""

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from typing import Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import logging

from .physics import RotaryCutterPhysics
from .validation import ParameterValidator, ValidationError


class IntegrationMethod(Enum):
    """Available integration methods for the simulation."""
    RK45 = "RK45"
    RK23 = "RK23"
    DOP853 = "DOP853"
    RADAU = "Radau"
    BDF = "BDF"
    LSODA = "LSODA"


@dataclass
class SimulationConfig:
    """Configuration parameters for simulation."""
    
    # Time parameters
    t_start: float = 0.0
    t_end: float = 10.0
    n_points: int = 1000
    
    # Integration parameters
    method: IntegrationMethod = IntegrationMethod.RK45
    rtol: float = 1e-8
    atol: float = 1e-10
    max_step: Optional[float] = None
    
    # Initial conditions
    initial_angle: float = 0.0
    initial_angular_velocity: float = 0.0
    
    # Output options
    dense_output: bool = False
    vectorized: bool = False


@dataclass
class SimulationResult:
    """Container for simulation results and metadata."""
    
    # Time series data
    time: np.ndarray
    angle: np.ndarray
    angular_velocity: np.ndarray
    torque: np.ndarray
    power: np.ndarray
    kinetic_energy: np.ndarray
    
    # Simulation metadata
    success: bool
    message: str
    n_evaluations: int
    execution_time: float
    
    # Physical parameters used
    parameters: Dict
    config: SimulationConfig
    
    # Derived quantities
    statistics: Dict = field(default_factory=dict)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert time series data to pandas DataFrame."""
        return pd.DataFrame({
            'time': self.time,
            'angle': self.angle,
            'angular_velocity': self.angular_velocity,
            'torque': self.torque,
            'power': self.power,
            'kinetic_energy': self.kinetic_energy
        })
    
    def get_final_state(self) -> Dict:
        """Get the final state of the simulation."""
        return {
            'final_time': self.time[-1],
            'final_angle': self.angle[-1],
            'final_angular_velocity': self.angular_velocity[-1],
            'final_torque': self.torque[-1],
            'final_power': self.power[-1],
            'final_kinetic_energy': self.kinetic_energy[-1]
        }


class SimulationEngine:
    """
    Main simulation engine for rotary cutter systems.
    
    This class orchestrates the numerical integration of the differential
    equation system and provides methods for running simulations with
    different configurations.
    """
    
    def __init__(self, physics_engine: Optional[RotaryCutterPhysics] = None,
                 validator: Optional[ParameterValidator] = None):
        """
        Initialize the simulation engine.
        
        Args:
            physics_engine: Physics engine to use. If None, a default is created.
            validator: Parameter validator to use. If None, a default is created.
        """
        self.physics = physics_engine or RotaryCutterPhysics()
        self.validator = validator or ParameterValidator()
        self.logger = logging.getLogger(__name__)
    
    def run_simulation(self, parameters: Dict, 
                      config: Optional[SimulationConfig] = None) -> SimulationResult:
        """
        Run a complete simulation with the given parameters and configuration.
        
        Args:
            parameters: Physical parameters for the system
            config: Simulation configuration. If None, defaults are used.
            
        Returns:
            SimulationResult containing all simulation data and metadata
            
        Raises:
            ValidationError: If parameters or configuration are invalid
        """
        # Use default config if none provided
        if config is None:
            config = SimulationConfig()
        
        # Validate inputs
        self.validator.validate_parameters(parameters)
        self._validate_config(config)
        
        # Record start time
        start_time = time.time()
        
        # Set up initial conditions
        y0 = [config.initial_angle, config.initial_angular_velocity]
        
        # Set up time evaluation points
        t_eval = np.linspace(config.t_start, config.t_end, config.n_points)
        
        # Run integration
        try:
            sol = solve_ivp(
                fun=lambda t, y: self.physics.differential_equation_system(t, y, parameters),
                t_span=(config.t_start, config.t_end),
                y0=y0,
                method=config.method.value,
                t_eval=t_eval,
                rtol=config.rtol,
                atol=config.atol,
                max_step=config.max_step,
                dense_output=config.dense_output,
                vectorized=config.vectorized
            )
            
            execution_time = time.time() - start_time
            
            if not sol.success:
                raise RuntimeError(f"Integration failed: {sol.message}")
            
            # Extract results
            time_array = sol.t
            angle_array = sol.y[0]
            angular_velocity_array = sol.y[1]
            
            # Calculate derived quantities
            torque_array = self._calculate_torque_time_series(
                time_array, angular_velocity_array, parameters
            )
            power_array = torque_array * angular_velocity_array
            
            # Calculate kinetic energy
            I_total = self.physics.calculate_total_moment_of_inertia(parameters)
            kinetic_energy_array = 0.5 * I_total * angular_velocity_array**2
            
            # Calculate statistics
            statistics = self._calculate_statistics(
                time_array, angle_array, angular_velocity_array,
                torque_array, power_array, kinetic_energy_array
            )
            
            # Create result object
            result = SimulationResult(
                time=time_array,
                angle=angle_array,
                angular_velocity=angular_velocity_array,
                torque=torque_array,
                power=power_array,
                kinetic_energy=kinetic_energy_array,
                success=True,
                message="Simulation completed successfully",
                n_evaluations=sol.nfev,
                execution_time=execution_time,
                parameters=parameters.copy(),
                config=config,
                statistics=statistics
            )
            
            self.logger.info(f"Simulation completed successfully in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Simulation failed: {str(e)}")
            
            # Return failed result with minimal data
            return SimulationResult(
                time=np.array([]),
                angle=np.array([]),
                angular_velocity=np.array([]),
                torque=np.array([]),
                power=np.array([]),
                kinetic_energy=np.array([]),
                success=False,
                message=str(e),
                n_evaluations=0,
                execution_time=execution_time,
                parameters=parameters.copy(),
                config=config
            )
    
    def _calculate_torque_time_series(self, time_array: np.ndarray,
                                    angular_velocity_array: np.ndarray,
                                    parameters: Dict) -> np.ndarray:
        """Calculate torque time series."""
        torque_array = np.zeros_like(time_array)
        
        for i, (t, omega) in enumerate(zip(time_array, angular_velocity_array)):
            torque_components = self.physics.calculate_torque_components(t, omega, parameters)
            torque_array[i] = torque_components['net']
        
        return torque_array
    
    def _calculate_statistics(self, time_array: np.ndarray, angle_array: np.ndarray,
                            angular_velocity_array: np.ndarray, torque_array: np.ndarray,
                            power_array: np.ndarray, kinetic_energy_array: np.ndarray) -> Dict:
        """Calculate simulation statistics."""
        return {
            'duration': time_array[-1] - time_array[0],
            'n_points': len(time_array),
            'angle_range': float(np.ptp(angle_array)),
            'angular_velocity_max': float(np.max(np.abs(angular_velocity_array))),
            'angular_velocity_rms': float(np.sqrt(np.mean(angular_velocity_array**2))),
            'torque_max': float(np.max(np.abs(torque_array))),
            'torque_rms': float(np.sqrt(np.mean(torque_array**2))),
            'power_avg': float(np.mean(power_array)),
            'power_max': float(np.max(power_array)),
            'energy_avg': float(np.mean(kinetic_energy_array)),
            'energy_final': float(kinetic_energy_array[-1]),
            'work_total': float(np.trapz(power_array, time_array))
        }
    
    def _validate_config(self, config: SimulationConfig) -> None:
        """Validate simulation configuration."""
        if config.t_end <= config.t_start:
            raise ValidationError("End time must be greater than start time")
        
        if config.n_points < 10:
            raise ValidationError("Number of points must be at least 10")
        
        if config.rtol <= 0 or config.atol <= 0:
            raise ValidationError("Tolerances must be positive")
        
        if config.max_step is not None and config.max_step <= 0:
            raise ValidationError("Maximum step size must be positive")
