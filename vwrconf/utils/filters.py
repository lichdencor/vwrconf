# vwrconf/utils/filters.py

import re
from typing import List
from vwrconf.models.Crontab.crontab_entry import CrontabEntry

def filter_entries(entries: List[CrontabEntry], pattern: str) -> List[CrontabEntry]:
    try:
        regex = re.compile(pattern)
        return [entry for entry in entries if regex.search(entry.line)]
    except re.error:
        return [] 

