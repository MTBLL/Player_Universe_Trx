"""Constants for ESPN data transformation."""

# ESPN Position ID to Position Name mapping
ESPN_POSITION_MAP = {
    0: "C",  # Catcher
    1: "1B",  # First Base
    2: "2B",  # Second Base
    3: "3B",  # Third Base
    4: "SS",  # Shortstop
    5: "OF",  # Outfield
    6: "MI",  # Middle Infield (2B/SS)
    7: "CI",  # Corner Infield (1B/3B)
    8: "LF",  # Left Field
    9: "RF",  # Right Field
    10: "DH",  # Designated Hitter
    11: "UTIL",  # Utility
    12: "P",  # Pitcher
    13: "SP",  # Starting Pitcher
    14: "RP",  # Relief Pitcher
}

# ESPN Lineup Slot ID to Position Name mapping
ESPN_LINEUP_SLOT_MAP = {
    0: "C",  # Catcher
    1: "1B",  # First Base
    2: "2B",  # Second Base
    3: "3B",  # Third Base
    4: "SS",  # Shortstop
    5: "OF",  # Outfield
    6: "MI",  # Middle Infield
    7: "CI",  # Corner Infield
    8: "LF",  # Left Field
    9: "RF",  # Right Field
    10: "DH",  # Designated Hitter
    11: "UTIL",  # Utility (any position)
    12: "UTIL",  # Utility (any position)
    13: "SP",  # Starting Pitcher
    14: "SP",  # Starting Pitcher
    15: "RP",  # Relief Pitcher
    16: "BENCH",  # Bench
    17: "IL",  # Injured List
    18: "IL",  # Injured List
    19: "IF",  # Infield
}

# ESPN Pro Team ID to MLB Team Abbreviation mapping
ESPN_PRO_TEAM_MAP = {
    0: "FA",  # Free Agent
    1: "ATL",  # Atlanta Braves
    2: "ARI",  # Arizona Diamondbacks
    3: "BAL",  # Baltimore Orioles
    4: "BOS",  # Boston Red Sox
    5: "CHC",  # Chicago Cubs
    6: "CIN",  # Cincinnati Reds
    7: "CLE",  # Cleveland Guardians
    8: "MIL",  # Milwaukee Brewers
    9: "COL",  # Colorado Rockies
    10: "DET",  # Detroit Tigers
    11: "OAK",  # Oakland Athletics
    12: "SEA",  # Seattle Mariners
    13: "TEX",  # Texas Rangers
    14: "HOU",  # Houston Astros
    15: "MIA",  # Miami Marlins
    16: "LAD",  # Los Angeles Dodgers
    17: "LAA",  # Los Angeles Angels
    18: "KC",  # Kansas City Royals
    19: "MIN",  # Minnesota Twins
    20: "WSH",  # Washington Nationals
    21: "NYM",  # New York Mets
    22: "PHI",  # Philadelphia Phillies
    23: "PIT",  # Pittsburgh Pirates
    24: "STL",  # St. Louis Cardinals
    25: "SD",  # San Diego Padres
    26: "SF",  # San Francisco Giants
    27: "TB",  # Tampa Bay Rays
    28: "TOR",  # Toronto Blue Jays
    29: "NYY",  # New York Yankees
    30: "CHW",  # Chicago White Sox
}

# Lineup slot type to roster field name mapping (for MtblTeamRosterModel)
ROSTER_FIELD_MAP = {
    "C": "c",
    "1B": "first_base",
    "2B": "second_base",
    "3B": "third_base",
    "SS": "shortstop",
    "OF": "outfield",
    "UTIL": "util",
    "SP": "sp",
    "RP": "rp",
    "BENCH": "bench",
    "IL": "injured_list",
}
