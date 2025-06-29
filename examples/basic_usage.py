#!/usr/bin/env python3
"""
Basic usage example for VRP Benchmarking API.

This example demonstrates how to:
1. Initialize the benchmark API
2. Create sample VRP instances
3. Run individual solvers
4. Benchmark multiple solvers
5. Compare and analyze results
6. Export results

Run this example with:
    python examples/basic_usage.py
"""

from vrp_benchmark import VRPBenchmark
from vrp_benchmark import (
    VRPBenchmark, create_sample_instance, create_clustered_instance
)
import logging
import sys
from pathlib import Path

# Add the parent directory to path so we can import vrp_benchmark
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))


def setup_logging():
    """Configure logging for the example"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('vrp_benchmark.log')
        ]
    )


def demo_basic_usage():
    """Demonstrate basic API usage"""
    print("=" * 60)
    print("VRP Benchmarking API - basic usage demo")
    print("=" * 60)

    # Initialize the benchmark API
    print("\n1. Initializing VRP benchmark API...")
    benchmark = VRPBenchmark()

    available_solvers = benchmark.get_available_solvers()
    print(f"Available solvers: {available_solvers}")

    if not available_solvers:
        print("No solvers available! Please install PyVRP and/or OR-Tools:")
        print("  pip install pyvrp ortools")
        return None

    # Create sample instances
    print("\n2. Creating sample VRP instances...")

    # Small instance for quick testing
    small_instance = benchmark.create_sample_instance(
        name="small_feasible",
        num_customers=6,
        num_vehicles=2,
        vehicle_capacity=60,
        demand_range=(5, 15)
    )
    total_demand = sum(
        loc.demand for loc in small_instance.locations if loc.id != 0)
    total_capacity = sum(veh.capacity for veh in small_instance.vehicles)
    print(
        f"Created '{small_instance.name}': {small_instance.get_num_customers()} customers")
    print(f"  Total demand: {total_demand}, Total capacity: {total_capacity}")

    # Medium instance
    medium_instance = benchmark.create_sample_instance(
        name="medium_feasible",
        num_customers=10,
        num_vehicles=3,
        vehicle_capacity=80,
        demand_range=(8, 20)
    )
    total_demand = sum(
        loc.demand for loc in medium_instance.locations if loc.id != 0)
    total_capacity = sum(veh.capacity for veh in medium_instance.vehicles)
    print(
        f"Created '{medium_instance.name}': {medium_instance.get_num_customers()} customers")
    print(f"  Total demand: {total_demand}, Total capacity: {total_capacity}")

    return benchmark


def demo_individual_solving(benchmark):
    """Demonstrate solving with individual solvers"""
    print("\n3. Solving with individual solvers...")

    available_solvers = benchmark.get_available_solvers()
    instance_name = "small_feasible"

    solutions = {}
    for solver_name in available_solvers:
        print(f"\nSolving '{instance_name}' with {solver_name}...")
        try:
            solution = benchmark.solve(
                instance_name=instance_name,
                solver_name=solver_name,
                time_limit=15
            )
            solutions[solver_name] = solution

            if solution.status == "ERROR":
                print(f"  ❌ {solver_name}: Failed to solve")
            else:
                print(f"  ✅ {solver_name}: {solution.total_distance:.2f} "
                      f"({len(solution.routes)} routes, {solution.solve_time:.3f}s)")

        except Exception as e:
            print(f"  ❌ {solver_name}: Exception - {e}")

    return solutions


def demo_benchmarking(benchmark):
    """Demonstrate benchmarking multiple solvers"""
    print("\n4. Running benchmark comparison...")

    instance_name = "medium_feasible"
    print(f"Benchmarking instance: {instance_name}")

    try:
        instance_results = benchmark.benchmark(
            instance_name=instance_name,
            time_limit=20
        )

        print("Results:")
        for solver_name, solution in instance_results.items():
            if solution.status == "ERROR":
                print(f"  ❌ {solver_name}: Failed")
            else:
                print(f"  ✅ {solver_name}: {solution.total_distance:.2f} "
                      f"({solution.solve_time:.2f}s)")

        return instance_results

    except Exception as e:
        print(f"Failed to benchmark {instance_name}: {e}")
        return {}


def demo_comparison_analysis(benchmark, solutions):
    """Demonstrate solution comparison"""
    print("\n5. Comparing solver performance...")

    if not solutions:
        print("No solutions to compare")
        return

    comparison = benchmark.compare_solutions(solutions)

    if 'best_solver' in comparison:
        print(
            f"🏆 Best solution: {comparison['best_distance']:.2f} by {comparison['best_solver']}")
        print(
            f"📊 Success rate: {comparison['successful_solvers']}/{comparison['total_solvers']} solvers")

        # Performance gaps
        if 'gaps' in comparison and len(comparison['gaps']) > 1:
            print("📈 Performance gaps from best:")
            for solver, gap in comparison['gaps'].items():
                if gap > 0:
                    print(f"    {solver}: +{gap:.1f}%")
                else:
                    print(f"    {solver}: Best solution")
    else:
        print("❌ No valid solutions found")


def demo_solver_info(benchmark):
    """Show detailed solver information"""
    print("\n6. Solver Information:")

    solver_info = benchmark.get_solver_info()
    for solver_name, info in solver_info.items():
        print(f"\n{solver_name}:")
        print(f"  Available: {info['available']}")
        print(f"  Category: {info.get('category', 'unknown')}")
        if 'algorithm' in info:
            print(f"  Algorithm: {info['algorithm']}")
        if 'best_for' in info:
            print(f"  Best for: {info['best_for']}")

def demo_export(benchmark):
    """Demonstrate exporting results"""
    print("\n7. Exporting results...")

    # to JSON
    json_file = "benchmark_results.json"
    benchmark.export_results(json_file, include_instances=True)
    print(f"Results exported to {json_file}")

    # to CSV
    try:
        from vrp_benchmark.core.utils import export_solution_to_csv
        csv_file = "benchmark_results.csv"
        export_solution_to_csv(benchmark.results, csv_file)
        print(f"Results exported to {csv_file}")
    except Exception as e:
        print(f"CSV export failed: {e}")

def demo_custom_problem():
    """Demonstrate custom problem creation"""
    print("\n7. Creating custom problem...")

    from vrp_benchmark import VRPInstance, Location, Vehicle, create_distance_matrix

    # Simple 4-customer problem
    locations = [
        Location(id=0, x=0, y=0, demand=0),      # Depot
        Location(id=1, x=10, y=0, demand=10),    # Customer 1
        Location(id=2, x=20, y=0, demand=15),    # Customer 2
        Location(id=3, x=10, y=10, demand=12),   # Customer 3
        Location(id=4, x=0, y=10, demand=8),     # Customer 4
    ]

    vehicles = [Vehicle(id=0, capacity=30), Vehicle(id=1, capacity=30)]

    custom_instance = VRPInstance(
        name="custom_demo",
        locations=locations,
        vehicles=vehicles,
        distance_matrix=create_distance_matrix(locations),
        problem_type="CVRP"
    )

    print(f"Created custom instance:")
    print(f"  Customers: {custom_instance.get_num_customers()}")
    print(f"  Total demand: {custom_instance.get_total_demand()}")
    print(f"  Total capacity: {sum(v.capacity for v in vehicles)}")

    # Quick solve
    benchmark = VRPBenchmark()
    benchmark.load_instance(custom_instance)

    if benchmark.get_available_solvers():
        print("  Testing with available solvers...")
        results = benchmark.benchmark("custom_demo", time_limit=10)

        for solver_name, solution in results.items():
            if solution.status != "ERROR":
                print(f"    ✅ {solver_name}: {solution.total_distance:.2f}")
            else:
                print(f"    ❌ {solver_name}: Failed")


def main():
    """Main demo function"""
    setup_logging()

    try:
        print("🚀 Starting VRP Benchmarking API Demo")

        benchmark = demo_basic_usage()
        if benchmark is None:
            return

        solutions = demo_individual_solving(benchmark)
        benchmark_results = demo_benchmarking(benchmark)
        demo_comparison_analysis(benchmark, benchmark_results)
        demo_solver_info(benchmark)
        demo_export(benchmark)
        demo_custom_problem()

        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("\nGenerated files:")
        print("  - benchmark_results.json (detailed results)")
        print("  - benchmark_results.csv (summary data)")
        print("  - vrp_benchmark.log (execution log)")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logging.error(f"Demo failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()
