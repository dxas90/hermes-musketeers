---
name: musketeers-feature
description: "Parallel feature development with file ownership boundaries, interface contracts, and multi-agent implementation (Aramis). Load when building features that can be decomposed into parallel work streams."
version: 1.0.0
tags: [musketeers, feature, aramis, parallel, implementation]
---

# Musketeers Parallel Feature Development

Orchestrate parallel feature implementation with multiple builder sub-agents (Aramis), each working within strict file ownership boundaries and coordinating via interface contracts.

## When to Use

- Feature can be split into 2+ independent work streams
- Changes span multiple files/modules/layers
- User requests parallel implementation or uses `--plan-first`
- Large feature that benefits from divide-and-conquer

## File Ownership Strategies

### By Directory
```
implementer-1: src/components/auth/
implementer-2: src/api/auth/
implementer-3: tests/auth/
```
Best for: Well-organized codebases with clear boundaries.

### By Module
```
implementer-1: Authentication (login, register, logout)
implementer-2: Authorization (roles, permissions, guards)
```
Best for: Domain-driven design, feature architectures.

### By Layer
```
implementer-1: UI layer (components, styles)
implementer-2: Business logic (services, validators)
implementer-3: Data layer (models, repositories)
```
Best for: Traditional MVC/layered architectures.

## The Cardinal Rule

**One owner per file.** No file should be assigned to multiple implementers.

When files must be shared:
1. Designate a single owner
2. Other implementers request changes via their report
3. Owner applies changes sequentially
4. Alternative: Extract interfaces into a contract file

## Workflow

### 1. Analyze & Decompose

1. Explore the codebase: identify files to modify, patterns, integration points
2. Decompose into work streams:
   - Each gets exclusive file ownership
   - Define interface contracts at boundaries
   - Identify dependencies (minimize chain depth)
   - Balance workload across streams

### 2. Plan Presentation (--plan-first)

Present decomposition before spawning:

```markdown
## Feature Decomposition: {feature}

### Stream 1: {name}
- Owner: implementer-1
- Files: {exclusive list}
- Dependencies: none
- Acceptance criteria: {verifiable checks}

### Stream 2: {name}
- Owner: implementer-2
- Files: {exclusive list}
- Dependencies: blocked by Stream 1 (needs interface from {file})
- Acceptance criteria: {verifiable checks}

### Interface Contract
{shared types/signatures both streams agree on}
```

### 3. Spawn Implementers (Parallel)

```
delegate_task(tasks=[
  {
    "goal": "Implement {stream_1_name}. ONLY modify files in your ownership boundary.",
    "context": "You are Aramis, a parallel feature builder.\n\nOWNED FILES (you may only modify these):\n{file_list}\n\nDO NOT TOUCH:\n{excluded_files}\n\nInterface contract (immutable — do not change):\n{contract}\n\nAcceptance criteria:\n{criteria}\n\nExisting patterns to follow:\n{conventions}\n\nWorkflow:\n1. Read and understand your assigned files\n2. Plan implementation within your boundary\n3. Build — match existing style, follow contracts\n4. Verify: lint passes, tests pass, contracts satisfied\n5. Report: summary of changes, any integration concerns",
    "toolsets": ["terminal", "file", "web"]
  },
  {
    "goal": "Implement {stream_2_name}...",
    ...
  }
])
```

### 4. Integration & Verification

After all implementers complete:
1. Verify interface contracts are satisfied on all sides
2. Run integration tests
3. Check for any file ownership violations
4. Resolve any integration issues (may require a follow-up task)

### 5. Report

```markdown
## Feature Implementation Report: {feature}

### Streams Completed
| Stream | Owner | Files Changed | Status |
|--------|-------|---------------|--------|
| {name} | impl-1 | 3 files | ✅ Complete |
| {name} | impl-2 | 4 files | ✅ Complete |

### Integration Status
- Interface contracts: ✅ Satisfied
- Tests: ✅ Passing
- Lint: ✅ Clean

### Files Modified
{consolidated list}

### Notes
{any concerns, deviations, or follow-up items}
```

## Conflict Avoidance Checklist

Before spawning:
- [ ] Every file has exactly one owner
- [ ] Interface contracts are explicit (types, not descriptions)
- [ ] Acceptance criteria are testable
- [ ] Dependencies are minimal (prefer independent streams)
- [ ] Shared config/types extracted to a contract file if needed

## DArtagnan Integration

After feature implementation, optionally spawn DArtagnan:
```
delegate_task(
  goal="Write documentation for the {feature} feature.",
  context="You are DArtagnan, a documentation specialist.\nSource files: {modified_files}\nDoc type: {README update | API reference | Architecture guide}\nAudience: {target}\nWrite by reading source directly — do not invent APIs.",
  toolsets=["terminal", "file"]
)
```
