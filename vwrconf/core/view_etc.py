from typing import Dict
from vwrconf.models.config_model import Config
from vwrconf.models.SSH_Broker import SSHConnectionHandler

def fetch_all_etc(config: Config, etc_paths: list[str], sudo_password: str | None = None) -> Dict[str, Dict[str, str]]:
    """
    Connects to all non-readonly hosts and fetches specified /etc files.
    Returns a nested dict: {host_id: {etc_path: content}}.

    Uses sudo with password if necessary, via stdin (no prompt).
    """
    results: Dict[str, Dict[str, str]] = {}

    for client in config.clients:
        if client.readonly:
            continue

        ssh_user = client.ssh_user or config.defaults.ssh_user or "root"
        ssh = SSHConnectionHandler(client, config.defaults)
        if not ssh.connect():
            print(f"[SKIP] Could not connect to {client.id}")
            continue

        host_data = {}
        for path in etc_paths:
            if ssh_user != "root":
                if sudo_password is None:
                    print(f"[ERROR] Missing sudo password for host {client.id}.")
                    continue
                cmd = f"sudo -S cat {path}"
                stdout, stderr = ssh.run(cmd, input_data=sudo_password + "\n", use_pty=True)
            else:
                cmd = f"cat {path}"
                stdout, stderr = ssh.run(cmd)

            if stderr.strip():
                print(f"[WARN] Error fetching {path} from {client.id}: {stderr.strip()}")
                continue

            # Clean sudo prompt + echoed password
            cleaned_lines = [
                line for line in stdout.splitlines()
                if line.strip() not in ("Password:", (sudo_password or "").strip()) and
                not line.lower().startswith("[sudo] password")
            ]
            host_data[path] = "\n".join(cleaned_lines)

        ssh.close()

        if host_data:
            results[client.id] = host_data

    return results

