
A modular Python project to extract OSM data, generate synthetic families, simulate events, and analyze results for urban studies and mobility research.

## Installation

1. Navigate to the `data-simulator` directory
2. Install the package in development mode:

   ```bash
   pip install -e .
   ```

## Workflow

### 1. Extract OSM Data

Run the unified extraction script to populate the `data/` directory with a single GeoJSON file containing all locations of interest:

# Data Simulator

A modular Python project to extract OSM data, generate synthetic families, simulate positions, and analyze results for urban studies and mobility research.

## Directory Structure

```
data-simulator/
├── src/
│   ├── extraction/         # OSM data extraction scripts and extractors
│   │   ├── extract_locations.py   # Unified extraction script
│   │   └── extractors/
│   │       ├── base_extractor.py
│   │       └── location_extractor.py
│   ├── simulation/         # Family and position generation
│   │   ├── position_generator.py
│   │   ├── family_generator.py
│   │   ├── location_assigner.py
│   │   └── models/
│   │       ├── family.py
│   │       ├── person.py
│   │       ├── position.py
│   │       ├── location.py
│   │       ├── location_repository.py
│   │       └── __init__.py
│   ├── analysis/           # Position analysis and stats tools
│   │   ├── position_stats.py
│   │   ├── person_church_stats.py
│   │   ├── church_position_count.py
│   │   ├── person_location_categories.py
│   │   └── draw_person_path.py
│   └── ...
├── data/                   # Data files (GeoJSON, Parquet, etc.)
├── pyproject.toml
└── README.md
```

## Installation

1. Navigate to the `data-simulator` directory
2. Install the package in development mode:

   ```bash
   pip install -e .
   ```

3. Download the OpenStreetMap data:

   ```bash
   mkdir -p data
   wget https://download.geofabrik.de/europe/france/midi-pyrenees-latest.osm.pbf -O data/midi-pyrenees-latest.osm.pbf
   ```

## Workflow

### 1. Extract OSM Data

Run the unified extraction script to populate the `data/` directory with a single GeoJSON file containing all locations of interest:


**Extract locations (run from the `location/src` directory):**

```bash
cd ../location/src
../../.venv/bin/python -m location.extract_locations
```

- The output file is: `../data/toulouse_locations_of_interest.geojson` (relative to `location/src`)
- Each feature in the GeoJSON includes a `category` property that corresponds to the original kind of extractor (e.g., `church`, `entertainment`, `work`, `hospitality`, `educational`).
- The extraction logic is now unified and maintained in the standalone `location` package.

### 2. Generate Families and Positions

Generate synthetic families, assign locations, and simulate daily positions:


**Generate families and positions (run from the `data-simulator/src` directory):**

```bash
../../.venv/bin/python -m simulation.family_generator
../../.venv/bin/python -m simulation.position_generator
```

Outputs: `data/families.json`, `data/positions.parquet` (relative to `data-simulator/src`)

### 3. Analyze Positions

You can analyze the generated positions with the following tools:

- **List All Position Locations for a Person:**

  ```bash
   ../../.venv/bin/python -m analysis.person_location_categories --person PERSON_ID
  ```

- **Draw a Person's Path:**

  ```bash
   ../../.venv/bin/python -m analysis.draw_person_path
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