---
name: musketeers-explore-first
description: >
  Gather repo ground truth with batched reads before planning or spawning team members.
  Swarms amplify wrong assumptions — spend one coordinator turn on facts before
  any delegate_task call. Load before musketeers-feature, musketeers-debug, or plan.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [musketeers, discovery, context, software-development]
    related_skills:
      - musketeers-scope-router
      - musketeers-orchestration
      - musketeers-karpathy
      - plan
---

# Musketeers Explore First

Delegates have no memory of your conversation. Wrong file lists and bad
assumptions in `context` fields are the main cause of shallow patches, wrong
files, and false "tests passed" summaries. Spend one coordinator turn gathering
ground truth before spawning anyone.

## When to Use

- New or unfamiliar repo / directory for the user task
- Bug report with a stack trace or symptom description
- Before any `delegate_task` batch for feature/bugfix/refactor
- Before loading `plan` or `musketeers-feature`

Skip when:

- You already have exact `path:line` and confirmed file contents this session
- Trivial one-file typo with path explicitly given by user
- User explicitly asked for single-agent / solo mode

## Explore Checklist (batch all in one turn)

Run these as parallel tool calls — do NOT serialize independent reads:

1. **Manifest** — `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml` at root.
2. **Agent rules** — `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.hermes.md` if present.
3. **Layout** — `search_files` for key dirs; do NOT dump the whole tree.
4. **Relevant symbols** — `search_files` for error strings, function names, feature flags.
5. **Test location** — find test tree and naming convention (`tests/`, `__tests__`, `*_test.go`).
6. **Repro** — Run the smallest command that shows the bug or build failure; save ≤80 lines
   of output for delegate `context`.

**Done when:** you can name root path, test command, and at least 3 relevant
`path:line` anchors without guessing.

## Batching Rule

Independent lookups belong in **one assistant turn**. Do not serialize
`read_file` / `search_files` / `terminal` calls that do not depend on each other.

```
GOOD (one turn):
  read_file(pyproject.toml) + search_files(error_string) + terminal(test --collect-only)

BAD (three turns):
  read_file(pyproject.toml) → wait → search_files(...) → wait → terminal(...)
```

## Handoff

After explore:

- **Solo fix**: `patch` + `musketeers-ship-gate`.
- **Bug (unclear)**: load `musketeers-debug` with evidence gathered here.
- **Feature/refactor**: load `plan`, then `musketeers-feature` with touch map.
- **Review**: load `musketeers-review` with confirmed file list.

## Context Packet for Delegates

Include in every `delegate_task` context after explore:

```
Repo root: <path>
Branch: <name> — clean/dirty (<git status -sb one-liner>)
Test command: <exact command from manifest/AGENTS.md>
Relevant files:
  - <path:line> — <why relevant>
  - ...
Repro output (≤80 lines):
  <paste>
Out of scope: <explicit exclusions>
```

## Pitfalls

- Do NOT paste entire directory listings — use `search_files` with `limit`.
- Do NOT read whole files when you only need definitions — use `offset`/`limit`.
- Do NOT skip explore because "it's a small change" — that assumption is the bug.
- Cap stack traces and CI logs at ~80 lines in delegate context; use `execute_code`
  to filter if output is large.
