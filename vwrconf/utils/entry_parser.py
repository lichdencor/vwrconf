# vwrconf/utils/entry_parser.py

from vwrconf.models.Crontab.crontab_entry import CrontabEntry
import os
import re

def lines_to_entries(host: str, lines: list[str], source: str = "live") -> set[CrontabEntry]:
    """Generate entries from a list of lines"""
    return {
        CrontabEntry(line=line.strip(), host=host, source=source)
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    }

def normalize_line(line: str) -> str:
    """
    Normalize cron entry:
    - Strip full binary path (keep command name)
    - Normalize home/user paths (/home/kimba → ~/)
    """
    parts = line.strip().split()
    if len(parts) < 6:
        return line  # skip invalid

    schedule = parts[:5]
    command = parts[5:]

    if command:
        # Normalize binary (e.g., /usr/bin/python3 → python3)
        command[0] = os.path.basename(command[0])

        # Normalize all args: replace /home/* with ~/
        command = [re.sub(r"/home/\w+", "~", arg) for arg in command]

    return " ".join(schedule + command)
