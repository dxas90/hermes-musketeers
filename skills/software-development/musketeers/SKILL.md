---
name: musketeers
description: "Use when orchestrating multi-agent teams for parallel code review, hypothesis-driven debugging, parallel feature development, or documentation generation. Adapts the Musketeers framework to Hermes delegate_task."
version: 1.0.0
author: Daniel Ramirez
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [multi-agent, delegation, code-review, debugging, feature-development, orchestration, parallel]
    related_skills: [requesting-code-review, systematic-debugging, plan, hermes-agent]
---

# Hermes Musketeers — Multi-Agent Orchestration

Orchestrate specialized agent teams for parallel code review, hypothesis-driven debugging, parallel feature development, and documentation generation using `delegate_task`.

## Overview

Musketeers is a multi-agent orchestration framework adapted for Hermes. It provides four named agent personas — **Athos** (reviewer), **Porthos** (debugger), **Aramis** (builder), **DArtagnan** (documentation) — and an orchestrator persona **Dumas** for complex coordination. All agents run via `delegate_task`.

**Core principle:** No agent verifies its own work. Parallel specialists working concurrently with fresh context outperform a single generalist working sequentially.

## When to Use

- Code review across multiple quality dimensions (security, performance, architecture, testing, accessibility)
- Debugging where the root cause is unknown — investigate competing hypotheses in parallel
- Feature development where work can be split by file ownership boundaries
- Documentation generation after a feature ships
- Any task where 2-5 independent workstreams would be faster than one sequential pass

**Don't use for:** single-file edits, simple bug fixes, quick questions, or tasks that inherently require sequential steps.

## The Agent Personas

### Athos — Code Reviewer

Operates on one assigned review dimension. Returns structured findings with file:line citations, severity ratings, and actionable fixes. **Read-only** — uses `["terminal"]` to search and read; never writes files.

### Porthos — Hypothesis Investigator

Investigates one assigned hypothesis about a bug's root cause. Gathers confirming and falsifying evidence. Reports confidence level (High/Medium/Low) and causal chain. **Read-only** — uses `["terminal"]`.

### Aramis — Parallel Builder

Implements features within explicitly assigned file ownership boundaries. Never touches files outside its assignment. Communicates interface mismatches back as text output. Uses `["terminal", "file"]`.

### DArtagnan — Documentation Specialist

Reads source files directly to produce accurate documentation: READMEs, API references, architecture overviews, setup guides. Uses `["terminal", "file"]`.

### Dumas — Orchestrator

Decomposes complex tasks into parallel workstreams, spawns teammates as `role="orchestrator"`, synthesizes results. Used for the most complex multi-step work. Uses `["terminal", "file"]`.

## Workflow: Multi-Reviewer Code Review

See [team-review](references/team-review.md) for the full procedure.

**Quick pattern:**

```python
dimensions = ["security", "performance", "architecture"]
tasks = [
    {
        "goal": f"""You are Athos, a specialized code reviewer focused exclusively on {dim}.
Review the following git diff and return ONLY findings in this format:
### [SEVERITY] Title
**Location**: `file:line`
**Severity**: Critical | High | Medium | Low
**Evidence**: what was found
**Impact**: what could go wrong
**Fix**: specific actionable remediation

SECURITY focuses on: input validation, auth, injection, secrets, CVEs.
PERFORMANCE focuses on: N+1 queries, memory leaks, caching, algorithm complexity.
ARCHITECTURE focuses on: SOLID, coupling, separation of concerns, error handling patterns.
TESTING focuses on: coverage gaps, test isolation, edge cases, assertion quality.
ACCESSIBILITY focuses on: WCAG 2.1 AA, ARIA, keyboard nav, screen reader support.

Report "No findings for this dimension." if nothing warrants attention.

<diff>
{diff_content}
</diff>""",
        "context": f"Code review: {dim} dimension. Return structured findings only.",
        "toolsets": ["terminal"],
    }
    for dim in dimensions
]

results = delegate_task(
    goal="Run parallel code review across dimensions",
    context="Parallel review — consolidate results",
    toolsets=["terminal"],
    tasks=tasks,
)
```

After collecting results, consolidate: deduplicate same file:line findings, use the higher severity on conflicts, group by Critical/High/Medium/Low.

## Workflow: Hypothesis-Driven Debugging

See [parallel-debugging](references/parallel-debugging.md) for the full procedure.

**Quick pattern:**

1. Triage the error: read relevant files, collect stack trace and symptom
2. Generate N hypotheses (cover Logic Error, Data Issue, State Problem, Integration Failure, Resource Issue, Environment)
3. Spawn one Porthos per hypothesis in parallel

```python
hypotheses = [
    "Race condition in cache invalidation between write and read operations",
    "Input validation missing on the POST /users endpoint — null body crashes handler",
    "Dependency version mismatch — library v2.x removed method called by this code",
]

tasks = [
    {
        "goal": f"""You are Porthos, a hypothesis-driven debugging investigator.
Your assigned hypothesis: {h}

Investigation protocol:
1. Identify what must be true if this hypothesis is correct
2. Search for confirming evidence (file:line citations required)
3. Search for falsifying evidence (also cite)
4. Rate confidence: High (>80%), Medium (50-80%), Low (<50%)
5. If confirmed, propose the minimal fix

Return structured report:
HYPOTHESIS: {h}
STATUS: Confirmed | Falsified | Inconclusive
CONFIDENCE: High | Medium | Low
CONFIRMING EVIDENCE:
- file:line — description
FALSIFYING EVIDENCE:
- file:line — description
CAUSAL CHAIN: (if confirmed)
PROPOSED FIX: (if confirmed)

Context about the bug:
{bug_context}""",
        "context": f"Investigate hypothesis: {h[:60]}. Return evidence report.",
        "toolsets": ["terminal"],
    }
    for h in hypotheses
]

results = delegate_task(
    goal="Parallel hypothesis investigation",
    context="Debug: investigate competing hypotheses, collect evidence",
    toolsets=["terminal"],
    tasks=tasks,
)
```

Compare confidence ratings. Confirmed hypotheses with causal chains are root causes. Present the highest-confidence confirmed hypothesis with its fix.

## Workflow: Parallel Feature Development

See [parallel-feature](references/parallel-feature.md) for the full procedure.

**Quick pattern:**

1. Decompose: identify independent file ownership streams
2. Define interface contracts at stream boundaries
3. Spawn Aramis agents in parallel; Dumas (orchestrator) coordinates if dependencies exist

```python
streams = [
    {
        "name": "backend-api",
        "owned_files": ["src/api/users.py", "src/models/user.py", "tests/test_users.py"],
        "contract": "Exposes POST /users → UserResponse(id, email, created_at)",
        "task": "Implement the user creation endpoint with input validation and unit tests",
    },
    {
        "name": "frontend-form",
        "owned_files": ["src/components/UserForm.tsx", "src/components/UserForm.test.tsx"],
        "contract": "Calls POST /users, handles 201 and 422 responses",
        "task": "Implement the user registration form with error handling",
    },
]

tasks = [
    {
        "goal": f"""You are Aramis, a parallel feature builder with strict file ownership.
Stream: {s['name']}
Owned files (ONLY modify these): {', '.join(s['owned_files'])}
Interface contract: {s['contract']}
Task: {s['task']}

FILE OWNERSHIP RULES:
- Only modify files in your owned list
- Never touch files owned by other streams
- If a shared file needs changing, describe what change is needed in your output
- Implement exactly what is specified — no scope creep

When complete, report:
FILES CHANGED: list with summary of changes
INTERFACE DELIVERED: confirm or describe deviation
BLOCKERS: any issues that require coordination
TEST RESULTS: pass/fail""",
        "context": f"Build {s['name']} stream. Strict file ownership. Return implementation report.",
        "toolsets": ["terminal", "file"],
    }
    for s in streams
]

results = delegate_task(
    goal="Parallel feature implementation",
    context="Feature development: parallel streams with file ownership boundaries",
    toolsets=["terminal", "file"],
    tasks=tasks,
)
```

## Workflow: Documentation Generation

```python
delegate_task(
    goal="""You are DArtagnan, a technical documentation specialist.
Read the source files listed below and produce accurate documentation.
Never document based on assumption — read the actual code.

Documentation to produce: {doc_type}
Target audience: {audience}
Files to read: {file_list}

Documentation standards:
- Start with the "why" before the "how"
- Active voice: "Run the server" not "The server should be run"
- Test every code example — it must run without modification
- Keep sentences short and steps numbered for sequences
- Remove outdated content rather than leaving it

Write the documentation to: {output_file}""",
    context="Documentation generation. Read source, write accurate docs.",
    toolsets=["terminal", "file"],
)
```

## Consolidation Patterns

### Deduplicating Review Findings

When multiple Athos agents report the same file:line:
- Same issue → merge, keep more detailed description, use higher severity
- Different issues at same location → keep both, tag as co-located
- Conflicting recommendations → include both with reviewer attribution

### Arbitrating Debug Results

Rank by: confidence level (High > Medium > Low) → strength of causal chain → amount of supporting evidence → absence of contradicting evidence.

A falsified hypothesis is a valuable result — it eliminates a possibility.

### Merging Build Streams

After parallel Aramis runs:
1. Verify no two streams modified the same file (ownership violation)
2. Check interface contracts were fulfilled
3. Run build + tests on the merged result
4. If conflicts, assign a single Aramis or DArtagnan to resolve the shared file

## Common Pitfalls

1. **Vague hypotheses** — Porthos needs a specific, falsifiable claim. "Something is wrong with auth" is not a hypothesis. "JWT expiry is not checked on the /admin endpoint" is.

2. **Overlapping file ownership** — Two Aramis agents touching the same file causes conflicts. Assign ownership before spawning. When in doubt, one agent owns the shared file.

3. **Missing context in delegate_task** — Subagents start with zero history. Include the full diff, bug description, or feature spec in `goal` or `context`. Don't reference "what we discussed" — they can't see it.

4. **Treating suggestions as blockers** — Athos findings marked Low are non-blocking. Only Critical and High findings require resolution before shipping.

5. **Running delegate_task inside execute_code** — `delegate_task` is a top-level tool call, not callable from within scripts. Call it directly from your agent loop.

6. **Forgetting to consolidate** — Parallel results land as separate outputs. Always merge, deduplicate, and prioritize before presenting to the user.

7. **Spawning too many agents** — 2-4 is optimal. Beyond 5, coordination overhead outweighs parallelism gains.

## Verification Checklist

- [ ] `delegate_task` called at top level (not inside execute_code)
- [ ] Each agent's `goal` contains all necessary context (diff, bug description, file list)
- [ ] File ownership boundaries are non-overlapping for Aramis agents
- [ ] Review findings are deduplicated by file:line before presenting
- [ ] Debug hypotheses are specific and falsifiable
- [ ] Porthos reports include both confirming AND falsifying evidence
- [ ] Athos reports include file:line citations for every finding
- [ ] DArtagnan output files verified against actual source before writing
