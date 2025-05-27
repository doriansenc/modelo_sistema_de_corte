"""
Core physics and simulation engine for the ORC system.

This module contains the fundamental physics equations, simulation engine,
and validation logic that form the foundation of the rotary cutter modeling system.

Modules:
    physics: Core physics equations and mathematical models
    simulation: Simulation engine and integration methods
    validation: Parameter and input validation logic
"""

from .physics import (
    RotaryCutterPhysics,
    calculate_moment_of_inertia,
    calculate_torque_components
)

from .simulation import (
    SimulationEngine,
    SimulationResult,
    IntegrationMethod
)

from .validation import (
    ParameterValidator,
    ValidationError,
    validate_simulation_inputs
)

__all__ = [
    # Physics
    'RotaryCutterPhysics',
    'calculate_moment_of_inertia',
    'calculate_torque_components',
    
    # Simulation
    'SimulationEngine',
    'SimulationResult',
    'IntegrationMethod',
    
    # Validation
    'ParameterValidator',
    'ValidationError',
    'validate_simulation_inputs'
]
