# Installation Guide

This guide provides detailed installation instructions for the ORC Rotary Cutter Optimization System across different operating systems.

## Prerequisites

### System Requirements

**Minimum Requirements:**
- Python 3.8 or higher
- 4 GB RAM
- 1 GB free disk space
- Modern web browser (Chrome, Firefox, Safari, Edge)

**Recommended Requirements:**
- Python 3.10 or higher
- 8 GB RAM
- 2 GB free disk space
- Multi-core processor for faster simulations

### Software Dependencies

- **Git**: For cloning the repository
- **Python**: With pip package manager
- **Web Browser**: For accessing the Streamlit interface

## Platform-Specific Installation

### Windows

#### Option 1: Automated Installation (Recommended)

1. **Install Python**:
   - Download Python from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Verify installation: Open Command Prompt and run `python --version`

2. **Install Git**:
   - Download Git from [git-scm.com](https://git-scm.com/download/win)
   - Use default installation options

3. **Clone and Setup**:
   ```cmd
   git clone https://github.com/orc-team/orc.git
   cd orc
   python scripts/setup.py
   ```

4. **Run the Application**:
   ```cmd
   python scripts/run_app.py
   ```

#### Option 2: Manual Installation

1. **Create Virtual Environment**:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```cmd
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Run Application**:
   ```cmd
   streamlit run src/orc/ui/app.py
   ```

#### Windows-Specific Notes

- Use Command Prompt or PowerShell
- Virtual environment activation: `venv\Scripts\activate`
- If you encounter permission errors, run as Administrator
- For PowerShell users, you may need to enable script execution:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### macOS

#### Option 1: Automated Installation (Recommended)

1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python and Git**:
   ```bash
   brew install python git
   ```

3. **Clone and Setup**:
   ```bash
   git clone https://github.com/orc-team/orc.git
   cd orc
   python3 scripts/setup.py
   ```

4. **Run the Application**:
   ```bash
   python3 scripts/run_app.py
   ```

#### Option 2: Using System Python

1. **Verify Python Installation**:
   ```bash
   python3 --version
   # Should be 3.8 or higher
   ```

2. **Clone Repository**:
   ```bash
   git clone https://github.com/orc-team/orc.git
   cd orc
   ```

3. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -e .
   ```

#### macOS-Specific Notes

- Use `python3` instead of `python` on most macOS systems
- Virtual environment activation: `source venv/bin/activate`
- For Apple Silicon Macs, all dependencies should work natively
- If you encounter SSL certificate errors, update certificates:
  ```bash
  /Applications/Python\ 3.x/Install\ Certificates.command
  ```

### Linux (Ubuntu/Debian)

#### Option 1: Automated Installation (Recommended)

1. **Update System and Install Dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv git
   ```

2. **Clone and Setup**:
   ```bash
   git clone https://github.com/orc-team/orc.git
   cd orc
   python3 scripts/setup.py
   ```

3. **Run the Application**:
   ```bash
   python3 scripts/run_app.py
   ```

#### Option 2: Manual Installation

1. **Install System Dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv git build-essential
   ```

2. **Clone Repository**:
   ```bash
   git clone https://github.com/orc-team/orc.git
   cd orc
   ```

3. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -e .
   ```

### Linux (CentOS/RHEL/Fedora)

#### CentOS/RHEL 7/8:
```bash
sudo yum install python3 python3-pip git
# or for newer versions:
sudo dnf install python3 python3-pip git
```

#### Fedora:
```bash
sudo dnf install python3 python3-pip git
```

Then follow the same steps as Ubuntu/Debian.

## Development Installation

For contributors and developers who want to work on the codebase:

### 1. Fork and Clone
```bash
# Fork the repository on GitHub first
git clone https://github.com/YOUR_USERNAME/orc.git
cd orc
```

### 2. Install Development Dependencies
```bash
python scripts/setup.py --dev
```

This installs additional tools for development:
- Testing framework (pytest)
- Code formatting (black, isort)
- Linting (flake8, mypy)
- Documentation tools (sphinx)
- Jupyter notebooks

### 3. Set Up Pre-commit Hooks (Optional)
```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install pre-commit hooks
pre-commit install
```

## Verification

After installation, verify everything works correctly:

### 1. Test Basic Imports
```bash
python -c "import orc; print(f'ORC version: {orc.get_version()}')"
```

### 2. Run Tests (Development Installation)
```bash
pytest tests/
```

### 3. Start the Application
```bash
python scripts/run_app.py --no-browser
```

The application should start and display:
```
ORC - ROTARY CUTTER OPTIMIZATION SYSTEM
========================================
URL: http://localhost:8501
```

## Troubleshooting

### Common Issues

#### Python Version Issues
```bash
# Check Python version
python --version
python3 --version

# Use specific Python version
python3.10 -m venv venv
```

#### Permission Errors (Windows)
- Run Command Prompt as Administrator
- Check antivirus software settings
- Ensure Python is added to PATH

#### SSL Certificate Errors
```bash
# macOS
/Applications/Python\ 3.x/Install\ Certificates.command

# Linux
sudo apt-get update && sudo apt-get install ca-certificates

# Windows
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org <package>
```

#### Port Already in Use
```bash
# Use different port
python scripts/run_app.py --port 8502
```

#### Memory Issues
- Close other applications
- Increase virtual memory/swap space
- Use smaller simulation parameters

### Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/orc-team/orc/issues)
2. Search existing issues for solutions
3. Create a new issue with:
   - Operating system and version
   - Python version
   - Complete error message
   - Steps to reproduce

## Next Steps

After successful installation:

1. Read the [User Guide](user_guide.md) for usage instructions
2. Explore the [API Reference](api_reference.md) for programmatic usage
3. Check out [Physics Model](physics_model.md) to understand the underlying mathematics
4. See [Examples](../examples/) for sample configurations and use cases

## Updating

To update to the latest version:

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Reinstall package
pip install -e .
```

For major updates, it's recommended to recreate the virtual environment:

```bash
# Remove old environment
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# Run setup again
python scripts/setup.py
```
