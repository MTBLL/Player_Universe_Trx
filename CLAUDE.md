# Claude Development Guide

This document contains helpful information for Claude when working on this repository.

## Project Overview

This module is part of the MTBL ETL pipeline, transforming player data from ESPN and FanGraphs into normalized Pydantic objects that will be loaded into a PostgreSQL database.

## Development Workflow

1. **Development Commands**:
   ```bash
   # Install dependencies
   poetry install

   # Run tests
   poetry run pytest

   # Type check with mypy
   poetry run mypy player_universe_trx/

   # Run linting with ruff
   poetry run ruff check player_universe_trx/

   # Format code with ruff
   poetry run ruff format player_universe_trx/
   ```

2. **Project Structure**:
   - `models/player.py`: Contains the Pydantic model definitions
   - `transformers/`: Contains transformation logic for different data sources
   - `main.py`: Entry point for the transformation pipeline

## Common Tasks

### Working with Poetry

```bash
# Add a dependency
poetry add <package-name>

# Add a dev dependency
poetry add --group dev <package-name>

# Update dependencies
poetry update

# Run a script within the environment
poetry run <command>
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run a specific test file
poetry run pytest tests/test_specific.py

# Run with verbose output
poetry run pytest -v
```

### Formatting and Linting

```bash
# Check typing
poetry run mypy player_universe_trx/

# Lint code with ruff
poetry run ruff check player_universe_trx/

# Format code with ruff
poetry run ruff format player_universe_trx/
```