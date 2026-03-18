# Changelog

## 1.0.2 (2026-03-18)
- Fix: raise task fetch limit from 100 to 500 (was silently dropping tasks)

## 1.0.1 (2026-03-18)
- Fix: `search` now uses server-side API (`/workspaces/:gid/tasks/search`) instead of client-side filtering
- Searches title + description, no 100-task limit, finds all tasks

## 1.0.0 (2026-03-17)
- **Breaking fix**: per-target token loading in multi-target loop (was using single token for all)
- Fix: per-target token file takes priority over ASANA_TOKEN env var
- Fix: pre-config commands (whoami, projects) resolve base URL from config default
- Fix: `--target all` catches all exceptions, not just SystemExit
- Fix: missing projectId gives clean error instead of KeyError crash
- Fix: `set-target-project`, `dismiss-multitarget` no longer require token
- Fix: `add-target` without `--token` reads per-target token file
- Codex code review: 8 issues found and fixed

## 0.9.6 (2026-03-17)
- Fix: resolve default target name before loading token — prevents 401 when default is non-asana backend

## 0.9.5 (2026-03-17)
- Fix: handle `null` section in task memberships (Taskana returns `section: null` for tasks without section)
- Extract `get_task_section()` helper for safe membership access

## 0.9.4 (2026-03-17)
- Skill: check for existing per-target token before asking user for one

## 0.9.3 (2026-03-17)
- Fix: block `--target all` for ID-dependent commands (IDs differ between backends)
- `--target all` only works for: list, overview, board, create, sections, members, my, search

## 0.9.2 (2026-03-17)
- Skill: simplified add-target flow — ask all 3 params at once, never offer to reuse Asana token

## 0.9.1 (2026-03-17)
- New: `--token` flag for `add-target` — saves per-target token automatically
- Prevents Claude from overwriting default Asana token with Taskana token

## 0.9.0 (2026-03-17)
- `add-target` now fully configures in one call: verifies connection, resolves workspace, validates project
- New: `--project` flag for `add-target` (e.g. `add-target taskana https://... --project 12`)
- New: `set-target-project` command for post-hoc project assignment
- Preserves prefixes, phases when migrating legacy → multi-target

## 0.8.9 (2026-03-17)
- Fix: `init-write` refuses to overwrite multi-target config (prevents data loss)

## 0.8.8 (2026-03-17)
- Hint now includes Taskana URL and token instructions

## 0.8.7 (2026-03-17)
- Fix: reword FOR CLAUDE hint — must ask user, not auto-dismiss

## 0.8.6 (2026-03-17)
- Change: multi-target hint now prefixed "FOR CLAUDE:" with explicit instructions to ask user

## 0.8.5 (2026-03-17)
- New: `add-target` command — add another backend, auto-migrate legacy config
- New: `dismiss-multitarget` — suppress the multi-target hint
- `overview` shows NOTE hint when single-target and not dismissed
- Multi-target hint moved from skill to CLI output (more reliable)

## 0.8.4 (2026-03-17)
- Fix: multi-target graceful error handling — skip target on API error instead of crashing

## 0.8.3 (2026-03-17)
- Skill: use `.claude-team/.multitarget-offered` flag file — ask once, never again

## 0.8.2 (2026-03-17)
- Skill: move multi-target check into work mode (was being skipped in activation flow)

## 0.8.1 (2026-03-17)
- Skill: add target flow — offers to add Taskana when single-target config detected
- Fix: `--target` now works for `whoami`, `workspaces`, `projects` (resolves base URL early)
- Fix: global declaration order for ACTIVE_BASE_URL

## 0.8.0 (2026-03-17)
- New: multi-target support (`--target <name>`, `--target all`)
- Config supports `targets` map with `default` key
- Per-target tokens in `~/.config/asana/tokens/<name>`
- Backward compatible with legacy single-target config
- Enables dual write to Asana + Taskana simultaneously

## 0.7.0 (2026-03-17)
- New: `deps` — list dependencies (blocked by)
- New: `dep` / `undep` — add/remove dependency
- New: `blocks` — list dependents (blocking)
- New: `block` / `unblock` — add/remove dependent
- `show` now displays dependencies and dependents

## 0.6.8 (2026-03-16)
- New: `rename` command — rename a task

## 0.6.7 (2026-03-16)
- New: `--pin` flag for `comment` command (sets `is_pinned` on the comment)

## 0.6.6 (2026-03-16)
- Fix: `#` → `<h1>`, `##` → `<h2>` in markdown conversion (was all `<strong>`)
- Fix: `**bold**` now works inside list items

## 0.6.5 (2026-03-16)
- Fix: remove extra newlines between sections in markdown→HTML output

## 0.6.4 (2026-03-16)
- Restore markdown→Asana HTML conversion for `comment` and `description`
- Use `\n` for line breaks instead of `<br>` (Asana doesn't support `<br>`)

## 0.6.3 (2026-03-16)
- Revert html_text — plain text fallback while investigating Asana rich text issues

## 0.6.2 (2026-03-16)
- Auto-convert markdown to Asana rich text HTML in `comment` and `description`

## 0.6.1 (2026-03-16)
- `overview` now shows section name for "My Tasks"

## 0.6.0 (2026-03-16)
- New: `overview` command — single API call dashboard (my + review + todo + in progress + bugs)
- Skill updated to use `overview` instead of 4 separate calls

## 0.5.6 (2026-03-16)
- Fix: `my` command — filter by assignee client-side instead of broken `/tasks?assignee=` API query

## 0.5.4 (2026-03-16)
- New: `--assign` and `--watch` flags for `create` command

## 0.5.3 (2026-03-16)
- New: `users` command — list workspace users

## 0.5.2 (2026-03-16)
- Fix: `project-create` — auto-detect organization, resolve team

## 0.5.1 (2026-03-16)
- New: `project-create` command

## 0.5.0 (2026-03-16)
- New: `section-create`, `section-rename`, `section-delete` commands

## 0.4.0 (2026-03-16)
- New: `members`, `due`, `comment`, `subtasks`, `subtask`, `tags`, `tag`, `untag`, `reopen`, `description`, `history`, `board` commands
- Refactor: extract `resolve_user()` helper, remove duplication

## 0.3.3 (2026-03-16)
- `--version` now checks for updates via GitHub API

## 0.3.2 (2026-03-16)
- Use GitHub API instead of raw CDN for update checks (no cache delay)

## 0.3.0 (2026-03-16)
- New: `watch`, `unwatch` commands (task followers)

## 0.2.0 (2026-03-16)
- New: `update` command — self-update CLI + skill from GitHub
- New: `assign` command

## 0.1.0 (2026-03-16)
- Initial release
- Commands: `list`, `show`, `done`, `start`, `move`, `create`, `sections`, `search`, `my`, `whoami`
- Self-bootstrapping skill: auth → init → prefixes → phases → rules → CLAUDE.md
- Project config via `.claude-team/asana.json`
- Personal token in `~/.config/asana/token`
- `install.sh` for one-line setup
