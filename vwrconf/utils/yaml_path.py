# vwrconf/utils/yaml_path.py

import os
import sys

CONFIG_PATH_FILE = os.path.expanduser("~/.vwrconf/vwrconf_config_path")

def cmd_config(args):
    """Set or show the default config path"""
    if args.set:
        # Store absolute path
        abs_path = os.path.abspath(args.set)
        if not os.path.isfile(abs_path):
            print(f"Error: File does not exist: {abs_path}")
            sys.exit(1)

        # Ensure the config directory exists
        config_dir = os.path.dirname(CONFIG_PATH_FILE)
        os.makedirs(config_dir, exist_ok=True)

        with open(CONFIG_PATH_FILE, "w") as f:
            f.write(abs_path)

        print(f"Default config path set to: {abs_path}")
    else:
        # Show absolute path (if it exists)
        if os.path.exists(CONFIG_PATH_FILE):
            with open(CONFIG_PATH_FILE) as f:
                path = f.read().strip()
            print(f"Default config path: {path}")
        else:
            print("No default config path set.")

