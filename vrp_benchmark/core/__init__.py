"""
Core functionality for VRP benchmarking.

This module contains the main benchmark class and utility functions.
"""

from .benchmark import VRPBenchmark
from .utils import (
    create_sample_instance,
    create_clustered_instance,
    create_time_window_instance,
    calculate_solution_statistics,
    validate_solution_feasibility
)

__all__ = [
    'VRPBenchmark',
    'create_sample_instance',
    'create_clustered_instance',
    'create_time_window_instance',
    'calculate_solution_statistics',
    'validate_solution_feasibility'
]
