#!/bin/bash

# Stop the previous instance of the WUI if it exists
WUI_PID=$(lsof -ti:3000) # Assuming the WUI runs on port 3000
if [ -n "$WUI_PID" ]; then
  echo "Stopping existing WUI instance..."
  kill -9 $WUI_PID
fi

bun run start