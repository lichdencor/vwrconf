# vwrconf

**vwrconf** is a terminal-native TUI tool to **view, diff, edit, and synchronize configuration files** across multiple Unix systems — currently via SSH. It was initially focused on crontabs, and is now expanding into a broader multi-host configuration management utility with support for systemd units, SSHD configs, nginx files, and more.

Built with extensibility, auditability, and portability in mind, `vwrconf` enables reliable config inspection and control from the command line or a powerful TUI interface.

---

## Vision & Connectivity

**Current:** Operates over SSH, using per-host credentials or `~/.ssh/config`.

**Planned support for additional communication channels:**

- [✓] SSH (current)
- [?] Reverse SSH tunnels
- [?] Mesh VPNs (Tailscale, Zerotier)
- [?] gRPC/TLS agent API (`vwrconf-agent`)
- [?] GitOps-style central pull (Git-based snapshots)
- [?] Pub/Sub event systems (MQTT, WebSockets)

All integrations will conform to a unified interface (`.fetch()`, `.diff()`, `.push()`, etc.) via the plugin system.

---

## Features

- [✓] SSH-based access using `~/.ssh/config`, key files, or password auth
- [✓] View and edit crontab entries across multiple remote hosts
- [✓] Diff configurations between systems to detect drift
- [✓] Backup and restore crontabs by host and timestamp
- [✓] Detect syntax errors, duplicates, and conflicting job schedules
- [?] Search and filter jobs by time, command, host, or tags
- [?] Tagging support (e.g., `#backup`, `#monitoring`)
- [?] TUI interface with multi-pane layout and keyboard shortcuts
- [?] Configuration file in YAML or TOML with host/group definitions
- [?] Plugin system for other domains: `systemd`, `nginx`, `sshd`
- [?] Export to HTML or JSON for audits and reports
- [?] Offline mode with last-known cache
- [?] Role-based access modes: admin, operator, viewer
- [?] Git-based snapshot exports
- [?] Audit logs and history
- [?] Agent protocol (gRPC/TLS)

---

## Installation

Requires Python 3.9+

### Option 1: Installer Script

Run:

    ./install_vwrconf.sh

This will install the tool system-wide or locally and place the `vwrconf` executable in your `$PATH`.

### Option 2: Manual Install

Create a virtual environment and install the dependencies manually:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

---

## Configuration

Default config path:

    ~/.config/vwrconf/vwrconf.yml

(If you chose a different filename during install, adjust accordingly.)

Use a custom config path:

    vwrconf config -c /path/to/config.yml

Each host entry can define:

- SSH connection info (host, user, port)
- Tags and groups for filtering
- Plugins to load per host
- Access level (e.g., read-only, full control)

Supports both YAML and TOML formats.

---

## Usage

To launch the TUI interface:

    vwrconf
    # or
    python3 -m vwrconf

Inside the interface:

- Browse host list and their config domains
- View diffs, job metadata, and status
- Edit, clone, or delete jobs across hosts
- Perform backups or restore from snapshots
- Export to disk or remote location

A headless CLI mode is also supported for scripting and automation workflows.

---

## Development Roadmap

Below is the staged plan of features and capabilities:

| Feature / Milestone          | Status     |
|-----------------------------|------------|
| Multi-host crontab TUI      | [?] Planned   |
| Backup/restore support      | [✓] Done   |
| Live diffing engine         | [✓] Done   |
| Plugin architecture         | [?] Planned|
| Systemd/nginx/sshd support  | [?] Planned|
| HTML/JSON report export     | [?] Planned|
| Git snapshot integration    | [?] Planned|
| Agent protocol (gRPC/TLS)   | [?] Optional|
| Role-based access (RBAC)    | [?] Planned|
| MQTT or WebSocket support   | [?] Exploratory|

See `FEATURES.md` and `TODO.md` for detailed task tracking.

---

## Contributing

All contributions are welcome.

The plugin system will allow developers to add:

- New configuration domains (e.g., `systemd`, `nginx`, `firewalld`)
- Transport layers (e.g., gRPC agents, MQTT relays)
- Report/export formats (e.g., Markdown, XML, InfluxDB)
- Host discovery or synchronization logic

To contribute, fork the repo and open a pull request or discussion thread. A plugin authoring guide (`docs/PLUGIN_GUIDE.md`) will be added soon.

---

## License

MIT License © 2025
