# Musketeers Repository Agent Instructions

This repository is a Hermes profile distribution. Keep it installable and
accurate — do not describe planned capabilities as implemented.

## Hard rules

1. Never commit secrets. `.env` is forbidden. `.env.EXAMPLE` is allowed.
2. Keep `distribution.yaml` at the repository root with all required fields.
3. Keep the profile installable via `hermes profile install github.com/dxas90/hermes-musketeers`.
4. Do not commit files in `.gitignore` (`memories/`, `sessions/`, `logs/`,
   state databases, `.env`, caches).
5. SKILL.md frontmatter must include `name`, `description`, `version`, `author`,
   `license`, and `metadata.hermes.tags`. Directory name must match `name:`.
   No top-level `tags:` field.
6. Run validation before pushing:
   ```bash
   python3 .github/validate-profile.py
   ```

## Validation (full)

```bash
python3 .github/validate-profile.py
```

This checks YAML parse, distribution.yaml required fields, all SKILL.md
frontmatter (author, license, metadata.hermes.tags, dir-name match), and
secret patterns.

## Skill authoring rules

- Skill `name:` must be unique across all `skills/**/SKILL.md`.
- Directory name under `skills/<category>/` must exactly match the `name:` field.
- Tags live in `metadata.hermes.tags` (list), not top-level `tags:`.
- Related skills listed in `metadata.hermes.related_skills` must exist.
- Body should be under 500 lines.

## Version discipline

Any change to skills, SOUL.md, config.yaml, or memories/MEMORY.md constitutes
a distribution change. Bump `distribution.yaml` version (semver) and add a
matching `## <version>` entry to `CHANGELOG.md`.

## Git

- Branch naming: `feature/<desc>`, `fix/<desc>`, `docs/<desc>`.
- Squash merge to `main`.
- Do not force-push or rewrite history on `main`.
