from player_universe_trx.models.espn import (
    EspnBatterModel,
    EspnBatterStatsModel,
    EspnPitcherModel,
    EspnPitcherStatsModel,
)
from player_universe_trx.models.espn.batter import EspnBatterStatsGroupModel


def test_batter_model_validation(sample_batter):
    """Test EspnBatterModel validates real fixture data."""
    batter = EspnBatterModel.model_validate(sample_batter)

    assert batter.id == sample_batter["id"]
    assert batter.name == sample_batter["name"]
    assert batter.primary_position == sample_batter["primary_position"]
    assert batter.stats is not None
    assert batter.stats.projections is not None
    assert batter.on_team_id == sample_batter["on_team_id"]
    assert batter.draft_auction_value == sample_batter["draft_auction_value"]


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
    assert batter.stats.previous_season is not None
    assert batter.stats.last_7_games is not None
    assert batter.stats.last_15_games is not None
    assert batter.stats.last_30_games is not None


def test_pitcher_model_all_stat_periods(espn_pitcher_data):
    """Test all stat periods load correctly for pitchers."""
    pitcher = EspnPitcherModel.model_validate(espn_pitcher_data[0])

    assert pitcher.stats is not None
    assert pitcher.stats.projections is not None
    assert pitcher.stats.current_season is not None
    assert pitcher.stats.previous_season is not None
    assert pitcher.stats.last_7_games is not None
    assert pitcher.stats.last_15_games is not None
    assert pitcher.stats.last_30_games is not None


def test_previous_season_year_suffix_mapped_to_canonical_field():
    """ESPN emits previous_season_{YY}; the model normalizes to `previous_season`.

    Locks in the year-agnostic contract — whatever year-suffixed key the wire
    uses (`_24`, `_25`, `_26`, ...) lands at the same `stats.previous_season`
    path on the model.
    """
    # Each year-suffixed wire key should land at the canonical field
    for suffix in ("24", "25", "26", "30"):
        raw = {
            f"previous_season_{suffix}": {"AB": 480, "HR": 28, "AVG": 0.285},
        }
        m = EspnBatterStatsGroupModel.model_validate(raw)
        assert m.previous_season is not None, f"suffix _{suffix} dropped"
        assert m.previous_season.AB == 480
        assert m.previous_season.HR == 28


def test_previous_season_explicit_wins_over_suffix():
    """If both `previous_season` and a year-suffixed key are present, prefer the explicit one."""
    raw = {
        "previous_season": {"AB": 100},
        "previous_season_24": {"AB": 999},
    }
    m = EspnBatterStatsGroupModel.model_validate(raw)
    assert m.previous_season is not None
    assert m.previous_season.AB == 100


def test_previous_season_validator_passes_non_dict_input_through():
    """The pre-validator guards against non-dict input by returning it unchanged.

    Pydantic normally hands the validator a dict, but the defensive
    `if not isinstance(data, dict): return data` branch means non-dict inputs
    (e.g., something pydantic later rejects, or future revalidation paths
    that hand the validator a model instance) won't crash the validator.
    """
    from player_universe_trx.models.espn.pitcher import EspnPitcherStatsGroupModel

    # Call the validator classmethod directly with non-dict inputs — exercises
    # the early-return branch without depending on how pydantic normalizes
    # external inputs before invoking before-validators.
    for non_dict in (None, "string", 42, ["a", "b"], object()):
        assert (
            EspnBatterStatsGroupModel._map_previous_season_wire_key(non_dict)
            is non_dict
        )
        assert (
            EspnPitcherStatsGroupModel._map_previous_season_wire_key(non_dict)
            is non_dict
        )


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
