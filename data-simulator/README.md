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
3. Download the OpenStreetMap data:
   ```bash
   mkdir -p data
   wget https://download.geofabrik.de/europe/france/midi-pyrenees-latest.osm.pbf -O data/midi-pyrenees-latest.osm.pbf
   ```
4. Extract data from OpenStreetMap to support simulation process:
   ```bash
   cd src
   python3 extract_educational.py
   python3 extract_entertainment.py
   python3 extract_hospitality.py
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