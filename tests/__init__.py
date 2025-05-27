"""
Test suite for the ORC Rotary Cutter Optimization System.

This package contains all tests for the ORC system, organized by module:
- test_core/: Tests for core physics and simulation engine
- test_models/: Tests for physical models and components
- test_analysis/: Tests for analysis and metrics tools
- test_ui/: Tests for user interface components
- fixtures/: Test data and fixtures

Test categories:
- Unit tests: Test individual functions and classes
- Integration tests: Test component interactions
- Performance tests: Test simulation performance
- UI tests: Test user interface functionality
"""

import sys
from pathlib import Path

# Add src directory to path for testing
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Test configuration
TEST_DATA_DIR = Path(__file__).parent / "fixtures"
SAMPLE_CONFIG_FILE = TEST_DATA_DIR / "sample_config.json"
SAMPLE_DATA_FILE = TEST_DATA_DIR / "sample_data.csv"

# Common test parameters
DEFAULT_TEST_PARAMS = {
    'I_plate': 0.5,
    'm_c': 1.0,
    'R': 0.6,
    'L': 0.18,
    'n_blades': 2,
    'tau_input': 200.0,
    'b': 0.1,
    'c_drag': 0.01,
    'rho_veg': 1.0,
    'k_grass': 15.0,
    'v_avance': 3.0,
    'w': 1.8
}

# Test tolerances
NUMERICAL_TOLERANCE = 1e-6
PHYSICS_TOLERANCE = 1e-4
SIMULATION_TOLERANCE = 1e-3
