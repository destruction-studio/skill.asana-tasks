#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://raw.githubusercontent.com/destruction-studio/skill.asana-tasks/main"
CLI_DEST="$HOME/.local/bin/asana-cli"
SKILL_DEST="$HOME/.claude/skills/asana-tasks"

# Fetch version
VERSION=$(curl -fsSL "$REPO_URL/VERSION")
echo "Installing skill.asana-tasks v${VERSION}..."
echo ""

# Install CLI
mkdir -p "$(dirname "$CLI_DEST")"
curl -fsSL "$REPO_URL/cli/asana_cli.py" -o "$CLI_DEST"
chmod +x "$CLI_DEST"
echo "  CLI installed: $CLI_DEST"

# Install skill as SKILL.md (Claude Code convention)
mkdir -p "$SKILL_DEST"
curl -fsSL "$REPO_URL/skill/asana-tasks.md" -o "$SKILL_DEST/SKILL.md"
echo "  Skill installed: $SKILL_DEST/SKILL.md"

# Check PATH
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo ""
    echo "  WARNING: ~/.local/bin is not in your PATH."
    echo "  Add to your shell profile (~/.zshrc or ~/.bashrc):"
    echo ""
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "  Then restart your terminal or run: source ~/.zshrc"
fi

# Save version check timestamp
mkdir -p "$HOME/.config/asana"
date +%s > "$HOME/.config/asana/last-version-check"

echo ""
echo "Done! Next steps:"
echo "  1. Restart Claude Code (so the skill is picked up)"
echo "  2. Say 'что по задачам?' or '/asana-tasks' — the skill will guide you through setup"
