#!/usr/bin/env python3
"""Local profile validator for hermes-musketeers.

Runs the same checks as .github/workflows/validate.yml so contributors
can verify locally before pushing.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - depends on environment
    yaml = None


ROOT = Path(__file__).resolve().parent.parent
REQUIRED_SKILL_FRONTMATTER = {"name", "description", "version", "author", "license"}
SECRET_PATTERN = re.compile(
    r"(api_key|secret|password|token)\s*=\s*['\"][^'\"]{8,}['\"]",
    re.IGNORECASE,
)


def check_yaml_files() -> bool:
    """Parse the main YAML files to ensure they're valid."""
    yaml_files = ["distribution.yaml", "config.yaml", "skins/musketeers.yaml"]
    if yaml is None:
        print("SKIP: pyyaml is not installed; YAML parse checks are skipped.")
        return True

    ok = True
    for name in yaml_files:
        path = ROOT / name
        try:
            with path.open("r", encoding="utf-8") as fh:
                yaml.safe_load(fh)
            print(f"OK: {name}")
        except Exception as exc:  # pragma: no cover
            print(f"ERROR: {name}: {exc}", file=sys.stderr)
            ok = False
    return ok


def check_skill_frontmatter() -> bool:
    """Ensure every SKILL.md has required YAML frontmatter (mirrors CI checks)."""
    errors: list[str] = []
    skills_dir = ROOT / "skills"
    skill_files = list(skills_dir.rglob("SKILL.md"))
    for path in skill_files:
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            errors.append(f"{path}: missing YAML frontmatter")
            continue
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            errors.append(f"{path}: malformed frontmatter")
            continue
        frontmatter_raw = match.group(1)

        # Parse with yaml if available, else fall back to regex
        if yaml is not None:
            try:
                fm = yaml.safe_load(frontmatter_raw)
            except Exception as exc:
                errors.append(f"{path}: frontmatter YAML parse error: {exc}")
                continue
            if not isinstance(fm, dict):
                errors.append(f"{path}: frontmatter is not a YAML mapping")
                continue
            found = set(fm.keys())
        else:
            found = set(re.findall(r"^(\w+):", frontmatter_raw, re.MULTILINE))
            fm = None

        missing = REQUIRED_SKILL_FRONTMATTER - found
        if missing:
            errors.append(f"{path}: missing fields: {missing}")

        # top-level tags: is wrong per spec — must be metadata.hermes.tags
        if "tags" in found:
            errors.append(f"{path}: top-level 'tags:' found — move to metadata.hermes.tags")

        # metadata.hermes.tags must exist and be a non-empty list
        if yaml is not None and fm is not None:
            meta = fm.get("metadata")
            if not isinstance(meta, dict) or "hermes" not in meta:
                errors.append(f"{path}: missing metadata.hermes block")
            else:
                hermes_meta = meta["hermes"]
                tags = hermes_meta.get("tags") if isinstance(hermes_meta, dict) else None
                if not tags or not isinstance(tags, list):
                    errors.append(f"{path}: metadata.hermes.tags must be a non-empty list")
        else:
            # regex fallback: look for hermes: block with tags
            if not re.search(r"hermes:\s*\n\s+tags:", frontmatter_raw):
                errors.append(f"{path}: missing metadata.hermes.tags block")

        # directory name must match skill name field
        skill_dir_name = path.parent.name
        if yaml is not None and fm is not None:
            skill_name = fm.get("name", "")
        else:
            m2 = re.search(r"^name:\s*(.+)$", frontmatter_raw, re.MULTILINE)
            skill_name = m2.group(1).strip() if m2 else ""
        if skill_name and skill_dir_name != skill_name:
            errors.append(f"{path}: directory '{skill_dir_name}' does not match skill name '{skill_name}'")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return False
    print(f"OK: {len(skill_files)} SKILL.md files checked")
    return True


def check_no_secrets() -> bool:
    """Scan text files for obvious hardcoded secrets."""
    extensions = {".yaml", ".yml", ".md", ".json", ".toml", ".txt"}
    errors: list[str] = []
    for path in ROOT.rglob("*"):
        if path.is_dir() or path.suffix.lower() not in extensions:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if SECRET_PATTERN.search(text):
            errors.append(f"{path}: possible hardcoded secret")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return False
    print("OK: no obvious secrets detected")
    return True


def main() -> int:
    print("Validating hermes-musketeers profile...")
    checks = [check_yaml_files, check_skill_frontmatter, check_no_secrets]
    results = [check() for check in checks]
    if all(results):
        print("All validators passed.")
        return 0
    print("Validation failed.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
