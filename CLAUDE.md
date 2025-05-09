# Claude Development Guide

This document contains helpful information for Claude when working on this repository.

## Project Overview

This module is part of the MTBL ETL pipeline, transforming player data from ESPN and FanGraphs into normalized Pydantic objects that will be loaded into a PostgreSQL database.

## Development Workflow

1. **Development Commands**:
   ```bash
   # Install dependencies
   uv pip install -e .

   # Run tests
   python -m pytest

   # Type check with mypy
   python -m mypy player_universe_trx/

   # Run linting with ruff
   python -m ruff check player_universe_trx/

   # Format code with ruff
   python -m ruff format player_universe_trx/
   ```

2. **Project Structure**:
   - `models/player.py`: Contains the Pydantic model definitions
   - `transformers/`: Contains transformation logic for different data sources
   - `main.py`: Entry point for the transformation pipeline

## Common Tasks

### Working with uv

```bash
# Add a dependency
uv pip install <package-name>

# Add a dev dependency
uv pip install --dev <package-name>

# Update dependencies
uv pip sync requirements.txt

# Run a command
python -m <command>
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run a specific test file
python -m pytest tests/test_specific.py

# Run with verbose output
python -m pytest -v
```

### Formatting and Linting

```bash
# Check typing
python -m mypy player_universe_trx/

# Lint code with ruff
python -m ruff check player_universe_trx/

# Format code with ruff
python -m ruff format player_universe_trx/
```