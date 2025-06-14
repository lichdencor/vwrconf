# vwrconf/cli/Commands/CronCommands.py

from vwrconf.cli.Commands.GlobalCommand import GlobalCommand

import sys
from vwrconf.core.view_crontab import fetch_all_crontabs
from vwrconf.core.diff import diff_crontabs
from vwrconf.models.Backup.cron import CronBackup
from vwrconf.models.Crontab.crontab_entry import CrontabEntry
from vwrconf.utils.entry_parser import normalize_line
from vwrconf.utils.filters import filter_entries


class CronCommands(GlobalCommand):
    @classmethod
    def cmd_view_crontabs(cls, args):
        config = cls.load_config(args.config)
        crontabs = fetch_all_crontabs(config)
        for host, jobs in crontabs.items():
            print(f"\n🔸 Crontab for {host}:")
            entries = [CrontabEntry(line, host=host, source="live") for line in jobs if line.strip()]
            filtered_entries = filter_entries(entries, args.grep) if args.grep else entries
            for entry in filtered_entries:
                print(f"  {entry.line}")

    @classmethod
    def cmd_backup_crontabs(cls, args):
        config = cls.load_config(args.config)
        crontabs = fetch_all_crontabs(config)
        backup = CronBackup(config)
        for host, lines in crontabs.items():
            backup.write_backup(host, lines)

    @classmethod
    def cmd_restore_crontab(cls, args):
        config = cls.load_config(args.config)
        backup = CronBackup(config)
        success = backup.restore_backup(args.host, args.file)
        if not success:
            sys.exit(1)

    @classmethod
    def cmd_list_backup_dates(cls, args):
        config = cls.load_config(args.config)
        backup = CronBackup(config)
        dates = backup.read_backup_stored_dates(args.host)
        if dates:
            print(f"Available backups for '{args.host}':")
            for d in dates:
                print(f"  - {d}")
        else:
            print(f"No backups found for '{args.host}'.")

    @classmethod
    def cmd_read_backup_file(cls, args):
        config = cls.load_config(args.config)
        backup = CronBackup(config)
        lines = backup.read_backup_stored(args.host, args.file)
        print(f"Contents of backup {args.file} for {args.host}:\n")
        for line in lines:
            print(line)

    @classmethod
    def cmd_list_backup_hosts(cls, args):
        config = cls.load_config(args.config)
        backup = CronBackup(config)
        hosts = backup.read_backup_known_hosts()
        if hosts:
            print("Hosts with backups:")
            for h in hosts:
                print(f"  - {h}")
        else:
            print("No hosts with backups found.")    

    @classmethod
    def cmd_diff_live_backup(cls, args):
        config = cls.load_config(args.config)
        crontabs = fetch_all_crontabs(config)
        backup = CronBackup(config)

        host = args.host
        if host not in crontabs:
            print(f"Host '{host}' not found in live crontabs.")
            sys.exit(1)

        latest_backup = backup.latest_backup_filename(host)
        if not latest_backup:
            print(f"No backups found for host '{host}'.")
            sys.exit(1)

        live_lines = crontabs[host]
        backup_lines = backup.read_backup_stored(host, latest_backup)

        live_entries = {
            CrontabEntry(line, host=host, source="live")
            for line in live_lines
            if line.strip() and not line.strip().startswith("#")
        }
        backup_entries = {
            CrontabEntry(line, host=host, source="backup")
            for line in backup_lines
            if line.strip() and not line.strip().startswith("#")
        }

        if args.grep:
            live_entries = set(filter_entries(list(live_entries), args.grep))
            backup_entries = set(filter_entries(list(backup_entries), args.grep))

        diff = diff_crontabs(live_entries, backup_entries)

        print(f"\n[{host}] Diff between live and latest backup ({latest_backup}):")

        RED = "\033[91m"
        GREEN = "\033[92m"
        GRAY = "\033[90m"
        RESET = "\033[0m"

        print(f"  Added ({len(diff['added'])}):")
        for e in diff["added"]:
            print(f"    {GREEN}+ {e.line}{RESET}")

        print(f"  Removed ({len(diff['removed'])}):")
        for e in diff["removed"]:
            print(f"    {RED}- {e.line}{RESET}")

        print(f"  Unchanged ({len(diff['unchanged'])}):")
        for e in diff["unchanged"]:
            print(f"    {GRAY}  {e.line}{RESET}")


    @classmethod
    def cmd_diff_backups(cls, args):
        config = cls.load_config(args.config)
        backup = CronBackup(config)

        older_file = args.file1
        newer_file = args.file2
        host = args.host

        older_lines = backup.read_backup_stored(host, older_file)
        newer_lines = backup.read_backup_stored(host, newer_file)

        if not older_lines or not newer_lines:
            print(f"Missing data in one or both backup files for host '{host}'.")
            sys.exit(1)

        older_entries = {
            CrontabEntry(line, host=host, source="backup")
            for line in older_lines
            if line.strip() and not line.strip().startswith("#")
        }
        newer_entries = {
            CrontabEntry(line, host=host, source="backup")
            for line in newer_lines
            if line.strip() and not line.strip().startswith("#")
        }

        if args.grep:
            older_entries = set(filter_entries(list(older_entries), args.grep))
            newer_entries = set(filter_entries(list(newer_entries), args.grep))

        diff = diff_crontabs(newer_entries, older_entries)

        RED = "\033[91m"
        GREEN = "\033[92m"
        GRAY = "\033[90m"
        RESET = "\033[0m"

        print(f"  Added ({len(diff['added'])}):")
        for e in diff["added"]:
            print(f"    {GREEN}+ {e.line}{RESET}")

        print(f"  Removed ({len(diff['removed'])}):")
        for e in diff["removed"]:
            print(f"    {RED}- {e.line}{RESET}")

        print(f"  Unchanged ({len(diff['unchanged'])}):")
        for e in diff["unchanged"]:
            print(f"    {GRAY}  {e.line}{RESET}")


    @classmethod
    def cmd_diff_hosts(cls, args):
        config = cls.load_config(args.config)
        crontabs = fetch_all_crontabs(config)

        host1 = args.host1
        host2 = args.host2

        if host1 not in crontabs or host2 not in crontabs:
            print("One or both hosts not found in live crontabs.")
            if host1 not in crontabs:
                print(f"  ✘ Missing: {host1}")
            if host2 not in crontabs:
                print(f"  ✘ Missing: {host2}")
            sys.exit(1)

        def parse_lines(lines, host):
            entries = set()
            for line in lines:
                if not line.strip() or line.strip().startswith("#"):
                    continue
                line_str = normalize_line(line) if args.normalize else line
                entries.add(CrontabEntry(line_str, host=host, source="live"))
            return entries

        entries1 = parse_lines(crontabs[host1], host1)
        entries2 = parse_lines(crontabs[host2], host2)

        if args.grep:
            entries1 = set(filter_entries(list(entries1), args.grep))
            entries2 = set(filter_entries(list(entries2), args.grep))

        diff = diff_crontabs(entries2, entries1)  # new, old

        RED = "\033[91m"
        GREEN = "\033[92m"
        GRAY = "\033[90m"
        RESET = "\033[0m"

        print(f"\n🔸 Diff between live crontabs of '{host1}' and '{host2}':\n")

        print(f"  Added in {host2} (not in {host1}) ({len(diff['added'])}):")
        for e in diff["added"]:
            print(f"    {GREEN}+ {e.line}{RESET}")

        print(f"  Removed from {host1} (missing in {host2}) ({len(diff['removed'])}):")
        for e in diff["removed"]:
            print(f"    {RED}- {e.line}{RESET}")

        print(f"  Common to both ({len(diff['unchanged'])}):")
        for e in diff["unchanged"]:
            print(f"    {GRAY}  {e.line}{RESET}")

