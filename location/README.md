# location

Location definitions and extraction logic for event-discovery.

## Installation

1. Navigate to the `location` directory
2. Install the package in development mode:

   ```bash
   pip install -e .
   ```

3. Download the OpenStreetMap data:

   ```bash
   mkdir -p data
   wget https://download.geofabrik.de/europe/france/midi-pyrenees-latest.osm.pbf -O data/midi-pyrenees-latest.osm.pbf
   ```


## Location Extraction

This package provides unified logic to extract locations of interest from OpenStreetMap (OSM) data.

### Extract OSM Data



Run the unified extraction script as a module from the `src` directory to populate the `../data/` directory with a single GeoJSON file containing all locations of interest:

```bash
cd src
../../.venv/bin/python -m location.extract_locations
```

- The output file is: `../data/locations_of_interest.geojson` (relative to `src`)
- This file is used as input for the family and event generation in the `data-simulator` project.
- Each feature in the GeoJSON includes a `category` property that corresponds to the original kind of extractor (e.g., `church`, `entertainment`, `work`, `hospitality`, `educational`).
- The extraction logic is now unified and maintained in the standalone `location` package.
