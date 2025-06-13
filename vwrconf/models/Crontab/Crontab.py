# vwrconf/models/Crontab/crontab.py

from vwrconf.models.SSH_Broker import RemoteCommandProxy, SSH_Broker
from vwrconf.models.config_model import Config

class Crontab:
    """
    Retrieves crontab entries from a list of configured remote hosts using a proxy.

    The RemoteCommandProxy handles connection and command execution, abstracting
    away SSH logic. Results are returned as a dictionary mapping host IDs to 
    crontab lines.
    """

    def __init__(self, config: Config):
        self.config = config

    def fetch(self) -> dict[str, list[str]]:
        results = {}
        broker = SSH_Broker()

        for cli in self.config.clients:
            try:
                broker.register_service(cli.id, cli, self.config.defaults)
            except ConnectionError as e:
                print(f"[BROKER ERROR] {e}")
                continue

            proxy = RemoteCommandProxy(broker, cli.id)
            stdout, stderr = proxy.execute("crontab -l")

            if stderr.strip():
                print(f"[CRONTAB ERROR] {cli.id}: {stderr.strip()}")
                continue

            results[cli.id] = stdout.strip().splitlines()

        broker.shutdown()
        return results

