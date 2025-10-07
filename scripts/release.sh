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
TODAY=$(date +%Y-%m-%d)
print_info "Updating CHANGELOG.md with version $NEW_VERSION and date $TODAY..."

# Create backup
cp CHANGELOG.md CHANGELOG.md.bak

# Update CHANGELOG
awk -v version="$NEW_VERSION" -v date="$TODAY" '
/## \[Unreleased\]/ {
    print $0
    print ""
    print "## [" version "] - " date
    next
}
{ print }
' CHANGELOG.md.bak > CHANGELOG.md

rm CHANGELOG.md.bak
print_success "CHANGELOG.md updated"

# Show the changes
echo ""
print_info "CHANGELOG changes:"
echo "---"
head -20 CHANGELOG.md | grep -A 10 "## \[$NEW_VERSION\]"
echo "---"
echo ""

read -p "Commit CHANGELOG changes? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    print_info "Release cancelled. CHANGELOG.md has been modified but not committed."
    print_info "You can manually commit or revert the changes."
    exit 0
fi

# Commit CHANGELOG
git add CHANGELOG.md README.md 2>/dev/null || git add CHANGELOG.md
git commit -m "docs: Update CHANGELOG for v$NEW_VERSION release"
print_success "CHANGELOG committed"

print_step "Step 4: Merge dev to main"

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

# Create annotated tag
TAG_MESSAGE="Release v$NEW_VERSION

$(awk "/## \[$NEW_VERSION\]/,/## \[/" CHANGELOG.md | grep -v "^## \[$NEW_VERSION\]" | grep -v "^## \[" | head -20)

Generated with [Claude Code](https://claude.com/claude-code)"

git tag -a "v$NEW_VERSION" -m "$TAG_MESSAGE"
print_success "Created tag v$NEW_VERSION"

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
