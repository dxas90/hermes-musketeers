---
name: musketeers-review
description: "Multi-reviewer parallel code review across quality dimensions (security, performance, architecture, testing, accessibility). Load when the user asks for a code review or '/team-review' style workflow."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [musketeers, review, athos, code-quality, parallel]
    related_skills: [musketeers-debug, musketeers-feature, musketeers-orchestration, requesting-code-review, industry-security-standards]
---

# Musketeers Multi-Reviewer Code Review

Orchestrate parallel code reviews where each sub-agent (Athos) focuses on a specific quality dimension, then consolidate into a prioritized report.

## When to Use

- User asks for code review of a file, directory, diff, or PR
- Multiple quality dimensions are relevant (security + performance + architecture)
- Review needs structured, actionable findings with severity ratings

## Review Dimensions

| Dimension         | Focus Areas                                                                                     | When to Include                          |
|-------------------|-------------------------------------------------------------------------------------------------|------------------------------------------|
| **Security**      | Input validation, auth, injection, secrets, CVEs, crypto, container hardening, data privacy     | Always — Security is NEVER optional      |
| **Performance**   | N+1 queries, memory leaks, caching, async, O(n²)                                               | Data access or hot paths                 |
| **Architecture**  | SOLID, coupling, layering, error handling, API design                                           | Structural changes or new modules        |
| **Testing**       | Coverage gaps, isolation, mocks, edge cases, assertions                                         | New functionality                        |
| **Accessibility** | WCAG 2.1 AA, ARIA, keyboard nav, contrast, focus mgmt                                          | UI/frontend changes                      |

## Recommended Combinations

**Security is ALWAYS included. It is never optional — even when not explicitly requested.**

| Scenario               | Dimensions                                     |
|------------------------|------------------------------------------------|
| API endpoint changes   | Security, Performance, Architecture            |
| Frontend component     | Security, Architecture, Testing, Accessibility |
| Database migration     | Security, Performance, Architecture            |
| Authentication changes | Security, Testing                              |
| Full feature review    | Security, Performance, Architecture, Testing   |
| Any other change       | Security + relevant dimensions                 |

## Workflow

### 1. Determine Target & Scope

Identify what to review:
- **File/directory path** → review those files
- **Git diff** (`main...HEAD`) → `git diff --name-only` for changed files
- **PR number** → `gh pr diff {N} --name-only`

### 2. Spawn Reviewers (Parallel Delegation)

For each dimension, delegate to a sub-agent playing the Athos role. The Security
reviewer context below is mandatory and must not be trimmed:

```
delegate_task(tasks=[
  {
    "goal": "Review the following code for SECURITY issues. Load skill_view(name='industry-security-standards') before reviewing. Map every finding to a specific standard (OWASP Top 10, CWE, NIST). Flag any gaps in mandatory obligations as at least High severity.",
    "context": "You are Athos, a specialized code reviewer focused on Security.\n\nSTEP 1 — Before reviewing any code:\n  Load skill_view(name='industry-security-standards') and read it fully.\n  That skill defines the exact standards to check against.\n\nSTEP 2 — Run the non-negotiable checklist against every file:\n  - No hardcoded secrets, tokens, or credentials\n  - No InsecureSkipVerify:true or TLS verification bypasses\n  - No PII or sensitive data in log output, traces, or error responses\n  - All K8s list calls paginated (Limit + Continue) — no unbounded lists\n  - All async consumers have bounded in-flight queue sizes\n  - context.Context propagated to goroutines — no context.Background() in long-lived paths\n  - RBAC grants use minimal explicit verbs — no wildcards\n  - Container: runAsNonRoot, allowPrivilegeEscalation:false, capabilities.drop:ALL\n  - Resource limits (CPU + memory) set on every container\n  - CI actions pinned to digest (not mutable tag)\n\nSTEP 3 — Review the code against OWASP Top 10, CWE Top 25, NIST SP 800-53:\n  Target files:\n  {file_list}\n\nFor each finding use this format:\n### [SEVERITY] Finding Title\n**Location**: path/to/file.go:42\n**Dimension**: Security\n**Severity**: Critical | High | Medium | Low\n**Standard**: OWASP A03:2021 / CWE-89 (cite the specific standard)\n**Evidence**: What was found in the code.\n**Impact**: What could go wrong.\n**Recommended Fix**: Specific remediation with code example where useful.\n\nSeverity rules:\n- Critical: exploitable, data loss, or credential exposure\n- High: significant risk, broken security contract\n- Medium: suboptimal pattern, minor risk\n- Low: nit or hardening improvement\n\nCite file:line for every finding. Stay strictly within the Security dimension.",
    "toolsets": ["terminal", "file"]
  },
  {
    "goal": "Review the following code for PERFORMANCE issues...",
    "context": "You are Athos, a specialized code reviewer focused on Performance.\n\nTarget files:\n{file_list}\n\nFor each finding:\n### [SEVERITY] Finding Title\n**Location**: path/to/file:line\n**Dimension**: Performance\n**Severity**: Critical | High | Medium | Low\n**Evidence**: What was found.\n**Impact**: What could go wrong.\n**Recommended Fix**: Specific remediation.\n\nFocus: N+1 queries, memory leaks, caching, async bottlenecks, O(n²) loops, unbounded allocations.",
    "toolsets": ["terminal", "file"]
  },
  {
    "goal": "Review the following code for ARCHITECTURE issues...",
    "context": "You are Athos, a specialized code reviewer focused on Architecture.\n\nTarget files:\n{file_list}\n\nFor each finding:\n### [SEVERITY] Finding Title\n**Location**: path/to/file:line\n**Dimension**: Architecture\n**Severity**: Critical | High | Medium | Low\n**Evidence**: What was found.\n**Impact**: What could go wrong.\n**Recommended Fix**: Specific remediation.\n\nFocus: SOLID violations, tight coupling, missing error handling, layering violations, API design issues, goroutine lifecycle (context.Background() anti-pattern), graceful shutdown gaps.",
    "toolsets": ["terminal", "file"]
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

| Severity     | Meaning                                             | Action             |
|--------------|-----------------------------------------------------|--------------------|
| **Critical** | Exploitable vulnerability, data loss, crash in prod | Fix before merge   |
| **High**     | Significant risk, major perf issue, broken contract | Fix before merge   |
| **Medium**   | Code smell, minor risk, suboptimal pattern          | Fix or justify     |
| **Low**      | Nit, style preference, minor improvement            | Optional fix       |

## Pitfalls

- **Skipping Security** — Security is NEVER optional. Always spawn a Security Athos, always load industry-security-standards, always run the checklist.
- **Reviewer modifying files** — Reviewers are read-only. Proposed fixes are suggestions only; implementation is a separate step.
- **Overlapping findings** — When 2+ reviewers flag the same line, deduplicate and credit all dimensions. Do not report the same issue twice.
- **Severity inflation** — Not every issue is Critical. Reserve Critical for exploitable or data-loss issues only.
- **Missing file:line** — Any finding without a file:line citation should be treated as Low severity regardless of stated severity.
- **Reviewer times out** — Proceed with remaining results; note the missing dimension in the report header.

### Scoping Second-Pass Reviews

When running a second Athos pass on the same code, explicitly tell reviewers which
findings were already accepted in the prior round and must not be re-raised. Without
this filter, reviewers repeat known findings, burying net-new regressions.

Include in context: `"Known issues already accepted (do NOT re-raise): {list}"` and
set scope to: `"Only report regressions introduced by THIS round, or new Critical/High
issues not present in the original code."`
