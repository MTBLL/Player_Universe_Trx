"""Atomic publish for trx output files.

trx emits ~25 JSON files (player files plus per-team rosters, the league
summary and the schedule) into a single publish directory. Writing them in
place, sequentially, over the course of a run means a downstream reader that
scans the directory mid-run can see a *torn snapshot*: some files from this
run, some still from the previous one. When a run adds or removes players the
snapshot is internally inconsistent -- a roster cites a ``player_id`` that has
not yet been written to the player files -- which surfaced in
``Player_Universe_Load`` as transient, non-reproducible FK violations.

The fix mirrors the write-to-temp + ``os.replace`` pattern the load applet
already uses for its parquet exports, lifted one level up to the *directory*:
the whole run writes into a staging directory that shares a filesystem with
the publish directory, then a tight loop atomically renames every file into
place. The window during which the publish directory is internally
inconsistent shrinks from the whole run (minutes) to the rename loop
(milliseconds) -- short enough that any sane reader interleaves around it, not
through it.

A ``MANIFEST.json``, written last, gives downstream a positive "run complete"
gate plus per-file sha256/size so a paranoid reader can verify the set it is
about to consume rather than trusting directory mtimes.
"""

import hashlib
import json
import logging
import os
import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

logger = logging.getLogger("player_universe_trx.utils.atomic_publish")

MANIFEST_NAME = "MANIFEST.json"

# Read in 1 MiB chunks so hashing the larger player files (tens of MB) stays
# bounded in memory rather than slurping the whole file.
_HASH_CHUNK = 1024 * 1024


def _sha256(path: Path) -> str:
    """Return the hex sha256 digest of ``path``, read in bounded chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(_HASH_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def _atomic_write_json(data: object, dest: Path) -> None:
    """Write ``data`` as JSON to ``dest`` atomically via a same-dir temp file.

    Used for the manifest, which is written directly into the publish
    directory (not staged) and must itself never be observed half-written.
    """
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, dest)


def _publish(staging: Path, publish: Path, run_id: Optional[str], started_at: str) -> None:
    """Atomically move every file from ``staging`` into ``publish`` and write
    the manifest last.

    The rename loop is the only window during which ``publish`` can hold a
    mix of old and new files; keep it tight (no I/O beyond ``os.replace``).
    Checksums for the manifest are computed *after* the renames, reading from
    the now-published files.
    """
    files = sorted(p for p in staging.iterdir() if p.is_file())

    # Tight atomic-rename loop -- minimal inconsistency window. os.replace is
    # POSIX-atomic per file because staging shares a filesystem with publish.
    for src in files:
        os.replace(src, publish / src.name)

    manifest = {
        "run_id": run_id,
        "started_at": started_at,
        "completed_at": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "files": {
            src.name: {
                "sha256": _sha256(publish / src.name),
                "size": (publish / src.name).stat().st_size,
            }
            for src in files
        },
    }
    _atomic_write_json(manifest, publish / MANIFEST_NAME)

    logger.info(
        "Atomically published %d files to %s (manifest: %s)",
        len(files),
        publish,
        publish / MANIFEST_NAME,
    )


@contextmanager
def atomic_publish(
    publish_dir: str, *, run_id: Optional[str] = None
) -> Iterator[Path]:
    """Stage trx output, then atomically publish it on clean exit.

    Yields a staging directory; write every output file there during the run
    exactly as if it were the real output directory. On normal exit the staged
    files are atomically renamed into ``publish_dir`` and a ``MANIFEST.json`` is
    written last. On exception nothing is published -- the staging directory is
    discarded and the last good contents of ``publish_dir`` are left untouched.

    The staging directory is created as a sibling of ``publish_dir`` (under the
    same parent) so it shares a filesystem and ``os.replace`` is genuinely
    atomic; a cross-device rename would silently degrade to copy+unlink and
    reopen the race this function exists to close.

    Args:
        publish_dir: Final directory readers consume.
        run_id: Optional identifier recorded in the manifest (e.g. an ISO8601
            run timestamp).

    Yields:
        Path to the staging directory to write outputs into.
    """
    publish = Path(publish_dir)
    publish.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    staging = Path(
        tempfile.mkdtemp(prefix=f".{publish.name}.staging-", dir=publish.parent)
    )
    try:
        yield staging
        _publish(staging, publish, run_id, started_at)
    finally:
        # On success the files have been renamed out and only the (now empty)
        # staging dir remains; on failure it still holds the partial run. Either
        # way, remove it. ignore_errors so cleanup never masks a real error.
        shutil.rmtree(staging, ignore_errors=True)
