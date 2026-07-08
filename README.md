# hermes-musketeers

A Hermes profile distribution that turns your agent into **Dumas** — a multi-agent orchestrator that decomposes complex software engineering tasks into parallel workstreams and synthesizes results using `delegate_task`.

> Adapted from the [musketeers](https://github.com/dxas90/opsy-bag) Claude Code plugin — the same agent team patterns reimplemented for Hermes `delegate_task`.

## What it does

Provides four specialist personas you can spawn as subagents:

| Persona | Role | Toolset |
|---|---|---|
| **Athos** | Code reviewer — one quality dimension per run (security, performance, architecture, testing, accessibility) | read-only |
| **Porthos** | Hypothesis investigator — gathers confirming and falsifying evidence for one assigned hypothesis | read-only |
| **Aramis** | Feature builder — implements within strict file ownership boundaries | read-write |
| **DArtagnan** | Documentation specialist — reads source to write accurate docs | read-write |

And six ready-to-use workflow skills:

- **`musketeers-karpathy`** — behavioral discipline (think first, simplicity, surgical changes)
- **`musketeers-orchestration`** — team composition, sizing, delegation templates
- **`musketeers-review`** — parallel code review across quality dimensions
- **`musketeers-debug`** — hypothesis-driven parallel debugging (ACH methodology)
- **`musketeers-feature`** — parallel feature development with file ownership
- **`musketeers-docs`** — documentation generation via DArtagnan

Plus complementary skills:

- **`systematic-debugging`** — single-agent 4-phase root cause analysis
- **`requesting-code-review`** — pre-commit verification pipeline
- **`plan`** — upfront decomposition before implementation

## Requirements

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) installed
- An LLM provider configured in your environment (`ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, etc.)

## Installation

```bash
hermes profile install github.com/dxas90/hermes-musketeers --alias
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
├── skins/
│   └── musketeers.yaml              # Custom theme (gold/bronze, ASCII hero)
├── memories/
│   └── MEMORY.md                    # Persistent facts (team structure, git rules)
├── skills/
│   ├── software-development/
│   │   ├── musketeers-karpathy/     # Behavioral guidelines
│   │   ├── musketeers-review/       # Parallel code review (Athos)
│   │   ├── musketeers-debug/        # Hypothesis debugging (Porthos)
│   │   ├── musketeers-feature/      # Parallel builds (Aramis)
│   │   ├── musketeers-docs/         # Documentation (DArtagnan)
│   │   ├── requesting-code-review/  # Pre-commit review
│   │   ├── systematic-debugging/    # Root cause analysis
│   │   └── plan/                    # Plan-before-build
│   └── devops/
│       ├── musketeers-orchestration/ # Team composition & coordination
│       └── musketeers-workspace/    # Cross-repo task tracking
├── cron/
└── hooks/
```

## License

MIT
