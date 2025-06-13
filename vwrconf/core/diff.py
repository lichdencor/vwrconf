# vwrconf/core/diff.py

from vwrconf.models.Crontab.crontab_entry import CrontabEntry


def diff_crontabs(live_entries: set[CrontabEntry], backup_entries: set[CrontabEntry]):
    """diff hashes from two sets of CrontabEntry objects"""
    live_hashes = {entry.hash(): entry for entry in live_entries}
    backup_hashes = {entry.hash(): entry for entry in backup_entries}

    live_keys = set(live_hashes.keys())
    backup_keys = set(backup_hashes.keys())

    added = live_keys - backup_keys
    removed = backup_keys - live_keys
    unchanged = live_keys & backup_keys

    return {
        "added": [live_hashes[h] for h in added],
        "removed": [backup_hashes[h] for h in removed],
        "unchanged": [live_hashes[h] for h in unchanged],
    }

