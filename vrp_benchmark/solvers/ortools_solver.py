"""
Google OR-Tools solver implementation.
"""

import time
from typing import List, Optional

from .base import HeuristicSolver
from ..models import VRPInstance, VRPSolution, Route

# Try to import OR-Tools
try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    routing_enums_pb2 = None
    pywrapcp = None


class ORToolsSolver(HeuristicSolver):
    """
    Google OR-Tools solver implementation.
    """

    def __init__(self, **kwargs):
        """
        Initialize OR-Tools solver.

        Args:
            **kwargs: Configuration parameters for OR-Tools
                - first_solution_strategy: strategy for finding initial solution
                - local_search_metaheuristic: socal search method
                - solution_limit: max number of solutions to find
        """
        super().__init__(**kwargs)

        # Default OR-Tools parameters
        self.default_config = {
            'first_solution_strategy': 'PATH_CHEAPEST_ARC',
            'local_search_metaheuristic': 'GUIDED_LOCAL_SEARCH',
            'solution_limit': 100
        }

        # Merge with user config
        self.config = {**self.default_config, **self.config}

        if not ORTOOLS_AVAILABLE:
            self.logger.warning(
                "OR-Tools not available. Install with: pip install ortools")

    def is_available(self) -> bool:
        """Check if OR-Tools is available"""
        return ORTOOLS_AVAILABLE

    def get_solver_name(self) -> str:
        return "OR-Tools"

    def get_supported_problem_types(self) -> List[str]:
        return ["CVRP", "VRPTW", "VRP", "MDVRP"]

    def solve(self, instance: VRPInstance, time_limit: int = 30, **kwargs) -> VRPSolution:
        """
        Solves VRP with OR-Tools.

        Args:
            instance: VRP problem instance to solve
            time_limit: Maximum solving time in seconds
            **kwargs: Additional OR-Tools-specific parameters

        Returns:
            VRPSolution containing the best solution found
        """
        if not self.is_available():
            return self.create_error_solution(
                instance, "OR-Tools is not available", 0.0
            )

        if not self.validate_instance(instance):
            return self.create_error_solution(
                instance, "Instance validation failed", 0.0
            )

        start_time = time.time()

        try:
            # Merge runtime config with kwargs
            runtime_config = {**self.config, **kwargs}

            # Create OR-Tools routing model
            manager, routing = self._create_routing_model(instance)

            # Add constraints and objectives
            self._add_distance_constraint(manager, routing, instance)
            self._add_capacity_constraint(manager, routing, instance)

            if instance.problem_type == "VRPTW":
                self._add_time_window_constraint(manager, routing, instance)

            # Set search parameters
            search_parameters = self._create_search_parameters(
                time_limit, runtime_config
            )

            # Solve the problem
            assignment = routing.SolveWithParameters(search_parameters)
            solve_time = time.time() - start_time

            if assignment:
                # Convert solution
                vrp_solution = self._convert_solution(
                    assignment, manager, routing, instance, solve_time
                )
                return vrp_solution
            else:
                return self.create_error_solution(
                    instance, "OR-Tools found no solution", solve_time
                )

        except Exception as e:
            solve_time = time.time() - start_time
            error_msg = f"OR-Tools solver error: {str(e)}"
            self.logger.error(error_msg)
            return self.create_error_solution(instance, error_msg, solve_time)

    def _create_routing_model(self, instance: VRPInstance):
        """
        Create OR-Tools routing model from VRP instance.

        Returns:
            Tuple of (RoutingIndexManager, RoutingModel)
        """
        # Create the routing index manager
        manager = pywrapcp.RoutingIndexManager(
            len(instance.locations),  # Number of locations
            len(instance.vehicles),   # Number of vehicles
            0  # Depot index (assuming depot is at index 0)
        )

        # Create routing model
        routing = pywrapcp.RoutingModel(manager)

        return manager, routing

    def _add_distance_constraint(self, manager, routing, instance: VRPInstance):
        """
        Add distance/cost constraint to the routing model.

        Args:
            manager: OR-Tools routing index manager
            routing: OR-Tools routing model
            instance: VRP problem instance
        """
        def distance_callback(from_index, to_index):
            """Returns the distance between two nodes"""
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            # Scale distance by 1000 to work with integers (OR-Tools requirement)
            return int(instance.distance_matrix[from_node][to_node] * 1000)

        transit_callback_index = routing.RegisterTransitCallback(
            distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def _add_capacity_constraint(self, manager, routing, instance: VRPInstance):
        """
        Add vehicle capacity constraint to the routing model.

        Args:
            manager: OR-Tools routing index manager
            routing: OR-Tools routing model
            instance: VRP problem instance
        """
        def demand_callback(from_index):
            """Returns the demand of the node"""
            from_node = manager.IndexToNode(from_index)
            return instance.locations[from_node].demand

        demand_callback_index = routing.RegisterUnaryTransitCallback(
            demand_callback)

        # Get vehicle capacities
        vehicle_capacities = [
            vehicle.capacity for vehicle in instance.vehicles]

        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            vehicle_capacities,  # vehicle maximum capacities
            True,  # start cumul to zero
            'Capacity'
        )

    def _add_time_window_constraint(self, manager, routing, instance: VRPInstance):
        """
        Add time window constraints for VRPTW problems.

        Args:
            manager: OR-Tools routing index manager
            routing: OR-Tools routing model
            instance: VRP problem instance
        """
        def time_callback(from_index, to_index):
            """Returns the travel time between two nodes"""
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)

            # Travel time (assume speed = 1, so time = distance)
            travel_time = int(instance.distance_matrix[from_node][to_node])

            # Add service time at the destination
            service_time = instance.locations[to_node].service_time

            return travel_time + service_time

        time_callback_index = routing.RegisterTransitCallback(time_callback)

        # Create time dimension
        max_time = max(vehicle.max_time for vehicle in instance.vehicles)
        routing.AddDimension(
            time_callback_index,
            max_time,  # allow waiting time
            max_time,  # maximum time per vehicle
            False,  # don't force start cumul to zero
            'Time'
        )

        time_dimension = routing.GetDimensionOrDie('Time')

        # Add time window constraints for each location
        for location_idx, location in enumerate(instance.locations):
            index = manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(
                location.time_window_start,
                location.time_window_end
            )

    def _create_search_parameters(self, time_limit: int, config: dict):
        """
        Create search parameters for OR-Tools solver.

        Args:
            time_limit: max solving time in seconds
            config: Configuration dictionary

        Returns:
            OR-Tools search parameters object
        """
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()

        # Set time limit
        search_parameters.time_limit.seconds = time_limit

        # Set first solution strategy
        strategy_name = config.get(
            'first_solution_strategy', 'PATH_CHEAPEST_ARC')
        if hasattr(routing_enums_pb2.FirstSolutionStrategy, strategy_name):
            search_parameters.first_solution_strategy = getattr(
                routing_enums_pb2.FirstSolutionStrategy, strategy_name
            )

        # Set local search metaheuristic
        metaheuristic_name = config.get(
            'local_search_metaheuristic', 'GUIDED_LOCAL_SEARCH')
        if hasattr(routing_enums_pb2.LocalSearchMetaheuristic, metaheuristic_name):
            search_parameters.local_search_metaheuristic = getattr(
                routing_enums_pb2.LocalSearchMetaheuristic, metaheuristic_name
            )

        # Set solution limit
        solution_limit = config.get('solution_limit', 100)
        search_parameters.solution_limit = solution_limit

        return search_parameters

    def _convert_solution(self, assignment, manager, routing,
                          instance: VRPInstance, solve_time: float) -> VRPSolution:
        """
        Convert OR-Tools solution to VRPSolution format.

        Args:
            assignment: OR-Tools assignment solution
            manager: OR-Tools routing index manager
            routing: OR-Tools routing model
            instance: Original VRP instance
            solve_time: Time taken to solve

        Returns:
            VRPSolution object
        """
        routes = []
        total_distance = 0.0

        for vehicle_id in range(len(instance.vehicles)):
            index = routing.Start(vehicle_id)
            route_locations = []
            route_distance = 0.0
            route_demand = 0
            route_time = 0.0

            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route_locations.append(node_index)
                route_demand += instance.locations[node_index].demand
                route_time += instance.locations[node_index].service_time

                previous_index = index
                index = assignment.Value(routing.NextVar(index))

                # Add arc cost (unscale by dividing by 1000)
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                ) / 1000.0

            # Add final node (depot)
            final_node = manager.IndexToNode(index)
            route_locations.append(final_node)

            # Only include routes that visit customers (more than just depot->depot)
            if len(route_locations) > 2:
                routes.append(Route(
                    vehicle_id=vehicle_id,
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
            status="OPTIMAL",  # OR-Tools doesn't clearly distinguish optimal vs feasible
            objective_value=total_distance
        )

    def validate_instance(self, instance: VRPInstance) -> bool:
        """
        Validate instance for OR-Tools compatibility.
        """
        if not super().validate_instance(instance):
            return False

        try:
            # OR-Tools specific validation
            if not self.supports_problem_type(instance.problem_type):
                self.logger.error(
                    f"Problem type {instance.problem_type} not supported")
                return False

            # Check for very large distances (OR-Tools uses 32-bit integers internally)
            max_distance = max(
                max(row) for row in instance.distance_matrix
            )
            if max_distance * 1000 > 2**31 - 1:  # We scale by 1000
                self.logger.error(
                    "Distance values too large for OR-Tools (after scaling)")
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
            self.logger.error(f"OR-Tools instance validation error: {e}")
            return False

    def get_solver_info(self) -> dict:
        """Detailed solver information"""
        info = super().get_solver_info()
        info.update({
            'algorithm': 'Constraint Programming + Local Search',
            'best_for': 'Production systems, large-scale problems',
            'google_backed': True,
            'supports_constraints': True
        })
        return info
