# vwrconf/models/Backup/base.py
from abc import ABC, abstractmethod

from vwrconf.models.config_model import Config

class Backup(ABC):
    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def write_backup(self, host_id: str, lines: list[str]):
        pass

    @abstractmethod
    def restore_backup(self, host_id: str, timestamp: str):
        pass

    @abstractmethod
    def read_backup_stored(self, host_id: str, timestamp: str) -> list[str]:
        pass

    @abstractmethod
    def read_backup_stored_dates(self, host_id: str) -> list[str]:
        pass

    @abstractmethod
    def read_backup_known_hosts(self) -> list[str]:
        pass

    @abstractmethod
    def latest_backup_filename(self, host_id: str) -> str:
        pass
