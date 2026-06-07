#!/bin/bash
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

show_help() {
  cat <<'EOF'
Financial Advisor Installer

Install financial-advisor agent and skills for OpenCode.

Usage:
  bash install.sh -g              Global install (~/.config/opencode/)
  bash install.sh -p              Project install (.opencode/ in current dir)
  bash install.sh -d <path>       Install to custom directory
  bash install.sh --verify        Verify existing installation
  bash install.sh                  Interactive mode (prompts for choice)

Options:
  -g, --global    Install to ~/.config/opencode/
  -p, --project   Install to .opencode/ in current directory
  -d, --dir       Install to specified project directory (e.g., -d /path/to/project — creates .opencode/ inside)
  --verify        Check that all required files exist in the target directory
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

install_to() {
  local target="$1"
  local manifest_dir="$target/.financial-advisor"
  local manifest="$manifest_dir/manifest"
  echo "  Target: $target"

  # Cleanup previous installation from manifest
  if [ -f "$manifest" ]; then
    echo "  Cleaning up previous installation..."
    while IFS= read -r installed_file; do
      rm -f "$installed_file"
    done < "$manifest"
  fi

  mkdir -p "$target/agents"
  mkdir -p "$target/skills/financial-analyst/scripts"
  mkdir -p "$target/skills/pdf-report/scripts"
  mkdir -p "$manifest_dir"

  : > "$manifest"

  # Install agents
  local src fname dest
  for src in "$REPO_DIR/agents/"*.md; do
    [ -f "$src" ] || continue
    fname=$(basename "$src")
    dest="$target/agents/$fname"
    cp "$src" "$dest"
    echo "$dest" >> "$manifest"
  done

  # Install skills (SKILL.md only)
  for dest_dir in skills/financial-analyst skills/pdf-report; do
    src="$REPO_DIR/$dest_dir/SKILL.md"
    if [ -f "$src" ]; then
      dest="$target/$dest_dir/SKILL.md"
      cp "$src" "$dest"
      echo "$dest" >> "$manifest"
    fi
  done

  # Install scripts
  for dest_dir in skills/financial-analyst/scripts skills/pdf-report/scripts; do
    for src in "$REPO_DIR/$dest_dir/"*.py; do
      [ -f "$src" ] || continue
      fname=$(basename "$src")
      dest="$target/$dest_dir/$fname"
      cp "$src" "$dest"
      echo "$dest" >> "$manifest"
    done
  done

  echo "  - agents ($(ls "$target/agents/"*.md 2>/dev/null | wc -l) files)"
  echo "  - skills/financial-analyst ($(ls "$target/skills/financial-analyst/scripts/"*.py 2>/dev/null | wc -l) scripts)"
  echo "  - skills/pdf-report ($(ls "$target/skills/pdf-report/scripts/"*.py 2>/dev/null | wc -l) scripts)"
}

install_python() {
  if [ -f "$REPO_DIR/requirements.txt" ]; then
    echo "  Installing Python packages..."
    pip install -r "$REPO_DIR/requirements.txt" -q
    echo "  - pip install complete"
  fi
}

verify_installation() {
  local target="$1"
  local errors=0

  echo ""
  echo "Verifying installation at: $target"
  echo "======================================"

  if [ -f "$target/agents/finance-advisor.md" ]; then
    echo "  ✅ agents/finance-advisor.md"
  else
    echo "  ❌ agents/finance-advisor.md — MISSING"
    errors=$((errors + 1))
  fi

  if [ -f "$target/skills/financial-analyst/SKILL.md" ]; then
    echo "  ✅ skills/financial-analyst/SKILL.md"
  else
    echo "  ❌ skills/financial-analyst/SKILL.md — MISSING"
    errors=$((errors + 1))
  fi

  for script in market_data_fetcher.py dcf_valuation.py ratio_calculator.py; do
    if [ -f "$target/skills/financial-analyst/scripts/$script" ]; then
      echo "  ✅ skills/financial-analyst/scripts/$script"
    else
      echo "  ❌ skills/financial-analyst/scripts/$script — MISSING"
      errors=$((errors + 1))
    fi
  done

  if [ -f "$target/skills/pdf-report/SKILL.md" ]; then
    echo "  ✅ skills/pdf-report/SKILL.md"
  else
    echo "  ❌ skills/pdf-report/SKILL.md — MISSING"
    errors=$((errors + 1))
  fi

  if [ -f "$target/skills/pdf-report/scripts/html_to_pdf.py" ]; then
    echo "  ✅ skills/pdf-report/scripts/html_to_pdf.py"
  else
    echo "  ❌ skills/pdf-report/scripts/html_to_pdf.py — MISSING"
    errors=$((errors + 1))
  fi

  echo ""
  if [ "$errors" -eq 0 ]; then
    echo "✅ All files present."
  else
    echo "❌ $errors file(s) missing."
    exit 1
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
  --verify)
    if [ -n "$2" ]; then
      verify_installation "$2"
    elif [ -d "$HOME/.config/opencode" ]; then
      verify_installation "$HOME/.config/opencode"
    elif [ -d "$(pwd)/.opencode" ]; then
      verify_installation "$(pwd)/.opencode"
    else
      echo "No installation found. Specify path: bash install.sh --verify <path>"
      exit 1
    fi
    exit 0
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
elif [ "$MODE" = "custom" ]; then
  TARGET="$CUSTOM_DIR/.opencode"
  install_to "$TARGET"
else
  TARGET="$(pwd)/.opencode"
  install_to "$TARGET"
fi

install_python

echo ""
echo "Done! Use @finance-advisor in OpenCode."
echo '  Example: "@finance-advisor analyze my portfolio"'
echo "  Verify: bash install.sh --verify"
echo ""
