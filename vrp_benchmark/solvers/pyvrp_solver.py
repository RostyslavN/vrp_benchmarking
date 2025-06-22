"""
PyVRP solver implementation.
"""

import time
from typing import List, Optional

from .base import MetaheuristicSolver
from ..models import VRPInstance, VRPSolution, Route

# Try to import PyVRP
try:
    import vrp
    PYVRP_AVAILABLE = True
except ImportError:
    PYVRP_AVAILABLE = False
    vrp = None


class PyVRPSolver(MetaheuristicSolver):
    """
    PyVRP solver implementation using Hybrid Genetic Search.
    """

    def __init__(self, **kwargs):
        """        
        Args:
            **kwargs: Configuration parameters for PyVRP
                - max_iterations: max number of iterations
                - population_size: size of genetic algorithm population
                - min_population_size: min population size
                - nb_close: number of closest neighbors to consider
                - nb_granular: granular search neighborhood size
        """
        super().__init__(**kwargs)

        # Default PyVRP parameters
        self.default_config = {
            'max_iterations': 25000,
            'population_size': 25,
            'min_population_size': 4,
            'nb_close': 5,
            'nb_granular': 20
        }

        # Merge with user config
        self.config = {**self.default_config, **self.config}

        if not PYVRP_AVAILABLE:
            self.logger.warning(
                "PyVRP not available. Install with: pip install vrp")

    def is_available(self) -> bool:
        return PYVRP_AVAILABLE

    def get_solver_name(self) -> str:
        return "PyVRP"

    def get_supported_problem_types(self) -> List[str]:
        return ["CVRP", "VRPTW", "VRP"]

    def solve(self, instance: VRPInstance, time_limit: int = 30, **kwargs) -> VRPSolution:
        """
        Args:
            instance: VRP problem instance to solve
            time_limit: Maximum solving time in seconds
            **kwargs: Additional PyVRP-specific parameters

        Returns:
            VRPSolution containing the best solution found
        """
        if not self.is_available():
            return self.create_error_solution(
                instance, "PyVRP is not available", 0.0
            )

        if not self.validate_instance(instance):
            return self.create_error_solution(
                instance, "Instance validation failed", 0.0
            )

        start_time = time.time()

        try:
            # Merge runtime config with kwargs
            runtime_config = {**self.config, **kwargs}

            # Convert VRPInstance to PyVRP format
            pyvrp_locations = self._convert_locations(instance)
            pyvrp_vehicles = self._convert_vehicles(instance)

            # Create PyVRP problem
            problem = vrp.Problem(
                locations=pyvrp_locations,
                vehicle_types=pyvrp_vehicles
            )

            # Set solving parameters
            problem.solve(
                max_runtime=time_limit,
                max_iterations=runtime_config.get('max_iterations', 25000),
                population_size=runtime_config.get('population_size', 25),
                min_population_size=runtime_config.get(
                    'min_population_size', 4),
                nb_close=runtime_config.get('nb_close', 5),
                nb_granular=runtime_config.get('nb_granular', 20)
            )

            solve_time = time.time() - start_time

            # Get best solution
            best_solution = problem.best_solution()
            if best_solution is None:
                return self.create_error_solution(
                    instance, "PyVRP found no solution", solve_time
                )

            # Convert PyVRP solution back to our format
            vrp_solution = self._convert_solution(
                best_solution, instance, solve_time
            )

            return vrp_solution

        except Exception as e:
            solve_time = time.time() - start_time
            error_msg = f"PyVRP solver error: {str(e)}"
            self.logger.error(error_msg)
            return self.create_error_solution(instance, error_msg, solve_time)

    def _convert_locations(self, instance: VRPInstance) -> List:
        """
        Convert VRPInstance locations to PyVRP format.

        Args:
            instance: VRP instance with locations

        Returns:
            List of PyVRP Location objects
        """
        pyvrp_locations = []

        for loc in instance.locations:
            # PyVRP uses different parameter names
            pyvrp_loc = vrp.Location(
                x=loc.x,
                y=loc.y,
                delivery=loc.demand,  # PyVRP uses 'delivery' for demand
                service_duration=loc.service_time,
                tw_early=loc.time_window_start,
                tw_late=loc.time_window_end
            )
            pyvrp_locations.append(pyvrp_loc)

        return pyvrp_locations

    def _convert_vehicles(self, instance: VRPInstance) -> List:
        """
        Convert VRPInstance vehicles to PyVRP format.

        Args:
            instance: VRP instance with vehicles

        Returns:
            List of PyVRP VehicleType objects
        """
        pyvrp_vehicles = []

        for vehicle in instance.vehicles:
            pyvrp_vehicle = vrp.VehicleType(
                capacity=vehicle.capacity,
                max_duration=vehicle.max_time,
                depot=vehicle.depot_id
            )
            pyvrp_vehicles.append(pyvrp_vehicle)

        return pyvrp_vehicles

    def _convert_solution(self, pyvrp_solution, instance: VRPInstance,
                          solve_time: float) -> VRPSolution:
        """
        Convert PyVRP solution to VRPSolution format.

        Args:
            pyvrp_solution: Solution object from PyVRP
            instance: Original VRP instance
            solve_time: Time taken to solve

        Returns:
            VRPSolution object
        """
        routes = []
        total_distance = 0.0

        # Extract routes from PyVRP solution
        for route_idx, route in enumerate(pyvrp_solution.routes()):
            route_locations = [0]  # Start at depot
            route_distance = 0.0
            route_demand = 0
            route_time = 0.0

            # Add customer visits
            for visit in route:
                customer_id = visit.client()
                route_locations.append(customer_id)
                route_demand += instance.locations[customer_id].demand
                route_time += instance.locations[customer_id].service_time

            route_locations.append(0)  # Return to depot

            # Calculate route distance using instance distance matrix
            for i in range(len(route_locations) - 1):
                from_loc = route_locations[i]
                to_loc = route_locations[i + 1]
                route_distance += instance.distance_matrix[from_loc][to_loc]

            # Only include non-empty routes
            if len(route_locations) > 2:
                routes.append(Route(
                    vehicle_id=route_idx,
                    locations=route_locations,
                    total_distance=route_distance,
                    total_demand=route_demand,
                    total_time=route_time
                ))
                total_distance += route_distance

        # Determine solution status
        status = "OPTIMAL" if pyvrp_solution.is_complete() else "FEASIBLE"

        return VRPSolution(
            solver_name=self.get_solver_name(),
            instance_name=instance.name,
            routes=routes,
            total_distance=total_distance,
            total_time=sum(route.total_time for route in routes),
            solve_time=solve_time,
            status=status,
            objective_value=total_distance
        )

    def validate_instance(self, instance: VRPInstance) -> bool:
        """
        Validate instance for PyVRP compatibility.

        Args:
            instance: VRP instance to validate

        Returns:
            True if instance is compatible with PyVRP
        """
        if not super().validate_instance(instance):
            return False

        try:
            # PyVRP-specific validation
            if not self.supports_problem_type(instance.problem_type):
                self.logger.error(
                    f"Problem type {instance.problem_type} not supported")
                return False

            # Check for negative coordinates (PyVRP can handle them but warn)
            for loc in instance.locations:
                if loc.x < 0 or loc.y < 0:
                    self.logger.warning(
                        f"Location {loc.id} has negative coordinates")

            # Check vehicle capacity vs total demand
            total_demand = sum(
                loc.demand for loc in instance.locations if loc.id != 0)
            total_capacity = sum(veh.capacity for veh in instance.vehicles)

            if total_capacity < total_demand:
                self.logger.error(
                    "Total vehicle capacity insufficient for total demand")
                return False

            return True

        except Exception as e:
            self.logger.error(f"PyVRP instance validation error: {e}")
            return False

    def get_solver_info(self) -> dict:
        """Detailed solver information"""
        info = super().get_solver_info()
        info.update({
            'algorithm': 'Hybrid Genetic Search',
            'best_for': 'VRPTW problems',
            'competition_winner': True,
            'version': getattr(vrp, '__version__', 'unknown') if PYVRP_AVAILABLE else None
        })
        return info
