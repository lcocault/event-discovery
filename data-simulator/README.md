# Data Simulator

A Python project to simulate family data generation.

## Features

- Generate 1000 families with unique identifiers
- Each family is represented as a Python class instance

## Installation

1. Navigate to the data-simulator directory
2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Usage

Run the main program to generate families:
```bash
python src/main.py
```

## Development

Install development dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

Format code:
```bash
black src/
isort src/
```