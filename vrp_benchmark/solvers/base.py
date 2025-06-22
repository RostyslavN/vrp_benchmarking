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
