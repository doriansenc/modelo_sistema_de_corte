"""
Settings management for the ORC system.

This module provides application settings management including
UI settings, performance settings, and user preferences.
"""

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
import logging


@dataclass
class Settings:
    """Application settings for the ORC system."""

    # UI settings
    theme: str = "professional"
    layout: str = "wide"
    sidebar_state: str = "expanded"

    # Performance settings
    enable_caching: bool = True
    cache_size: int = 100
    parallel_processing: bool = False

    # Export settings
    default_export_format: str = "csv"
    export_directory: str = "./data/outputs"

    # Logging settings
    log_level: str = "INFO"
    enable_file_logging: bool = False

    # Development settings
    debug_mode: bool = False
    profiling_enabled: bool = False


def load_settings(filepath: Optional[Union[str, Path]] = None) -> Settings:
    """
    Load settings from file or return defaults.

    Args:
        filepath: Path to settings file. If None, uses defaults.

    Returns:
        Settings object
    """
    if filepath is None:
        return Settings()

    filepath = Path(filepath)
    logger = logging.getLogger(__name__)

    if not filepath.exists():
        logger.info(f"Settings file not found: {filepath}, using defaults")
        return Settings()

    try:
        with open(filepath, 'r') as f:
            if filepath.suffix.lower() in ['.yaml', '.yml']:
                if YAML_AVAILABLE:
                    data = yaml.safe_load(f)
                else:
                    logger.error("YAML support not available. Install PyYAML to load YAML files.")
                    return Settings()
            elif filepath.suffix.lower() == '.json':
                data = json.load(f)
            else:
                logger.error(f"Unsupported settings file format: {filepath.suffix}")
                return Settings()

        # Create settings object with loaded data
        settings = Settings()
        for key, value in data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
            else:
                logger.warning(f"Unknown setting: {key}")

        logger.info(f"Loaded settings from {filepath}")
        return settings

    except Exception as e:
        logger.error(f"Error loading settings from {filepath}: {e}")
        return Settings()


def save_settings(settings: Settings, filepath: Union[str, Path]) -> bool:
    """
    Save settings to file.

    Args:
        settings: Settings object to save
        filepath: Output file path

    Returns:
        True if successful, False otherwise
    """
    filepath = Path(filepath)
    logger = logging.getLogger(__name__)

    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = asdict(settings)

        with open(filepath, 'w') as f:
            if filepath.suffix.lower() in ['.yaml', '.yml']:
                if YAML_AVAILABLE:
                    yaml.dump(data, f, default_flow_style=False, indent=2)
                else:
                    logger.error("YAML support not available. Install PyYAML to save YAML files.")
                    return False
            elif filepath.suffix.lower() == '.json':
                json.dump(data, f, indent=2)
            else:
                logger.error(f"Unsupported settings file format: {filepath.suffix}")
                return False

        logger.info(f"Saved settings to {filepath}")
        return True

    except Exception as e:
        logger.error(f"Error saving settings to {filepath}: {e}")
        return False
