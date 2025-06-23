# VRP benchmarking API

A unified Python API for benchmarking Vehicle Routing Problem (VRP) algorithms. The goal of this library is to provide a consistent interface for comparing different VRP solvers including PyVRP, Google OR-Tools and in plans - LKH-3, VRPSolver, OptaPy.

## Installation

### Basic installation

```bash
pip install numpy
```

### Install solvers

```bash
pip install vrp ortools
```

### Development installation

```bash
git clone https://github.com/RostyslavN/vrp_benchmarking
cd vrp-benchmark
pip install -e .[dev]
```

## Quick start

```python
from vrp_benchmark import VRPBenchmark

# Initialize the API
benchmark = VRPBenchmark()
print(f"Available solvers: {benchmark.get_available_solvers()}")

# Create a sample problem
instance = benchmark.create_sample_instance("test", num_customers=10)

# Solve with a specific solver
solution = benchmark.solve("test", "PyVRP", time_limit=30)
solution.print_summary()

# Benchmark multiple solvers
solutions = benchmark.benchmark("test", time_limit=30)
comparison = benchmark.compare_solutions(solutions)

print(f"Best: {comparison['best_distance']:.2f} by {comparison['best_solver']}")
```

## Supported solvers

| Solver        | Type                   | Problems           | License    | Installation          |
| ------------- | ---------------------- | ------------------ | ---------- | --------------------- |
| **PyVRP**     | Metaheuristic          | CVRP, VRPTW        | MIT        | `pip install vrp`     |
| **OR-Tools**  | Constraint Programming | CVRP, VRPTW, MDVRP | Apache 2.0 | `pip install ortools` |
| **LKH-3**     | Exact                  | CVRP, VRPTW        | Academic   | _Coming Soon_         |
| **VRPSolver** | Exact                  | CVRP, VRPTW        | Academic   | _Coming Soon_         |
| **OptaPy**    | Constraint-based       | Custom VRP         | Apache 2.0 | _Coming Soon_         |

## Usage Examples

### Creating custom instances

```python
from vrp_benchmark import VRPInstance, Location, Vehicle, create_distance_matrix

# Define locations
locations = [
    Location(id=0, x=0, y=0, demand=0),      # Depot
    Location(id=1, x=10, y=10, demand=15),   # Customer 1
    Location(id=2, x=20, y=5, demand=12),    # Customer 2
]

# Define vehicles
vehicles = [Vehicle(id=0, capacity=30)]

# Create instance
instance = VRPInstance(
    name="custom",
    locations=locations,
    vehicles=vehicles,
    distance_matrix=create_distance_matrix(locations)
)
```

### Benchmarking multiple instances

```python
# Create test instances
benchmark.create_sample_instance("small", num_customers=10)
benchmark.create_sample_instance("medium", num_customers=20)
benchmark.create_sample_instance("large", num_customers=50)

# Run full benchmark
results = benchmark.run_full_benchmark(
    instances=["small", "medium", "large"],
    time_limit=60
)

# Print report
benchmark.print_benchmark_report(results)
```

### Advanced analysis

```python
# Get detailed statistics
summary = benchmark.get_results_summary()
print(f"Overall success rate: {summary['overall_success_rate']:.1%}")

# Export for analysis
benchmark.export_results("results.json", include_instances=True)

# Validate solution quality
from vrp_benchmark.core.utils import validate_solution_feasibility
is_valid, violations = validate_solution_feasibility(solution, instance)
```

### Adding new solvers

1.  Inherit from `VRPSolver` base class
2.  Implement required methods (`solve`, `get_solver_name`, etc.)
3.  Add solver registration in `__init__.py`
4.  Include tests and documentation

## Running examples

```bash
# Basic usage demonstration
python examples/basic_usage.py

# Custom instance creation
python examples/custom_instance.py

# Comprehensive benchmarking
python examples/benchmark_comparison.py
```
