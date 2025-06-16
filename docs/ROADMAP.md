# vwrconf - Short Term Roadmap (Next 7 Days)

This roadmap outlines the priority tasks to focus on during the upcoming week, based on the current development status and planned features in FEATURES.md and TODO.md.

---

## Main Objectives

1. Stabilize and complete the TUI interface for config exploration and basic management  
2. Finalize editing and safe deployment workflows for configuration files  
3. Lay groundwork for basic validation and tagging features  
4. Improve existing plugins and start support for additional config domains  

---

## Detailed Tasks

### 1. TUI Dashboard  
- [ ] Complete and stabilize file viewer panel with integrated diff output  
- [ ] Implement keybindings to toggle between raw and parsed views  
- [ ] Enable basic TUI actions: backup, restore, export (read-only mode)  
- [ ] Improve navigation between hosts and config domains  
- [ ] Add simple visual indicators (synced, modified, error states)  

### 2. Inline Editor & Deployment  
- [ ] Finalize integration of inline or external editor with confirmation step  
- [ ] Add simple pre-push validation (basic length and format checks)  
- [ ] Implement basic rollback mechanism on failed deploy  
- [ ] Add pre-save diff and change summary before applying edits  

### 3. Validation and Tagging (Initial Phase)  
- [ ] Integrate basic syntax validation for crontab files  
- [ ] Support simple job tagging using comments (e.g. `#tags`)  
- [ ] Display basic warnings in the viewer (e.g. malformed cron expressions)  

### 4. Plugins  
- [ ] Improve robustness of `SSHDConfigPlugin` (parsing and diff stability)  
- [ ] Begin development of `NginxPlugin` (basic loading and diff support)  

### 5. CLI and Logging  
- [x] Add `--verbose` flag for detailed CLI debug output  
- [x] Improve error messages and logging for remote operations  
- [x] Update documentation for existing CLI commands and TUI shortcuts  

---

## Expected Deliverables by Next Week

- Functional TUI with navigation and diff visualization  
- Inline editor workflow: edit → validate → deploy → rollback  
- Stable `SSHDConfigPlugin` parsing and diff without critical errors  
- Initial `NginxPlugin` supporting raw load and diff  
- Updated CLI and TUI usage documentation  

---

## Notes

- Focus on stability and usability rather than introducing new complex features  
- Ensure compatibility with existing backup and restore mechanisms  
- Prepare foundation for more advanced semantic analysis in upcoming phases  

---


