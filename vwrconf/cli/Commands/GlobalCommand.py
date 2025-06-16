# vwrconf/cli/Commands/GlobalCommand.py

import os
from vwrconf.models.config_model import Config
import yaml
import re

CONFIG_PATH_FILE = os.path.expanduser("~/.vwrconf/vwrconf_config_path")

class GlobalCommand:
    @classmethod
    def load_config(cls, path=None) -> Config:
        """
        Load the configuration file as a Config object.

        If no path is given, attempts to read it from the default location.
        Falls back to a built-in path if needed.

        Args:
            path (str, optional): Path to the config file.

        Returns:
            Config: Loaded configuration object.

        Raises:
            FileNotFoundError: If the config file cannot be found.
        """
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
        """
        Compile a regular expression pattern with optional case insensitivity.

        Args:
            pattern (str | None): Regex pattern to compile.
            ignore_case (bool): Whether to ignore case in matching.

        Returns:
            re.Pattern | None: Compiled regex object, or None if pattern is not given.
        """
        if not pattern:
            return None
        flags = re.IGNORECASE if ignore_case else 0
        return re.compile(pattern, flags)

    @staticmethod
    def grep_lines(text: str, pattern: re.Pattern | None) -> list[str]:
        """
        Filter lines of text using a compiled regex pattern.

        Args:
            text (str): Multiline string to filter.
            pattern (re.Pattern | None): Compiled regex pattern.

        Returns:
            list[str]: Lines that match the pattern, or all lines if no pattern.
        """
        if not pattern:
            return text.splitlines()
        return [line for line in text.splitlines() if pattern.search(line)]

    @classmethod
    def should_filter_host(cls, args, is_diff: bool = False) -> Config:
        """
        Return a filtered config with a specific host or the full config.

        If `select_host` is present in args and not a diff command, returns a config with just that host.
        Otherwise, loads and returns the full config.

        Args:
            args: Parsed CLI arguments with optional `select_host` and `config`.
            is_diff (bool): If True, skips filtering.

        Returns:
            Config: Config object filtered by host or full config.

        Raises:
            ValueError: If the specified host is not found in the config.
        """
        if is_diff or not hasattr(args, "select_host") or not args.select_host:
            return cls.load_config(getattr(args, "config", None))

        config = cls.load_config(getattr(args, "config", None))
        selected = next((c for c in config.clients if c.id == args.select_host), None)
        if not selected:
            raise ValueError(f"Host '{args.select_host}' not found in config.")
        return Config(defaults=config.defaults, clients=[selected])

    @staticmethod
    def verbose_log(args, message: str):
        """
        Print a verbose log message if the --verbose flag is set.

        Args:
            args: Parsed CLI arguments containing a 'verbose' attribute.
            message (str): Message to print.
        """
        if getattr(args, "verbose", False):
            print(f"[vwrconf][verbose] {message}")

