---
name: musketeers-context-budget
description: >
  Token discipline for coordinators and delegates — batch reads, cap pasted logs,
  filter before paste, load only phase-relevant skills. Keeps swarms fast and
  delegate context packets tight. Load alongside musketeers-explore-first.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [musketeers, performance, context, delegation, coordinator]
    related_skills:
      - musketeers-explore-first
      - musketeers-orchestration
      - musketeers-scope-router
---

# Musketeers Context Budget

Musketeers optimize swarm **breadth** (parallel delegates). Coordinator and leaf
**depth** (megabyte pastes, full file dumps, full skill catalog) destroys latency
and blows context windows. Apply this discipline on every explore and pre-dispatch turn.

## Coordinator Rules

### Batch independent I/O

Multiple `read_file` / `search_files` / read-only `terminal` calls in **one turn**
when inputs do not depend on each other. Never serialize independent reads.

### Cap pasted material

| Material                  | Max in context / chat           |
|---------------------------|---------------------------------|
| Stack trace / test output | ~80 lines or 4 KB               |
| Full file body            | Use `offset`/`limit`; cite `path:line` |
| Directory listings        | `search_files` with `limit=50`  |
| Delegate summaries        | Bullets: files, commands, exit codes |
| Skill body                | Load only the skill for current phase |

### Filter before paste

Use `execute_code` when you need to:

- Ripgrep and return only matching lines + numbers
- Parse JSON test output for failures only
- Count or dedupe paths across candidate summaries

### Skills loading

Load only the skill relevant to the current phase:

```
Route turn:    musketeers-scope-router
Explore turn:  musketeers-explore-first  (+  musketeers-context-budget)
Plan turn:     plan
Dispatch turn: musketeers-orchestration
Synthesis:     (use result summaries — no extra skill load)
Gate turn:     musketeers-ship-gate
```

Do NOT load the full musketeers skill catalog on every turn.

## Delegate Context Rules

Each `delegate_task` `context` field should contain:

1. Repo root + branch + dirty/clean status (~1 line)
2. Task contract — what "done" means (~1 paragraph, explicit out-of-scope)
3. Touch map — exact `path:line` anchors (≤10 entries)
4. Evidence bar — exact verification commands to run before finishing
5. Constraints — no commits unless asked, style files, secrets policy
6. Return format — changed files, commands with exit codes, blockers

**Cap per-leaf context at ~3,000 characters.** Longer context dilutes the signal
and triggers compression in mid-swarm turns.

## Coordinator Self-Check Before Dispatch

Before calling `delegate_task`:

- [ ] Context fits ~3,000 chars per leaf
- [ ] Stack traces / logs trimmed to ≤80 lines
- [ ] No full-file pastes — `path:line` references instead
- [ ] Verification commands copied from `AGENTS.md` / manifest, not invented
- [ ] Skill load for this turn is phase-appropriate (not the full catalog)

## Pitfalls

- Do NOT paste `ls -la` output — use `search_files(target='files')`.
- Do NOT include full `read_file` output in delegate context — cite lines.
- Do NOT load every musketeers skill on the first turn; use the scope router to
  determine which phase you are in, then load that phase's skill.
- Compression kicks in at 50 % threshold — keeping context lean prevents mid-session
  quality drops from compressed earlier turns.
