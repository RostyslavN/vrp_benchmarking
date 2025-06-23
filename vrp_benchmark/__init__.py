"""
VRP Benchmarking API - unified interface for Vehicle Routing Problem solvers.

This package provides a comprehensive benchmarking platform for comparing
different VRP algorithms (including PyVRP, Google OR-Tools and more in the future.)

Example usage:
    >>> from vrp_benchmark import VRPBenchmark
    >>> benchmark = VRPBenchmark()
    >>> instance = benchmark.create_sample_instance("test", num_customers=10)
    >>> solutions = benchmark.benchmark("test", time_limit=30)
    >>> comparison = benchmark.compare_solutions(solutions)
"""

from .models import (
    VRPInstance, VRPSolution, Location, Vehicle, Route, SolverType,
    calculate_euclidean_distance, create_distance_matrix
)
from .core.benchmark import VRPBenchmark
from .core.utils import (
    create_sample_instance, create_clustered_instance, create_time_window_instance,
    calculate_solution_statistics, validate_solution_feasibility
)
from .solvers.base import VRPSolver, ExactSolver, HeuristicSolver, MetaheuristicSolver

# Import available solvers
try:
    from .solvers.pyvrp_solver import PyVRPSolver
except ImportError:
    PyVRPSolver = None

try:
    from .solvers.ortools_solver import ORToolsSolver
except ImportError:
    ORToolsSolver = None

__version__ = "0.1.0"
__author__ = "Rostyslav Novak"
__email__ = "novak.rostyslav@gmail.com"

# Public API
__all__ = [
    # Main classes
    'VRPBenchmark',
    'VRPInstance',
    'VRPSolution',
    'Location',
    'Vehicle',
    'Route',
    'SolverType',

    # Solver classes
    'VRPSolver',
    'ExactSolver',
    'HeuristicSolver',
    'MetaheuristicSolver',
    'PyVRPSolver',
    'ORToolsSolver',

    # Utility functions
    'create_sample_instance',
    'create_clustered_instance',
    'create_time_window_instance',
    'calculate_solution_statistics',
    'validate_solution_feasibility',
    'calculate_euclidean_distance',
    'create_distance_matrix',
]
