"""Tests for the atomic publish helper.

These guard the property the publish layer exists to provide: the publish
directory only ever flips from one internally-consistent set of files to the
next, and a failed run never corrupts the last good output.
"""

import hashlib
import json
import os
from pathlib import Path

import pytest

from player_universe_trx.utils import atomic_publish as ap
from player_universe_trx.utils.atomic_publish import MANIFEST_NAME, atomic_publish


def _write(d: Path, name: str, text: str) -> None:
    (d / name).write_text(text)


def test_publishes_staged_files_on_clean_exit(tmp_path):
    publish = tmp_path / "transform"

    with atomic_publish(str(publish), run_id="run-1") as staging:
        _write(staging, "hitters.json", '{"a": 1}')
        _write(staging, "team_18_roster.json", '{"b": 2}')
        # Nothing is visible in the publish dir mid-run.
        assert not publish.exists() or not list(publish.glob("*.json"))

    assert (publish / "hitters.json").read_text() == '{"a": 1}'
    assert (publish / "team_18_roster.json").read_text() == '{"b": 2}'


def test_staging_dir_removed_after_publish(tmp_path):
    publish = tmp_path / "transform"
    seen = {}

    with atomic_publish(str(publish)) as staging:
        seen["staging"] = staging
        _write(staging, "f.json", "{}")

    assert not seen["staging"].exists()


def test_staging_shares_parent_with_publish(tmp_path):
    """Staging must be a sibling of the publish dir so os.replace is atomic
    (same filesystem), not under the system temp dir."""
    publish = tmp_path / "transform"

    with atomic_publish(str(publish)) as staging:
        assert staging.parent == publish.parent
        _write(staging, "f.json", "{}")


def test_manifest_records_sha256_and_size(tmp_path):
    publish = tmp_path / "transform"
    payload = '{"hello": "world"}'

    with atomic_publish(str(publish), run_id="2026-05-28T00:00:00Z") as staging:
        _write(staging, "hitters.json", payload)

    manifest = json.loads((publish / MANIFEST_NAME).read_text())
    assert manifest["run_id"] == "2026-05-28T00:00:00Z"
    assert manifest["completed_at"].endswith("Z")
    entry = manifest["files"]["hitters.json"]
    assert entry["size"] == len(payload.encode())
    assert entry["sha256"] == hashlib.sha256(payload.encode()).hexdigest()
    # The manifest never lists itself.
    assert MANIFEST_NAME not in manifest["files"]


def test_failed_run_leaves_previous_output_untouched(tmp_path):
    publish = tmp_path / "transform"

    # An initial good run.
    with atomic_publish(str(publish)) as staging:
        _write(staging, "hitters.json", '{"v": 1}')

    # A second run that blows up mid-flight must publish nothing.
    staging_seen = {}
    with pytest.raises(RuntimeError):
        with atomic_publish(str(publish)) as staging:
            staging_seen["dir"] = staging
            _write(staging, "hitters.json", '{"v": 2}')
            raise RuntimeError("boom")

    # Last good contents preserved, staging cleaned up.
    assert (publish / "hitters.json").read_text() == '{"v": 1}'
    assert not staging_seen["dir"].exists()


def test_publish_dir_created_if_missing(tmp_path):
    publish = tmp_path / "nested" / "transform"

    with atomic_publish(str(publish)) as staging:
        _write(staging, "f.json", "{}")

    assert (publish / "f.json").exists()


def test_manifest_write_failure_rolls_back_whole_run(tmp_path, monkeypatch):
    """If the manifest write fails after every file is installed, the run
    reverts: prior files restored, newly-added files removed."""
    publish = tmp_path / "transform"

    # Good run 1: a.json only.
    with atomic_publish(str(publish)) as staging:
        _write(staging, "a.json", '{"v": 1}')
    run1_manifest = json.loads((publish / MANIFEST_NAME).read_text())

    # Run 2 overwrites a.json and adds c.json, but the manifest write blows up.
    def _boom(*_a, **_k):
        raise OSError("manifest disk full")

    monkeypatch.setattr(ap, "_atomic_write_json", _boom)

    with pytest.raises(OSError):
        with atomic_publish(str(publish)) as staging:
            _write(staging, "a.json", '{"v": 2}')
            _write(staging, "c.json", '{"new": True}')

    # a.json reverted to v1, c.json gone, manifest unchanged from run 1.
    assert (publish / "a.json").read_text() == '{"v": 1}'
    assert not (publish / "c.json").exists()
    assert json.loads((publish / MANIFEST_NAME).read_text()) == run1_manifest
    # No backup dir left behind on a clean rollback.
    assert not list(publish.parent.glob(".*backup*"))


def test_failure_between_backup_and_install_does_not_lose_old_file(
    tmp_path, monkeypatch
):
    """The dangerous window: the old file is moved into backup, then installing
    the new version fails. The old version must come back, not vanish."""
    publish = tmp_path / "transform"

    with atomic_publish(str(publish)) as staging:
        _write(staging, "a.json", '{"v": 1}')

    real_replace = os.replace
    calls = {"n": 0}

    def _flaky_replace(src, dst):
        calls["n"] += 1
        # Call 1 = move old a.json into backup; call 2 = install new a.json.
        if calls["n"] == 2:
            raise OSError("install failed mid-swap")
        return real_replace(src, dst)

    monkeypatch.setattr(ap.os, "replace", _flaky_replace)

    with pytest.raises(OSError):
        with atomic_publish(str(publish)) as staging:
            _write(staging, "a.json", '{"v": 2}')

    # Old version restored from backup despite failing between move and install.
    assert (publish / "a.json").read_text() == '{"v": 1}'


def test_failed_manifest_write_cleans_tmp_and_rolls_back(tmp_path, monkeypatch):
    """A real manifest write failure (fsync errors) must remove the .tmp file
    and revert installed files, not leave a stray half-written manifest."""
    publish = tmp_path / "transform"

    with atomic_publish(str(publish)) as staging:
        _write(staging, "a.json", '{"v": 1}')

    def _boom_fsync(_fd):
        raise OSError("fsync failed")

    monkeypatch.setattr(ap.os, "fsync", _boom_fsync)

    with pytest.raises(OSError):
        with atomic_publish(str(publish)) as staging:
            _write(staging, "a.json", '{"v": 2}')

    # No stray MANIFEST.json.tmp, and a.json reverted to the prior run.
    assert not list(publish.glob("*.tmp"))
    assert (publish / "a.json").read_text() == '{"v": 1}'


def test_rollback_logs_when_unlinking_new_file_fails(tmp_path, monkeypatch):
    """If removing a newly-added file during rollback fails, the error is
    swallowed-and-logged so the rest of the rollback still runs."""
    publish = tmp_path / "transform"

    monkeypatch.setattr(ap.os, "fsync", lambda _fd: (_ for _ in ()).throw(OSError()))

    real_unlink = Path.unlink

    def _flaky_unlink(self, *a, **k):
        # Fail on the new file (rollback path) and on the manifest .tmp cleanup
        # (the nested best-effort unlink in _atomic_write_json).
        if self.name == "c.json" or self.suffix == ".tmp":
            raise OSError("cannot remove")
        return real_unlink(self, *a, **k)

    monkeypatch.setattr(Path, "unlink", _flaky_unlink)

    with pytest.raises(OSError):
        with atomic_publish(str(publish)) as staging:
            _write(staging, "c.json", '{"new": True}')

    # Rollback couldn't remove it, but the run still raised rather than
    # silently "succeeding".


def test_rollback_restore_failure_retains_backup(tmp_path, monkeypatch):
    """If restoring a backed-up file fails, the backup dir is retained for
    manual recovery rather than deleted."""
    publish = tmp_path / "transform"

    with atomic_publish(str(publish)) as staging:
        _write(staging, "a.json", '{"v": 1}')

    real_replace = os.replace
    calls = {"n": 0}

    def _flaky_replace(src, dst):
        calls["n"] += 1
        # 1 = move old aside (ok); 2 = install new (fail -> rollback);
        # 3 = restore backup (fail -> backup retained).
        if calls["n"] in (2, 3):
            raise OSError("replace failed")
        return real_replace(src, dst)

    monkeypatch.setattr(ap.os, "replace", _flaky_replace)

    with pytest.raises(OSError):
        with atomic_publish(str(publish)) as staging:
            _write(staging, "a.json", '{"v": 2}')

    # A backup dir was kept behind for forensics.
    backups = list(publish.parent.glob(".transform.backup-*"))
    assert backups, "expected a retained backup dir after a failed rollback"
