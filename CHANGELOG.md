# Changelog - pyASDReader

[![PyPI version](https://img.shields.io/pypi/v/pyASDReader.svg)](https://pypi.org/project/pyASDReader/)
[![Version](https://img.shields.io/badge/version-v1.1.0-blue.svg)](https://github.com/KaiTastic/pyASDReader/releases)
[![Semantic Versioning](https://img.shields.io/badge/semver-2.0.0-green.svg)](https://semver.org/spec/v2.0.0.html)
[![Keep a Changelog](https://img.shields.io/badge/changelog-Keep%20a%20Changelog-orange.svg)](https://keepachangelog.com/en/1.0.0/)
[![Latest Release](https://img.shields.io/github/v/release/KaiTastic/pyASDReader)](https://github.com/KaiTastic/pyASDReader/releases/latest)
[![Release Date](https://img.shields.io/github/release-date/KaiTastic/pyASDReader)](https://github.com/KaiTastic/pyASDReader/releases)

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html), and the format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [1.2.0] - 2025-10-05

### Changed
- 🔄 **Package renamed** from `pyASD` to `pyASDReader` across all configuration files
- 📦 Updated package configuration in pyproject.toml with improved metadata
- 🏗️ **Major code structure refactoring** for improved readability and maintainability
- 📚 Significantly enhanced README.md with comprehensive documentation
- 🔧 Modernized dependency management with expanded dev tools
- 🧪 Improved CI/CD workflows for better reliability and accuracy
- 📝 Updated all GitHub Actions workflows to use correct branch references (main)
- 🎯 Enhanced pre-commit configuration for better code quality
- 🚀 Improved publish scripts with better error handling

### Added
- ✨ **CITATION.cff** - Formal citation support for academic use
- 📚 **VERSION_MANAGEMENT.md** - Comprehensive version management documentation
- 📝 **examples/README.md** - Detailed examples documentation
- 📝 **examples/basic_usage.py** - Practical usage examples
- 🛠️ Enhanced development dependencies:
  - Added `black>=21.0.0` for code formatting
  - Added `isort>=5.0.0` for import sorting
  - Added `build>=0.7.0` for package building
  - Added `twine>=3.0.0` for PyPI publishing
  - Added `pre-commit>=2.15.0` for git hooks
  - Added `tox>=3.20.0` for testing automation
- 🎨 Added maintainers field to project metadata
- 📦 Added "all" optional dependencies group for complete installation
- 🔗 Enhanced project URLs with Source and Issues links
- 📄 Improved README content-type specification in pyproject.toml
- ✅ Enhanced package metadata verification using importlib.metadata
- 🔍 Improved CI workflows with better testing and validation

### Removed
- ❌ **Deleted requirements.txt** (consolidated into pyproject.toml)
- ❌ **Deleted requirements-dev.txt** (consolidated into pyproject.toml)
- ❌ **Deleted setup.py** (fully migrated to pyproject.toml)

### Fixed
- 🔧 Fixed package metadata verification in CI/CD workflows
- ✅ Corrected test file naming convention (test_ASD_File_Reader.py → test_asd_file_reader.py)
- 🔗 Updated all repository URLs from pyASD to pyASDReader
- 📝 Fixed MANIFEST.in to properly include package data
- 🐛 Improved error handling in asd_file_reader.py

### Technical Improvements
- Centralized all dependencies in pyproject.toml optional-dependencies
- Improved package structure with proper namespace configuration
- Enhanced setuptools_scm integration for version management
- Better test coverage configuration targeting pyASDReader module
- Streamlined build and publish workflows

## [1.1.0] - 2025-10-05

### Fixed
- 🔴 **Critical**: Removed broken root `__init__.py` that caused ModuleNotFoundError
- 🔴 **Critical**: Fixed pyproject.toml package configuration for proper pip installation
- 🔴 **Critical**: Unified version management (removed conflicting version definitions)
- 🔴 **Critical**: Fixed GitHub Actions branch configuration (now triggers on main branch)
- 🔴 **Critical**: Removed conflicting setup.py (now using only pyproject.toml)
- 🔴 Fixed binary flag error in SWIR2_TEC_ALARM detection (0x16 → 0x10)
- 🟠 Fixed read() method to properly return False on file errors
- ⚠️ Fixed logger undefined error by adding module-level logger
- ⚠️ Added Python 3.8 compatibility with `from __future__ import annotations`

### Changed
- 🔄 **Repository renamed** from `ASD_File_Reader` to `pyASDReader` for consistency with PyPI package name
- 📦 **PyPI package name**: `pyASDReader` (install: `pip install pyASDReader`)
- 🏠 **New repository URL**: https://github.com/KaiTastic/pyASDReader
- ℹ️ **Module import**: `from pyASDReader import ASDFile` (improved package exports)
- 🧪 GitHub Actions now tests stable Python versions only (3.8-3.12, removed 3.13 and 3.x)
- 🧪 Removed `continue-on-error` from CI to properly report test failures
- 📊 Test matrix reduced from 21 to 15 combinations for better stability
- Modernized dependency management: moved all dependencies to pyproject.toml optional-dependencies
- Updated all CI/CD workflows to use `pip install -e ".[dev]"` instead of requirements files
- Enhanced README with Development Installation section
- Standardized version number to 1.1.0 across all configuration files

### Added
- ✨ Automatic version management using setuptools-scm
- 🤖 Dual GitHub Actions workflows: dev branch → TestPyPI, tag → PyPI
- 📚 Comprehensive documentation for version management and publishing
- 📝 CLAUDE.md - Guide for Claude Code integration
- 📝 VERSION_MANAGEMENT.md - Complete guide for version management with Git tags and setuptools_scm
- 📝 SECURITY.md - Security policy and vulnerability reporting guidelines
- 📝 PROJECT_IMPROVEMENT_ANALYSIS.md - Detailed analysis of 26 issues
- 📝 FIXES_APPLIED.md - First round fix summary
- 📝 ADDITIONAL_IMPROVEMENTS.md - Second round analysis of 15 issues
- 📝 ROUND2_FIXES_APPLIED.md - Second round fix summary
- ✅ Support for auto-loading files: `ASDFile(filepath)` constructor
- Added examples/ directory with basic usage examples
- Enhanced project URLs in pyproject.toml (Issues, Source, Changelog, PyPI)
- Comprehensive optional-dependencies groups: dev, docs, all

### Removed
- ❌ Deleted conflicting `setup.py`
- ❌ Deleted broken root `__init__.py`
- ❌ Deleted requirements.txt (moved to pyproject.toml)
- ❌ Deleted requirements-dev.txt (moved to pyproject.toml)
- ❌ Removed duplicate v1.0.0 git tag

### Note
- Old repository URLs will redirect automatically
- No breaking changes for existing users - all fixes are backward compatible
- Package is now fully functional (fixed from "broken" state)
- Version management now uses Git tags as single source of truth

## [1.0.1] - 2025-08-29

### Added

- Enhanced README documentation with compatibility testing details
- Improved GitHub Actions CI/CD workflow with multi-platform testing
- Extended Python version support (3.8-3.13)
- Code quality improvements and linting integration (flake8)
- Comprehensive badge system showing CI status, version, Python compatibility, and license

### Changed

- Updated documentation structure and clarity
- Improved project organization and maintainability
- Enhanced cross-platform compatibility testing

### Fixed

- Minor documentation formatting issues
- CI/CD pipeline optimizations

## [1.0.0] - 2025-03-12

### Added

- Initial release with full ASD file format support (versions 1-8)
- Comprehensive parsing capabilities for all ASD file structures:
  - Spectrum File Header and metadata
  - Spectrum Data parsing
  - Reference File Header and Reference Data
  - Classifier Data support
  - Dependent Variables handling
  - Calibration Header and calibration series data
  - Audit Log parsing
  - Digital signature support
- Benchmark testing against ASD ViewSpecPro 6.2.0 for accuracy validation
- Support for multiple ASD instrument types:
  - ASD AgriSpec, FieldSpec series, HandHeld 2, LabSpec series, TerraSpec series
- Spectral data processing capabilities:
  - Digital number extraction
  - Reflectance calculations (with derivatives)
  - Absolute reflectance
  - log(1/R) calculations
  - Transmittance support
- Comprehensive unit test suite
- MIT License
- Python package structure with setuptools support

### Features

- **File Format Compatibility**: Complete support for ASD file format versions 1 through 8
- **Multi-instrument Support**: Works with all major ASD spectroradiometer models
- **Data Extraction**: Full access to all data blocks within ASD files
- **Calculation Support**: Built-in spectral calculations and transformations
- **Validation**: Benchmark-tested against official ASD software

## Upcoming Features

- [ ] Spectral discontinuities correction (Hueni & ASD Parabolic methods)
- [ ] File format converter (ASCII export functionality)
- [ ] Enhanced radiometric and statistical tools
- [ ] Extended instrument support and metadata extraction
- [ ] PyPI package distribution
