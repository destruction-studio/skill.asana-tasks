#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://raw.githubusercontent.com/destruction-studio/skill.asana-tasks/main"
CLI_DEST="$HOME/.local/bin/asana-cli"
SKILL_DEST="$HOME/.claude/skills/asana-tasks"

echo "Installing skill.asana-tasks..."

# Install CLI
mkdir -p "$(dirname "$CLI_DEST")"
curl -fsSL "$REPO_URL/cli/asana_cli.py" -o "$CLI_DEST"
chmod +x "$CLI_DEST"
echo "  CLI installed: $CLI_DEST"

# Install skill
mkdir -p "$SKILL_DEST"
curl -fsSL "$REPO_URL/skill/asana-tasks.md" -o "$SKILL_DEST/asana-tasks.md"
echo "  Skill installed: $SKILL_DEST/asana-tasks.md"

# Check PATH
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo ""
    echo "  NOTE: ~/.local/bin is not in your PATH."
    echo "  Add to your shell profile:"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# Save version check timestamp
mkdir -p "$HOME/.config/asana"
date +%s > "$HOME/.config/asana/last-version-check"

echo ""
echo "Done! Run 'asana-cli help' to get started."
