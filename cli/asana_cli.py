#!/usr/bin/env python3
"""
asana-cli — Universal Asana CLI for Claude Code skill.

Reads config from:
  1. .claude-team/asana.json  (project binding — projectId, workspaceId)
  2. ~/.config/asana/token    (personal access token)
  3. ASANA_TOKEN env var       (fallback)

Usage:
  asana-cli list [section]        List tasks (filter by section)
  asana-cli show <id>             Task details
  asana-cli done <id>             Mark completed + move to Done
  asana-cli start <id>            Move to In Progress + assign to me
  asana-cli move <id> <section>   Move to section
  asana-cli create <name> [opts]  Create task
  asana-cli sections              List sections
  asana-cli search <query>        Search by name
  asana-cli my                    My assigned tasks
  asana-cli whoami                Show current user
  asana-cli update                Update CLI + skill
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

VERSION = "0.1.0"
BASE_URL = "https://app.asana.com/api/1.0"


def find_project_root():
    """Walk up from cwd to find .claude-team/asana.json."""
    path = Path.cwd()
    while path != path.parent:
        config = path / ".claude-team" / "asana.json"
        if config.exists():
            return path, config
        path = path.parent
    return None, None


def load_config():
    """Load project config from .claude-team/asana.json."""
    _, config_path = find_project_root()
    if not config_path:
        print("No .claude-team/asana.json found in current or parent directories.")
        print("See: https://github.com/destruction-studio/skill.asana-tasks#project-setup")
        sys.exit(1)

    with open(config_path) as f:
        return json.load(f)


def load_token():
    """Load token from ~/.config/asana/token or ASANA_TOKEN env var."""
    # Env var takes priority
    token = os.environ.get("ASANA_TOKEN")
    if token:
        return token.strip()

    # File
    token_path = Path.home() / ".config" / "asana" / "token"
    if token_path.exists():
        return token_path.read_text().strip()

    return None


def api(method, path, token, body=None):
    """Make Asana API request."""
    url = f"{BASE_URL}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            return result.get("data")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            errors = json.loads(error_body).get("errors", [])
            msg = errors[0]["message"] if errors else error_body
        except (json.JSONDecodeError, IndexError, KeyError):
            msg = error_body
        print(f"API Error ({e.code}): {msg}", file=sys.stderr)
        sys.exit(1)


def get_sections(token, project_id):
    """Get project sections."""
    return api("GET", f"/projects/{project_id}/sections?opt_fields=name", token)


def find_section(token, project_id, name):
    """Find section by name (fuzzy match)."""
    sections = get_sections(token, project_id)
    lower = name.lower().replace(" ", "")
    for s in sections:
        if lower in s["name"].lower().replace(" ", ""):
            return s
    names = ", ".join(s["name"] for s in sections)
    print(f'Section "{name}" not found. Available: {names}', file=sys.stderr)
    sys.exit(1)


def get_me(token):
    """Get current user."""
    return api("GET", "/users/me?opt_fields=name,email,gid", token)


# --- Commands ---

def cmd_list(token, config, section_filter=None):
    project_id = config["projectId"]
    fields = "name,completed,assignee.name,memberships.section.name,tags.name"
    tasks = api("GET", f"/projects/{project_id}/tasks?opt_fields={fields}&limit=100", token)

    if section_filter:
        section = find_section(token, project_id, section_filter)
        tasks = [t for t in tasks
                 if any(m.get("section", {}).get("gid") == section["gid"]
                        for m in t.get("memberships", []))]

    # Group by section
    grouped = {}
    for t in tasks:
        sec = (t.get("memberships") or [{}])[0].get("section", {}).get("name", "No section")
        grouped.setdefault(sec, []).append(t)

    for sec, sec_tasks in grouped.items():
        if not section_filter:
            print(f"\n── {sec} ──")
        for t in sec_tasks:
            done = "✓" if t.get("completed") else " "
            assignee = t.get("assignee", {})
            assignee_name = f"  @{assignee['name']}" if assignee else ""
            print(f"[{done}] {t['gid']}  {t['name']}{assignee_name}")

    print(f"\nTotal: {len(tasks)} tasks")


def cmd_my(token, config):
    project_id = config["projectId"]
    me = get_me(token)
    fields = "name,completed,memberships.section.name"
    tasks = api("GET", f"/projects/{project_id}/tasks?opt_fields={fields}&limit=100", token)

    my_tasks = [t for t in tasks if t.get("assignee", {}).get("gid") == me["gid"]]
    # Re-fetch with assignee field since list doesn't always include it
    # Use assignee filter instead
    my_tasks_url = (
        f"/tasks?project={project_id}&assignee={me['gid']}"
        f"&opt_fields=name,completed,memberships.section.name&limit=100"
    )
    my_tasks = api("GET", my_tasks_url, token)

    if not my_tasks:
        print("No tasks assigned to you.")
        return

    for t in my_tasks:
        done = "✓" if t.get("completed") else " "
        sec = (t.get("memberships") or [{}])[0].get("section", {}).get("name", "")
        print(f"[{done}] {t['gid']}  {t['name']}  ({sec})")

    print(f"\nTotal: {len(my_tasks)} tasks")


def cmd_show(token, task_id):
    fields = "name,completed,notes,assignee.name,memberships.section.name,tags.name,created_at,modified_at,due_on"
    t = api("GET", f"/tasks/{task_id}?opt_fields={fields}", token)

    print(f"Task: {t['name']}")
    print(f"ID: {t['gid']}")
    print(f"Status: {'Done' if t.get('completed') else 'Open'}")
    sec = (t.get("memberships") or [{}])[0].get("section", {}).get("name", "-")
    print(f"Section: {sec}")
    assignee = t.get("assignee")
    print(f"Assignee: {assignee['name'] if assignee else '-'}")
    tags = ", ".join(tag["name"] for tag in t.get("tags", [])) or "-"
    print(f"Tags: {tags}")
    if t.get("due_on"):
        print(f"Due: {t['due_on']}")
    print(f"Created: {(t.get('created_at') or '')[:10]}")
    print(f"Modified: {(t.get('modified_at') or '')[:10]}")
    if t.get("notes"):
        print(f"\nNotes:\n{t['notes']}")


def cmd_done(token, config, task_id):
    project_id = config["projectId"]
    api("PUT", f"/tasks/{task_id}", token, {"data": {"completed": True}})
    sections = get_sections(token, project_id)
    done_sec = next((s for s in sections if "done" in s["name"].lower()), None)
    if done_sec:
        api("POST", f"/sections/{done_sec['gid']}/addTask", token, {"data": {"task": task_id}})
    print(f"Task {task_id} marked as done")


def cmd_start(token, config, task_id):
    project_id = config["projectId"]
    me = get_me(token)

    # Assign to current user
    api("PUT", f"/tasks/{task_id}", token, {"data": {"assignee": me["gid"]}})

    # Move to In Progress
    section = find_section(token, project_id, "in progress")
    api("POST", f"/sections/{section['gid']}/addTask", token, {"data": {"task": task_id}})

    print(f"Task {task_id} assigned to {me['name']}, moved to \"{section['name']}\"")


def cmd_move(token, config, task_id, section_name):
    project_id = config["projectId"]
    section = find_section(token, project_id, section_name)
    api("POST", f"/sections/{section['gid']}/addTask", token, {"data": {"task": task_id}})
    print(f"Task {task_id} moved to \"{section['name']}\"")


def cmd_create(token, config, name, section_name=None, notes=None):
    project_id = config["projectId"]
    sections = get_sections(token, project_id)

    section_gid = None
    if section_name:
        sec = find_section(token, project_id, section_name)
        section_gid = sec["gid"]
    else:
        backlog = next((s for s in sections if "backlog" in s["name"].lower()), None)
        if backlog:
            section_gid = backlog["gid"]

    body = {
        "data": {
            "name": name,
            "projects": [project_id],
        }
    }
    if notes:
        body["data"]["notes"] = notes
    if section_gid:
        body["data"]["memberships"] = [{"project": project_id, "section": section_gid}]

    task = api("POST", "/tasks", token, body)
    print(f"Created: {task['gid']}  {task['name']}")


def cmd_sections(token, config):
    sections = get_sections(token, config["projectId"])
    for s in sections:
        print(f"{s['gid']}  {s['name']}")


def cmd_search(token, config, query):
    project_id = config["projectId"]
    fields = "name,completed,memberships.section.name,assignee.name"
    tasks = api("GET", f"/projects/{project_id}/tasks?opt_fields={fields}&limit=100", token)
    lower = query.lower()
    matched = [t for t in tasks if lower in t["name"].lower()]

    if not matched:
        print("No tasks found")
        return

    for t in matched:
        done = "✓" if t.get("completed") else " "
        sec = (t.get("memberships") or [{}])[0].get("section", {}).get("name", "")
        print(f"[{done}] {t['gid']}  {t['name']}  ({sec})")

    print(f"\nFound: {len(matched)}")


def cmd_whoami(token):
    me = get_me(token)
    print(f"Name: {me['name']}")
    print(f"Email: {me.get('email', '-')}")
    print(f"GID: {me['gid']}")


def cmd_update():
    # TODO: pull latest from GitHub repo
    print(f"Current version: {VERSION}")
    print("Update not yet implemented")


# --- Main ---

def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print(__doc__.strip())
        return

    if args[0] == "--version":
        print(VERSION)
        return

    if args[0] == "update":
        cmd_update()
        return

    # Load token
    token = load_token()
    if not token:
        print("No Asana token found.")
        print("Create a Personal Access Token at: https://app.asana.com/0/my-apps")
        print("Then save it to: ~/.config/asana/token")
        sys.exit(1)

    # whoami doesn't need project config
    if args[0] == "whoami":
        cmd_whoami(token)
        return

    # Load project config
    config = load_config()

    cmd = args[0]

    if cmd in ("list", "ls"):
        cmd_list(token, config, args[1] if len(args) > 1 else None)
    elif cmd == "my":
        cmd_my(token, config)
    elif cmd == "show":
        if len(args) < 2:
            print("Usage: asana-cli show <task_id>", file=sys.stderr)
            sys.exit(1)
        cmd_show(token, args[1])
    elif cmd == "done":
        if len(args) < 2:
            print("Usage: asana-cli done <task_id>", file=sys.stderr)
            sys.exit(1)
        cmd_done(token, config, args[1])
    elif cmd == "start":
        if len(args) < 2:
            print("Usage: asana-cli start <task_id>", file=sys.stderr)
            sys.exit(1)
        cmd_start(token, config, args[1])
    elif cmd == "move":
        if len(args) < 3:
            print("Usage: asana-cli move <task_id> <section>", file=sys.stderr)
            sys.exit(1)
        cmd_move(token, config, args[1], " ".join(args[2:]))
    elif cmd in ("create", "add"):
        if len(args) < 2:
            print("Usage: asana-cli create <name> [--section X] [--notes X]", file=sys.stderr)
            sys.exit(1)
        name_parts = []
        section = None
        notes = None
        i = 1
        while i < len(args):
            if args[i] in ("--section", "-s"):
                i += 1
                section = args[i] if i < len(args) else None
            elif args[i] in ("--notes", "-n"):
                i += 1
                notes = args[i] if i < len(args) else None
            else:
                name_parts.append(args[i])
            i += 1
        cmd_create(token, config, " ".join(name_parts), section, notes)
    elif cmd == "sections":
        cmd_sections(token, config)
    elif cmd in ("search", "find"):
        if len(args) < 2:
            print("Usage: asana-cli search <query>", file=sys.stderr)
            sys.exit(1)
        cmd_search(token, config, " ".join(args[1:]))
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print("Run 'asana-cli help' for usage.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
