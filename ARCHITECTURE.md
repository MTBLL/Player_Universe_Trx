# Transformation Architecture
transform_app/
├── __main__.py                 # Entry point - orchestrates the pipeline
├── models/
│   ├── espn.py            # ESPNBatter, ESPNPitcher
│   ├── fangraphs.py       # FangraphsBatter, FangraphsPitcher  
│   ├── savant.py          # SavantBatter, SavantPitcher
│   └── player.py          # Batter, Pitcher (output models)
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
