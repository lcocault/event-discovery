#!/bin/bash

# Navigate to the deployment directory
cd $(dirname "$0")

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
if [ -f pyproject.toml ]; then
    pip install . --ignore-requires-python
else
    echo "pyproject.toml not found. Please ensure it is uploaded."
fi

# Deactivate the virtual environment
deactivate

echo "Setup complete. The virtual environment is ready."