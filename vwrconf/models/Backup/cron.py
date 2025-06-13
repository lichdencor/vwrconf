# vwrconf/models/Backup/cron.py

import os
from datetime import datetime
from typing import List
from vwrconf.models.SSH_Broker import SSHConnectionHandler
from .base import Backup as BaseBackup

class CronBackup(BaseBackup):
    BASE_BACKUP_DIR = os.path.expanduser("~/.vwrconf/backups/cron")

    def _is_readonly(self, host_id: str) -> bool:
        cli = next((c for c in self.config.clients if c.id == host_id), None)
        if not cli:
            raise ValueError(f"Unknown host id: {host_id}")
        return getattr(cli, "readonly", False)

    def _get_host_backup_dir(self, host_id: str) -> str:
        return os.path.join(self.BASE_BACKUP_DIR, host_id)

    def write_backup(self, host_id: str, lines: list[str]):
        if self._is_readonly(host_id):
            print(f"[SKIP] Host '{host_id}' is readonly. Write not allowed.")
            return

        client = next((c for c in self.config.clients if c.id == host_id), None)
        if not client:
            print(f"[SKIP] Unknown host '{host_id}'.")
            return

        print(f"[INFO] Connecting to host '{host_id}' to fetch crontab...")

        ssh = SSHConnectionHandler(client, self.config.defaults)
        if not ssh.connect():
            print(f"[SKIP] Could not connect to host '{host_id}'.")
            return

        stdout, stderr = ssh.run("crontab -l")
        ssh.close()

        if stderr.strip():
            print(f"[SKIP] Error retrieving crontab from '{host_id}': {stderr.strip()}")
            return

        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        host_dir = self._get_host_backup_dir(host_id)
        os.makedirs(host_dir, exist_ok=True)

        file_path = os.path.join(host_dir, f"{timestamp}.cron")
        with open(file_path, "w") as f:
            f.write(stdout)

        print(f"[OK] Backup for host '{host_id}' written to: {file_path}")


    def restore_backup(self, host_id: str, timestamp: str):
        if self._is_readonly(host_id):
            print(f"Skipping readonly host {host_id}: restore not allowed.")
            return

        backup_path = os.path.join(self._get_host_backup_dir(host_id), f"{timestamp}.cron")
        if not os.path.exists(backup_path):
            print(f"Skipping {host_id}: Backup not found at {backup_path}")
            return

        with open(backup_path, "r") as f:
            content = f.read()

        client = next((c for c in self.config.clients if c.id == host_id), None)
        if not client:
            print(f"Skipping unknown host {host_id}.")
            return

        ssh = SSHConnectionHandler(client, self.config.defaults)
        if not ssh.connect():
            print(f"Skipping {host_id}: SSH connection failed.")
            return

        temp_path = "/tmp/vwrconf_restore.cron"
        echo_cmd = f"echo '{content}' > {temp_path} && crontab {temp_path} && rm {temp_path}"
        _, stderr = ssh.run(echo_cmd)
        ssh.close()

        if stderr.strip():
            print(f"Restore failed for {host_id}: {stderr.strip()}")

    def read_backup_stored(self, host_id: str, timestamp: str) -> list[str]:
        file_path = os.path.join(self._get_host_backup_dir(host_id), timestamp)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No backup found at {file_path}")
        with open(file_path, "r") as f:
            return f.readlines()


    def read_backup_stored_dates(self, host_id: str) -> List[str]:
        host_dir = self._get_host_backup_dir(host_id)
        if not os.path.isdir(host_dir):
            return []
        return sorted(f[:-5] for f in os.listdir(host_dir) if f.endswith(".cron"))

    def read_backup_known_hosts(self) -> List[str]:
        if not os.path.isdir(self.BASE_BACKUP_DIR):
            return []
        return sorted(d for d in os.listdir(self.BASE_BACKUP_DIR) if os.path.isdir(os.path.join(self.BASE_BACKUP_DIR, d)))

    def latest_backup_filename(self, host_id: str) -> str:
        dates = self.read_backup_stored_dates(host_id)
        if not dates:
            return ""
        return dates[-1]

