#!/usr/bin/env python3
"""
Extract all locations of interest from Toulouse OSM data in a single pass.

This script processes the OSM PBF file to extract churches, educational institutions,
hospitality venues, entertainment venues, and work places, then exports them to GeoJSON format.
The original category is preserved in the GeoJSON properties as 'category'.
"""

import logging
import os
import sys
import time
import json
from pathlib import Path

src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))
from extraction.location_extractor import LocationExtractor

os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)


def main():
    """Main extraction function for all locations of interest."""
    # Configure logging
    log_path = os.path.join(os.path.dirname(__file__), "../../data/locations_extraction.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting unified extraction of locations of interest")

    # Path to OSM PBF file
    pbf_file = Path("data/midi-pyrenees-latest.osm.pbf")
    if not pbf_file.exists():
        logger.error(f"PBF file not found: {pbf_file}")
        logger.info(
            "Please download the file from: http://download.geofabrik.de/europe/france/midi-pyrenees-latest.osm.pbf"
        )
        return 1

    # Initialize location extractor
    extractor = LocationExtractor()

    # Process the PBF file
    start_time = time.time()
    logger.info("Processing OSM PBF file...")

    try:
        extractor.apply_file(str(pbf_file))
        repository = extractor.get_repository()

        processing_time = time.time() - start_time
        logger.info(f"Processing completed in {processing_time:.2f} seconds")

        if not repository.get_all_locations():
            logger.warning("No locations of interest found in Toulouse area")
            return 1

        # Export to GeoJSON (with category in properties)
        output_file = Path("data/toulouse_locations_of_interest.geojson")
        geojson_data = repository.to_geojson()
        # Add 'category' property to each feature
        for feature in geojson_data.get("features", []):
            if "location_type" in feature["properties"]:
                feature["properties"]["category"] = feature["properties"]["location_type"]
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(geojson_data, f, indent=2, ensure_ascii=False)

        # Print summary
        stats = repository.get_statistics()
        logger.info(f"Successfully extracted {stats['total_venues']} locations of interest")
        logger.info("\nBreakdown by category:")
        for category, count in sorted(stats["venue_breakdown"].items()):
            logger.info(f"  {category:<20}: {count:3d}")

        logger.info(f"\n✓ GeoJSON exported to: {output_file}")
        logger.info("✓ Ready for mapping applications")
        logger.info("=" * 60)
        return 0

    except KeyboardInterrupt:
        logger.info("Extraction interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
