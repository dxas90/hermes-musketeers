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

### Athos (Reviewer)
```
delegate_task(
  goal="Review {target} for {dimension} issues. Produce structured findings with file:line citations, severity (Critical/High/Medium/Low), evidence, impact, and recommended fix.",
  context="Dimension: {security|performance|architecture|testing|accessibility}\nTarget files: {file list}\nDiff content: {diff}\nOutput format: ### [SEVERITY] Title\n**Location**: file:line\n**Severity**: ...\n**Evidence**: ...\n**Impact**: ...\n**Recommended Fix**: ...",
  toolsets=["terminal", "file", "web"]
)
```

### Porthos (Debugger)
```
delegate_task(
  goal="Investigate hypothesis: '{hypothesis}'. Gather evidence to confirm or falsify. Report confidence level (High >80%, Medium 50-80%, Low <50%) with file:line citations and causal chain.",
  context="Bug symptoms: {description}\nScope: {files|module|project}\nHypothesis: {statement}\nEvidence criteria:\n  Confirming: {what would prove it}\n  Falsifying: {what would disprove it}",
  toolsets=["terminal", "file"]
)
```

### Aramis (Builder)
```
delegate_task(
  goal="Implement {component}. Work ONLY within owned files. Follow interface contracts at boundaries.",
  context="Owned files/dirs: {list}\nInterface contracts: {types/signatures}\nAcceptance criteria: {verifiable checks}\nExisting patterns to follow: {conventions}\nDO NOT modify: {excluded files}",
  toolsets=["terminal", "file", "web"]
)
```

### DArtagnan (Docs)
```
delegate_task(
  goal="Write {doc_type} documentation for {subject}. Read source files directly — do not invent APIs.",
  context="Doc type: {README|API Reference|Architecture|Setup Guide|Troubleshooting}\nSource files to read: {list}\nAudience: {new contributors|integrators|operators}\nOutput location: {path}",
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
1. **Deduplicate** — Merge findings about the same location/issue
2. **Resolve conflicts** — When agents disagree, use higher severity
3. **Prioritize** — Group by severity (Critical → High → Medium → Low)
4. **Cross-reference** — Note findings that span multiple dimensions
5. **Gap analysis** — Identify areas with insufficient coverage

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
