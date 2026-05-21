"""Transform ESPN league data to MTBL format."""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from player_universe_trx.constants import (
    ESPN_LINEUP_SLOT_MAP,
    ESPN_POSITION_MAP,
    ESPN_PRO_TEAM_MAP,
)
from player_universe_trx.models.espn import (
    EspnLeagueModel,
    EspnRosterEntryModel,
    EspnScheduleMatchupModel,
    EspnTeamModel,
)
from player_universe_trx.models.mtbl import (
    CategoryResultModel,
    GamesStartedLimitsModel,
    GamesStartedModel,
    MtblLeagueModel,
    MtblScheduleModel,
    MtblTeamRosterModel,
    RosterSettingsModel,
    RosterSlotPlayer,
    ScheduleMatchupModel,
    ScoringCategoriesModel,
    ScoringCategoryModel,
    TeamRecordModel,
    TransactionSummaryModel,
)

logger = logging.getLogger(__name__)


class LeagueTransformer:
    """
    Transform ESPN league data to MTBL format.

    Handles mapping of position IDs to names, pro team IDs to abbreviations,
    and organizing players by roster slot type.
    """

    @staticmethod
    def _get_position_name(position_id: int) -> str:
        """
        Convert ESPN position ID to position name.

        Args:
            position_id: ESPN position ID

        Returns:
            Position name (e.g., "C", "1B", "OF", "SP")
        """
        return ESPN_POSITION_MAP.get(position_id, f"POS_{position_id}")

    @staticmethod
    def _get_lineup_slot_name(slot_id: int) -> str:
        """
        Convert ESPN lineup slot ID to slot name.

        Args:
            slot_id: ESPN lineup slot ID

        Returns:
            Lineup slot name (e.g., "C", "OF", "SP", "BENCH", "IL")
        """
        return ESPN_LINEUP_SLOT_MAP.get(slot_id, f"SLOT_{slot_id}")

    @staticmethod
    def _get_pro_team_abbrev(team_id: int) -> str:
        """
        Convert ESPN pro team ID to MLB team abbreviation.

        Args:
            team_id: ESPN pro team ID

        Returns:
            MLB team abbreviation (e.g., "NYY", "LAD", "BOS")
        """
        return ESPN_PRO_TEAM_MAP.get(team_id, f"TEAM_{team_id}")

    @staticmethod
    def _get_eligible_positions(eligible_slot_ids: List[int]) -> List[str]:
        """
        Convert list of ESPN eligible slot IDs to position names.

        Args:
            eligible_slot_ids: List of ESPN slot IDs

        Returns:
            List of position names
        """
        positions = []
        for slot_id in eligible_slot_ids:
            pos = ESPN_LINEUP_SLOT_MAP.get(slot_id)
            if pos and pos not in positions:
                positions.append(pos)
        return positions

    @staticmethod
    def _format_acquisition_date(timestamp: int) -> str:
        """
        Convert Unix timestamp (milliseconds) to ISO format date string.

        Args:
            timestamp: Unix timestamp in milliseconds

        Returns:
            ISO format date string
        """
        try:
            dt = datetime.fromtimestamp(timestamp / 1000)
            return dt.isoformat() + "Z"
        except (ValueError, OSError):
            return ""

    @classmethod
    def _build_eligible_date_by_position(
        cls, eligible_dates: Optional[Dict[str, int]]
    ) -> Optional[Dict[str, str]]:
        """
        Map ESPN ``eligibleDateByPosition`` to MTBL-native names and dates.

        ESPN keys this by numeric slot ID with epoch-millisecond values.
        MTBL surfaces position names with ISO date strings, consistent with
        ``eligible_positions`` and ``acquisition_date``.

        Args:
            eligible_dates: ESPN ``slot_id`` -> epoch-ms map, or None

        Returns:
            ``position_name`` -> ISO date string map, or None when absent
        """
        if not eligible_dates:
            return None
        return {
            cls._get_lineup_slot_name(int(slot_id)): cls._format_acquisition_date(ts)
            for slot_id, ts in eligible_dates.items()
        }

    @classmethod
    def _create_roster_slot_player(
        cls, entry: EspnRosterEntryModel
    ) -> RosterSlotPlayer:
        """
        Create a RosterSlotPlayer from an ESPN roster entry.

        Args:
            entry: ESPN roster entry

        Returns:
            RosterSlotPlayer with minimal player data
        """
        player = entry.playerPoolEntry.player
        lineup_slot = cls._get_lineup_slot_name(entry.lineupSlotId)

        # Split full name into first and last (simple split on space)
        name_parts = player.fullName.split(" ", 1)
        first_name = name_parts[0] if len(name_parts) > 0 else None
        last_name = name_parts[1] if len(name_parts) > 1 else None

        return RosterSlotPlayer(
            player_id=player.id,
            name=player.fullName,
            first_name=first_name,
            last_name=last_name,
            pro_team=cls._get_pro_team_abbrev(player.proTeamId),
            primary_position=cls._get_position_name(player.defaultPositionId),
            eligible_positions=cls._get_eligible_positions(player.eligibleSlots),
            lineup_slot=lineup_slot,
            acquisition_type=entry.acquisitionType,
            acquisition_date=(
                cls._format_acquisition_date(entry.acquisitionDate)
                if entry.acquisitionDate
                else None
            ),
            injury_status=player.injuryStatus,
            active=player.active,
            keeper_value=entry.playerPoolEntry.keeperValue,
            jersey=player.jersey,
            eligible_date_by_position=cls._build_eligible_date_by_position(
                player.eligibleDateByPosition
            ),
        )

    @classmethod
    def _organize_roster_by_slots(
        cls, roster_entries: List[EspnRosterEntryModel]
    ) -> Dict[str, List[RosterSlotPlayer]]:
        """
        Organize roster entries by position slot type.

        Args:
            roster_entries: List of ESPN roster entries

        Returns:
            Dictionary mapping slot names to lists of players
        """
        # Group players by lineup slot type
        roster_by_slot: Dict[str, List[RosterSlotPlayer]] = defaultdict(list)

        for entry in roster_entries:
            slot_name = cls._get_lineup_slot_name(entry.lineupSlotId)
            player = cls._create_roster_slot_player(entry)
            roster_by_slot[slot_name].append(player)

        return roster_by_slot

    @classmethod
    def _create_team_record(cls, espn_team: EspnTeamModel) -> TeamRecordModel:
        """
        Create a TeamRecordModel from ESPN team record.

        Args:
            espn_team: ESPN team model

        Returns:
            TeamRecordModel with record summary
        """
        if not espn_team.record or not espn_team.record.overall:
            return TeamRecordModel()

        overall = espn_team.record.overall
        return TeamRecordModel(
            wins=overall.wins,
            losses=overall.losses,
            ties=overall.ties,
            percentage=overall.percentage,
            games_back=overall.gamesBack,
        )

    @classmethod
    def _create_transaction_summary(
        cls,
        espn_team: EspnTeamModel,
        league_budget: Optional[int] = None,
    ) -> Optional[TransactionSummaryModel]:
        """
        Create transaction summary from ESPN team.

        Args:
            espn_team: ESPN team model
            league_budget: League acquisition budget

        Returns:
            TransactionSummaryModel or None
        """
        if not espn_team.transactionCounter:
            return None

        tc = espn_team.transactionCounter
        budget_remaining = None
        if league_budget is not None:
            budget_remaining = league_budget - tc.acquisitionBudgetSpent

        return TransactionSummaryModel(
            budget_spent=tc.acquisitionBudgetSpent,
            budget_remaining=budget_remaining,
            acquisitions=tc.acquisitions,
            drops=tc.drops,
            trades=tc.trades,
            waiver_rank=espn_team.waiverRank,
        )

    @classmethod
    def transform_team(
        cls,
        espn_team: EspnTeamModel,
        league_id: int,
        season_id: int,
        league_budget: Optional[int] = None,
    ) -> MtblTeamRosterModel:
        """
        Transform an ESPN team to MTBL team roster model.

        Args:
            espn_team: ESPN team model
            league_id: League ID
            season_id: Season ID
            league_budget: League acquisition budget

        Returns:
            MtblTeamRosterModel with organized roster
        """
        # Organize roster by slot type
        roster_by_slot = cls._organize_roster_by_slots(espn_team.roster.entries)

        # Extract team record
        record = cls._create_team_record(espn_team)

        # Extract transaction summary
        transactions = cls._create_transaction_summary(espn_team, league_budget)

        # Build the team roster model with explicit position fields
        team_roster = MtblTeamRosterModel(
            league_id=league_id,
            season_id=season_id,
            team_id=espn_team.id,
            team_name=espn_team.name,
            team_abbrev=espn_team.abbrev,
            team_logo=espn_team.logo,
            owners=espn_team.owners,
            primary_owner=espn_team.primaryOwner,
            record=record,
            transactions=transactions,
            # Single-player positions (take first player if multiple)
            c=roster_by_slot.get("C", [None])[0],
            first_base=roster_by_slot.get("1B", [None])[0],
            second_base=roster_by_slot.get("2B", [None])[0],
            third_base=roster_by_slot.get("3B", [None])[0],
            shortstop=roster_by_slot.get("SS", [None])[0],
            util=roster_by_slot.get("UTIL", [None])[0],
            # Multi-player positions (arrays)
            outfield=roster_by_slot.get("OF", []),
            sp=roster_by_slot.get("SP", []),
            rp=roster_by_slot.get("RP", []),
            bench=roster_by_slot.get("BENCH", []),
            injured_list=roster_by_slot.get("IL", []),
        )

        logger.info(
            f"Transformed team {espn_team.id} ({espn_team.name}) with {len(espn_team.roster.entries)} roster entries"
        )
        return team_roster

    @classmethod
    def transform_league(
        cls, espn_league: EspnLeagueModel
    ) -> List[MtblTeamRosterModel]:
        """
        Transform ESPN league to list of MTBL team roster models.

        Args:
            espn_league: ESPN league model

        Returns:
            List of MtblTeamRosterModel, one per team
        """
        logger.info(
            f"Transforming league {espn_league.id} with {len(espn_league.teams)} teams"
        )

        # Get league budget if available
        league_budget = None
        if espn_league.settings and espn_league.settings.acquisitionSettings:
            league_budget = espn_league.settings.acquisitionSettings.acquisitionBudget

        team_rosters = []
        for espn_team in espn_league.teams:
            team_roster = cls.transform_team(
                espn_team, espn_league.id, espn_league.seasonId, league_budget
            )
            team_rosters.append(team_roster)

        logger.info(f"Successfully transformed {len(team_rosters)} teams")
        return team_rosters

    @classmethod
    def create_league_summary(cls, espn_league: EspnLeagueModel) -> MtblLeagueModel:
        """
        Create a league summary model from ESPN league.

        Args:
            espn_league: ESPN league model

        Returns:
            MtblLeagueModel with league summary
        """
        roster_settings = None
        if espn_league.settings and espn_league.settings.rosterSettings:
            roster_settings = RosterSettingsModel(
                lineup_slot_counts=espn_league.settings.rosterSettings.lineupSlotCounts,
                roster_size=espn_league.settings.rosterSettings.rosterSize,
            )

        # Extract scoring categories
        scoring_categories = None
        if espn_league.settings and espn_league.settings.scoringSettings:
            scoring_settings = espn_league.settings.scoringSettings
            batting_cats = [
                ScoringCategoryModel(
                    stat_id=cat.statId,
                    name=cat.name,
                    is_reverse=cat.isReverseItem,
                )
                for cat in scoring_settings.categories.batting
            ]
            pitching_cats = [
                ScoringCategoryModel(
                    stat_id=cat.statId,
                    name=cat.name,
                    is_reverse=cat.isReverseItem,
                )
                for cat in scoring_settings.categories.pitching
            ]
            scoring_categories = ScoringCategoriesModel(
                batting=batting_cats, pitching=pitching_cats
            )

        # Extract games-started limits (pitcher start cap)
        games_started_limits = None
        if espn_league.settings and espn_league.settings.gamesStartedLimits:
            limits = espn_league.settings.gamesStartedLimits
            games_started_limits = GamesStartedLimitsModel(
                stat_id=limits.statId,
                min=limits.min,
                max_per_scoring_period=limits.maxPerScoringPeriod,
                max_per_matchup=limits.maxPerMatchup,
            )

        # Get acquisition budget
        acquisition_budget = None
        if espn_league.settings and espn_league.settings.acquisitionSettings:
            acquisition_budget = (
                espn_league.settings.acquisitionSettings.acquisitionBudget
            )

        # Get draft auction budget
        draft_auction_budget = None
        if espn_league.settings and espn_league.settings.draftSettings:
            draft_auction_budget = espn_league.settings.draftSettings.auctionBudget

        # Preserve upstream league name from ESPN settings
        league_name = None
        if espn_league.settings:
            league_name = espn_league.settings.name

        return MtblLeagueModel(
            league_id=espn_league.id,
            league_name=league_name,
            season_id=espn_league.seasonId,
            scoring_period_id=espn_league.scoringPeriodId,
            num_teams=len(espn_league.teams),
            roster_settings=roster_settings,
            scoring_categories=scoring_categories,
            games_started_limits=games_started_limits,
            acquisition_budget=acquisition_budget,
            draft_auction_budget=draft_auction_budget,
        )

    @staticmethod
    def _build_category_name_map(espn_league: EspnLeagueModel) -> Dict[str, str]:
        """
        Map stringified ESPN ``stat_id`` -> category name from league scoring
        settings.

        These are the same statId/name pairs that feed
        ``league_scoring_categories``; reusing them keeps matchup categories
        named consistently with every other category surface.

        Args:
            espn_league: ESPN league model

        Returns:
            Dict of ``str(stat_id)`` -> category name; empty when the league
            carries no scoring settings (points/roster-limit leagues)
        """
        name_map: Dict[str, str] = {}
        if espn_league.settings and espn_league.settings.scoringSettings:
            categories = espn_league.settings.scoringSettings.categories
            for cat in (*categories.batting, *categories.pitching):
                name_map[str(cat.statId)] = cat.name
        return name_map

    @staticmethod
    def _resolve_category_name(key: str, name_map: Dict[str, str]) -> str:
        """
        Resolve a ``categoryResults`` inner key to a category name.

        Upstream ESPN extracts now key the per-category breakdown by numeric
        ``stat_id`` (e.g. ``"20"``, ``"5"``); older exports keyed by name
        (``"R"``, ``"HR"``). Numeric keys are resolved via the league's
        scoring-category map. Any non-numeric key -- a name from an older
        export, or the ``"BYE"`` sentinel -- passes through unchanged. An
        unmapped numeric key falls back to the raw id so data is never
        silently dropped.

        Args:
            key: Raw ``categoryResults`` inner key
            name_map: ``str(stat_id)`` -> name map from
                :meth:`_build_category_name_map`

        Returns:
            The resolved category name
        """
        if not key.isdigit():
            return key
        resolved = name_map.get(key)
        if resolved is None:
            logger.warning(
                "matchup category stat_id %s not in league scoring "
                "settings; emitting raw id",
                key,
            )
            return key
        return resolved

    @classmethod
    def _extract_team_categories(
        cls,
        matchup: EspnScheduleMatchupModel,
        team_key: Optional[str],
        category_name_map: Dict[str, str],
    ) -> Optional[List[CategoryResultModel]]:
        """
        Extract a team's per-category results from an ESPN matchup.

        Args:
            matchup: ESPN schedule matchup
            team_key: Team ID as a string key (categoryResults is keyed by
                stringified team IDs, matching the ``teams`` mapping)
            category_name_map: ``str(stat_id)`` -> name map used to resolve
                numeric category keys back to names

        Returns:
            List of CategoryResultModel, or None for points/roster-limit
            leagues where ESPN provides no per-category breakdown
        """
        if not matchup.categoryResults or team_key is None:
            return None
        team_categories = matchup.categoryResults.get(team_key)
        if not team_categories:
            return None
        # Prefer the category name the extractor now emits inline; fall back
        # to resolving the numeric stat_id key for older extracts.
        return [
            CategoryResultModel(
                category=(
                    result.name
                    or cls._resolve_category_name(key, category_name_map)
                ),
                value=result.value,
                result=result.result,
            )
            for key, result in team_categories.items()
        ]

    @staticmethod
    def _extract_team_games_started(
        matchup: EspnScheduleMatchupModel, team_key: Optional[str]
    ) -> Optional[GamesStartedModel]:
        """
        Extract a team's games-started tally from an ESPN matchup.

        Args:
            matchup: ESPN schedule matchup
            team_key: Team ID as a string key (gamesStarted is keyed by
                stringified team IDs, matching the ``teams`` mapping)

        Returns:
            GamesStartedModel, or None for leagues without a pitcher start
            cap (no gamesStarted upstream)
        """
        if not matchup.gamesStarted or team_key is None:
            return None
        games_started = matchup.gamesStarted.get(team_key)
        if games_started is None:
            return None
        return GamesStartedModel(
            value=games_started.value,
            limit_exceeded=games_started.limitExceeded,
            exceeded_on_scoring_period=games_started.exceededOnScoringPeriod,
        )

    @classmethod
    def transform_schedule(cls, espn_league: EspnLeagueModel) -> MtblScheduleModel:
        """
        Transform ESPN schedule to MTBL schedule model.

        Args:
            espn_league: ESPN league model

        Returns:
            MtblScheduleModel with matchups
        """
        matchups = []
        category_name_map = cls._build_category_name_map(espn_league)
        for matchup in espn_league.schedule:
            # Determine if this is a playoff matchup
            is_playoff = (
                matchup.playoffTierType != "NONE" if matchup.playoffTierType else False
            )

            # Parse teams
            team_ids = list(matchup.teams.keys())
            is_bye = matchup.winner == "BYE WEEK"

            team1_key = team_ids[0] if team_ids else None
            team2_key = team_ids[1] if len(team_ids) > 1 else None

            team1_id = int(team1_key) if team1_key else None
            team1_score = matchup.teams.get(team1_key) if team1_key else None
            team2_id = int(team2_key) if team2_key else None
            team2_score = matchup.teams.get(team2_key) if team2_key else None

            # Per-category breakdown (H2H category leagues only)
            team1_categories = cls._extract_team_categories(
                matchup, team1_key, category_name_map
            )
            team2_categories = cls._extract_team_categories(
                matchup, team2_key, category_name_map
            )

            # Games-started tally (leagues with a pitcher start cap only)
            team1_games_started = cls._extract_team_games_started(matchup, team1_key)
            team2_games_started = cls._extract_team_games_started(matchup, team2_key)

            # Parse winner
            winner_id = None
            if not is_bye and matchup.winner and isinstance(matchup.winner, int):
                winner_id = matchup.winner

            matchups.append(
                ScheduleMatchupModel(
                    matchup_id=matchup.id,
                    period_id=matchup.matchupPeriodId,
                    is_playoff=is_playoff,
                    team1_id=team1_id,
                    team1_score=team1_score,
                    team2_id=team2_id,
                    team2_score=team2_score,
                    winner_id=winner_id,
                    is_bye_week=is_bye,
                    team1_categories=team1_categories,
                    team2_categories=team2_categories,
                    team1_games_started=team1_games_started,
                    team2_games_started=team2_games_started,
                )
            )

        logger.info(f"Transformed {len(matchups)} schedule matchups")
        return MtblScheduleModel(
            league_id=espn_league.id,
            season_id=espn_league.seasonId,
            matchups=matchups,
        )
