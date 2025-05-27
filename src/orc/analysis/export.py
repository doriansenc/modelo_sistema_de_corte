"""
Data export functionality for rotary cutter analysis results.

This module provides tools for exporting simulation results and analysis
data in various formats including CSV, Excel, JSON, and custom formats.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import logging
from datetime import datetime

from ..core.simulation import SimulationResult
from .metrics import PerformanceMetrics
from .comparison import ComparisonResult

# Import RotaryCutterConfig only when needed to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..models.rotary_cutter import RotaryCutterConfig


class ExportFormat(Enum):
    """Available export formats."""
    CSV = "csv"
    EXCEL = "xlsx"
    JSON = "json"
    PARQUET = "parquet"


class DataExporter:
    """
    Comprehensive data exporter for simulation results and analysis.

    This class provides methods to export various types of data in
    multiple formats with customizable options.
    """

    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the data exporter.

        Args:
            output_dir: Directory for output files. If None, uses current directory.
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def export_simulation_result(self, result: SimulationResult,
                                config: 'RotaryCutterConfig',
                                filename: Optional[str] = None,
                                format: ExportFormat = ExportFormat.CSV,
                                include_metadata: bool = True) -> Path:
        """
        Export a single simulation result.

        Args:
            result: SimulationResult to export
            config: Configuration used for the simulation
            filename: Output filename. If None, auto-generated.
            format: Export format
            include_metadata: Whether to include metadata

        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simulation_result_{config.name}_{timestamp}.{format.value}"

        filepath = self.output_dir / filename

        # Create main data DataFrame
        data_df = pd.DataFrame({
            'time': result.time,
            'angle': result.angle,
            'angular_velocity': result.angular_velocity,
            'torque': result.torque,
            'power': result.power,
            'kinetic_energy': result.kinetic_energy
        })

        if format == ExportFormat.CSV:
            self._export_csv_simulation(data_df, result, config, filepath, include_metadata)
        elif format == ExportFormat.EXCEL:
            self._export_excel_simulation(data_df, result, config, filepath, include_metadata)
        elif format == ExportFormat.JSON:
            self._export_json_simulation(data_df, result, config, filepath, include_metadata)
        elif format == ExportFormat.PARQUET:
            self._export_parquet_simulation(data_df, result, config, filepath, include_metadata)

        self.logger.info(f"Exported simulation result to {filepath}")
        return filepath

    def export_performance_metrics(self, metrics: PerformanceMetrics,
                                  config: 'RotaryCutterConfig',
                                  filename: Optional[str] = None,
                                  format: ExportFormat = ExportFormat.JSON) -> Path:
        """
        Export performance metrics.

        Args:
            metrics: PerformanceMetrics to export
            config: Associated configuration
            filename: Output filename
            format: Export format

        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_metrics_{config.name}_{timestamp}.{format.value}"

        filepath = self.output_dir / filename

        # Convert metrics to dictionary
        metrics_dict = {
            'configuration_name': config.name,
            'export_timestamp': datetime.now().isoformat(),
            'energy_metrics': {
                'efficiency': metrics.efficiency,
                'cutting_efficiency': metrics.cutting_efficiency,
                'energy_total': metrics.energy_total,
                'energy_useful': metrics.energy_useful,
                'energy_losses': metrics.energy_losses
            },
            'power_metrics': {
                'power_avg': metrics.power_avg,
                'power_max': metrics.power_max,
                'power_min': metrics.power_min,
                'power_rms': metrics.power_rms
            },
            'stability_metrics': {
                'omega_stability': metrics.omega_stability,
                'torque_stability': metrics.torque_stability,
                'power_stability': metrics.power_stability
            },
            'cutting_metrics': {
                'area_cut': metrics.area_cut,
                'cutting_rate': metrics.cutting_rate,
                'area_efficiency': metrics.area_efficiency
            },
            'dynamic_metrics': {
                'settling_time': metrics.settling_time,
                'overshoot': metrics.overshoot,
                'steady_state_error': metrics.steady_state_error
            },
            'frequency_metrics': {
                'dominant_frequency': metrics.dominant_frequency,
                'frequency_content': metrics.frequency_content
            },
            'statistics': metrics.statistics
        }

        if format == ExportFormat.JSON:
            with open(filepath, 'w') as f:
                json.dump(metrics_dict, f, indent=2, default=self._json_serializer)
        elif format == ExportFormat.CSV:
            # Flatten metrics for CSV export
            flat_metrics = self._flatten_dict(metrics_dict)
            df = pd.DataFrame([flat_metrics])
            df.to_csv(filepath, index=False)
        elif format == ExportFormat.EXCEL:
            # Create multi-sheet Excel file
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for category, data in metrics_dict.items():
                    if isinstance(data, dict) and category.endswith('_metrics'):
                        df = pd.DataFrame([data])
                        df.to_excel(writer, sheet_name=category.replace('_metrics', ''), index=False)

        self.logger.info(f"Exported performance metrics to {filepath}")
        return filepath

    def export_comparison_result(self, comparison: ComparisonResult,
                                filename: Optional[str] = None,
                                format: ExportFormat = ExportFormat.EXCEL) -> Path:
        """
        Export comparison results.

        Args:
            comparison: ComparisonResult to export
            filename: Output filename
            format: Export format

        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comparison_result_{timestamp}.{format.value}"

        filepath = self.output_dir / filename

        if format == ExportFormat.EXCEL:
            self._export_excel_comparison(comparison, filepath)
        elif format == ExportFormat.CSV:
            comparison.summary.to_csv(filepath, index=False)
        elif format == ExportFormat.JSON:
            comparison_dict = {
                'summary': comparison.summary.to_dict('records'),
                'rankings': comparison.rankings,
                'best_configs': {k: v.name for k, v in comparison.best_config.items()},
                'analysis': comparison.analysis,
                'export_timestamp': datetime.now().isoformat()
            }
            with open(filepath, 'w') as f:
                json.dump(comparison_dict, f, indent=2, default=self._json_serializer)

        self.logger.info(f"Exported comparison result to {filepath}")
        return filepath

    def _export_csv_simulation(self, data_df: pd.DataFrame, result: SimulationResult,
                              config: 'RotaryCutterConfig', filepath: Path,
                              include_metadata: bool):
        """Export simulation to CSV format."""
        if include_metadata:
            # Write metadata as comments
            with open(filepath, 'w') as f:
                f.write(f"# ORC Simulation Result Export\n")
                f.write(f"# Configuration: {config.name}\n")
                f.write(f"# Export Date: {datetime.now().isoformat()}\n")
                f.write(f"# Success: {result.success}\n")
                f.write(f"# Execution Time: {result.execution_time:.3f}s\n")
                f.write(f"# Parameters: {result.parameters}\n")
                f.write("#\n")

            # Append data
            data_df.to_csv(filepath, mode='a', index=False)
        else:
            data_df.to_csv(filepath, index=False)

    def _export_excel_simulation(self, data_df: pd.DataFrame, result: SimulationResult,
                                config: 'RotaryCutterConfig', filepath: Path,
                                include_metadata: bool):
        """Export simulation to Excel format."""
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Main data
            data_df.to_excel(writer, sheet_name='Time_Series', index=False)

            if include_metadata:
                # Metadata sheet
                metadata = {
                    'Property': ['Configuration Name', 'Export Date', 'Success',
                               'Execution Time (s)', 'Number of Points', 'Message'],
                    'Value': [config.name, datetime.now().isoformat(), result.success,
                             result.execution_time, len(result.time), result.message]
                }
                metadata_df = pd.DataFrame(metadata)
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)

                # Parameters sheet
                params_df = pd.DataFrame([result.parameters])
                params_df.to_excel(writer, sheet_name='Parameters', index=False)

                # Statistics sheet
                if hasattr(result, 'statistics') and result.statistics:
                    stats_df = pd.DataFrame([result.statistics])
                    stats_df.to_excel(writer, sheet_name='Statistics', index=False)

    def _export_json_simulation(self, data_df: pd.DataFrame, result: SimulationResult,
                               config: 'RotaryCutterConfig', filepath: Path,
                               include_metadata: bool):
        """Export simulation to JSON format."""
        export_data = {
            'time_series': data_df.to_dict('records'),
            'success': result.success,
            'message': result.message,
            'execution_time': result.execution_time
        }

        if include_metadata:
            export_data.update({
                'configuration': {
                    'name': config.name,
                    'description': config.description,
                    'parameters': result.parameters
                },
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'n_points': len(result.time),
                    'n_evaluations': result.n_evaluations
                },
                'statistics': result.statistics if hasattr(result, 'statistics') else {}
            })

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=self._json_serializer)

    def _export_parquet_simulation(self, data_df: pd.DataFrame, result: SimulationResult,
                                  config: 'RotaryCutterConfig', filepath: Path,
                                  include_metadata: bool):
        """Export simulation to Parquet format."""
        if include_metadata:
            # Add metadata as DataFrame attributes (if supported)
            data_df.attrs['configuration_name'] = config.name
            data_df.attrs['export_date'] = datetime.now().isoformat()
            data_df.attrs['success'] = result.success
            data_df.attrs['execution_time'] = result.execution_time

        data_df.to_parquet(filepath, index=False)

    def _export_excel_comparison(self, comparison: ComparisonResult, filepath: Path):
        """Export comparison to Excel format with multiple sheets."""
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Summary sheet
            comparison.summary.to_excel(writer, sheet_name='Summary', index=False)

            # Rankings sheet
            rankings_data = []
            for metric, ranking in comparison.rankings.items():
                for rank, config_idx in enumerate(ranking):
                    rankings_data.append({
                        'Metric': metric,
                        'Rank': rank + 1,
                        'Configuration': comparison.configurations[config_idx].name,
                        'Configuration_Index': config_idx
                    })

            if rankings_data:
                rankings_df = pd.DataFrame(rankings_data)
                rankings_df.to_excel(writer, sheet_name='Rankings', index=False)

            # Best configurations sheet
            best_configs_data = []
            for metric, config in comparison.best_config.items():
                best_configs_data.append({
                    'Metric': metric,
                    'Best_Configuration': config.name,
                    'Description': config.description
                })

            if best_configs_data:
                best_df = pd.DataFrame(best_configs_data)
                best_df.to_excel(writer, sheet_name='Best_Configs', index=False)

            # Analysis sheet (simplified)
            if comparison.analysis:
                analysis_data = self._flatten_dict(comparison.analysis)
                if analysis_data:
                    analysis_df = pd.DataFrame([analysis_data])
                    analysis_df.to_excel(writer, sheet_name='Analysis', index=False)

    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten a nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _json_serializer(self, obj):
        """JSON serializer for numpy types."""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def export_simulation_results(results: List[SimulationResult],
                             configs: List['RotaryCutterConfig'],
                             output_dir: Optional[Union[str, Path]] = None,
                             format: ExportFormat = ExportFormat.EXCEL) -> List[Path]:
    """
    Convenience function to export multiple simulation results.

    Args:
        results: List of simulation results
        configs: List of corresponding configurations
        output_dir: Output directory
        format: Export format

    Returns:
        List of paths to exported files
    """
    exporter = DataExporter(output_dir)
    exported_files = []

    for result, config in zip(results, configs):
        filepath = exporter.export_simulation_result(result, config, format=format)
        exported_files.append(filepath)

    return exported_files


def export_comparison_results(comparison: ComparisonResult,
                            output_dir: Optional[Union[str, Path]] = None,
                            format: ExportFormat = ExportFormat.EXCEL) -> Path:
    """
    Convenience function to export comparison results.

    Args:
        comparison: Comparison result to export
        output_dir: Output directory
        format: Export format

    Returns:
        Path to exported file
    """
    exporter = DataExporter(output_dir)
    return exporter.export_comparison_result(comparison, format=format)
