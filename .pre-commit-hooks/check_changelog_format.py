#!/usr/bin/env python3
"""
Pre-commit hook to validate CHANGELOG.md format.

Validates that CHANGELOG.md follows the Keep a Changelog format:
- Has [Unreleased] section
- Version entries follow format: ## [X.Y.Z] - YYYY-MM-DD
- Versions are in descending order
- Uses standard sections (Added, Changed, Fixed, etc.)
"""

import re
import sys
from datetime import datetime
from pathlib import Path


def check_unreleased_section(content):
    """Check if [Unreleased] section exists."""
    if not re.search(r'##\s+\[Unreleased\]', content):
        return False, "[Unreleased] section is missing"
    return True, None


def extract_versions(content):
    """Extract all version entries from CHANGELOG."""
    # Match pattern: ## [X.Y.Z] - YYYY-MM-DD
    pattern = r'##\s+\[(\d+\.\d+\.\d+)\]\s+-\s+(\d{4}-\d{2}-\d{2})'
    matches = re.findall(pattern, content)
    return matches


def validate_version_format(version):
    """Validate semantic version format."""
    pattern = r'^\d+\.\d+\.\d+$'
    return re.match(pattern, version) is not None


def validate_date_format(date_str):
    """Validate date format (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def check_version_order(versions):
    """Check if versions are in descending order."""
    version_numbers = [tuple(map(int, v[0].split('.'))) for v in versions]

    for i in range(len(version_numbers) - 1):
        if version_numbers[i] < version_numbers[i + 1]:
            return False, f"Version {versions[i][0]} should come before {versions[i+1][0]}"

    return True, None


def check_standard_sections(content):
    """Check if content uses standard Keep a Changelog sections."""
    standard_sections = [
        'Added', 'Changed', 'Deprecated', 'Removed',
        'Fixed', 'Security', 'Technical Improvements'
    ]

    # Find all section headers (### Section)
    section_pattern = r'###\s+([A-Za-z\s]+)'
    found_sections = re.findall(section_pattern, content)

    # Check if non-standard sections are used
    warnings = []
    for section in found_sections:
        section = section.strip()
        if section not in standard_sections and section != '':
            warnings.append(f"Non-standard section: '{section}'")

    return warnings


def main():
    """Validate CHANGELOG.md format."""
    project_root = Path(__file__).parent.parent
    changelog_path = project_root / 'CHANGELOG.md'

    if not changelog_path.exists():
        print("CHANGELOG.md not found")
        return 1

    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []
    warnings = []

    # Check 1: Unreleased section
    has_unreleased, error = check_unreleased_section(content)
    if not has_unreleased:
        errors.append(error)

    # Check 2: Extract and validate version entries
    versions = extract_versions(content)

    if not versions:
        errors.append("No version entries found in CHANGELOG.md")
    else:
        # Check version format
        for version, date in versions:
            if not validate_version_format(version):
                errors.append(f"Invalid version format: {version}")
            if not validate_date_format(date):
                errors.append(f"Invalid date format for version {version}: {date}")

        # Check version order
        ordered, error = check_version_order(versions)
        if not ordered:
            errors.append(error)

    # Check 3: Standard sections (warnings only)
    section_warnings = check_standard_sections(content)
    warnings.extend(section_warnings)

    # Print results
    if errors:
        print("CHANGELOG.md validation failed")
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")

        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"  - {warning}")

        print("\nPlease fix the errors and ensure CHANGELOG.md follows Keep a Changelog format.")
        print("See: https://keepachangelog.com/en/1.0.0/")
        return 1
    else:
        if warnings:
            print("CHANGELOG.md validation passed with warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        else:
            print("CHANGELOG.md validation passed")
        return 0


if __name__ == '__main__':
    sys.exit(main())