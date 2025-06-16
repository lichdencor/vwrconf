# vwrconf/models/SSH_Broker.py

import os
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from vwrconf.models.config_model import Client, Defaults
import traceback

class RemoteCommandProxy:
    def __init__(self, broker, service_id: str):
        self.broker = broker
        self.service_id = service_id

    def execute(self, command: str) -> tuple[str, str]:
        return self.broker.dispatch(self.service_id, command)

class SSH_Broker:
    def __init__(self):
        self.services = {}

    def register_service(self, service_id: str, client: Client, defaults: Defaults):
        handler = SSHConnectionHandler(client, defaults)
        if handler.connect():
            self.services[service_id] = handler
        else:
            raise ConnectionError(f"Failed to connect to service '{service_id}'")

    def dispatch(self, service_id: str, command: str) -> tuple[str, str]:
        if service_id not in self.services:
            return "", f"Service '{service_id}' not found"
        return self.services[service_id].run(command)

    def shutdown(self):
        for handler in self.services.values():
            handler.close()

class SSHConnectionHandler:
    def __init__(self, client: Client, defaults: Defaults):
        self.hostname = client.host
        self.port = get_defaulted(client.port, defaults.port, "port")
        self.username = client.ssh_user or defaults.ssh_user
        self.key_path = os.path.expanduser("~/.ssh/id_rsa")
        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())

    def connect(self) -> bool:
        try:
            pkey = RSAKey.from_private_key_file(self.key_path)
            self.ssh.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                pkey=pkey
            )
            return True
        except Exception as e:
            print(f"[SSH ERROR] Connection to {self.hostname} failed: {e}")
            return False

    def run(self, command: str, input_data: str | None = None, use_pty: bool = False) -> tuple[str, str]:
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command, get_pty=use_pty)
            if input_data:
                stdin.write(input_data)
                stdin.flush()
            out = stdout.read().decode()
            err = stderr.read().decode()
            return out, err
        except Exception as e:
            # Obtener traceback completo
            tb_str = traceback.format_exc()
            err_msg = f"[SSH RUN ERROR] Exception running command:\n{e}\nTraceback:\n{tb_str}"
            print(err_msg)  # Podés cambiar a logging si querés
            return "", err_msg

    def close(self):
        self.ssh.close()

def get_defaulted(value, fallback, field):
    if value is not None:
        return value
    if fallback is not None:
        return fallback
    raise ValueError(f"Missing required SSH config field: {field}")

