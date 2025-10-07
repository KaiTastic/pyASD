#!/usr/bin/env python3
"""
Pre-commit hook to check version consistency across multiple files.

Ensures that version numbers in CHANGELOG.md, README.md, pyproject.toml,
and src/_version.py are consistent.
"""

import re
import sys
from pathlib import Path


def extract_changelog_version(changelog_path):
    """Extract the latest version from CHANGELOG.md."""
    if not changelog_path.exists():
        return None

    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match pattern: ## [X.Y.Z] - YYYY-MM-DD
    match = re.search(r'##\s+\[(\d+\.\d+\.\d+)\]\s+-\s+\d{4}-\d{2}-\d{2}', content)
    if match:
        return match.group(1)
    return None


def extract_readme_version(readme_path):
    """Extract version from README.md citation section."""
    if not readme_path.exists():
        return None

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match pattern: version = {X.Y.Z}
    match = re.search(r'version\s*=\s*\{(\d+\.\d+\.\d+)\}', content)
    if match:
        return match.group(1)
    return None


def extract_pyproject_version(pyproject_path):
    """Extract fallback_version from pyproject.toml."""
    if not pyproject_path.exists():
        return None

    with open(pyproject_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match pattern: fallback_version = "X.Y.Z"
    match = re.search(r'fallback_version\s*=\s*["\'](\d+\.\d+\.\d+)["\']', content)
    if match:
        return match.group(1)
    return None


def extract_version_py_version(version_py_path):
    """Extract __version__ from src/_version.py."""
    if not version_py_path.exists():
        return None

    with open(version_py_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match pattern: __version__ = "X.Y.Z"
    match = re.search(r'__version__\s*=\s*["\'](\d+\.\d+\.\d+)["\']', content)
    if match:
        return match.group(1)
    return None


def main():
    """Check version consistency across all files."""
    project_root = Path(__file__).parent.parent

    files = {
        'CHANGELOG.md': project_root / 'CHANGELOG.md',
        'README.md': project_root / 'README.md',
        'pyproject.toml': project_root / 'pyproject.toml',
        'src/_version.py': project_root / 'src' / '_version.py',
    }

    # Extract versions
    versions = {
        'CHANGELOG.md': extract_changelog_version(files['CHANGELOG.md']),
        'README.md': extract_readme_version(files['README.md']),
        'pyproject.toml': extract_pyproject_version(files['pyproject.toml']),
        'src/_version.py': extract_version_py_version(files['src/_version.py']),
    }

    # Filter out None values
    valid_versions = {k: v for k, v in versions.items() if v is not None}

    if not valid_versions:
        print("Warning: Could not extract version from any file")
        return 0

    # Check consistency
    unique_versions = set(valid_versions.values())

    if len(unique_versions) == 1:
        print(f"✓ Version consistency check passed: {unique_versions.pop()}")
        return 0
    else:
        print("✗ Version inconsistency detected!")
        print("\nVersions found:")
        for file, version in sorted(valid_versions.items()):
            print(f"  {file:20} -> {version}")

        print("\nPlease ensure all version numbers are consistent before committing.")
        print("Expected version (from CHANGELOG.md): {}".format(
            versions.get('CHANGELOG.md', 'NOT FOUND')
        ))
        return 1


if __name__ == '__main__':
    sys.exit(main())
