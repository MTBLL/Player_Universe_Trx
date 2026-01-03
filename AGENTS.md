# Claude Development Guide

This document contains helpful information for Claude when working on this repository.

## Project Overview

This module is part of the MTBL ETL pipeline, transforming player data from ESPN and FanGraphs into normalized Pydantic objects that will be loaded into a PostgreSQL database.

## Development Workflow

1. **Development Commands**:
   ```bash
   # Install dependencies
   uv sync

   # Run tests
   uv run pytest

   # Type check with mypy
   uv run mypy player_universe_trx/

   # Run linting with ruff
   uv run ruff check player_universe_trx/

   # Format code with ruff
   uv run ruff format player_universe_trx/
   ```

2. **Project Structure**:
   - `models/player.py`: Contains the Pydantic model definitions
   - `transformers/`: Contains transformation logic for different data sources
   - `main.py`: Entry point for the transformation pipeline

## Common Tasks

### Working with uv

```bash
# Add a dependency
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# Update dependencies
uv sync

# Run a command
uv run <command>
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run a specific test file
uv run pytest tests/test_specific.py

# Run with verbose output
uv run pytest -v
```

### Formatting and Linting

```bash
# Check typing
uv run mypy player_universe_trx/

# Lint code with ruff
uv run ruff check player_universe_trx/

# Format code with ruff
uv run ruff format player_universe_trx/
```
