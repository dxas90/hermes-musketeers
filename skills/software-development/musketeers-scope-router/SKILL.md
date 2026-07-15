---
name: musketeers-scope-router
description: >
  Route every user request to the cheapest team composition that satisfies it —
  read-only, single-agent, or full Musketeers team — before spending tokens or
  spawning leaves. Load this before musketeers-orchestration on every non-trivial task.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [musketeers, triage, orchestration, performance]
    related_skills:
      - musketeers-explore-first
      - musketeers-orchestration
      - musketeers-karpathy
      - plan
---

# Musketeers Scope Router

Wrong routing is the most expensive mistake: three Athos reviewers on a trivial
one-liner, or a solo coordinator on a cross-cutting security refactor. Run this
skill first on every non-trivial task.

## When to Use

- Start of any turn with a new or shifted user goal
- User asks to review, audit, explain, or compare code (read-only)
- User asks to implement, fix, refactor, or ship (build)
- Ambiguous ask ("look at X and fix it") — classify the implement portion
  only after explore

## Decision Tree

```
User request
  ├─ Explicit: "solo", "just you", "no team", "single agent"?
  │     → Dumas solo: explore → implement → musketeers-ship-gate
  │
  ├─ Read-only intent? ("review", "audit", "explain", "what's wrong", "check",
  │   "opportunities", "architecture question", no "fix"/"add"/"implement")?
  │     → musketeers-explore-first; spawn Athos ONLY if user asks for review
  │
  ├─ Trivial one-liner? (exact file:line given, single obvious edit, typo)?
  │     → Dumas solo fix + musketeers-ship-gate
  │
  ├─ Pure documentation task?
  │     → Spawn DArtagnan (musketeers-docs)
  │
  ├─ Bug with unclear root cause?
  │     → musketeers-explore-first → musketeers-debug (Porthos competing hypotheses)
  │
  ├─ Code changes needing quality gates (security, perf, arch)?
  │     → musketeers-review (Athos, 1-4 dimensions per task size)
  │
  └─ Non-trivial implementation / feature / refactor?
        → musketeers-explore-first → plan → musketeers-feature (Aramis parallel)
```

## Read-Only Signals

Treat as explore-only when the user says:

- "check out", "review", "audit", "what's wrong with", "explain", "summarize"
- "opportunities", "suggestions", "thoughts on"
- Architecture or docs questions without "change the code" or "fix"

No `delegate_task` unless the user explicitly asks to implement.

## Team Size Heuristics

| Request type         | Team                          | Skills                                    |
|----------------------|-------------------------------|-------------------------------------------|
| Read-only / explore  | Dumas only                    | musketeers-explore-first                  |
| Trivial one-liner    | Dumas only                    | musketeers-ship-gate                      |
| Bug (known location) | Dumas or 1 Porthos            | musketeers-debug (width=1)                |
| Bug (unclear cause)  | 2-3 Porthos (ACH)             | musketeers-debug                          |
| Code review          | 1-4 Athos (one dim each)      | musketeers-review                         |
| Feature / refactor   | 1-3 Aramis (parallel streams) | musketeers-feature                        |
| Docs                 | 1 DArtagnan                   | musketeers-docs                           |
| Full-stack           | Dumas + 3 Aramis + 1 Athos    | musketeers-feature + musketeers-review    |

**Rule**: Start with the smallest team that covers all required dimensions.
Adding agents adds coordination overhead — justify every slot.

## Pitfalls

- Do NOT spawn Aramis for a read-only request just because it involves code.
- Do NOT spawn Porthos before exploring — hypotheses need evidence first.
- Do NOT skip routing on "small" tasks — the cheapest mistake is wrong team size.
- If the user's intent is ambiguous, state the routing decision and ask to confirm.
