#!/bin/bash

set -e

echo "#######################################"
echo "### Build API for Location Services ###"
echo "#######################################"

# Context
export NVM_VERSION=v0.40.2
export SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
export REPO_DIR="$(cd "${SCRIPT_DIR}/../.." &>/dev/null && pwd)"
export TARGET_DIR="${SCRIPT_DIR}/specifications"

# Ensure fastapi-codegen is installed
uv pip install fastapi-code-generator

# Ensure output directory exists
export DOMAIN="location"
mkdir -p ${REPO_DIR}/src/api/stubs/${DOMAIN}

# Generate the FastAPI code for Location API
fastapi-codegen --input ${REPO_DIR}/src/api/specifications/location.yaml \
    --output ${REPO_DIR}/src/api/stubs/${DOMAIN} \
    --generate-routers \
    --output-model-type pydantic_v2.BaseModel \
    --python-version 3.11 \
    --template-dir ${REPO_DIR}/src/api/templates/${DOMAIN} \
    --enum-field-as-literal all
