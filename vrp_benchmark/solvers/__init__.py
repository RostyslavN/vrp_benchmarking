"""
VRP Solver implementations.

This module contains all solver implementations and the base classes that define the common solver interface.
"""

from .base import VRPSolver, ExactSolver, HeuristicSolver, MetaheuristicSolver, solver_registry

# Import available solvers
__all__ = ['VRPSolver', 'ExactSolver', 'HeuristicSolver',
           'MetaheuristicSolver', 'solver_registry']

try:
    from .pyvrp_solver import PyVRPSolver
    __all__.append('PyVRPSolver')
except ImportError:
    pass

try:
    from .ortools_solver import ORToolsSolver
    __all__.append('ORToolsSolver')
except ImportError:
    pass
