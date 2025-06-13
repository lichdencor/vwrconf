# vwrconf - Feature Plan and Roadmap

`vwrconf` is a terminal-native tool to view, diff, manage, and synchronize configuration files across multiple Unix systems. Initially focused on crontabs, it is evolving into a general-purpose config management utility, supporting additional formats such as `sshd_config`, `nginx.conf`, and `systemd` units. Future versions will expand beyond SSH to support alternative transport mechanisms via a unified plugin interface.

---

## Architecture Overview

### Presentation Layer

- Textual-based TUI
- CLI for scripting and automation
- Optional HTML/JSON report views

### Core Logic

- Unified configuration parsing and diff engine
- Backup and restore system
- Structured, editable config views
- Plugin system for config formats and transport protocols

---

## Access and Security

- [x] SSH-based remote access with `~/.ssh/config` support
- [x] Per-host authentication: key, password, or agent
- [ ] Reverse SSH tunnel support
- [ ] VPN or mesh integrations (e.g., Tailscale, Zerotier)
- [ ] `vwrconf-agent` for gRPC over TLS
- [ ] Read-only vs write-mode enforcement
- [ ] SSH multiplexing (ControlMaster)
- [ ] Role-based access control via config
- [ ] Offline-only mode using local backups

---

## Core Capabilities

- [x] Load host definitions and aliases from YAML or TOML
- [x] Fetch configuration files by domain alias (e.g., `crontab`, `sshd`)
- [x] Create timestamped backups
- [x] Restore from backups (single or bulk)
- [x] View raw and parsed config formats
- [ ] Inline editor with confirmation and deployment support
- [x] Configuration diffing:
  - [x] Live vs backup
  - [x] Host A vs Host B
  - [x] Backup vs backup

---

## Config Intelligence

- [~] Syntax validation per config domain
- [ ] Structured parsing with AST-like models
- [ ] Conflict and duplication detection
- [ ] Job tagging and metadata annotations
- [ ] Time-based job analysis (cron and systemd)
- [ ] Timeline view for scheduled configurations

---

## Filtering and Search

- [ ] Regex and glob-based search
- [ ] Filtering by:
  - [ ] Host or group
  - [ ] Configuration domain
  - [ ] Comments or keywords
  - [ ] Schedule time or job tags

---

## TUI Dashboard

- [~] Two-pane interface:
  - [x] Hosts/configs selector
  - [~] File viewer and diff output
- [~] Keybindings:
  - [x] Navigation between nodes
  - [ ] Toggle between raw and parsed views
  - [ ] Open inline editor
  - [ ] Apply or discard changes
- [ ] Visual indicators:
  - [ ] Synced
  - [ ] Modified
  - [ ] Error or invalid
- [ ] Theming support (light, dark, custom)

---

## Plugin System

- [ ] Base interface: `ConfigPlugin`
- [ ] Built-in plugins:
  - [ ] `CrontabPlugin`
  - [ ] `SSHDConfigPlugin`
  - [ ] `NginxPlugin`
  - [ ] `SystemdTimerPlugin`
  - [ ] `SysctlPlugin`
- [ ] Standard methods for all plugins:
  - `.fetch()`, `.backup()`, `.diff()`, `.push()`
- [ ] Lifecycle hooks (pre/post actions)
- [ ] Config templating and generation

---

## Export and Reporting

- [ ] Export current config state to:
  - [ ] JSON
  - [ ] HTML via templating
- [ ] Git-style diff view export
- [ ] Change logs between backups
- [ ] Integration with Git-based snapshot workflows

---

## Developer Utilities

- [x] Local SSH emulation for dev/test
- [ ] Syntax and schema validator for config formats
- [ ] Unit testing per plugin
- [ ] Fixture-based testing with YAML snapshots
- [ ] Verbose/debug/test flags for CLI

---

## Roadmap by Phase

| Phase                   | Description                                   | Status        |
|------------------------|-----------------------------------------------|---------------|
| Phase 0 – Bootstrap     | Initial scaffolding and layout                | Complete      |
| Phase 1 – SSH Access    | Remote shell-based file retrieval             | Complete      |
| Phase 2 – Backup System | Timestamped backups and restore functionality | Complete      |
| Phase 3 – Diff Engine   | Comparison engine for live and cached states  | Complete      |
| Phase 4 – TUI Interface | Host and domain browsing interface            | In progress   |
| Phase 5 – Edit/Deploy   | Inline editor with diff + push                | In progress   |
| Phase 6 – Analysis      | Conflict detection, tag parsing, validation   | Planned       |
| Phase 7 – Export        | HTML, JSON, and GitOps report generation      | Planned       |
| Phase 8 – Plugin System | Add plugins for more domains and protocols    | Planned       |
| Phase 9 – Protocols     | gRPC agents, VPN support, pub/sub transport   | Planned       |
| Phase 10 – Access Roles | RBAC config and offline cache modes           | Planned       |

---

## Contributing

Contributions are welcome.

New plugin types, protocol backends, and format parsers can be implemented easily using the unified plugin interface. See `docs/PLUGIN_GUIDE.md` and `examples/plugins/` for guidance once available.
