"""Regression guard for the `universe-trx` CLI exit-code contract.

An earlier version of the CLI returned exit code 1 on the happy path. The
mtbl-et orchestrator and MTBL_Prefect both whitelisted that exit code as
success (`allow_exit_code_1=True`) to keep their flows green — which meant a
later real exit-code-1 failure would be silently swallowed.

The fix is to keep `cli()` returning None (Python translates a clean module
exit to code 0). This test invokes the CLI via subprocess against the test
fixtures and asserts exit code 0, so any future regression that reintroduces
the quirk fails CI loudly.

See Linear MTBL-153.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"
REPO_ROOT = Path(__file__).resolve().parent.parent


def test_cli_exit_code_zero_on_success(tmp_path):
    """`python -m player_universe_trx` exits 0 against valid inputs."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "player_universe_trx",
            "--year",
            "2026",
            "--resources-path",
            str(FIXTURES),
            "--output-dir",
            str(tmp_path),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"CLI exited with code {result.returncode} on the happy path.\n"
        f"stdout tail:\n{result.stdout[-1000:]}\n"
        f"stderr tail:\n{result.stderr[-1000:]}"
    )
    # And the run produced its canonical output files (so we didn't catch
    # an early-exit-before-work-done case as a false positive).
    assert (tmp_path / "batters_matched.json").exists()
    assert (tmp_path / "pitchers_matched.json").exists()
    assert (tmp_path / "league_10998_summary.json").exists()
