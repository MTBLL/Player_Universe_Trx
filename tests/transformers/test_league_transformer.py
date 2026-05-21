import pytest

from player_universe_trx.transformers import league_transformer
from player_universe_trx.models.espn import EspnLeagueModel, EspnRosterModel, EspnTeamModel
from player_universe_trx.models.espn.league import (
    EspnAcquisitionSettingsModel,
    EspnCategoryResultModel,
    EspnDraftSettingsModel,
    EspnLeagueSettingsModel,
    EspnPlayerMinimalModel,
    EspnPlayerPoolEntryModel,
    EspnRecordDetailModel,
    EspnRecordModel,
    EspnRosterEntryModel,
    EspnRosterSettingsModel,
    EspnScoringCategoriesModel,
    EspnScoringCategoryModel,
    EspnScoringSettingsModel,
    EspnScheduleMatchupModel,
    EspnTransactionCounterModel,
)
from player_universe_trx.transformers.league_transformer import LeagueTransformer


def _make_player_minimal(
    player_id: int,
    full_name: str,
    pro_team_id: int = 29,
    default_position_id: int = 0,
    eligible_slots: list[int] | None = None,
    injury_status: str | None = None,
    active: bool = True,
) -> EspnPlayerMinimalModel:
    return EspnPlayerMinimalModel(
        id=player_id,
        fullName=full_name,
        proTeamId=pro_team_id,
        defaultPositionId=default_position_id,
        eligibleSlots=eligible_slots or [0],
        injuryStatus=injury_status,
        active=active,
    )


def _make_roster_entry(
    player: EspnPlayerMinimalModel,
    lineup_slot_id: int,
    acquisition_date: int | None = None,
    acquisition_type: str | None = None,
    keeper_value: int | None = None,
) -> EspnRosterEntryModel:
    pool_entry = EspnPlayerPoolEntryModel(
        id=player.id,
        onTeamId=1,
        keeperValue=keeper_value,
        player=player,
    )
    return EspnRosterEntryModel(
        playerId=player.id,
        lineupSlotId=lineup_slot_id,
        acquisitionDate=acquisition_date,
        acquisitionType=acquisition_type,
        playerPoolEntry=pool_entry,
    )


def _make_team(
    team_id: int,
    roster_entries: list[EspnRosterEntryModel],
    record: EspnRecordModel | None = None,
    transaction_counter: EspnTransactionCounterModel | None = None,
    waiver_rank: int | None = None,
) -> EspnTeamModel:
    return EspnTeamModel(
        id=team_id,
        name=f"Team {team_id}",
        abbrev=f"T{team_id}",
        primaryOwner="owner",
        owners=["owner"],
        roster=EspnRosterModel(entries=roster_entries),
        record=record,
        transactionCounter=transaction_counter,
        waiverRank=waiver_rank,
    )


def test_mapping_helpers_and_eligible_positions():
    assert LeagueTransformer._get_position_name(0) == "C"
    assert LeagueTransformer._get_position_name(99) == "POS_99"

    assert LeagueTransformer._get_lineup_slot_name(16) == "BENCH"
    assert LeagueTransformer._get_lineup_slot_name(99) == "SLOT_99"

    assert LeagueTransformer._get_pro_team_abbrev(29) == "NYY"
    assert LeagueTransformer._get_pro_team_abbrev(99) == "TEAM_99"

    positions = LeagueTransformer._get_eligible_positions([0, 5, 5, 99, 11])
    assert positions == ["C", "OF", "UTIL"]


def test_format_acquisition_date_valid_and_invalid(monkeypatch):
    valid = LeagueTransformer._format_acquisition_date(1700000000000)
    assert valid.endswith("Z")
    assert "T" in valid

    class _BadDateTime:
        @staticmethod
        def fromtimestamp(*_args, **_kwargs):
            raise ValueError("bad timestamp")

    monkeypatch.setattr(league_transformer, "datetime", _BadDateTime)
    invalid = LeagueTransformer._format_acquisition_date(1)
    assert invalid == ""


def test_create_roster_slot_player_and_organize_roster():
    player = _make_player_minimal(
        player_id=10,
        full_name="Prince",
        eligible_slots=[0, 5],
        injury_status="DTD",
        active=False,
    )
    entry = _make_roster_entry(
        player=player,
        lineup_slot_id=0,
        acquisition_date=1700000000000,
        acquisition_type="DRAFT",
        keeper_value=5,
    )
    roster_player = LeagueTransformer._create_roster_slot_player(entry)
    assert roster_player.first_name == "Prince"
    assert roster_player.last_name is None
    assert roster_player.pro_team == "NYY"
    assert roster_player.primary_position == "C"
    assert roster_player.eligible_positions == ["C", "OF"]
    assert roster_player.lineup_slot == "C"
    assert roster_player.acquisition_date is not None
    assert roster_player.keeper_value == 5

    bench_player = _make_player_minimal(
        player_id=11,
        full_name="Two Names",
        eligible_slots=[16],
    )
    bench_entry = _make_roster_entry(
        player=bench_player,
        lineup_slot_id=16,
        acquisition_date=None,
        acquisition_type=None,
    )

    roster_by_slot = LeagueTransformer._organize_roster_by_slots(
        [entry, bench_entry]
    )
    assert roster_by_slot["C"][0].player_id == 10
    assert roster_by_slot["BENCH"][0].player_id == 11
    assert roster_by_slot["BENCH"][0].acquisition_date is None


def test_create_team_record_and_transaction_summary():
    empty_team = _make_team(team_id=1, roster_entries=[])
    record = LeagueTransformer._create_team_record(empty_team)
    assert record.wins == 0
    assert record.losses == 0

    record_detail = EspnRecordDetailModel(
        wins=10, losses=5, ties=1, percentage=0.667, gamesBack=2.5
    )
    record_model = EspnRecordModel(overall=record_detail)
    team_with_record = _make_team(team_id=2, roster_entries=[], record=record_model)
    record = LeagueTransformer._create_team_record(team_with_record)
    assert record.wins == 10
    assert record.games_back == 2.5

    assert LeagueTransformer._create_transaction_summary(empty_team) is None

    counter = EspnTransactionCounterModel(
        acquisitionBudgetSpent=25, acquisitions=3, drops=1, trades=0
    )
    team_with_tx = _make_team(
        team_id=3, roster_entries=[], transaction_counter=counter, waiver_rank=4
    )
    summary = LeagueTransformer._create_transaction_summary(team_with_tx, league_budget=100)
    assert summary.budget_spent == 25
    assert summary.budget_remaining == 75
    assert summary.waiver_rank == 4

    summary_no_budget = LeagueTransformer._create_transaction_summary(team_with_tx)
    assert summary_no_budget.budget_remaining is None


def test_transform_team_builds_roster_and_transactions():
    player_c = _make_player_minimal(player_id=1, full_name="Catcher One")
    player_of = _make_player_minimal(player_id=2, full_name="Outfielder One", default_position_id=5)
    entry_c = _make_roster_entry(player_c, lineup_slot_id=0)
    entry_of = _make_roster_entry(player_of, lineup_slot_id=5)

    counter = EspnTransactionCounterModel(
        acquisitionBudgetSpent=10, acquisitions=1, drops=0, trades=0
    )
    team = _make_team(
        team_id=10,
        roster_entries=[entry_c, entry_of],
        record=EspnRecordModel(overall=EspnRecordDetailModel()),
        transaction_counter=counter,
    )

    roster = LeagueTransformer.transform_team(team, league_id=99, season_id=2025, league_budget=100)

    assert roster.league_id == 99
    assert roster.team_id == 10
    assert roster.c is not None
    assert roster.c.primary_position == "C"
    assert len(roster.outfield) == 1
    assert roster.transactions.budget_remaining == 90


def test_transform_league_with_and_without_budget():
    player = _make_player_minimal(player_id=1, full_name="Team Player")
    entry = _make_roster_entry(player, lineup_slot_id=0)
    counter = EspnTransactionCounterModel(
        acquisitionBudgetSpent=50, acquisitions=2, drops=0, trades=0
    )
    team = _make_team(team_id=1, roster_entries=[entry], transaction_counter=counter)

    settings = EspnLeagueSettingsModel(
        acquisitionSettings=EspnAcquisitionSettingsModel(acquisitionBudget=200)
    )
    league = EspnLeagueModel(
        id=1,
        seasonId=2025,
        teams=[team],
        settings=settings,
    )

    rosters = LeagueTransformer.transform_league(league)
    assert rosters[0].transactions.budget_remaining == 150

    league_no_budget = EspnLeagueModel(
        id=2,
        seasonId=2025,
        teams=[team],
        settings=None,
    )
    rosters_no_budget = LeagueTransformer.transform_league(league_no_budget)
    assert rosters_no_budget[0].transactions.budget_remaining is None


def test_create_league_summary_with_and_without_settings():
    scoring_settings = EspnScoringSettingsModel(
        categories=EspnScoringCategoriesModel(
            batting=[EspnScoringCategoryModel(statId=1, name="HR", isReverseItem=False)],
            pitching=[EspnScoringCategoryModel(statId=2, name="ERA", isReverseItem=True)],
        )
    )
    settings = EspnLeagueSettingsModel(
        rosterSettings=EspnRosterSettingsModel(lineupSlotCounts={"C": 1}, rosterSize=25),
        scoringSettings=scoring_settings,
        acquisitionSettings=EspnAcquisitionSettingsModel(acquisitionBudget=100),
        draftSettings=EspnDraftSettingsModel(auctionBudget=260),
    )
    league = EspnLeagueModel(id=5, seasonId=2025, teams=[], settings=settings)
    summary = LeagueTransformer.create_league_summary(league)
    assert summary.roster_settings is not None
    assert summary.scoring_categories is not None
    assert summary.acquisition_budget == 100
    assert summary.draft_auction_budget == 260

    league_no_settings = EspnLeagueModel(id=6, seasonId=2025, teams=[], settings=None)
    summary_none = LeagueTransformer.create_league_summary(league_no_settings)
    assert summary_none.roster_settings is None
    assert summary_none.scoring_categories is None
    assert summary_none.acquisition_budget is None
    assert summary_none.draft_auction_budget is None


def test_create_league_summary_preserves_league_name():
    # Name survives the ESPN settings -> MTBL summary boundary
    settings = EspnLeagueSettingsModel(name="The Merican Fantasy Invitational")
    league = EspnLeagueModel(id=7, seasonId=2025, teams=[], settings=settings)
    summary = LeagueTransformer.create_league_summary(league)
    assert summary.league_name == "The Merican Fantasy Invitational"

    # No settings block -> league_name is None, not an error
    league_no_settings = EspnLeagueModel(id=8, seasonId=2025, teams=[], settings=None)
    assert (
        LeagueTransformer.create_league_summary(league_no_settings).league_name is None
    )

    # Settings present but name absent -> None
    settings_no_name = EspnLeagueSettingsModel(
        acquisitionSettings=EspnAcquisitionSettingsModel(acquisitionBudget=100)
    )
    league_no_name = EspnLeagueModel(
        id=9, seasonId=2025, teams=[], settings=settings_no_name
    )
    assert (
        LeagueTransformer.create_league_summary(league_no_name).league_name is None
    )

    # Raw-dict parse: ESPN puts the league name at settings.name
    parsed = EspnLeagueSettingsModel.model_validate({"name": "Raw League"})
    assert parsed.name == "Raw League"


def test_transform_schedule_playoff_and_bye_week():
    matchup_regular = EspnScheduleMatchupModel(
        id=1,
        matchupPeriodId=1,
        playoffTierType="NONE",
        winner=1,
        teams={"1": "5-3", "2": "3-5"},
    )
    matchup_bye = EspnScheduleMatchupModel(
        id=2,
        matchupPeriodId=2,
        playoffTierType="WINNERS_BRACKET",
        winner="BYE WEEK",
        teams={"3": "0-0"},
    )
    league = EspnLeagueModel(
        id=1,
        seasonId=2025,
        teams=[],
        schedule=[matchup_regular, matchup_bye],
    )

    schedule = LeagueTransformer.transform_schedule(league)
    assert len(schedule.matchups) == 2

    first = schedule.matchups[0]
    assert first.is_playoff is False
    assert first.team1_id == 1
    assert first.team2_id == 2
    assert first.winner_id == 1
    assert first.is_bye_week is False

    second = schedule.matchups[1]
    assert second.is_playoff is True
    assert second.team1_id == 3
    assert second.team2_id is None
    assert second.winner_id is None
    assert second.is_bye_week is True

    # No categoryResults upstream -> per-category fields stay None
    assert first.team1_categories is None
    assert first.team2_categories is None


def test_transform_schedule_category_breakdown():
    matchup = EspnScheduleMatchupModel(
        id=1,
        matchupPeriodId=3,
        playoffTierType="NONE",
        winner=31,
        teams={"31": "7-5-0", "1": "5-7-0"},
        categoryResults={
            "31": {
                "R": EspnCategoryResultModel(value=45, result="WIN"),
                "HR": EspnCategoryResultModel(value=12, result="LOSS"),
            },
            "1": {
                "R": EspnCategoryResultModel(value=40, result="LOSS"),
                "HR": EspnCategoryResultModel(value=15, result="WIN"),
            },
        },
    )
    league = EspnLeagueModel(id=1, seasonId=2025, teams=[], schedule=[matchup])

    schedule = LeagueTransformer.transform_schedule(league)
    m = schedule.matchups[0]

    assert m.team1_categories is not None
    assert {c.category: c.result for c in m.team1_categories} == {
        "R": "WIN",
        "HR": "LOSS",
    }
    assert {c.category: c.value for c in m.team1_categories} == {
        "R": 45.0,
        "HR": 12.0,
    }
    assert {c.category: c.result for c in m.team2_categories} == {
        "R": "LOSS",
        "HR": "WIN",
    }

    # categoryResults parses from a raw dict via the camelCase alias
    parsed = EspnScheduleMatchupModel.model_validate(
        {
            "id": 2,
            "matchupPeriodId": 3,
            "winner": 5,
            "teams": {"5": "6-6-0", "6": "6-6-0"},
            "categoryResults": {
                "5": {"SB": {"value": 8, "result": "TIE"}},
            },
        }
    )
    assert parsed.categoryResults["5"]["SB"].result == "TIE"


def test_transform_schedule_without_category_results():
    # Points / roster-limit leagues have no categoryResults -> fields are None
    matchup = EspnScheduleMatchupModel(
        id=1,
        matchupPeriodId=1,
        winner=1,
        teams={"1": "5-3", "2": "3-5"},
    )
    league = EspnLeagueModel(id=1, seasonId=2025, teams=[], schedule=[matchup])

    m = LeagueTransformer.transform_schedule(league).matchups[0]
    assert m.team1_categories is None
    assert m.team2_categories is None
