#!/usr/bin/env python3
"""
Extract hospitality venues from Toulouse OSM data.

This script processes the OSM PBF file to extract hospitality venues
like bars, cafes, pubs, restaurants, nightclubs, and beer gardens,
then exports them to GeoJSON format.
"""

import logging
import os
import sys
import time
import json
from pathlib import Path

# Add src to Python path
script_dir = Path(__file__).parent
src_dir = script_dir
sys.path.insert(0, str(src_dir))

from extraction.extractors.toulouse_hospitality_extractor import (
    ToulouseHospitalityExtractor,
)


os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)


def main():
    """Main extraction function."""
    # Configure logging
    log_path = os.path.join(
        os.path.dirname(__file__), "data/hospitality_extraction.log"
    )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(),
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting Toulouse hospitality venues extraction")

    # Path to OSM PBF file
    pbf_file = Path("data/midi-pyrenees-latest.osm.pbf")
    if not pbf_file.exists():
        logger.error(f"PBF file not found: {pbf_file}")
        logger.info(
            "Please download the file from: http://download.geofabrik.de/europe/france/midi-pyrenees-latest.osm.pbf"
        )
        return 1

    # Initialize extractor
    extractor = ToulouseHospitalityExtractor()

    # Process the PBF file
    start_time = time.time()
    logger.info("Processing OSM PBF file...")

    try:
        # Extract venues
        extractor.apply_file(str(pbf_file))
        repository = extractor.get_repository()

        processing_time = time.time() - start_time
        logger.info(f"Processing completed in {processing_time:.2f} seconds")

        if not repository.get_all_locations():
            logger.warning("No hospitality venues found in Toulouse area")
            return 1

        # Export to GeoJSON
        output_file = Path("data/toulouse_hospitality_venues.geojson")
        geojson_data = repository.to_geojson()

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(geojson_data, f, indent=2, ensure_ascii=False)

        # Print summary
        stats = repository.get_statistics()
        logger.info(f"Successfully extracted {stats['total']} hospitality venues")

        # Breakdown by type
        venue_type_counts = {}
        for location in repository.get_all_locations():
            venue_type = location.location_type.value
            venue_type_counts[venue_type] = venue_type_counts.get(venue_type, 0) + 1

        logger.info("\n" + "=" * 60)
        logger.info("TOULOUSE HOSPITALITY VENUES EXTRACTION RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total venues: {stats['total']}")

        if venue_type_counts:
            logger.info("\nBreakdown by venue type:")
            type_names = {
                "bar": "Bars",
                "cafe": "Cafés",
                "pub": "Pubs",
                "restaurant": "Restaurants",
                "nightclub": "Nightclubs",
                "biergarten": "Beer Gardens",
            }

            for venue_type, count in sorted(venue_type_counts.items()):
                display_name = type_names.get(venue_type, venue_type.title())
                logger.info(f"  {display_name:<20}: {count:3d}")

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
