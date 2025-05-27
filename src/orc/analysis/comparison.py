"""
Configuration comparison tools for rotary cutter systems.

This module provides tools for comparing multiple configurations and
analyzing their relative performance characteristics.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

from ..core.simulation import SimulationResult
from .metrics import PerformanceAnalyzer, PerformanceMetrics

# Import RotaryCutterConfig only when needed to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..models.rotary_cutter import RotaryCutterConfig


@dataclass
class ComparisonResult:
    """Container for configuration comparison results."""

    configurations: List['RotaryCutterConfig']
    metrics: List[PerformanceMetrics]
    rankings: Dict[str, List[int]]
    summary: pd.DataFrame
    best_config: Dict[str, 'RotaryCutterConfig']
    analysis: Dict[str, Any]


class ConfigurationComparator:
    """
    Tool for comparing multiple rotary cutter configurations.

    This class provides methods to compare configurations across
    various performance metrics and identify optimal settings.
    """

    def __init__(self):
        """Initialize the configuration comparator."""
        self.analyzer = PerformanceAnalyzer()
        self.logger = logging.getLogger(__name__)

    def compare(self, results: List[Tuple['RotaryCutterConfig', SimulationResult]],
                metrics: Optional[List[str]] = None) -> ComparisonResult:
        """
        Compare multiple configurations and their simulation results.

        Args:
            results: List of (config, simulation_result) tuples
            metrics: List of metric names to compare. If None, uses default set.

        Returns:
            ComparisonResult with comprehensive comparison analysis
        """
        if not results:
            raise ValueError("No results provided for comparison")

        if metrics is None:
            metrics = [
                'efficiency', 'power_avg', 'omega_stability',
                'area_efficiency', 'cutting_rate'
            ]

        # Extract configurations and analyze results
        configs = [config for config, _ in results]
        sim_results = [result for _, result in results]

        # Calculate performance metrics for all results
        performance_metrics = []
        for result in sim_results:
            try:
                perf_metrics = self.analyzer.analyze(result)
                performance_metrics.append(perf_metrics)
            except Exception as e:
                self.logger.error(f"Failed to analyze result: {e}")
                # Create dummy metrics for failed analysis
                performance_metrics.append(self._create_dummy_metrics())

        # Create comparison summary
        summary_df = self._create_summary_dataframe(configs, performance_metrics, metrics)

        # Calculate rankings
        rankings = self._calculate_rankings(performance_metrics, metrics)

        # Identify best configurations
        best_configs = self._identify_best_configurations(configs, performance_metrics, metrics)

        # Perform additional analysis
        analysis = self._perform_additional_analysis(configs, performance_metrics)

        return ComparisonResult(
            configurations=configs,
            metrics=performance_metrics,
            rankings=rankings,
            summary=summary_df,
            best_config=best_configs,
            analysis=analysis
        )

    def _create_summary_dataframe(self, configs: List['RotaryCutterConfig'],
                                 metrics: List[PerformanceMetrics],
                                 metric_names: List[str]) -> pd.DataFrame:
        """Create a summary DataFrame for comparison."""
        data = []

        for i, (config, perf_metrics) in enumerate(zip(configs, metrics)):
            row = {
                'Configuration': config.name,
                'Mass (kg)': config.total_mass,
                'Radius (m)': config.radius,
                'Blades': config.n_blades,
                'Torque (Nm)': config.input_torque,
                'Advance_Speed (m/s)': config.advance_velocity
            }

            # Add performance metrics
            for metric_name in metric_names:
                if hasattr(perf_metrics, metric_name):
                    value = getattr(perf_metrics, metric_name)
                    row[metric_name.title()] = value
                else:
                    row[metric_name.title()] = 0.0

            data.append(row)

        return pd.DataFrame(data)

    def _calculate_rankings(self, metrics: List[PerformanceMetrics],
                           metric_names: List[str]) -> Dict[str, List[int]]:
        """Calculate rankings for each metric."""
        rankings = {}

        for metric_name in metric_names:
            values = []
            for perf_metrics in metrics:
                if hasattr(perf_metrics, metric_name):
                    values.append(getattr(perf_metrics, metric_name))
                else:
                    values.append(0.0)

            # Higher values are better for most metrics
            if metric_name in ['efficiency', 'omega_stability', 'torque_stability',
                              'power_stability', 'area_efficiency']:
                # Higher is better
                ranking_indices = np.argsort(values)[::-1]
            else:
                # Lower might be better (e.g., for some cost metrics)
                ranking_indices = np.argsort(values)[::-1]

            rankings[metric_name] = ranking_indices.tolist()

        return rankings

    def _identify_best_configurations(self, configs: List['RotaryCutterConfig'],
                                    metrics: List[PerformanceMetrics],
                                    metric_names: List[str]) -> Dict[str, 'RotaryCutterConfig']:
        """Identify best configurations for each metric."""
        best_configs = {}

        for metric_name in metric_names:
            values = []
            for perf_metrics in metrics:
                if hasattr(perf_metrics, metric_name):
                    values.append(getattr(perf_metrics, metric_name))
                else:
                    values.append(0.0)

            # Find best configuration for this metric
            if metric_name in ['efficiency', 'omega_stability', 'torque_stability',
                              'power_stability', 'area_efficiency']:
                best_idx = np.argmax(values)
            else:
                best_idx = np.argmax(values)  # Assume higher is better for now

            best_configs[metric_name] = configs[best_idx]

        return best_configs

    def _perform_additional_analysis(self, configs: List['RotaryCutterConfig'],
                                   metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Perform additional comparative analysis."""
        analysis = {}

        # Parameter correlation analysis
        analysis['correlations'] = self._analyze_parameter_correlations(configs, metrics)

        # Pareto frontier analysis
        analysis['pareto_frontier'] = self._analyze_pareto_frontier(configs, metrics)

        # Sensitivity analysis
        analysis['sensitivity'] = self._analyze_sensitivity(configs, metrics)

        # Trade-off analysis
        analysis['tradeoffs'] = self._analyze_tradeoffs(configs, metrics)

        return analysis

    def _analyze_parameter_correlations(self, configs: List['RotaryCutterConfig'],
                                      metrics: List[PerformanceMetrics]) -> Dict:
        """Analyze correlations between parameters and performance."""
        # Extract parameter values
        param_data = {
            'mass': [c.total_mass for c in configs],
            'radius': [c.radius for c in configs],
            'n_blades': [c.n_blades for c in configs],
            'torque': [c.input_torque for c in configs],
            'advance_velocity': [c.advance_velocity for c in configs]
        }

        # Extract performance metrics
        metric_data = {
            'efficiency': [m.efficiency for m in metrics],
            'power_avg': [m.power_avg for m in metrics],
            'omega_stability': [m.omega_stability for m in metrics]
        }

        # Calculate correlations (simplified)
        correlations = {}
        for param_name, param_values in param_data.items():
            correlations[param_name] = {}
            for metric_name, metric_values in metric_data.items():
                if len(set(param_values)) > 1:  # Avoid division by zero
                    corr = np.corrcoef(param_values, metric_values)[0, 1]
                    correlations[param_name][metric_name] = corr if not np.isnan(corr) else 0.0
                else:
                    correlations[param_name][metric_name] = 0.0

        return correlations

    def _analyze_pareto_frontier(self, configs: List['RotaryCutterConfig'],
                               metrics: List[PerformanceMetrics]) -> Dict:
        """Analyze Pareto frontier for multi-objective optimization."""
        # Simplified Pareto analysis for efficiency vs power
        efficiency_values = [m.efficiency for m in metrics]
        power_values = [m.power_avg for m in metrics]

        pareto_indices = []
        for i in range(len(configs)):
            is_pareto = True
            for j in range(len(configs)):
                if i != j:
                    # Check if j dominates i
                    if (efficiency_values[j] >= efficiency_values[i] and
                        power_values[j] <= power_values[i] and
                        (efficiency_values[j] > efficiency_values[i] or
                         power_values[j] < power_values[i])):
                        is_pareto = False
                        break
            if is_pareto:
                pareto_indices.append(i)

        return {
            'pareto_indices': pareto_indices,
            'pareto_configs': [configs[i].name for i in pareto_indices],
            'efficiency_values': efficiency_values,
            'power_values': power_values
        }

    def _analyze_sensitivity(self, configs: List['RotaryCutterConfig'],
                           metrics: List[PerformanceMetrics]) -> Dict:
        """Analyze sensitivity of performance to parameter changes."""
        # Simplified sensitivity analysis
        sensitivity = {}

        # Calculate coefficient of variation for each metric
        metric_names = ['efficiency', 'power_avg', 'omega_stability']
        for metric_name in metric_names:
            values = [getattr(m, metric_name) for m in metrics]
            mean_val = np.mean(values)
            std_val = np.std(values)
            cv = std_val / (mean_val + 1e-10)
            sensitivity[metric_name] = {
                'coefficient_of_variation': cv,
                'range': np.ptp(values),
                'mean': mean_val,
                'std': std_val
            }

        return sensitivity

    def _analyze_tradeoffs(self, configs: List['RotaryCutterConfig'],
                         metrics: List[PerformanceMetrics]) -> Dict:
        """Analyze trade-offs between different objectives."""
        tradeoffs = {}

        # Efficiency vs Power trade-off
        efficiency_values = [m.efficiency for m in metrics]
        power_values = [m.power_avg for m in metrics]

        if len(set(efficiency_values)) > 1 and len(set(power_values)) > 1:
            correlation = np.corrcoef(efficiency_values, power_values)[0, 1]
            tradeoffs['efficiency_vs_power'] = {
                'correlation': correlation if not np.isnan(correlation) else 0.0,
                'description': 'Negative correlation indicates trade-off'
            }

        # Stability vs Performance trade-off
        stability_values = [m.omega_stability for m in metrics]
        if len(set(stability_values)) > 1:
            correlation = np.corrcoef(efficiency_values, stability_values)[0, 1]
            tradeoffs['efficiency_vs_stability'] = {
                'correlation': correlation if not np.isnan(correlation) else 0.0,
                'description': 'Relationship between efficiency and stability'
            }

        return tradeoffs

    def _create_dummy_metrics(self) -> PerformanceMetrics:
        """Create dummy metrics for failed analysis."""
        from .metrics import PerformanceMetrics

        return PerformanceMetrics(
            efficiency=0.0,
            cutting_efficiency=0.0,
            energy_total=0.0,
            energy_useful=0.0,
            energy_losses=0.0,
            power_avg=0.0,
            power_max=0.0,
            power_min=0.0,
            power_rms=0.0,
            omega_stability=0.0,
            torque_stability=0.0,
            power_stability=0.0,
            area_cut=0.0,
            cutting_rate=0.0,
            area_efficiency=0.0,
            settling_time=0.0,
            overshoot=0.0,
            steady_state_error=0.0,
            dominant_frequency=0.0,
            frequency_content={},
            statistics={}
        )


def compare_configurations(configs: List['RotaryCutterConfig'],
                         results: List[SimulationResult],
                         metrics: Optional[List[str]] = None) -> ComparisonResult:
    """
    Convenience function to compare configurations.

    Args:
        configs: List of configurations to compare
        results: List of corresponding simulation results
        metrics: List of metric names to compare

    Returns:
        ComparisonResult with comparison analysis
    """
    if len(configs) != len(results):
        raise ValueError("Number of configurations must match number of results")

    comparator = ConfigurationComparator()
    config_result_pairs = list(zip(configs, results))

    return comparator.compare(config_result_pairs, metrics)
