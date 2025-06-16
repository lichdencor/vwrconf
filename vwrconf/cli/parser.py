# vwrconf/cli/parser.py

import argparse
import sys
from vwrconf.cli.Commands.CronCommands import CronCommands
from vwrconf.cli.Commands.EtcCommands import EtcCommands


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

    # 1.1. Subparser for "cron" commands
    cron_parser = top_level.add_parser("cron", help="Manage remote crontab configurations")
    cron_subparsers = cron_parser.add_subparsers(dest="command", required=True)

    # 1.2. Subparser for "etc" commands
    etc_parser = top_level.add_parser("etc", help="Manage remote /etc file backups")
    etc_subparsers = etc_parser.add_subparsers(dest="command", required=True)

    # 2. Global config command
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
        subparser.add_argument(
            "-i", "--ignore-case",
            action="store_true",
            help="Perform case-insensitive matching"
        )
        subparser.add_argument(
            "-s", "--select-host",
            metavar="HOST",
            help="Only show output for this host"
        )


    # --- Cron subcommands ---
    # Subcommand: cron_view
    cron_view = cron_subparsers.add_parser("view", help="Fetch and display remote crontabs")
    cron_view.add_argument("-c", "--config", default=None)
    add_common_grep_arg(cron_view)
    cron_view.set_defaults(func=CronCommands.cmd_view_crontabs)

    # Subcommand: cron_backup
    cron_backup = cron_subparsers.add_parser("backup", help="Backup remote crontabs to local files")
    cron_backup.add_argument("-c", "--config", default=None)
    cron_backup.set_defaults(func=CronCommands.cmd_backup_crontabs)

    # Subcommand: cron_restore
    cron_restore = cron_subparsers.add_parser("restore", help="Restore a crontab to a remote host")
    cron_restore.add_argument("host")
    cron_restore.add_argument("file")
    cron_restore.add_argument("-c", "--config", default=None)
    cron_restore.add_argument("--dry-run", action="store_true", help="Show what would be restored without applying it")
    cron_restore.set_defaults(func=CronCommands.cmd_restore_crontab)

    # Subcommand: cron_read_dates
    cron_read_dates = cron_subparsers.add_parser("read-dates", help="List backup snapshots for a host")
    cron_read_dates.add_argument("host")
    cron_read_dates.add_argument("-c", "--config", default=None)
    cron_read_dates.set_defaults(func=CronCommands.cmd_list_backup_dates)

    # Subcommand: cron_read_file
    cron_read_file = cron_subparsers.add_parser("read-file", help="Print contents of a crontab backup file")
    cron_read_file.add_argument("host")
    cron_read_file.add_argument("file")
    cron_read_file.add_argument("-c", "--config", default=None)
    add_common_grep_arg(cron_read_file)
    cron_read_file.set_defaults(func=CronCommands.cmd_read_backup_file)

    # Subcommand: cron_list_hosts
    cron_list_hosts = cron_subparsers.add_parser("list-hosts", help="List all hosts with backups")
    cron_list_hosts.add_argument("-c", "--config", default=None)
    cron_list_hosts.set_defaults(func=CronCommands.cmd_list_backup_hosts)

    # Subcommand: cron_diff_live
    cron_diff_live = cron_subparsers.add_parser("diff-live", help="Diff between live crontab and latest backup")
    cron_diff_live.add_argument("host")
    cron_diff_live.add_argument("-c", "--config", default=None)
    add_common_grep_arg(cron_diff_live)
    cron_diff_live.set_defaults(func=CronCommands.cmd_diff_live_backup)

    # Subcommand: cron_diff_backups
    cron_diff_backups = cron_subparsers.add_parser("diff-backups", help="Diff between two crontab backups for a host")
    cron_diff_backups.add_argument("host")
    cron_diff_backups.add_argument("file1")
    cron_diff_backups.add_argument("file2")
    cron_diff_backups.add_argument("-c", "--config", default=None)
    add_common_grep_arg(cron_diff_backups)
    cron_diff_backups.set_defaults(func=CronCommands.cmd_diff_backups)

    # Subcommand: cron_diff_hosts
    cron_diff_hosts = cron_subparsers.add_parser("diff-hosts", help="Diff between two hosts' crontabs")
    cron_diff_hosts.add_argument("host1")
    cron_diff_hosts.add_argument("host2")
    cron_diff_hosts.add_argument("-c", "--config", default=None)
    cron_diff_hosts.add_argument("-n", "--normalize", action="store_true")
    add_common_grep_arg(cron_diff_hosts)
    cron_diff_hosts.set_defaults(func=CronCommands.cmd_diff_hosts)


    # --- EtcCommands ---    
    # Subcommand: view /etc files
    etc_view = etc_subparsers.add_parser("view", help="View live /etc files from hosts")
    etc_view.add_argument("paths", nargs="+", help="Paths to /etc files to fetch (e.g., /etc/hostname)")
    etc_view.add_argument("-c", "--config", default=None)
    add_common_grep_arg(etc_view)
    etc_view.set_defaults(func=EtcCommands.cmd_view_etc)

    # Subcommand: backup /etc files
    etc_backup = etc_subparsers.add_parser("backup", help="Backup /etc files from all hosts")
    etc_backup.add_argument("paths", nargs="+", help="Paths to /etc files to fetch and store")
    etc_backup.add_argument("-c", "--config", default=None)
    etc_backup.set_defaults(func=EtcCommands.cmd_backup_etc)

    # Subcommand: restore /etc files to host
    etc_restore = etc_subparsers.add_parser("restore", help="Restore a set of /etc files to a host")
    etc_restore.add_argument("host", help="Host ID")
    etc_restore.add_argument("timestamp", help="Backup timestamp to restore")
    etc_restore.add_argument("-c", "--config", default=None)
    etc_restore.set_defaults(func=EtcCommands.cmd_restore_etc)

    # Subcommand: list available backup timestamps for host
    etc_dates = etc_subparsers.add_parser("read-dates", help="List /etc backup timestamps for a host")
    etc_dates.add_argument("host", help="Host ID")
    etc_dates.add_argument("-c", "--config", default=None)
    etc_dates.set_defaults(func=EtcCommands.cmd_list_etc_dates)

    # Subcommand: read contents of a stored backup
    etc_read = etc_subparsers.add_parser("read-file", help="Print contents of an /etc backup")
    etc_read.add_argument("host", help="Host ID")
    etc_read.add_argument("-c", "--config", default=None)
    etc_read.add_argument("-t", "--timestamp", required=True, help="Backup timestamp to restore")
    etc_read.add_argument("--dry-run", action="store_true", help="Print files that would be restored")
    etc_read.add_argument("--force", action="store_true", help="Skip confirmation prompts")

    add_common_grep_arg(etc_read)
    etc_read.set_defaults(func=EtcCommands.cmd_read_etc_backup)

    # Subcommand: list known backup hosts
    etc_hosts = etc_subparsers.add_parser("list-hosts", help="List hosts with /etc backups")
    etc_hosts.add_argument("-c", "--config", default=None)
    etc_hosts.set_defaults(func=EtcCommands.cmd_list_etc_hosts)

    # Subcommand: diff live host
    etc_diff_live = etc_subparsers.add_parser("diff-live", help="Diff between live /etc and latest backup")
    etc_diff_live.add_argument("host")
    etc_diff_live.add_argument("-c", "--config", default=None)
    add_common_grep_arg(etc_diff_live)  # Add this
    etc_diff_live.set_defaults(func=EtcCommands.cmd_diff_live_backup_etc)

    # Subcommand: diff backup files
    etc_diff_backups = etc_subparsers.add_parser("diff-backups", help="Diff between two /etc backups for a host")
    etc_diff_backups.add_argument("host")
    etc_diff_backups.add_argument("file1")
    etc_diff_backups.add_argument("file2")
    etc_diff_backups.add_argument("-c", "--config", default=None)
    add_common_grep_arg(etc_diff_backups)  # Add this
    etc_diff_backups.set_defaults(func=EtcCommands.cmd_diff_backups_etc)

    # Subcommand: diff hosts
    etc_diff_hosts = etc_subparsers.add_parser("diff-hosts", help="Diff live /etc files between two hosts")
    etc_diff_hosts.add_argument("host1")
    etc_diff_hosts.add_argument("host2")
    etc_diff_hosts.add_argument("-c", "--config", default=None)
    add_common_grep_arg(etc_diff_hosts)
    etc_diff_hosts.set_defaults(func=EtcCommands.cmd_diff_hosts_etc)



    return parser

def run_cli():
    parser = build_parser()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)

