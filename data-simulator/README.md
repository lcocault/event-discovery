# Data Simulator

A modular Python project to extract OSM data, generate synthetic families, simulate events, and analyze results for urban studies and mobility research.

## Directory Structure

```
data-simulator/
├── src/
│   ├── extraction/         # OSM data extraction scripts and extractors
│   │   ├── extract_churches.py
│   │   ├── extract_educational.py
│   │   ├── extract_entertainment.py
│   │   ├── extract_hospitality.py
│   │   ├── extract_work_places.py
│   │   └── extractors/
│   │       ├── toulouse_church_extractor.py
│   │       ├── toulouse_educational_extractor.py
│   │       ├── toulouse_entertainment_extractor.py
│   │       ├── toulouse_hospitality_extractor.py
│   │       ├── toulouse_work_places_extractor.py
│   │       └── toulouse_base_extractor.py
│   ├── simulation/         # Family and event generation
│   │   ├── main.py
│   │   ├── event_generator.py
│   │   ├── family_generator.py
│   │   ├── location_assigner.py
│   │   └── models/
│   │       ├── family.py
│   │       ├── person.py
│   │       ├── event.py
│   │       ├── location.py
│   │       ├── location_repository.py
│   │       └── __init__.py
│   ├── analysis/           # Event analysis and stats tools
│   │   ├── event_stats.py
│   │   ├── person_church_stats.py
│   │   ├── church_event_count.py
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

Run all extraction scripts to populate the `data/` directory with GeoJSON files:

```bash
python src/extraction/extract_educational.py
python src/extraction/extract_entertainment.py
python src/extraction/extract_hospitality.py
python src/extraction/extract_churches.py
python src/extraction/extract_work_places.py
```

### 2. Generate Families and Events

Generate synthetic families, assign locations, and simulate daily events:

```bash
python src/simulation/main.py
```

Outputs: `data/families.json`, `data/events.parquet`

### 3. Analyze Events

- **Global and Per-Person Event Stats:**

  ```bash
  python src/analysis/event_stats.py --events events.parquet [--person PERSON_ID]
  ```

- **Count Church Events for All:**

  ```bash
  python src/analysis/church_event_count.py
  ```

- **Count Church Events for a Person:**

  ```bash
  python src/analysis/person_church_stats.py
  ```

- **List All Event Locations for a Person:**

  ```bash
  python src/analysis/person_location_categories.py --person PERSON_ID
  ```

- **Draw a Person's Path:**

  ```bash
  python src/analysis/draw_person_path.py
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