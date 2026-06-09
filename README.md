# hermes-musketeers

A Hermes profile distribution that turns your agent into **Dumas** — a multi-agent orchestrator that decomposes complex software engineering tasks into parallel workstreams and synthesizes results using `delegate_task`.

## What it does

Provides four specialist personas you can spawn as subagents:

| Persona | Role | Toolset |
|---|---|---|
| **Athos** | Code reviewer — one quality dimension per run (security, performance, architecture, testing, accessibility) | read-only |
| **Porthos** | Hypothesis investigator — gathers confirming and falsifying evidence for one assigned hypothesis | read-only |
| **Aramis** | Feature builder — implements within strict file ownership boundaries | read-write |
| **DArtagnan** | Documentation specialist — reads source to write accurate docs | read-write |

And four ready-to-use workflows via skills:

- **`musketeers`** — parallel code review, hypothesis debugging, feature builds, docs generation
- **`requesting-code-review`** — pre-commit verification pipeline with independent reviewer subagent
- **`systematic-debugging`** — structured root cause analysis
- **`plan`** — upfront decomposition before implementation

## Requirements

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) installed
- An LLM provider configured in your environment (`ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, etc.)

## Installation

```bash
hermes profile install github.com/dxas90/hermes-musketeers --alias musketeers
```

Then start it:

```bash
musketeers chat
```

Or without an alias:

```bash
hermes -p musketeers chat
```

## Configuration

The profile defaults to `claude-sonnet-4-6` via Anthropic. Update `config.yaml` to match your provider:

```yaml
model:
  default: claude-sonnet-4-6   # your preferred model
  provider: anthropic          # anthropic | openrouter | ollama | ...
```

For delegation (the subagents spawned by `delegate_task`), you can use a lighter model:

```yaml
delegation:
  model: claude-haiku-4-5-20251001
  provider: anthropic
  max_concurrent_children: 3
  max_iterations: 50
```

## Updates

```bash
hermes profile update musketeers
```

## Usage

Once the profile is active, invoke workflows naturally:

```
# Parallel code review
Review the current diff across security, performance, and architecture dimensions

# Hypothesis-driven debugging
Debug this error: POST /users returns 500 intermittently under load

# Parallel feature development
Build user authentication with OAuth2 — decompose into parallel streams

# Documentation
Write a README for this project based on the source code
```

Or load a skill explicitly:

```
/skill musketeers
```

## Profile structure

```
~/.hermes/profiles/musketeers/
├── distribution.yaml                # Distribution manifest
├── SOUL.md                          # Dumas persona — the orchestrator identity
├── config.yaml                      # Model, provider, delegation settings
├── skills/
│   ├── software-development/
│   │   ├── musketeers/              # Main skill — all four workflows
│   │   │   ├── SKILL.md
│   │   │   └── references/
│   │   │       ├── team-review.md
│   │   │       ├── parallel-debugging.md
│   │   │       └── parallel-feature.md
│   │   ├── requesting-code-review/
│   │   ├── systematic-debugging/
│   │   └── plan/
│   └── autonomous-ai-agents/
│       └── hermes-agent/
├── cron/
└── hooks/
```

## License

MIT
