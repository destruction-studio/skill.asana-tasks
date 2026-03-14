---
name: asana-tasks
description: Use when the user asks to check tasks, pick a task, mark tasks done, manage the task board, or asks "what should we work on?" / "что по задачам?" at the start of a session. Also handles Asana onboarding, project init, and task assignment.
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

If `.claude-team/asana.json` does not exist → **Init flow**.

**IMPORTANT: You MUST complete ALL steps below before moving to work mode. Do NOT skip ahead to listing tasks.**

**Step 3a.** Run `asana-cli init` — lists available workspaces and projects.

**Step 3b.** Present projects as a numbered list. Ask the user to pick a project by number.

**Step 3c.** Run `asana-cli init-write <workspace_gid> <project_gid>` — creates `.claude-team/asana.json`.

**Step 3d. STOP and ask about prefixes.** Ask:
> "Do you want to configure task prefixes? These are tags like `[AN]`, `[iOS]`, `[Backend]` used in task names. List the ones you want, or skip."

If yes → read `.claude-team/asana.json`, add `"prefixes": [...]`, write it back.

**Step 3e. STOP and ask about phase tags.** Ask:
> "Do you want to configure phase tags? These group tasks by roadmap phase (e.g. `P0: Deploy`, `P1: MVP`). List the ones you want, or skip."

If yes → read `.claude-team/asana.json`, add `"phases": [...]`, write it back.

**Step 3f. STOP and ask about workflow rules.** Ask:
> "Do you want to create workflow rules (.claude-team/RULES.md)? This defines how tasks are prioritized, what to show when you ask 'what to work on?', naming conventions, etc. I can generate a template — want to configure it?"

If yes → ask about their preferences (priority order, limits, naming) and generate `.claude-team/RULES.md`.

**Step 3g.** Tell the user: "Setup complete! Commit `.claude-team/` to your repo so the team gets the same config."

**Only after all steps above are done, proceed to work mode.**

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
