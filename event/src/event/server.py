"""Set up the FastAPI application and mount the Event endpoints."""

from __future__ import annotations

from event.event_dispatcher import EventDispatcher
from event.event_repository import EventRepository
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.stubs.event.main import event, initialize_event_dispatcher

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


# Create repository and dispatcher
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

repository = EventRepository()
dispatcher = EventDispatcher(repository)

# Bind the dispatcher
initialize_event_dispatcher(dispatcher)

# Mount the API
app.mount("", event)

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=2702)  # noqa: S104
