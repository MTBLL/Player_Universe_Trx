# League Transformation Design

## Overview
Transform ESPN league data into team-based roster tables with minimal player information for database loading and JSON export.

## Data Flow
```
ESPN League JSON → League Models → Team/Roster Models → Per-Team JSON Export
                                                      → Database Tables
```

## ESPN League Structure Analysis

### League Level
- `id`: League ID (e.g., 10998)
- `seasonId`: Season year (e.g., 2025)
- `teams`: Array of team objects (11 teams in fixture)
- `settings`: League configuration including roster settings
- `schedule`: Matchup schedule (not needed for roster transformation)

### Team Level
- `id`: Team ID (e.g., 1, 7, 8, etc.)
- `name`: Team name (e.g., "Hader's Gon Hate")
- `abbrev`: Team abbreviation (e.g., "PEWB")
- `logo`: Team logo URL
- `owners`: Array of owner IDs
- `primaryOwner`: Primary owner ID
- `record`: Team record (overall, home, away, division)
- `roster`: Roster object containing entries

### Roster Entry Structure
Each roster entry contains:
- `playerId`: ESPN player ID (links to player universe)
- `lineupSlotId`: Position slot (0=C, 1=1B, 2=2B, 3=3B, 4=SS, 5=OF, 12=UTIL, 13/14=SP, 15=RP, 16=BENCH, 17=IL)
- `acquisitionDate`: Unix timestamp
- `acquisitionType`: "DRAFT", "ADD", "TRADE", etc.
- `injuryStatus`: "NORMAL", "OUT", etc.
- `playerPoolEntry`:
  - `onTeamId`: Team that owns this player (matches team.id)
  - `keeperValue`: Keeper round value
  - `player`: Nested player object with:
    - `id`: Player ID
    - `fullName`: Full name
    - `firstName`, `lastName`: Name components
    - `proTeamId`: MLB team ID
    - `defaultPositionId`: Primary position
    - `eligibleSlots`: Array of eligible lineup slots
    - `injuryStatus`: Injury status
    - `active`: Active status

### Roster Slot Configuration (from fixture)
```
0:  1 position  - C (Catcher)
1:  1 position  - 1B (First Base)
2:  1 position  - 2B (Second Base)
3:  1 position  - 3B (Third Base)
4:  1 position  - SS (Shortstop)
5:  3 positions - OF (Outfield)
12: 1 position  - UTIL (Utility)
13: 2 positions - SP (Starting Pitcher)
14: 3 positions - SP (Starting Pitcher)
15: 2 positions - RP (Relief Pitcher)
16: 5 positions - BENCH (Bench)
17: 6 positions - IL (Injured List)
```

## Proposed Model Structure

### 1. ESPN Models (Input)

#### `EspnLeagueModel`
```python
class EspnLeagueModel(BaseModel):
    id: int
    seasonId: int
    scoringPeriodId: Optional[int]
    teams: List[EspnTeamModel]
    settings: Optional[EspnLeagueSettingsModel]
```

#### `EspnTeamModel`
```python
class EspnTeamModel(BaseModel):
    id: int
    name: str
    abbrev: str
    logo: Optional[str]
    owners: List[str]
    primaryOwner: str
    roster: EspnRosterModel
    record: Optional[EspnRecordModel]
```

#### `EspnRosterModel`
```python
class EspnRosterModel(BaseModel):
    entries: List[EspnRosterEntryModel]
```

#### `EspnRosterEntryModel`
```python
class EspnRosterEntryModel(BaseModel):
    playerId: int
    lineupSlotId: int
    acquisitionDate: Optional[int]
    acquisitionType: Optional[str]
    injuryStatus: Optional[str]
    playerPoolEntry: EspnPlayerPoolEntryModel
```

#### `EspnPlayerPoolEntryModel`
```python
class EspnPlayerPoolEntryModel(BaseModel):
    id: int
    onTeamId: int
    keeperValue: Optional[int]
    keeperValueFuture: Optional[int]
    player: EspnPlayerMinimalModel  # Minimal player info
```

#### `EspnPlayerMinimalModel`
```python
class EspnPlayerMinimalModel(BaseModel):
    id: int
    fullName: str
    firstName: Optional[str]
    lastName: Optional[str]
    proTeamId: int
    defaultPositionId: int
    eligibleSlots: List[int]
    injuryStatus: Optional[str]
    active: bool
```

### 2. MTBL Output Models

#### `MtblLeagueModel`
```python
class MtblLeagueModel(BaseModel):
    league_id: int
    season_id: int
    scoring_period_id: Optional[int]
    num_teams: int
    roster_settings: Optional[RosterSettingsModel]
```

#### `MtblTeamRosterModel` (Main export model)
```python
class MtblTeamRosterModel(BaseModel):
    # Team Info
    league_id: int
    season_id: int
    team_id: int
    team_name: str
    team_abbrev: str
    team_logo: Optional[str]
    owners: List[str]
    primary_owner: str

    # Record (optional)
    record: Optional[TeamRecordModel]

    # Roster Slots (explicit fields for each position)
    # Each field contains player_id and minimal player data
    c: Optional[RosterSlotPlayer]           # Catcher
    first_base: Optional[RosterSlotPlayer]  # 1B
    second_base: Optional[RosterSlotPlayer] # 2B
    third_base: Optional[RosterSlotPlayer]  # 3B
    shortstop: Optional[RosterSlotPlayer]   # SS
    outfield: List[RosterSlotPlayer]        # OF (3 slots)
    util: Optional[RosterSlotPlayer]        # UTIL (1 slot)
    sp: List[RosterSlotPlayer]              # SP (5 slots combined: 2 + 3)
    rp: List[RosterSlotPlayer]              # RP (2 slots)
    bench: List[RosterSlotPlayer]           # BENCH (5 slots)
    injured_list: List[RosterSlotPlayer]    # IL (6 slots)
```

#### `RosterSlotPlayer` (Minimal player data)
```python
class RosterSlotPlayer(BaseModel):
    # Core identification
    player_id: int  # ESPN player ID (links to player universe)

    # Basic info (no stats)
    name: str
    first_name: Optional[str]
    last_name: Optional[str]

    # Team/Position info
    pro_team: str  # MLB team abbreviation (derived from proTeamId)
    primary_position: str  # Position name (derived from defaultPositionId)
    eligible_positions: List[str]  # Position names (derived from eligibleSlots)

    # Roster info
    lineup_slot: str  # "C", "1B", "OF", "SP", "BENCH", etc.
    acquisition_type: Optional[str]  # "DRAFT", "ADD", "TRADE"
    acquisition_date: Optional[str]  # ISO format date

    # Status
    injury_status: Optional[str]
    active: bool

    # Keeper value
    keeper_value: Optional[int]
```

#### `TeamRecordModel`
```python
class TeamRecordModel(BaseModel):
    wins: int
    losses: int
    ties: int
    percentage: float
    games_back: float
```

## Database Schema Design

### `mtbl_team_roster` Table
```sql
CREATE TABLE mtbl_team_roster (
    id SERIAL PRIMARY KEY,
    league_id INTEGER NOT NULL,
    season_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    team_name VARCHAR(255),
    team_abbrev VARCHAR(10),
    team_logo VARCHAR(500),
    primary_owner VARCHAR(255),
    wins INTEGER,
    losses INTEGER,
    ties INTEGER,
    win_percentage DECIMAL(5,4),
    games_back DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(league_id, season_id, team_id)
);
```

### `mtbl_roster_slot` Table
```sql
CREATE TABLE mtbl_roster_slot (
    id SERIAL PRIMARY KEY,
    league_id INTEGER NOT NULL,
    season_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,

    -- Position slot
    slot_type VARCHAR(20) NOT NULL,  -- 'C', '1B', '2B', '3B', 'SS', 'OF', 'UTIL', 'SP', 'RP', 'BENCH', 'IL'
    slot_index INTEGER DEFAULT 0,    -- For multi-slot positions (OF, SP, BENCH, IL)

    -- Player reference (links to player universe)
    player_id INTEGER NOT NULL,

    -- Minimal player data (denormalized for convenience)
    player_name VARCHAR(255),
    player_first_name VARCHAR(255),
    player_last_name VARCHAR(255),
    pro_team VARCHAR(10),
    primary_position VARCHAR(20),
    eligible_positions TEXT[],  -- Array of positions

    -- Roster metadata
    acquisition_type VARCHAR(20),
    acquisition_date TIMESTAMP,
    injury_status VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    keeper_value INTEGER,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (league_id, season_id, team_id)
        REFERENCES mtbl_team_roster(league_id, season_id, team_id),
    UNIQUE(league_id, season_id, team_id, slot_type, slot_index)
);
```

## JSON Export Format

### Per-Team Export
Each team gets its own JSON file: `team_{team_id}_roster.json`

```json
{
  "league_id": 10998,
  "season_id": 2025,
  "team_id": 1,
  "team_name": "Hader's Gon Hate",
  "team_abbrev": "PEWB",
  "team_logo": "https://i.imgur.com/EhYdq2q.jpg",
  "owners": ["{3D596368-E046-4194-8C20-C0CB4F2E8BBD}"],
  "primary_owner": "{3D596368-E046-4194-8C20-C0CB4F2E8BBD}",
  "record": {
    "wins": 38,
    "losses": 78,
    "ties": 4,
    "percentage": 0.3333,
    "games_back": 40.0
  },
  "c": {
    "player_id": 4781491,
    "name": "Yainer Diaz",
    "first_name": "Yainer",
    "last_name": "Diaz",
    "pro_team": "HOU",
    "primary_position": "C",
    "eligible_positions": ["C", "1B", "UTIL"],
    "lineup_slot": "C",
    "acquisition_type": "DRAFT",
    "acquisition_date": "2025-01-26T12:30:29Z",
    "injury_status": "ACTIVE",
    "active": true,
    "keeper_value": 1,
  },
  "first_base": {
    "player_id": 39833,
    "name": "Michael Toglia",
    ...
  },
  "outfield": [
    {
      "player_id": 4917869,
      "name": "Jackson Chourio",
      "pro_team": "MIL",
      ...
    },
    {
      "player_id": 4719324,
      "name": "Wyatt Langford",
      ...
    },
    {
      "player_id": 40926,
      "name": "Brent Rooker",
      ...
    }
  ],
  "sp": [
    {
      "player_id": 5134630,
      "name": "Shota Imanaga",
      ...
    },
    ...
  ],
  "bench": [
    ...
  ],
  "injured_list": [
    ...
  ]
}
```

## Implementation Steps

1. **Create ESPN League Models** (`player_universe_trx/models/espn/league.py`)
   - EspnLeagueModel
   - EspnTeamModel
   - EspnRosterModel
   - EspnRosterEntryModel
   - EspnPlayerPoolEntryModel
   - EspnPlayerMinimalModel

2. **Create MTBL Output Models** (`player_universe_trx/models/mtbl/league.py`)
   - MtblLeagueModel
   - MtblTeamRosterModel
   - RosterSlotPlayer
   - TeamRecordModel
   - RosterSettingsModel

3. **Create League Loader** (`player_universe_trx/loaders/league_loader.py`)
   - Load league JSON from file
   - Validate against ESPN models
   - Return EspnLeagueModel instance

4. **Create League Transformer** (`player_universe_trx/transformers/league_transformer.py`)
   - Transform EspnLeagueModel → List[MtblTeamRosterModel]
   - Map lineup slot IDs to position names
   - Map pro team IDs to abbreviations
   - Map position IDs to position names
   - Extract minimal player data
   - Group players by roster slot type

5. **Create Output Utilities** (`player_universe_trx/utils/league_output.py`)
   - Save per-team JSON files
   - Generate SQL INSERT statements (optional)
   - Save league summary

6. **Update Main Pipeline** (`player_universe_trx/__main__.py`)
   - Add league transformation option
   - Integrate with existing player transformation
   - Support dual-mode operation (players-only, league-only, or both)

## Configuration & Lookups

### Position ID to Name Mapping
```python
ESPN_POSITION_MAP = {
    0: "C",      # Catcher
    1: "1B",     # First Base
    2: "2B",     # Second Base
    3: "3B",     # Third Base
    4: "SS",     # Shortstop
    5: "OF",     # Outfield
    6: "MI",     # Middle Infield (2B/SS)
    7: "CI",     # Corner Infield (1B/3B)
    8: "LF",     # Left Field
    9: "RF",     # Right Field
    10: "DH",    # Designated Hitter
    11: "UTIL",  # Utility
    12: "P",     # Pitcher
    13: "SP",    # Starting Pitcher
    14: "RP",    # Relief Pitcher
    15: "RP",    # Relief Pitcher
}
```

### Lineup Slot ID to Position Name
```python
ESPN_LINEUP_SLOT_MAP = {
    0: "C",
    1: "1B",
    2: "2B",
    3: "3B",
    4: "SS",
    5: "OF",
    12: "UTIL",
    13: "SP",
    14: "SP",
    15: "RP",
    16: "BENCH",
    17: "IL",
}
```

### MLB Team ID to Abbreviation (use existing mapping if available)

## Benefits of This Design

1. **Database-Friendly**: Each table row represents a discrete roster slot with foreign key to team
2. **JSON Export Transit**: Clean, minimal player data without stats bloat
3. **Flexible Queries**: Can easily query by team, position, player, or slot type
4. **Maintainable**: Clear separation between ESPN source format and MTBL output format
5. **Extensible**: Easy to add more fields or position types as needed
6. **Type-Safe**: Pydantic models ensure data validation at every step
7. **Denormalized Player Data**: Minimal player info stored with roster slot for convenience, but player_id provides link to full player universe for stats
