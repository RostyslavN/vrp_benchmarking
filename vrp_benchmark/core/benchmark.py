"""
VRP benchmarking API.

Module with primary VRPBenchmark class that coordinates solver registration, instance management, and benchmarking operations.
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..models import VRPInstance, VRPSolution, SolverType
from ..solvers.base import VRPSolver, solver_registry
from ..solvers.pyvrp_solver import PyVRPSolver
from ..solvers.ortools_solver import ORToolsSolver
from .utils import create_sample_instance, calculate_solution_statistics


class VRPBenchmark:
    """
    Main API class for VRP benchmarking.

    This class provides a unified interface for managing VRP solvers,
    problem instances, and benchmarking operations.
    """

    def __init__(self, auto_register: bool = True):
        """
        Initialize the VRP benchmark API.

        Args:
            auto_register: Whether to automatically register available solvers
        """
        self.instances: Dict[str, VRPInstance] = {}
        self.results: List[VRPSolution] = []
        self.logger = logging.getLogger(self.__class__.__name__)

        if auto_register:
            self._auto_register_solvers()

    def _auto_register_solvers(self):
        """Automatically register all available solvers"""
        # Register PyVRP if available
        try:
            pyvrp_solver = PyVRPSolver()
            if pyvrp_solver.is_available():
                solver_registry.register_solver(pyvrp_solver)
        except Exception as e:
            self.logger.warning(f"Failed to register PyVRP: {e}")

        # Register OR-Tools if available
        try:
            ortools_solver = ORToolsSolver()
            if ortools_solver.is_available():
                solver_registry.register_solver(ortools_solver)
        except Exception as e:
            self.logger.warning(f"Failed to register OR-Tools: {e}")

        self.logger.info(
            f"Auto-registered {len(solver_registry.get_available_solvers())} solvers")

    def register_solver(self, solver: VRPSolver, force: bool = False) -> bool:
        """
        Register a VRP solver.

        Args:
            solver: VRP solver instance to register
            force: Whether to override existing solver with same name

        Returns:
            True if registration successful, False otherwise
        """
        return solver_registry.register_solver(solver, force)

    def get_available_solvers(self) -> List[str]:
        """
        Get list of available solver names.

        Returns:
            List of solver name strings
        """
        return solver_registry.get_solver_names()

    def get_solver_info(self, solver_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about solvers.

        Args:
            solver_name: Specific solver name, or None for all solvers

        Returns:
            Dictionary with solver information
        """
        if solver_name:
            solver = solver_registry.get_solver(solver_name)
            if solver:
                return solver.get_solver_info()
            else:
                return {}
        else:
            return {
                name: solver.get_solver_info()
                for name, solver in solver_registry.get_available_solvers().items()
            }

    def load_instance(self, instance: VRPInstance):
        """
        Load a VRP problem instance.

        Args:
            instance: VRP instance to load
        """
        self.instances[instance.name] = instance
        self.logger.info(f"Loaded instance: {instance.name}")

    def load_instance_from_file(self, filepath: str) -> VRPInstance:
        """
        Load VRP instance from JSON file.

        Args:
            filepath: Path to JSON file containing instance data

        Returns:
            Loaded VRP instance
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        instance = VRPInstance.from_dict(data)
        self.load_instance(instance)
        return instance

    def create_sample_instance(self, name: str = "sample",
                               num_customers: int = 10, **kwargs) -> VRPInstance:
        """
        Create a sample VRP instance for testing.

        Args:
            name: Name for the instance
            num_customers: Number of customers to generate
            **kwargs: Additional parameters for instance generation

        Returns:
            Generated VRP instance
        """
        instance = create_sample_instance(name, num_customers, **kwargs)
        self.load_instance(instance)
        return instance

    def get_instance(self, instance_name: str) -> Optional[VRPInstance]:
        """
        Get a loaded instance by name.

        Args:
            instance_name: Name of the instance

        Returns:
            VRP instance or None if not found
        """
        return self.instances.get(instance_name)

    def list_instances(self) -> List[str]:
        """
        Get list of loaded instance names.

        Returns:
            List of instance name strings
        """
        return list(self.instances.keys())

    def solve(self, instance_name: str, solver_name: str,
              time_limit: int = 30, **kwargs) -> VRPSolution:
        """
        Solve a VRP instance with specified solver.

        Args:
            instance_name: Name of the instance to solve
            solver_name: Name of the solver to use
            time_limit: Maximum solving time in seconds
            **kwargs: Additional solver-specific parameters

        Returns:
            VRP solution
        """
        # Validate inputs
        if instance_name not in self.instances:
            raise ValueError(f"Instance '{instance_name}' not found")

        solver = solver_registry.get_solver(solver_name)
        if not solver:
            raise ValueError(f"Solver '{solver_name}' not available")

        instance = self.instances[instance_name]

        # Log solve attempt
        self.logger.info(
            f"Solving '{instance_name}' with {solver.get_solver_name()} "
            f"(time limit: {time_limit}s)"
        )

        # Solve the problem
        solution = solver.solve(instance, time_limit, **kwargs)

        # Store result
        self.results.append(solution)

        # Log result
        self.logger.info(
            f"Solution found: {solution.status}, "
            f"Distance: {solution.total_distance:.2f}, "
            f"Time: {solution.solve_time:.3f}s"
        )

        return solution

    def benchmark(self, instance_name: str, solver_names: Optional[List[str]] = None,
                  time_limit: int = 30, **kwargs) -> Dict[str, VRPSolution]:
        """
        Benchmark multiple solvers on the same instance.

        Args:
            instance_name: name of the instance to solve
            solver_names: list of solver names, or None for all available
            time_limit: max solving time per solver
            **kwargs: additional solver-specific parameters

        Returns:
            Dictionary mapping solver names to solutions
        """
        if solver_names is None:
            solver_names = self.get_available_solvers()

        if instance_name not in self.instances:
            raise ValueError(f"Instance '{instance_name}' not found")

        self.logger.info(
            f"Benchmarking instance '{instance_name}' with "
            f"{len(solver_names)} solvers"
        )

        results = {}
        for solver_name in solver_names:
            try:
                solution = self.solve(
                    instance_name, solver_name, time_limit, **kwargs)
                results[solver_name] = solution
            except Exception as e:
                self.logger.error(f"Failed to solve with {solver_name}: {e}")
                # Create error solution for failed solver
                instance = self.instances[instance_name]
                error_solution = VRPSolution(
                    solver_name=solver_name,
                    instance_name=instance_name,
                    routes=[],
                    total_distance=float('inf'),
                    total_time=0.0,
                    solve_time=0.0,
                    status="ERROR",
                    objective_value=float('inf')
                )
                results[solver_name] = error_solution

        return results

    def compare_solutions(self, solutions: Dict[str, VRPSolution]) -> Dict[str, Any]:
        """
        Compare solutions from different solvers.

        Args:
            solutions: Dictionary mapping solver names to solutions

        Returns:
            Dictionary with comparison statistics
        """
        if not solutions:
            return {}

        # Filter out error solutions for comparison
        valid_solutions = {
            name: sol for name, sol in solutions.items()
            if sol.status != "ERROR" and sol.total_distance != float('inf')
        }

        if not valid_solutions:
            return {
                'error': 'No valid solutions to compare',
                'all_failed': True
            }

        # Find best solution
        best_entry = min(valid_solutions.items(),
                         key=lambda x: x[1].total_distance)
        best_solver, best_solution = best_entry

        # Calculate statistics
        distances = [sol.total_distance for sol in valid_solutions.values()]
        solve_times = [sol.solve_time for sol in valid_solutions.values()]

        comparison = {
            'best_distance': best_solution.total_distance,
            'best_solver': best_solver,
            'worst_distance': max(distances),
            'avg_distance': sum(distances) / len(distances),
            'distance_std': calculate_solution_statistics(distances)['std'],
            'solve_times': {name: sol.solve_time for name, sol in solutions.items()},
            'distances': {name: sol.total_distance for name, sol in solutions.items()},
            'status': {name: sol.status for name, sol in solutions.items()},
            'num_routes': {name: len(sol.routes) for name, sol in solutions.items()},
            'vehicles_used': {name: sol.get_num_vehicles_used() for name, sol in solutions.items()},
            'total_solvers': len(solutions),
            'successful_solvers': len(valid_solutions),
            'failed_solvers': len(solutions) - len(valid_solutions)
        }

        # Add gap analysis
        if len(valid_solutions) > 1:
            comparison['gaps'] = {}
            for name, sol in valid_solutions.items():
                if sol.total_distance > 0:
                    gap = ((sol.total_distance - best_solution.total_distance) /
                           best_solution.total_distance) * 100
                    comparison['gaps'][name] = gap

        return comparison

    def export_results(self, filepath: str, include_instances: bool = False):
        """
        Export results to JSON file.

        Args:
            filepath: Output file path
            include_instances: Whether to include instance data in export
        """
        export_data = {
            'metadata': {
                'export_time': time.time(),
                'num_results': len(self.results),
                'num_instances': len(self.instances),
                'available_solvers': self.get_available_solvers()
            },
            'results': [solution.to_dict() for solution in self.results]
        }

        if include_instances:
            export_data['instances'] = {
                name: instance.to_dict()
                for name, instance in self.instances.items()
            }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)

        self.logger.info(f"Results exported to {filepath}")

    def import_results(self, filepath: str) -> int:
        """
        Import results from JSON file.

        Args:
            filepath: Input file path

        Returns:
            Number of results imported
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        imported_count = 0

        # Import instances if present
        if 'instances' in data:
            for instance_data in data['instances'].values():
                instance = VRPInstance.from_dict(instance_data)
                self.load_instance(instance)

        # Import results
        if 'results' in data:
            for result_data in data['results']:
                solution = VRPSolution.from_dict(result_data)
                self.results.append(solution)
                imported_count += 1

        self.logger.info(f"Imported {imported_count} results from {filepath}")
        return imported_count

    def get_results_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of all results.

        Returns:
            Dictionary with summary statistics
        """
        if not self.results:
            return {'total_results': 0}

        # Group results by solver
        solver_results = {}
        for result in self.results:
            solver_name = result.solver_name
            if solver_name not in solver_results:
                solver_results[solver_name] = []
            solver_results[solver_name].append(result)

        # Calculate statistics per solver
        solver_stats = {}
        for solver_name, results in solver_results.items():
            valid_results = [r for r in results if r.status != "ERROR"]

            if valid_results:
                distances = [r.total_distance for r in valid_results]
                times = [r.solve_time for r in valid_results]

                solver_stats[solver_name] = {
                    'total_runs': len(results),
                    'successful_runs': len(valid_results),
                    'success_rate': len(valid_results) / len(results),
                    'avg_distance': sum(distances) / len(distances),
                    'best_distance': min(distances),
                    'worst_distance': max(distances),
                    'avg_solve_time': sum(times) / len(times),
                    'min_solve_time': min(times),
                    'max_solve_time': max(times)
                }
            else:
                solver_stats[solver_name] = {
                    'total_runs': len(results),
                    'successful_runs': 0,
                    'success_rate': 0.0
                }

        # Overall statistics
        all_valid_results = [r for r in self.results if r.status != "ERROR"]

        summary = {
            'total_results': len(self.results),
            'successful_results': len(all_valid_results),
            'overall_success_rate': len(all_valid_results) / len(self.results) if self.results else 0,
            'unique_instances': len(set(r.instance_name for r in self.results)),
            'unique_solvers': len(set(r.solver_name for r in self.results)),
            'solver_statistics': solver_stats
        }

        return summary

    def clear_results(self):
        """clear all stored results"""
        self.results.clear()
        self.logger.info("Cleared all results")

    def clear_instances(self):
        """clear all loaded instances"""
        self.instances.clear()
        self.logger.info("Cleared all instances")

    def clear_all(self):
        """clear all results and instances"""
        self.clear_results()
        self.clear_instances()

    def run_full_benchmark(self, instances: Optional[List[str]] = None,
                           solvers: Optional[List[str]] = None,
                           time_limit: int = 30) -> Dict[str, Dict[str, VRPSolution]]:
        """
        Run complete benchmark across multiple instances and solvers.

        Args:
            instances: List of instance names, or None for all loaded
            solvers: List of solver names, or None for all available
            time_limit: Time limit per solve

        Returns:
            Nested dictionary: {instance_name: {solver_name: solution}}
        """
        if instances is None:
            instances = self.list_instances()

        if solvers is None:
            solvers = self.get_available_solvers()

        if not instances:
            raise ValueError("No instances available for benchmarking")

        if not solvers:
            raise ValueError("No solvers available for benchmarking")

        self.logger.info(
            f"Running full benchmark: {len(instances)} instances × "
            f"{len(solvers)} solvers = {len(instances) * len(solvers)} total runs"
        )

        results = {}
        total_runs = len(instances) * len(solvers)
        completed_runs = 0

        for instance_name in instances:
            self.logger.info(f"Benchmarking instance: {instance_name}")
            instance_results = self.benchmark(
                instance_name, solvers, time_limit)
            results[instance_name] = instance_results

            completed_runs += len(solvers)
            progress = (completed_runs / total_runs) * 100
            self.logger.info(
                f"Progress: {progress:.1f}% ({completed_runs}/{total_runs})")

        self.logger.info("Full benchmark completed")
        return results

    def print_benchmark_report(self, results: Dict[str, Dict[str, VRPSolution]]):
        """
        Print a formatted benchmark report.

        Args:
            results: Results from run_full_benchmark()
        """
        print("\n" + "="*60)
        print("VRP BENCHMARK REPORT")
        print("="*60)

        if not results:
            print("No results to display.")
            return

        # Print summary table
        print(f"\nInstances: {len(results)}")
        print(f"Solvers: {len(next(iter(results.values())))}")

        # Create summary table
        print(
            f"\n{'Instance':<15} {'Solver':<12} {'Distance':<10} {'Time(s)':<8} {'Status':<10}")
        print("-" * 60)

        for instance_name, instance_results in results.items():
            for solver_name, solution in instance_results.items():
                distance_str = f"{solution.total_distance:.2f}" if solution.total_distance != float(
                    'inf') else "FAILED"
                print(
                    f"{instance_name:<15} {solver_name:<12} {distance_str:<10} {solution.solve_time:<8.3f} {solution.status:<10}")

        # Print best solutions per instance
        print(f"\n{'Best Solutions by Instance:'}")
        print("-" * 40)

        for instance_name, instance_results in results.items():
            valid_results = {k: v for k, v in instance_results.items()
                             if v.status != "ERROR" and v.total_distance != float('inf')}

            if valid_results:
                best_solver, best_solution = min(valid_results.items(),
                                                 key=lambda x: x[1].total_distance)
                print(
                    f"{instance_name}: {best_solution.total_distance:.2f} ({best_solver})")
            else:
                print(f"{instance_name}: No valid solutions found")

        print("\n" + "="*60)
