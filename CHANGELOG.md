# Changelog

[![Version](https://img.shields.io/badge/version-v1.0.1-blue.svg)](https://github.com/KaiTastic/ASD_File_Reader/releases) [![Semantic Versioning](https://img.shields.io/badge/semver-2.0.0-green.svg)](https://semver.org/spec/v2.0.0.html) [![Keep a Changelog](https://img.shields.io/badge/changelog-Keep%20a%20Changelog-orange.svg)](https://keepachangelog.com/en/1.0.0/) [![Latest Release](https://img.shields.io/github/v/release/KaiTastic/ASD_File_Reader)](https://github.com/KaiTastic/ASD_File_Reader/releases/latest) [![Release Date](https://img.shields.io/github/release-date/KaiTastic/ASD_File_Reader)](https://github.com/KaiTastic/ASD_File_Reader/releases)

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html), and the format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
