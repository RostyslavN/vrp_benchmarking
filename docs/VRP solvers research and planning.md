# VRP Solver Research and Planning Documentation

## Summary

Here are the findings from the research for developing a Python API to benchmark VRP algorithms. The analysis covers these VRP solvers: LKH-3, PyVRP, Google OR-Tools, VRPSolver, and OptaPy, examining their capabilities, interfaces, data formats, and integration requirements.

## Solver Analysis

### 1. LKH-3 (Lin-Kernighan-Helsgaun)

**Overview:**
- Originally designed for TSP, then extended to handle various VRP variants
- High-performance exact solver, based on the Lin-Kernighan-Helsgaun heuristic

**Supported Problem Types:**
- CVRP (Capacitated VRP)
- ACVRP (Asymmetric Capacitated VRP)
- VRPTW (VRP with Time Windows)
- VRPMPDTW (VRP with Mixed Pickup and Delivery and Time Windows)
- VRPSPD (VRP with Simultaneous Pickup and Delivery)
- VRPSPDTW (VRP with Simultaneous Pickup-Delivery and Time Windows)

**Technical Details:**
- **Language:** C++ (core solver)
- **Input Format:** TSPLIB format with VRP extensions
- **Python Integration:** Available through PyLKH wrapper (PyPI package)

**Integration Considerations:**
- Requires separate installation of LKH-3 binary
- TSPLIB format requires integer distance matrices
- Well-established Python wrapper available
- Strong performance on benchmark datasets

### 2. PyVRP

**Overview:**
- Implements Hybrid Genetic Search
- Designed for high performance with Python

**Supported Problem Types:**
- VRPTW (primary focus)
- Extensible to other VRP variants
- Capacity constraints
- Time window constraints

**Technical Details:**
- **Language:** Python with C++ core
- **Input Format:** Native Python objects and standard formats
- **API:** object-oriented Python interface

**Integration Considerations:**
- Installation via pip
- Has good documentation and examples
- Modern, well-maintained codebase
- Strong community support, active development

### 3. Google OR-Tools

**Overview:**
- Toolkit from Google
- Includes dedicated routing library for VRP problems

**Supported Problem Types:**
- Basic VRP
- CVRP (Capacitated VRP)
- VRPTW (VRP with Time Windows)
- VRP with resource constraints
- Multi-depot VRP
- VRP with pickup and delivery

**Technical Details:**
- **Language:** C++ core with Python, Java, .NET wrappers
- **Input Format:** Programmatic API (distance matrices, constraint definitions)
- **API:** object-oriented interface

**Integration Considerations:**
- Installation via pip
- Has good documentation and examples
- Maintenance and support by Google
- Large community and ecosystem

### 4. VRPSolver

**Overview:**
- Branch-Cut-and-Price based exact solver
- Focused on exact solutions for benchmarking

**Supported Problem Types:**
- CVRP
- VRPTW
- Various VRP extensions
- Specialized for exact solving

**Technical Details:**
- **Language:** C++ with Python interface (VRPSolverEasy)
- **Input Format:** Custom format and Python modeling interface
- **API:** VRPSolverEasy provides simplified Python interface

**Integration Considerations:**
- Not installable via pip, requires specific dependencies
- Excellent for exact benchmarking on smaller instances
- Limited scalability for large problems

### 5. OptaPy

**Overview:**
- Python port of OptaPlanner (Java-based planning engine)
- Part of Red Hat’s optimization suite

**Supported Problem Types:**
- VRP variants through constraint modeling
- Flexible problem definition
- Multi-objective optimization

**Technical Details:**
- **Language:** Python (JPype bridge to Java OptaPlanner)
- **Input Format:** Python domain model definitions
- **API:** Domain-specific language approach

**Integration Considerations:**
- Requires Java runtime environment
- More complex setup
- Powerful for complex constraint scenarios
- Less specialized for pure VRP compared to other solvers

## Data Format Analysis

### Common Input Requirements

1. **Distance/Cost patrix:** All solvers require distance or cost information between locations
2. **Vehicle limits:** Capacity, count, depot information
3. **Location data:** Coordinates, demands, time windows
4. **Problem parameters:** Service times, vehicle costs

### Format Compatibility Matrix

| Solver | TSPLIB | JSON/Python Objects | CSV | Custom Format |
| --- | --- | --- | --- | --- |
| LKH-3 | ✓ (primary) | Via wrapper | ✗ | ✗ |
| PyVRP | ✗ | ✓ (primary) | ✓ | ✓ |
| OR-Tools | ✗ | ✓ (primary) | ✓ | ✓ |
| VRPSolver | ✗ | ✓ (via Easy) | ✗ | ✓ |
| OptaPy | ✗ | ✓ (primary) | ✓ | ✓ |

## API Design

### Project architecture

```
API
├── common (solve_vrp, load_data, get_results)
├── adapters
│   ├── LKH3Adapter (TSPLIB conversion)
│   ├── PyVRPAdapter (native Python)
│   ├── ORToolsAdapter (programmatic setup)
│   ├── VRPSolverAdapter (model conversion)
│   └── OptaPyAdapter (domain model setup)
├── data
│   ├── format converters
│   ├── validators
│   └── cache
└── formatters
    ├── solution extraction
    ├── metrics calculation
    └── comparison tools
```

## Implementation

### Technical Considerations

**Installation:**

- PyVRP: with `pip install`
- OR-Tools: with `pip install`
- OptaPy:  requires Java
- LKH-3: binary compilation + wrapper
- VRPSolver: this one required academic dependencies

## Conclusion

The research indicates that PyVRP and Google OR-Tools are the optimal choices for initial prototype development due to their excellent Python integration, comprehensive documentation, and minimal setup requirements. LKH-3 should be prioritized for the full implementation phase to provide high-performance exact solutions, while VRPSolver can add exact solving capabilities for smaller benchmark instances. OptaPy may be considered for advanced constraint scenarios but has the highest integration complexity.

The unified API should focus on abstracting the differences between solvers while preserving their unique strengths, with automatic format conversion and standardized result reporting being critical components for successful benchmarking.