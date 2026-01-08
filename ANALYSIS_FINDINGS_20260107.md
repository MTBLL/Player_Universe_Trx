# Player Universe Transform - Analysis Findings
**Generated**: 2026-01-07 20:41
**Data Source**: Production ESPN & FanGraphs files (2025 season data)
**Note**: Run without Savant data (Savant files are 2026, ESPN/FG are 2025)

---

## 🎯 Key Findings Summary

### ✅ RESOLVED: IP Field Issue
**ESPN now provides `OUTS` instead of `IP`**
- Calculation: `IP = OUTS / 3`
- Coverage: 798 pitchers (51.7%) have OUTS field
- Example: Logan Webb has 621 OUTS = 207.0 IP
- **Action**: Transform layer should calculate IP from OUTS

### ⚠️ Missing FanGraphs Projections
- **0 batters** have FanGraphs projections (proj_ab, proj_hr, etc.)
- **0 pitchers** have FanGraphs projections (proj_ip, proj_era, etc.)
- **Investigation needed**: Are projections in a different field or missing from source?

### 📊 Data Coverage
**Batters:**
- Total matched: 1,409
- With current season stats: 666 (47.3%)
- Without stats: 743 (52.7%)

**Pitchers:**
- Total matched: 1,543
- With current season stats (W field): 556 (36.0%)
- With OUTS field: 798 (51.7%)
- Without stats: 987 (64.0%)

### 🎖️ Match Quality
- Match success rate: 84.9% (2,952 / 3,478)
- Primary match method: Slug matching (80.5%)
- High confidence matches: 80.6%
- Unmatched: 211 players
- Ambiguous: 246 players

---

## 📈 Top Performers - 2025 Season

### Batters

#### 🏆 Highest Batting Average (min 300 AB)
1. **Aaron Judge** (.331) - Also hit 53 HR with 114 RBI
2. Miguel Andujar (.318) - 321 AB, 10 HR
3. Jonathan Aranda (.316) - 370 AB, 14 HR
4. Bo Bichette (.311) - 582 AB, 18 HR
5. Jacob Wilson (.311) - 486 AB, 13 HR

#### 💪 Home Run Leaders
1. **Cal Raleigh** (60) - Catcher with 125 RBI, .247 AVG
2. Kyle Schwarber (56) - 132 RBI, .240 AVG
3. Shohei Ohtani (55) - 102 RBI, .282 AVG
4. Aaron Judge (53) - 114 RBI, .331 AVG
5. Eugenio Suarez (49) - 118 RBI, .228 AVG

#### 🏃 Stolen Base Leaders
1. **Jose Caballero** (49) - 11 CS, .236 AVG
2. Jose Ramirez (44) - 7 CS, .283 AVG (power+speed combo)
3. Chandler Simpson (44) - 12 CS, .295 AVG
4. Bobby Witt Jr. (38) - 9 CS, .295 AVG (elite all-around)
5. Juan Soto (38) - 4 CS, .263 AVG (surprising speed!)

#### 📊 Workhorses (Most At-Bats)
1. Julio Rodriguez (652 AB) - .267, 32 HR, 95 RBI
2. Francisco Lindor (644 AB) - .267, 31 HR, 86 RBI
3. Elly De La Cruz (629 AB) - .264, 22 HR, 86 RBI, 37 SB

### Pitchers

#### ⭐ Lowest ERA (min 50 IP)
1. **Aroldis Chapman** (1.17) - RP, 61.3 IP, 0.70 WHIP
2. Edwin Diaz (1.63) - RP, 66.3 IP, 0.87 WHIP
3. Abner Uribe (1.67) - RP, 75.3 IP
4. **Nathan Eovaldi** (1.73) - SP, 130.0 IP, 11 W (elite starter!)
5. Andres Munoz (1.73) - RP, 62.3 IP

#### 🏆 Win Leaders
1. **Max Fried** (19 W) - 195.3 IP, 2.86 ERA, 189 K
2. Garrett Crochet (18 W) - 205.3 IP, 2.59 ERA, 255 K
3. Carlos Rodon (18 W) - 195.3 IP, 3.09 ERA, 203 K
4. Freddy Peralta (17 W) - 176.7 IP, 2.70 ERA, 204 K
5. Logan Webb (15 W) - 207.0 IP, 3.22 ERA, 224 K

#### 🔥 Strikeout Leaders
1. **Garrett Crochet** (255 K) - 205.3 IP, 2.59 ERA, 18 W
2. Tarik Skubal (241 K) - 195.3 IP, 2.21 ERA, 13 W
3. Logan Webb (224 K) - 207.0 IP, 3.22 ERA, 15 W
4. Paul Skenes (216 K) - 187.7 IP, 1.97 ERA, 10 W (rookie sensation!)
5. Jesus Luzardo (216 K) - 183.7 IP, 3.92 ERA, 15 W

#### 🌟 Standout Performances
- **Paul Skenes**: 216 K in 187.7 IP with 1.97 ERA (likely rookie of year)
- **Nathan Eovaldi**: 1.73 ERA in 130 IP as a starter (dominant)
- **Trevor Rogers**: 1.81 ERA in 109.7 IP, 9 W (breakout year?)
- **Cristopher Sanchez**: 212 K in 202 IP, 2.50 ERA, 13 W

---

## 💡 Interesting Observations

### Power + Average Combo
- **Aaron Judge**: .331 AVG + 53 HR (elite in both categories)
- **Bobby Witt Jr.**: .295 AVG + 23 HR + 38 SB (five-tool player)
- **Jose Ramirez**: .283 AVG + 44 SB (power-speed combo)

### Surprising Speed
- **Juan Soto**: 38 SB (not known as a speedster!)
- Only 4 caught stealing vs 38 successful (90.5% success rate)

### Catcher Power
- **Cal Raleigh**: 60 HR from catcher position (historic?)
- 125 RBI despite .247 average

### Pitcher Workloads
- **Logan Webb**: 207.0 IP (workhorse)
- **Garrett Crochet**: 205.3 IP with 255 K (K/9 = 11.2)
- Several pitchers exceeding 195+ IP

### Elite Rookie
- **Paul Skenes**: 1.97 ERA, 216 K in 187.7 IP
- 0.95 WHIP, 10 W
- Likely Rookie of the Year candidate

---

## 🔍 Data Quality Notes

### Strengths
- ✅ ESPN current season stats well-populated (47% batters, 36% pitchers)
- ✅ OUTS field present for IP calculation (52% of pitchers)
- ✅ Slug matching highly effective (80.5% of matches)
- ✅ High confidence matches (80.6%)

### Issues to Investigate
- ❌ **No FanGraphs projections** - All proj_* fields are empty
- ⚠️ **52.7% of batters have no stats** - Likely minor leaguers or bench players
- ⚠️ **64% of pitchers have no stats** - High percentage, needs investigation
- ⚠️ **246 ambiguous matches** - Need better disambiguation logic

### Missing Data
- **Savant metrics**: Not included in this run (year mismatch)
- **FanGraphs projections**: Expected but missing
- **Advanced metrics**: exit_velo, xwOBA, etc. require Savant data

---

## 📝 Recommendations

1. **Add IP calculated field** - Transform OUTS to IP in the output
2. **Investigate FanGraphs projections** - Why are proj_* fields empty?
3. **Align Savant data year** - Get 2025 Savant data or use 2026 for all sources
4. **Improve ambiguous match resolution** - Use additional heuristics (draft year, team history)
5. **Document no-stats players** - Clarify why 50%+ have no stats (rookies, injuries, etc.)

---

## 📂 Output Files

Located in `.temp/`:
- `batters_matched.json` (9.5 MB) - 1,409 batters
- `batters_unmatched.json` (553 KB) - 136 batters
- `batters_ambiguous.json` (3.0 MB) - 150 batters
- `pitchers_matched.json` (9.3 MB) - 1,543 pitchers
- `pitchers_unmatched.json` (259 KB) - 75 pitchers
- `pitchers_ambiguous.json` (1.7 MB) - 96 pitchers

---

## 🎯 Next Steps

1. ✅ **COMPLETED**: Identified OUTS field for IP calculation
2. ⏭️ Investigate missing FanGraphs projections
3. ⏭️ Add IP as calculated field in transform layer
4. ⏭️ Align Savant data year with ESPN/FanGraphs
5. ⏭️ Improve match disambiguation for ambiguous cases
