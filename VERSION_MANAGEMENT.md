# Version Management Guide

## Overview

pyASDReader uses **setuptools_scm** for automatic version management based on Git tags. This ensures version consistency across:
- Local development environment
- PyPI packages
- GitHub releases

## Single Source of Truth

```
Git Tag → setuptools_scm → Package Version → PyPI Version
```

All versions are derived from Git tags automatically. No manual version file editing required.

## Configuration

**pyproject.toml:**
```toml
[project]
dynamic = ["version"]  # Version is dynamic, not hardcoded

[tool.setuptools_scm]
version_scheme = "guess-next-dev"
local_scheme = "no-local-version"
fallback_version = "1.0.0"
```

**How it works:**
- **With Git tag**: Uses tag as version (e.g., `v1.2.0` → `1.2.0`)
- **Between tags**: Adds dev suffix (e.g., `1.2.0.dev3+g7a8b9c0`)
- **No Git/tags**: Falls back to `1.0.0`

## Release Workflow

### Step 1: Development Phase

```bash
# Regular development commits
git add .
git commit -m "feat: Add new feature"
git push origin main

# Version during development: 1.1.0.dev1+g7100d29
```

### Step 2: Prepare Release

```bash
# 1. Update CHANGELOG.md with release notes
vim CHANGELOG.md

# 2. Move changes from [Unreleased] to new version section
## [1.2.0] - 2025-10-05

### Added
- New feature X
- Enhancement Y

### Fixed
- Bug Z

# 3. Commit the changelog
git add CHANGELOG.md
git commit -m "docs: Update CHANGELOG for v1.2.0 release"
```

### Step 3: Create Git Tag

```bash
# Create annotated tag (REQUIRED for setuptools_scm)
git tag -a v1.2.0 -m "Release v1.2.0"

# Verify tag
git describe --tags
# Output: v1.2.0

# Push tag to remote
git push origin v1.2.0
```

### Step 4: Build and Publish

#### Option A: Manual Publishing

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check version in built package
tar -tzf dist/pyASDReader-1.2.0.tar.gz | grep PKG-INFO
tar -xzf dist/pyASDReader-1.2.0.tar.gz -O pyASDReader-1.2.0/PKG-INFO | grep Version

# Upload to TestPyPI (optional, for testing)
python -m twine upload --repository testpypi dist/*

# Upload to PyPI (production)
python -m twine upload dist/*
```

#### Option B: Automatic Publishing (GitHub Actions)

```bash
# Just push the tag - GitHub Actions handles the rest
git push origin v1.2.0

# Workflow automatically:
# 1. Builds the package
# 2. Runs tests
# 3. Publishes to PyPI
# 4. Creates GitHub Release
```

See `.github/workflows/publish-to-pypi.yml`

## Version Verification

### Check Local Version

```bash
# Method 1: Using Python
python -c "from pyASDReader import __version__; print(__version__)"

# Method 2: Using setuptools_scm directly
python -m setuptools_scm

# Method 3: After installation
pip show pyASDReader | grep Version
```

### Check PyPI Version

```bash
# Latest version on PyPI
pip index versions pyASDReader

# Or visit
# https://pypi.org/project/pyASDReader/
```

### Check Git Tags

```bash
# List all tags
git tag -l

# Show latest tag
git describe --tags --abbrev=0

# Show detailed tag info
git show v1.2.0
```

## Semantic Versioning

Follow [Semantic Versioning 2.0.0](https://semver.org/):

```
v{MAJOR}.{MINOR}.{PATCH}

MAJOR: Incompatible API changes
MINOR: Backwards-compatible new features
PATCH: Backwards-compatible bug fixes
```

**Examples:**
- `v1.0.0` → `v1.0.1`: Bug fix release
- `v1.0.1` → `v1.1.0`: New feature added
- `v1.1.0` → `v2.0.0`: Breaking changes

## Troubleshooting

### Problem: Wrong version displayed

```bash
# Check what tag Git sees
git describe --tags

# If wrong tag is shown, check for duplicate tags
git tag -l

# Remove incorrect tag
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
```

### Problem: Version shows as fallback (1.0.0)

**Cause:** setuptools_scm not installed or not in Git repository

**Solution:**
```bash
# Install setuptools_scm
pip install setuptools_scm>=8

# Verify you're in a Git repo
git status

# Verify tags exist
git tag -l
```

### Problem: Duplicate tags on same commit

```bash
# Current status
git tag --points-at HEAD
# Output: v1.0.0
#         v1.1.0

# Delete the incorrect tag
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# Verify
git describe --tags
# Output: v1.1.0
```

### Problem: PyPI version doesn't match Git tag

**Cause:** Package was built before tag was created

**Solution:**
```bash
# 1. Clean old builds
rm -rf dist/ build/ *.egg-info

# 2. Verify current Git tag
git describe --tags

# 3. Rebuild
python -m build

# 4. Check built version
ls dist/
# Should show: pyASDReader-1.2.0.tar.gz

# 5. Re-upload (requires new version number on PyPI)
python -m twine upload dist/*
```

## Best Practices

1. **Always use annotated tags**: `git tag -a v1.2.0 -m "message"`
   - NOT `git tag v1.2.0` (lightweight tag)

2. **Never edit version files manually**
   - src/_version.py is auto-generated
   - pyproject.toml has `dynamic = ["version"]`

3. **Update CHANGELOG before tagging**
   - Users need to know what changed
   - Tag message can reference CHANGELOG

4. **Test before releasing**
   - Run full test suite: `pytest tests/`
   - Test installation: `pip install -e .`
   - Verify version: `python -c "from pyASDReader import __version__; print(__version__)"`

5. **Use TestPyPI for testing**
   - Test uploads: `bash scripts/publish.sh test`
   - Verify installation: `pip install -i https://test.pypi.org/simple/ pyASDReader`

6. **One tag per release**
   - Don't create multiple tags on same commit
   - Don't move tags after pushing

## Quick Reference

```bash
# Development workflow
git commit -m "feat: New feature"
git push

# Release workflow
vim CHANGELOG.md
git commit -m "docs: Update CHANGELOG for v1.2.0"
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# Automatic publishing via GitHub Actions
# Manual publishing
python -m build
python -m twine upload dist/*

# Verification
git describe --tags
python -c "from pyASDReader import __version__; print(__version__)"
pip index versions pyASDReader
```

## References

- [setuptools_scm documentation](https://setuptools-scm.readthedocs.io/)
- [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
- [PEP 440 - Version Identification](https://peps.python.org/pep-0440/)
- [Git Tagging Documentation](https://git-scm.com/book/en/v2/Git-Basics-Tagging)
