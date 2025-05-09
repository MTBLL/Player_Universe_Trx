# Player Universe Transformer
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/MTBLL/Player_Universe_Trx/graph/badge.svg?token=9EE4ZWL41W)](https://codecov.io/gh/MTBLL/Player_Universe_Trx)

## Overview

As part of the MTBL ETL pipeline, this module serves to transform player data from the ESPN universe as well as the FanGraphs universe. The data in this step will be cleaned, normalized, and merged together to get a single Pydantic player object. The output from this step will be a JSON file of serialized Pydantic objects, that will be used in the next step to load into a PostgreSQL database.

## Features

- Transforms player data from ESPN sources
- Transforms player data from FanGraphs sources
- Merges and normalizes data into a unified player model
- Handles player projections data separately
- Outputs serialized Pydantic objects in JSON format

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone the repository
git clone <repository-url>
cd Player_Universe_Trx

# Install dependencies
uv sync
```

## Usage

```python
from player_universe_trx.main import transform_player_data
from player_universe_trx.models.player import PlayerModel

# Transform and output player data
transform_player_data(espn_source_path, fangraphs_source_path, output_path)

# Merge ESPN and FanGraphs data for a player
espn_player = PlayerModel.model_validate(espn_data)
espn_player.merge_fangraphs_data(fangraphs_data)
```

## Development

### Setup

```bash
# Install dev dependencies
uv sync"

# Run tests
uv run pytest
```

### Project Structure

```
player_universe_trx/
   __init__.py          # Package initialization
   main.py              # Main entry point
   models/              # Pydantic data models
      player.py         # Player model definition
   projections/         # Projections handling modules
      __init__.py
      manager.py        # Manages player projections data
   transformers/        # Data transformation modules
       __init__.py
       espn_universe_trx.py  # ESPN data transformer
       fangraphs_trx.py      # FanGraphs data transformer
```

## Testing

```bash
# Run all tests
uv run pytest

# Run a specific test
uv run pytest tests/test_player_model_merge.py -v

# Run with coverage
uv run pytest --cov=player_universe_trx
```

### Testing Framework

This project uses pytest for testing with the following features:

- **Centralized Fixtures**: All test fixtures are defined in `tests/conftest.py` and available to all test files
- **Real Data Testing**: Tests use real data samples from fixtures in `tests/fixtures/`
- **Parameterized Tests**: Uses pytest's parameterization to test multiple scenarios with the same test function
- **Specific Player Testing**: Special fixtures for specific players like Corbin Carroll to ensure consistency

```python
# Example of using fixtures in tests
def test_merge_fangraphs_data_corbin_carroll(corbin_carroll_espn, corbin_carroll_fangraphs):
    # Create player model from ESPN data
    player = PlayerModel.model_validate(corbin_carroll_espn)

    # Merge FanGraphs data
    player.merge_fangraphs_data(corbin_carroll_fangraphs)

    # Assertions
    assert player.id_fangraphs == corbin_carroll_fangraphs["playerid"]
```

## Player Model Features

The PlayerModel class provides the following capabilities:

- Creation from ESPN JSON data
- Merging with FanGraphs data via `merge_fangraphs_data()` method
- Handling non-ASCII player names
- Converting to dictionaries suitable for database storage

### Merging FanGraphs Data

```python
# After creating a player from ESPN data
player = PlayerModel.model_validate(espn_data)

# Merge FanGraphs data
player.merge_fangraphs_data(fangraphs_data)

# Now the player has IDs from both sources
print(f"ESPN ID: {player.id_espn}")
print(f"FanGraphs ID: {player.id_fangraphs}")
print(f"MLB ID: {player.id_xmlbam}")
```

## License

[License information]
