# vwrconf/cli/Commands/GlobalCommand.py

import os
from vwrconf.models.config_model import Config
import yaml

CONFIG_PATH_FILE = os.path.expanduser("~/.vwrconf/vwrconf_config_path")

class GlobalCommand:
    @classmethod
    def load_config(cls, path=None) -> Config:
        if path is None:
            if os.path.exists(CONFIG_PATH_FILE):
                with open(CONFIG_PATH_FILE) as f:
                    path = f.read().strip()

        if path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(base_dir, "vwcron.yml")

        if not os.path.exists(path):
            raise FileNotFoundError(f"Could not find config file: {path}")

        with open(path) as f:
            raw = yaml.safe_load(f)

        return Config(**raw)
