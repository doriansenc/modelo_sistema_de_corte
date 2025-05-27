"""
ORC - Rotary Cutter Optimization System

A comprehensive simulation and optimization system for rotary cutters based on 
advanced physical modeling with differential equations.

This package provides:
- Core physics simulation engine
- Physical models for rotary cutter systems
- Analysis and performance metrics tools
- Configuration management
- User interface components
- Utility functions

Author: ORC Development Team
License: Academic Use
"""

__version__ = "2.0.0"
__author__ = "ORC Development Team"
__email__ = "orc-dev@example.com"

# Core imports for easy access
from .core.simulation import SimulationEngine
from .models.rotary_cutter import RotaryCutterModel
from .config.parameters import ParameterManager
from .analysis.metrics import PerformanceAnalyzer

# Version information
VERSION_INFO = {
    'major': 2,
    'minor': 0,
    'patch': 0,
    'release': 'stable'
}

def get_version():
    """Get the current version string."""
    return __version__

def get_version_info():
    """Get detailed version information."""
    return VERSION_INFO.copy()

# Package-level configuration
DEFAULT_CONFIG = {
    'simulation': {
        'default_method': 'RK45',
        'default_rtol': 1e-8,
        'default_atol': 1e-10
    },
    'analysis': {
        'default_metrics': ['efficiency', 'stability', 'power'],
        'export_formats': ['csv', 'excel', 'json']
    },
    'ui': {
        'theme': 'professional',
        'layout': 'wide'
    }
}

def get_default_config():
    """Get the default package configuration."""
    return DEFAULT_CONFIG.copy()
