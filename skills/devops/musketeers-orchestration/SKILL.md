---
name: musketeers-orchestration
description: "Team composition patterns, sizing heuristics, task coordination strategies, and communication protocols for multi-agent Musketeers workflows. Load when spawning teams, delegating work, or managing parallel workstreams."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [musketeers, orchestration, teams, delegation, coordination]
    related_skills: [musketeers-review, musketeers-feature, musketeers-debug, musketeers-workspace]
---

# Musketeers Team Orchestration

Patterns for composing, coordinating, and communicating within multi-agent teams using Hermes delegation.

## Team Composition Presets

| Preset       | Size | Agents                                         | Use When                                      |
|--------------|------|------------------------------------------------|-----------------------------------------------|
| **review**   | 3    | 3× Athos (security, perf, architecture)        | Code changes need multi-dimensional review    |
| **debug**    | 3    | 3× Porthos (competing hypotheses)              | Bug has multiple plausible root causes        |
| **feature**  | 3    | 1× Dumas + 2× Aramis                           | Feature decomposes into parallel streams      |
| **fullstack**| 4    | 1× Dumas + 3× Aramis (FE, BE, tests)           | Full-stack features with clear layers         |
| **research** | 3    | 3× general-purpose (Grep/Read/WebSearch)        | Parallel investigation of different questions  |
| **security** | 4    | 4× Athos (OWASP, auth, deps, secrets)           | Comprehensive security audit                  |
| **migration**| 4    | 1× Dumas + 2× Aramis + 1× Athos (verifier)     | Large refactor or codebase migration          |
| **docs**     | 1    | 1× DArtagnan                                    | Documentation generation or update            |

## Sizing Heuristics

| Complexity   | Team Size | When                                              |
|--------------|-----------|---------------------------------------------------|
| Simple       | 1-2       | Single-dimension review, isolated bug, small fix  |
| Moderate     | 2-3       | Multi-file changes, 2-3 concerns, medium features |
| Complex      | 3-4       | Cross-cutting concerns, large features            |
| Very Complex | 4-5       | Full-stack features, systemic issues              |

**Rule**: Start with the smallest team that covers all required dimensions. More teammates = more coordination overhead.

## Hermes Delegation Mapping

Use `delegate_task` to spawn teammates as subagents:

### Six-Section Context Contract

Every `delegate_task` context must include all six sections. Delegates have no
memory of your conversation — missing sections cause wrong-file edits and false
"tests passed" summaries.

```
1. Repo root: <absolute path>, branch: <name>, status: clean/dirty (<git status -sb>)
2. Task contract: What "done" means in one paragraph. Out-of-scope bullets.
3. Touch map: Exact paths + symbols to read/change (path:line anchors, ≤10 entries).
4. Evidence bar: Exact commands delegates must run before claiming done.
5. Constraints: No commits unless asked. Honor AGENTS.md / style files. No secrets.
6. Return format: Changed file list, commands run with exit codes, blockers.
```

Cap per-delegate context at ~3,000 characters. See `musketeers-context-budget`.

### Athos (Reviewer)
```
delegate_task(
  goal="Review {target} for {dimension} issues. Produce structured findings with file:line citations, severity (Critical/High/Medium/Low), evidence, impact, and recommended fix.",
  context="""
1. Repo root: {path}, branch: {branch}
2. Task contract: Review for {dimension} only. Do not implement fixes.
3. Touch map: {file list with path:line}
4. Evidence bar: Read each file; cite line numbers for every finding.
5. Constraints: Read-only. Do not modify files.
6. Return format:
   ### [SEVERITY] Title
   **Location**: file:line
   **Evidence**: ...
   **Impact**: ...
   **Recommended Fix**: ...
""",
  toolsets=["terminal", "file", "web"]
)
```

### Porthos (Debugger)
```
delegate_task(
  goal="Investigate hypothesis: '{hypothesis}'. Gather evidence to confirm or falsify. Report confidence (High >80%, Medium 50-80%, Low <50%) with file:line citations and causal chain.",
  context="""
1. Repo root: {path}, branch: {branch}
2. Task contract: Confirm or falsify this hypothesis only. Do not fix.
3. Touch map: {relevant files + error location path:line}
4. Evidence bar: Run repro command; capture exit code + ≤80 lines output.
   Repro: {exact command}
   Confirming evidence: {what would prove it}
   Falsifying evidence: {what would disprove it}
5. Constraints: Read-only preferred. No commits.
6. Return format: Confidence level, evidence list with path:line, causal chain.
""",
  toolsets=["terminal", "file"]
)
```

### Aramis (Builder)
```
delegate_task(
  goal="Implement {component}. Work ONLY within owned files. Follow interface contracts at boundaries.",
  context="""
1. Repo root: {path}, branch: {branch}, status: {git status -sb}
2. Task contract: Implement {component}. Out of scope: {exclusions}.
3. Touch map: Owned files/dirs: {list with path:line anchors}.
   Interface contracts: {types/signatures at boundaries}.
   DO NOT modify: {excluded files}.
4. Evidence bar: {test command from AGENTS.md/manifest}. Must exit 0.
5. Constraints: No commits unless asked. Match existing style. No secrets.
6. Return format: Changed file list, commands run with exit codes, blockers.
""",
  toolsets=["terminal", "file", "web"]
)
```

### DArtagnan (Docs)
```
delegate_task(
  goal="Write {doc_type} documentation for {subject}. Read source files directly — do not invent APIs.",
  context="""
1. Repo root: {path}, branch: {branch}
2. Task contract: Write {doc_type} for {audience}. Output to {path}.
3. Touch map: Source files to read: {list with path:line}.
4. Evidence bar: All APIs/types cited from actual source, not invented.
5. Constraints: Read source before writing. No code changes.
6. Return format: Output file path, source files read, any gaps found.
""",
  toolsets=["terminal", "file"]
)
```

## Task Coordination

### Decomposition Principles
1. **Minimize chain depth** — Prefer wide, shallow dependency graphs
2. **One owner per file** — No file assigned to multiple agents
3. **Interface contracts at boundaries** — Define types/signatures agents agree on
4. **Independent verification** — Each task has its own success criteria

### Dependency Patterns

**Independent (best parallelism):**
```
Task A ─┐
Task B ─┼→ Integration
Task C ─┘
```

**Sequential (when required):**
```
Task A → Task B → Task C
```

**Diamond (mixed):**
```
        ┌→ Task B ─┐
Task A ─┤          ├→ Task D
        └→ Task C ─┘
```

### Result Synthesis
After all delegates complete:
1. **Collect** — Gather each delegate summary; extract file lists, commands, exit codes.
2. **Score on evidence** — Test evidence > scope discipline > regression risk > maintainability. Ignore eloquence.
3. **Choose spine** — One candidate (or approach) owns the base diff.
4. **Cherry-pick hunks** — Import only hunks with independent evidence (test or cited path:line reason).
5. **Deduplicate** — Merge findings about the same location/issue across delegates.
6. **Resolve conflicts** — When delegates disagree, use higher severity / stronger evidence.
7. **Prioritize** — Group by severity (Critical → High → Medium → Low).
8. **Re-read before apply** — `read_file` every file you will touch after mental merge.
9. **Gap analysis** — Identify areas with insufficient coverage; note explicitly.
10. **Gate** — Run `musketeers-ship-gate` before declaring done.

## Error Handling & Retry Patterns

### Retry Policy

For transient delegate failures, use bounded retries:

| Parameter | Default | Rule |
|---|---|---|
| **Max attempts** | 2 | Original + 1 retry |
| **Backoff** | Small delay between attempts | Do not spam retries |
| **Allowed cases** | Timeouts, empty output, transient tool errors | Not logic/acceptance failures |

### Timeout Handling

- Prefer shorter, scoped tasks over long-running delegates.
- If a delegate times out:
  1. Classify the missing result as partial
  2. Retry once with tighter scope or reduced files
  3. If still missing, proceed with degraded synthesis if safe

### Degraded Synthesis

When one delegate fails after retries:

- **Do not block the whole workflow** if remaining delegates cover the critical path.
- Mark the missing dimension explicitly in the final report.
- Prefer completeness with one gap over full failure.

### Abort / Replan Criteria

Stop and replan instead of retrying when:

- A delegate fails due to acceptance-criteria mismatch, not execution error
- File ownership conflict is detected mid-stream
- Interface contract is broken by another delegate’s output

### Synthesis With Missing Results

If some delegates never return:

1. Use available results
2. Flag missing coverage explicitly
3. Recommend a follow-up task for the missing dimension instead of fabricating findings

## Communication Anti-Patterns

| Anti-Pattern                     | Problem                              | Better                                |
|----------------------------------|--------------------------------------|---------------------------------------|
| Vague task descriptions          | Agents diverge from intent           | Specific files, criteria, constraints |
| Overlapping file ownership       | Merge conflicts, duplicated work     | Exclusive ownership + contracts       |
| Too many agents                  | Coordination overhead > parallelism  | Start small, add only if needed       |
| No success criteria              | No way to verify completion          | Testable acceptance criteria          |
| Speculative workstreams          | Wasted compute on unused work        | Only tasks that directly serve goal   |
