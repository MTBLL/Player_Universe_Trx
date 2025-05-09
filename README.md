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
- Matches players between data sources with an intelligent, state-aware algorithm:
  - Prevents duplicate matches for players with common last names
  - Strategically processes players in optimal order
  - Handles international names and accented characters
- Resolves team code differences between data sources
- Outputs serialized Pydantic objects in JSON format
- Provides detailed reporting on matching results

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

### From the Command Line

```bash
# Run the main transformation pipeline
python -m player_universe_trx.main

# Run with custom file paths
python -m player_universe_trx.main --espn-file /path/to/espn.json --fangraphs-file /path/to/fangraphs.json --output-dir /path/to/output
```

### As a Python Module

```python
from player_universe_trx.main import main
from player_universe_trx.models.player import PlayerModel
from player_universe_trx.matchers.player_matcher import PlayerMatcher, match_player_models_on_fangraphs_data
from player_universe_trx.utils.file_utils import load_json_data
from player_universe_trx.utils.model_utils import create_player_models

# Run the full transformation pipeline
result = main(espn_file="/path/to/espn.json", 
              fangraphs_file="/path/to/fangraphs.json",
              output_dir="/path/to/output")

# Or perform steps individually
# 1. Load data
espn_data = load_json_data("/path/to/espn.json")
fangraphs_data = load_json_data("/path/to/fangraphs.json")

# 2. Create player models
player_models = create_player_models(espn_data)

# 3. Match players using the function interface (recommended for most cases)
matching_result = match_player_models_on_fangraphs_data(player_models, fangraphs_data)
matched_players = matching_result["matched"]

# Or use the class interface for more control
matcher = PlayerMatcher(player_models, fangraphs_data)
matcher_result = matcher.match_players()
```

## Development

### Setup

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest
```

### Project Structure

```
player_universe_trx/
   __init__.py          # Package initialization
   main.py              # Main entry point
   matchers/            # Player matching algorithms
      __init__.py
      player_matcher.py # Player matching between data sources
   models/              # Pydantic data models
      player.py         # Player model definition
   projections/         # Projections handling modules
      __init__.py
      manager.py        # Manages player projections data
   transformers/        # Data transformation modules
       __init__.py
       espn_universe_trx.py  # ESPN data transformer
       fangraphs_trx.py      # FanGraphs data transformer
   utils/               # Utility functions
       __init__.py
       constants.py     # Constants used throughout the app
       file_utils.py    # Functions for file operations
       model_utils.py   # Utility functions for models
       output_utils.py  # Functions for saving output
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

## Player Matching System

The `PlayerMatcher` class in `player_matcher.py` provides sophisticated matching between ESPN and FanGraphs player data with state management and optimized performance.

### Features

- **Class-Based State Management**: Efficiently tracks already matched players to prevent duplicates
  - Prevents players with common last names from being matched multiple times
  - Maintains a set of matched FanGraphs IDs for quick lookups
  - Important for players like "Gary Sanchez" who could otherwise match with multiple "Sanchez" players

- **Strategic Processing Order**: Processes players in a priority order for optimal results
  1. Special players with known common last names (e.g., "Gary Sanchez", "Jose Ramirez")
  2. Active players on teams (most likely to have accurate data)
  3. Inactive players on teams
  4. Players without team information

- **Tiered Matching Approach**: Uses a series of progressively more relaxed matching criteria:
  1. Exact last name + exact first name match
  2. Exact last name + prefix first name match (e.g., "Mike" matches "Michael")
  3. Last name + team match

- **International Name Support**: Handles accented characters in player names:
  - Properly matches names with accents (e.g., "Suárez") to their ASCII equivalents ("Suarez")
  - Uses the `ascii_name` field from FanGraphs data for consistent matching

- **Team Code Mapping**: Converts between different team abbreviation formats:
  ```python
  # Sample of team code mapping
  ESPN_TO_FG_TEAM_MAPPING = {
      "KC": "KCR",  # Kansas City Royals
      "SD": "SDP",  # San Diego Padres
      "TB": "TBR",  # Tampa Bay Rays
      "SF": "SFG",  # San Francisco Giants
  }
  ```

- **Name Suffix Handling**: Correctly extracts names with suffixes like Jr., Sr., III, IV, etc.

### Example Usage - Function Interface

For compatibility, a function-based interface is still provided:

```python
from player_universe_trx.matchers.player_matcher import match_player_models_on_fangraphs_data
from player_universe_trx.models.player import PlayerModel

# Load player models and FanGraphs data
player_models = [...]  # List of PlayerModel instances
fangraphs_data = [...]  # List of FanGraphs player data dictionaries

# Match players
result = match_player_models_on_fangraphs_data(player_models, fangraphs_data)

# Access results
matched_players = result["matched"]
unmatched_players = result["no_matches"]
ambiguous_matches = result["multiple_matches"]
```

### Example Usage - Class Interface

For more control, you can use the class interface directly:

```python
from player_universe_trx.matchers.player_matcher import PlayerMatcher
from player_universe_trx.models.player import PlayerModel

# Load player models and FanGraphs data
player_models = [...]  # List of PlayerModel instances
fangraphs_data = [...]  # List of FanGraphs player data dictionaries

# Create matcher instance
matcher = PlayerMatcher(player_models, fangraphs_data)

# Match players
result = matcher.match_players()

# Access results
matched_players = result["matched"]
unmatched_players = result["no_matches"]
ambiguous_matches = result["multiple_matches"]

# Advanced: Access internal matcher state
matched_fg_ids = matcher.matched_fg_ids  # Set of matched FanGraphs player IDs
```

## License

[License information]
