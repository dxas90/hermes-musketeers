## Summary

<!-- What does this PR change and why? -->

## Verification

- [ ] `python3 .github/validate-profile.py` passes locally
- [ ] No secrets in diff (`git diff --cached | grep -iE 'api_key|token|password'`)

## Skills (if adding/changing skills)

- [ ] Frontmatter includes `name`, `description`, `version`, `author`, `license`
- [ ] Tags are under `metadata.hermes.tags` (not top-level `tags:`)
- [ ] Directory name matches `name:` field
- [ ] `related_skills` entries exist in the repo

## Distribution version discipline

- [ ] I changed no profile files, OR I bumped `distribution.yaml` version
- [ ] `CHANGELOG.md` has a matching `## <version>` entry for any version bump

## Safety

- [ ] No secrets committed
- [ ] Planned capabilities are not described as implemented unless true
