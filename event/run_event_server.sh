#!/bin/bash
# Script to run the FastAPI location server

# Stop the previous instance of the server if it exists
SERVER_PID=$(lsof -ti:3702)
if [ -n "$SERVER_PID" ]; then
  echo "Stopping existing server instance..."
  kill -9 $SERVER_PID
fi

cd "$(dirname "$0")"
cd src
# Ensure PYTHONPATH includes src and src/api for stubs import
export PYTHONPATH="$(pwd):$(pwd)/api:$PYTHONPATH"
exec uvicorn event.server:app --host 0.0.0.0 --port 3702
