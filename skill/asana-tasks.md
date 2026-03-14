---
name: asana-tasks
description: Manage Asana tasks via CLI. Auto-activates when .claude-team/asana.json exists in the project. Handles onboarding, task listing, assignment, and workflow.
---

# Asana Tasks Skill

## Activation check

Before doing anything, verify the environment:

1. **Project config**: Look for `.claude-team/asana.json` in the current repo (walk up from cwd).
   - If missing → say "This project is not connected to Asana. Add `.claude-team/asana.json` — see examples at [repo URL]." Stop.

2. **Token**: Check if `~/.config/asana/token` exists or `ASANA_TOKEN` env var is set.
   - If missing → run **Onboarding flow** (see below).

3. **CLI**: Check if `asana-cli` is available (`which asana-cli` or `~/.local/bin/asana-cli`).
   - If missing → install from public repo (see Install section).

4. **Version check**: If `~/.config/asana/last-version-check` is older than 24h or missing → check for updates.

## Onboarding flow (no token)

When token is not found:

1. Tell the developer:
   ```
   Asana is not configured yet. Let's set it up — takes 30 seconds.

   1. Go to https://app.asana.com/0/my-apps
   2. Click "Create new token"
   3. Name it anything (e.g. "Claude Code")
   4. Copy the token and paste it here
   ```
2. Wait for the user to paste the token.
3. Save it:
   ```bash
   mkdir -p ~/.config/asana
   echo "TOKEN_VALUE" > ~/.config/asana/token
   chmod 600 ~/.config/asana/token
   ```
4. Verify: run `asana-cli whoami` — confirm name and access.
5. Continue with the original task.

## Project rules

If `.claude-team/RULES.md` exists, read it and follow the workflow rules defined there.
These rules override the defaults below.

## Default workflow

### When developer asks "what to work on?" or similar:

```bash
asana-cli my                    # show tasks assigned to this developer
asana-cli list review           # show tasks awaiting deploy/test
asana-cli list todo             # show tasks ready to start
```

Present the results and ask what to pick.

### When starting a task:

```bash
asana-cli start <id>            # assigns to current user + moves to In Progress
```

### When completing a task:

```bash
asana-cli done <id>             # marks completed + moves to Done
```

### When creating a task:

Use prefixes from `asana.json` config if defined:

```bash
asana-cli create "[Prefix] Task name" --notes "details"
```

## CLI reference

```
asana-cli list [section]        List tasks (filter by section)
asana-cli show <id>             Task details
asana-cli done <id>             Mark completed + move to Done
asana-cli start <id>            Move to In Progress + assign to me
asana-cli move <id> <section>   Move to section
asana-cli create <name> [opts]  Create task (--section, --notes)
asana-cli sections              List sections
asana-cli search <query>        Search by name
asana-cli my                    My assigned tasks
asana-cli whoami                Current user info
```

## Install

If CLI is not installed:

```bash
# Download and install
curl -fsSL https://raw.githubusercontent.com/destruction-studio/skill.asana-tasks/main/install.sh | bash
```

## Important

- Always use the CLI tool, not raw curl, for Asana operations.
- The CLI reads `.claude-team/asana.json` from the project and `~/.config/asana/token` for auth.
- Task IDs are Asana GIDs (long numbers).
- `start` auto-assigns the task to the current developer.
