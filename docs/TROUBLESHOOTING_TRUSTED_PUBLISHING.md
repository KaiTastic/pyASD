# Trusted Publishing Troubleshooting Guide

Quick reference for diagnosing and fixing Trusted Publishing issues.

---

## 🚨 Quick Diagnostic Checklist

Run this checklist first before diving into specific errors:

```bash
# 1. Check local environment setup
bash scripts/test_environment_setup.sh

# 2. Verify GitHub CLI authentication
gh auth status

# 3. Check recent workflow runs
gh run list --workflow=publish-to-pypi.yml --limit=5

# 4. View latest run details
gh run view --log-failed
```

---

## 📊 Error Message → Solution Matrix

### Error: "Trusted publishing exchange failure"

**Full Error**:
```
Error: Trusted publishing exchange failure:
Token request failed
```

| Symptom | Root Cause | Solution |
|---------|------------|----------|
| Token request failed | PyPI not configured | [Configure PyPI Trusted Publisher](#solution-1-configure-pypi) |
| Audience claim mismatch | Wrong PyPI URL | [Update PyPA action](#solution-2-update-action) |
| Subject claim mismatch | Config mismatch | [Fix configuration mismatch](#solution-3-fix-mismatch) |

---

### Error: "Environment protection rules"

**Full Error**:
```
Error: Environment protection rules prevent this deployment
```

| Symptom | Root Cause | Solution |
|---------|------------|----------|
| Waiting for approval | Manual approval required | [Approve deployment](#solution-4-approve-deployment) |
| Branch not allowed | Tag on wrong branch | [Fix branch restriction](#solution-5-fix-branch) |
| Reviewer not configured | No reviewers set | [Add reviewers](#solution-6-add-reviewers) |

---

### Error: "Permission denied"

**Full Error**:
```
Error: Unable to get OIDC token: id-token permission required
```

| Symptom | Root Cause | Solution |
|---------|------------|----------|
| Permission missing | Missing `id-token: write` | [Add permission](#solution-7-add-permission) |
| Forked repo | OIDC unsupported in forks | [Use API token instead](#solution-8-use-token) |

---

## 🔧 Detailed Solutions

### Solution 1: Configure PyPI Trusted Publisher

**When**: First-time setup or "Token request failed"

**Steps**:

1. Log in to [PyPI](https://pypi.org/)

2. Navigate to:
   ```
   https://pypi.org/manage/project/pyASDReader/settings/publishing/
   ```

3. Click **"Add a new publisher"**

4. Fill in EXACTLY as shown:
   ```
   Owner: KaiTastic
   Repository: pyASDReader
   Workflow: publish-to-pypi.yml
   Environment: pypi-production
   ```

5. **Verify**: Check saved configuration matches character-by-character

6. **Test**: Push a tag to trigger the workflow

---

### Solution 2: Update PyPA Action

**When**: "Audience claim mismatch"

**Steps**:

1. Edit `.github/workflows/publish-to-pypi.yml`

2. Update action version:
   ```yaml
   # Change this:
   - uses: pypa/gh-action-pypi-publish@v1.8.0

   # To this:
   - uses: pypa/gh-action-pypi-publish@release/v1
   ```

3. Commit and push:
   ```bash
   git add .github/workflows/publish-to-pypi.yml
   git commit -m "fix: Update PyPA publish action to latest"
   git push
   ```

---

### Solution 3: Fix Configuration Mismatch

**When**: "Subject claim mismatch"

**Diagnosis**:

Run diagnostic to see actual token claims:
```bash
gh workflow run debug-trusted-publishing.yml
gh run watch
```

**Compare**:

| Token Claim | PyPI Configuration | Match? |
|-------------|-------------------|--------|
| repository: KaiTastic/pyASDReader | Owner: KaiTastic, Repo: pyASDReader | ? |
| workflow: publish-to-pypi.yml | Workflow: publish-to-pypi.yml | ? |
| environment: pypi-production | Environment: pypi-production | ? |

**Fix**:

Adjust PyPI configuration to match token claims (or vice versa).

---

### Solution 4: Approve Deployment

**When**: "Waiting for approval" status

**Steps**:

1. Go to GitHub Actions:
   ```
   https://github.com/KaiTastic/pyASDReader/actions
   ```

2. Click on the waiting workflow run

3. Click **"Review deployments"** button

4. Select **"Approve and deploy"**

5. Add optional comment and click **"Approve and deploy"**

---

### Solution 5: Fix Branch Restriction

**When**: "Branch not allowed" or tag not on main

**Diagnosis**:

Check where tag points:
```bash
git tag -l --contains v1.2.3
```

**If not on main**:

```bash
# Delete incorrect tag
git tag -d v1.2.3
git push origin :refs/tags/v1.2.3

# Merge to main first
git checkout main
git merge dev
git push origin main

# Re-create tag on main
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

---

### Solution 6: Add Reviewers

**When**: "No reviewers configured"

**Steps**:

1. Go to Environments:
   ```
   https://github.com/KaiTastic/pyASDReader/settings/environments
   ```

2. Click on **"pypi-production"**

3. Enable **"Required reviewers"**

4. Add yourself and/or team members

5. Click **"Save protection rules"**

---

### Solution 7: Add id-token Permission

**When**: "Permission denied" or "Unable to get OIDC token"

**Steps**:

1. Edit `.github/workflows/publish-to-pypi.yml`

2. Add permissions to publish job:
   ```yaml
   publish-to-pypi:
     name: Publish to PyPI
     runs-on: ubuntu-latest

     permissions:
       id-token: write  # Add this line

     steps:
       # ... rest of workflow
   ```

3. Commit and push changes

---

### Solution 8: Use API Token (Fallback)

**When**: OIDC not available (forked repos, etc.)

**Steps**:

See [FALLBACK_API_TOKEN_SETUP.md](./FALLBACK_API_TOKEN_SETUP.md) for complete guide.

Quick version:

1. Generate PyPI API token
2. Add to GitHub Secrets as `PYPI_API_TOKEN`
3. Update workflow:
   ```yaml
   - uses: pypa/gh-action-pypi-publish@release/v1
     with:
       password: ${{ secrets.PYPI_API_TOKEN }}
   ```

---

## 🔍 Diagnostic Workflow

Use this flowchart to systematically diagnose issues:

```
┌─────────────────────────┐
│ Does workflow trigger?  │
└───────┬─────────────────┘
        │
    No  │  Yes
        │
        ▼
┌─────────────────────────┐       ┌─────────────────────────┐
│ Check trigger config    │       │ Does it reach publish   │
│ (tags, branches)        │       │ step?                   │
└─────────────────────────┘       └───────┬─────────────────┘
                                          │
                                      No  │  Yes
                                          │
                                          ▼
                          ┌─────────────────────────┐       ┌─────────────────────────┐
                          │ Check dependencies &    │       │ What's the error?       │
                          │ previous steps          │       │                         │
                          └─────────────────────────┘       └───────┬─────────────────┘
                                                                    │
                    ┌────────────────────┬────────────────────────┼────────────────────────┐
                    │                    │                        │                        │
                    ▼                    ▼                        ▼                        ▼
    ┌───────────────────────┐  ┌───────────────────┐  ┌──────────────────┐  ┌──────────────────┐
    │ "Token request failed"│  │ "Environment..."  │  │ "Permission..."  │  │ "Claim mismatch" │
    └───────┬───────────────┘  └─────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
            │                            │                      │                      │
            ▼                            ▼                      ▼                      ▼
    ┌───────────────────────┐  ┌───────────────────┐  ┌──────────────────┐  ┌──────────────────┐
    │ Solution 1:           │  │ Solution 4-6:     │  │ Solution 7:      │  │ Solution 3:      │
    │ Configure PyPI        │  │ Fix environment   │  │ Add permission   │  │ Fix mismatch     │
    └───────────────────────┘  └───────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## 🧪 Testing Checklist

After making changes, test in this order:

### 1. Configuration Validation
```bash
bash scripts/test_environment_setup.sh
```
Expected: All green checkmarks ✓

### 2. TestPyPI Test
```bash
git checkout dev
git push origin dev
gh run watch
```
Expected: "Package published successfully"

### 3. PyPI Test (Cautious)
```bash
# Use a version that doesn't exist yet
git tag -a v0.0.0-test -m "Test"
git push origin v0.0.0-test

# Watch
gh run watch

# Clean up
git tag -d v0.0.0-test
git push origin :refs/tags/v0.0.0-test
```
Expected: "Package published successfully"

---

## 📋 Configuration Verification Checklist

Use this to manually verify all configurations are correct:

### PyPI Configuration

```
□ Logged in to pypi.org
□ Navigated to project publishing settings
□ Trusted Publisher exists
□ Owner = "KaiTastic" (exact case)
□ Repository = "pyASDReader" (exact case, not full path)
□ Workflow = "publish-to-pypi.yml" (filename only, with extension)
□ Environment = "pypi-production" (exact match, or empty if not using)
□ Status shows "Active" or "Pending first use"
```

### GitHub Environment

```
□ Navigated to repository environments
□ Environment "pypi-production" exists
□ Required reviewers configured (if desired)
□ Deployment branches set to "main" only
□ Protection rules saved
```

### Workflow File

```
□ File: .github/workflows/publish-to-pypi.yml
□ Trigger: on.push.tags includes 'v*.*.*'
□ Environment: name matches PyPI configuration
□ Permissions: id-token: write is present
□ Publish step: uses pypa/gh-action-pypi-publish@release/v1
□ No password parameter (unless using fallback)
□ verbose: true (for debugging)
```

---

## 🆘 Emergency Fallback Procedure

If Trusted Publishing is completely broken and you need to publish urgently:

### 1. Generate Emergency API Token

```
https://pypi.org/manage/account/token/
Scope: "Entire account (all projects)"
Copy token immediately
```

### 2. Add to Workflow Temporarily

```bash
# Add to GitHub Secrets
gh secret set PYPI_API_TOKEN_EMERGENCY

# Or via web UI:
# Settings → Secrets → Actions → New repository secret
```

### 3. Update Workflow

```yaml
- name: Publish to PyPI (EMERGENCY)
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.PYPI_API_TOKEN_EMERGENCY }}
    verbose: true
```

### 4. Publish

```bash
git add .github/workflows/publish-to-pypi.yml
git commit -m "temp: Emergency API token fallback"
git push

# Trigger release
git tag -a vX.X.X -m "Emergency release"
git push origin vX.X.X
```

### 5. Revert After Publishing

```bash
git revert HEAD
git push

# Rotate the emergency token
# Delete it from PyPI and GitHub Secrets
```

---

## 📞 Getting Help

If you've tried all solutions and still have issues:

### 1. Collect Diagnostic Information

```bash
# Run all diagnostics
bash scripts/test_environment_setup.sh > diagnostics.txt
gh run view --log-failed >> diagnostics.txt
git remote -v >> diagnostics.txt
git log --oneline -5 >> diagnostics.txt
```

### 2. Check Workflow Runs

```
https://github.com/KaiTastic/pyASDReader/actions
```

Copy the full error message from the failed step.

### 3. Review Documentation

- [Trusted Publishing Setup Guide](./TRUSTED_PUBLISHING_SETUP.md)
- [PyPI Trusted Publishers Docs](https://docs.pypi.org/trusted-publishers/)
- [GitHub OIDC Docs](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)

### 4. Open GitHub Issue

Include:
- Error message (full text)
- Diagnostic output
- What you've already tried
- Workflow run URL

---

## 🔗 Related Resources

- [Main Setup Guide](./TRUSTED_PUBLISHING_SETUP.md)
- [API Token Fallback Guide](./FALLBACK_API_TOKEN_SETUP.md)
- [Version Management Guide](../VERSION_MANAGEMENT.md)
- [CI/CD Workflows Documentation](./CI_CD_WORKFLOWS.md)

---

**Last Updated**: October 7, 2025
**Version**: 1.0
**Maintained by**: pyASDReader Development Team
