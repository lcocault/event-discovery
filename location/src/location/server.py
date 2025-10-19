"""Set up the FastAPI application and mount the Location endpoints."""

from __future__ import annotations

from location.location_dispatcher import LocationDispatcher
from location.location_repository import LocationRepository
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.stubs.location.main import location, initialize_location_dispatcher

# Start the FastAPI application.
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create the repository and load locations from the GeoJSON file
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

repository = LocationRepository()
geojson_path = "../data/locations_of_interest.geojson"
try:
    repository.add_locations_from_geojson(geojson_path)
    logger.info(f"Loaded {len(repository._locations)} locations from {geojson_path}")
except Exception as e:
    logger.warning(f"Could not load locations from {geojson_path}: {e}")

dispatcher = LocationDispatcher(repository)

# Bind the repositories to the FastAPI app via dispatchers.
initialize_location_dispatcher(dispatcher)

# Mount the metdata endpoint.
app.mount("", location)

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=2701)  # noqa: S104
