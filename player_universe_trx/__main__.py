import logging
from typing import Dict, Optional

from player_universe_trx.loaders import DataLoader
from player_universe_trx.matchers.player_matcher import (
    PlayerMatcher,
    apply_matches,
)
from player_universe_trx.utils.model_utils import (
    create_espn_batter_models,
    create_espn_pitcher_models,
    create_fangraphs_batter_models,
    create_fangraphs_pitcher_models,
    create_savant_batter_models,
    create_savant_pitcher_models,
)
from player_universe_trx.utils.output_utils import save_results

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("player_universe_trx")


def main(
    resources_path: Optional[str] = None,
    year: Optional[int] = None,
    output_dir: Optional[str] = None,
) -> Dict:
    """
    Main entry point for the player universe transformation pipeline.

    Args:
        resources_path: Path to directory containing input files (defaults to DataLoader.DEFAULT_RESOURCES_PATH)
        year: Year for data files (defaults to current year)
        output_dir: Directory to save output files (defaults to './output')

    Returns:
        Dictionary with counts of matched, unmatched, and ambiguous players
    """
    output_dir = output_dir or "./output"

    logger.info("Starting player universe transformation")

    # Initialize data loader
    loader = DataLoader(resources_path=resources_path, year=year)

    # Load ESPN player data
    logger.info("Loading ESPN player data...")
    espn_batters_raw = loader.load_espn_batters()
    espn_pitchers_raw = loader.load_espn_pitchers()

    # Create player models from ESPN data
    logger.info("Creating player models from ESPN data...")
    espn_batters = create_espn_batter_models(espn_batters_raw)
    espn_pitchers = create_espn_pitcher_models(espn_pitchers_raw)

    # Load FanGraphs player data (raw dicts for matching)
    logger.info("Loading FanGraphs player data...")
    fangraphs_batters_raw = loader.load_fangraphs_batters()
    fangraphs_pitchers_raw = loader.load_fangraphs_pitchers()
    logger.info("Creating player models from FanGraphs data...")
    fangraphs_batters = create_fangraphs_batter_models(fangraphs_batters_raw)
    fangraphs_pitchers = create_fangraphs_pitcher_models(fangraphs_pitchers_raw)

    # Load Savant player data (raw dicts for matching)
    logger.info("Loading Savant player data...")
    savant_batters_raw = loader.load_savant_batters()
    savant_pitchers_raw = loader.load_savant_pitchers()
    logger.info("Creating player models from Savant data...")
    savant_batters = create_savant_batter_models(savant_batters_raw)
    savant_pitchers = create_savant_pitcher_models(savant_pitchers_raw)

    # Match batters
    logger.info("Matching batters across ESPN, FanGraphs, and Savant...")
    batter_matcher = PlayerMatcher(
        espn_players=espn_batters,
        fangraphs_data=fangraphs_batters,
        savant_data=savant_batters,
    )
    batter_results = batter_matcher.match_players()
    batter_merged = apply_matches(batter_results)

    # Match pitchers
    logger.info("Matching pitchers across ESPN, FanGraphs, and Savant...")
    pitcher_matcher = PlayerMatcher(
        espn_players=espn_pitchers,
        fangraphs_data=fangraphs_pitchers,
        savant_data=savant_pitchers,
    )
    pitcher_results = pitcher_matcher.match_players()
    pitcher_merged = apply_matches(pitcher_results)

    # Combine results
    matched_players = batter_merged["matched"] + pitcher_merged["matched"]
    unmatched_players = batter_merged["unmatched"] + pitcher_merged["unmatched"]
    ambiguous_players = batter_merged["ambiguous"] + pitcher_merged["ambiguous"]

    # Report statistics
    logger.info("=" * 60)
    logger.info("Matching complete!")
    logger.info("=" * 60)
    logger.info(f"Total players processed: {len(espn_batters) + len(espn_pitchers)}")
    logger.info(f"  Batters: {len(espn_batters)}")
    logger.info(f"  Pitchers: {len(espn_pitchers)}")
    logger.info("")
    logger.info(f"Successfully matched: {len(matched_players)}")
    logger.info(f"  Batters: {len(batter_merged['matched'])}")
    logger.info(f"  Pitchers: {len(pitcher_merged['matched'])}")
    logger.info("")
    logger.info(f"Unmatched players: {len(unmatched_players)}")
    logger.info(f"  Batters: {len(batter_merged['unmatched'])}")
    logger.info(f"  Pitchers: {len(pitcher_merged['unmatched'])}")
    logger.info("")
    logger.info(f"Ambiguous matches: {len(ambiguous_players)}")
    logger.info(f"  Batters: {len(batter_merged['ambiguous'])}")
    logger.info(f"  Pitchers: {len(pitcher_merged['ambiguous'])}")

    # Report match method breakdown
    _report_match_statistics(batter_results, pitcher_results)

    # Save results to output directory
    logger.info("Saving results...")
    save_results(matched_players, unmatched_players, ambiguous_players, output_dir)

    logger.info("=" * 60)
    logger.info("Player universe transformation complete")
    logger.info("=" * 60)

    return {
        "matched": len(matched_players),
        "unmatched": len(unmatched_players),
        "ambiguous": len(ambiguous_players),
    }


def _report_match_statistics(batter_results, pitcher_results):
    """Report detailed statistics about match methods and confidence levels."""
    from collections import Counter

    all_results = batter_results + pitcher_results

    # Count by match method
    method_counts = Counter(r.match_method for r in all_results)

    # Count by confidence level
    confidence_counts = Counter(r.confidence for r in all_results)

    # Count Savant matches
    savant_matches = sum(1 for r in all_results if r.savant_match is not None)

    logger.info("")
    logger.info("Match Method Breakdown:")
    for method, count in sorted(
        method_counts.items(), key=lambda x: x[1], reverse=True
    ):
        percentage = (count / len(all_results)) * 100 if all_results else 0
        logger.info(f"  {method.value:15s}: {count:4d} ({percentage:5.1f}%)")

    logger.info("")
    logger.info("Confidence Level Breakdown:")
    for confidence, count in sorted(
        confidence_counts.items(), key=lambda x: x[0].value, reverse=True
    ):
        percentage = (count / len(all_results)) * 100 if all_results else 0
        logger.info(
            f"  {confidence.name:10s} ({confidence.value:3d}): {count:4d} ({percentage:5.1f}%)"
        )

    logger.info("")
    logger.info("Savant Data Enrichment:")
    savant_percentage = (savant_matches / len(all_results)) * 100 if all_results else 0
    logger.info(
        f"  Players with Savant data: {savant_matches} ({savant_percentage:.1f}%)"
    )
    logger.info("")


if __name__ == "__main__":
    # Default to 2025 for now since that's the latest data we have
    main(year=2025)
