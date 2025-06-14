# vwrconf/tui/views/crontab_view.py
#
from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from textual.containers import Horizontal
from vwrconf.tui.widgets.tables import ConfigTable, CrontabTable
from vwrconf.cli.Commands.GlobalCommand import GlobalCommand
from pathlib import Path


class CrontabView(Screen):
    CSS_PATH = Path(__file__).with_name("crontab_view.css")

    def compose(self):
        yield Header()
        yield ConfigTable(id="config-table")
        yield CrontabTable(config=None, id="crontab-table")  # config se asigna luego
        yield Footer()

    async def on_mount(self):
        try:
            config = GlobalCommand.load_config()

            self._config = config
            self.query_one("#config-table", ConfigTable)
            crontab_table = self.query_one("#crontab-table", CrontabTable)
            crontab_table.set_config(config)

            await self.query_one("#config-table", ConfigTable).update_with_config(config)

        except Exception as e:
            print(f"[CrontabView] Error: {e}")

    async def on_config_table_client_selected(self, message: ConfigTable.ClientSelected):
        host = message.host
        crontab_table = self.query_one("#crontab-table", CrontabTable)
        await crontab_table.update_for_host(host)


