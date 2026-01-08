# Player Universe Transform - Analysis Findings

**Generated**: 2026-01-06
**Source Files**: Test fixtures from `tests/fixtures/` (2025 data)

---

## 🔍 Key Items to Investigate Tomorrow

1. **❗ Missing IP (Innings Pitched) field** - All pitchers are missing the IP field from ESPN stats, even though W, ERA, K, BB, WHIP are present. Why?

2. **❗ Zero FanGraphs Projections** - No players have `proj_AB` or `proj_IP` fields populated. Are projections not being extracted from the FanGraphs source data, or are they missing in the fixture files?

3. **⚠️ 52.6% of batters have empty stats** - 741 batters (52.6%) matched across sources but have no statistics at all. These players likely exist in rosters but haven't played yet or have minimal playing time.

4. **⚠️ Ambiguous matches need resolution** - 246 players have multiple FanGraphs candidates (avg 7.6 candidates each, max 54). Common last names like "Alvarez", "Taylor", "Anderson" create many false positives.

5. **✅ Savant enrichment is strong** - 43.4% of batters and 49.9% of pitchers have Savant data, providing valuable advanced metrics (exit velocity, xwOBA, swing & miss %).

6. **✅ ESPN + Savant combination works well** - 610 batters (43.3%) and 547 pitchers (35.4%) have both ESPN current season stats and Savant metrics, providing a complete analytical picture.

---

## Overall Statistics

- Total matched players: 2952
  - Batters: 1408
  - Pitchers: 1544
- Unmatched: 211
- Ambiguous: 246

## Batter Statistics Coverage

- Batters with stats object: 1408 / 1408 (100.0%)
- Batters with ESPN current season stats (AB field): 666 / 1408 (47.3%)
- Batters with FanGraphs projections (proj_AB): 0 / 1408 (0.0%)
- Batters with Savant data (exit_velo): 611 / 1408 (43.4%)

### Batter Stat Source Combinations

- No stats (empty): 741 batters (52.6%)
- ESPN + Savant only: 610 batters (43.3%)
- ESPN only: 56 batters (4.0%)
- Savant only: 1 batters (0.1%)

## Pitcher Statistics Coverage

- Pitchers with stats object: 1544 / 1544 (100.0%)
- Pitchers with ESPN current season stats (W field): 556 / 1544 (36.0%)
- Pitchers with FanGraphs projections (proj_IP): 0 / 1544 (0.0%)
- Pitchers with Savant data (swing_miss_pct): 770 / 1544 (49.9%)

### Pitcher Stat Source Combinations

- No stats (empty): 765 pitchers (49.5%)
- ESPN + Savant only: 547 pitchers (35.4%)
- Savant only: 223 pitchers (14.4%)
- ESPN only: 9 pitchers (0.6%)

## Notable Missing ESPN Fields

- Pitchers have W (wins): 556
- Pitchers have IP (innings pitched): 0
- **Investigation needed**: Why is IP missing from ESPN pitcher stats?

## Sample Players for Validation

### Batters with ESPN + Savant (top 5 by AB):

- Francisco Lindor (SS): AB=644, exit_velo=90.1, xwOBA=0.345
- Elly De La Cruz (SS): AB=629, exit_velo=90.8, xwOBA=0.322
- Brent Rooker (DH): AB=626, exit_velo=90.7, xwOBA=0.352
- Steven Kwan (LF): AB=625, exit_velo=84.9, xwOBA=0.309
- Pete Alonso (1B): AB=624, exit_velo=93.5, xwOBA=0.385

### Pitchers with ESPN + Savant (top 5 by W):

- Max Fried (SP): W=19, ERA=2.86, swing_miss=26.6%
- Garrett Crochet (SP): W=18, ERA=2.59, swing_miss=29.4%
- Carlos Rodon (SP): W=18, ERA=3.09, swing_miss=30.3%
- Freddy Peralta (SP): W=17, ERA=2.70, swing_miss=30.1%
- Logan Webb (SP): W=15, ERA=3.22, swing_miss=24.7%

## Ambiguous Match Analysis

- Total ambiguous matches: 246
- Average candidates per ambiguous match: 7.6
- Max candidates for a single player: 54

### Sample Ambiguous Matches (first 3):

- **Andrew Alvarez** (WSH) has 13 candidates:
  - Nacho Alvarez Jr. (ATL)
  - Armando Alvarez (FA)
  - Andrés Alvarez (FA)

- **Grant Taylor** (CHW) has 10 candidates:
  - Tyrone Taylor (NYM)
  - Samad Taylor (SEA)
  - Brayden Taylor (TBR)

- **Kade Anderson** (SEA) has 6 candidates:
  - Max Anderson (DET)
  - Tim Anderson (FA)
  - Ethan Anderson (BAL)

## Unmatched Player Analysis

- Unmatched batters: 118
- Unmatched pitchers: 93

### Sample Unmatched Players (first 5):

- Nolan McLean (DH, NYM)
- Connelly Early (SP, BOS)
- Parker Messick (SP, CLE)
- Payton Tolle (SP, BOS)
- Mitch Farris (SP, LAA)

## Key Statistics Available

### Sample Batter Stats (Francisco Lindor):

**ESPN Current Season:**
- AB: 644.0, H: 172.0, HR: 31.0
- AVG: 0.267, OBP: 0.346, SLG: 0.466

**Savant:**
- Exit Velocity: 90.1
- xwOBA: 0.345, xAVG: 0.263, xSLG: 0.448
- Barrel %: 8.897485493230175, Hard Hit %: 44.680851063829785

### Sample Pitcher Stats (Max Fried):

**ESPN Current Season:**
- W: 19.0, L: 5.0, ERA: 2.86
- K: 189.0, BB: 51, WHIP: 1.10

**Savant:**
- Swing & Miss %: 26.6
- Whiff %: None, Chase %: None

---

## 📋 Quick Reference

### Output Files in `.temp/`

- `matched_players.json` (19MB) - 2,952 successfully matched players
- `unmatched_players.json` (1.3MB) - 211 players with no FanGraphs match
- `ambiguous_matches.json` (3.9MB) - 246 players with multiple candidates
- `batter_example.json` - Bobby Witt Jr. (SS) - has ESPN + Savant
- `pitcher_example.json` - Gavin Williams (SP) - has ESPN stats

### Code Files to Review

- `player_universe_trx/matchers/player_matcher.py:913-916` - Retired player filter
- `player_universe_trx/matchers/player_matcher.py:870-889` - Type-narrowed stats model creation
- `player_universe_trx/__main__.py:125` - Enabled save_results call
- `player_universe_trx/utils/output_utils.py:47-49` - Fixed ambiguous candidate serialization

### Running the Pipeline

```bash
# Run with test fixtures
uv run python run_with_fixtures.py

# Or run with production data
uv run python -m player_universe_trx
```

### Match Statistics

- **Primary match method**: Slug (80.5%)
- **High confidence**: 80.6%
- **Match success rate**: 84.9%
- **Savant enrichment**: 39.7%
