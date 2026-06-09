# Parallel Debugging — Full Procedure

Hypothesis-driven debugging using Porthos agents via `delegate_task`. Based on Analysis of Competing Hypotheses (ACH) methodology.

## When to Use

When a bug's root cause is unknown and multiple explanations are plausible. Running investigators in parallel against competing hypotheses is faster and more reliable than sequential debugging.

## Step 1 — Triage

Before spawning agents, collect context yourself:

```bash
# Recent changes in the affected area
git log --oneline -20 -- src/affected_module/

# Find related error messages
grep -r "the error string" src/

# Check related tests
find . -name "test_*.py" | xargs grep "FunctionName"

# If stack trace available, read the top frames
```

Identify clearly: **what is failing**, **when**, **how reproducibly**, and **what changed recently**.

## Step 2 — Generate Hypotheses

Generate N hypotheses covering different failure categories. Each must be specific and falsifiable.

| Category | Example Hypothesis |
|---|---|
| Logic Error | "The pagination offset calculation is off-by-one when page=0 is passed" |
| Data Issue | "NULL user_id is not handled in the JOIN — returns empty set instead of error" |
| State Problem | "Redis cache is not invalidated on user update — stale data served for up to 5 min" |
| Integration Failure | "Library upgraded from v2 to v3 changed the error format — our parser still expects v2" |
| Resource Issue | "Database connection pool exhausted under concurrent load — requests queue until timeout" |
| Environment | "CI uses Python 3.9, dev uses 3.11 — walrus operator behavior differs in edge case" |

**Rule:** "Something is wrong with auth" is NOT a hypothesis. "JWT token is not validated on the /admin/users endpoint — any token passes" IS.

Present hypotheses to the user: "Generated {N} hypotheses. Investigate in parallel?"

## Step 3 — Spawn Porthos Investigators

```python
hypotheses = [
    "Redis cache is not invalidated on user update — stale profile data served for up to 5 minutes",
    "Input validation missing on the POST /users payload — null email field crashes the email sender",
    "Database connection pool exhaustion under concurrent load — requests queue past the 30s timeout",
]

bug_context = """
Bug report: POST /users endpoint intermittently returns 500 with no body
Frequency: ~1 in 50 requests under load
Stack trace (when available): [paste here]
Recent changes: [list relevant commits]
Affected files: [list suspected files]
"""

tasks = [
    {
        "goal": f"""You are Porthos, a hypothesis-driven debugging investigator.

ASSIGNED HYPOTHESIS: {h}

Investigation protocol — follow in order:
1. Identify what must be true for this hypothesis to be correct
2. List observable consequences if this hypothesis IS the root cause
3. Search for CONFIRMING evidence — cite file:line for every claim
4. Search for FALSIFYING evidence — cite file:line for every contradicting observation
5. Assess confidence: High (>80%), Medium (50-80%), Low (<50%)
6. If confidence is High or Medium, propose the minimal fix

SCOPE DISCIPLINE: Investigate your hypothesis only. If you discover evidence pointing to a different root cause, mention it briefly but do not change your investigation focus.

Return this EXACT structure:
HYPOTHESIS: {h}
STATUS: Confirmed | Falsified | Inconclusive
CONFIDENCE: High | Medium | Low

CONFIRMING EVIDENCE:
- file.py:42 — description of what this shows
(list all, or "None found")

FALSIFYING EVIDENCE:
- file.py:99 — description of what this contradicts
(list all, or "None found")

EVIDENCE GAPS: (conditions you couldn't verify)

CAUSAL CHAIN: (if Confirmed)
  symptom ← immediate cause ← root cause

PROPOSED FIX: (if Confirmed — minimal change only)

OTHER ROOT CAUSES NOTICED: (brief, do not investigate)

Bug context:
{bug_context}""",
        "context": f"Debug hypothesis: {h[:80]}. Evidence-based investigation, file:line citations required.",
        "toolsets": ["terminal"],
    }
    for h in hypotheses
]

investigation_results = delegate_task(
    goal="Parallel hypothesis investigation. Collect all evidence reports.",
    context="Debug session. Investigators work independently. Consolidate after.",
    toolsets=["terminal"],
    tasks=tasks,
)
```

## Step 4 — Arbitrate Results

Compare all investigation reports:

1. **Rank confirmed hypotheses** by:
   - Confidence level: High > Medium > Low
   - Strength of causal chain (complete cause→symptom chain beats partial)
   - Volume of supporting evidence
   - Absence of contradicting evidence

2. **Falsified hypotheses** — valuable! They eliminate possibilities. Note them.

3. **Inconclusive hypotheses** — decide whether to investigate further or treat as unlikely.

4. **Cross-hypothesis clues** — "Other Root Causes Noticed" sections may reveal a hypothesis worth adding.

## Step 5 — Present Root Cause Analysis

```
## Debug Report: {error description}

### Root Cause (Most Likely)
**Hypothesis**: {description}
**Confidence**: High
**Evidence**: {key evidence with file:line citations}
**Causal Chain**: stale cache ← no invalidation on UPDATE ← missing call in user_service.py:87

### Recommended Fix
{specific code change with before/after}

### Other Hypotheses
- {hypothesis 2}: Falsified — users.py:34 shows null check exists (line 34)
- {hypothesis 3}: Inconclusive — could not reproduce under test load
```

## Step 6 — Verify the Fix

After applying the fix, run a second round:

```python
delegate_task(
    goal="""Verify that the following fix correctly addresses the root cause.
Do NOT verify anything else — only confirm this specific fix resolves the identified issue.

Root cause: {root_cause_description}
Fix applied: {fix_description}
Changed files: {file_list}

Verify:
1. The causal chain is broken by the fix
2. No new issues are introduced
3. Tests cover the fixed path (or document that they don't)

Return: VERIFIED or NOT VERIFIED with evidence.""",
    context="Fix verification only. Narrow scope.",
    toolsets=["terminal"],
)
```

## Common Pitfalls

1. **Vague hypotheses** — "The auth module is broken" spawns an unfocused investigation. Specify the exact mechanism.

2. **Hypotheses that are too similar** — Three variations of "missing null check" waste three agent runs. Cover different failure categories.

3. **Missing bug context** — Porthos starts with zero knowledge. Include the stack trace, error message, recent git log, and affected files in `bug_context`.

4. **Ignoring falsifying evidence** — A confident "Confirmed" with no falsifying evidence search is suspect. Good investigators look for both.

5. **Too many hypotheses** — 3-4 is optimal. Beyond 5, the probability any single one is correct drops, and consolidation becomes harder.
