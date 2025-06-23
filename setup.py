"""
Setup script for VRP Benchmarking API.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = "VRP Benchmarking API - A unified interface for Vehicle Routing Problem solvers"

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, 'r') as f:
        requirements = [line.strip() for line in f if line.strip()
                        and not line.startswith('#')]
else:
    requirements = ['numpy>=1.20.0']

setup(
    name="vrp-benchmark",
    version="0.1.0",
    description="A unified Python API for benchmarking Vehicle Routing Problem algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rostyslav Novak",
    author_email="novak.rostyslav@gmail.com",
    url="https://github.com/RostyslavN/vrp_benchmarking",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy>=1.20.0',
    ],
    extras_require={
        'pyvrp': ['vrp>=0.4.0'],
        'ortools': ['ortools>=9.0.0'],
        'all': ['vrp>=0.4.0', 'ortools>=9.0.0'],
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0'
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="vrp vehicle routing optimization benchmark solver",
    project_urls={
        "Bug Reports": "https://github.com/RostyslavN/vrp_benchmarking/issues",
        "Documentation": "https://github.com/RostyslavN/vrp_benchmarking/tree/main/docs",
        "Source": "https://github.com/RostyslavN/vrp_benchmarking",
    },
    entry_points={
        'console_scripts': [
            'vrp-benchmark=vrp_benchmark.cli:main',  # Future CLI interface
        ],
    },
)
