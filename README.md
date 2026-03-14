# skill.asana-tasks

Universal Asana integration for Claude Code — CLI tool + skill.

## How it works

```
CLI (this repo)                ← Python, universal CRUD for Asana API
Skill (this repo)              ← Claude Code skill, workflow logic
.claude-team/asana.json        ← per-project config (committed to repo)
.claude-team/RULES.md          ← per-project workflow rules (committed to repo)
~/.config/asana/token          ← personal access token (local, per-developer)
```

## Installation

```bash
# Auto-install CLI + skill
curl -fsSL https://raw.githubusercontent.com/destruction-studio/skill.asana-tasks/main/install.sh | bash
```

Or manually:

```bash
git clone https://github.com/destruction-studio/skill.asana-tasks.git
cd skill.asana-tasks
./install.sh
```

This installs:
- `asana-cli` → `~/.local/bin/`
- skill → `~/.claude/skills/asana-tasks/`

## Project setup

Add `.claude-team/asana.json` to your repo:

```json
{
    "projectId": "YOUR_ASANA_PROJECT_GID",
    "workspaceId": "YOUR_ASANA_WORKSPACE_GID"
}
```

Optionally add `.claude-team/RULES.md` with project-specific workflow rules.

See `examples/` for templates.

## Developer onboarding

First time a developer uses the skill, Claude will:

1. Detect missing token
2. Guide through PAT creation at https://app.asana.com/0/my-apps
3. Save token to `~/.config/asana/token`
4. Verify access and continue

## CLI usage (standalone)

```bash
asana-cli list [section]        # list tasks
asana-cli show <id>             # task details
asana-cli done <id>             # mark completed
asana-cli start <id>            # move to In Progress + assign to me
asana-cli create <name> [opts]  # create task
asana-cli sections              # list sections
asana-cli search <query>        # search by name
asana-cli my                    # my assigned tasks
asana-cli update                # update CLI + skill to latest version
```

## Auto-update

The skill checks for updates once per day (timestamp in `~/.config/asana/last-version-check`).
If a new version is available, it pulls CLI + skill from this repo.
