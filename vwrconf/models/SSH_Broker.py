# vwrconf/models/SSH_Broker.py

import os
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from vwrconf.models.config_model import Client, Defaults

class RemoteCommandProxy:
    """
    Client-side proxy for executing commands on a remote service via the SSH broker.

    This class serves as the access point for a client to execute remote shell 
    commands without needing to know the connection details. It delegates all 
    requests to an underlying broker instance, which manages the actual SSH connections.

    Attributes:
        broker (SSH_Broker): The broker responsible for dispatching commands.
        service_id (str): Identifier of the registered remote service.

    Methods:
        execute(command: str) -> tuple[str, str]:
            Executes the specified command on the remote server and returns the output.
    """
    def __init__(self, broker, service_id: str):
        self.broker = broker
        self.service_id = service_id

    def execute(self, command: str) -> tuple[str, str]:
        return self.broker.dispatch(self.service_id, command)

class SSH_Broker:
    """
    Acts as a broker for dispatching commands to remote servers over SSH.
    Manages multiple connections and routes commands by service_id.
    """

    def __init__(self):
        self.services = {}  # service_id -> SSHConnectionHandler

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
    """
    Handles a single SSH connection using Paramiko.

    This class is responsible for establishing and managing a secure SSH session 
    with a remote host. It uses key-based authentication and provides methods to 
    execute shell commands on the remote server.

    Attributes:
        hostname (str): The target server's hostname or IP address.
        port (int): The SSH port to connect to.
        username (str): The username used for authentication.
        key_path (str): Path to the RSA private key file.
        ssh (paramiko.SSHClient): The underlying Paramiko SSH client.

    Methods:
        connect() -> bool:
            Establishes the SSH connection.
        
        run(command: str) -> tuple[str, str]:
            Executes a command on the remote server and returns stdout and stderr.

        close() -> None:
            Closes the SSH connection.
    """
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

    def run(self, command: str) -> tuple[str, str]:
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            return stdout.read().decode(), stderr.read().decode()
        except Exception as e:
            return "", str(e)

    def close(self):
        self.ssh.close()

def get_defaulted(value, fallback, field):
    if value is not None:
        return value
    if fallback is not None:
        return fallback
    raise ValueError(f"Missing required SSH config field: {field}")

