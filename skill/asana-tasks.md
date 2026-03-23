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

First, check if a per-target token already exists: `~/.config/asana/tokens/<name>`.

Ask the user for:
1. Target name (e.g. "taskana")
2. Base URL (e.g. `https://taskana.example.com/api/1.0`)
3. Token — **only if** `~/.config/asana/tokens/<name>` does NOT exist. Each backend has its own token — NEVER reuse the Asana token.

Then run one command (include `--token` only if user provided a new token):
```bash
asana-cli add-target <name> <base_url> --token <token>
# or without --token if token file already exists:
asana-cli add-target <name> <base_url>
```

If user doesn't know the project GID, omit `--project` — the command will list available projects and ask to re-run with `--project`.

After setup, ask: "Want to set the new target as default?" If yes, edit `asana.json` and change `"default"`.

Tell user to commit updated `asana.json`.

## Default workflow

### When developer asks "what to work on?" or similar:

If `.claude-team/asana.json` has `"targets"` key (multi-target config):
```bash
asana-cli overview --target all
```

Otherwise (single target):
```bash
asana-cli overview
```

Present the results and ask what to pick.

### When starting a task:

```bash
asana-cli start <id>            # assigns to current user + moves to In Progress
```

After starting, offer to set a time estimate:
> "How long do you estimate this task will take? (e.g. 2, 0.5, 4)"

If the developer gives an estimate:
```bash
asana-cli estimate <id> <hours>
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
Setup:
  asana-cli auth <token> [--target <name>]   Save token (per-target with --target)
  asana-cli init                             List workspaces & projects
  asana-cli init-write <ws_gid> <proj_gid>   Write .claude-team/asana.json
  asana-cli status                           Check configuration
  asana-cli update                           Update CLI + skill
  asana-cli whoami                           Current user info
  asana-cli workspaces                       List workspaces
  asana-cli projects [ws_gid]                List projects
  asana-cli users [ws_gid]                   List workspace users

Tasks:
  asana-cli list [section]                   List tasks (filter by section)
  asana-cli show <id>                        Task details
  asana-cli my                               My assigned tasks
  asana-cli search <query>                   Search by name
  asana-cli overview                         Dashboard: my + todo + review + progress
  asana-cli board                            Board view (by section)
  asana-cli create <name> [options]          Create task
      --section <name>                         Section (default: Backlog)
      --notes <text>                           Description
      --due <YYYY-MM-DD>                       Due date
      --assign <user>                          Assign ("me", name, email)
      --watch <user>                           Add watcher (repeatable)
  asana-cli done <id>                        Complete + move to Done
  asana-cli start <id>                       Assign to me + In Progress
  asana-cli move <id> <section>              Move to section
  asana-cli assign <id> <user>               Assign ("me", name, email)
  asana-cli unassign <id>                    Remove assignee
  asana-cli due <id> <date>                  Set due date (YYYY-MM-DD / "clear")
  asana-cli rename <id> <name>               Rename task
  asana-cli reopen <id>                      Reopen completed task
  asana-cli description <id> <text>          Update description (markdown → rich text)
  asana-cli comment <id> <text> [--pin]      Add comment (--pin to pin)
  asana-cli history <id>                     Task activity log

Subtasks:
  asana-cli subtasks <id>                    List subtasks
  asana-cli subtask <id> <name>              Create subtask

Watchers:
  asana-cli watch <id> [user]                Add watcher ("me" default)
  asana-cli unwatch <id> [user]              Remove watcher

Tags:
  asana-cli tags <id>                        List tags
  asana-cli tag <id> <name>                  Add tag (creates if needed)
  asana-cli untag <id> <name>                Remove tag

Dependencies:
  asana-cli deps <id>                        Blocked by (dependencies)
  asana-cli dep <id> <dep_id>                Add dependency
  asana-cli undep <id> <dep_id>              Remove dependency
  asana-cli blocks <id>                      Blocking (dependents)
  asana-cli block <id> <dep_id>              Add dependent
  asana-cli unblock <id> <dep_id>            Remove dependent

Custom fields:
  asana-cli custom-fields                    List project fields
  asana-cli custom-field-create <name> <type>  Create (text/number/enum/date)
  asana-cli task-fields <id>                 Field values on task
  asana-cli task-field-set <id> <fld> <val>  Set field value
  asana-cli estimate <id> <hours>            Set estimate (auto-creates field)

Sections:
  asana-cli sections                         List sections
  asana-cli section-create <name>            Create section
  asana-cli section-rename <old> <new>       Rename section
  asana-cli section-delete <name>            Delete section

Project:
  asana-cli members                          List members
  asana-cli project-create <name> [--workspace <gid>] [--team <gid>]

Multi-target:
  asana-cli add-target <name> <url> [--project <gid>] [--token <tok>]
  asana-cli set-target-project <target> <gid>
  asana-cli dismiss-multitarget              Suppress multi-target prompt

Global flags:
  --target <name>    Use specific backend
  --target all       Execute on all backends (dual write)
  --project <gid>    Override projectId (work with different project)
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
- `--project <gid>` → override projectId (work with a different project)
- Per-target tokens: `~/.config/asana/tokens/<name>`

Legacy single-target config still works.

## Important

- Always use the CLI tool, not raw curl, for Asana operations.
- The CLI reads `.claude-team/asana.json` from the project and `~/.config/asana/token` for auth.
- Task IDs are Asana GIDs (long numbers).
- `start` auto-assigns the task to the current developer.
- Do NOT create config files for the user during init — use `asana-cli init-write` instead.
