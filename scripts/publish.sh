#!/bin/bash

# pyASDReader PyPI Publishing Script
# Usage:
#   bash scripts/publish.sh test    # Publish to TestPyPI
#   bash scripts/publish.sh prod    # Publish to PyPI

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check arguments
if [ $# -eq 0 ]; then
    print_error "Missing argument. Usage: bash scripts/publish.sh [test|prod]"
    exit 1
fi

TARGET=$1

if [ "$TARGET" != "test" ] && [ "$TARGET" != "prod" ]; then
    print_error "Invalid argument. Use 'test' for TestPyPI or 'prod' for PyPI"
    exit 1
fi

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

print_info "Starting PyPI publishing process for pyASDReader..."
print_info "Target: $TARGET"
print_info "Project root: $PROJECT_ROOT"

# Safety check 1: Verify branch for production releases
if [ "$TARGET" == "prod" ]; then
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    if [ "$CURRENT_BRANCH" != "main" ]; then
        print_error "Production releases must be made from 'main' branch"
        print_error "Current branch: $CURRENT_BRANCH"
        print_error "Please switch to main branch and merge your changes first"
        exit 1
    fi
    print_info "✓ Branch check passed: on main branch"
fi

# Safety check 2: Verify git working directory is clean
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    print_warning "Warning: You have uncommitted changes"
    git status --short
    read -p "Continue anyway? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_info "Publishing cancelled"
        exit 0
    fi
else
    print_info "✓ Git working directory is clean"
fi

# Check if required tools are installed
print_info "Checking required tools..."
if ! command -v python3 &> /dev/null; then
    print_error "python3 is not installed"
    exit 1
fi

if ! python3 -m pip show build &> /dev/null; then
    print_warning "build package not found. Installing..."
    python3 -m pip install --upgrade build
fi

if ! python3 -m pip show twine &> /dev/null; then
    print_warning "twine package not found. Installing..."
    python3 -m pip install --upgrade twine
fi

# Read version from pyproject.toml or use setuptools-scm
if grep -q 'dynamic = \["version"\]' pyproject.toml; then
    print_info "Version is dynamic (managed by setuptools-scm)"
    # Try to get version from git tags
    if command -v git &> /dev/null && git rev-parse --git-dir > /dev/null 2>&1; then
        VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "unknown")
        if [ "$VERSION" = "unknown" ]; then
            print_warning "No git tags found. Version will be determined by setuptools-scm during build"
            VERSION="(determined during build)"
        fi
    else
        VERSION="(determined during build)"
    fi
else
    VERSION=$(grep -m 1 'version = ' pyproject.toml | sed 's/.*version = "\(.*\)".*/\1/')
fi
print_info "Version: $VERSION"

# Safety check 3: Verify version consistency
if [ -f ".pre-commit-hooks/check_version_consistency.py" ]; then
    print_info "Checking version consistency..."
    if ! python3 .pre-commit-hooks/check_version_consistency.py; then
        print_error "Version consistency check failed"
        print_error "Please ensure all version numbers are synchronized"
        exit 1
    fi
fi

# Safety check 4: Verify CHANGELOG has entry for this version
if [ "$TARGET" == "prod" ] && [ "$VERSION" != "(determined during build)" ]; then
    if ! grep -q "## \[$VERSION\]" CHANGELOG.md 2>/dev/null; then
        print_warning "Warning: No CHANGELOG entry found for version $VERSION"
        print_warning "Please ensure CHANGELOG.md is updated before releasing"
        read -p "Continue anyway? (yes/no): " -r
        echo
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            print_info "Publishing cancelled"
            exit 0
        fi
    else
        print_info "✓ CHANGELOG entry found for version $VERSION"
    fi
fi

# Confirm before proceeding
if [ "$TARGET" == "prod" ]; then
    print_warning "You are about to publish version $VERSION to PyPI (production)"
    read -p "Are you sure you want to continue? (yes/no): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_info "Publishing cancelled"
        exit 0
    fi
fi

# Step 1: Clean previous builds
print_info "Step 1: Cleaning previous build artifacts..."
rm -rf build/ dist/ *.egg-info src/*.egg-info
print_info "Cleaned successfully"

# Step 2: Run tests (recommended for production releases)
if [ "$TARGET" == "prod" ]; then
    print_info "Step 2: Running tests..."
    if command -v pytest &> /dev/null; then
        if ! python3 -m pytest tests/ -v; then
            print_error "Tests failed. Publishing cancelled"
            print_error "Fix the failing tests before publishing to production PyPI"
            exit 1
        fi
        print_info "All tests passed"
    else
        print_warning "pytest not found, skipping tests"
        print_warning "It is recommended to run tests before production releases"
        read -p "Continue without running tests? (yes/no): " -r
        echo
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            print_info "Publishing cancelled"
            exit 0
        fi
    fi
else
    print_info "Step 2: Skipping tests for TestPyPI (optional for testing)"
fi

# Step 3: Build the package
print_info "Step 2: Building the package..."
if ! python3 -m build; then
    print_error "Build failed"
    exit 1
fi
print_info "Build successful"

# Step 4: Check the distribution
print_info "Step 3: Checking the distribution..."
if ! python3 -m twine check dist/*; then
    print_error "Distribution check failed"
    exit 1
fi
print_info "Distribution check passed"

# Step 5: Upload to PyPI or TestPyPI
if [ "$TARGET" == "test" ]; then
    print_info "Step 4: Uploading to TestPyPI..."
    python3 -m twine upload --repository testpypi dist/*

    print_info "Successfully published to TestPyPI!"
    print_info "View at: https://test.pypi.org/project/pyASDReader/$VERSION/"
    print_info ""
    print_info "To test installation, run:"
    print_info "  pip install --index-url https://test.pypi.org/simple/ --no-deps pyASDReader"

elif [ "$TARGET" == "prod" ]; then
    print_info "Step 4: Uploading to PyPI..."
    python3 -m twine upload dist/*

    print_info "Successfully published to PyPI!"
    print_info "View at: https://pypi.org/project/pyASDReader/$VERSION/"
    print_info ""
    print_info "To install, run:"
    print_info "  pip install --upgrade pyASDReader"
    print_info ""
    print_info "Don't forget to create a git tag:"
    print_info "  git tag v$VERSION"
    print_info "  git push origin v$VERSION"
fi

print_info "Publishing process completed successfully!"
