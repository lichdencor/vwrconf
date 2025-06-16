# vwrconf/models/Etc/etc_entry.py

import hashlib
from dataclasses import dataclass
from vwrconf.models.Backup.backup_entry_base import BackupEntry

@dataclass(frozen=True)
class EtcEntry(BackupEntry):
    line: str
    host: str = ""
    path: str = ""
    source: str = "unknown"

    def normalized(self) -> str:
        return self.line.strip()

    def hash(self) -> str:
        data = f"{self.path}:{self.normalized()}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

