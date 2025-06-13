#!/usr/bin/env bash

# vwrconf installer
set -euo pipefail

trap 'echo "[!] Error on line $LINENO. Exiting."; exit 1' ERR

CLI_NAME="vwrconf"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQUIREMENTS="$PROJECT_DIR/requirements.txt"
VENV_DIR="$PROJECT_DIR/.venv"
DEFAULT_CONFIG_DIR="$HOME/.config/vwrconf"
DEFAULT_CONFIG_FILE="vwrconf.yml"
EXAMPLE_CONFIG_SOURCE="$PROJECT_DIR/example.yml"

echo "[0] Starting $CLI_NAME CLI installation..."
echo "Project directory: $PROJECT_DIR"
echo "Requirements file: $REQUIREMENTS"

# Prompt for local or global install
echo "Install $CLI_NAME as a TUI/CLI tool:"
select SCOPE in "Local (user only)" "Global (system-wide)"; do
  case $REPLY in
  1)
    INSTALL_PATH="$HOME/.local/bin/$CLI_NAME"
    echo "1) Installing locally at: $INSTALL_PATH"
    break
    ;;
  2)
    INSTALL_PATH="/usr/local/bin/$CLI_NAME"
    echo "2) Installing globally at: $INSTALL_PATH"
    break
    ;;
  *)
    echo "[!] Invalid selection. Please enter 1 or 2."
    ;;
  esac
done

# Create virtual environment if needed
if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  echo "[1] Creating virtual environment at $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
else
  echo "[1] Virtual environment already exists: $VENV_DIR"
fi

VENV_PYTHON="$VENV_DIR/bin/python"
echo "Using Python binary: $VENV_PYTHON"
"$VENV_PYTHON" --version

# Install dependencies
echo "[2] Installing dependencies..."
"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -r "$REQUIREMENTS"

# Install package in editable mode
echo "[3] Installing package in editable mode..."
"$VENV_PYTHON" -m pip install -e "$PROJECT_DIR"
echo "Package installed."

# Create CLI launcher
echo "[4] Creating CLI launcher at $INSTALL_PATH..."
WRAPPER="#!/usr/bin/env bash
exec \"$VENV_PYTHON\" -m vwrconf \"\$@\"
"

if [[ $INSTALL_PATH == "$HOME"* ]]; then
  mkdir -p "$(dirname "$INSTALL_PATH")"
  echo "$WRAPPER" >"$INSTALL_PATH"
  chmod +x "$INSTALL_PATH"
else
  echo "$WRAPPER" | sudo tee "$INSTALL_PATH" >/dev/null
  sudo chmod +x "$INSTALL_PATH"
fi

echo "[5] Installed tool launcher."

# Prompt to copy example config with custom name
echo
echo "Do you want to copy the example config to your config directory?"
read -rp "Enter config filename (default: $DEFAULT_CONFIG_FILE): " USER_CONFIG_FILE
USER_CONFIG_FILE=${USER_CONFIG_FILE:-$DEFAULT_CONFIG_FILE}

mkdir -p "$DEFAULT_CONFIG_DIR"
if [[ -f "$DEFAULT_CONFIG_DIR/$USER_CONFIG_FILE" ]]; then
  echo "[!] Config file $USER_CONFIG_FILE already exists at $DEFAULT_CONFIG_DIR, skipping copy."
else
  cp "$EXAMPLE_CONFIG_SOURCE" "$DEFAULT_CONFIG_DIR/$USER_CONFIG_FILE"
  echo "[6] Example config copied to $DEFAULT_CONFIG_DIR/$USER_CONFIG_FILE"
fi

# PATH notice
if [[ "$INSTALL_PATH" == "$HOME"* && ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
  echo "    [!] You may want to add ~/.local/bin to your PATH:"
  echo '    echo "export PATH=$HOME/.local/bin:$PATH" >> ~/.bashrc'
  echo '    source ~/.bashrc'
fi

echo "-> Installation complete!"
echo "-> Run the CLI using:"
echo "   $CLI_NAME -h"
echo
echo "-> Default config path:"
echo "   $DEFAULT_CONFIG_DIR/$USER_CONFIG_FILE"
echo "-> To use a custom config file path, run:"
echo "   $CLI_NAME config -c /path/to/config.yml"
