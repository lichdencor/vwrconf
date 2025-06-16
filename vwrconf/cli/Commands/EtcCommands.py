# vwrconf/cli/Commands/EtcCommands.py

import sys
import os
from vwrconf.cli.Commands.GlobalCommand import GlobalCommand
from vwrconf.models.Backup.etc import EtcBackup
from vwrconf.core.view_etc import fetch_all_etc
from vwrconf.models.Etc.etc_entry import EtcEntry
from vwrconf.core.diff import diff_etc_files
import getpass

class EtcCommands(GlobalCommand):
    @classmethod
    def cmd_view_etc(cls, args):
        config = cls.should_filter_host(args)

        sudo_needed = any(c.ssh_user != "root" for c in config.clients)
        sudo_password = getpass.getpass("Enter sudo password for remote hosts: ") if sudo_needed else None

        data = fetch_all_etc(config, args.paths, sudo_password=sudo_password)

        for host, files in data.items():
            print(f"\n🔸 /etc files on {host}:")
            for path, content in files.items():
                print(f"\n# {path}\n{content}")

    @classmethod
    def cmd_backup_etc(cls, args):
        config = cls.load_config(args.config)
        backup = EtcBackup(config)

        sudo_needed = any(c.ssh_user != "root" and not c.readonly for c in config.clients)
        sudo_password = getpass.getpass("Enter sudo password for remote hosts: ") if sudo_needed else None

        for client in config.clients:
            backup.write_backup(client.id, args.paths, sudo_password=sudo_password)

    @classmethod
    def cmd_restore_etc(cls, args):
        config = cls.load_config(args.config)
        backup = EtcBackup(config)

        # Validar host
        if args.host not in [c.id for c in config.clients]:
            print(f"[ERROR] Host '{args.host}' not found in config.")
            sys.exit(1)

        # Validar timestamp disponible
        valid_timestamps = backup.read_backup_stored_dates(args.host)
        if not valid_timestamps:
            print(f"[ERROR] No backups found for host '{args.host}'.")
            sys.exit(1)

        if args.timestamp not in valid_timestamps:
            print(f"[ERROR] Backup timestamp '{args.timestamp}' not found for host '{args.host}'.")
            print("Available backups:")
            for ts in valid_timestamps:
                print(f"  - {ts}")
            sys.exit(1)

        # Mostrar advertencia visible
        RED = "\033[91m"
        RESET = "\033[0m"
        print(f"{RED}[!]  You are about to overwrite /etc files on host '{args.host}' with backup from '{args.timestamp}'.{RESET}")
        print("This operation is potentially destructive and cannot be undone.")

        if not args.force:
            first_confirm = input("Type 'yes' to continue: ").strip().lower()
            if first_confirm != "yes":
                print("Aborted.")
                sys.exit(0)

            second_confirm = input("Type 'yes, I understand this will overwrite files' to confirm: ").strip().lower()
            if second_confirm != "yes, i understand this will overwrite files":
                print("Aborted.")
                sys.exit(0)

        if args.dry_run:
            print("[DRY RUN] Showing files that would be restored:")
            files = backup.read_backup_stored(args.host, args.timestamp)
            for line in files:
                print(line)
            sys.exit(0)

        success = backup.restore_backup(args.host, args.timestamp)
        if success:
            print(f"[OK] Backup from {args.timestamp} restored on host '{args.host}'.")
        else:
            print("[ERROR] Restore failed.")
            sys.exit(1)

    @classmethod
    def cmd_list_etc_dates(cls, args):
        config = cls.load_config(args.config)
        backup = EtcBackup(config)
        dates = backup.read_backup_stored_dates(args.host)
        if dates:
            print(f"Available /etc backups for '{args.host}':")
            for d in dates:
                print(f"  - {d}")
        else:
            print(f"No /etc backups found for '{args.host}'.")

    @classmethod
    def cmd_read_etc_backup(cls, args):
        config = cls.load_config(args.config)
        backup = EtcBackup(config)
        contents = backup.read_backup_stored(args.host, args.timestamp)

        pattern = cls.compile_grep_pattern(args.grep, getattr(args, "ignore_case", False))
        print(f"\nContents of /etc backup '{args.timestamp}' for host '{args.host}':\n")

        for file_content in contents:
            filtered = cls.grep_lines(file_content, pattern)
            if filtered:
                print("\n".join(filtered))

    @classmethod
    def cmd_list_etc_hosts(cls, args):
        config = cls.load_config(args.config)
        backup = EtcBackup(config)
        hosts = backup.read_backup_known_hosts()
        if hosts:
            print("Hosts with /etc backups:")
            for h in hosts:
                print(f"  - {h}")
        else:
            print("No /etc backups found.")

    @classmethod
    def diff_line_level(cls, new_files, old_files, host):
        # Parse line entries from each set
        new_entries = cls.parse_etc_entries(new_files, host, source="new")
        old_entries = cls.parse_etc_entries(old_files, host, source="old")

        added = new_entries - old_entries
        removed = old_entries - new_entries

        cls.print_line_diff(added, removed)

    @classmethod
    def cmd_diff_live_backup_etc(cls, args):
        config = cls.should_filter_host(args, is_diff=True)
        etc_backup = EtcBackup(config)
        live_etc_data = fetch_all_etc(config, args.paths)  # {host: {path: content}}

        host = args.host
        if host not in live_etc_data:
            print(f"Host '{host}' not found in live /etc data.")
            sys.exit(1)

        latest_backup = etc_backup.latest_backup_filename(host)
        if not latest_backup:
            print(f"No /etc backups found for host '{host}'.")
            sys.exit(1)

        host_dir = etc_backup._get_host_backup_dir(host)
        backup_files = {}
        for f in os.listdir(host_dir):
            if f.startswith(latest_backup) and f.endswith(".etc"):
                path_part = f.split("__",1)[-1].replace(".etc", "").replace("_", "/")
                full_path = os.path.join(host_dir, f)
                with open(full_path, "r") as fp:
                    backup_files[f"/{path_part}"] = fp.read()

        live_files = live_etc_data[host]

        diff_result = diff_etc_files(live_files, backup_files)

        RED = "\033[91m"
        GREEN = "\033[92m"
        RESET = "\033[0m"

        print(f"\n[{host}] Diff between live /etc and latest backup ({latest_backup}):\n")

        print(f"  Added files ({len(diff_result['added'])}):")
        for f in diff_result["added"]:
            print(f"    {GREEN}+ {f}{RESET}")

        print(f"  Removed files ({len(diff_result['removed'])}):")
        for f in diff_result["removed"]:
            print(f"    {RED}- {f}{RESET}")

        print(f"  Changed files ({len(diff_result['changed'])}):")
        for f in diff_result["changed"]:
            print(f"\n--- {f} ---")
            # Line-level diff for each changed file only:
            cls.diff_line_level(
                {f: live_files.get(f, "")},
                {f: backup_files.get(f, "")},
                host
            )

        if not diff_result["added"] and not diff_result["removed"] and not diff_result["changed"]:
            print("  No differences found.")

    @classmethod
    def cmd_diff_backups_etc(cls, args):
        config = cls.should_filter_host(args, is_diff=True)
        etc_backup = EtcBackup(config)
        host = args.host

        def load_backup_files(timestamp):
            host_dir = etc_backup._get_host_backup_dir(host)
            files = [f for f in os.listdir(host_dir) if f.startswith(timestamp) and f.endswith(".etc")]
            files_content = {}
            for f in files:
                path_part = f.split("__", 1)[-1].replace(".etc", "").replace("_", "/")
                with open(os.path.join(host_dir, f), "r") as fp:
                    files_content[f"/{path_part}"] = fp.read()
            return files_content

        older_files = load_backup_files(args.file1)
        newer_files = load_backup_files(args.file2)

        diff_result = diff_etc_files(newer_files, older_files)

        RED = "\033[91m"
        GREEN = "\033[92m"
        RESET = "\033[0m"

        print(f"\n[{host}] Diff between /etc backups '{args.file1}' → '{args.file2}':\n")

        print(f"  Added files ({len(diff_result['added'])}):")
        for f in diff_result["added"]:
            print(f"    {GREEN}+ {f}{RESET}")

        print(f"  Removed files ({len(diff_result['removed'])}):")
        for f in diff_result["removed"]:
            print(f"    {RED}- {f}{RESET}")

        print(f"  Changed files ({len(diff_result['changed'])}):")
        for f in diff_result["changed"]:
            print(f"\n--- {f} ---")
            cls.diff_line_level(
                {f: newer_files.get(f, "")},
                {f: older_files.get(f, "")},
                host
            )

        if not diff_result["added"] and not diff_result["removed"] and not diff_result["changed"]:
            print("  No differences found.")

    @classmethod
    def cmd_diff_hosts_etc(cls, args):
        config = cls.should_filter_host(args, is_diff=True)
        live_etc = fetch_all_etc(config, args.paths)

        host1 = args.host1
        host2 = args.host2

        if host1 not in live_etc or host2 not in live_etc:
            print("One or both hosts not found in live /etc data.")
            if host1 not in live_etc:
                print(f"  ✘ Missing: {host1}")
            if host2 not in live_etc:
                print(f"  ✘ Missing: {host2}")
            sys.exit(1)

        diff_result = diff_etc_files(live_etc[host2], live_etc[host1])

        RED = "\033[91m"
        GREEN = "\033[92m"
        RESET = "\033[0m"

        print(f"\n🔸 Diff between live /etc of '{host1}' and '{host2}':\n")

        print(f"  Added files in {host2} (not in {host1}) ({len(diff_result['added'])}):")
        for f in diff_result["added"]:
            print(f"    {GREEN}+ {f}{RESET}")

        print(f"  Removed files from {host1} (missing in {host2}) ({len(diff_result['removed'])}):")
        for f in diff_result["removed"]:
            print(f"    {RED}- {f}{RESET}")

        print(f"  Changed files ({len(diff_result['changed'])}):")
        for f in diff_result["changed"]:
            print(f"\n--- {f} ---")
            cls.diff_line_level(
                {f: live_etc[host2].get(f, "")},
                {f: live_etc[host1].get(f, "")},
                host2
            )

        if not diff_result["added"] and not diff_result["removed"] and not diff_result["changed"]:
            print("  No differences found.")

    @classmethod
    def parse_etc_entries(cls, files_dict, host, source="live"):
        entries = set()
        for path, content in files_dict.items():
            for line in content.splitlines():
                if line.strip():
                    entries.add(EtcEntry(line=line, host=host, path=path, source=source))
        return entries

    @classmethod
    def print_line_diff(cls, added, removed):
        RED = "\033[91m"
        GREEN = "\033[92m"
        RESET = "\033[0m"

        if added:
            print(f"  Added lines ({len(added)}):")
            for entry in sorted(added, key=lambda e: (e.path, e.line)):
                print(f"    {GREEN}+ {entry.path}: {entry.line}{RESET}")
        else:
            print("  No added lines.")

        if removed:
            print(f"  Removed lines ({len(removed)}):")
            for entry in sorted(removed, key=lambda e: (e.path, e.line)):
                print(f"    {RED}- {entry.path}: {entry.line}{RESET}")
        else:
            print("  No removed lines.")
