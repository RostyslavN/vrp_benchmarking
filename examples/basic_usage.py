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

from vrp_benchmark import (
    VRPBenchmark, create_sample_instance, create_clustered_instance
)
import logging
import sys
from pathlib import Path

# Add the parent directory to path so we can import vrp_benchmark
sys.path.insert(0, str(Path(__file__).parent.parent))


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
        print("  pip install vrp ortools")
        return

    # Create sample instances
    print("\n2. Creating sample VRP instances...")

    # Small instance for quick testing
    small_instance = benchmark.create_sample_instance(
        name="small_test",
        num_customers=8,
        num_vehicles=2,
        vehicle_capacity=40
    )
    print(
        f"Created '{small_instance.name}' with {small_instance.get_num_customers()} customers")

    # Medium instance for comparison
    medium_instance = benchmark.create_sample_instance(
        name="medium_test",
        num_customers=15,
        num_vehicles=3,
        vehicle_capacity=50
    )
    print(
        f"Created '{medium_instance.name}' with {medium_instance.get_num_customers()} customers")

    # Clustered instance
    clustered_instance = create_clustered_instance(
        name="clustered_test",
        num_customers=12,
        num_clusters=3
    )
    benchmark.load_instance(clustered_instance)
    print(
        f"Created '{clustered_instance.name}' with {clustered_instance.get_num_customers()} customers in clusters")

    return benchmark


def demo_individual_solving(benchmark):
    """Demonstrate solving with individual solvers"""
    print("\n3. Solving with individual solvers...")

    available_solvers = benchmark.get_available_solvers()
    instance_name = "small_test"

    solutions = {}
    for solver_name in available_solvers:
        print(f"\nSolving with {solver_name}...")
        try:
            solution = benchmark.solve(
                instance_name=instance_name,
                solver_name=solver_name,
                time_limit=10  # 10 seconds
            )
            solutions[solver_name] = solution
            solution.print_summary()

        except Exception as e:
            print(f"Failed to solve with {solver_name}: {e}")

    return solutions


def demo_benchmarking(benchmark):
    """Demonstrate benchmarking multiple solvers"""
    print("\n4. Running comprehensive benchmark...")

    # Benchmark all instances with all solvers
    instances = ["small_test", "medium_test", "clustered_test"]
    results = {}

    for instance_name in instances:
        print(f"\nBenchmarking instance: {instance_name}")
        try:
            instance_results = benchmark.benchmark(
                instance_name=instance_name,
                time_limit=15  # seconds
            )
            results[instance_name] = instance_results

            # Show quick summary
            for solver_name, solution in instance_results.items():
                status = "✓" if solution.status != "ERROR" else "✗"
                print(f"  {status} {solver_name}: {solution.total_distance:.2f} "
                      f"({solution.solve_time:.2f}s)")

        except Exception as e:
            print(f"Failed to benchmark {instance_name}: {e}")

    return results


def demo_analysis(benchmark, results):
    """Demonstrate solution analysis and comparison"""
    print("\n5. Analyzing results...")

    # Analyze each instance
    for instance_name, instance_results in results.items():
        print(f"\nAnalysis for {instance_name}:")

        comparison = benchmark.compare_solutions(instance_results)

        if 'best_solver' in comparison:
            print(
                f"  Best solution: {comparison['best_distance']:.2f} by {comparison['best_solver']}")
            print(f"  Average distance: {comparison['avg_distance']:.2f}")
            print(
                f"  Successful solvers: {comparison['successful_solvers']}/{comparison['total_solvers']}")

            # Show solver comparison
            if 'gaps' in comparison:
                print("  Performance gaps:")
                for solver, gap in comparison['gaps'].items():
                    print(f"    {solver}: +{gap:.1f}%")
        else:
            print("  No valid solutions found")

    # Overall summary
    print(f"\n6. Overall Summary:")
    summary = benchmark.get_results_summary()
    print(f"  Total runs: {summary['total_results']}")
    print(f"  Success rate: {summary['overall_success_rate']:.1%}")
    print(f"  Unique instances: {summary['unique_instances']}")
    print(f"  Unique solvers: {summary['unique_solvers']}")

    # Solver statistics
    print("\nSolver Performance:")
    for solver_name, stats in summary['solver_statistics'].items():
        print(f"  {solver_name}:")
        print(f"    Success rate: {stats['success_rate']:.1%}")
        if stats['success_rate'] > 0:
            print(f"    Avg distance: {stats['avg_distance']:.2f}")
            print(f"    Avg time: {stats['avg_solve_time']:.2f}s")


def demo_export(benchmark):
    """Demonstrate exporting results"""
    print("\n7. Exporting results...")

    # Export to JSON
    json_file = "benchmark_results.json"
    benchmark.export_results(json_file, include_instances=True)
    print(f"Results exported to {json_file}")

    # Export to CSV (using utility function)
    try:
        from vrp_benchmark.core.utils import export_solution_to_csv
        csv_file = "benchmark_results.csv"
        export_solution_to_csv(benchmark.results, csv_file)
        print(f"Results exported to {csv_file}")
    except Exception as e:
        print(f"CSV export failed: {e}")


def demo_custom_instance():
    """Demonstrate creating custom instances"""
    print("\n8. Creating custom instance...")

    from vrp_benchmark import VRPInstance, Location, Vehicle, create_distance_matrix

    # Define custom locations
    locations = [
        Location(id=0, x=0, y=0, demand=0),      # Depot
        Location(id=1, x=10, y=0, demand=15),    # Customer 1
        Location(id=2, x=20, y=10, demand=10),   # Customer 2
        Location(id=3, x=10, y=20, demand=12),   # Customer 3
        Location(id=4, x=0, y=10, demand=8),     # Customer 4
    ]

    # Define vehicles
    vehicles = [
        Vehicle(id=0, capacity=25),
        Vehicle(id=1, capacity=25)
    ]

    # Calculate distance matrix
    distance_matrix = create_distance_matrix(locations)

    # Create instance
    custom_instance = VRPInstance(
        name="custom_square",
        locations=locations,
        vehicles=vehicles,
        distance_matrix=distance_matrix,
        problem_type="CVRP"
    )

    print(f"Created custom instance '{custom_instance.name}'")
    print(f"Total demand: {custom_instance.get_total_demand()}")
    print(f"Total capacity: {sum(v.capacity for v in vehicles)}")

    # Test with benchmark
    benchmark = VRPBenchmark()
    benchmark.load_instance(custom_instance)

    if benchmark.get_available_solvers():
        solutions = benchmark.benchmark("custom_square", time_limit=5)
        comparison = benchmark.compare_solutions(solutions)

        if 'best_solver' in comparison:
            print(
                f"Best solution: {comparison['best_distance']:.2f} by {comparison['best_solver']}")

        return custom_instance

    return None


def main():
    """Main demo function"""
    setup_logging()

    try:
        # Run all demos
        benchmark = demo_basic_usage()
        if benchmark is None:
            return

        solutions = demo_individual_solving(benchmark)
        results = demo_benchmarking(benchmark)
        demo_analysis(benchmark, results)
        demo_export(benchmark)
        demo_custom_instance()

        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("Check the generated files:")
        print("  - benchmark_results.json (detailed results)")
        print("  - benchmark_results.csv (summary data)")
        print("  - vrp_benchmark.log (execution log)")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        logging.error(f"Demo failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()
