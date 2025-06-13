# vwrconf/cli/parser.py

import argparse
import sys
from vwrconf.cli.Commands.CronCommands import CronCommands

from vwrconf.utils.yaml_path import cmd_config

def build_parser():
    """
    Builds the parser to run the cli commands
    """
    parser = argparse.ArgumentParser(
        prog="vwrconf",
        description="vwrconf – remote configuration manager"
    )
    top_level = parser.add_subparsers(dest="category", required=True)

    # 1. Subparser for "cron" commands
    cron_parser = top_level.add_parser("cron", help="Manage remote crontab configurations")
    cron_subparsers = cron_parser.add_subparsers(dest="command", required=True)

    # 2. Global config command (not under cron)
    config = top_level.add_parser("config", help="Manage vwrconf config path")
    config.add_argument("-s", "--set", metavar="PATH", help="Set default config YAML file path")
    config.set_defaults(func=cmd_config)

    # 3. Global regex common to subcommands
    def add_common_grep_arg(subparser):
        subparser.add_argument(
            "-g", "--grep",
            metavar="PATTERN",
            help="Filter entries by regex pattern"
        )


    # --- Cron subcommands ---
    # Subcommand: view
    view = cron_subparsers.add_parser("view", help="Fetch and display remote crontabs")
    view.add_argument("-c", "--config", default=None)
    add_common_grep_arg(view)
    view.set_defaults(func=CronCommands.cmd_view_crontabs)

    # Subcommand: backup
    backup = cron_subparsers.add_parser("backup", help="Backup remote crontabs to local files")
    backup.add_argument("-c", "--config", default=None)
    backup.set_defaults(func=CronCommands.cmd_backup_crontabs)

    # Subcommand: restore
    restore = cron_subparsers.add_parser("restore", help="Restore a crontab to a remote host")
    restore.add_argument("host")
    restore.add_argument("file")
    restore.add_argument("-c", "--config", default=None)
    restore.set_defaults(func=CronCommands.cmd_restore_crontab)

    # Subcommand: read dates
    dates = cron_subparsers.add_parser("read-dates", help="List backup snapshots for a host")
    dates.add_argument("host")
    dates.add_argument("-c", "--config", default=None)
    dates.set_defaults(func=CronCommands.cmd_list_backup_dates)

    # Subcommand: read file
    read = cron_subparsers.add_parser("read-file", help="Print contents of a crontab backup file")
    read.add_argument("host")
    read.add_argument("file")
    read.add_argument("-c", "--config", default=None)
    add_common_grep_arg(read)
    read.set_defaults(func=CronCommands.cmd_read_backup_file)

    # Subcommand: list hosts
    list_hosts = cron_subparsers.add_parser("list-hosts", help="List all hosts with backups")
    list_hosts.add_argument("-c", "--config", default=None)
    list_hosts.set_defaults(func=CronCommands.cmd_list_backup_hosts)

    # Subcommand: diff live hosts
    diff_live = cron_subparsers.add_parser("diff-live", help="Diff between live crontab and latest backup")
    diff_live.add_argument("host")
    diff_live.add_argument("-c", "--config", default=None)
    add_common_grep_arg(diff_live)
    diff_live.set_defaults(func=CronCommands.cmd_diff_live_backup)

    # Subcommand: diff backup files
    diff_backups = cron_subparsers.add_parser("diff-backups", help="Diff between two crontab backups for a host")
    diff_backups.add_argument("host")
    diff_backups.add_argument("file1")
    diff_backups.add_argument("file2")
    diff_backups.add_argument("-c", "--config", default=None)
    add_common_grep_arg(diff_backups)
    diff_backups.set_defaults(func=CronCommands.cmd_diff_backups)

    # Subcommand: diff hosts
    diff_hosts = cron_subparsers.add_parser("diff-hosts", help="Diff between two hosts' crontabs")
    diff_hosts.add_argument("host1")
    diff_hosts.add_argument("host2")
    diff_hosts.add_argument("-c", "--config", default=None)
    diff_hosts.add_argument("-n", "--normalize", action="store_true")
    add_common_grep_arg(diff_hosts)
    diff_hosts.set_defaults(func=CronCommands.cmd_diff_hosts)



    return parser

def run_cli():
    parser = build_parser()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)

