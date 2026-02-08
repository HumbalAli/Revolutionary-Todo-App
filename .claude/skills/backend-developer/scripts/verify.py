#!/usr/bin/env python3
"""
Verification script for the backend-developer skill.
Checks that the skill follows proper structure and format.
"""

import os
import yaml
from pathlib import Path

def verify_skill(skill_path):
    """Verify that the skill is properly structured."""
    skill_path = Path(skill_path)

    # Check if SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"[ERROR] {skill_path.name}: SKILL.md file missing")
        return False

    # Read and parse SKILL.md
    content = skill_md.read_text()

    # Check for YAML frontmatter
    if not content.startswith("---\n"):
        print(f"[ERROR] {skill_path.name}: Missing YAML frontmatter")
        return False

    # Extract frontmatter
    parts = content.split("---", 2)
    if len(parts) < 3:
        print(f"[ERROR] {skill_path.name}: Invalid YAML frontmatter")
        return False

    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        print(f"[ERROR] {skill_path.name}: Invalid YAML in frontmatter")
        return False

    # Check required fields
    if "name" not in frontmatter:
        print(f"[ERROR] {skill_path.name}: Missing 'name' in frontmatter")
        return False

    if "description" not in frontmatter:
        print(f"[ERROR] {skill_path.name}: Missing 'description' in frontmatter")
        return False

    # Check description follows the "Use when" pattern
    description = frontmatter["description"]
    if not description.strip().startswith("Use when"):
        print(f"[ERROR] {skill_path.name}: Description should start with 'Use when'")
        return False

    # Check directory structure
    expected_dirs = ["scripts", "references", "assets"]
    for dir_name in expected_dirs:
        dir_path = skill_path / dir_name
        if not dir_path.exists():
            print(f"[WARN] {skill_path.name}: Optional directory {dir_name}/ missing")

    print(f"[SUCCESS] {skill_path.name} valid")
    return True

if __name__ == "__main__":
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else ".claude/skills/backend-developer"
    verify_skill(skill_path)