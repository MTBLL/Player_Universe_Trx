import re
from typing import Any, Dict, Optional

from pydantic import BaseModel, model_validator

from player_universe_trx.models.espn.espn_player import EspnPlayerModel
from player_universe_trx.models.espn.stats import EspnBatterStatsModel

_PREVIOUS_SEASON_WIRE_RE = re.compile(r"^previous_season_\d{2}$")


class EspnBatterStatsGroupModel(BaseModel):
    """Container for all batter stat periods.

    The upstream ESPN extractor emits the prior-season key with a year suffix
    (`previous_season_{YY}` — e.g. `previous_season_25` during the 2026 season,
    `previous_season_24` during 2025). The pre-validator below maps whichever
    suffixed key the wire emits onto a stable `previous_season` field so
    downstream consumers don't have to migrate every season.
    """

    projections: Optional[EspnBatterStatsModel] = None
    current_season: Optional[EspnBatterStatsModel] = None
    previous_season: Optional[EspnBatterStatsModel] = None
    last_7_games: Optional[EspnBatterStatsModel] = None
    last_15_games: Optional[EspnBatterStatsModel] = None
    last_30_games: Optional[EspnBatterStatsModel] = None

    @model_validator(mode="before")
    @classmethod
    def _map_previous_season_wire_key(cls, data: Any) -> Any:
        """Move `previous_season_{YY}` from the wire into `previous_season`.

        Picks the first matching key (the wire only emits one per snapshot).
        If both `previous_season` and a year-suffixed key are present, the
        explicit `previous_season` wins.
        """
        if not isinstance(data, dict):
            return data
        if data.get("previous_season") is not None:
            return data
        for key in list(data.keys()):
            if _PREVIOUS_SEASON_WIRE_RE.match(key):
                data["previous_season"] = data.pop(key)
                break
        return data


class EspnBatterModel(EspnPlayerModel):
    """ESPN batter model with batter-specific statistics."""

    stats: Optional[EspnBatterStatsGroupModel] = None
