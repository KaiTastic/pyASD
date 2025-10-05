# Version file for pyASDReader
# This file provides access to the package version number
# Version is automatically managed by setuptools-scm from git tags

try:
    from setuptools_scm import get_version
    __version__ = get_version(root='..', relative_to=__file__)
except (ImportError, LookupError):
    # Fallback version when setuptools_scm is not available
    # or when not in a git repository
    # Use actual release version as fallback
    __version__ = "1.1.0"
