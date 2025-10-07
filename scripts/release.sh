#!/bin/bash

# pyASDReader Automated Release Script
# Usage:
#   bash scripts/release.sh <version>
#   version: "patch", "minor", "major", or specific version like "1.2.4"
#
# This script automates the entire release workflow:
#   1. Pre-flight checks (branch, working directory, tests)
#   2. CHANGELOG preparation
#   3. Version tagging
#   4. Branch merging (dev -> main)
#   5. Tag pushing to trigger CI/CD

set -e  # Exit on error

# State tracking for error recovery
RELEASE_STATE_FILE=".release_state.tmp"
ORIGINAL_BRANCH=""
RELEASE_STAGE=""

# Cleanup function for error recovery
cleanup_on_error() {
    local exit_code=$?

    if [ $exit_code -ne 0 ]; then
        echo ""
        print_error "Release process failed at stage: ${RELEASE_STAGE:-unknown}"
        echo ""
        echo "Recovery instructions:"

        case "$RELEASE_STAGE" in
            "CHANGELOG_UPDATE")
                echo "  1. Check CHANGELOG.md for partial updates"
                echo "  2. Restore from backup if needed: mv CHANGELOG.md.bak CHANGELOG.md"
                echo "  3. Fix the issue and re-run the release script"
                ;;
            "VERSION_SYNC")
                echo "  1. Uncommitted changes exist in version files"
                echo "  2. Review changes: git diff"
                echo "  3. Either commit manually or restore: git restore CHANGELOG.md README.md src/_version.py pyproject.toml"
                ;;
            "MERGE_TO_MAIN")
                echo "  1. Currently on branch: $(git rev-parse --abbrev-ref HEAD)"
                echo "  2. Resolve merge conflicts if any"
                echo "  3. After resolving, continue with:"
                echo "     git add <resolved-files>"
                echo "     git commit"
                echo "     git tag -a v${NEW_VERSION} -m \"Release v${NEW_VERSION}\""
                echo "     git push origin main"
                echo "     git push origin v${NEW_VERSION}"
                echo "  Or abort the merge:"
                echo "     git merge --abort"
                echo "     git checkout ${ORIGINAL_BRANCH}"
                ;;
            "TAGGING")
                echo "  1. Main branch updated but tag not created"
                echo "  2. Create tag manually:"
                echo "     git checkout main"
                echo "     git tag -a v${NEW_VERSION} -m \"Release v${NEW_VERSION}\""
                echo "     git push origin main"
                echo "     git push origin v${NEW_VERSION}"
                ;;
            "PUSHING")
                echo "  1. Tag created but not pushed"
                echo "  2. Push manually:"
                echo "     git push origin main"
                echo "     git push origin v${NEW_VERSION}"
                ;;
            *)
                echo "  1. Review git status: git status"
                echo "  2. Review recent commits: git log -3 --oneline"
                echo "  3. Check current branch: git branch"
                if [ -n "$ORIGINAL_BRANCH" ]; then
                    echo "  4. Return to original branch: git checkout ${ORIGINAL_BRANCH}"
                fi
                ;;
        esac

        echo ""
        echo "For more help, see docs/VERSION_ROLLBACK.md"

        # Clean up state file
        rm -f "$RELEASE_STATE_FILE"
    fi
}

# Set up error trap
trap cleanup_on_error EXIT ERR INT TERM

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_step() {
    echo -e "\n${BLUE}==== $1 ====${NC}\n"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check arguments
if [ $# -eq 0 ]; then
    print_error "Missing version argument"
    echo "Usage: bash scripts/release.sh <version>"
    echo "  version: patch, minor, major, or specific version (e.g., 1.2.4)"
    echo ""
    echo "Examples:"
    echo "  bash scripts/release.sh patch   # 1.2.3 -> 1.2.4"
    echo "  bash scripts/release.sh minor   # 1.2.3 -> 1.3.0"
    echo "  bash scripts/release.sh major   # 1.2.3 -> 2.0.0"
    echo "  bash scripts/release.sh 1.2.4   # Specific version"
    exit 1
fi

VERSION_ARG=$1

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

print_step "Step 1: Pre-flight Checks"

# Check 1: Must be on dev branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
ORIGINAL_BRANCH="$CURRENT_BRANCH"  # Track original branch for error recovery

if [ "$CURRENT_BRANCH" != "dev" ]; then
    print_error "Releases must be initiated from 'dev' branch"
    print_error "Current branch: $CURRENT_BRANCH"
    echo ""
    echo "Please switch to dev branch:"
    echo "  git checkout dev"
    exit 1
fi
print_info "Branch check passed: on dev branch"

# Check 2: Git working directory must be clean
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    print_error "You have uncommitted changes"
    git status --short
    echo ""
    read -p "Do you want to continue anyway? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_info "Release cancelled"
        exit 0
    fi
else
    print_info "Git working directory is clean"
fi

# Check 3: Sync with remote
print_info "Fetching latest changes from remote..."
git fetch origin

# Check 4: Run tests (optional but recommended)
if command -v pytest &> /dev/null; then
    echo ""
    read -p "Run tests before release? (recommended) (yes/no): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_info "Running tests..."
        if ! python -m pytest tests/ -v; then
            print_error "Tests failed. Please fix the issues before releasing."
            exit 1
        fi
        print_success "All tests passed"
    fi
else
    print_warning "pytest not found, skipping tests"
fi

# Check 5: Pre-commit hooks installed
if [ -f ".git/hooks/pre-commit" ] && [ -f ".git/hooks/commit-msg" ]; then
    print_info "Pre-commit hooks are installed"
else
    print_warning "Pre-commit hooks not installed. Version consistency will not be validated automatically."
    echo ""
    read -p "Do you want to continue without pre-commit hooks? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_info "Release cancelled"
        echo ""
        echo "To install pre-commit hooks:"
        echo "  pip install pre-commit"
        echo "  pre-commit install"
        echo "  pre-commit install --hook-type commit-msg"
        exit 0
    fi
fi

print_step "Step 2: Calculate Version Number"

# Get current version from latest git tag
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//' || echo "0.0.0")
print_info "Current version: $CURRENT_VERSION"

# Calculate new version
if [[ "$VERSION_ARG" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    # Specific version provided
    NEW_VERSION="$VERSION_ARG"
    print_info "Using specified version: $NEW_VERSION"
else
    # Calculate based on semver bump type
    IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

    case "$VERSION_ARG" in
        patch)
            PATCH=$((PATCH + 1))
            ;;
        minor)
            MINOR=$((MINOR + 1))
            PATCH=0
            ;;
        major)
            MAJOR=$((MAJOR + 1))
            MINOR=0
            PATCH=0
            ;;
        *)
            print_error "Invalid version argument: $VERSION_ARG"
            echo "Must be 'patch', 'minor', 'major', or a specific version (e.g., 1.2.4)"
            exit 1
            ;;
    esac

    NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
    print_info "Calculated new version: $NEW_VERSION"
fi

# Confirm version
echo ""
print_warning "About to release version: v$NEW_VERSION"
print_warning "Current version: v$CURRENT_VERSION"
echo ""
read -p "Is this correct? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    print_info "Release cancelled"
    exit 0
fi

print_step "Step 3: Update CHANGELOG"

# Check if CHANGELOG has unreleased section with content
if ! grep -q "## \[Unreleased\]" CHANGELOG.md; then
    print_error "CHANGELOG.md is missing [Unreleased] section"
    exit 1
fi

# Check if there's content in Unreleased section
UNRELEASED_CONTENT=$(awk '/## \[Unreleased\]/,/## \[/' CHANGELOG.md | grep -v "^## " | grep -v "^$" | wc -l)
if [ "$UNRELEASED_CONTENT" -lt 2 ]; then
    print_warning "CHANGELOG [Unreleased] section appears empty"
    echo ""
    read -p "Open CHANGELOG.md for editing? (yes/no): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        ${EDITOR:-vim} CHANGELOG.md
    else
        print_error "Please update CHANGELOG.md with release notes before proceeding"
        exit 1
    fi
fi

# Update CHANGELOG: Move [Unreleased] content to new version
RELEASE_STAGE="CHANGELOG_UPDATE"
TODAY=$(date +%Y-%m-%d)
print_info "Updating CHANGELOG.md with version $NEW_VERSION and date $TODAY..."

# Create backup
cp CHANGELOG.md CHANGELOG.md.bak

# Extract [Unreleased] content and move it to new version
python3 - <<EOF
import re
import sys

with open('CHANGELOG.md.bak', 'r', encoding='utf-8') as f:
    content = f.read()

# Find [Unreleased] section and next version section
unreleased_pattern = r'(## \[Unreleased\])\n+(.*?)(?=\n## \[|$)'
match = re.search(unreleased_pattern, content, re.DOTALL)

if not match:
    print("Error: Could not find [Unreleased] section", file=sys.stderr)
    sys.exit(1)

unreleased_content = match.group(2).strip()

# Insert new version section after [Unreleased] and clear [Unreleased] content
new_section = f"""## [Unreleased]

## [{sys.argv[1]}] - {sys.argv[2]}

{unreleased_content}"""

# Replace the [Unreleased] section
# Handle both cases: when there's a next section (## [) or end of file ($)
result = re.sub(
    r'## \[Unreleased\].*?(?=\n## \[|$)',
    new_section + '\n',
    content,
    count=1,
    flags=re.DOTALL
)

with open('CHANGELOG.md', 'w', encoding='utf-8') as f:
    f.write(result)

print(f"Moved {len(unreleased_content)} characters from [Unreleased] to [{sys.argv[1]}]")
EOF
$NEW_VERSION $TODAY

if [ $? -ne 0 ]; then
    print_error "Failed to update CHANGELOG.md"
    mv CHANGELOG.md.bak CHANGELOG.md
    exit 1
fi

rm CHANGELOG.md.bak
print_success "CHANGELOG.md updated"

# Show the changes
echo ""
print_info "CHANGELOG changes:"
echo "---"
head -20 CHANGELOG.md | grep -A 10 "## \[$NEW_VERSION\]"
echo "---"
echo ""

read -p "Proceed with version updates? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    print_info "Release cancelled. CHANGELOG.md has been modified but not committed."
    print_info "You can manually commit or revert the changes."
    exit 0
fi

print_step "Step 3.5: Synchronize Version Numbers"

RELEASE_STAGE="VERSION_SYNC"
# CRITICAL: Update all version files BEFORE committing to avoid pre-commit hook conflicts.
# The check_version_consistency.py pre-commit hook will validate that all these files
# have matching version numbers. By updating them here first, the hook will pass.
# Files to synchronize: CHANGELOG.md (already updated), README.md, src/_version.py, pyproject.toml

# Update README.md citation version
if grep -q "version = {" README.md; then
    print_info "Updating README.md citation version..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/version = {[0-9.]*}/version = {$NEW_VERSION}/" README.md
    else
        sed -i "s/version = {[0-9.]*}/version = {$NEW_VERSION}/" README.md
    fi
    print_success "README.md updated"
fi

# Update src/_version.py fallback version
if [ -f "src/_version.py" ]; then
    print_info "Updating src/_version.py fallback version..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/__version__ = \"[0-9.]*\"/__version__ = \"$NEW_VERSION\"/" src/_version.py
    else
        sed -i "s/__version__ = \"[0-9.]*\"/__version__ = \"$NEW_VERSION\"/" src/_version.py
    fi
    print_success "src/_version.py updated"
fi

# Update pyproject.toml fallback version
if grep -q "fallback_version" pyproject.toml; then
    print_info "Updating pyproject.toml fallback version..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/fallback_version = \"[0-9.]*\"/fallback_version = \"$NEW_VERSION\"/" pyproject.toml
    else
        sed -i "s/fallback_version = \"[0-9.]*\"/fallback_version = \"$NEW_VERSION\"/" pyproject.toml
    fi
    print_success "pyproject.toml updated"
fi

# Verify version consistency
print_info "Verifying version consistency..."
if [ -f ".pre-commit-hooks/check_version_consistency.py" ]; then
    if python3 .pre-commit-hooks/check_version_consistency.py; then
        print_success "All version numbers synchronized"
    else
        print_error "Version consistency check failed"
        echo "Please check the files manually"
        exit 1
    fi
fi

# Commit all version changes
print_info "Committing version updates..."
git add CHANGELOG.md README.md src/_version.py pyproject.toml
git commit -m "chore: Release v$NEW_VERSION

- Update CHANGELOG.md with v$NEW_VERSION
- Synchronize version numbers across all files
- Move [Unreleased] content to v$NEW_VERSION"
print_success "Version updates committed"

print_step "Step 4: Merge dev to main"

RELEASE_STAGE="MERGE_TO_MAIN"
print_info "Switching to main branch..."
git checkout main

print_info "Merging dev into main..."
if ! git merge dev; then
    print_error "Merge failed. Please resolve conflicts manually."
    echo ""
    echo "After resolving conflicts:"
    echo "  git add <resolved-files>"
    echo "  git commit"
    echo "  git tag -a v$NEW_VERSION -m \"Release v$NEW_VERSION\""
    echo "  git push origin main"
    echo "  git push origin v$NEW_VERSION"
    exit 1
fi

print_success "Merged dev to main"

print_step "Step 5: Create and Push Version Tag"

RELEASE_STAGE="TAGGING"
# Create annotated tag
TAG_MESSAGE="Release v$NEW_VERSION

$(awk "/## \[$NEW_VERSION\]/,/## \[/" CHANGELOG.md | grep -v "^## \[$NEW_VERSION\]" | grep -v "^## \[" | head -20)

Generated with [Claude Code](https://claude.com/claude-code)"

git tag -a "v$NEW_VERSION" -m "$TAG_MESSAGE"
print_success "Created tag v$NEW_VERSION"

RELEASE_STAGE="PUSHING"
# Push main branch
print_info "Pushing main branch..."
git push origin main
print_success "Pushed main branch"

# Push tag
print_info "Pushing tag v$NEW_VERSION..."
git push origin "v$NEW_VERSION"
print_success "Pushed tag v$NEW_VERSION"

print_step "Step 6: Back to dev branch"

git checkout dev
git merge main
git push origin dev
print_success "Synced dev branch with main"

print_step "Release Complete!"

echo ""
print_success "Version v$NEW_VERSION has been released!"
echo ""
echo "Next steps:"
echo "  1. Monitor GitHub Actions: https://github.com/KaiTastic/pyASDReader/actions"
echo "  2. PyPI workflow will publish to: https://pypi.org/project/pyASDReader/"
echo "  3. GitHub Release will be created automatically"
echo ""
echo "Estimated workflow completion time: ~8 minutes (with TestPyPI test reuse)"
echo ""
