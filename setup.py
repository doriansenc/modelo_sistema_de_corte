"""
Setup script for the ORC Rotary Cutter Optimization System.

This script configures the package for installation using pip.
It defines package metadata, dependencies, and entry points.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "ORC - Rotary Cutter Optimization System"

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "streamlit>=1.28.0",
        "pandas>=2.0.0",
        "plotly>=5.17.0",
        "openpyxl>=3.1.0",
        "scipy>=1.11.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0"
    ]

# Development requirements
dev_requirements = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
    "jupyter>=1.0.0",
    "ipykernel>=6.0.0"
]

setup(
    name="orc",
    version="2.0.0",
    author="ORC Development Team",
    author_email="orc-dev@example.com",
    description="Advanced simulation and optimization system for rotary cutters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/orc-team/orc",
    project_urls={
        "Bug Tracker": "https://github.com/orc-team/orc/issues",
        "Documentation": "https://github.com/orc-team/orc/docs",
        "Source Code": "https://github.com/orc-team/orc",
    },
    
    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Include additional files
    include_package_data=True,
    package_data={
        "orc": [
            "ui/styles/*.css",
            "config/*.yaml",
            "data/examples/*.csv",
            "data/examples/*.xlsx"
        ]
    },
    
    # Dependencies
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0"
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0"
        ]
    },
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Entry points for command-line scripts
    entry_points={
        "console_scripts": [
            "orc-app=orc.ui.app:main",
            "orc-simulate=orc.cli.simulate:main",
            "orc-analyze=orc.cli.analyze:main",
        ]
    },
    
    # Classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    
    # Keywords for package discovery
    keywords=[
        "rotary cutter",
        "optimization",
        "simulation",
        "physics modeling",
        "differential equations",
        "agricultural machinery",
        "engineering",
        "streamlit"
    ],
    
    # Zip safety
    zip_safe=False,
)
