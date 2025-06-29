"""
Utils for VRP benchmarking.

Module provides utils (helper functions) for creating instances, calculating statistics, and other common operations.
"""

import random
import math
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from ..models import VRPInstance, Location, Vehicle, create_distance_matrix


def create_sample_instance(name: str = "sample", num_customers: int = 10,
                           seed: int = 42, **kwargs) -> VRPInstance:
    """
    Create a sample VRP instance for testing and demonstration.

    Args:
        name: Name for the instance
        num_customers: Number of customers to generate
        seed: Random seed for reproducible results
        **kwargs: Additional parameters for instance generation
            - area_size: Size of the coordinate area (default: 100)
            - num_vehicles: Number of vehicles (default: 3)
            - vehicle_capacity: Vehicle capacity (default: 50)
            - demand_range: Tuple of (min, max) demand values
            - service_time_range: Tuple of (min, max) service times
            - depot_location: Tuple of (x, y) for depot, or None for center

    Returns:
        Generated VRP instance
    """
    # Set random seed for reproducibility
    random.seed(seed)
    np.random.seed(seed)

    # Extract parameters with defaults
    area_size = kwargs.get('area_size', 100)
    num_vehicles = kwargs.get('num_vehicles', 3)
    vehicle_capacity = kwargs.get('vehicle_capacity', 50)
    demand_range = kwargs.get('demand_range', (1, 20))
    service_time_range = kwargs.get('service_time_range', (5, 15))
    depot_location = kwargs.get('depot_location', (area_size/2, area_size/2))

    # Create depot
    depot = Location(
        id=0,
        x=depot_location[0],
        y=depot_location[1],
        demand=0,
        service_time=0
    )

    locations = [depot]

    # Generate customer locations
    for i in range(1, num_customers + 1):
        location = Location(
            id=i,
            x=random.uniform(0, area_size),
            y=random.uniform(0, area_size),
            demand=random.randint(demand_range[0], demand_range[1]),
            service_time=random.randint(
                service_time_range[0], service_time_range[1])
        )
        locations.append(location)

    # Create vehicles
    vehicles = []
    for i in range(num_vehicles):
        vehicle = Vehicle(
            id=i,
            capacity=vehicle_capacity,
            depot_id=0
        )
        vehicles.append(vehicle)

    # Calculate distance matrix
    distance_matrix = create_distance_matrix(locations)

    return VRPInstance(
        name=name,
        locations=locations,
        vehicles=vehicles,
        distance_matrix=distance_matrix,
        problem_type="CVRP"
    )


def create_clustered_instance(name: str = "clustered", num_customers: int = 20,
                              num_clusters: int = 3, seed: int = 42, **kwargs) -> VRPInstance:
    """
    Create a VRP instance with clustered customers.

    Args:
        name: Name for the instance
        num_customers: Total number of customers
        num_clusters: Number of customer clusters
        seed: Random seed for reproducibility
        **kwargs: Additional parameters (listed on first util)

    Returns:
        VRP instance with clustered customer distribution
    """
    random.seed(seed)
    np.random.seed(seed)

    area_size = kwargs.get('area_size', 100)
    cluster_radius = kwargs.get('cluster_radius', 15)
    num_vehicles = kwargs.get('num_vehicles', num_clusters)
    vehicle_capacity = kwargs.get('vehicle_capacity', 60)

    # Create depot at center
    depot = Location(id=0, x=area_size/2, y=area_size/2, demand=0)
    locations = [depot]

    # Generate cluster centers
    cluster_centers = []
    for _ in range(num_clusters):
        center_x = random.uniform(cluster_radius, area_size - cluster_radius)
        center_y = random.uniform(cluster_radius, area_size - cluster_radius)
        cluster_centers.append((center_x, center_y))

    # Distribute customers among clusters
    customers_per_cluster = num_customers // num_clusters
    remaining_customers = num_customers % num_clusters

    customer_id = 1
    for cluster_idx, (center_x, center_y) in enumerate(cluster_centers):
        # Number of customers in this cluster
        cluster_size = customers_per_cluster
        if cluster_idx < remaining_customers:
            cluster_size += 1

        # Generate customers around cluster center
        for _ in range(cluster_size):
            # Random angle and distance from center
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, cluster_radius)

            x = center_x + distance * math.cos(angle)
            y = center_y + distance * math.sin(angle)

            # Keep within bounds
            x = max(0, min(area_size, x))
            y = max(0, min(area_size, y))

            location = Location(
                id=customer_id,
                x=x,
                y=y,
                demand=random.randint(5, 25),
                service_time=random.randint(5, 15)
            )
            locations.append(location)
            customer_id += 1

    # Create vehicles
    vehicles = [Vehicle(id=i, capacity=vehicle_capacity)
                for i in range(num_vehicles)]

    # Calculate distance matrix
    distance_matrix = create_distance_matrix(locations)

    return VRPInstance(
        name=name,
        locations=locations,
        vehicles=vehicles,
        distance_matrix=distance_matrix,
        problem_type="CVRP"
    )


def create_time_window_instance(name: str = "vrptw", num_customers: int = 15,
                                seed: int = 42, **kwargs) -> VRPInstance:
    """
    Create a VRP instance with time windows (VRPTW).

    Args:
        name: Name for the instance
        num_customers: Number of customers
        seed: Random seed
        **kwargs: Additional parameters (listed on first util)

    Returns:
        VRPTW instance
    """
    # Start with basic instance
    instance = create_sample_instance(name, num_customers, seed, **kwargs)

    # Add time windows to customers
    random.seed(seed)

    # Working day: 8 AM to 6 PM (480 to 1080 minutes)
    day_start = 480
    day_end = 1080
    window_size = kwargs.get('time_window_size', 60)  # 1 hour windows

    for location in instance.locations:
        if location.id == 0:  # Depot
            location.time_window_start = day_start
            location.time_window_end = day_end
        else:  # Customers
            # Random start time during the day
            latest_start = day_end - window_size - location.service_time
            start_time = random.randint(day_start, latest_start)

            location.time_window_start = start_time
            location.time_window_end = start_time + window_size

    instance.problem_type = "VRPTW"
    return instance


def calculate_solution_statistics(values: List[float]) -> Dict[str, float]:
    """
    Calculate basic statistics for a list of values.

    Args:
        values: List of numerical values

    Returns:
        Dictionary with statistical measures
    """
    if not values:
        return {}

    # Filter out infinite values
    values = [v for v in values if v != float('inf')]

    if not values:
        return {'count': 0}

    n = len(values)
    mean = sum(values) / n

    if n == 1:
        return {
            'count': n,
            'mean': mean,
            'min': values[0],
            'max': values[0],
            'std': 0.0,
            'median': values[0]
        }

    # Calculate variance and standard deviation
    variance = sum((x - mean) ** 2 for x in values) / (n - 1)
    std = math.sqrt(variance)

    # Calculate median
    sorted_values = sorted(values)
    if n % 2 == 0:
        median = (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
    else:
        median = sorted_values[n//2]

    return {
        'count': n,
        'mean': mean,
        'min': min(values),
        'max': max(values),
        'std': std,
        'median': median,
        'range': max(values) - min(values)
    }


def validate_solution_feasibility(solution, instance: VRPInstance) -> Tuple[bool, List[str]]:
    """
    Validate that a solution is feasible for the given instance.

    Args:
        solution: VRP solution to validate
        instance: VRP instance the solution should solve

    Returns:
        Tuple of (is_feasible, list_of_violations)
    """
    violations = []

    if solution.status == "ERROR":
        return False, ["Solution has ERROR status"]

    # Check if all customers are visited exactly once
    all_customers = set(range(1, len(instance.locations)))
    visited_customers = set()

    for route in solution.routes:
        customers_in_route = [
            loc_id for loc_id in route.locations if loc_id != 0]

        # Check for duplicate visits within route
        if len(customers_in_route) != len(set(customers_in_route)):
            violations.append(
                f"Route {route.vehicle_id} visits customers multiple times")

        # Check for customers visited in multiple routes
        route_customers = set(customers_in_route)
        overlap = visited_customers & route_customers
        if overlap:
            violations.append(
                f"Customers {overlap} visited in multiple routes")

        visited_customers.update(route_customers)

    # Check if all customers are visited
    unvisited = all_customers - visited_customers
    if unvisited:
        violations.append(f"Customers {unvisited} not visited")

    # Check vehicle capacity constraints
    for route in solution.routes:
        if route.vehicle_id >= len(instance.vehicles):
            violations.append(
                f"Route uses invalid vehicle ID {route.vehicle_id}")
            continue

        vehicle = instance.vehicles[route.vehicle_id]
        if route.total_demand > vehicle.capacity:
            violations.append(
                f"Route {route.vehicle_id} demand ({route.total_demand}) "
                f"exceeds capacity ({vehicle.capacity})"
            )

    # Check route structure (should start and end at depot)
    for route in solution.routes:
        if not route.is_valid_route():
            violations.append(
                f"Route {route.vehicle_id} doesn't start/end at depot")

    return len(violations) == 0, violations


def calculate_route_distance(route_locations: List[int],
                             distance_matrix: List[List[float]]) -> float:
    """
    Calculate total distance for a route.

    Args:
        route_locations: List of location IDs in visit order
        distance_matrix: Distance matrix between locations

    Returns:
        Total route distance
    """
    if len(route_locations) < 2:
        return 0.0

    total_distance = 0.0
    for i in range(len(route_locations) - 1):
        from_loc = route_locations[i]
        to_loc = route_locations[i + 1]
        total_distance += distance_matrix[from_loc][to_loc]

    return total_distance


def generate_instance_variants(base_instance: VRPInstance,
                               variants: List[str]) -> Dict[str, VRPInstance]:
    """
    Generate variants of a base instance for testing.

    Args:
        base_instance: Base VRP instance
        variants: List of variant types to generate
            - "larger": Increase problem size
            - "smaller": Decrease problem size  
            - "tighter_capacity": Reduce vehicle capacities
            - "more_vehicles": Add more vehicles
            - "time_windows": Add time window constraints

    Returns:
        Dictionary mapping variant names to instances
    """
    result = {}

    for variant in variants:
        if variant == "larger":
            # Add more customers by duplicating and shifting existing ones
            new_locations = base_instance.locations.copy()
            next_id = len(new_locations)

            # Add 50% more customers
            customers_to_add = len(base_instance.locations) // 2
            for i in range(customers_to_add):
                orig_customer = base_instance.locations[1 +
                                                        (i % (len(base_instance.locations) - 1))]
                new_location = Location(
                    id=next_id,
                    x=orig_customer.x + random.uniform(-10, 10),
                    y=orig_customer.y + random.uniform(-10, 10),
                    demand=orig_customer.demand,
                    service_time=orig_customer.service_time
                )
                new_locations.append(new_location)
                next_id += 1

            # Recalculate distance matrix
            new_distance_matrix = create_distance_matrix(new_locations)

            result[f"{base_instance.name}_larger"] = VRPInstance(
                name=f"{base_instance.name}_larger",
                locations=new_locations,
                vehicles=base_instance.vehicles.copy(),
                distance_matrix=new_distance_matrix,
                problem_type=base_instance.problem_type
            )

        elif variant == "tighter_capacity":
            # Reduce vehicle capacities by 25%
            new_vehicles = []
            for vehicle in base_instance.vehicles:
                new_vehicle = Vehicle(
                    id=vehicle.id,
                    capacity=max(1, int(vehicle.capacity * 0.75)),
                    depot_id=vehicle.depot_id,
                    max_time=vehicle.max_time
                )
                new_vehicles.append(new_vehicle)

            result[f"{base_instance.name}_tight_capacity"] = VRPInstance(
                name=f"{base_instance.name}_tight_capacity",
                locations=base_instance.locations.copy(),
                vehicles=new_vehicles,
                distance_matrix=[row.copy()
                                 for row in base_instance.distance_matrix],
                problem_type=base_instance.problem_type
            )

        # Add more variants as needed...

    return result


def format_solution_summary(solution) -> str:
    """
    Format a solution as a readable summary string.

    Args:
        solution: VRP solution to format

    Returns:
        Formatted summary string
    """
    if solution.status == "ERROR":
        return f"{solution.solver_name}: ERROR (time: {solution.solve_time:.3f}s)"

    return (f"{solution.solver_name}: {solution.total_distance:.2f} "
            f"({len(solution.routes)} routes, {solution.solve_time:.3f}s)")


def export_solution_to_csv(solutions: List, filepath: str):
    """
    Export solutions to CSV format for analysis.

    Args:
        solutions: List of VRP solutions
        filepath: Output CSV file path
    """
    import csv

    filepath = 'data/benchmark_results/' + filepath;
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = [
            'solver_name', 'instance_name', 'total_distance', 'num_routes',
            'solve_time', 'status', 'objective_value'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for solution in solutions:
            writer.writerow({
                'solver_name': solution.solver_name,
                'instance_name': solution.instance_name,
                'total_distance': solution.total_distance,
                'num_routes': len(solution.routes),
                'solve_time': solution.solve_time,
                'status': solution.status,
                'objective_value': solution.objective_value
            })
