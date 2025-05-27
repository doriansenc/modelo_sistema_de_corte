# ORC - Rotary Cutter Optimization System

Advanced simulation and optimization system for rotary cutters based on physical modeling with differential equations.

## Quick Start

### Option 1: Automated Scripts (Recommended)

1. **Initial setup** (first time only):
   ```bash
   python scripts/setup.py
   ```

2. **Run the application**:
   ```bash
   python scripts/run_app.py
   ```

### Option 2: Manual Installation

1. **Create and activate virtual environment**:
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run application**:
   ```bash
   streamlit run src/orc/ui/app.py
   ```

## Project Structure

```
orc/
├── src/orc/                    # Main source code package
│   ├── core/                   # Core physics and simulation engine
│   ├── models/                 # Physical models and components
│   ├── analysis/               # Analysis and metrics tools
│   ├── config/                 # Configuration management
│   ├── ui/                     # User interface components
│   └── utils/                  # Utility functions
├── tests/                      # Test suite
├── docs/                       # Documentation
├── scripts/                    # Cross-platform scripts
├── config/                     # Configuration files
├── data/                       # Sample data and outputs
└── requirements/               # Dependency specifications
```

## Key Features

- **Advanced Physics Modeling**: Differential equation-based simulation using Newton's laws of rotational motion
- **Comprehensive Parameter Management**: Structured configuration system with validation and persistence
- **Interactive Web Interface**: Modern Streamlit-based UI with real-time visualization
- **Performance Analysis**: Built-in metrics calculation and comparative analysis tools
- **Cross-Platform Compatibility**: Works seamlessly on Windows, macOS, and Linux
- **Modular Architecture**: Clean separation of concerns with reusable components
- **Export Capabilities**: Multiple output formats (CSV, Excel, JSON) for data analysis
- **Batch Processing**: Support for multiple configuration comparison and analysis

## Installation

### Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)

### Quick Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/orc-team/orc.git
   cd orc
   ```

2. **Run the setup script**:
   ```bash
   # Basic installation
   python scripts/setup.py

   # Development installation (includes testing and development tools)
   python scripts/setup.py --dev
   ```

3. **Start the application**:
   ```bash
   python scripts/run_app.py
   ```

### Manual Installation

If you prefer manual installation or need more control:

1. **Create virtual environment**:
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   # Basic requirements
   pip install -r requirements.txt

   # Development requirements (optional)
   pip install -r requirements/dev.txt
   ```

3. **Install the package**:
   ```bash
   pip install -e .
   ```

## Usage

### Starting the Application

The easiest way to start the application is using the cross-platform launcher:

```bash
python scripts/run_app.py
```

Options:
- `--port PORT`: Specify port number (default: 8501)
- `--host HOST`: Specify host address (default: localhost)
- `--dev`: Run in development mode with debug features
- `--no-browser`: Don't automatically open browser

### Using the Web Interface

1. Open your browser to `http://localhost:8501`
2. Configure system parameters in the sidebar
3. Select torque functions and initial conditions
4. Run simulations and analyze results
5. Export data for further analysis

### Programmatic Usage

```python
from orc import RotaryCutterModel, RotaryCutterConfig

# Create configuration
config = RotaryCutterConfig(
    name="Test Configuration",
    radius=0.6,
    total_mass=15.0,
    input_torque=200.0,
    simulation_time=10.0
)

# Create and run model
model = RotaryCutterModel(config)
result = model.run_simulation()

# Analyze results
analysis = model.analyze_performance(result)
print(f"Efficiency: {analysis['efficiency']:.2%}")
```

## Documentation

- **[Installation Guide](docs/installation.md)**: Detailed installation instructions for all platforms
- **[User Guide](docs/user_guide.md)**: Complete user manual with examples
- **[API Reference](docs/api_reference.md)**: Comprehensive API documentation
- **[Physics Model](docs/physics_model.md)**: Detailed explanation of the physical model
- **[Developer Guide](docs/developer_guide.md)**: Information for contributors and developers

## System Requirements

### Minimum Requirements
- Python 3.8+
- 4 GB RAM
- 1 GB free disk space
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Recommended Requirements
- Python 3.10+
- 8 GB RAM
- 2 GB free disk space
- Multi-core processor for faster simulations

### Platform Support
- **Windows**: Windows 10/11 (x64)
- **macOS**: macOS 10.15+ (Intel and Apple Silicon)
- **Linux**: Ubuntu 18.04+, CentOS 7+, or equivalent distributions

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Clone your fork
3. Install development dependencies:
   ```bash
   python scripts/setup.py --dev
   ```
4. Create a feature branch
5. Make your changes
6. Run tests:
   ```bash
   pytest
   ```
7. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/orc-team/orc/issues)
- **Discussions**: Join the community on [GitHub Discussions](https://github.com/orc-team/orc/discussions)
- **Documentation**: Visit our [documentation site](https://orc-team.github.io/orc)

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the web interface
- Physics simulation powered by [SciPy](https://scipy.org/)
- Visualization using [Plotly](https://plotly.com/) and [Matplotlib](https://matplotlib.org/)
- Special thanks to all contributors and the open-source community


