from player_universe_trx.models.espn import (
    EspnBatterModel,
    EspnBatterStatsModel,
    EspnPitcherModel,
    EspnPitcherStatsModel,
)


def test_batter_model_validation(sample_batter):
    """Test EspnBatterModel validates real fixture data."""
    batter = EspnBatterModel.model_validate(sample_batter)

    assert batter.id == sample_batter["id"]
    assert batter.name == sample_batter["name"]
    assert batter.primary_position == sample_batter["primary_position"]
    assert batter.stats is not None
    assert batter.stats.projections is not None


def test_pitcher_model_validation(sample_pitcher):
    """Test EspnPitcherModel validates real fixture data."""
    pitcher = EspnPitcherModel.model_validate(sample_pitcher)

    assert pitcher.id == sample_pitcher["id"]
    assert pitcher.name == sample_pitcher["name"]
    assert pitcher.primary_position == sample_pitcher["primary_position"]
    assert pitcher.stats is not None
    assert pitcher.stats.projections is not None


def test_batter_stats_model(sample_batter):
    """Test EspnBatterStatsModel with projection data."""
    stats = EspnBatterStatsModel.model_validate(sample_batter["stats"]["projections"])

    assert stats.AB is not None
    assert stats.H is not None
    assert stats.AVG is not None
    assert stats.HR is not None
    assert stats.RBI is not None


def test_pitcher_stats_model(sample_pitcher):
    """Test EspnPitcherStatsModel with projection data."""
    stats = EspnPitcherStatsModel.model_validate(sample_pitcher["stats"]["projections"])

    assert stats.W is not None
    assert stats.ERA is not None
    assert stats.K is not None
    assert stats.WHIP is not None


def test_batter_model_all_stat_periods(espn_batter_data):
    """Test all stat periods load correctly for batters."""
    batter = EspnBatterModel.model_validate(espn_batter_data[0])

    assert batter.stats is not None
    assert batter.stats.projections is not None
    assert batter.stats.current_season is not None
    assert batter.stats.previous_season_24 is not None
    assert batter.stats.last_7_games is not None
    assert batter.stats.last_15_games is not None
    assert batter.stats.last_30_games is not None


def test_pitcher_model_all_stat_periods(espn_pitcher_data):
    """Test all stat periods load correctly for pitchers."""
    pitcher = EspnPitcherModel.model_validate(espn_pitcher_data[0])

    assert pitcher.stats is not None
    assert pitcher.stats.projections is not None
    assert pitcher.stats.current_season is not None
    assert pitcher.stats.previous_season_24 is not None
    assert pitcher.stats.last_7_games is not None
    assert pitcher.stats.last_15_games is not None
    assert pitcher.stats.last_30_games is not None


def test_batter_nested_models(sample_batter):
    """Test nested models in batter data."""
    batter = EspnBatterModel.model_validate(sample_batter)

    assert batter.birth_place is not None
    assert batter.birth_place.country is not None
    assert batter.draft_ranks is not None
    assert batter.transactions is not None
    assert len(batter.transactions) > 0


def test_pitcher_nested_models(sample_pitcher):
    """Test nested models in pitcher data."""
    pitcher = EspnPitcherModel.model_validate(sample_pitcher)

    assert pitcher.birth_place is not None
    assert pitcher.birth_place.country is not None
    assert pitcher.draft_ranks is not None
    assert pitcher.transactions is not None
    assert len(pitcher.transactions) > 0
