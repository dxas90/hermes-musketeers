---
name: musketeers-workspace
description: "Create and manage long-running task workspaces for cross-codebase work. Use when starting bulk operations, cross-repo tasks, or resuming multi-session work that shouldn't pollute repo git histories."
version: 1.0.0
tags: [musketeers, workspace, orchestration, cross-repo]
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [musketeers, workspace, orchestration, cross-repo]
    related_skills: [musketeers-orchestration, plan]
---

# Agent Workspace Management

Workspaces provide isolated tracking for long-running, cross-codebase agent tasks without polluting individual repository git histories.

## When to Use

- Starting a long-running task spanning multiple repos
- Tracking progress on bulk operations (fix all issues, handle PRs)
- Resuming work on a previously started cross-codebase task
- Organizing work that shouldn't pollute individual repo histories

## CRITICAL: Gather Requirements First

**NEVER start creating a workspace without user input.** Always ask:

1. **Goal**: What does success look like?
2. **Scope**: Which repos/orgs are included? What's excluded?
3. **Workflow**: What steps should be performed for each item?
4. **Validation**: How do we verify each item is complete?
5. **Output**: Where do results go? (PRs, docs, reports?)

## Workspace Structure

```
~/git/agent-workspace/<task-name>/
├── README.md          # Goal, scope, workflow, validation criteria
├── progress.md        # Tracking: done items, remaining, blockers
├── notes/             # Per-repo or per-item findings
│   ├── repo-a.md
│   └── repo-b.md
└── output/            # Generated artifacts (docs, configs, reports)
```

## Lifecycle

### 1. Create
```bash
mkdir -p ~/git/agent-workspace/<task-name>/{notes,output}
```
Write `README.md` with the 5 gathered requirements.

### 2. Track Progress
Update `progress.md` as work completes:
```markdown
## Progress: <task-name>

### Completed (3/10)
- [x] repo-a — PR #42 merged
- [x] repo-b — PR #55 merged
- [x] repo-c — PR #61 merged

### In Progress (1)
- [ ] repo-d — PR #70 open, waiting review

### Remaining (6)
- [ ] repo-e
- [ ] repo-f
...

### Blockers
- repo-g: no access, need credentials
```

### 3. Resume
When resuming, read `progress.md` to understand current state and pick up next item.

### 4. Close
When all items complete, update `README.md` with summary and final status.

## Integration with Musketeers

The orchestrator (Dumas) can delegate workspace items to sub-agents:
- Each Aramis gets one repo/item to work on
- Progress tracking stays in the workspace
- Results (PRs, docs) are linked back in `progress.md`
