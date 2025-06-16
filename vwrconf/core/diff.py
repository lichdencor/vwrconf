# vwrconf/core/diff.py

from vwrconf.models.Crontab.crontab_entry import CrontabEntry
import difflib
from typing import Dict

def diff_crontabs(
    live_entries: set[CrontabEntry],
    backup_entries: set[CrontabEntry]
) -> dict:
    """
    Normalized diff format:
    {
        added: [entry1, entry2],
        removed: [entry3],
        changed: {}  # empty, crontabs don't use unified diffs
    }
    """
    live_hashes = {entry.hash(): entry for entry in live_entries}
    backup_hashes = {entry.hash(): entry for entry in backup_entries}

    live_keys = set(live_hashes.keys())
    backup_keys = set(backup_hashes.keys())

    added = [live_hashes[h] for h in live_keys - backup_keys]
    removed = [backup_hashes[h] for h in backup_keys - live_keys]

    return {
        "added": added,
        "removed": removed,
        "changed": {},  # optional; reserved for detailed diffs
    }


def diff_etc_files(live_files: Dict[str, str], backup_files: Dict[str, str]) -> dict:
    """
    Returns a unified diff format for etc file differences:
    {
        added: ["/etc/xyz"],
        removed: ["/etc/abc"],
        changed: {
            "/etc/foo": "<unified diff text>"
        }
    }
    """
    added = []
    removed = []
    changed = {}

    for path in live_files:
        if path not in backup_files:
            added.append(path)
            continue

        live_lines = live_files[path].splitlines(keepends=True)
        backup_lines = backup_files[path].splitlines(keepends=True)

        diff = difflib.unified_diff(
            backup_lines,
            live_lines,
            fromfile=f"{path} (backup)",
            tofile=f"{path} (live)",
            lineterm=""
        )
        diff_output = ''.join(diff)
        if diff_output:
            changed[path] = diff_output

    for path in backup_files:
        if path not in live_files:
            removed.append(path)

    return {
        "added": sorted(added),
        "removed": sorted(removed),
        "changed": changed,
    }

