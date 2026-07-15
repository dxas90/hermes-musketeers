---
name: musketeers-ship-gate
description: >
  Completion gate before telling the user a coding task is done or opening a PR.
  Run project verification commands, cite real exit codes, and block completion
  on missing evidence. No "done" without executed verification.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [musketeers, verification, tests, quality, ship]
    related_skills:
      - musketeers-synthesize-winner
      - requesting-code-review
      - systematic-debugging
      - musketeers-karpathy
---

# Musketeers Ship Gate

Dumas's SOUL contract: report scope, files changed, commands run, test results,
remaining risks, and honest implementation status. No "done" without evidence.

## When to Use

- After synthesis or solo edits, before final user reply
- Before pushing / opening a PR
- After a bug fix (regression check)

Skip for:

- Read-only research answers
- Scaffolds / docs explicitly marked as incomplete

## Gate Steps

1. **Scope audit** — List every modified path; confirm each maps to the user's request.
   Flag any drift.

2. **Discover commands** — Priority order:
   - `AGENTS.md` / `README.md` / `CONTRIBUTING.md` in repo root
   - `package.json` scripts, `pyproject.toml` `[tool.scripts]`, `Makefile`
   - `scripts/ci_local.sh` or equivalent

3. **Run** — Execute each required command with `terminal` (foreground); capture exit
   code and material stdout/stderr. Do not invent output.

4. **Lint / types** — If the repo uses them (`ruff`, `mypy`, `eslint`, `golangci-lint`),
   run on touched paths or project default.

5. **Secrets scan** — No `.env`, tokens, or private keys in diff. Confirm `.gitignore`
   covers any new credential files before they are created.

6. **Report** — Use the table below with honest status.

**Done when:** every required command has a real exit code recorded; failures are
fixed or explicitly surfaced as blockers.

## Report Format

```
## Ship Gate

| Check                  | Status     | Evidence                          |
|------------------------|------------|-----------------------------------|
| Scope (files changed)  | PASS/FAIL  | <list of paths>                   |
| Tests                  | PASS/FAIL  | <command + exit code + key lines> |
| Lint / types           | PASS/SKIP  | <command + exit code>             |
| Secrets scan           | PASS/FAIL  | <method used>                     |

Implementation status: IMPLEMENTED | SCAFFOLDED | BLOCKED
Remaining risks: <explicit list or "none">
```

## Status Definitions

| Status        | Meaning                                                      |
|---------------|--------------------------------------------------------------|
| IMPLEMENTED   | Behavior is present, tests pass, commands exit 0             |
| SCAFFOLDED    | Structure exists; behavior incomplete — say so explicitly    |
| BLOCKED       | Depends on external change, missing data, or unresolved bug  |

Never claim IMPLEMENTED when tests were not run. If you cannot run tests (no
environment, missing deps), state the concrete blocker.

## After a Failed Gate

Do not re-run the full team. Load `systematic-debugging` or spawn 1-2 focused
Porthos delegates with the failing command output as evidence. See the repair
pattern in `musketeers-debug`.

## Pitfalls

- Do NOT declare done before running tests — "it looks correct" is not evidence.
- Do NOT skip gate for "minor" changes — regressions live in minor changes.
- Do NOT fabricate exit codes. If a command was not run, say so.
- A gate that blocks on a known external dependency is fine — report it honestly.
