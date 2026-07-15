# Contributing

Thanks for helping improve the Musketeers profile.

## Local setup

No Python package install needed — just pyyaml for validation:

```bash
pip install pyyaml
```

Or use the system Python if pyyaml is already available.

## Required checks before pushing

```bash
python3 .github/validate-profile.py
```

This runs:
- YAML parse of `distribution.yaml`, `config.yaml`, `skins/musketeers.yaml`
- SKILL.md frontmatter validation (name, description, version, author, license,
  metadata.hermes.tags, dir-name match, no top-level tags:)
- Secret pattern scan across tracked files

## Contribution rules

- Keep external dependencies minimal (the profile has none at runtime).
- Add skills under `skills/<category>/<skill-name>/SKILL.md`.
- Skill `name:` must match its directory name exactly.
- Tags belong in `metadata.hermes.tags`, not top-level `tags:`.
- `related_skills` entries must exist in the repo.
- Body under 500 lines per skill.
- Any change to skills, SOUL.md, config.yaml, or memories/MEMORY.md is a
  distribution change: bump `distribution.yaml` version (semver) and add
  a matching `## <version>` entry to `CHANGELOG.md`.
- Do not commit `memories/`, `sessions/`, `logs/`, `.env`, or state databases
  (covered by `.gitignore`).
- Do not describe planned capabilities as implemented.

## Branch and PR workflow

1. Fork and create a `feature/<desc>` or `fix/<desc>` branch.
2. Make changes, run `python3 .github/validate-profile.py`.
3. Open a PR against `main` — CI validates YAML and frontmatter automatically.
4. Squash merge is the default.

## Testing a skill locally

Load a skill in a live Hermes session:

```
/skill <skill-name>
```

Or trigger naturally via a task that matches the skill's trigger conditions.
