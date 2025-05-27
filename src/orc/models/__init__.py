"""
Physical models and components for rotary cutter systems.

This module contains the high-level model classes and components that represent
different aspects of rotary cutter systems, including:
- Main rotary cutter model
- Torque function definitions
- Initial condition utilities
- Configuration management

Modules:
    rotary_cutter: Main rotary cutter model class
    torque_functions: Predefined torque functions (temporal and spatial)
    initial_conditions: Initial condition utilities and presets
    configuration: Configuration management and parameter handling
"""

from .rotary_cutter import (
    RotaryCutterModel,
    RotaryCutterConfig,
    ConfigurationManager
)

from .torque_functions import (
    TorqueFunctionType,
    TemporalTorqueFunctions,
    SpatialTorqueFunctions,
    create_torque_function
)

from .initial_conditions import (
    InitialConditionType,
    InitialConditionManager,
    create_initial_conditions
)

__all__ = [
    # Main model
    'RotaryCutterModel',
    'RotaryCutterConfig',
    'ConfigurationManager',
    
    # Torque functions
    'TorqueFunctionType',
    'TemporalTorqueFunctions',
    'SpatialTorqueFunctions',
    'create_torque_function',
    
    # Initial conditions
    'InitialConditionType',
    'InitialConditionManager',
    'create_initial_conditions'
]
