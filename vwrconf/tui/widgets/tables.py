# vwrconf/tui/widgets/tables.py

from textual.widgets import DataTable
from textual.message import Message
from vwrconf.core.view_crontab import fetch_all_crontabs
from vwrconf.models.Crontab.crontab_entry import CrontabEntry

class ConfigTable(DataTable):
    class ClientSelected(Message):
        def __init__(self, sender: "ConfigTable", host: str) -> None:
            super().__init__()
            self.sender = sender
            self.host = host

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_columns(
            "id", "host", "label", "readonly", "tags", "port", "method", "notes", "ssh_user"
        )
        self.zebra_stripes = True
        self.cursor_type = "row"

    async def update_with_config(self, config):
        self.clear()
        for client in config.clients:
            self.add_row(
                client.id,
                client.host,
                client.label,
                str(client.readonly),
                ", ".join(client.tags or []),
                str(client.port),
                client.method,
                client.notes or "",
                client.ssh_user or ""
            )

    async def on_data_table_row_selected(self, event: DataTable.RowSelected):
        client = self.get_row(event.row_key)
        host = client[1]  # Assuming second column is 'host'
        self.post_message(self.ClientSelected(self, host))


class CrontabTable(DataTable):
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_columns("min", "hour", "dom", "month", "dow", "command")
        self.zebra_stripes = True
        self.cursor_type = "row"
        self._config = config

    def set_config(self, config):
        self._config = config

    async def update_for_host(self, host: str):
        self.clear()
        if not self._config:
            return
        all_crontabs = fetch_all_crontabs(self._config)
        jobs = all_crontabs.get(host, [])
        entries = [CrontabEntry(line, host=host, source="live") for line in jobs if line.strip()]
        for entry in entries:
            if entry.is_comment:
                continue  # skip comments for now
            parsed = entry.parsed
            self.add_row(
                parsed["minute"],
                parsed["hour"],
                parsed["dom"],
                parsed["month"],
                parsed["dow"],
                parsed["command"],
            )

