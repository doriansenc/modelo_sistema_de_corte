"""
Analysis and performance metrics tools for rotary cutter systems.

This module provides comprehensive analysis capabilities including:
- Performance metrics calculation
- Efficiency analysis
- Comparative analysis between configurations
- Data export functionality
- Statistical analysis

Modules:
    metrics: Performance metrics calculation and analysis
    comparison: Configuration comparison tools
    export: Data export functionality
    statistics: Statistical analysis tools
"""

from .metrics import (
    PerformanceAnalyzer,
    PerformanceMetrics,
    calculate_efficiency,
    calculate_stability_metrics
)

from .comparison import (
    ConfigurationComparator,
    ComparisonResult,
    compare_configurations
)

from .export import (
    DataExporter,
    ExportFormat,
    export_simulation_results,
    export_comparison_results
)

__all__ = [
    # Metrics
    'PerformanceAnalyzer',
    'PerformanceMetrics',
    'calculate_efficiency',
    'calculate_stability_metrics',
    
    # Comparison
    'ConfigurationComparator',
    'ComparisonResult',
    'compare_configurations',
    
    # Export
    'DataExporter',
    'ExportFormat',
    'export_simulation_results',
    'export_comparison_results'
]
