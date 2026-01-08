#!/usr/bin/env python
"""Run the player universe transformation pipeline with test fixtures."""

from player_universe_trx.__main__ import main

if __name__ == "__main__":
    # Run with test fixtures (all files are for year 2025)
    main(
        resources_path="tests/fixtures",
        year=2025,
        output_dir=".temp"
    )
