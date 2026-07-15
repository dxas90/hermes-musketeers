# Security Policy

## Supported versions

The `main` branch is the only supported line. Install via
`hermes profile install github.com/dxas90/hermes-musketeers` for the latest.

## Reporting vulnerabilities

Please report security issues privately via GitHub Security Advisories, or
contact the maintainer through the repository. Do not open a public issue
for exploitable vulnerabilities.

## Security boundaries

- This is a Hermes profile distribution — it contains skills, config, and a
  SOUL persona. It does not execute code autonomously or make network calls on
  its own.
- The profile respects `approvals.mode: manual` — all shell commands require
  user approval unless explicitly changed.
- `security.redact_secrets: true` is set in `config.yaml`.
- Do not store secrets in `memories/MEMORY.md` or any tracked file. Use
  `$ENV_VAR (.env)` references instead.
- Credential files (`.env`, `auth.json`) are covered by `.gitignore`.

## Best practices for users

- Review `config.yaml` before deploying to a shared or automated environment.
- Keep `approvals.mode: manual` on developer workstations.
- Rotate any credential immediately if accidentally committed; then clean history.
