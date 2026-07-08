---
name: musketeers-review
description: "Multi-reviewer parallel code review across quality dimensions (security, performance, architecture, testing, accessibility). Load when the user asks for a code review or '/team-review' style workflow."
version: 1.0.0
tags: [musketeers, review, athos, code-quality, parallel]
---

# Musketeers Multi-Reviewer Code Review

Orchestrate parallel code reviews where each sub-agent (Athos) focuses on a specific quality dimension, then consolidate into a prioritized report.

## When to Use

- User asks for code review of a file, directory, diff, or PR
- Multiple quality dimensions are relevant (security + performance + architecture)
- Review needs structured, actionable findings with severity ratings

## Review Dimensions

| Dimension         | Focus Areas                                                  | When to Include                     |
|-------------------|--------------------------------------------------------------|-------------------------------------|
| **Security**      | Input validation, auth, injection, secrets, CVEs, crypto     | Code handling user input or auth    |
| **Performance**   | N+1 queries, memory leaks, caching, async, O(n²)            | Data access or hot paths            |
| **Architecture**  | SOLID, coupling, layering, error handling, API design        | Structural changes or new modules   |
| **Testing**       | Coverage gaps, isolation, mocks, edge cases, assertions      | New functionality                   |
| **Accessibility** | WCAG 2.1 AA, ARIA, keyboard nav, contrast, focus mgmt       | UI/frontend changes                 |

## Recommended Combinations

| Scenario               | Dimensions                                   |
|------------------------|----------------------------------------------|
| API endpoint changes   | Security, Performance, Architecture          |
| Frontend component     | Architecture, Testing, Accessibility         |
| Database migration     | Performance, Architecture                    |
| Authentication changes | Security, Testing                            |
| Full feature review    | Security, Performance, Architecture, Testing |

## Workflow

### 1. Determine Target & Scope

Identify what to review:
- **File/directory path** → review those files
- **Git diff** (`main...HEAD`) → `git diff --name-only` for changed files
- **PR number** → `gh pr diff {N} --name-only`

### 2. Spawn Reviewers (Parallel Delegation)

For each dimension, delegate to a sub-agent playing the Athos role:

```
delegate_task(tasks=[
  {
    "goal": "Review the following code for SECURITY issues...",
    "context": "You are Athos, a specialized code reviewer focused on Security.\n\nTarget files:\n{file_list}\n\nFor each finding use this format:\n### [SEVERITY] Finding Title\n**Location**: path/to/file.ts:42\n**Dimension**: Security\n**Severity**: Critical | High | Medium | Low\n**Evidence**: What was found.\n**Impact**: What could go wrong.\n**Recommended Fix**: Specific remediation.\n\nStay strictly within your dimension. Cite file:line for every finding.",
    "toolsets": ["terminal", "file"]
  },
  {
    "goal": "Review the following code for PERFORMANCE issues...",
    ...
  },
  {
    "goal": "Review the following code for ARCHITECTURE issues...",
    ...
  }
])
```

### 3. Consolidate Results

After all reviewers complete:

1. **Parse findings** from each reviewer's report
2. **Deduplicate**: Same file:line + same issue → merge, credit all dimensions
3. **Severity calibration**:
   - If reviewers disagree, use the higher severity
   - Cross-dimensional findings (found by 2+ reviewers) bump severity one level
4. **Organize by severity**: Critical → High → Medium → Low
5. **Generate summary statistics**: findings count, dimension breakdown

### 4. Present Consolidated Report

```markdown
## Code Review Report: {target}

**Reviewed by**: security, performance, architecture
**Files reviewed**: {N}
**Total findings**: {N} (Critical: X, High: Y, Medium: Z, Low: W)

### Critical Findings
[findings...]

### High Findings
[findings...]

### Summary & Recommendations
[top priorities, quick wins, systemic patterns]
```

## Finding Severity Definitions

| Severity     | Meaning                                            | Action              |
|--------------|----------------------------------------------------|---------------------|
| **Critical** | Exploitable vulnerability, data loss, crash in prod | Fix before merge   |
| **High**     | Significant risk, major perf issue, broken contract | Fix before merge   |
| **Medium**   | Code smell, minor risk, suboptimal pattern          | Fix or justify     |
| **Low**      | Nit, style preference, minor improvement            | Optional fix       |

## Pitfalls

- **Reviewer modifying files** — Reviewers are read-only. If a reviewer proposes a fix, that is a suggestion only. Implementation is separate.
- **Overlapping findings** — When 2+ reviewers flag the same line, deduplicate and credit all dimensions. Do not report the same issue twice.
- **Severity inflation** — Not every issue is Critical. Reserve Critical for exploitable or data-loss issues only.
- **Missing file:line** — Any finding without a file:line citation should be treated as Low severity regardless of the reviewer's stated severity.
- **Reviewer times out** — If one reviewer times out, proceed with remaining results; note the missing dimension in the report header.
