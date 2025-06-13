#!/usr/bin/env bash

set -euo pipefail

TOOL_NAME="vwrconf"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
CONFIG_DIR="$HOME/.config/vwrconf"

echo "Uninstall $TOOL_NAME"

select SCOPE in "Local (user only)" "Global (system-wide)" "Cancel"; do
  case $REPLY in
  1)
    INSTALL_PATH="$HOME/.local/bin/$TOOL_NAME"
    break
    ;;
  2)
    INSTALL_PATH="/usr/local/bin/$TOOL_NAME"
    break
    ;;
  3)
    echo "[!] Cancelled."
    exit 0
    ;;
  *)
    echo "[x] Invalid selection. Please enter 1, 2, or 3."
    continue
    ;;
  esac
done

# Remove launcher
if [[ -f "$INSTALL_PATH" ]]; then
  echo "[!] Found launcher at $INSTALL_PATH"
  read -rp "Do you want to remove it? [y/N]: " confirm
  if [[ "$confirm" =~ ^[Yy]$ ]]; then
    if [[ $INSTALL_PATH == "$HOME"* ]]; then
      rm "$INSTALL_PATH"
    else
      sudo rm "$INSTALL_PATH"
    fi
    echo "[✓] Removed tool launcher."
  else
    echo "Skipped removal of $INSTALL_PATH"
  fi
else
  echo "[!] No launcher found at $INSTALL_PATH"
fi

# Remove virtual environment
if [[ -d "$VENV_DIR" ]]; then
  echo "[!] Found virtual environment at $VENV_DIR"
  read -rp "Do you want to delete the virtual environment? [y/N]: " delete_venv
  if [[ "$delete_venv" =~ ^[Yy]$ ]]; then
    rm -rf "$VENV_DIR"
    echo "[✓] Virtual environment deleted."
  else
    echo "Skipped deletion of $VENV_DIR"
  fi
fi

# Remove configuration directory

if [[ -d "$CONFIG_DIR" ]]; then
  read -rp "Do you want to remove your config directory at $CONFIG_DIR? This will delete all configs. [y/N]: " del_cfg
  if [[ "$del_cfg" =~ ^[Yy]$ ]]; then
    rm -rf "$CONFIG_DIR"
    echo "[✓] Config directory deleted."
  else
    echo "Skipped deletion of config directory."
  fi
fi

echo "[✓] Uninstallation complete."
