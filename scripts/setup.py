#!/usr/bin/env python3
"""
Cross-platform setup script for the ORC Rotary Cutter Optimization System.

This script handles:
- Virtual environment creation
- Dependency installation
- Platform-specific configuration
- Development environment setup

Usage:
    python scripts/setup.py [options]

Options:
    --dev       Install development dependencies
    --force     Force reinstallation of virtual environment
    --python    Specify Python executable (default: python)
"""

import sys
import os
import subprocess
import platform
import argparse
from pathlib import Path
import logging


def setup_logging():
    """Configure logging for the setup process."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    return logging.getLogger(__name__)


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_python_executable(python_cmd="python"):
    """Get the appropriate Python executable."""
    try:
        # Test if the specified Python works
        result = subprocess.run([python_cmd, "--version"], 
                              capture_output=True, text=True, check=True)
        logger.info(f"Using Python: {result.stdout.strip()}")
        return python_cmd
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Try alternatives
        alternatives = ["python3", "python3.9", "python3.10", "python3.11", "python3.12"]
        for alt in alternatives:
            try:
                result = subprocess.run([alt, "--version"], 
                                      capture_output=True, text=True, check=True)
                logger.info(f"Using Python: {result.stdout.strip()}")
                return alt
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        raise RuntimeError("No suitable Python executable found")


def create_virtual_environment(project_root, python_cmd, force=False):
    """Create a virtual environment."""
    venv_path = project_root / "venv"
    
    if venv_path.exists() and not force:
        logger.info("Virtual environment already exists. Use --force to recreate.")
        return venv_path
    
    if venv_path.exists() and force:
        logger.info("Removing existing virtual environment...")
        import shutil
        shutil.rmtree(venv_path)
    
    logger.info("Creating virtual environment...")
    subprocess.run([python_cmd, "-m", "venv", str(venv_path)], check=True)
    
    return venv_path


def get_venv_python(venv_path):
    """Get the Python executable in the virtual environment."""
    system = platform.system().lower()
    
    if system == "windows":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"


def get_venv_pip(venv_path):
    """Get the pip executable in the virtual environment."""
    system = platform.system().lower()
    
    if system == "windows":
        return venv_path / "Scripts" / "pip.exe"
    else:
        return venv_path / "bin" / "pip"


def upgrade_pip(venv_path):
    """Upgrade pip in the virtual environment."""
    logger.info("Upgrading pip...")
    pip_cmd = get_venv_pip(venv_path)
    subprocess.run([str(pip_cmd), "install", "--upgrade", "pip"], check=True)


def install_dependencies(venv_path, project_root, dev=False):
    """Install project dependencies."""
    pip_cmd = get_venv_pip(venv_path)
    
    # Install base requirements
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        logger.info("Installing base requirements...")
        subprocess.run([str(pip_cmd), "install", "-r", str(requirements_file)], check=True)
    
    # Install development requirements if requested
    if dev:
        dev_requirements = project_root / "requirements" / "dev.txt"
        if dev_requirements.exists():
            logger.info("Installing development requirements...")
            subprocess.run([str(pip_cmd), "install", "-r", str(dev_requirements)], check=True)
        else:
            logger.info("Installing common development packages...")
            dev_packages = [
                "pytest>=7.0.0",
                "pytest-cov>=4.0.0",
                "black>=23.0.0",
                "flake8>=6.0.0",
                "mypy>=1.0.0",
                "jupyter>=1.0.0",
                "ipykernel>=6.0.0"
            ]
            subprocess.run([str(pip_cmd), "install"] + dev_packages, check=True)
    
    # Install the package in development mode
    logger.info("Installing ORC package in development mode...")
    subprocess.run([str(pip_cmd), "install", "-e", str(project_root)], check=True)


def create_activation_scripts(project_root, venv_path):
    """Create convenient activation scripts."""
    system = platform.system().lower()
    
    if system == "windows":
        # Create batch file for Windows
        activate_script = project_root / "activate.bat"
        with open(activate_script, 'w') as f:
            f.write(f'@echo off\n')
            f.write(f'call "{venv_path}\\Scripts\\activate.bat"\n')
            f.write(f'echo Virtual environment activated!\n')
            f.write(f'echo Run "python scripts/run_app.py" to start the application.\n')
        
        # Create PowerShell script
        activate_ps1 = project_root / "activate.ps1"
        with open(activate_ps1, 'w') as f:
            f.write(f'& "{venv_path}\\Scripts\\Activate.ps1"\n')
            f.write(f'Write-Host "Virtual environment activated!"\n')
            f.write(f'Write-Host "Run \'python scripts/run_app.py\' to start the application."\n')
    
    else:
        # Create shell script for Unix-like systems
        activate_script = project_root / "activate.sh"
        with open(activate_script, 'w') as f:
            f.write(f'#!/bin/bash\n')
            f.write(f'source "{venv_path}/bin/activate"\n')
            f.write(f'echo "Virtual environment activated!"\n')
            f.write(f'echo "Run \'python scripts/run_app.py\' to start the application."\n')
        
        # Make it executable
        os.chmod(activate_script, 0o755)
    
    logger.info(f"Created activation script: {activate_script}")


def create_environment_file(project_root):
    """Create a .env.example file with default settings."""
    env_example = project_root / ".env.example"
    
    env_content = """# ORC Environment Configuration
# Copy this file to .env and modify as needed

# Application settings
ORC_DEBUG=false
ORC_LOG_LEVEL=INFO

# Streamlit settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost

# Simulation settings
ORC_DEFAULT_SIMULATION_TIME=10.0
ORC_DEFAULT_TIME_POINTS=1000
ORC_MAX_SIMULATION_TIME=3600.0

# Performance settings
ORC_ENABLE_CACHING=true
ORC_CACHE_SIZE=100

# Export settings
ORC_DEFAULT_EXPORT_FORMAT=csv
ORC_EXPORT_DIRECTORY=./data/outputs
"""
    
    with open(env_example, 'w') as f:
        f.write(env_content)
    
    logger.info("Created .env.example file")


def verify_installation(venv_path):
    """Verify that the installation was successful."""
    logger.info("Verifying installation...")
    
    python_cmd = get_venv_python(venv_path)
    
    # Test basic imports
    test_script = """
import sys
try:
    import streamlit
    import numpy
    import pandas
    import scipy
    import matplotlib
    import plotly
    import orc
    print("All imports successful!")
    print(f"ORC version: {orc.get_version()}")
    sys.exit(0)
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
"""
    
    result = subprocess.run([str(python_cmd), "-c", test_script], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        logger.info("Installation verification successful!")
        logger.info(result.stdout.strip())
    else:
        logger.error("Installation verification failed!")
        logger.error(result.stderr.strip())
        return False
    
    return True


def print_next_steps(project_root):
    """Print instructions for next steps."""
    system = platform.system().lower()
    
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    
    if system == "windows":
        print(f"   activate.bat")
        print(f"   # or in PowerShell: .\\activate.ps1")
    else:
        print(f"   source activate.sh")
    
    print("\n2. Start the application:")
    print("   python scripts/run_app.py")
    
    print("\n3. Open your browser to:")
    print("   http://localhost:8501")
    
    print("\nFor development:")
    print("- Run tests: pytest")
    print("- Format code: black src/")
    print("- Type checking: mypy src/")
    
    print("\nDocumentation:")
    print("- User guide: docs/user_guide.md")
    print("- API reference: docs/api_reference.md")
    print("- Physics model: docs/physics_model.md")
    print("="*60)


def main():
    """Main setup function."""
    global logger
    logger = setup_logging()
    
    parser = argparse.ArgumentParser(description="Setup ORC development environment")
    parser.add_argument("--dev", action="store_true", 
                       help="Install development dependencies")
    parser.add_argument("--force", action="store_true",
                       help="Force recreation of virtual environment")
    parser.add_argument("--python", default="python",
                       help="Python executable to use")
    
    args = parser.parse_args()
    
    try:
        project_root = get_project_root()
        logger.info(f"Setting up ORC in: {project_root}")
        
        # Get Python executable
        python_cmd = get_python_executable(args.python)
        
        # Create virtual environment
        venv_path = create_virtual_environment(project_root, python_cmd, args.force)
        
        # Upgrade pip
        upgrade_pip(venv_path)
        
        # Install dependencies
        install_dependencies(venv_path, project_root, args.dev)
        
        # Create activation scripts
        create_activation_scripts(project_root, venv_path)
        
        # Create environment file
        create_environment_file(project_root)
        
        # Verify installation
        if verify_installation(venv_path):
            print_next_steps(project_root)
        else:
            logger.error("Setup completed with errors. Please check the logs.")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
