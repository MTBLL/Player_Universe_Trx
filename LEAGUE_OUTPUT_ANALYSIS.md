# League Transformation Output Analysis

## Overview
Complete analysis of league transformation outputs in `.temp/` directory.

## Files Generated

### League Summary
- **File**: `league_10998_summary.json` (443 bytes)
- **Contains**: League metadata, roster settings, slot counts
- **Purpose**: Reference for league configuration

### Team Rosters
- **Files**: 11 team roster files (`team_*.json`)
- **Total Size**: 139,190 bytes (135.9 KB)
- **Average per Team**: 12.4 KB
- **Size Range**: 11-14 KB per team

## League Summary Structure

```json
{
  "league_id": 10998,
  "season_id": 2025,
  "scoring_period_id": 196,
  "num_teams": 11,
  "roster_settings": {
    "lineup_slot_counts": {
      "0": 1,    // C
      "1": 1,    // 1B
      "2": 1,    // 2B
      "3": 1,    // 3B
      "4": 1,    // SS
      "5": 3,    // OF
      "12": 1,   // UTIL
      "13": 2,   // SP
      "14": 3,   // SP
      "15": 2,   // RP
      "16": 5,   // BENCH
      "17": 6    // IL
    }
  }
}
```

## Team Roster Structure

### Example: Team 1 (Hader's Gon Hate)

**Team Metadata:**
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
    "percentage": 0.333,
    "games_back": 40.0
  }
}
```

**Roster Positions:**

Single-player positions (Optional fields):
- `c` - Catcher
- `first_base` - First Base
- `second_base` - Second Base
- `third_base` - Third Base
- `shortstop` - Shortstop
- `util` - Utility

Multi-player positions (Array fields):
- `outfield` - Outfield (typically 3 players)
- `sp` - Starting Pitchers (typically 5 players)
- `rp` - Relief Pitchers (typically 2 players)
- `bench` - Bench (typically 5 players)
- `injured_list` - Injured List (0-6 players)

## Player Data Structure (Minimal - No Stats)

### Complete Player Object
```json
{
  "player_id": 4781491,
  "name": "Yainer Diaz",
  "first_name": "Yainer",
  "last_name": "Diaz",
  "pro_team": "KC",
  "primary_position": "2B",
  "eligible_positions": ["C", "UTIL", "BENCH", "IL"],
  "lineup_slot": "C",
  "acquisition_type": "DRAFT",
  "acquisition_date": "2025-03-29T11:37:09.283000Z",
  "injury_status": "ACTIVE",
  "active": true,
  "keeper_value": 1,
}
```

### Field Descriptions

**Identification:**
- `player_id` - ESPN player ID (links to player universe for full stats)
- `name` - Full player name
- `first_name`, `last_name` - Name components

**Team & Position:**
- `pro_team` - MLB team abbreviation (NYY, LAD, etc.)
- `primary_position` - Primary position (C, 1B, OF, SP, etc.)
- `eligible_positions` - All eligible positions in fantasy league
- `lineup_slot` - Current roster slot (C, OF, SP, BENCH, IL)

**Acquisition:**
- `acquisition_type` - How acquired: "DRAFT", "ADD", "TRADE"
- `acquisition_date` - ISO 8601 timestamp

**Status:**
- `injury_status` - Injury status (ACTIVE, OUT, etc.)
- `active` - Boolean active status

**Keeper Info:**
- `keeper_value` - Current keeper round value

**NO STATS**: No AB, H, HR, AVG, ERA, WHIP, or any statistical fields

## Roster Size Analysis

### All Teams
```
Team ID  Team Name                      Total  Active  Bench  IL
========================================================================
17       October's Very Own                23      16      5    2
18       Toner from Minnesota               26      16      5    5
1        Hader's Gon Hate                   21      16      5    0
31       Bucco Bandwagon                    21      16      5    0
35       Acuna Matata                       26      15      6    5
36       Campus Popo                        24      16      4    4
39       Wolfey's Miracle Makers            24      16      3    5
40       john's Finest Team                 24      16      5    3
41       We Bring The Boom-bas              22      16      5    1
7        Puckett, We'll Do it Live          26      16      5    5
8        Pablo Sanchez's                    21      16      5    0
```

**Summary:**
- Total Teams: 11
- Roster Size Range: 21-26 players
- Active Positions: 15-16 players (C, 1B, 2B, 3B, SS, OF×3, UTIL, SP×5, RP×2)
- Bench: 3-6 players
- IL: 0-5 players

## Statistical Analysis

### Keeper Values
- **Total Players with Keeper Value**: 126 (49% of all rostered players)
- **Range**: 1 to 116
- **Average**: 16.9
- **Distribution**: Most players have values 1-30, with some high-value keepers (116, 100+)

### Acquisition Types
```
DRAFT : 128 players (49.6%)
ADD   : 118 players (45.7%)
TRADE :  12 players (4.7%)
```

### MLB Teams Represented
- **Total Teams**: 31 (includes FA = Free Agent)
- **Top 5 Most Rostered**:
  - FA (Free Agent): 24 players
  - MIN (Minnesota Twins): 13 players
  - SEA (Seattle Mariners): 12 players
  - SD (San Diego Padres): 11 players
  - MIA (Miami Marlins): 11 players

## Data Size Comparison

### Player Universe (Full Stats) vs League Roster (Minimal)

**Example: Yainer Diaz (id_espn: 4781491)**

| Metric | Player Universe | League Roster | Difference |
|--------|----------------|---------------|------------|
| Fields | 30 | 14 | 53% fewer |
| Has Stats | Yes (current + projections) | No | - |
| JSON Size | 5,477 bytes (5.35 KB) | 375 bytes (0.37 KB) | **93.2% reduction** |
| Ratio | - | - | **14.6x smaller** |

### Benefits of Minimal Data
1. **Performance**: 93% smaller = faster parsing, transfer, and database operations
2. **Storage Efficiency**: Minimal roster storage, full stats available via `player_id` link
3. **Clear Separation**: Roster management separate from statistical analysis
4. **Database Design**: Perfect for normalized schema with FK to player universe

## Database Schema Mapping

### Table: `mtbl_team_roster`
One row per team with metadata.

### Table: `mtbl_roster_slot`
One row per roster slot per team:
```sql
CREATE TABLE mtbl_roster_slot (
    team_id INTEGER,
    slot_type VARCHAR(20),  -- 'C', '1B', 'OF', 'SP', 'BENCH', 'IL'
    slot_index INTEGER,     -- For multi-slot positions
    player_id INTEGER,      -- FK to player universe

    -- Denormalized player data (for convenience)
    player_name VARCHAR(255),
    pro_team VARCHAR(10),
    primary_position VARCHAR(20),

    -- Roster metadata
    acquisition_type VARCHAR(20),
    acquisition_date TIMESTAMP,
    keeper_value INTEGER,

    FOREIGN KEY (player_id) REFERENCES player_universe(id_espn)
);
```

**Example Queries:**

Get team's active lineup:
```sql
SELECT * FROM mtbl_roster_slot
WHERE team_id = 1 AND slot_type NOT IN ('BENCH', 'IL');
```

Get all catchers in league:
```sql
SELECT team_id, player_name, pro_team
FROM mtbl_roster_slot
WHERE slot_type = 'C';
```

Get player stats via FK:
```sql
SELECT r.*, p.stats
FROM mtbl_roster_slot r
JOIN player_universe p ON r.player_id = p.id_espn
WHERE r.team_id = 1;
```

## JSON Export Use Cases

### 1. Frontend Display
Small JSON files perfect for web/mobile apps showing team rosters without stats bloat.

### 2. Roster Management APIs
Lightweight payloads for roster moves, trades, lineup changes.

### 3. Quick Reference
Fast loading of team composition without loading full player stats.

### 4. Sync with Player Universe
`player_id` provides link to fetch full stats when needed:
```javascript
// Load minimal roster
const roster = await fetch('/api/team/1/roster').then(r => r.json());

// Load full stats for specific player
const playerId = roster.c.player_id;
const fullPlayer = await fetch(`/api/players/${playerId}`).then(r => r.json());
```

## Validation Results

✅ **All 11 teams successfully transformed**
✅ **No stats fields in roster player objects**
✅ **All position IDs mapped to names**
✅ **All pro team IDs mapped to abbreviations**
✅ **Keeper values preserved**
✅ **Acquisition dates in ISO 8601 format**
✅ **Record data included**
✅ **14.6x size reduction vs full player data**

## Conclusion

The league transformation successfully creates:
1. **Lightweight team roster files** (12 KB avg) with minimal player data
2. **Clear position organization** with explicit fields for each position type
3. **Database-ready structure** for easy SQL table mapping
4. **93% size reduction** compared to full player data
5. **Foreign key linkage** via `player_id` to player universe for stats

This design perfectly separates roster management (lightweight, frequently accessed) from statistical analysis (heavyweight, accessed on-demand).
