# vwrconf/cli/Commands/CronCommands.py

from vwrconf.cli.Commands.GlobalCommand import GlobalCommand

import sys
from vwrconf.core.view_crontab import fetch_all_crontabs
from vwrconf.core.diff import diff_crontabs
from vwrconf.models.Backup.cron import CronBackup
from vwrconf.models.Crontab.crontab_entry import CrontabEntry
from vwrconf.utils.entry_parser import normalize_line



class CronCommands(GlobalCommand):
    @classmethod
    def cmd_view_crontabs(cls, args):
        cls.verbose_log(args, "Loading config and fetching live crontabs...")
        config = cls.should_filter_host(args)
        crontabs = fetch_all_crontabs(config)
        pattern = cls.compile_grep_pattern(args.grep, args.ignore_case)

        for host, jobs in crontabs.items():
            print(f"\n🔸 Crontab for {host}:")
            entries = [CrontabEntry(line, host=host, source="live") for line in jobs if line.strip()]
            for entry in entries:
                lines = cls.grep_lines(entry.line, pattern)
                if lines:
                    print(f"  {entry.line}")
        cls.verbose_log(args, "Finished displaying crontabs.")

    @classmethod
    def cmd_backup_crontabs(cls, args):
        cls.verbose_log(args, "Loading config and starting backup of live crontabs...")
        config = cls.should_filter_host(args)
        crontabs = fetch_all_crontabs(config)
        backup = CronBackup(config)
        for host, lines in crontabs.items():
            cls.verbose_log(args, f"Writing backup for host '{host}'...")
            backup.write_backup(host, lines)
        cls.verbose_log(args, "All backups completed.")

    @classmethod
    def cmd_restore_crontab(cls, args):
        cls.verbose_log(args, "Loading config and preparing to restore crontab...")
        config = cls.load_config(args.config)
        backup = CronBackup(config)

        lines = backup.read_backup_stored(args.host, args.file)
        if not lines:
            print(f"[ERROR] Backup file '{args.file}' for host '{args.host}' is empty or not found.")
            sys.exit(1)

        if getattr(args, "dry_run", False):
            print(f"[DRY RUN] This is the content of '{args.file}' that would be restored to host '{args.host}':\n")
            for line in lines:
                print(line)
            return

        confirm = input(f"\nAre you sure you want to overwrite the crontab on host '{args.host}' with backup '{args.file}'? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Aborted by user.")
            sys.exit(0)

        cls.verbose_log(args, f"Restoring crontab on host '{args.host}' from file '{args.file}'...")
        success = backup.restore_backup(args.host, args.file)
        if not success:
            print(f"[ERROR] Failed to restore backup '{args.file}' on host '{args.host}'.")
            sys.exit(1)

        print(f"[OK] Crontab restored successfully on host '{args.host}' from backup '{args.file}'.")

    @classmethod
    def cmd_list_backup_dates(cls, args):
        cls.verbose_log(args, f"Loading backup dates for host '{args.host}'...")
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
        cls.verbose_log(args, f"Reading backup file '{args.file}' for host '{args.host}'...")
        config = cls.load_config(args.config)
        backup = CronBackup(config)
        lines = backup.read_backup_stored(args.host, args.file)
        pattern = cls.compile_grep_pattern(args.grep, args.ignore_case)

        print(f"Contents of backup {args.file} for {args.host}:\n")
        for line in lines:
            if cls.grep_lines(line, pattern):
                print(line)

    @classmethod
    def cmd_list_backup_hosts(cls, args):
        cls.verbose_log(args, "Listing all known backup hosts...")
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
        cls.verbose_log(args, f"Loading config and live crontab for host '{args.host}'...")
        config = cls.should_filter_host(args, is_diff=True)
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

        cls.verbose_log(args, f"Comparing live crontab against latest backup: {latest_backup}")

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

        pattern = cls.compile_grep_pattern(args.grep, args.ignore_case)
        if pattern:
            live_entries = {
                entry for entry in live_entries if cls.grep_lines(entry.line, pattern)
            }
            backup_entries = {
                entry for entry in backup_entries if cls.grep_lines(entry.line, pattern)
            }

        diff = diff_crontabs(live_entries, backup_entries)

        print(f"\n[{host}] Diff between live and latest backup ({latest_backup}):")

        RED = "\033[91m"
        GREEN = "\033[92m"
        RESET = "\033[0m"

        print(f"  Added ({len(diff['added'])}):")
        for e in diff["added"]:
            print(f"    {GREEN}+ {e.line}{RESET}")

        print(f"  Removed ({len(diff['removed'])}):")
        for e in diff["removed"]:
            print(f"    {RED}- {e.line}{RESET}")

        if not diff["added"] and not diff["removed"]:
            print("  No differences found.")


    @classmethod
    def cmd_diff_backups(cls, args):
        cls.verbose_log(args, f"Loading config and backup files for host '{args.host}'...")
        config = cls.should_filter_host(args, is_diff=True)
        backup = CronBackup(config)

        older_file = args.file1
        newer_file = args.file2
        host = args.host

        older_lines = backup.read_backup_stored(host, older_file)
        newer_lines = backup.read_backup_stored(host, newer_file)

        if not older_lines or not newer_lines:
            print(f"Missing data in one or both backup files for host '{host}'.")
            sys.exit(1)

        cls.verbose_log(args, f"Comparing '{older_file}' → '{newer_file}'...")

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

        pattern = cls.compile_grep_pattern(args.grep, args.ignore_case)
        if pattern:
            older_entries = {e for e in older_entries if cls.grep_lines(e.line, pattern)}
            newer_entries = {e for e in newer_entries if cls.grep_lines(e.line, pattern)}

        diff = diff_crontabs(newer_entries, older_entries)

        RED = "\033[91m"
        GREEN = "\033[92m"
        RESET = "\033[0m"

        print(f"\n[{host}] Diff between backups '{older_file}' → '{newer_file}':")

        print(f"  Added ({len(diff['added'])}):")
        for e in diff["added"]:
            print(f"    {GREEN}+ {e.line}{RESET}")

        print(f"  Removed ({len(diff['removed'])}):")
        for e in diff["removed"]:
            print(f"    {RED}- {e.line}{RESET}")

        if not diff["added"] and not diff["removed"]:
            print("  No differences found.")


    @classmethod
    def cmd_diff_hosts(cls, args):
        cls.verbose_log(args, f"Loading live crontabs for '{args.host1}' and '{args.host2}'...")
        config = cls.should_filter_host(args, is_diff=True)
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

        cls.verbose_log(args, "Parsing and normalizing crontab lines for comparison...")

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

        pattern = cls.compile_grep_pattern(args.grep, args.ignore_case)
        if pattern:
            entries1 = {e for e in entries1 if cls.grep_lines(e.line, pattern)}
            entries2 = {e for e in entries2 if cls.grep_lines(e.line, pattern)}

        diff = diff_crontabs(entries2, entries1)  # new, old

        RED = "\033[91m"
        GREEN = "\033[92m"
        RESET = "\033[0m"

        print(f"\n🔸 Diff between live crontabs of '{host1}' and '{host2}':\n")

        print(f"  Added in {host2} (not in {host1}) ({len(diff['added'])}):")
        for e in diff["added"]:
            print(f"    {GREEN}+ {e.line}{RESET}")

        print(f"  Removed from {host1} (missing in {host2}) ({len(diff['removed'])}):")
        for e in diff["removed"]:
            print(f"    {RED}- {e.line}{RESET}")

        if not diff["added"] and not diff["removed"]:
            print("  No differences found.")
