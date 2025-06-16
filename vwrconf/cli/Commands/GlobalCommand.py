# vwrconf/cli/Commands/GlobalCommand.py

import os
from vwrconf.models.config_model import Config
import yaml
import re

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

    @staticmethod
    def compile_grep_pattern(pattern: str | None, ignore_case: bool) -> re.Pattern | None:
        if not pattern:
            return None
        flags = re.IGNORECASE if ignore_case else 0
        return re.compile(pattern, flags)

    @staticmethod
    def grep_lines(text: str, pattern: re.Pattern | None) -> list[str]:
        if not pattern:
            return text.splitlines()
        return [line for line in text.splitlines() if pattern.search(line)]

    @classmethod
    def should_filter_host(cls, args, is_diff: bool = False) -> Config:
        """
        Load a full or filtered config depending on select_host.
        If is_diff is True, skip select_host filtering and load full config.
        """
        if is_diff or not hasattr(args, "select_host") or not args.select_host:
            return cls.load_config(getattr(args, "config", None))

        config = cls.load_config(getattr(args, "config", None))
        selected = next((c for c in config.clients if c.id == args.select_host), None)
        if not selected:
            raise ValueError(f"Host '{args.select_host}' not found in config.")
        return Config(defaults=config.defaults, clients=[selected])
