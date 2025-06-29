#!/usr/bin/env python3
"""
VRP Benchmarking API - Complete Demonstration

This example demonstrates the full capabilities of the VRP benchmarking API:
1. Initialize the benchmark system
2. Create sample VRP instances  
3. Solve with individual algorithms
4. Benchmark multiple solvers
5. Analyze and compare results
6. Export data for further analysis
7. Create custom problem instances

Run with: python examples/basic_usage.py
"""

from vrp_benchmark import (
    VRPBenchmark, VRPInstance, Location, Vehicle, create_distance_matrix
)
import logging
import sys
from pathlib import Path

# Ensure we can import our package
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))


def setup_logging():
    """Configure logging for detailed execution tracking"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('vrp_benchmark.log')
        ]
    )


def demo_initialization():
    """Step 1: Initialize the VRP benchmarking system"""
    print("🚀 VRP Benchmarking API - Live Demonstration")
    print("=" * 60)
    print("\n1. 🔧 Initializing VRP Benchmark System...")

    benchmark = VRPBenchmark()
    available_solvers = benchmark.get_available_solvers()

    print(
        f"✅ System ready with {len(available_solvers)} solvers: {available_solvers}")

    if not available_solvers:
        print("❌ No solvers available! Please install:")
        print("   pip install pyvrp ortools")
        return None

    return benchmark


def demo_instance_creation(benchmark):
    """Step 2: Create diverse VRP problem instances"""
    print("\n2. 📋 Creating VRP problem instances...")

    # Small realistic logistics problem
    small_instance = benchmark.create_sample_instance(
        name="delivery_route",
        num_customers=8,
        num_vehicles=2,
        vehicle_capacity=60,
        demand_range=(5, 15),
        seed=42  # Reproducible results
    )

    total_demand = sum(
        loc.demand for loc in small_instance.locations if loc.id != 0)
    total_capacity = sum(veh.capacity for veh in small_instance.vehicles)
    utilization = (total_demand / total_capacity) * 100

    print(f"📦 Created '{small_instance.name}':")
    print(f"   • {small_instance.get_num_customers()} delivery locations")
    print(f"   • {len(small_instance.vehicles)} delivery trucks")
    print(f"   • Capacity utilization: {utilization:.1f}%")

    # Medium distribution problem
    medium_instance = benchmark.create_sample_instance(
        name="distribution_network",
        num_customers=12,
        num_vehicles=3,
        vehicle_capacity=80,
        demand_range=(10, 25),
        seed=42
    )

    total_demand = sum(
        loc.demand for loc in medium_instance.locations if loc.id != 0)
    total_capacity = sum(veh.capacity for veh in medium_instance.vehicles)
    utilization = (total_demand / total_capacity) * 100

    print(f"🏭 Created '{medium_instance.name}':")
    print(f"   • {medium_instance.get_num_customers()} distribution centers")
    print(f"   • {len(medium_instance.vehicles)} vehicles")
    print(f"   • Capacity utilization: {utilization:.1f}%")

    return benchmark


def demo_individual_solving(benchmark):
    """Step 3: Solve with individual algorithms"""
    print("\n3. 🔍 Testing Individual Solver Performance...")

    available_solvers = benchmark.get_available_solvers()
    instance_name = "delivery_route"
    solutions = {}

    for solver_name in available_solvers:
        print(f"\n   🧮 Solving with {solver_name}...")
        try:
            solution = benchmark.solve(
                instance_name=instance_name,
                solver_name=solver_name,
                time_limit=15
            )
            solutions[solver_name] = solution

            if solution.status == "ERROR":
                print(f"      ❌ Failed: {solution.status}")
            else:
                print(f"      ✅ Success: {solution.total_distance:.2f} units")
                print(
                    f"         Routes: {len(solution.routes)}, Time: {solution.solve_time:.2f}s")

        except Exception as e:
            print(f"      ❌ Exception: {e}")

    return solutions


def demo_algorithmic_comparison(benchmark):
    """Step 4: Compare multiple algorithms on same problem"""
    print("\n4. ⚡ Algorithm Performance Comparison...")

    instance_name = "distribution_network"
    print(f"   📊 Benchmarking on '{instance_name}'...")

    try:
        results = benchmark.benchmark(
            instance_name=instance_name,
            time_limit=20
        )

        print("   📈 Results:")
        for solver_name, solution in results.items():
            if solution.status != "ERROR":
                print(f"      {solver_name:>10}: {solution.total_distance:>8.1f} units "
                      f"({solution.solve_time:>5.2f}s)")
            else:
                print(f"      {solver_name:>10}: FAILED")

        return results

    except Exception as e:
        print(f"   ❌ Benchmark failed: {e}")
        return {}


def demo_performance_analysis(benchmark, solutions):
    """Step 5: Analyze and compare algorithm performance"""
    print("\n5. 📊 Performance Analysis...")

    if not solutions:
        print("   ⚠️  No solutions to analyze")
        return

    comparison = benchmark.compare_solutions(solutions)

    if 'best_solver' in comparison:
        print(f"   🏆 Winner: {comparison['best_solver']}")
        print(f"   🎯 Best distance: {comparison['best_distance']:.2f} units")
        print(
            f"   ✅ Success rate: {comparison['successful_solvers']}/{comparison['total_solvers']} algorithms")

        if 'gaps' in comparison and len(comparison['gaps']) > 1:
            print("   📈 Performance gaps from best:")
            for solver, gap in comparison['gaps'].items():
                if gap > 0:
                    print(f"      {solver:>10}: +{gap:>5.1f}%")
                else:
                    print(f"      {solver:>10}: OPTIMAL")
    else:
        print("   ❌ No valid solutions found")


def demo_solver_capabilities(benchmark):
    """Step 6: Display solver technical information"""
    print("\n6. 🔧 Solver Technical Specifications...")

    solver_info = benchmark.get_solver_info()
    for solver_name, info in solver_info.items():
        print(f"\n   {solver_name}:")
        print(
            f"      Status: {'🟢 Available' if info['available'] else '🔴 Unavailable'}")
        print(f"      Type: {info.get('category', 'unknown').title()}")
        if 'algorithm' in info:
            print(f"      Algorithm: {info['algorithm']}")
        if 'best_for' in info:
            print(f"      Optimal for: {info['best_for']}")
        if 'competition_winner' in info and info['competition_winner']:
            print(f"      🏆 Competition winner")


def demo_data_export(benchmark):
    """Step 7: Export results for further analysis"""
    print("\n7. 💾 Exporting Results...")

    try:
        # Export to JSON (detailed)
        json_file = "benchmark_results.json"
        benchmark.export_results(json_file, include_instances=True)
        print(f"   ✅ Detailed results: {json_file}")

        # Export to CSV (summary)
        try:
            from vrp_benchmark.core.utils import export_solution_to_csv
            csv_file = "benchmark_results.csv"
            export_solution_to_csv(benchmark.results, csv_file)
            print(f"   ✅ Summary data: {csv_file}")
        except ImportError:
            print("   ⚠️  CSV export requires additional setup")

    except Exception as e:
        print(f"   ❌ Export failed: {e}")


def demo_custom_problem():
    """Step 8: Create and solve custom logistics problem"""
    print("\n8. Custom problem creation...")

    print("   📍 Defining a real logistics scenario...")

    # Real-world inspired problem: Food delivery service
    locations = [
        Location(id=0, x=0, y=0, demand=0),        # Restaurant (depot)
        Location(id=1, x=5, y=2, demand=12),       # Office building
        Location(id=2, x=8, y=6, demand=8),        # Residential area
        Location(id=3, x=3, y=7, demand=15),       # Shopping center
        Location(id=4, x=1, y=5, demand=10),       # University campus
        Location(id=5, x=6, y=1, demand=6),        # Hospital
    ]

    vehicles = [
        Vehicle(id=0, capacity=25),  # Delivery bike
        Vehicle(id=1, capacity=35)   # Delivery car
    ]

    custom_instance = VRPInstance(
        name="food_delivery",
        locations=locations,
        vehicles=vehicles,
        distance_matrix=create_distance_matrix(locations),
        problem_type="CVRP"
    )

    print(f"   🍕 Food delivery scenario:")
    print(f"      • {custom_instance.get_num_customers()} delivery locations")
    print(f"      • Total orders: {custom_instance.get_total_demand()} items")
    print(f"      • Fleet capacity: {sum(v.capacity for v in vehicles)} items")

    # Solve the custom problem
    benchmark = VRPBenchmark()
    benchmark.load_instance(custom_instance)

    if benchmark.get_available_solvers():
        print("   🚚 Optimizing delivery routes...")
        results = benchmark.benchmark("food_delivery", time_limit=10)

        for solver_name, solution in results.items():
            if solution.status != "ERROR":
                print(f"      {solver_name}: {solution.total_distance:.1f} km "
                      f"({len(solution.routes)} routes)")
                # Show actual routes
                for i, route in enumerate(solution.routes):
                    customers = route.get_customer_sequence()
                    if customers:
                        route_str = " → ".join([f"Loc{c}" for c in customers])
                        print(
                            f"         Route {i+1}: Restaurant → {route_str} → Restaurant")
            else:
                print(f"      {solver_name}: Optimization failed")


def demo_summary():
    """Final summary of capabilities demonstrated"""
    print("\n" + "=" * 60)
    print("✅ VRP benchmarking API demo complete!")
    print("=" * 60)
    print("\n🎯 Capabilities:")
    print("   ✓ Multi-algorithm VRP solving")
    print("   ✓ Performance benchmarking & comparison")
    print("   ✓ Custom problem modeling")
    print("   ✓ Data export for analysis")
    print("   ✓ Professional error handling")
    print("   ✓ Extensible architecture")

    print("\n📁 Generated files:")
    print("   • benchmark_results.json (detailed results)")
    print("   • benchmark_results.csv (summary data)")
    print("   • vrp_benchmark.log (execution log)")

    print("\n🔬 Perfect for operations research:")
    print("   • Algorithm comparison studies")
    print("   • Logistics optimization")
    print("   • Academic research")
    print("   • Industry applications")
    print("=" * 60)


def main():
    """Main demonstration orchestrator"""
    setup_logging()

    try:
        # Run complete demonstration
        benchmark = demo_initialization()
        if benchmark is None:
            return

        benchmark = demo_instance_creation(benchmark)
        solutions = demo_individual_solving(benchmark)
        comparison_results = demo_algorithmic_comparison(benchmark)
        demo_performance_analysis(benchmark, comparison_results)
        demo_solver_capabilities(benchmark)
        demo_data_export(benchmark)
        demo_custom_problem()
        demo_summary()

    except KeyboardInterrupt:
        print("\n⏹️  Demonstration interrupted")
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        logging.error(f"Demo error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
