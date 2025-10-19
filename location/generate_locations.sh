#!/bin/bash
# Generate the locations GeoJSON from OSM PBF
echo "Running unified location extraction..."
python3 -m src.location.extract_locations
