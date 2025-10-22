#!/bin/bash
# Script to run the FastAPI location server

cd "$(dirname "$0")"
cd src
# Ensure PYTHONPATH includes src and src/api for stubs import
export PYTHONPATH="$(pwd):$(pwd)/api:$PYTHONPATH"
exec uvicorn event.server:app --host 0.0.0.0 --port 2702
