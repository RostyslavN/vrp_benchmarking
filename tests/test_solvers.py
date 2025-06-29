#!/usr/bin/env python3
"""
Quick test script to verify both solvers are working correctly.
"""

from vrp_benchmark import VRPBenchmark
import sys
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent
if len(sys.path) == 0 or sys.path[0] != str(current_dir):
    sys.path.insert(0, str(current_dir))


def test_solvers():
    """Test both solvers with a simple problem"""
    print("🧪 Testing VRP Solvers")
    print("=" * 40)

    # Initialize benchmark
    benchmark = VRPBenchmark()
    available_solvers = benchmark.get_available_solvers()

    print(f"Available solvers: {available_solvers}")

    if not available_solvers:
        print("❌ No solvers available!")
        return

    # Create a simple, well-balanced test problem
    print("\n📋 Creating test problem...")
    instance = benchmark.create_sample_instance(
        name="test_problem",
        num_customers=5,        # Small problem
        num_vehicles=2,         # 2 vehicles
        vehicle_capacity=100,   # High capacity
        demand_range=(10, 20),  # Moderate demands
        seed=123                # Fixed seed for reproducibility
    )

    total_demand = sum(loc.demand for loc in instance.locations if loc.id != 0)
    total_capacity = sum(veh.capacity for veh in instance.vehicles)

    print(f"Problem: {instance.get_num_customers()} customers")
    print(f"Total demand: {total_demand}")
    print(f"Total capacity: {total_capacity}")
    print(f"Capacity utilization: {(total_demand/total_capacity)*100:.1f}%")

    # Test each solver individually
    print(f"\n🔍 Testing individual solvers...")
    results = {}

    for solver_name in available_solvers:
        print(f"\nTesting {solver_name}...")
        try:
            solution = benchmark.solve(
                instance_name="test_problem",
                solver_name=solver_name,
                time_limit=10
            )

            if solution.status == "ERROR":
                print(f"  ❌ {solver_name}: {solution.status}")
            else:
                print(f"  ✅ {solver_name}: Distance={solution.total_distance:.2f}, "
                      f"Routes={len(solution.routes)}, Time={solution.solve_time:.3f}s")
                results[solver_name] = solution

        except Exception as e:
            print(f"  ❌ {solver_name}: Exception - {e}")

    # Compare results if we have multiple working solvers
    if len(results) > 1:
        print(f"\n📊 Comparison:")
        comparison = benchmark.compare_solutions(results)

        if 'best_solver' in comparison:
            print(
                f"  🏆 Best: {comparison['best_distance']:.2f} by {comparison['best_solver']}")

            if 'gaps' in comparison:
                print("  Performance gaps:")
                for solver, gap in comparison['gaps'].items():
                    print(f"    {solver}: +{gap:.1f}%")

    # Show detailed route information for working solutions
    print(f"\n🗺️  Route Details:")
    for solver_name, solution in results.items():
        print(f"\n{solver_name} routes:")
        for i, route in enumerate(solution.routes):
            customers = [str(loc_id)
                         for loc_id in route.locations if loc_id != 0]
            print(f"  Route {i+1}: 0 → {' → '.join(customers)} → 0")
            print(
                f"    Distance: {route.total_distance:.2f}, Demand: {route.total_demand}")

    # Summary
    working_solvers = len(results)
    total_solvers = len(available_solvers)

    print(f"\n✅ Test Summary:")
    print(f"  Working solvers: {working_solvers}/{total_solvers}")
    print(f"  Success rate: {(working_solvers/total_solvers)*100:.0f}%")

    if working_solvers == total_solvers:
        print("  🎉 All solvers working correctly!")
    elif working_solvers > 0:
        print("  ⚠️  Some solvers have issues")
    else:
        print("  ❌ No solvers working")


if __name__ == "__main__":
    test_solvers()
