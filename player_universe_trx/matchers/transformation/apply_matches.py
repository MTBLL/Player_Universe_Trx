"""Apply player matches into source-bundled MTBL models.

This module turns `PlayerMatchResult` objects (produced by PlayerMatcher) into
typed `MtblBatterModel` / `MtblPitcherModel` instances whose `.stats` carries
three source-by-source bundles: `espn`, `fangraphs`, `savant`. Each bundle is
a thin re-projection of the matched source's raw model — no cross-source
merging happens here, so consumers reach for the source they care about
(e.g. `stats.espn.current_season.HR` for actuals, `stats.fangraphs.ros.HR`
for rest-of-season projection, `stats.savant.all.xwOBA` for sabermetrics).
"""

from typing import Any, Dict, List, Optional, Sequence, Tuple

from typing_extensions import TYPE_CHECKING

from player_universe_trx.matchers.models import MatchConfidence, PlayerMatchResult
from player_universe_trx.models.espn import (
    EspnBatterModel,
    EspnBatterStatsGroupModel,
    EspnPitcherStatsGroupModel,
)
from player_universe_trx.models.fangraphs import (
    FangraphsBatterModel,
    FangraphsPitcherModel,
    FangraphsPlayerModel,
)
from player_universe_trx.models.mtbl import (
    MtblBatterFangraphsBundle,
    MtblBatterModel,
    MtblBatterSavantBundle,
    MtblBatterStatsModel,
    MtblPitcherFangraphsBundle,
    MtblPitcherModel,
    MtblPitcherSavantBundle,
    MtblPitcherStatsModel,
    MtblPlayerModel,
)
from player_universe_trx.models.savant import SavantBatterModel, SavantPitcherModel

if TYPE_CHECKING:  # pragma: no cover
    from player_universe_trx.models.espn import (
        EspnBatterModel,
        EspnPitcherModel,
    )
    from player_universe_trx.models.fangraphs import (
        FangraphsBatterModel,
        FangraphsPitcherModel,
    )
    from player_universe_trx.models.savant import SavantBatterModel, SavantPitcherModel


def _coerce_empty_to_none(model: Any) -> Any:
    """Collapse an all-None pydantic model into None.

    Upstream FanGraphs emits `{}` for projection slots whose endpoint hasn't
    published yet — those round-trip into pydantic models whose
    `model_dump(exclude_none=True)` is `{}`. Downstream consumers treat
    "no data" as None, so we coerce the empty model to None here.
    """
    if model is None:
        return None
    if not model.model_dump(exclude_none=True):
        return None
    return model


def _build_fangraphs_bundle(
    fg_match: Optional["FangraphsBatterModel | FangraphsPitcherModel"],
    is_batter: bool,
) -> Optional["MtblBatterFangraphsBundle | MtblPitcherFangraphsBundle"]:
    """Project a Fangraphs raw model into the MTBL FanGraphs bundle.

    Returns None when there's no FanGraphs match OR when the match's three
    slots all coerce to None (identity-only match with no projection data
    published yet — typical pre-draft for projs_updated and ros).
    """
    if fg_match is None:
        return None

    preseason = _coerce_empty_to_none(fg_match.projections)
    updated = _coerce_empty_to_none(fg_match.projs_updated)
    ros = _coerce_empty_to_none(fg_match.ros)
    if preseason is None and updated is None and ros is None:
        return None

    if is_batter:
        return MtblBatterFangraphsBundle(
            projections=preseason,
            projs_updated=updated,
            ros=ros,
        )
    return MtblPitcherFangraphsBundle(
        projections=preseason,
        projs_updated=updated,
        ros=ros,
    )


def _build_savant_bundle(
    savant_match: Optional["SavantBatterModel | SavantPitcherModel"],
    is_batter: bool,
) -> Optional["MtblBatterSavantBundle | MtblPitcherSavantBundle"]:
    """Project a SavantBatter/PitcherModel into the MTBL Savant bundle.

    Field types match 1:1 between the raw Savant model and the MTBL bundle.
    Returns None when there's no Savant match.

    Args:
        savant_match: Savant player model with per-split + sub-domain data.
        is_batter: Selects the bundle class and which role-only field
            (`sprint_speed` vs `expected_statistics`) to surface.
    """
    if savant_match is None:
        return None

    # Narrow the union via isinstance up front; both branches then use direct
    # typed access (mypy can't bridge the is_batter flag to the union arm).
    if is_batter:
        assert isinstance(savant_match, SavantBatterModel)
        arsenal_b = list(savant_match.pitch_arsenal or [])
        if not any(
            [
                savant_match.all is not None,
                savant_match.vs_r is not None,
                savant_match.vs_l is not None,
                savant_match.statcast is not None,
                savant_match.home_runs is not None,
                arsenal_b,
                savant_match.sprint_speed is not None,
                savant_match.swing_take is not None,
            ]
        ):
            return None
        return MtblBatterSavantBundle(
            all=savant_match.all,
            vs_r=savant_match.vs_r,
            vs_l=savant_match.vs_l,
            statcast=savant_match.statcast,
            home_runs=savant_match.home_runs,
            pitch_arsenal=arsenal_b,
            sprint_speed=savant_match.sprint_speed,
            swing_take=savant_match.swing_take,
        )

    assert isinstance(savant_match, SavantPitcherModel)
    arsenal_p = list(savant_match.pitch_arsenal or [])
    if not any(
        [
            savant_match.all is not None,
            savant_match.vs_r is not None,
            savant_match.vs_l is not None,
            savant_match.statcast is not None,
            savant_match.home_runs is not None,
            arsenal_p,
            savant_match.expected_statistics is not None,
            savant_match.swing_take is not None,
        ]
    ):
        return None
    return MtblPitcherSavantBundle(
        all=savant_match.all,
        vs_r=savant_match.vs_r,
        vs_l=savant_match.vs_l,
        statcast=savant_match.statcast,
        home_runs=savant_match.home_runs,
        pitch_arsenal=arsenal_p,
        expected_statistics=savant_match.expected_statistics,
        swing_take=savant_match.swing_take,
    )


def _create_player_model(
    base_player: MtblPlayerModel,
    espn_bundle: Optional[EspnBatterStatsGroupModel | EspnPitcherStatsGroupModel],
    fangraphs_bundle: Optional[
        "MtblBatterFangraphsBundle | MtblPitcherFangraphsBundle"
    ],
    savant_bundle: Optional["MtblBatterSavantBundle | MtblPitcherSavantBundle"],
    is_batter: bool,
) -> MtblPlayerModel:
    """Assemble the typed MtblBatter/PitcherModel from three source bundles.

    The output's `.stats` carries exactly three optional fields — `espn`,
    `fangraphs`, `savant`. When all three bundles are None (and there's no
    ESPN container either), `.stats` itself stays None.

    Args:
        base_player: Base MTBL player model (identity / fantasy-team fields).
        espn_bundle: ESPN stats container (current_season + projections +
            last_*_games + previous_season), or None.
        fangraphs_bundle: Pre-built MTBL FanGraphs bundle, or None.
        savant_bundle: Pre-built MTBL Savant bundle, or None.
        is_batter: Selects MtblBatterModel vs MtblPitcherModel.
    """
    base_data: Dict[str, Any] = base_player.model_dump()
    has_any = espn_bundle is not None or fangraphs_bundle is not None or savant_bundle is not None

    if is_batter:
        batter_stats: Optional[MtblBatterStatsModel] = None
        if has_any:
            batter_espn: Optional[EspnBatterStatsGroupModel] = (
                espn_bundle
                if isinstance(espn_bundle, EspnBatterStatsGroupModel)
                else None
            )
            batter_fg: Optional[MtblBatterFangraphsBundle] = (
                fangraphs_bundle
                if isinstance(fangraphs_bundle, MtblBatterFangraphsBundle)
                else None
            )
            batter_sav: Optional[MtblBatterSavantBundle] = (
                savant_bundle
                if isinstance(savant_bundle, MtblBatterSavantBundle)
                else None
            )
            batter_stats = MtblBatterStatsModel(
                espn=batter_espn,
                fangraphs=batter_fg,
                savant=batter_sav,
            )
        return MtblBatterModel(**base_data, stats=batter_stats)

    pitcher_stats: Optional[MtblPitcherStatsModel] = None
    if has_any:
        pitcher_espn: Optional[EspnPitcherStatsGroupModel] = (
            espn_bundle
            if isinstance(espn_bundle, EspnPitcherStatsGroupModel)
            else None
        )
        pitcher_fg: Optional[MtblPitcherFangraphsBundle] = (
            fangraphs_bundle
            if isinstance(fangraphs_bundle, MtblPitcherFangraphsBundle)
            else None
        )
        pitcher_sav: Optional[MtblPitcherSavantBundle] = (
            savant_bundle
            if isinstance(savant_bundle, MtblPitcherSavantBundle)
            else None
        )
        pitcher_stats = MtblPitcherStatsModel(
            espn=pitcher_espn,
            fangraphs=pitcher_fg,
            savant=pitcher_sav,
        )
    return MtblPitcherModel(**base_data, stats=pitcher_stats)


def apply_matches(results: List[PlayerMatchResult]) -> Dict[str, List]:
    """
    Apply matches: assemble source-bundled MTBL models from PlayerMatchResults.

    Each output player carries three source bundles under `.stats`:
      - `espn`:      ESPN periods (current_season / projections / last_* / previous_season)
      - `fangraphs`: FanGraphs projection slots (projections / projs_updated / ros)
      - `savant`:    Savant splits + sub-domains (all/vs_r/vs_l + statcast/HR/arsenal/...)

    No cross-source merging happens — each bundle is a thin re-projection of
    the matched source's raw model.

    Args:
        results: List of PlayerMatchResult objects from PlayerMatcher.match_players()

    Returns:
        Dictionary with categorized results:
        - 'matched':   List of MtblBatter/PitcherModel with FG (and optionally Savant) matches.
        - 'ambiguous': List of (MtblPlayerModel, candidates) tuples for manual review.
        - 'unmatched': List of MtblBatter/PitcherModel with no FG match.
    """
    matched: List[MtblPlayerModel] = []
    ambiguous: List[Tuple[MtblPlayerModel, Sequence[FangraphsPlayerModel]]] = []
    unmatched: List[MtblPlayerModel] = []

    for result in results:
        # Skip retired players (they cannot be serialized to MtblPlayerModel)
        if result.espn_player.status == "retired":
            continue

        is_batter: bool = isinstance(result.espn_player, EspnBatterModel)

        # Convert ESPN player to base MtblPlayerModel
        espn_data: Dict[str, Any] = result.espn_player.model_dump(exclude_none=True)
        if "on_team_id" in espn_data:
            espn_data["fantasy_team"] = espn_data.pop("on_team_id")
        if "draft_auction_value" in espn_data:
            espn_data["draft_value"] = espn_data.pop("draft_auction_value")
        base_player: MtblPlayerModel = MtblPlayerModel.model_validate(espn_data)

        espn_bundle: Optional[
            EspnBatterStatsGroupModel | EspnPitcherStatsGroupModel
        ] = (result.espn_player.stats if result.espn_player.stats else None)

        # Ambiguous matches carry ESPN data only — FG and Savant bundles stay
        # None since we haven't resolved which match candidate is correct.
        if result.confidence == MatchConfidence.AMBIGUOUS:
            ambiguous_player: MtblPlayerModel = _create_player_model(
                base_player=base_player,
                espn_bundle=espn_bundle,
                fangraphs_bundle=None,
                savant_bundle=None,
                is_batter=is_batter,
            )
            ambiguous.append((ambiguous_player, result.candidates))
            continue

        is_matched: bool = result.fangraphs_match is not None

        # Merge FanGraphs ID/route metadata onto the base player (matched only)
        if is_matched:
            base_player.merge_fangraphs_data(result.fangraphs_match)

        fangraphs_bundle: Optional[
            "MtblBatterFangraphsBundle | MtblPitcherFangraphsBundle"
        ] = (
            _build_fangraphs_bundle(result.fangraphs_match, is_batter)
            if is_matched
            else None
        )

        savant_bundle: Optional["MtblBatterSavantBundle | MtblPitcherSavantBundle"] = (
            _build_savant_bundle(result.savant_match, is_batter) if is_matched else None
        )

        player_model: MtblPlayerModel = _create_player_model(
            base_player=base_player,
            espn_bundle=espn_bundle,
            fangraphs_bundle=fangraphs_bundle,
            savant_bundle=savant_bundle,
            is_batter=is_batter,
        )

        if is_matched:
            matched.append(player_model)
        else:
            unmatched.append(player_model)

    return {"matched": matched, "ambiguous": ambiguous, "unmatched": unmatched}
