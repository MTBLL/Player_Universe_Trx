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

# Plan: Implement Savant Data Support

## Overview
Add complete Savant data support following the ESPN/FanGraphs pattern:
1. Add loader methods to `DataLoader` for Savant batters and pitchers
2. Create Savant Pydantic models with nested stats structure
3. Add model creation utilities
4. Create comprehensive tests with 100% coverage

## Savant Data Characteristics

**File Naming Pattern:**
```
savant_batters_{YYYY}_{MM}_{DD}_{HHMM}.json
savant_pitchers_{YYYY}_{MM}_{DD}_{HHMM}.json
```
Example: `savant_batters_2026_01_03_1444.json`

**Data Structure:**
- Flat JSON structure (all fields at root level)
- Will be transformed into nested stats model for consistency with ESPN/FanGraphs
- 39 common fields + 10 batter-specific or 13 pitcher-specific fields

## Implementation Plan

### Part 1: Loader Implementation

**File:** `player_universe_trx/loaders/file_loader.py`

Add two new methods to the `DataLoader` class:

1. `get_savant_batters_file() -> Path`
   - Pattern: `savant_batters_{year}_{timestamp}.json`
   - Timestamp format: `YYYY_MM_DD_HHMM`

2. `get_savant_pitchers_file() -> Path`
   - Pattern: `savant_pitchers_{year}_{timestamp}.json`
   - Timestamp format: `YYYY_MM_DD_HHMM`

3. `load_savant_batters() -> List[Dict]`
   - Calls `get_savant_batters_file()` and loads JSON

4. `load_savant_pitchers() -> List[Dict]`
   - Calls `get_savant_pitchers_file()` and loads JSON

**Update loader docstring** to document Savant file patterns.

### Part 2: Model Architecture

Create 5 models in `player_universe_trx/models/savant/`:

#### 1. SavantPlayerModel (Base Class)
**File:** `player_universe_trx/models/savant/savant_player.py`

**Player Identity Fields:**
```python
player_id: int
name: str              # "Last, First" format
first_name: str
last_name: str
name_ascii: str        # "First Last" format
slug: str
```

**Pitch Count Fields:**
```python
pitches: int
total_pitches: int
pitch_percent: float
```

**Nested Base Stats Model:** `SavantBaseStats` (39 common fields)
- Batting stats: BABIP, BB, BB_pct, BBdist, BIP, ISO, K, K_pct, OBP, SLG
- Contact metrics: adj_exit_velo, exit_velo, launch_angle, percieved_velo
- Plate discipline: swings, takes, whiffs, swing_miss_pct
- Advanced: barrels_total, run_exp, rate_ideal_attack_angle, wOBA, wOBAdiff, xAVG, xAVGdiff, xOBP, xOBPdiff, xSLG, xSLGdiff, xwOBA

#### 2. SavantBatterStatsModel
**File:** `player_universe_trx/models/savant/stats.py`

Inherits `SavantBaseStats` and adds 10 batter-specific fields:
```python
# Swing mechanics
attack_angle: float
attack_dir: float
bat_speed: float
swing_length: float
swing_path_tilt: float

# Performance
pitch_velo: float
barrels_per_bbe_pct: float
barrels_per_pa_pct: float
hardhit_pct: float
batter_run_value_per_100: float
```

#### 3. SavantPitcherStatsModel
**File:** `player_universe_trx/models/savant/stats.py`

Inherits `SavantBaseStats` and adds 13 pitcher-specific fields:
```python
# Pitch characteristics
velo: float
spin_rate: float
eff_min_vel: float

# Release point
release_extension: float
release_pos_x: float
release_pos_z: float

# Movement
break_z: float
induced_break_z: float
break_x_arm_side: float
break_x_batter_in: float

# Mechanics & performance
arm_angle: float
pitcher_run_exp: float
pitcher_run_value_per_100: float
```

#### 4. SavantBatterModel
**File:** `player_universe_trx/models/savant/batter.py`

```python
class SavantBatterModel(SavantPlayerModel):
    stats: Optional[SavantBatterStatsModel] = None
```

#### 5. SavantPitcherModel
**File:** `player_universe_trx/models/savant/pitcher.py`

```python
class SavantPitcherModel(SavantPlayerModel):
    stats: Optional[SavantPitcherStatsModel] = None
```

### Part 3: Model Utilities

**File:** `player_universe_trx/utils/model_utils.py`

Add two functions:

```python
def create_savant_batter_models(batter_data: List[Dict]) -> List[SavantBatterModel]:
    """
    Transform flat Savant batter data into nested SavantBatterModel instances.

    Separates player metadata from stats and creates nested structure.
    """

def create_savant_pitcher_models(pitcher_data: List[Dict]) -> List[SavantPitcherModel]:
    """
    Transform flat Savant pitcher data into nested SavantPitcherModel instances.

    Separates player metadata from stats and creates nested structure.
    """
```

**Key transformation:** Since Savant data is flat but our models are nested, these functions must:
1. Extract identity fields (player_id, name, etc.) and pitch count fields
2. Group remaining fields into a `stats` dictionary
3. Validate using Pydantic models

### Part 4: Tests

#### 4.1 Loader Tests
**File:** `tests/loaders/test_file_loader.py`

Add tests for Savant methods (update existing test):
- Test `get_savant_batters_file()` pattern matching
- Test `get_savant_pitchers_file()` pattern matching
- Test `load_savant_batters()` and `load_savant_pitchers()`

#### 4.2 Model Tests
**File:** `tests/models/savant/test_models.py` (NEW)

Create 8 minimal tests:
- `test_batter_model_validation` - Validate single batter
- `test_pitcher_model_validation` - Validate single pitcher
- `test_batter_model_with_all_data` - All fixture batters
- `test_pitcher_model_with_all_data` - All fixture pitchers
- `test_batter_stats_fields` - Verify stats fields accessible
- `test_pitcher_stats_fields` - Verify stats fields accessible
- `test_batter_model_with_invalid_data` - Missing required fields
- `test_pitcher_model_with_invalid_data` - Missing required fields

#### 4.3 Model Utils Tests
**File:** `tests/utils/test_model_utils.py`

Add 6 tests for Savant utilities:
- `test_create_savant_batter_models` - Valid data
- `test_create_savant_pitcher_models` - Valid data
- `test_create_savant_batter_models_with_empty_input` - Empty list
- `test_create_savant_pitcher_models_with_empty_input` - Empty list
- `test_create_savant_batter_models_with_invalid_data(caplog)` - Exception handling
- `test_create_savant_pitcher_models_with_invalid_data(caplog)` - Exception handling

#### 4.4 Fixtures
**File:** `tests/conftest.py`

Add fixtures:
```python
@pytest.fixture
def savant_batter_data() -> List[Dict]:
    fixtures_path = Path(__file__).parent / "fixtures"
    with open(fixtures_path / "savant_batters_2026_01_03_1444.json") as f:
        data = json.load(f)
    return data[:10]

@pytest.fixture
def savant_pitcher_data() -> List[Dict]:
    fixtures_path = Path(__file__).parent / "fixtures"
    with open(fixtures_path / "savant_pitchers_2026_01_03_1444.json") as f:
        data = json.load(f)
    return data[:10]
```

## Implementation Steps (Execution Order)

1. **Update DataLoader:**
   - Add Savant file discovery methods
   - Add Savant load methods
   - Update docstring

2. **Create Savant Models:**
   - Create `models/savant/__init__.py`
   - Create `savant_player.py` with `SavantPlayerModel` and `SavantBaseStats`
   - Create `stats.py` with `SavantBatterStatsModel` and `SavantPitcherStatsModel`
   - Create `batter.py` with `SavantBatterModel`
   - Create `pitcher.py` with `SavantPitcherModel`

3. **Add Model Utilities:**
   - Import Savant models in `model_utils.py`
   - Implement `create_savant_batter_models()` with data transformation
   - Implement `create_savant_pitcher_models()` with data transformation

4. **Create Tests:**
   - Add fixtures to `conftest.py`
   - Update loader tests in `test_file_loader.py`
   - Create `tests/models/savant/test_models.py`
   - Update `tests/utils/test_model_utils.py`

5. **Run Tests:**
   - Verify all Savant tests pass
   - Ensure 100% coverage on new code

## Critical Files

**New Files:**
- `player_universe_trx/models/savant/__init__.py`
- `player_universe_trx/models/savant/savant_player.py`
- `player_universe_trx/models/savant/stats.py`
- `player_universe_trx/models/savant/batter.py`
- `player_universe_trx/models/savant/pitcher.py`
- `tests/models/savant/__init__.py`
- `tests/models/savant/test_models.py`

**Modified Files:**
- `player_universe_trx/loaders/file_loader.py`
- `player_universe_trx/utils/model_utils.py`
- `tests/loaders/test_file_loader.py`
- `tests/utils/test_model_utils.py`
- `tests/conftest.py`

## Design Decisions

1. **Nested Stats Model:** Group statistics in a `stats` object for consistency with ESPN/FanGraphs
2. **Field Names:** Keep snake_case as-is from JSON (e.g., `player_id`, `BB_pct`)
3. **Two-way Players:** Separate objects (one SavantBatterModel + one SavantPitcherModel)
4. **Timestamp Format:** Savant uses `YYYY_MM_DD_HHMM` (different from ESPN/FanGraphs `YYYYMMDD_HHMMSS`)
5. **Data Transformation:** Utility functions must transform flat JSON into nested model structure

## Pydantic Configuration

All models use:
```python
model_config = ConfigDict(populate_by_name=True)
```

## Special Considerations

**Field Name with Percentage Sign:**
- `BB%` and `K%` in JSON should map to `BB_pct` and `K_pct` in models
- Use `Field(alias="BB%")` to handle this mapping

**Flat to Nested Transformation:**
The utility functions must intelligently separate:
- Identity fields → root level
- Pitch count fields → root level
- All other fields → `stats` nested object
