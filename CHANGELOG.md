# Changelog

All notable changes to the Musketeers profile distribution.

Format: `## <version> — <date>`
Entries: Added / Changed / Fixed / Removed

---

## 1.2.0 — 2026-07-15

### Added
- `musketeers-scope-router` — route every request to cheapest team path before
  spawning (ported from codegraphtheory/heavy-coder)
- `musketeers-explore-first` — batch ground-truth reads before any delegation
- `musketeers-ship-gate` — completion gate with real exit codes before done
- `musketeers-context-budget` — token discipline: batch I/O, cap logs, phase-only
  skill loading
- `.hermes.md` — per-turn coordinator routing rules loaded by Hermes for
  installed profiles
- `AGENTS.md` — agent instructions for working on this repository
- `CONTRIBUTING.md` — local setup, contribution rules, PR workflow
- `SECURITY.md` — security policy and boundaries
- `CHANGELOG.md` — this file
- `.github/pull_request_template.md` — PR checklist (validation, version discipline)
- `.github/ISSUE_TEMPLATE/bug.yml` and `feature.yml`
- `.github/dependabot.yml` — weekly GitHub Actions version updates

### Changed
- `musketeers-orchestration` — 6-section leaf brief contract replaces flat context
  strings; evidence-based synthesis with ship-gate reference
- `SOUL.md` — fixed skill reference `claude-code` → `hermes-agent`
- `config.yaml` — delegation model/provider/reasoning_effort set (was silent inherit)
- `memories/MEMORY.md` — added `industry-security-standards` and 4 new skills
- `README.md` — documented new skills, fixed dir tree indent, fixed frontmatter spec
  in Contributing section
- `.github/validate-profile.py` — aligned with CI: `author`, `license`,
  `metadata.hermes.tags`, dir-name match, `yaml.safe_load`

---

## 1.1.1 — initial public release

- Dumas orchestrator persona with Athos / Porthos / Aramis / DArtagnan team
- Skills: musketeers-karpathy, musketeers-orchestration, musketeers-review,
  musketeers-debug, musketeers-feature, musketeers-docs, musketeers-workspace,
  systematic-debugging, requesting-code-review, plan, jira-cli,
  industry-security-standards
- Musketeers skin (gold/bronze theme, ASCII hero)
- CI workflow: YAML lint, distribution.yaml validation, SKILL.md frontmatter,
  secret scan, directory layout
