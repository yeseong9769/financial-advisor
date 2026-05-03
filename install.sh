#!/bin/bash
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

show_help() {
  cat <<'EOF'
Financial Advisor Installer

Install financial-advisor agents and skills for OpenCode.

Usage:
  bash install.sh -g              Global install (~/.config/opencode/)
  bash install.sh -p              Project install (.opencode/ in current dir)
  bash install.sh -d <path>       Install to custom directory
  bash install.sh                  Interactive mode (prompts for choice)

Options:
  -g, --global    Install to ~/.config/opencode/
  -p, --project   Install to .opencode/ in current directory
  -d, --dir       Install to specified project directory (e.g., -d /path/to/project — creates .opencode/ inside)
  -h, --help      Show this help
EOF
  exit 0
}

choose_target() {
  echo "Financial Advisor - OpenCode Installer"
  echo "======================================"
  echo "Select install target:"
  echo "  g) Global  — ~/.config/opencode/ (available in all projects)"
  echo "  p) Project — $(pwd)/.opencode/ (current directory only)"
  echo "  c) Custom  — specify a custom directory"
  echo ""
  read -rp "Choice (g/p/c): " choice
  case "$choice" in
    g|G) MODE="global" ;;
    p|P) MODE="project" ;;
    c|C)
      MODE="custom"
      read -rp "Enter target path: " CUSTOM_DIR
      if [ -z "$CUSTOM_DIR" ]; then
        echo "Path cannot be empty."; exit 1
      fi
      ;;
    *) echo "Invalid choice. Enter g, p, or c."; exit 1 ;;
  esac
}

setup_api_key() {
  if [ -n "${ALPHAVANTAGE_API_KEY:-}" ]; then
    echo "  - ALPHAVANTAGE_API_KEY already set, skipping"
    return
  fi

  echo ""
  echo "Alpha Vantage API key is required for market data."
  echo "  Get a free key: https://www.alphavantage.co/support/#api-key"
  echo ""
  read -rp "Enter your API key (or press Enter to skip): " api_key

  if [ -z "$api_key" ]; then
    echo "  Skipped. Set ALPHAVANTAGE_API_KEY later in your shell rc."
    return
  fi

  # Detect shell rc file
  local rc_file=""
  case "${SHELL:-}" in
    */zsh) rc_file="$HOME/.zshrc" ;;
    */bash) rc_file="$HOME/.bashrc" ;;
  esac

  if [ -n "$rc_file" ]; then
    echo "export ALPHAVANTAGE_API_KEY='$api_key'" >> "$rc_file"
    export ALPHAVANTAGE_API_KEY="$api_key"
    echo "  Saved to $rc_file"
    echo "  Run: source $rc_file"
  else
    echo "  Unknown shell ($SHELL). Add this to your shell rc manually:"
    echo "    export ALPHAVANTAGE_API_KEY='$api_key'"
  fi
}

install_to() {
  local target="$1"
  echo "  Target: $target"

  mkdir -p "$target/agents"
  mkdir -p "$target/skills/financial-analyst/scripts"

  cp "$REPO_DIR/agents/"*.md "$target/agents/"
  cp "$REPO_DIR/skills/financial-analyst/SKILL.md" "$target/skills/financial-analyst/"
  cp "$REPO_DIR/skills/financial-analyst/scripts/"*.py "$target/skills/financial-analyst/scripts/"

  echo "  - agents ($(ls "$target/agents/"*.md 2>/dev/null | wc -l) files)"
  echo "  - skills/financial-analyst ($(ls "$target/skills/financial-analyst/scripts/"*.py 2>/dev/null | wc -l) scripts)"
}

install_python() {
  if [ -f "$REPO_DIR/requirements.txt" ]; then
    echo "  Installing Python packages..."
    pip install -r "$REPO_DIR/requirements.txt" -q
    echo "  - pip install complete"
  fi
}

add_mcp_config() {
  local config_file="$1"
  local config_dir
  config_dir="$(dirname "$config_file")"
  mkdir -p "$config_dir"

  if [ ! -f "$config_file" ]; then
    cp "$REPO_DIR/opencode.json.example" "$config_file"
    echo "  - Created opencode.json (set API key before use)"
    return
  fi

  if python3 -c "
import json, sys
with open('$config_file') as f:
    cfg = json.load(f)
if 'alphavantage' in cfg.get('mcp', {}):
    sys.exit(0)
else:
    sys.exit(1)
" 2>/dev/null; then
    echo "  - opencode.json: Alpha Vantage MCP already configured, skipped"
  else
    python3 -c "
import json
with open('$config_file') as f:
    cfg = json.load(f)
if 'mcp' not in cfg:
    cfg['mcp'] = {}
cfg['mcp']['alphavantage'] = {
    'type': 'remote',
    'url': 'https://mcp.alphavantage.co/mcp?apikey={env:ALPHAVANTAGE_API_KEY}'
}
with open('$config_file', 'w') as f:
    json.dump(cfg, f, indent=2)
print('  - Alpha Vantage MCP config added to opencode.json')
" 2>/dev/null || echo "  Warning: Failed to update opencode.json"
  fi
}

# --- Main ---

case "${1:-}" in
  -g|--global) MODE="global" ;;
  -p|--project) MODE="project" ;;
  -d|--dir)
    MODE="custom"
    CUSTOM_DIR="$2"
    if [ -z "$CUSTOM_DIR" ]; then
      echo "Error: --dir requires a path argument"
      exit 1
    fi
    ;;
  -h|--help) show_help ;;
  "") choose_target ;;
  *) echo "Unknown option: $1"; show_help ;;
esac

echo ""
echo "Installing Financial Advisor..."
echo ""

if [ "$MODE" = "global" ]; then
  TARGET="$HOME/.config/opencode"
  install_to "$TARGET"
  add_mcp_config "$TARGET/opencode.json"
elif [ "$MODE" = "custom" ]; then
  TARGET="$CUSTOM_DIR/.opencode"
  install_to "$TARGET"
  add_mcp_config "$TARGET/opencode.json"
else
  TARGET="$(pwd)/.opencode"
  install_to "$TARGET"
  add_mcp_config "$TARGET/opencode.json"
fi

install_python

echo ""
setup_api_key

echo ""
echo "Done! Use @finance-advisor in OpenCode."
echo '  Example: "@finance-advisor analyze my portfolio"'
echo ""
