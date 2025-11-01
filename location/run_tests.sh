#!/bin/bash

# Dynamically determine the workspace path
WORKSPACE_DIR=$(dirname $(dirname $(realpath $0)))

# Run pytest with uv
PYTHONPATH=$WORKSPACE_DIR/src uv run pytest