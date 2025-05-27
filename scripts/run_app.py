#!/usr/bin/env python3
"""
Cross-platform application launcher for the ORC Rotary Cutter Optimization System.

This script handles:
- Virtual environment detection and activation
- Streamlit application launching
- Port management and conflict resolution
- Environment variable configuration
- Logging setup

Usage:
    python scripts/run_app.py [options]

Options:
    --port PORT     Specify port number (default: 8501)
    --host HOST     Specify host address (default: localhost)
    --dev           Run in development mode with debug features
    --no-browser    Don't automatically open browser
    --config FILE   Specify custom configuration file
"""

import sys
import os
import subprocess
import platform
import argparse
import socket
import webbrowser
import time
import logging
from pathlib import Path
from typing import Optional


def setup_logging(debug=False):
    """Configure logging for the application launcher."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    return logging.getLogger(__name__)


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def find_virtual_environment():
    """Find and return the path to the virtual environment."""
    project_root = get_project_root()
    
    # Common virtual environment locations
    venv_candidates = [
        project_root / "venv",
        project_root / ".venv",
        project_root / "env",
        project_root / ".env"
    ]
    
    for venv_path in venv_candidates:
        if venv_path.exists():
            return venv_path
    
    return None


def get_venv_python(venv_path):
    """Get the Python executable in the virtual environment."""
    system = platform.system().lower()
    
    if system == "windows":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"
    
    if python_exe.exists():
        return python_exe
    
    return None


def check_port_available(host, port):
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0
    except Exception:
        return False


def find_available_port(host, start_port=8501, max_attempts=10):
    """Find an available port starting from start_port."""
    for i in range(max_attempts):
        port = start_port + i
        if check_port_available(host, port):
            return port
    
    raise RuntimeError(f"No available ports found starting from {start_port}")


def setup_environment_variables(dev_mode=False):
    """Setup environment variables for the application."""
    project_root = get_project_root()
    
    # Load .env file if it exists
    env_file = project_root / ".env"
    if env_file.exists():
        logger.info("Loading environment variables from .env file")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    # Set default environment variables
    env_defaults = {
        'ORC_DEBUG': 'true' if dev_mode else 'false',
        'ORC_LOG_LEVEL': 'DEBUG' if dev_mode else 'INFO',
        'ORC_ENABLE_CACHING': 'true',
        'ORC_CACHE_SIZE': '100',
        'ORC_DEFAULT_EXPORT_FORMAT': 'csv',
        'ORC_EXPORT_DIRECTORY': str(project_root / "data" / "outputs")
    }
    
    for key, value in env_defaults.items():
        if key not in os.environ:
            os.environ[key] = value


def verify_dependencies(python_cmd):
    """Verify that required dependencies are installed."""
    logger.info("Verifying dependencies...")
    
    test_script = """
import sys
missing_packages = []

required_packages = [
    'streamlit',
    'numpy',
    'pandas',
    'scipy',
    'matplotlib',
    'plotly',
    'openpyxl'
]

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print(f"Missing packages: {', '.join(missing_packages)}")
    sys.exit(1)
else:
    print("All dependencies verified!")
    sys.exit(0)
"""
    
    result = subprocess.run([str(python_cmd), "-c", test_script], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error("Dependency verification failed!")
        logger.error(result.stdout.strip())
        logger.error("Please run 'python scripts/setup.py' to install dependencies.")
        return False
    
    logger.info("All dependencies verified!")
    return True


def create_data_directories():
    """Create necessary data directories."""
    project_root = get_project_root()
    
    directories = [
        project_root / "data" / "outputs",
        project_root / "data" / "examples",
        project_root / "logs"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created directory: {directory}")


def launch_streamlit(python_cmd, host, port, app_path, no_browser=False, dev_mode=False):
    """Launch the Streamlit application."""
    logger.info(f"Starting Streamlit application on {host}:{port}")
    
    # Build Streamlit command
    cmd = [
        str(python_cmd), "-m", "streamlit", "run",
        str(app_path),
        "--server.port", str(port),
        "--server.address", host,
        "--server.headless", "true" if no_browser else "false",
        "--server.runOnSave", "true" if dev_mode else "false",
        "--server.allowRunOnSave", "true" if dev_mode else "false"
    ]
    
    if dev_mode:
        cmd.extend([
            "--server.fileWatcherType", "auto",
            "--logger.level", "debug"
        ])
    
    # Set environment for subprocess
    env = os.environ.copy()
    env['PYTHONPATH'] = str(get_project_root() / "src")
    
    try:
        # Start Streamlit process
        process = subprocess.Popen(cmd, env=env)
        
        # Wait a moment for Streamlit to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            url = f"http://{host}:{port}"
            logger.info(f"Application started successfully!")
            logger.info(f"URL: {url}")
            
            if not no_browser:
                logger.info("Opening browser...")
                webbrowser.open(url)
            
            # Wait for process to complete
            try:
                process.wait()
            except KeyboardInterrupt:
                logger.info("Shutting down application...")
                process.terminate()
                process.wait()
        else:
            logger.error("Failed to start Streamlit application")
            return False
    
    except Exception as e:
        logger.error(f"Error launching application: {e}")
        return False
    
    return True


def print_startup_info(host, port, dev_mode=False):
    """Print startup information."""
    print("\n" + "="*60)
    print("ORC - ROTARY CUTTER OPTIMIZATION SYSTEM")
    print("="*60)
    print(f"Mode: {'Development' if dev_mode else 'Production'}")
    print(f"URL: http://{host}:{port}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print("\nPress Ctrl+C to stop the application")
    print("="*60 + "\n")


def main():
    """Main application launcher function."""
    global logger
    
    parser = argparse.ArgumentParser(description="Launch ORC Streamlit application")
    parser.add_argument("--port", type=int, default=8501,
                       help="Port number (default: 8501)")
    parser.add_argument("--host", default="localhost",
                       help="Host address (default: localhost)")
    parser.add_argument("--dev", action="store_true",
                       help="Run in development mode")
    parser.add_argument("--no-browser", action="store_true",
                       help="Don't automatically open browser")
    parser.add_argument("--config", type=str,
                       help="Custom configuration file")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.dev)
    
    try:
        project_root = get_project_root()
        logger.info(f"Starting ORC application from: {project_root}")
        
        # Find virtual environment
        venv_path = find_virtual_environment()
        if venv_path is None:
            logger.error("Virtual environment not found!")
            logger.error("Please run 'python scripts/setup.py' first.")
            sys.exit(1)
        
        logger.info(f"Using virtual environment: {venv_path}")
        
        # Get Python executable
        python_cmd = get_venv_python(venv_path)
        if python_cmd is None:
            logger.error("Python executable not found in virtual environment!")
            sys.exit(1)
        
        # Setup environment variables
        setup_environment_variables(args.dev)
        
        # Verify dependencies
        if not verify_dependencies(python_cmd):
            sys.exit(1)
        
        # Create data directories
        create_data_directories()
        
        # Check port availability
        if not check_port_available(args.host, args.port):
            logger.warning(f"Port {args.port} is not available")
            new_port = find_available_port(args.host, args.port)
            logger.info(f"Using port {new_port} instead")
            args.port = new_port
        
        # Find Streamlit app
        app_path = project_root / "src" / "orc" / "ui" / "app.py"
        if not app_path.exists():
            # Fallback to old location
            app_path = project_root / "streamlit_app.py"
            if not app_path.exists():
                logger.error("Streamlit application file not found!")
                sys.exit(1)
        
        logger.info(f"Using app file: {app_path}")
        
        # Print startup info
        print_startup_info(args.host, args.port, args.dev)
        
        # Launch application
        success = launch_streamlit(
            python_cmd, args.host, args.port, app_path,
            args.no_browser, args.dev
        )
        
        if not success:
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
