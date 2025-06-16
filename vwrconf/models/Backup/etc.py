#vwrconf/models/Backup/etc.py

import os
from vwrconf.models.Backup.base import Backup
from vwrconf.models.SSH_Broker import SSHConnectionHandler
from datetime import datetime
import base64
from typing import List

class EtcBackup(Backup):
    BASE_BACKUP_DIR = os.path.expanduser("~/.vwrconf/backups/etc")

    def _is_readonly(self, host_id: str) -> bool:
        cli = next((c for c in self.config.clients if c.id == host_id), None)
        if not cli:
            raise ValueError(f"Unknown host id: {host_id}")
        return getattr(cli, "readonly", False)

    def _get_host_backup_dir(self, host_id: str) -> str:
        return os.path.join(self.BASE_BACKUP_DIR, host_id)

    def write_backup(self, host_id: str, lines: list[str], sudo_password: str | None = None):
        if self._is_readonly(host_id):
            print(f"[SKIP] readonly host {host_id}: write not allowed.")
            return

        cli = next((c for c in self.config.clients if c.id == host_id), None)
        if not cli:
            print(f"[SKIP] Unknown host {host_id}.")
            return

        print(f"[INFO] Connecting to host {host_id} to fetch /etc files...")

        ssh = SSHConnectionHandler(cli, self.config.defaults)
        if not ssh.connect():
            print(f"[SKIP] Could not connect to host {host_id}.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        host_dir = self._get_host_backup_dir(host_id)
        os.makedirs(host_dir, exist_ok=True)

        ssh_user = cli.ssh_user or self.config.defaults.ssh_user or "root"

        for etc_path in lines:
            if ssh_user != "root":
                if sudo_password is None:
                    print(f"[ERROR] Missing sudo password for host {host_id}.")
                    continue
                cmd = f"sudo -S cat {etc_path}"
                out, err = ssh.run(cmd, input_data=sudo_password + "\n", use_pty=True)
            else:
                cmd = f"cat {etc_path}"
                out, err = ssh.run(cmd)

            if err.strip():
                print(f"[WARN] Error reading {etc_path} from {host_id}: {err.strip()}")
                continue

            sanitized = etc_path.strip("/").replace("/", "_")
            file_path = os.path.join(host_dir, f"{timestamp}__{sanitized}.etc")
            with open(file_path, "w") as f:
                f.write(out)

            print(f"[OK] Backed up {etc_path} to {file_path}")

        ssh.close()


    def restore_backup(self, host_id: str, timestamp: str) -> bool:
        if self._is_readonly(host_id):
            print(f"Skipping readonly host {host_id}: restore not allowed.")
            return False

        client = next((c for c in self.config.clients if c.id == host_id), None)
        if not client:
            print(f"Skipping unknown host {host_id}.")
            return False

        host_dir = self._get_host_backup_dir(host_id)
        files = [f for f in os.listdir(host_dir) if f.startswith(timestamp) and f.endswith(".etc")]

        if not files:
            print(f"No backup files found for timestamp '{timestamp}' on host '{host_id}'")
            return False

        ssh = SSHConnectionHandler(client, self.config.defaults)
        if not ssh.connect():
            print(f"Skipping {host_id}: SSH connection failed.")
            return False

        success = True

        for f in files:
            filename = f.split("__", 1)[-1].replace(".etc", "")
            full_path = os.path.join(host_dir, f)

            with open(full_path, "rb") as fp:
                raw = fp.read()
            encoded = base64.b64encode(raw).decode("utf-8")

            target_path = f"/etc/{filename}"
            cmd = f"echo '{encoded}' | base64 -d | sudo -S -p '' tee {target_path} > /dev/null"
            _, stderr = ssh.run(cmd, use_pty=True)

            if stderr.strip():
                print(f"[WARN] Failed to restore {target_path} on {host_id}: {stderr.strip()}")
                success = False
            else:
                print(f"[OK] Restored {target_path} on {host_id}")

        ssh.close()
        return success



    def read_backup_stored(self, host_id: str, timestamp: str) -> list[str]:
        host_dir = self._get_host_backup_dir(host_id)
        files = sorted(
            f for f in os.listdir(host_dir)
            if f.startswith(timestamp) and f.endswith(".etc")
        )
        output = []
        for f in files:
            with open(os.path.join(host_dir, f), "r") as fp:
                output.append(fp.read())
        return output

    def read_backup_stored_dates(self, host_id: str) -> List[str]:
        host_dir = self._get_host_backup_dir(host_id)
        if not os.path.isdir(host_dir):
            return []
        timestamps = set(f.split("__")[0] for f in os.listdir(host_dir) if f.endswith(".etc"))
        return sorted(timestamps)

    def read_backup_known_hosts(self) -> List[str]:
        if not os.path.isdir(self.BASE_BACKUP_DIR):
            return []
        return sorted(d for d in os.listdir(self.BASE_BACKUP_DIR) if os.path.isdir(os.path.join(self.BASE_BACKUP_DIR, d)))

    def latest_backup_filename(self, host_id: str) -> str:
        dates = self.read_backup_stored_dates(host_id)
        if not dates:
            return ""
        return dates[-1]
