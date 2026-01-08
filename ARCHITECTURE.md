# Transformation Architecture
transform_app/
├── __main__.py                 # Entry point - orchestrates the pipeline
├── models/
│   ├── espn/
│   │   ├── batter.py          # ESPNBatter
│   │   └── pitcher.py         # ESPNPitcher
│   │   └── stats.py           # ESPNStats
│   ├── fangraphs/
│   │   ├── batter.py          # FangraphsBatter
│   │   └── pitcher.py         # FangraphsPitcher
│   │   └── stats.py           # FangraphsStats
│   ├── savant/
│   │   ├── batter.py          # SavantBatter
│   │   └── pitcher.py         # SavantPitcher
│   │   └── stats.py           # SavantStats
│   └── player.py              # Batter, Pitcher (output models)
├── loaders/
│   └── file_loader.py     # Read JSON files from local dir
├── transformers/
│   ├── espn_transformer.py
│   ├── fangraphs_transformer.py
│   ├── savant_transformer.py
│   └── player_merger.py   # Merge sources → final models
├── validators/
│   └── data_validator.py  # Cross-source validation logic
└── writers/
    └── graphql_writer.py  # Write to GraphQL endpoint
