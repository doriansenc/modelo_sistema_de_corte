"""
Configuration management for the ORC system.

This module provides configuration management capabilities including:
- Parameter management and validation
- Settings management
- Configuration file handling
- Default parameter definitions
"""

from .parameters import (
    ParameterManager,
    DefaultParameters,
    load_parameters,
    save_parameters
)

from .settings import (
    Settings,
    load_settings,
    save_settings
)

__all__ = [
    # Parameters
    'ParameterManager',
    'DefaultParameters',
    'load_parameters',
    'save_parameters',
    
    # Settings
    'Settings',
    'load_settings',
    'save_settings'
]
