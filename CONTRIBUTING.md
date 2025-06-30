````markdown
# Contributing to VRP Benchmarking API

Thank you for your interest in contributing! This project aims to provide a unified platform for VRP algorithm comparison and benchmarking.

## 🚀 Getting Started

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/RostyslavN/vrp_benchmarking.git`
3. **Install** dependencies: `pip install -e .[dev]`
4. **Create** a branch: `git checkout -b feature/your-feature-name`

## 🔧 Development Setup

```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8

# Run tests
python tests/test_basic_functionality.py

# Run code formatting
black vrp_benchmark/
```
````

## 🧪 Testing

- All new features must include tests
- Existing tests must continue to pass
- Aim for good test coverage

## 📝 Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Include comprehensive docstrings
- Run `black` for code formatting

## 🔄 Pull Request Process

1. Update documentation for any new features
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md if applicable
5. Submit pull request with clear description

## 🐛 Reporting Bugs

Use the bug report template when filing issues. Include:

- Clear reproduction steps
- Expected vs actual behavior
- Environment information
- Minimal code example

## 💡 Feature Requests

Use the feature request template. Consider:

- Use case and motivation
- Implementation suggestions
- Impact on existing functionality

## 🔧 Adding New Solvers

1. Inherit from appropriate base class (`VRPSolver`, `ExactSolver`, etc.)
2. Implement required methods (`solve`, `get_solver_name`, `is_available`)
3. Add comprehensive error handling
4. Include validation tests
5. Update documentation

## 📚 Documentation

- Update README.md for user-facing changes
- Add docstrings for all public methods
- Include usage examples
- Update API documentation

## 🏷️ Commit Messages

Use clear, descriptive commit messages:

- `feat: add LKH-3 solver integration`
- `fix: handle empty routes in solution parsing`
- `docs: update installation instructions`
- `test: add validation for custom instances`

## 🎯 Project Goals

Keep these principles in mind:

- **Simplicity**: Easy to use for researchers
- **Extensibility**: Easy to add new solvers
- **Reliability**: Robust error handling
- **Performance**: Minimal overhead
- **Documentation**: Clear and comprehensive

## 📞 Questions?

- Create an issue for general questions
- Use discussions for design questions
- Check existing issues and documentation first

Thank you for contributing to the VRP research community! 🚀

```

```
