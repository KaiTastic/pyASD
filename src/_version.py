# Version file for pyASDReader
# This file provides access to the package version number
# Version is automatically managed by setuptools-scm from git tags
#
# IMPORTANT: The fallback version should ONLY be used in non-git environments
# (e.g., when installed from source archive without git metadata).
# In normal development and CI/CD, setuptools_scm determines the version from git tags.

try:
    from setuptools_scm import get_version
    __version__ = get_version(root='..', relative_to=__file__)
except (ImportError, LookupError):
    # Fallback version for non-git environments
    # MUST match fallback_version in pyproject.toml
    __version__ = "0.0.0"
