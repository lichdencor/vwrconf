# vwrconf/tui/views/config_view.py

from textual.widgets import Static
from textual.containers import Vertical

class HostsView(Vertical):
    """View showing only hosts labels as a simple list with a title."""

    def compose(self):
        yield Static("Known Hosts", id="hosts-title", classes="title")
        self.hosts_list = Static("", id="hosts-list")
        yield self.hosts_list

    async def update_with_config(self, config):
        hosts = getattr(config, "clients", None)
        if not hosts:
            self.hosts_list.update("No hosts configured")
            return
        content = "\n".join(client.label for client in hosts)
        self.hosts_list.update(content)

