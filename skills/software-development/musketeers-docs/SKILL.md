---
name: musketeers-docs
description: "Documentation generation via DArtagnan — README, API references, architecture guides, setup guides, troubleshooting. Load when the user needs documentation written or updated based on existing code."
version: 1.0.0
tags: [musketeers, docs, dartagnan, documentation, writing]
---

# Musketeers Documentation (DArtagnan)

Spawn a DArtagnan sub-agent to read source code directly and produce accurate, audience-appropriate documentation.

## When to Use

- After a feature ships and needs documentation
- Onboarding docs are missing
- API reference is outdated
- Architecture overview needed
- README needs refresh after changes

## Document Types

| Type | Purpose | Audience |
|------|---------|----------|
| **README** | Entry point: what/quickstart/features/config | Everyone |
| **API Reference** | Per-endpoint docs: params, responses, errors, examples | Integrators |
| **Architecture** | Components, responsibilities, data flow, dependencies | Engineers |
| **Setup Guide** | Prerequisites, install, config, first run | New contributors |
| **Troubleshooting** | Common failures, symptoms, causes, fixes | Operators |

## Delegation Pattern

```python
delegate_task(
    goal="Write {doc_type} documentation for {subject}.",
    context="""You are DArtagnan, a technical documentation specialist.

SOURCE FILES TO READ (read these first — do NOT invent APIs):
{file_list}

DOCUMENT TYPE: {type}
AUDIENCE: {audience}
OUTPUT FILE: {output_path}

WRITING STANDARDS:
- Simple words: "use" not "utilize", "start" not "commence"
- Active voice: "Run the server" not "The server should be run"
- Concrete examples that actually run — no pseudocode
- Short sentences, numbered steps for sequences
- Start with "why" before "how"
- Every code example must work without modification
- Verify file paths, command names, config keys are accurate

WORKFLOW:
1. Read all source files to understand actual behavior
2. Outline: what sections, what order
3. Write: why → how, with working examples
4. Verify: check all paths/commands are real
5. Report: files written + any undocumented areas found

DO NOT:
- Invent features that don't exist in the code
- Add placeholder text ("TODO", "Coming soon")
- Document internal implementation details unless architecture doc
- Use jargon the audience wouldn't know""",
    toolsets=["terminal", "file"]
)
```

## Quality Checklist

Before accepting DArtagnan's output:
- [ ] Every code example is runnable
- [ ] All file paths and commands exist
- [ ] Matches current code behavior (not stale)
- [ ] Appropriate for stated audience
- [ ] No invented/assumed APIs
- [ ] Links resolve
