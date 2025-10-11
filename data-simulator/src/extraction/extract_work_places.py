#!/usr/bin/env python3
"""
Extract work places (shop/office) from Toulouse OSM data.

This script processes the OSM PBF file to extract all objects with 'shop' or 'office' tags,
then exports them to GeoJSON format.
"""

import logging
import sys
import time
import json
from pathlib import Path

# Add src to Python path
script_dir = Path(__file__).parent
src_dir = script_dir
sys.path.insert(0, str(src_dir))

from extraction.extractors.toulouse_work_places_extractor import (
    ToulouseWorkPlaceExtractor,
)


def main():
    """Main extraction function."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("data/work_places_extraction.log"),
            logging.StreamHandler(),
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting Toulouse work places extraction")

    # Path to OSM PBF file
    pbf_file = Path("data/midi-pyrenees-latest.osm.pbf")
    if not pbf_file.exists():
        logger.error(f"PBF file not found: {pbf_file}")
        logger.info(
            "Please download the file from: http://download.geofabrik.de/europe/france/midi-pyrenees-latest.osm.pbf"
        )
        return 1

    # Initialize extractor
    extractor = ToulouseWorkPlaceExtractor()

    # Process the PBF file
    start_time = time.time()
    logger.info("Processing OSM PBF file...")

    try:
        # Extract work places
        extractor.apply_file(str(pbf_file))
        repository = extractor.repository

        processing_time = time.time() - start_time
        logger.info(f"Processing completed in {processing_time:.2f} seconds")

        if not repository.get_all_locations():
            logger.warning("No work places found in Toulouse area")
            return 1

        # Export to GeoJSON
        output_file = Path("data/toulouse_work_places.geojson")

        geojson_data = repository.to_geojson()
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(geojson_data, f, indent=2, ensure_ascii=False)

        # Print summary
        stats = repository.get_statistics()
        logger.info(f"Successfully extracted {stats['total']} work places")
        logger.info("\n" + "=" * 60)
        logger.info("TOULOUSE WORK PLACES EXTRACTION RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total work places: {stats['total']}")
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
