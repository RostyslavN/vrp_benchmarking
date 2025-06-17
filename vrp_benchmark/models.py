"""
All data structures used throughout the API
"""

from dataclasses import dataclass, asdict
from typing import List, Dict
from enum import Enum


class SolverType(Enum):
    PYVRP = "pyvrp"
    ORTOOLS = "ortools"
    # LKH3 = "lkh3"
    # VRPSOLVER = "vrpsolver"
    # OPTAPY = "optapy"


@dataclass
class Location:
    """
    Represents a location in the VRP instance.

    Attributes:
        id: Location ID
        x
        y
        demand: Customer demand at this location (0 for depot)
        service_time
        time_window_start: Earliest time service can begin
        time_window_end: Latest time service can begin
    """

    id: int
    x: float
    y: float
    demand: int = 0
    service_time: int = 0
    time_window_start: int = 0
    time_window_end: int = 86400  # 24 hours default

    def __post_init__(self):
        if self.demand < 0:
            raise ValueError("Demand cannot be negative")
        if self.service_time < 0:
            raise ValueError("Service time cannot be negative")
        if self.time_window_start < 0:
            raise ValueError("Time window start cannot be negative")
        if self.time_window_end <= self.time_window_start:
            raise ValueError("Time window end must be after start")


@dataclass
class Vehicle:
    """
    Represents a vehicle in the VRP instance.

    Attributes:
        id: Vehicle ID
        capacity
        depot_id: ID of the depot where vehicle starts/ends
        max_time: Maximum route duration allowed
    """

    id: int
    capacity: int
    depot_id: int = 0
    max_time: int = 86400  # 24 hours default

    def __post_init__(self):
        if self.capacity <= 0:
            raise ValueError("Vehicle capacity must be positive")
        if self.max_time <= 0:
            raise ValueError("Max time must be positive")


@dataclass
class VRPInstance:
    """
    Represents a complete VRP problem instance.

    Attributes:
        name: Instance ID
        locations: All locations (depot + customers)
        vehicles
        distance_matrix: Square matrix of distances between locations
        problem_type: Type of VRP problem (CVRP, VRPTW, etc.)
    """

    name: str
    locations: List[Location]
    vehicles: List[Vehicle]
    distance_matrix: List[List[float]]
    problem_type: str = "CVRP"

    def __post_init__(self):
        if not self.locations:
            raise ValueError("Instance must have at least one location")
        if not self.vehicles:
            raise ValueError("Instance must have at least one vehicle")

        n_locations = len(self.locations)
        if len(self.distance_matrix) != n_locations:
            raise ValueError(
                "Distance matrix size must match number of locations")

        for i, row in enumerate(self.distance_matrix):
            if len(row) != n_locations:
                raise ValueError(f"Distance matrix row {i} has incorrect size")
            if row[i] != 0:
                raise ValueError(
                    f"Distance from location {i} to itself must be 0")

    def to_dict(self) -> Dict:
        """Convert instance to dictionary format for serialization"""
        return {
            "name": self.name,
            "locations": [asdict(loc) for loc in self.locations],
            "vehicles": [asdict(veh) for veh in self.vehicles],
            "distance_matrix": self.distance_matrix,
            "problem_type": self.problem_type,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "VRPInstance":
        """Create instance from dictionary data"""
        locations = [Location(**loc_data) for loc_data in data["locations"]]
        vehicles = [Vehicle(**veh_data) for veh_data in data["vehicles"]]

        return cls(
            name=data["name"],
            locations=locations,
            vehicles=vehicles,
            distance_matrix=data["distance_matrix"],
            problem_type=data.get("problem_type", "CVRP"),
        )

    def get_num_customers(self) -> int:
        """Get number of customers (excluding depot)"""
        return len(self.locations) - 1

    def get_total_demand(self) -> int:
        """Get total demand across all customers"""
        return sum(loc.demand for loc in self.locations if loc.id != 0)


@dataclass
class Route:
    """
    Represents a single route in the solution.

    Attributes:
        vehicle_id: ID of vehicle assigned to this route
        locations: Ordered sequence of location IDs visited
        total_distance: Total distance of the route
        total_demand: Total demand served by this route
        total_time: Total time for the route
    """

    vehicle_id: int
    locations: List[int]
    total_distance: float
    total_demand: int
    total_time: float

    def __post_init__(self):
        """Validate route data after initialization"""
        if not self.locations:
            raise ValueError("Route must visit at least one location")
        if self.total_distance < 0:
            raise ValueError("Total distance cannot be negative")
        if self.total_demand < 0:
            raise ValueError("Total demand cannot be negative")
        if self.total_time < 0:
            raise ValueError("Total time cannot be negative")

    def is_valid_route(self) -> bool:
        """Check if route starts and ends at depot (location 0)"""
        return (
            len(self.locations) >= 2
            and self.locations[0] == 0
            and self.locations[-1] == 0
        )

    def get_customer_sequence(self) -> List[int]:
        """Get sequence of customers (excluding depot visits)"""
        return [loc_id for loc_id in self.locations if loc_id != 0]


@dataclass
class VRPSolution:
    """
    Represents a complete VRP solution from any solver.

    Attributes:
        solver_name
        instance_name
        routes
        total_distance
        total_time: Total time across all routes
        solve_time: Time taken by solver to find solution (seconds)
        status: Solution status (OPTIMAL, FEASIBLE, ERROR, etc.)
        objective_value: Value of the objective function
    """

    solver_name: str
    instance_name: str
    routes: List[Route]
    total_distance: float
    total_time: float
    solve_time: float
    status: str
    objective_value: float

    def to_dict(self) -> Dict:
        """Convert solution to dictionary format for serialization"""
        return {
            "solver_name": self.solver_name,
            "instance_name": self.instance_name,
            "routes": [asdict(route) for route in self.routes],
            "total_distance": self.total_distance,
            "total_time": self.total_time,
            "solve_time": self.solve_time,
            "status": self.status,
            "objective_value": self.objective_value,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "VRPSolution":
        """Create solution from dictionary data"""
        routes = [Route(**route_data) for route_data in data["routes"]]

        return cls(
            solver_name=data["solver_name"],
            instance_name=data["instance_name"],
            routes=routes,
            total_distance=data["total_distance"],
            total_time=data["total_time"],
            solve_time=data["solve_time"],
            status=data["status"],
            objective_value=data["objective_value"],
        )

    def print_summary(self):
        print(f"\n=== VRP Solution Summary ===")
        print(f"Solver: {self.solver_name}")
        print(f"Instance: {self.instance_name}")
        print(f"Status: {self.status}")
        print(f"Total Distance: {self.total_distance:.2f}")
        print(f"Number of Routes: {len(self.routes)}")
        print(f"Solve Time: {self.solve_time:.3f} seconds")
        print(f"Objective Value: {self.objective_value:.2f}")

        for i, route in enumerate(self.routes):
            customer_seq = route.get_customer_sequence()
            print(
                f"Route {i+1}: 0 -> {' -> '.join(map(str, customer_seq))} -> 0 "
                f"(Distance: {route.total_distance:.2f}, Demand: {route.total_demand})"
            )

    def is_feasible(self, instance: "VRPInstance") -> bool:
        """
        Check if solution is feasible for the given instance.

        Args:
            instance: The VRP instance this solution should solve

        Returns:
            True if solution is feasible, False otherwise
        """
        if not self.routes:
            return len(instance.locations) == 1  # Only depot

        # Check if all customers are visited exactly once
        all_customers = set(range(1, len(instance.locations)))
        visited_customers = set()

        for route in self.routes:
            customers_in_route = set(route.get_customer_sequence())
            if visited_customers & customers_in_route:
                return False  # Customer visited multiple times
            visited_customers.update(customers_in_route)

        return visited_customers == all_customers

    def get_num_vehicles_used(self) -> int:
        """Get number of vehicles actually used in solution"""
        return len(
            [route for route in self.routes if len(
                route.get_customer_sequence()) > 0]
        )


# Utility functions for working with data models


def calculate_euclidean_distance(loc1: Location, loc2: Location) -> float:
    """Calculate Euclidean distance between two locations"""
    return ((loc1.x - loc2.x) ** 2 + (loc1.y - loc2.y) ** 2) ** 0.5


def create_distance_matrix(locations: List[Location]) -> List[List[float]]:
    """Create distance matrix from list of locations using Euclidean distance"""
    n = len(locations)
    matrix = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = calculate_euclidean_distance(
                    locations[i], locations[j])

    return matrix


def validate_solution_format(solution: VRPSolution) -> List[str]:
    """
    Validate solution format and return list of issues found.

    Returns:
        List of validation error messages (empty if valid)
    """
    issues = []

    if not solution.solver_name:
        issues.append("Solver name cannot be empty")

    if not solution.instance_name:
        issues.append("Instance name cannot be empty")

    if solution.total_distance < 0:
        issues.append("Total distance cannot be negative")

    if solution.solve_time < 0:
        issues.append("Solve time cannot be negative")

    # Validate individual routes
    for i, route in enumerate(solution.routes):
        if not route.is_valid_route():
            issues.append(f"Route {i+1} does not start and end at depot")

    return issues
