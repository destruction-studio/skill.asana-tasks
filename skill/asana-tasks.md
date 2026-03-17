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

**Step 3g. STOP and ask about CLAUDE.md.** Ask:
> "Want me to add an asana-tasks section to your project's CLAUDE.md? This helps Claude automatically offer to check/close tasks during work."

If yes → append to CLAUDE.md (create if missing):

```markdown
## Tasks

- Task management: Asana — use `/asana-tasks` skill or ask "what to work on?"
- After completing work on a task, offer to mark it done via asana-tasks
- When creating new work items, offer to create an Asana task
```

**Step 3h.** Tell the user: "Setup complete! Commit `.claude-team/` (and CLAUDE.md if updated) to your repo so the team gets the same config."

**Only after all steps above are done, proceed to work mode.**

### 4. Everything configured → work mode

Read `.claude-team/asana.json` for project config.
If `.claude-team/RULES.md` exists, read it and follow the workflow rules defined there.
Rules override the defaults below.

**IMPORTANT: Multi-target check.** Before showing tasks, check TWO conditions:
1. `.claude-team/asana.json` has NO `"targets"` key (legacy single-target)
2. `.claude-team/.multitarget-offered` does NOT exist

If both true → ask:
> "You have a single Asana backend. Want to add another (e.g. Taskana) for dual-write? Say 'skip' to proceed without."

If user wants to add → run the **Add target flow** below.
If user says skip/no → create `.claude-team/.multitarget-offered` (empty file) and proceed to show tasks.
Once the file exists, never ask again.

#### Add target flow

Ask the user for three things in one message:
1. Target name (e.g. "taskana")
2. Base URL (e.g. `https://taskana.example.com/api/1.0`)
3. Token (each backend has its own token — NEVER reuse the Asana token)

Then run one command:
```bash
asana-cli add-target <name> <base_url> --token <token> --project <gid>
```

If user doesn't know the project GID, omit `--project` — the command will list available projects and ask to re-run with `--project`.

After setup, ask: "Want to set the new target as default?" If yes, edit `asana.json` and change `"default"`.

Tell user to commit updated `asana.json`.

## Default workflow

### When developer asks "what to work on?" or similar:

```bash
asana-cli overview              # single call: my tasks + review + todo + in progress + bugs
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
asana-cli assign <id> <user>    Assign task ("me" for self, or name/email)
asana-cli unassign <id>         Remove assignee
asana-cli watch <id> [user]     Add watcher ("me" by default)
asana-cli unwatch <id> [user]   Remove watcher
asana-cli due <id> <date>       Set due date (YYYY-MM-DD or "clear")
asana-cli comment <id> <text>   Add comment to task
asana-cli subtasks <id>         List subtasks
asana-cli subtask <id> <name>   Create subtask
asana-cli tags <id>             List tags on task
asana-cli tag <id> <name>       Add tag (creates if not found)
asana-cli untag <id> <name>     Remove tag
asana-cli deps <id>             List dependencies (blocked by)
asana-cli dep <id> <dep_id>     Add dependency
asana-cli undep <id> <dep_id>   Remove dependency
asana-cli blocks <id>           List dependents (blocking)
asana-cli block <id> <dep_id>   Add dependent
asana-cli unblock <id> <dep_id> Remove dependent
asana-cli rename <id> <name>    Rename task
asana-cli reopen <id>           Reopen completed task
asana-cli description <id> <t>  Update task description
asana-cli history <id>          Show task activity
asana-cli members               List project members
asana-cli overview              Dashboard (my + review + todo + progress, 1 API call)
asana-cli board                 Compact board view
asana-cli users [ws_gid]        List workspace users
asana-cli project-create <name> Create project (--workspace, --team)
asana-cli section-create <name> Create new section
asana-cli section-rename <s> <n> Rename section
asana-cli section-delete <s>    Delete section
asana-cli whoami                Current user info
asana-cli workspaces            List available workspaces
asana-cli projects [ws_gid]     List projects in workspace
```

## Multi-target

Config supports multiple backends (e.g. Asana + Taskana):

```json
{
    "targets": {
        "asana": { "baseUrl": "https://app.asana.com/api/1.0", "projectId": "...", "workspaceId": "..." },
        "taskana": { "baseUrl": "https://taskana.example.com/api/1.0", "projectId": "...", "workspaceId": "..." }
    },
    "default": "asana"
}
```

- Without `--target` → uses `default`
- `--target taskana` → specific target
- `--target all` → executes on all targets (dual write)
- Per-target tokens: `~/.config/asana/tokens/<name>`

Legacy single-target config still works.

## Important

- Always use the CLI tool, not raw curl, for Asana operations.
- The CLI reads `.claude-team/asana.json` from the project and `~/.config/asana/token` for auth.
- Task IDs are Asana GIDs (long numbers).
- `start` auto-assigns the task to the current developer.
- Do NOT create config files for the user during init — use `asana-cli init-write` instead.
