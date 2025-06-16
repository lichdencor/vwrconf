# vwrconf/models/Backup/backup_entry_base.py

from abc import ABC, abstractmethod

class BackupEntry(ABC):
    """
    Abstract class to model any backup entry
    """
    line: str
    host: str
    source: str

    @abstractmethod
    def normalized(self) -> str:
        ...

    @abstractmethod
    def hash(self) -> str:
        ...

