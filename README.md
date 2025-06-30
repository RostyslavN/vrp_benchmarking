![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

# VRP benchmarking API

A unified Python API for benchmarking Vehicle Routing Problem (VRP) algorithms. This library provides a consistent interface for comparing state-of-the-art VRP solvers including PyVRP, Google OR-Tools, and extensible support for additional algorithms.

## 🚀 Features

- **Unified interface**: Consistent API across all VRP solvers
- **Multiple algorithms**: PyVRP (Hybrid Genetic Search) + OR-Tools (Constraint Programming)
- **Performance benchmarking**: Compare solver performance objectively
- **Custom problem modeling**: Create and solve your own VRP instances
- **Data export**: JSON and CSV export for analysis
- **Professional architecture**: Extensible, well-documented, production-ready
- **Error handling**: Graceful failure management with detailed logging

## Installation

```bash
# Core package (manual installation)
git clone https://github.com/RostyslavN/vrp_benchmarking.git
cd vrp-benchmark
pip install -e .

# Install VRP solvers
pip install pyvrp ortools numpy
```

### Basic Usage

```python
from vrp_benchmark import VRPBenchmark

# Initialize the benchmarking system
benchmark = VRPBenchmark()
print(f"Available solvers: {benchmark.get_available_solvers()}")

# Create a sample logistics problem
instance = benchmark.create_sample_instance("delivery_routes", num_customers=10)

# Solve with multiple algorithms
solutions = benchmark.benchmark("delivery_routes", time_limit=30)

# Compare performance
comparison = benchmark.compare_solutions(solutions)
print(f"Best solution: {comparison['best_distance']:.2f} by {comparison['best_solver']}")

# Export results
benchmark.export_results("results.json")
```

## Demo

```bash
# Run the complete demonstration
python examples/basic_usage.py

# Quick solver test
python tests/test_solvers.py
```

**Expected Output:**

```
🚀 VRP Benchmarking API - Live Demonstration
============================================================
Available solvers: ['PyVRP', 'OR-Tools']

📦 Created 'delivery_route': 8 delivery locations
⚡ Algorithm Performance Comparison...
🏆 Winner: OR-Tools (215.18 units in 0.02s)
✅ All systems operational!
```

## Supported solvers

| Solver        | Algorithm              | Type          | Best For          | Performance        |
| ------------- | ---------------------- | ------------- | ----------------- | ------------------ |
| **PyVRP**     | Hybrid Genetic Search  | Metaheuristic | VRPTW, Research   | Competition winner |
| **OR-Tools**  | Constraint Programming | Heuristic     | Production, Scale | Google-backed      |
| **LKH-3**     | Lin-Kernighan-Helsgaun | Exact         | Optimal Solutions | _Coming soon_      |
| **VRPSolver** | Branch-Cut-Price       | Exact         | Academic Research | _Coming soon_      |

## Problem types supported

- **CVRP**: Capacitated Vehicle Routing Problem
- **VRPTW**: VRP with Time Windows
- **MDVRP**: Multi-Depot VRP
- **Custom**: Define your own constraints

## Architecture

```

vrp_benchmark/
├── models.py # Data structures (VRPInstance, VRPSolution, etc.)
├── solvers/ # Algorithm implementations
│ ├── base.py # Abstract interfaces
│ ├── pyvrp_solver.py # PyVRP integration
│ └── ortools_solver.py # OR-Tools integration
├── core/ # Main API logic
│ ├── benchmark.py # VRPBenchmark class
│ └── utils.py # Helper functions
└── examples/ # Usage demonstrations

```

## Performance Benchmarks

Tested on standard instances:

- **Small Problems** (≤20 customers): Both solvers find optimal solutions
- **Medium Problems** (20-50 customers): Sub-second solving for most instances
- **Large Problems** (50+ customers): Scalable performance with time/quality trade-offs

## Custom Problem Creation

```python
from vrp_benchmark import VRPInstance, Location, Vehicle, create_distance_matrix

# Define your logistics scenario
locations = [
    Location(id=0, x=0, y=0, demand=0),      # Warehouse
    Location(id=1, x=10, y=5, demand=15),    # Customer A
    Location(id=2, x=20, y=10, demand=20),   # Customer B
]

vehicles = [Vehicle(id=0, capacity=50)]  # Delivery truck

# Create and solve
instance = VRPInstance(
    name="my_routes",
    locations=locations,
    vehicles=vehicles,
    distance_matrix=create_distance_matrix(locations)
)

benchmark.load_instance(instance)
solutions = benchmark.benchmark("my_routes")
```

## Requirements

- **Python**: 3.8+
- **Core Dependencies**: NumPy
- **VRP Solvers**: PyVRP, OR-Tools (automatically detected)
- **Optional**: Matplotlib (for visualization - future feature)

## Testing

```bash
# Run functionality tests
python tests/test_solvers.py

# Validate solver integration
python -c "from vrp_benchmark import VRPBenchmark; print('✅ Import successful')"
```

## Documentation

- **API Reference**: See docstrings in source code
- **Examples**: `examples/` directory
- **Other docs**: `docs/` directory

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Add** tests for new functionality
4. **Submit** a pull request

### Adding new solvers

```python
# Inherit from base class
class YourSolver(VRPSolver):
    def solve(self, instance, time_limit=30):
        # Your implementation
        return solution

    def get_solver_name(self):
        return "YourSolver"
```
