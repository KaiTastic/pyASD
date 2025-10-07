# Version Rollback and Emergency Procedures

This document describes how to rollback a release in case of critical issues discovered after deployment.

## Table of Contents

- [When to Rollback](#when-to-rollback)
- [Quick Rollback Procedure](#quick-rollback-procedure)
- [Detailed Rollback Steps](#detailed-rollback-steps)
- [Post-Rollback Actions](#post-rollback-actions)
- [Prevention Strategies](#prevention-strategies)

## When to Rollback

Consider rolling back when:
- **Critical bug** discovered in production that breaks core functionality
- **Security vulnerability** identified
- **Data corruption** or loss issues
- **Major compatibility** problems affecting users
- **Installation failures** on PyPI preventing users from installing

**DO NOT rollback for**:
- Minor bugs that don't affect core functionality
- Documentation errors (fix with patch release)
- Performance issues (fix with patch release)

## Quick Rollback Procedure

For urgent situations, use this abbreviated process:

```bash
# 1. Identify the last good version
LAST_GOOD_VERSION="v1.2.2"  # Example

# 2. Remove problematic version from PyPI (cannot be undone!)
# Go to: https://pypi.org/manage/project/pyASDReader/releases/
# Click on the problematic version -> "Options" -> "Delete"

# 3. Tag and release the last good version as a new version
git checkout main
git checkout $LAST_GOOD_VERSION
git tag -a v1.2.4 -m "Rollback to $LAST_GOOD_VERSION due to critical issue"
git push origin v1.2.4

# 4. Update CHANGELOG and push
# (See detailed steps below)
```

**Timeline**: Can be completed in 10-15 minutes.

## Detailed Rollback Steps

### Step 1: Assess the Situation

1. **Identify the problematic version**
   ```bash
   # Current version on PyPI
   pip index versions pyASDReader

   # Recent git tags
   git tag -l --sort=-version:refname | head -5
   ```

2. **Identify the last known good version**
   ```bash
   # Check commit history
   git log --oneline --decorate

   # Verify the last good tag
   LAST_GOOD_VERSION="v1.2.2"
   git show $LAST_GOOD_VERSION
   ```

3. **Document the issue**
   - Create GitHub issue describing the problem
   - Tag as "critical" and "bug"
   - Include: affected versions, reproduction steps, impact

### Step 2: Remove Bad Version from PyPI

**WARNING**: PyPI does not allow re-uploading the same version number. Once deleted, that version number is permanently lost.

1. **Go to PyPI project management**
   - URL: https://pypi.org/manage/project/pyASDReader/releases/

2. **Delete the problematic version**
   - Click on the version (e.g., "1.2.3")
   - Click "Options" → "Delete"
   - Confirm deletion

3. **Verify deletion**
   ```bash
   pip index versions pyASDReader
   # The deleted version should not appear
   ```

**Alternative**: If users can be warned not to use the version, you may leave it and release a fixed version instead.

### Step 3: Prepare Rollback Release

1. **Checkout the last good version**
   ```bash
   git checkout main
   git pull origin main
   git checkout $LAST_GOOD_VERSION
   ```

2. **Determine new version number**

   Since PyPI versions cannot be reused:
   - If rolling back from `v1.2.3` to `v1.2.2`, release as `v1.2.4`
   - The new version re-publishes the last good code with a new version number

3. **Update CHANGELOG.md**

   ```bash
   # Switch to dev branch to update CHANGELOG
   git checkout dev
   git pull origin dev

   # Edit CHANGELOG.md
   ```

   Add entry:
   ```markdown
   ## [1.2.4] - 2025-10-07

   ### Fixed
   - **ROLLBACK**: Reverted to v1.2.2 due to critical bug in v1.2.3
   - Issue: [Brief description of the problem]
   - Affects: [Affected functionality]
   - Resolution: [How the issue will be properly fixed]

   ### Note
   Version 1.2.3 has been removed from PyPI due to [critical issue].
   This release restores the stable v1.2.2 codebase.
   ```

4. **Commit CHANGELOG update**
   ```bash
   git add CHANGELOG.md
   git commit -m "docs: Document v1.2.4 rollback release"
   ```

### Step 4: Create Rollback Release

#### Option A: Using Automated Script (Recommended)

```bash
# 1. Merge CHANGELOG to main
git checkout main
git merge dev
git push origin main

# 2. Create tag from last good version
git checkout v1.2.2
git tag -a v1.2.4 -m "Rollback release: restores v1.2.2 code

This is a rollback release due to critical issues in v1.2.3.

Issues fixed by rollback:
- [List critical issues]

Version 1.2.3 has been removed from PyPI.

This release restores the stable v1.2.2 codebase while maintaining
version progression (cannot reuse v1.2.2 on PyPI)."

# 3. Push tag (triggers CI/CD)
git push origin v1.2.4
```

#### Option B: Manual Release

```bash
# 1. Checkout last good version
git checkout v1.2.2

# 2. Build package
python -m build

# 3. Upload to PyPI
python -m twine upload dist/*

# 4. Create GitHub release manually
# Go to: https://github.com/KaiTastic/pyASDReader/releases/new
# Tag: v1.2.4
# Title: "v1.2.4 - Rollback Release"
# Description: [Include rollback details]
```

### Step 5: Verify Rollback

```bash
# 1. Wait for PyPI to update (2-5 minutes)

# 2. Test installation in clean environment
python -m venv test_env
source test_env/bin/activate
pip install pyASDReader

# 3. Verify version
python -c "from pyASDReader import __version__; print(__version__)"
# Should show: 1.2.4

# 4. Run smoke tests
python -c "from pyASDReader import ASDFile; print('Import successful')"
```

### Step 6: Sync Branches

```bash
# 1. Update main branch
git checkout main
git merge v1.2.4

# 2. Sync dev branch
git checkout dev
git merge main
git push origin dev
```

## Post-Rollback Actions

### Immediate (Within 24 hours)

1. **Notify users**
   - Create GitHub release announcement
   - Update README.md with warning (if needed)
   - Post to discussions/community channels

   Example announcement:
   ```markdown
   ## Important: Version 1.2.3 Rollback

   **Action Required**: If you installed v1.2.3, please upgrade to v1.2.4

   Version 1.2.3 contained [critical issue] and has been removed from PyPI.
   Version 1.2.4 restores the stable v1.2.2 codebase.

   Upgrade command:
   ```bash
   pip install --upgrade pyASDReader
   ```

   We apologize for the inconvenience. A proper fix is being developed.
   ```

2. **Monitor installations**
   - Check PyPI download statistics
   - Watch for related bug reports

3. **Create fix plan**
   - Open GitHub issue for proper fix
   - Assign developers
   - Set target release date

### Short-term (Within 1 week)

1. **Root cause analysis**
   - Document what went wrong
   - Identify gaps in testing
   - Update test cases

2. **Implement proper fix**
   - Create fix branch
   - Add regression tests
   - Thorough code review

3. **Enhanced testing**
   - Run on multiple platforms
   - Test with various Python versions
   - Consider beta testing with volunteers

4. **Release fixed version** (e.g., v1.2.5)
   ```bash
   # After fix is ready and tested
   git checkout dev
   # ... make fixes ...
   bash scripts/release.sh patch
   ```

### Long-term

1. **Update processes**
   - Add checks to prevent similar issues
   - Enhance CI/CD tests
   - Improve review process

2. **Document lessons learned**
   - Add to project documentation
   - Share with team
   - Update testing guidelines

## Prevention Strategies

### Before Releasing

1. **Comprehensive testing**
   ```bash
   # Run full test suite
   pytest tests/ -v

   # Test on multiple Python versions
   tox

   # Test installation from TestPyPI
   pip install --index-url https://test.pypi.org/simple/ pyASDReader
   ```

2. **Code review**
   - At least one other developer reviews
   - Focus on critical paths
   - Check for breaking changes

3. **TestPyPI validation**
   - Always publish to TestPyPI first
   - Test in clean environment
   - Wait 24-48 hours before PyPI

4. **Gradual rollout** (for major changes)
   - Beta/RC releases
   - Community testing
   - Monitor early adopters

### Monitoring After Release

1. **Watch for issues**
   - Monitor GitHub issues (first 48 hours critical)
   - Check PyPI download errors
   - Review user feedback

2. **Quick response plan**
   - Have rollback procedure ready
   - Team available for 24-48 hours
   - Clear communication channels

3. **Usage analytics**
   - Track download counts
   - Monitor error reports
   - Watch for unusual patterns

## Emergency Contacts

- **Project Maintainer**: caokai_cgs@163.com
- **GitHub Issues**: https://github.com/KaiTastic/pyASDReader/issues
- **PyPI Support**: https://pypi.org/help/

## Additional Resources

- [PyPI Package Management](https://pypi.org/manage/project/pyASDReader/)
- [GitHub Releases](https://github.com/KaiTastic/pyASDReader/releases)
- [VERSION_MANAGEMENT.md](../VERSION_MANAGEMENT.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)

## Rollback Checklist

Use this checklist during an emergency rollback:

- [ ] Issue documented in GitHub
- [ ] Last good version identified
- [ ] Stakeholders notified
- [ ] Bad version deleted from PyPI (if necessary)
- [ ] CHANGELOG.md updated
- [ ] New version tag created
- [ ] Release verified on PyPI
- [ ] Installation tested
- [ ] User announcement posted
- [ ] Fix plan created
- [ ] Post-mortem scheduled
- [ ] Documentation updated

---

**Last Updated**: 2025-10-07
**Version**: 1.0
