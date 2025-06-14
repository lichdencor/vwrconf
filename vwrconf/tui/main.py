# vwrconf/tui/main.py

from pathlib import Path

from textual.app import App

from vwrconf.cli.Commands.GlobalCommand import GlobalCommand
from vwrconf.tui.views.crontab_view import CrontabView

class VwrconfApp(App):
    CSS_PATH = Path(__file__).parent / "vwrconf.css"
    TITLE = "vwrconf – Remote Config Viewer"

    def __init__(self):
        super().__init__()
        self.config = GlobalCommand.load_config()

    async def on_mount(self) -> None:
        await self.push_screen(CrontabView())  # This shows your main screen


def main():
    VwrconfApp().run()

