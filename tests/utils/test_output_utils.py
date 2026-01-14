import json

from player_universe_trx.models.mtbl import MtblBatterModel, MtblPitcherModel
from player_universe_trx.utils.output_utils import save_results


def test_save_results_writes_output_files(tmp_path):
    batter = MtblBatterModel(id=1, name="Test Batter")
    pitcher = MtblPitcherModel(id=2, name="Test Pitcher")
    unmatched_batter = MtblBatterModel(id=3, name="Unmatched Batter")
    unmatched_pitcher = MtblPitcherModel(id=4, name="Unmatched Pitcher")
    candidate_batter = MtblBatterModel(id=5, name="Candidate Batter")
    candidate_pitcher = MtblPitcherModel(id=6, name="Candidate Pitcher")

    save_results(
        matched=[batter, pitcher],
        unmatched=[unmatched_batter, unmatched_pitcher],
        multiple_matches=[
            (batter, [candidate_batter]),
            (pitcher, [candidate_pitcher]),
        ],
        output_dir=str(tmp_path),
    )

    batters_matched_file = tmp_path / "batters_matched.json"
    pitchers_matched_file = tmp_path / "pitchers_matched.json"
    batters_unmatched_file = tmp_path / "batters_unmatched.json"
    pitchers_unmatched_file = tmp_path / "pitchers_unmatched.json"
    batters_ambiguous_file = tmp_path / "batters_ambiguous.json"
    pitchers_ambiguous_file = tmp_path / "pitchers_ambiguous.json"

    for path in (
        batters_matched_file,
        pitchers_matched_file,
        batters_unmatched_file,
        pitchers_unmatched_file,
        batters_ambiguous_file,
        pitchers_ambiguous_file,
    ):
        assert path.exists()

    with open(batters_matched_file, "r") as f:
        batters_matched = json.load(f)
    assert len(batters_matched) == 1
    assert batters_matched[0]["name"] == "Test Batter"

    with open(pitchers_matched_file, "r") as f:
        pitchers_matched = json.load(f)
    assert len(pitchers_matched) == 1
    assert pitchers_matched[0]["name"] == "Test Pitcher"

    with open(batters_unmatched_file, "r") as f:
        batters_unmatched = json.load(f)
    assert len(batters_unmatched) == 1
    assert batters_unmatched[0]["name"] == "Unmatched Batter"

    with open(pitchers_unmatched_file, "r") as f:
        pitchers_unmatched = json.load(f)
    assert len(pitchers_unmatched) == 1
    assert pitchers_unmatched[0]["name"] == "Unmatched Pitcher"

    with open(batters_ambiguous_file, "r") as f:
        batters_ambiguous = json.load(f)
    assert len(batters_ambiguous) == 1
    assert batters_ambiguous[0]["player"]["name"] == "Test Batter"
    assert batters_ambiguous[0]["candidates"][0]["name"] == "Candidate Batter"

    with open(pitchers_ambiguous_file, "r") as f:
        pitchers_ambiguous = json.load(f)
    assert len(pitchers_ambiguous) == 1
    assert pitchers_ambiguous[0]["player"]["name"] == "Test Pitcher"
    assert pitchers_ambiguous[0]["candidates"][0]["name"] == "Candidate Pitcher"
