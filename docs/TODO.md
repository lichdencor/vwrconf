# vwrconf Development Roadmap (Protocol-Aware & Plugin-Oriented)

vwrconf – A remote configuration manager for sysadmins and automation over SSH and beyond.

---

## Phase 0 – Project Scaffolding [✓]

Focus: Base setup

- [✓] Project initialized with `vwrconf/` package
- [✓] Git, README, LICENSE, CONTRIBUTING set
- [✓] Python virtualenv and `requirements.txt`
- [✓] Basic YAML config loader (hosts, aliases)
- [✓] CLI entrypoint and argument parser defined

---

## Phase 1 – SSH Operations Core [✓]

Focus: Connect via SSH to view remote files

- [✓] Host resolution and credential lookup (from config or `~/.ssh/config`)
- [✓/?] Execute remote shell commands (e.g., `crontab -l`, `cat /etc/sshd_config`)
- [✓/?] List available domains per host (crontab, sshd, etc.)
- [✓] Read-only support for remote fetching
- [✓] Store content snapshots locally

---

## Phase 2 – Backup & Restore [✓]

Focus: Remote file archiving

- [✓] Timestamped backup directory structure (`~/.vwrconf/backups/<host>/<alias>/`)
- [✓] Restore remote config via safe overwrite (`scp`, `echo`, `crontab`)
- [✓/?] Local cache view in TUI and CLI

---

## Phase 3 – Structured Diff Engine [✓]

Focus: Config analysis

- [✓] `ConfigFile` base class with `.raw`, `.parsed`, `.diff()` methods
- [✓] Crontab parser with job object model
- [✓] Line-by-line diff and semantic diff (where applicable)
- [✓] Support for live vs backup, host vs host, backup vs backup

---

## Phase 4 – Interactive TUI Browser [~]

Focus: Terminal UI

- [~] Textual-based interface for config viewing
- [~] Host selector panel
- [~] Config domain selector (e.g., cron, sshd, nginx)
- [~] Viewer pane with diff, syntax status
- [~] Actions: backup, restore, export, edit (WIP)

---

## Phase 5 – Editing & Deployment [~]

Focus: Change management

- [~] In-place or external editor integration
- [~] Validate and review edits pre-push
- [~] Push via SSH with rollback support
- [~] Optional pre-save diff and audit notes

---

## Phase 6 – Tagging, Search, Syntax Check [Planned]

Focus: Quality-of-life enhancements

- [?] Tag configs (e.g., `#monitoring`, `#critical`)
- [?] Search by command, time, pattern
- [?] Validate syntax (cron expression, nginx block, etc.)
- [?] Show warnings on scan

---

## Phase 7 – Export, Audit & Reports [Planned]

Focus: Offline or external consumption

- [?] Export JSON or HTML reports per host/domain
- [?] Print semantic diffs to disk or stdout
- [?] Git integration (commit snapshots, diffs)
- [?] Embed metadata (host, timestamp, editor, source)

---

## Phase 8 – Plugin System for Config Domains [Planned]

Focus: Extensibility

- [?] `ConfigType` plugin interface (for cron, systemd, nginx, etc.)
- [?] Auto-discovery via entrypoints or config
- [?] Domain capabilities: parse, diff, validate, render, edit
- [?] Official plugins: `cron`, `systemd`, `nginx`, `sshd`
- [?] Community plugin support (`docs/PLUGIN_GUIDE.md`)

---

## Phase 9 – Protocol Expansion Layer [Planned]

Focus: Beyond SSH

- [✓] SSH (current)
- [?] Reverse SSH tunnels
- [?] VPN mesh (Tailscale, Zerotier)
- [?] gRPC/TLS agent protocol (`vwrconf-agent`)
- [?] Central GitOps pull-based model
- [?] Pub/Sub via MQTT or WebSocket
- [?] Unified transport API: `.fetch()`, `.push()`, `.diff()`

---

## Phase 10 – RBAC, Offline Cache, Access Control [Planned]

Focus: Enterprise environments

- [?] Role-based UI (admin, operator, viewer)
- [?] Config-level lock/write permissions
- [?] Local-only mode with editable cache
- [?] Audit trails (timestamp, author, origin)

---

## Summary Timeline

| Phase                   | Status     | Notes                                      |
|------------------------|------------|--------------------------------------------|
| Phase 0 – Bootstrap     | [✓] Done   | Setup and scaffolding                      |
| Phase 1 – SSH Access    | [✓] Done   | Connect and fetch configs                  |
| Phase 2 – Backup/Restore| [✓] Done   | Store and push configs                     |
| Phase 3 – Diff Engine   | [✓] Done   | Raw and parsed diff support                |
| Phase 4 – TUI Browser   | [~] WIP    | Interactive visual exploration             |
| Phase 5 – Edit/Deploy   | [~] WIP    | Edit files safely and deploy via SSH       |
| Phase 6 – Tag/Search    | [?] Planned| Tagging, filtering, and syntax warnings    |
| Phase 7 – Export        | [?] Planned| Export formats, Git integration            |
| Phase 8 – Plugins       | [?] Planned| Add domains: systemd, nginx, etc.          |
| Phase 9 – Protocols     | [?] Planned| Reverse SSH, VPNs, agent API, MQTT         |
| Phase 10 – RBAC & ACL   | [?] Planned| User roles, local-only mode, access logs   |
