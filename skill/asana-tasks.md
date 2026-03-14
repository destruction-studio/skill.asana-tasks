---
name: asana-tasks
description: Manage Asana tasks via CLI. Auto-activates when .claude-team/asana.json exists in the project. Handles onboarding, task listing, assignment, and workflow.
user-invocable: true
---

# Asana Tasks Skill

## Activation — check environment in order

Run `asana-cli status` to check everything at once. Then follow the appropriate flow:

### 1. CLI missing?

If `asana-cli` is not found (`~/.local/bin/asana-cli`):

```bash
curl -fsSL https://raw.githubusercontent.com/destruction-studio/skill.asana-tasks/main/install.sh | bash
```

Tell the user to run this command. Do NOT run it yourself — let the user do it.

### 2. Token missing?

If `~/.config/asana/token` does not exist and `ASANA_TOKEN` is not set → **Auth flow**:

1. Tell the developer:
   ```
   Asana token not found. Let's set it up — takes 30 seconds.

   1. Go to https://app.asana.com/0/my-apps
   2. Click "Create new token"
   3. Name it anything (e.g. "Claude Code")
   4. Copy the token and paste it here
   ```
2. Wait for the user to paste the token.
3. Run `asana-cli auth <token>` — this saves and verifies the token.
4. Continue.

### 3. Project not initialized?

If `.claude-team/asana.json` does not exist → **Init flow**:

1. Run `asana-cli init` — this lists available workspaces and projects.
2. The output includes a JSON list of projects. Present them to the user as a numbered list.
3. Ask the user to pick a project by number.
4. Run `asana-cli init-write <workspace_gid> <project_gid>` — creates `.claude-team/asana.json`.
5. Ask the user if they want to configure prefixes (e.g. `[AN]`, `[iOS]`, `[Backend]`).
   - If yes → read the created `asana.json`, add `"prefixes": [...]`, write it back.
6. Ask the user if they want to configure phase tags.
   - If yes → add `"phases": [...]` to `asana.json`.
7. Ask if they want to create `.claude-team/RULES.md` with workflow rules.
   - If yes → ask about their workflow preferences and generate the file.
8. Tell the user to commit `.claude-team/` to their repo.

### 4. Everything configured → work mode

Read `.claude-team/asana.json` for project config.
If `.claude-team/RULES.md` exists, read it and follow the workflow rules defined there.
Rules override the defaults below.

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
asana-cli auth <token>          Save and verify personal access token
asana-cli init                  List workspaces & projects for init
asana-cli init-write <ws> <p>   Write .claude-team/asana.json
asana-cli status                Check configuration status
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
asana-cli workspaces            List available workspaces
asana-cli projects [ws_gid]     List projects in workspace
```

## Important

- Always use the CLI tool, not raw curl, for Asana operations.
- The CLI reads `.claude-team/asana.json` from the project and `~/.config/asana/token` for auth.
- Task IDs are Asana GIDs (long numbers).
- `start` auto-assigns the task to the current developer.
- Do NOT create config files for the user during init — use `asana-cli init-write` instead.
