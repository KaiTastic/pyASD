#!/usr/bin/env python3
"""
Pre-commit hook to validate commit message format.

Validates that commit messages follow Conventional Commits format:
- type(scope): description
- Valid types: feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert

Reference: https://www.conventionalcommits.org/
"""

import re
import sys
from pathlib import Path


VALID_TYPES = [
    'feat',      # New feature
    'fix',       # Bug fix
    'docs',      # Documentation changes
    'style',     # Code style changes (formatting, etc.)
    'refactor',  # Code refactoring
    'test',      # Adding or updating tests
    'chore',     # Maintenance tasks
    'perf',      # Performance improvements
    'ci',        # CI/CD changes
    'build',     # Build system changes
    'revert',    # Revert previous commit
]


def validate_commit_message(message):
    """
    Validate commit message format.

    Expected format:
    - type: description
    - type(scope): description

    Returns (is_valid, error_message)
    """
    lines = message.strip().split('\n')
    if not lines:
        return False, "Commit message is empty"

    first_line = lines[0].strip()

    # Check for merge commits (allowed)
    if first_line.startswith('Merge '):
        return True, None

    # Check for revert commits (allowed)
    if first_line.startswith('Revert '):
        return True, None

    # Pattern 1: type: description
    # Pattern 2: type(scope): description
    pattern = r'^(\w+)(\([a-zA-Z0-9_\-/]+\))?: .{3,}'

    match = re.match(pattern, first_line)
    if not match:
        return False, (
            f"Invalid commit message format: '{first_line}'\n"
            "Expected format: 'type: description' or 'type(scope): description'\n"
            f"Valid types: {', '.join(VALID_TYPES)}"
        )

    commit_type = match.group(1)
    if commit_type not in VALID_TYPES:
        return False, (
            f"Invalid commit type: '{commit_type}'\n"
            f"Valid types: {', '.join(VALID_TYPES)}"
        )

    # Check description length (at least 3 characters)
    description_start = first_line.find(':') + 1
    description = first_line[description_start:].strip()
    if len(description) < 3:
        return False, "Commit description too short (minimum 3 characters)"

    # Check first line length (recommended: 72 chars, max: 100)
    if len(first_line) > 100:
        return False, f"First line too long ({len(first_line)} chars, max 100)"

    # Check if description starts with capital letter
    if description and not description[0].isupper():
        return False, "Commit description should start with a capital letter"

    return True, None


def main():
    """Main function to validate commit message."""
    # Get commit message file path from arguments
    if len(sys.argv) < 2:
        print("Usage: check_commit_message.py <commit-msg-file>")
        return 0

    commit_msg_file = Path(sys.argv[1])

    if not commit_msg_file.exists():
        print(f"Error: Commit message file not found: {commit_msg_file}")
        return 1

    # Read commit message
    with open(commit_msg_file, 'r', encoding='utf-8') as f:
        commit_message = f.read()

    # Validate
    is_valid, error_message = validate_commit_message(commit_message)

    if not is_valid:
        print("\nCommit message validation failed")
        print(error_message)
        print("\nConventional Commits format:")
        print("  feat: Add new feature")
        print("  fix: Fix bug in parser")
        print("  docs: Update README")
        print("  chore(deps): Update dependencies")
        print("\nSee: https://www.conventionalcommits.org/")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
