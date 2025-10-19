# event

Event definitions and extraction logic for event-discovery.

## Installation

1. Navigate to the `event` directory
2. Install the package in development mode:

   ```bash
   pip install -e .
   ```

## Overview

This package mirrors the `location` package and provides:

- Event domain model and repository
- Simple extractor and dispatcher
- Minimal FastAPI server and API stubs

## Development environment (virtualenv)

Recommended: create a local virtual environment inside the `event/` folder and install runtime dependencies.

From the workspace root run:

```bash
cd event
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -e .
```

If `python3 -m venv .venv` hangs during creation on your machine, try one of these workarounds:

- Create a venv without pip and bootstrap pip manually:

```bash
python3 -m venv --without-pip .venv
source .venv/bin/activate
curl -sS https://bootstrap.pypa.io/get-pip.py | python -
pip install -r requirements.txt
```

- Use `virtualenv` if available:

```bash
pip install --user virtualenv
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you prefer Docker or conda, let me know and I can provide instructions.

