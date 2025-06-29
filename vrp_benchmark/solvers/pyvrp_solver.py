"""
PyVRP solver implementation.
"""

import time
from typing import List, Optional
import numpy as np

from .base import MetaheuristicSolver
from ..models import VRPInstance, VRPSolution, Route

# Try to import PyVRP with correct API
try:
    import pyvrp
    from pyvrp import Model, ProblemData, Client, Depot, VehicleType
    PYVRP_AVAILABLE = True
except ImportError:
    PYVRP_AVAILABLE = False
    pyvrp = None
    Model = None
    ProblemData = None
    Client = None
    Depot = None
    VehicleType = None


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

        self.default_config = {
            'seed': 42,
            'max_iterations': 1000
        }
        self.config = {**self.default_config, **self.config}

        if not PYVRP_AVAILABLE:
            self.logger.warning(
                "PyVRP not available. Install with: pip install pyvrp")

    def is_available(self) -> bool:
        """Check if PyVRP is available with correct API"""
        return (PYVRP_AVAILABLE and
                hasattr(pyvrp, 'Model') and
                hasattr(pyvrp, 'Client') and
                hasattr(pyvrp, 'Depot') and
                hasattr(pyvrp, 'VehicleType'))

    def get_solver_name(self) -> str:
        return "PyVRP"

    def get_supported_problem_types(self) -> List[str]:
        return ["CVRP", "VRPTW", "VRP"]

    def solve(self, instance: VRPInstance, time_limit: int = 30, **kwargs) -> VRPSolution:
        """Solve VRP instance using PyVRP"""
        if not self.is_available():
            return self.create_error_solution(
                instance, "PyVRP is not available or API incompatible", 0.0
            )

        if not self.validate_instance(instance):
            return self.create_error_solution(
                instance, "Instance validation failed", 0.0
            )

        start_time = time.time()

        try:
            # Create PyVRP problem data
            problem_data = self._create_problem_data(instance)
            model = Model.from_data(problem_data)

            # Set up stopping criterion
            if 'max_iterations' in kwargs:
                stop_criterion = pyvrp.stop.MaxIterations(
                    kwargs['max_iterations'])
            else:
                stop_criterion = pyvrp.stop.MaxRuntime(time_limit)

            # Solve the problem
            result = model.solve(
                stop=stop_criterion,
                seed=self.config.get('seed', 42),
                display=False
            )

            solve_time = time.time() - start_time

            if result.best is None:
                return self.create_error_solution(
                    instance, "PyVRP found no solution", solve_time
                )

            # Convert solution
            vrp_solution = self._convert_solution(
                result.best, instance, solve_time)
            return vrp_solution

        except Exception as e:
            solve_time = time.time() - start_time
            error_msg = f"PyVRP solver error: {str(e)}"
            self.logger.error(error_msg)
            return self.create_error_solution(instance, error_msg, solve_time)

    def _create_problem_data(self, instance: VRPInstance) -> 'ProblemData':
        """Create PyVRP ProblemData with correct API parameters"""

        # Create depot objects
        depots = []
        for loc in instance.locations:
            if loc.id == 0:  # Depot has ID 0
                depot = Depot(
                    x=int(round(loc.x)),
                    y=int(round(loc.y)),
                    name=f"Depot_{loc.id}"
                )
                depots.append(depot)

        # Create client objects (customers)
        clients = []
        for loc in instance.locations:
            if loc.id != 0:  # Clients have ID > 0
                client = Client(
                    x=int(round(loc.x)),           # Integer coordinates
                    y=int(round(loc.y)),           # Integer coordinates
                    delivery=[loc.demand],         # Delivery as list
                    pickup=[],                     # Empty pickup list
                    service_duration=int(loc.service_time),
                    tw_early=int(loc.time_window_start),
                    tw_late=int(loc.time_window_end),
                    name=f"Client_{loc.id}"
                )
                clients.append(client)

        # Create vehicle type objects - FIXED API
        vehicle_types = []
        unique_capacities = list(
            set(veh.capacity for veh in instance.vehicles))

        for i, capacity in enumerate(unique_capacities):
            # Count how many vehicles have this capacity
            num_vehicles = sum(
                1 for veh in instance.vehicles if veh.capacity == capacity)

            vehicle_type = VehicleType(
                num_available=num_vehicles,        # Number of vehicles of this type
                capacity=[capacity],               # Capacity as list!
                start_depot=0,                     # Start from depot 0
                end_depot=0,                       # End at depot 0
                max_duration=int(
                    max(veh.max_time for veh in instance.vehicles if veh.capacity == capacity)),
                name=f"VehicleType_{i}"
            )
            vehicle_types.append(vehicle_type)

        # Distance and duration matrices
        distance_matrix = np.array(instance.distance_matrix)
        distance_matrix_int = (distance_matrix * 1000).astype(int)

        # Create ProblemData
        problem_data = ProblemData(
            clients=clients,
            depots=depots,
            vehicle_types=vehicle_types,
            distance_matrices=[distance_matrix_int],
            duration_matrices=[distance_matrix_int],
            groups=[]
        )

        return problem_data

    def _convert_solution(self, pyvrp_solution, instance: VRPInstance,
                          solve_time: float) -> VRPSolution:
        """Convert PyVRP solution to VRPSolution format"""
        routes = []
        total_distance = 0.0

        for route_idx, route in enumerate(pyvrp_solution.routes()):
            if len(route) == 0:
                continue

            route_locations = [0]  # Start at depot
            route_distance = 0.0
            route_demand = 0
            route_time = 0.0

            # Add customer visits
            for client_idx in route:
                location_id = client_idx + 1  # Convert to 1-based
                if location_id < len(instance.locations):
                    route_locations.append(location_id)
                    route_demand += instance.locations[location_id].demand
                    route_time += instance.locations[location_id].service_time

            route_locations.append(0)  # Return to depot

            # Calculate route distance
            for i in range(len(route_locations) - 1):
                from_loc = route_locations[i]
                to_loc = route_locations[i + 1]
                route_distance += instance.distance_matrix[from_loc][to_loc]

            routes.append(Route(
                vehicle_id=route_idx,
                locations=route_locations,
                total_distance=route_distance,
                total_demand=route_demand,
                total_time=route_time
            ))
            total_distance += route_distance

        return VRPSolution(
            solver_name=self.get_solver_name(),
            instance_name=instance.name,
            routes=routes,
            total_distance=total_distance,
            total_time=sum(route.total_time for route in routes),
            solve_time=solve_time,
            status="OPTIMAL",
            objective_value=total_distance
        )

    def validate_instance(self, instance: VRPInstance) -> bool:
        """Validate instance for PyVRP compatibility"""
        if not super().validate_instance(instance):
            return False

        try:
            if not self.supports_problem_type(instance.problem_type):
                self.logger.error(
                    f"Problem type {instance.problem_type} not supported")
                return False

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
        """Get detailed solver information"""
        info = super().get_solver_info()
        info.update({
            'algorithm': 'Hybrid Genetic Search',
            'best_for': 'VRPTW problems',
            'competition_winner': True,
            'version': getattr(pyvrp, '__version__', 'unknown') if PYVRP_AVAILABLE else None
        })
        return info
