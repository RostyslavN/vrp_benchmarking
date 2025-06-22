"""
Base classes for VRP solvers.
Here are common interface that all VRP solvers must implement to keep consistency.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

from ..models import VRPInstance, VRPSolution


class VRPSolver(ABC):
    def __init__(self, **kwargs):
        """
        Args:
            **kwargs: solver-specific config parameters
        """
        self.config = kwargs
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def solve(self, instance: VRPInstance, time_limit: int = 30, **kwargs) -> VRPSolution:
        """
        Solves VRP instance.
        Args:
            instance: VRP problem instance to solve
            time_limit
            **kwargs: solver-specific parameters
        """
        pass

    @abstractmethod
    def get_solver_name(self) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        If the solver is available and properly installed
        """
        pass

    def get_solver_info(self) -> Dict[str, Any]:
        """
        Returns:
            Dictionary containing solver metadata
        """
        return {
            'name': self.get_solver_name(),
            'available': self.is_available(),
            'config': self.config,
            'class': self.__class__.__name__
        }

    def validate_instance(self, instance: VRPInstance) -> bool:
        """
        To validate that instance can be solved by this solver.

        Base implementation runs common validation.
        Solvers can override this for their edge-cases.
        """
        try:
            # Basic validation
            if not instance.locations:
                self.logger.error("Instance has no locations")
                return False

            if not instance.vehicles:
                self.logger.error("Instance has no vehicles")
                return False

            if len(instance.distance_matrix) != len(instance.locations):
                self.logger.error(
                    "Distance matrix size doesn't match locations")
                return False

            # Check for depot (location with ID 0)
            depot_found = any(loc.id == 0 for loc in instance.locations)
            if not depot_found:
                self.logger.error("No depot found (location with ID 0)")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Instance validation failed: {e}")
            return False

    def create_error_solution(self, instance: VRPInstance, error_msg: str,
                              solve_time: float = 0.0) -> VRPSolution:
        """
        Args:
            instance: instance that failed to solve
            error_msg
            solve_time: time spent before error occurred

        Returns:
            VRPSolution with error status
        """
        self.logger.error(f"Creating error solution: {error_msg}")

        return VRPSolution(
            solver_name=self.get_solver_name(),
            instance_name=instance.name,
            routes=[],
            total_distance=float('inf'),
            total_time=0.0,
            solve_time=solve_time,
            status="ERROR",
            objective_value=float('inf')
        )

    def preprocess_instance(self, instance: VRPInstance) -> VRPInstance:
        """
        (optional) Map the instance before solving. Up to solvers edge-cases.

        Args:
            instance: original VRP instance

        Returns:
            preprocessed VRP instance
        """
        return instance

    def postprocess_solution(self, solution: VRPSolution,
                             instance: VRPInstance) -> VRPSolution:
        """
        (optional) Postprocess the solution after solving.

        Args:
            solution: raw solution from solver
            instance: original VRP instance

        Returns:
            postprocessed VRP solution
        """
        return solution

    def get_supported_problem_types(self) -> list[str]:
        """
        To get list of VRP problem types supported by this solver.

        Base implementation returns common types.
        Solvers should override this to specify their types.
        """
        return ["CVRP"]  # Most basic type

    def supports_problem_type(self, problem_type: str) -> bool:
        """
        To check if solver supports a specific problem type.

        Args:
            problem_type: string (e.g., "CVRP", "VRPTW")
        """
        return problem_type.upper() in [pt.upper() for pt in self.get_supported_problem_types()]


class ExactSolver(VRPSolver):
    """
    Abstract base class for exact VRP solvers.

    Exact solvers guarantee optimal solutions, but may take longer and have limited scalability.
    """

    def get_solver_category(self) -> str:
        return "exact"

    def get_solver_info(self) -> Dict[str, Any]:
        info = super().get_solver_info()
        info['category'] = self.get_solver_category()
        info['guarantees_optimal'] = True
        return info


class HeuristicSolver(VRPSolver):
    """
    Abstract base class for heuristic VRP solvers.

    Heuristic solvers provide good solutions quickly, but don't guarantee optimality.
    """

    def get_solver_category(self) -> str:
        return "heuristic"

    def get_solver_info(self) -> Dict[str, Any]:
        info = super().get_solver_info()
        info['category'] = self.get_solver_category()
        info['guarantees_optimal'] = False
        return info


class MetaheuristicSolver(VRPSolver):
    """
    Abstract base class for metaheuristic VRP solvers.

    Metaheuristic solvers use advanced search strategies to explore the solution space effectively.
    """

    def get_solver_category(self) -> str:
        return "metaheuristic"

    def get_solver_info(self) -> Dict[str, Any]:
        info = super().get_solver_info()
        info['category'] = self.get_solver_category()
        info['guarantees_optimal'] = False
        info['uses_randomization'] = True
        return info


class SolverRegistry:
    """
    Registry for managing available VRP solvers.
    this class maintains a list of all available solvers and provides methods for solver discovery and selection.
    """

    def __init__(self):
        self._solvers: Dict[str, VRPSolver] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def register_solver(self, solver: VRPSolver, force: bool = False) -> bool:
        """
        Args:
            solver: VRP solver instance to register
            force: Whether to override existing solver with same name

        Returns:
            True if registration successful, False otherwise
        """
        solver_name = solver.get_solver_name()

        if solver_name in self._solvers and not force:
            self.logger.warning(f"Solver '{solver_name}' already registered")
            return False

        if not solver.is_available():
            self.logger.warning(f"Solver '{solver_name}' is not available")
            return False

        self._solvers[solver_name] = solver
        self.logger.info(f"Registered solver: {solver_name}")
        return True

    def get_solver(self, solver_name: str) -> Optional[VRPSolver]:
        """
        Get a solver by name.

        Args:
            solver_name: Name of the solver to retrieve

        Returns:
            VRP solver instance or None if not found
        """
        return self._solvers.get(solver_name)

    def get_available_solvers(self) -> Dict[str, VRPSolver]:
        """
        Returns:
            Dictionary mapping solver names to solver instances
        """
        return {name: solver for name, solver in self._solvers.items()
                if solver.is_available()}

    def get_solver_names(self) -> list[str]:
        """
        Returns:
            List of solver name strings
        """
        return list(self._solvers.keys())

    def get_solvers_by_category(self, category: str) -> Dict[str, VRPSolver]:
        """
        Get solvers by category (exact, heuristic, metaheuristic).

        Args:
            category: Solver category to filter by

        Returns:
            Dictionary of solvers in the specified category
        """
        result = {}
        for name, solver in self._solvers.items():
            if hasattr(solver, 'get_solver_category'):
                if solver.get_solver_category() == category.lower():
                    result[name] = solver
        return result

    def get_solvers_for_problem_type(self, problem_type: str) -> Dict[str, VRPSolver]:
        """
        To get solvers that support a specific problem type.

        Args:
            problem_type: e.g., "CVRP", "VRPTW"

        Returns:
            Dictionary of compatible solvers
        """
        result = {}
        for name, solver in self._solvers.items():
            if solver.supports_problem_type(problem_type):
                result[name] = solver
        return result

    def clear(self):
        """Clear all registered solvers"""
        self._solvers.clear()
        self.logger.info("Cleared all registered solvers")


# Global solver registry instance
solver_registry = SolverRegistry()
