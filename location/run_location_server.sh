#!/bin/bash
# Script to run the FastAPI location server

cd "$(dirname "$0")"
cd src
exec uvicorn location.server:app --host 0.0.0.0 --port 3701
