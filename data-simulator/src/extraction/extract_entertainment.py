#!/usr/bin/env python3
"""
Extract entertainment venues from Toulouse OSM data.

This script processes the OSM PBF file to extract entertainment venues
like cinemas, theaters, music venues, arts centers, community centers,
and event venues, then exports them to GeoJSON format.
"""

import logging
import os
import sys
import time
import os
import json
from pathlib import Path

# Add src to Python path
script_dir = Path(__file__).parent
src_dir = script_dir / "src"
sys.path.insert(0, str(src_dir))

from extraction.extractors.toulouse_entertainment_extractor import (
    ToulouseEntertainmentExtractor,
)


os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)


def main():
    """Main extraction function."""
    # Configure logging
    log_path = os.path.join(
        os.path.dirname(__file__), "data/entertainment_extraction.log"
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
    logger.info("Starting Toulouse entertainment venues extraction")

    # Path to OSM PBF file
    pbf_file = Path("data/midi-pyrenees-latest.osm.pbf")
    if not pbf_file.exists():
        logger.error(f"PBF file not found: {pbf_file}")
        logger.info(
            "Please download the file from: http://download.geofabrik.de/europe/france/midi-pyrenees-latest.osm.pbf"
        )
        sys.exit(1)

    # Initialize extractor
    extractor = ToulouseEntertainmentExtractor()

    # Process the PBF file
    start_time = time.time()
    logger.info(f"Processing PBF file: {pbf_file}")

    try:
        extractor.apply_file(str(pbf_file))
    except Exception as e:
        logger.error(f"Error processing PBF file: {e}")
        sys.exit(1)

    processing_time = time.time() - start_time

    # Get statistics
    stats = extractor.get_statistics()
    repository = extractor.get_repository()

    # Log results
    logger.info("=" * 60)
    logger.info("ENTERTAINMENT VENUES EXTRACTION COMPLETED")
    logger.info("=" * 60)
    logger.info(f"Processing time: {processing_time:.2f} seconds")
    logger.info(f"Nodes processed: {stats['processed_nodes']:,}")
    logger.info(f"Ways processed: {stats['processed_ways']:,}")
    logger.info(f"Total entertainment venues found: {stats['total_venues']:,}")

    if stats["total_venues"] > 0:
        logger.info("\\nVenue breakdown by type:")
        for venue_type, count in sorted(stats["venue_breakdown"].items()):
            logger.info(f"  {venue_type.replace('_', ' ').title()}: {count:,}")

        # Get geographic bounds
        bounds = repository.get_bounds()
        if bounds:
            logger.info(f"\\nGeographic bounds:")
            logger.info(
                f"  Latitude: {bounds['min_lat']:.6f} to {bounds['max_lat']:.6f}"
            )
            logger.info(
                f"  Longitude: {bounds['min_lon']:.6f} to {bounds['max_lon']:.6f}"
            )

        # Export to GeoJSON
        output_file = Path("data/toulouse_entertainment_venues.geojson")
        logger.info(f"\\nExporting venues to: {output_file}")

        try:
            geojson_data = repository.to_geojson()
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(geojson_data, f, indent=2, ensure_ascii=False)

            logger.info(
                f"Successfully exported {stats['total_venues']:,} venues to {output_file}"
            )

            # Show sample venues
            logger.info("\\nSample entertainment venues:")
            sample_venues = repository.get_all_locations()[:10]
            for venue in sample_venues:
                # Build address from additional_info
                address_parts = []
                if venue.additional_info.get("addr:housenumber"):
                    address_parts.append(venue.additional_info["addr:housenumber"])
                if venue.additional_info.get("addr:street"):
                    address_parts.append(venue.additional_info["addr:street"])
                if venue.additional_info.get("addr:city"):
                    address_parts.append(venue.additional_info["addr:city"])

                address = (
                    " ".join(address_parts)
                    if address_parts
                    else "Address not available"
                )
                logger.info(
                    f"  • {venue.name} ({venue.location_type.value}) - {address}"
                )

        except Exception as e:
            logger.error(f"Error exporting GeoJSON: {e}")
            sys.exit(1)

    else:
        logger.warning("No entertainment venues found!")
        logger.info("This might indicate:")
        logger.info("  - The PBF file doesn't cover Toulouse")
        logger.info("  - The entertainment venue mappings need adjustment")
        logger.info("  - The geographic bounds are incorrect")

    logger.info("\\nExtraction completed successfully!")


if __name__ == "__main__":
    main()
