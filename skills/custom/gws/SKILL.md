---
name: gws
description: "Google Workspace CLI skill for managing Gmail, Drive, Sheets, Calendar, Docs, Slides, Tasks, Chat, and other Google Workspace services via the `gws` command-line tool. Use this skill whenever the user mentions email, inbox, Google Drive files, spreadsheets, calendar events, Google Docs, presentations, tasks, Google Chat, contacts, or any Google Workspace operation — even if they don't explicitly say 'Google' or 'gws'. Also trigger for cross-service workflows like standup reports, meeting prep, weekly digests, or file announcements. If the user says things like 'check my email', 'what's on my calendar', 'upload this to Drive', 'send a message', 'create a spreadsheet', or 'what meetings do I have today', this is the right skill."
---

You have access to the `gws` CLI tool — a unified interface to all Google Workspace APIs. The user has it installed (v0.16.0) and authenticated. Use it to help them interact with Gmail, Drive, Sheets, Calendar, Docs, and more.

## Command Structure

```
gws <service> <resource> [sub-resource] <method> [flags]
```

### Services

| Service | What it does |
|---------|-------------|
| gmail | Send, read, manage email |
| drive | Files, folders, shared drives |
| sheets | Spreadsheets |
| calendar | Calendars and events |
| docs | Google Docs |
| slides | Presentations |
| tasks | Task lists and tasks |
| people | Contacts and profiles |
| chat | Chat spaces and messages |
| classroom | Classes, rosters, coursework |
| forms | Google Forms |
| keep | Google Keep notes |
| meet | Google Meet conferences |
| events | Workspace event subscriptions |
| workflow | Cross-service productivity workflows (alias: `wf`) |

### Flags

| Flag | Purpose |
|------|---------|
| `--params '<JSON>'` | Query/path parameters |
| `--json '<JSON>'` | Request body (POST/PATCH/PUT) |
| `--upload <PATH>` | File upload (multipart) |
| `--dry-run` | Preview without executing |
| `--format <FMT>` | Output: json (default), table, yaml, csv |
| `--page-all` | Auto-paginate (NDJSON output) |
| `--page-limit <N>` | Max pages (default: 10) |

## Helper Commands

Helpers are high-level shortcuts prefixed with `+`. Prefer these over raw API calls for common tasks — they handle threading, metadata, and formatting automatically.

| Service | Helpers |
|---------|---------|
| Gmail | `+send`, `+triage`, `+reply`, `+reply-all`, `+forward`, `+watch` |
| Sheets | `+append`, `+read` |
| Docs | `+write` |
| Drive | `+upload` |
| Calendar | `+insert`, `+agenda` |
| Chat | `+send` |
| Workflow | `+standup-report`, `+meeting-prep`, `+email-to-task`, `+weekly-digest`, `+file-announce` |

## How to Use This Skill

### 1. Prefer helpers for common tasks

```bash
# Email
gws gmail +send --to alice@example.com --subject "Hello" --body "Message body"
gws gmail +triage                          # Unread inbox summary
gws gmail +reply --message-id <id> --body "Thanks!"

# Calendar
gws calendar +agenda --today               # Today's schedule
gws calendar +agenda --date 2026-03-15     # Specific date

# Drive
gws drive +upload ./report.pdf --name "Q1 Report"

# Sheets
gws sheets +read --spreadsheet-id <id> --range "Sheet1!A1:D10"
gws sheets +append --spreadsheet-id <id> --range "Sheet1" --values '[["a","b","c"]]'

# Workflow
gws workflow +standup-report               # Today's meetings + open tasks
gws workflow +meeting-prep                 # Next meeting prep
gws workflow +weekly-digest                # Weekly summary
```

### 2. Use raw API calls for everything else

When a helper doesn't exist, use the full `gws <service> <resource> <method>` pattern:

```bash
# List Drive files
gws drive files list --params '{"pageSize": 10, "q": "mimeType=\"application/pdf\""}'

# Get a specific email
gws gmail users messages get --params '{"userId": "me", "id": "<messageId>"}'

# Create a calendar event
gws calendar events insert --params '{"calendarId": "primary"}' --json '{
  "summary": "Team standup",
  "start": {"dateTime": "2026-03-15T09:00:00+09:00"},
  "end": {"dateTime": "2026-03-15T09:30:00+09:00"}
}'

# List tasks
gws tasks tasklists list --params '{"maxResults": 10}'
```

### 3. Look up API parameters with schema introspection

When you're unsure about what parameters a method accepts, check the schema first:

```bash
gws schema drive.files.list
gws schema gmail.users.messages.list
gws schema calendar.events.insert
```

This returns the full request/response schema so you can construct the right `--params` and `--json` values.

### 4. Safety: confirm before acting on behalf of the user

**Always use `--dry-run` first** for operations that affect other people or are hard to undo:
- Sending emails (`+send`, `+reply`, `+forward`)
- Sharing files or changing permissions
- Posting to Chat spaces
- Creating/deleting calendar events with attendees
- Modifying or deleting documents

Show the user what will happen and get confirmation before running without `--dry-run`.

For read-only operations (listing files, checking calendar, triaging inbox), just go ahead — no confirmation needed.

### 5. Present results clearly

The `gws` CLI outputs JSON by default. After running a command:
- Parse the JSON output
- Present the key information in a readable format (tables, bullet points, or summaries)
- For long lists, summarize the most relevant items
- Use `--format table` when the user wants a quick glance

### 6. Handle errors gracefully

Exit codes tell you what went wrong:
- **1**: API error — check the error message, the request might need different params
- **2**: Auth error — suggest `gws auth login` to re-authenticate
- **3**: Validation — check flags and parameter format
- **4**: Discovery — the API/method might not exist, verify with `--help`

When a command fails, read the error message carefully, fix the issue, and retry. Use `gws <service> <resource> --help` to check available methods and flags.

### 7. Communicate in the user's language

This user prefers Korean. Present all results, summaries, and explanations in Korean. Keep technical terms (API names, field names, command syntax) in English.
