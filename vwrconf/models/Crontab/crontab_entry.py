# vwrconf/models/Crontab/crontab_entry.py

import hashlib
from dataclasses import dataclass, field

@dataclass(frozen=True)
class CrontabEntry:
    line: str
    host: str = ""
    source: str = "unknown"

    def normalized(self) -> str:
        return self.line.strip()

    def hash(self) -> str:
        norm = self.normalized().encode("utf-8")
        return hashlib.sha256(norm).hexdigest()

    @property
    def is_comment(self) -> bool:
        return self.line.strip().startswith("#")

    @property
    def parsed(self) -> dict:
        """Try to parse crontab line into parts"""
        parts = self.line.strip().split(None, 5)
        if len(parts) < 6:
            return {
                "minute": "", "hour": "", "dom": "", "month": "", "dow": "", "command": self.line.strip()
            }
        return {
            "minute": parts[0],
            "hour": parts[1],
            "dom": parts[2],
            "month": parts[3],
            "dow": parts[4],
            "command": parts[5],
        }

