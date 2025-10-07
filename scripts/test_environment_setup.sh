#!/bin/bash
#
# GitHub Environment Setup Verification Script
# Usage: bash scripts/test_environment_setup.sh
#
# This script verifies that the pypi-production environment is correctly configured

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "GitHub Environment Setup Verification"
echo "========================================"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}✗ GitHub CLI (gh) not installed${NC}"
    echo ""
    echo "Install with:"
    echo "  macOS: brew install gh"
    echo "  Linux: See https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    exit 1
fi

echo -e "${GREEN}✓ GitHub CLI installed${NC}"

# Check authentication
if ! gh auth status &> /dev/null; then
    echo -e "${RED}✗ Not authenticated with GitHub${NC}"
    echo ""
    echo "Authenticate with: gh auth login"
    exit 1
fi

echo -e "${GREEN}✓ Authenticated with GitHub${NC}"

# Get repository info
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo -e "${GREEN}✓ Repository: $REPO${NC}"
echo ""

# Check for pypi-production environment
echo "Checking for pypi-production environment..."

if gh api repos/$REPO/environments/pypi-production &> /dev/null; then
    echo -e "${GREEN}✓ Environment 'pypi-production' exists${NC}"

    # Get environment details
    ENV_DATA=$(gh api repos/$REPO/environments/pypi-production)

    # Check protection rules
    echo ""
    echo "Protection Rules:"
    echo "-----------------"

    # Reviewers
    REVIEWER_COUNT=$(echo "$ENV_DATA" | jq '.protection_rules[] | select(.type == "required_reviewers") | .reviewers | length' 2>/dev/null || echo "0")

    if [ "$REVIEWER_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓ Required reviewers: $REVIEWER_COUNT configured${NC}"
        echo "$ENV_DATA" | jq -r '.protection_rules[] | select(.type == "required_reviewers") | .reviewers[].reviewer.login' | sed 's/^/  - @/'
    else
        echo -e "${YELLOW}⚠ No required reviewers configured${NC}"
        echo "  Add reviewers in: https://github.com/$REPO/settings/environments"
    fi

    # Wait timer
    WAIT_TIMER=$(echo "$ENV_DATA" | jq -r '.protection_rules[] | select(.type == "wait_timer") | .wait_timer' 2>/dev/null || echo "null")

    if [ "$WAIT_TIMER" != "null" ]; then
        echo -e "${GREEN}✓ Wait timer: $WAIT_TIMER minutes${NC}"
    else
        echo -e "${YELLOW}⚠ No wait timer configured${NC}"
    fi

    # Deployment branches
    BRANCH_POLICY=$(echo "$ENV_DATA" | jq -r '.deployment_branch_policy.protected_branches' 2>/dev/null || echo "null")

    if [ "$BRANCH_POLICY" = "true" ]; then
        echo -e "${GREEN}✓ Deployment branch restriction: Enabled${NC}"
    else
        echo -e "${YELLOW}⚠ Deployment branch restriction: Not configured${NC}"
        echo "  Recommended: Restrict to 'main' branch only"
    fi

    echo ""
    echo "Environment URL: https://github.com/$REPO/settings/environments"

else
    echo -e "${RED}✗ Environment 'pypi-production' not found${NC}"
    echo ""
    echo "Create environment at:"
    echo "  https://github.com/$REPO/settings/environments"
    echo ""
    echo "Configuration needed:"
    echo "  1. Name: pypi-production"
    echo "  2. Required reviewers: Add at least 1 person"
    echo "  3. Deployment branches: Restrict to 'main'"
    exit 1
fi

# Check workflow configuration
echo ""
echo "Checking workflow configuration..."

WORKFLOW_FILE=".github/workflows/publish-to-pypi.yml"

if grep -q "environment:" "$WORKFLOW_FILE" && grep -q "name: pypi-production" "$WORKFLOW_FILE"; then
    echo -e "${GREEN}✓ Workflow correctly references 'pypi-production' environment${NC}"
else
    echo -e "${RED}✗ Workflow not configured to use environment${NC}"
    echo ""
    echo "Add to $WORKFLOW_FILE:"
    echo "  environment:"
    echo "    name: pypi-production"
    echo "    url: https://pypi.org/project/pyASDReader/"
fi

# Check trusted publishing configuration
echo ""
echo "Checking PyPI Trusted Publishing..."

if grep -q "id-token: write" "$WORKFLOW_FILE"; then
    echo -e "${GREEN}✓ Workflow configured for OIDC Trusted Publishing${NC}"
    echo "  No API token needed if PyPI is configured"
    echo ""
    echo "Verify PyPI configuration at:"
    echo "  https://pypi.org/manage/project/pyASDReader/settings/publishing/"
    echo ""
    echo "Expected configuration:"
    echo "  Owner: YOUR_USERNAME or KaiTastic"
    echo "  Repository: ASD_File_Reader"
    echo "  Workflow: publish-to-pypi.yml"
    echo "  Environment: pypi-production"
else
    echo -e "${YELLOW}⚠ Trusted Publishing not configured${NC}"
    echo "  Consider using OIDC instead of API tokens"
fi

# Summary
echo ""
echo "========================================"
echo "Summary"
echo "========================================"

if [ "$REVIEWER_COUNT" -gt 0 ] && [ "$BRANCH_POLICY" = "true" ]; then
    echo -e "${GREEN}✓ Configuration looks good!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Test with a dummy tag: git tag v0.0.0-test && git push origin v0.0.0-test"
    echo "  2. Check Actions tab for approval request"
    echo "  3. Delete test tag: git tag -d v0.0.0-test && git push origin :refs/tags/v0.0.0-test"
else
    echo -e "${YELLOW}⚠ Configuration incomplete${NC}"
    echo ""
    echo "Recommended actions:"
    [ "$REVIEWER_COUNT" -eq 0 ] && echo "  - Add required reviewers"
    [ "$BRANCH_POLICY" != "true" ] && echo "  - Restrict deployments to 'main' branch"
fi

echo ""
