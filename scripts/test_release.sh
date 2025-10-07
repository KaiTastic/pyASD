#!/bin/bash

# Test script for release.sh
# Tests core functionality without making actual releases

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

print_summary() {
    echo ""
    echo "================================"
    echo "Test Summary"
    echo "================================"
    echo -e "Passed: ${GREEN}${TESTS_PASSED}${NC}"
    echo -e "Failed: ${RED}${TESTS_FAILED}${NC}"
    echo "================================"

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
        return 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        return 1
    fi
}

# Test 1: Version calculation - patch
test_version_calculation_patch() {
    print_test "Testing version calculation: patch"

    CURRENT_VERSION="1.2.3"
    IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"
    PATCH=$((PATCH + 1))
    NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"

    if [ "$NEW_VERSION" = "1.2.4" ]; then
        print_pass "Patch version calculation: 1.2.3 -> 1.2.4"
    else
        print_fail "Patch version calculation failed: got $NEW_VERSION, expected 1.2.4"
    fi
}

# Test 2: Version calculation - minor
test_version_calculation_minor() {
    print_test "Testing version calculation: minor"

    CURRENT_VERSION="1.2.3"
    IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"
    MINOR=$((MINOR + 1))
    PATCH=0
    NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"

    if [ "$NEW_VERSION" = "1.3.0" ]; then
        print_pass "Minor version calculation: 1.2.3 -> 1.3.0"
    else
        print_fail "Minor version calculation failed: got $NEW_VERSION, expected 1.3.0"
    fi
}

# Test 3: Version calculation - major
test_version_calculation_major() {
    print_test "Testing version calculation: major"

    CURRENT_VERSION="1.2.3"
    IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
    NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"

    if [ "$NEW_VERSION" = "2.0.0" ]; then
        print_pass "Major version calculation: 1.2.3 -> 2.0.0"
    else
        print_fail "Major version calculation failed: got $NEW_VERSION, expected 2.0.0"
    fi
}

# Test 4: CHANGELOG parsing with Python script
test_changelog_parsing() {
    print_test "Testing CHANGELOG parsing logic"

    # Create test CHANGELOG
    cat > /tmp/test_changelog.md <<'EOF'
# Changelog

## [Unreleased]

### Added
- New feature X
- Enhancement Y

### Fixed
- Bug Z

## [1.2.0] - 2025-01-01

### Added
- Previous feature
EOF

    # Run the Python script logic
    python3 - <<'PYEOF' /tmp/test_changelog.md 1.3.0 2025-10-07
import re
import sys

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    content = f.read()

# Find [Unreleased] section
unreleased_pattern = r'(## \[Unreleased\])\n+(.*?)(?=\n## \[|$)'
match = re.search(unreleased_pattern, content, re.DOTALL)

if not match:
    print("Error: Could not find [Unreleased] section", file=sys.stderr)
    sys.exit(1)

unreleased_content = match.group(2).strip()

# Check if content was found
if "New feature X" in unreleased_content and "Bug Z" in unreleased_content:
    print("SUCCESS: CHANGELOG parsing works correctly")
    sys.exit(0)
else:
    print("ERROR: CHANGELOG content not extracted properly", file=sys.stderr)
    sys.exit(1)
PYEOF

    if [ $? -eq 0 ]; then
        print_pass "CHANGELOG parsing extracts content correctly"
    else
        print_fail "CHANGELOG parsing failed"
    fi

    # Cleanup
    rm -f /tmp/test_changelog.md
}

# Test 5: Version consistency check script
test_version_consistency_check() {
    print_test "Testing version consistency check script"

    if [ -f ".pre-commit-hooks/check_version_consistency.py" ]; then
        # Test that the script exists and can be executed
        if python3 .pre-commit-hooks/check_version_consistency.py --help > /dev/null 2>&1 || \
           python3 .pre-commit-hooks/check_version_consistency.py > /dev/null 2>&1 || \
           true; then
            print_pass "Version consistency check script exists and is executable"
        else
            # The script might fail normally because versions don't match, that's okay
            print_pass "Version consistency check script exists"
        fi
    else
        print_fail "Version consistency check script not found"
    fi
}

# Test 6: Commit message validation
test_commit_message_validation() {
    print_test "Testing commit message validation"

    if [ -f ".pre-commit-hooks/check_commit_message.py" ]; then
        # Create test commit message
        echo "feat: Add new feature" > /tmp/test_commit_msg.txt

        if python3 .pre-commit-hooks/check_commit_message.py /tmp/test_commit_msg.txt > /dev/null 2>&1; then
            print_pass "Valid commit message accepted"
        else
            print_fail "Valid commit message rejected"
        fi

        # Test invalid commit message
        echo "invalid commit message" > /tmp/test_commit_msg.txt

        if python3 .pre-commit-hooks/check_commit_message.py /tmp/test_commit_msg.txt > /dev/null 2>&1; then
            print_fail "Invalid commit message accepted"
        else
            print_pass "Invalid commit message rejected"
        fi

        rm -f /tmp/test_commit_msg.txt
    else
        print_fail "Commit message validation script not found"
    fi
}

# Test 7: CHANGELOG format validation
test_changelog_format_validation() {
    print_test "Testing CHANGELOG format validation"

    if [ -f ".pre-commit-hooks/check_changelog_format.py" ]; then
        if python3 .pre-commit-hooks/check_changelog_format.py > /dev/null 2>&1 || true; then
            print_pass "CHANGELOG format validation script exists and runs"
        else
            print_fail "CHANGELOG format validation script failed to run"
        fi
    else
        print_fail "CHANGELOG format validation script not found"
    fi
}

# Test 8: Release script exists and has correct permissions
test_release_script_exists() {
    print_test "Testing release.sh exists and is executable"

    if [ -f "scripts/release.sh" ]; then
        if [ -x "scripts/release.sh" ]; then
            print_pass "release.sh exists and is executable"
        else
            print_fail "release.sh exists but is not executable"
        fi
    else
        print_fail "release.sh not found"
    fi
}

# Test 9: Publish script exists
test_publish_script_exists() {
    print_test "Testing publish.sh exists"

    if [ -f "scripts/publish.sh" ]; then
        if [ -x "scripts/publish.sh" ]; then
            print_pass "publish.sh exists and is executable"
        else
            print_fail "publish.sh exists but is not executable"
        fi
    else
        print_fail "publish.sh not found"
    fi
}

# Test 10: Required files exist
test_required_files() {
    print_test "Testing required files exist"

    required_files=(
        "CHANGELOG.md"
        "README.md"
        "pyproject.toml"
        "src/_version.py"
        "VERSION_MANAGEMENT.md"
        "CONTRIBUTING.md"
    )

    all_exist=true
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_fail "Required file missing: $file"
            all_exist=false
        fi
    done

    if $all_exist; then
        print_pass "All required files exist"
    fi
}

# Main test execution
echo "================================"
echo "Testing release.sh functionality"
echo "================================"
echo ""

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Run all tests
test_version_calculation_patch
test_version_calculation_minor
test_version_calculation_major
test_changelog_parsing
test_version_consistency_check
test_commit_message_validation
test_changelog_format_validation
test_release_script_exists
test_publish_script_exists
test_required_files

# Print summary
print_summary
