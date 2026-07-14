---
name: musketeers-debug
description: "Hypothesis-driven parallel debugging using Analysis of Competing Hypotheses (ACH). Spawn multiple investigators (Porthos), each assigned one hypothesis. Load when debugging complex issues with multiple potential root causes."
version: 1.0.0
tags: [musketeers, debug, porthos, debugging, root-cause]
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [musketeers, debug, porthos, debugging, root-cause]
    related_skills: [systematic-debugging, musketeers-orchestration, musketeers-review]
---

# Musketeers Parallel Debugging

Debug complex issues using the Analysis of Competing Hypotheses (ACH) methodology with parallel investigation sub-agents (Porthos).

## When to Use

- Bug has multiple plausible root causes
- Initial debugging attempts haven't identified the issue
- Issue spans multiple modules or components
- Need systematic root cause analysis with evidence
- Want to avoid confirmation bias

## Hypothesis Generation

Generate hypotheses across 6 failure mode categories:

| Category             | Examples                                                      |
|----------------------|---------------------------------------------------------------|
| **Logic Error**      | Wrong condition, off-by-one, missing edge case                |
| **Data Issue**       | Invalid input, type mismatch, null/undefined, encoding        |
| **State Problem**    | Race condition, stale cache, incorrect init, mutation          |
| **Integration**      | API contract violation, version mismatch, config error         |
| **Resource Issue**   | Memory leak, connection exhaustion, timeout, disk full         |
| **Environment**      | Missing dependency, wrong version, platform-specific           |

**Rule**: Generate 3 hypotheses by default (covering different categories). User can request more.

## Workflow

### 1. Initial Triage

- Analyze the error: what's failing, when, how
- Gather context: recent git changes, related tests, logs
- Identify the symptom clearly

### 2. Generate Hypotheses

For each hypothesis, define:
- **Statement**: What the root cause is (specific and testable)
- **Category**: Which failure mode category
- **Confirming evidence**: What would prove it true
- **Falsifying evidence**: What would disprove it

### 3. Spawn Investigators (Parallel)

```
delegate_task(tasks=[
  {
    "goal": "Investigate hypothesis: '{hypothesis_1}'. Gather evidence to confirm or falsify.",
    "context": "You are Porthos, a hypothesis-driven debugger.\n\nBug symptoms: {description}\nHypothesis: {statement}\nCategory: {category}\n\nInvestigation protocol:\n1. Identify what must be true for this hypothesis to be correct\n2. Search for confirming evidence (file:line citations)\n3. Search for contradicting evidence\n4. Assess confidence: High (>80%), Medium (50-80%), Low (<50%)\n5. If confirmed, provide causal chain from root cause to symptom\n6. If confirmed, suggest specific fix\n\nEvidence standards:\n- Always cite file:line\n- Show causal chain\n- Report confidence honestly\n- Include contradicting evidence\n- Scope your claims precisely",
    "toolsets": ["terminal", "file"]
  },
  { "goal": "Investigate hypothesis: '{hypothesis_2}'...", ... },
  { "goal": "Investigate hypothesis: '{hypothesis_3}'...", ... }
])
```

### 4. Arbitrate Results

After all investigators report:

1. **Compare confidence levels** across hypotheses
2. **Check for convergence** — Do multiple investigators point at the same code?
3. **Evaluate evidence quality** — Direct (code proves it) vs circumstantial (consistent but not proof)
4. **Identify the winner**:
   - Highest confidence + strongest evidence = most likely root cause
   - If no clear winner, recommend additional investigation
5. **Present verdict** with causal chain and suggested fix

### 5. Report Format

```markdown
## Debug Report: {issue}

### Verdict
**Root Cause**: {winning hypothesis}
**Confidence**: {High/Medium/Low}
**Location**: {file:line}

### Causal Chain
1. {cause} → 2. {intermediate} → 3. {symptom}

### Suggested Fix
{specific code change}

### Evidence Summary
| Hypothesis | Confidence | Key Evidence |
|------------|-----------|--------------|
| {H1}       | High      | file:42 shows... |
| {H2}       | Low       | Contradicted by... |
| {H3}       | Medium    | Consistent but... |

### Eliminated Hypotheses
- {H2}: Falsified because {evidence}
- {H3}: Insufficient evidence, lower confidence
```

## Evidence Quality Scale

| Type           | Strength | Example                                            |
|----------------|----------|----------------------------------------------------|
| **Direct**     | Strong   | Code at file:42 shows the wrong comparison         |
| **Reproducing**| Strong   | Test case triggers the exact symptom                |
| **Correlating**| Medium   | Recent commit changed the suspected area           |
| **Absence**    | Medium   | Expected validation is missing                     |
| **Inferential**| Weak     | Similar pattern caused bugs elsewhere              |

### Low-Confidence Escalation

When ALL investigators return Low confidence (<50%):

1. **Do not guess** — present the evidence gap honestly
2. **Request instrumentation**: Ask the user to add logging at key boundaries
3. **Reduce scope**: Ask the user for a minimal reproduction case
4. **Widen hypotheses**: Generate 2 additional hypotheses from uncovered categories
5. **Escalate if still stuck**: Report the investigation results and ask the user what additional context they can provide

Never present a Low-confidence winner as the root cause. Always flag confidence explicitly.
