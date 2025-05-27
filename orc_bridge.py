"""
ORC Bridge Module - Compatibility Layer

This module provides backward compatibility between the old main_model.py API
and the new modular architecture in src/orc/. It allows the existing Streamlit
application to work without changes while using the new modular structure.

This bridge will be used during the transition period and can be removed
once the Streamlit app is fully migrated to use the new API directly.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Callable, Any, Tuple
import sys
import os

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import from new modular structure
try:
    from orc.core.physics import RotaryCutterPhysics
    from orc.core.simulation import SimulationEngine, SimulationConfig, SimulationResult
    from orc.core.validation import ParameterValidator, ValidationError
    from orc.models.rotary_cutter import RotaryCutterModel, RotaryCutterConfig
    from orc.analysis.metrics import PerformanceAnalyzer
    NEW_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: New modules not available, falling back to main_model.py: {e}")
    NEW_MODULES_AVAILABLE = False
    # Import from original main_model as fallback
    from main_model import *

# Only define bridge functions if new modules are available
if NEW_MODULES_AVAILABLE:

    # Global instances for compatibility
    _physics_engine = RotaryCutterPhysics()
    _simulation_engine = SimulationEngine(_physics_engine)
    _validator = ParameterValidator()
    _analyzer = PerformanceAnalyzer()

    def run_simulation(mass: float, radius: float, omega: float = None,
                      T_end: float = 5.0, dt: float = 0.01,
                      geometry: str = "disk", torque_type: str = "advanced_model",
                      use_advanced_model: bool = True,
                      advanced_params: Optional[Dict] = None,
                      y0: Optional[list] = None) -> Dict:
        """
        Bridge function for run_simulation - maintains original API.
        """
        try:
            # Use the original main_model implementation for now
            # This ensures 100% compatibility
            import main_model
            return main_model.run_simulation(
                mass, radius, omega, T_end, dt, geometry,
                torque_type, use_advanced_model, advanced_params, y0
            )

        except Exception as e:
            # If main_model fails, try a simplified implementation
            if advanced_params is None:
                advanced_params = create_default_params(mass, radius)

            # Use the original simulate_advanced_configuration function
            import main_model
            return main_model.simulate_advanced_configuration(
                advanced_params, T_end, np.linspace(0, T_end, int(T_end/dt)), y0
            )

    def create_default_params(mass: float = 10.0, radius: float = 0.5,
                             tau_input: float = 100.0) -> Dict:
        """
        Bridge function for create_default_params - maintains original API.
        """
        # Create parameters in the old format directly
        return {
            'I_plate': mass * 0.4 * radius**2,  # Estimate plate moment of inertia
            'm_c': mass * 0.1,  # Estimate blade mass (10% of total)
            'R': radius,
            'L': radius * 0.3,  # Estimate blade length
            'tau_input': tau_input,
            'b': 0.1,  # Default viscous friction
            'c_drag': 0.01,  # Default aerodynamic drag
            'rho_veg': 1.0,  # Default vegetation density
            'k_grass': 15.0,  # Default grass resistance
            'v_avance': 3.0,  # Default advance velocity
            'n_blades': 2,  # Default number of blades
            'w': 1.8  # Default cutting width
        }

    def create_validated_params(base_params: Dict, **overrides) -> Dict:
        """
        Bridge function for create_validated_params - maintains original API.
        """
        # Combine parameters
        params = base_params.copy()
        params.update(overrides)

        # Validate using new validator
        _validator.validate_parameters(params)

        return params

    def validate_params(params: Dict) -> None:
        """
        Bridge function for validate_params - maintains original API.
        """
        # Use original validation for compatibility
        import main_model
        main_model.validate_params(params)

    def analyze_performance(results: Dict) -> Dict:
        """
        Bridge function for analyze_performance - maintains original API.
        """
        # Convert old results format to new format if needed
        if 'simulation_result' in results:
            # Already in new format
            return _analyzer.analyze(results['simulation_result'])
        else:
            # Convert old format to new format for analysis
            # This is a simplified conversion - may need adjustment
            return {
                'efficiency': results.get('advanced_metrics', {}).get('eta', 0.0),
                'omega_stability': 1.0 - (np.std(results.get('omega', [0])) / (np.mean(np.abs(results.get('omega', [1]))) + 1e-10)),
                'torque_stability': 1.0 - (np.std(results.get('torque', [0])) / (np.mean(np.abs(results.get('torque', [1]))) + 1e-10)),
                'avg_power': np.mean(results.get('power', [0])),
                'peak_power': np.max(results.get('power', [0])),
                'energy_total': results.get('work_total', 0)
            }

    def compute_metrics(sol, params):
        """
        Bridge function for compute_metrics - maintains original API.
        """
        # Convert solve_ivp solution to new format
        time = sol.t
        omega = sol.y[1]

        # Calculate basic metrics using old method for compatibility
        dt = np.diff(time)
        omega_avg = (omega[:-1] + omega[1:]) / 2

        tau_input = params['tau_input']
        R = params['R']
        k_grass = params['k_grass']
        rho_veg = params['rho_veg']
        v_avance = params['v_avance']
        w = params.get('w', 1.8)

        # Energy calculations
        power_total = tau_input * omega_avg
        E_total = np.sum(power_total * dt)

        if 'tau_grass_func' in params and params['tau_grass_func'] is not None:
            tau_grass_values = np.array([params['tau_grass_func'](t_i) for t_i in time[:-1]])
            power_util = tau_grass_values * omega_avg
        else:
            tau_grass = k_grass * rho_veg * v_avance * R
            power_util = tau_grass * omega_avg

        E_util = np.sum(power_util * dt)
        A_total = v_avance * w * time[-1]

        eta = E_util / E_total if E_total > 0 else 0
        epsilon = A_total / E_total if E_total > 0 else 0

        return {
            'E_total': E_total,
            'E_util': E_util,
            'A_total': A_total,
            'eta': eta,
            'epsilon': epsilon,
            'power_total_avg': np.mean(power_total),
            'power_util_avg': np.mean(power_util),
            'cutting_width': w,
            'cutting_speed': v_avance,
            'simulation_time': time[-1]
        }

    def _params_to_config(params: Dict, mass: float, radius: float,
                         T_end: float, dt: float) -> RotaryCutterConfig:
        """Convert old parameter format to new configuration format."""
        # Extract parameters with defaults
        blade_mass = params.get('m_c', mass * 0.1)  # Estimate blade mass
        n_blades = params.get('n_blades', 2)
        total_blade_mass = blade_mass * n_blades
        plate_mass = mass - total_blade_mass
        plate_mass_percent = (plate_mass / mass) * 100 if mass > 0 else 40.0

        # Calculate blade length from parameters
        L = params.get('L', radius * 0.3)
        blade_length_percent = (L / radius) * 100 if radius > 0 else 30.0

        config = RotaryCutterConfig(
            name="Bridge Configuration",
            radius=radius,
            blade_length_percent=blade_length_percent,
            cutting_width=params.get('w', 1.8),
            total_mass=mass,
            plate_mass_percent=plate_mass_percent,
            n_blades=n_blades,
            input_torque=params.get('tau_input', 200.0),
            viscous_friction=params.get('b', 0.1),
            aerodynamic_drag=params.get('c_drag', 0.01),
            vegetation_density=params.get('rho_veg', 1.0),
            grass_resistance=params.get('k_grass', 15.0),
            advance_velocity=params.get('v_avance', 3.0),
            simulation_time=T_end,
            time_points=int(T_end / dt),
            torque_function=params.get('tau_grass_func')
        )

        return config

    def _convert_result_to_old_format(result: SimulationResult, config: RotaryCutterConfig) -> Dict:
        """Convert new SimulationResult to old result format."""
        # Calculate moment of inertia
        physics_params = config.to_physics_parameters()
        I_total = _physics_engine.calculate_total_moment_of_inertia(physics_params)

        # Calculate advanced metrics using old method
        class MockSol:
            def __init__(self, t, y):
                self.t = t
                self.y = y
                self.success = True

        mock_sol = MockSol(result.time, np.array([result.angle, result.angular_velocity]))
        advanced_metrics = compute_metrics(mock_sol, physics_params)

        return {
            'time': result.time,
            'theta': result.angle,
            'omega': result.angular_velocity,
            'torque': result.torque,
            'kinetic_energy': result.kinetic_energy,
            'power': result.power,
            'moment_of_inertia': I_total,
            'work_total': np.trapz(result.power, result.time),
            'statistics': {
                'omega_max': np.max(np.abs(result.angular_velocity)),
                'omega_rms': np.sqrt(np.mean(result.angular_velocity**2)),
                'torque_max': np.max(np.abs(result.torque)),
                'torque_rms': np.sqrt(np.mean(result.torque**2)),
                'energy_avg': np.mean(result.kinetic_energy),
                'simulation_time': result.time[-1],
                'integration_points': len(result.time),
                'success': result.success
            },
            'advanced_metrics': advanced_metrics,
            'simulation_result': result  # Include new format for future use
        }

# Import torque functions and other utilities from main_model for now
# These will be implemented in the new structure later
if not NEW_MODULES_AVAILABLE:
    # If new modules aren't available, everything is imported from main_model above
    pass
else:
    # Import remaining functions from main_model for now
    # TODO: Implement these in the new modular structure
    try:
        from main_model import (
            # Torque functions
            tau_grass_sinusoidal, tau_grass_step, tau_grass_ramp, tau_grass_exponential,
            tau_grass_spatial_zones, tau_grass_spatial_gaussian_patches,
            tau_grass_spatial_sigmoid_transition, tau_grass_spatial_sinusoidal,
            tau_grass_spatial_complex_terrain,
            # Initial condition functions
            create_initial_conditions, initial_conditions_from_rpm,
            initial_conditions_blade_angle, initial_conditions_spinning,
            # Configuration classes
            RotaryCutterConfig as OldRotaryCutterConfig,
            ConfigurationManager as OldConfigurationManager
        )

        # Use old configuration classes for now
        RotaryCutterConfig = OldRotaryCutterConfig
        ConfigurationManager = OldConfigurationManager

    except ImportError:
        # Define minimal stubs if main_model is not available
        def tau_grass_sinusoidal(*args, **kwargs):
            raise NotImplementedError("Torque functions not yet implemented in new architecture")

        def tau_grass_step(*args, **kwargs):
            raise NotImplementedError("Torque functions not yet implemented in new architecture")

        def tau_grass_ramp(*args, **kwargs):
            raise NotImplementedError("Torque functions not yet implemented in new architecture")

        def tau_grass_exponential(*args, **kwargs):
            raise NotImplementedError("Torque functions not yet implemented in new architecture")

        def tau_grass_spatial_zones(*args, **kwargs):
            raise NotImplementedError("Spatial torque functions not yet implemented in new architecture")

        def tau_grass_spatial_gaussian_patches(*args, **kwargs):
            raise NotImplementedError("Spatial torque functions not yet implemented in new architecture")

        def tau_grass_spatial_sigmoid_transition(*args, **kwargs):
            raise NotImplementedError("Spatial torque functions not yet implemented in new architecture")

        def tau_grass_spatial_sinusoidal(*args, **kwargs):
            raise NotImplementedError("Spatial torque functions not yet implemented in new architecture")

        def tau_grass_spatial_complex_terrain(*args, **kwargs):
            raise NotImplementedError("Spatial torque functions not yet implemented in new architecture")

        def create_initial_conditions(*args, **kwargs):
            raise NotImplementedError("Initial condition functions not yet implemented in new architecture")

        def initial_conditions_from_rpm(*args, **kwargs):
            raise NotImplementedError("Initial condition functions not yet implemented in new architecture")

        def initial_conditions_blade_angle(*args, **kwargs):
            raise NotImplementedError("Initial condition functions not yet implemented in new architecture")

        def initial_conditions_spinning(*args, **kwargs):
            raise NotImplementedError("Initial condition functions not yet implemented in new architecture")

        class RotaryCutterConfig:
            def __init__(self, *args, **kwargs):
                raise NotImplementedError("Configuration classes not yet implemented in new architecture")

        class ConfigurationManager:
            def __init__(self, *args, **kwargs):
                raise NotImplementedError("Configuration classes not yet implemented in new architecture")
