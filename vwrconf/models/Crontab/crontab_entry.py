# vwrconf/models/Crontab/crontab_entry.py
import hashlib
from dataclasses import dataclass

@dataclass(frozen=True)
class CrontabEntry:
    line: str
    host: str = ""
    source: str = "unknown"  # "live" or "backup"

    def normalized(self) -> str:
        return self.line.strip()

    def hash(self) -> str:
        # Normalized hash for comparison
        norm = self.normalized().encode("utf-8")
        return hashlib.sha256(norm).hexdigest()
