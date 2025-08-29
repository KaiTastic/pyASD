<p align="left">
	<img src="https://img.shields.io/badge/version-1.0.1-orange.svg?style=flat-square" alt="Current Version">
	<img src="https://img.shields.io/badge/python-3.8%2B-blue.svg?style=flat-square" alt="Python 3.8+">
	<img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="MIT License">
	<a href="https://github.com/KaiTastic/ASD_File_Reader/actions/workflows/python-package.yml">
		<img src="https://github.com/KaiTastic/ASD_File_Reader/actions/workflows/python-package.yml/badge.svg?branch=main" alt="CI Status">
	</a>
</p>

# ASD File Reader

**A Python library for reading and parsing all versions of ASD binary spectral files.**

## Version Information

**Current Version:** 1.0.1

📋 **[View Full Changelog](CHANGELOG.md)** - Complete version history and detailed release notes

### What's New in v1.0.1
- Enhanced README documentation with compatibility testing details
- Improved GitHub Actions CI/CD workflow
- Multi-platform testing across Ubuntu, Windows, and macOS
- Extended Python version support (3.8-3.13)
- Code quality improvements and linting integration

## Author & License

**Author:** Kai Cao

**Contact:** caokai_cgs@163.com

**License:** MIT License (see LICENSE file)

If you use this library, please cite:

```
Cao, Kai. (2025). "ASD_File_Reader". https://github.com/KaiTastic/ASD_File_Reader
```

## Overview

`ASD_File_Reader` is designed to read and parse binary `*.asd` files produced by a wide range of ASD spectroradiometers, supporting all major versions (1-8) and instrument types. It provides access to all key data structures in ASD files, including spectrum data, metadata, calibration, reference, classifier, and more.

### Compatibility Testing

This project is automatically tested via GitHub Actions across multiple platforms and Python versions:
- **Operating Systems:** Ubuntu, Windows, macOS
- **Python Versions:** 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, and latest stable
- **Testing:** Unit tests, code linting (flake8), and integration tests

All tests must pass before any code changes are merged, ensuring robust cross-platform compatibility.

#### Detailed Test Reports
- **[Latest CI Results](https://github.com/KaiTastic/ASD_File_Reader/actions/workflows/python-package.yml)** - View current build status and logs
- **[Test Matrix Summary](https://github.com/KaiTastic/ASD_File_Reader/actions)** - See all platform/version combinations
- **[Download Test Artifacts](https://github.com/KaiTastic/ASD_File_Reader/actions)** - Access detailed HTML test reports and coverage data

> **Tip:** Click on any completed workflow run to see the detailed test matrix summary and download platform-specific test reports.

## Supported Instruments

> ASD AgriSpec, ASD FieldSpec (all models), ASD HandHeld 2, ASD LabSpec (all models), ASD TerraSpec (all models), and more. See [ASD Inc., 2017](https://www.malvernpanalytical.com/en/learn/knowledge-center/user-manuals/asd-file-format-v8) for details.

## Installation

```bash
pip install numpy
# (Optional) For development:
# pip install -r requirements.txt
```

## Quick Start

```python
from src.asd_file_reader import ASDFile

asd = ASDFile('path/to/your/file.asd')
print(asd.metadata)
print(asd.spectrumData)
# Access other attributes: referenceFileHeader, referenceData, classifierData, calibrationHeader, etc.
```

## Features

- **Full ASD file version support** (v1-v8)
- Reads all major data blocks: metadata, spectrum, reference, classifier, calibration, audit log, signature
- Handles instrument-specific fields and calibration
- Benchmark-tested against ASD ViewSpecPro 6.2.0 for precision
- Extensible for future ASD file format changes

### ASD File Structure Mapping

| ASD File Structure             | Python Attribute(s)                                |
| ------------------------------ | -------------------------------------------------- |
| Spectrum File Header           | `asdFileVersion`, `metadata`                   |
| Spectrum Data                  | `spectrumData`                                   |
| Reference File Header          | `referenceFileHeader`                            |
| Reference Data                 | `referenceData`                                  |
| Classifier Data                | `classifierData`                                 |
| Dependent Variables            | `dependants`                                     |
| Calibration Header             | `calibrationHeader`                              |
| Absolute/Base Calibration Data | `calibrationSeriesABS`, `calibrationSeriesBSE` |
| Lamp Calibration Data          | `calibrationSeriesLMP`                           |
| Fiber Optic Data               | `calibrationSeriesFO`                            |
| Audit Log                      | `auditLog`                                       |
| Signature                      | `signature`                                      |

## Testing

Unit tests are provided in the `tests/` directory. To run all tests:

```bash
python -m unittest discover -s tests
```

Benchmark tests compare results with ASD ViewSpecPro 6.2.0 for:

- Digital number (dn)
- Reflectance (and derivatives)
- Absolute reflectance
- log(1/R) (and derivatives)

Planned: radiance, irradiance, parabolic correction

## Roadmap / Upcoming Features

- [ ] Spectral discontinuities (or "step/jump"): The radiation steps in the spectral curve at the junction of the instrument, which will affect the quality of the spectral data. This correction module will provide the temperature-based **Hueni method** ([Hueni and Bialek, 2017]()) and the parabola-based **ASD Parabolic method** ([ASD Inc., 2015]()) to correct the jumps.
- [ ] File format converter (ASCII export): Although the ASD Inc. official software **ViewSpecPro** has already offered the function "Process --> ASCII Export", to enhance the flexibility of ASD File Reader, the equivalent "ASCII Export" function, or a more powerful tool/module will be provided for further spectroscopy processing.
- [ ] More radiometric and statistical tools
- [ ] Extended instrument support and metadata extraction
- [ ] Release and pipy installation package

## References

- [ASD Inc., (2017). ASD File Format: Version 8 (Revision)](https://www.malvernpanalytical.com/en/learn/knowledge-center/user-manuals/asd-file-format-v8)
- ASD Inc., Indico Version 7 File Format
- ASD Inc., (2008). ViewSpec Pro User Manual
- ASD Inc., (2015). FieldSpec 4 User Manual
- [Hueni, A. &amp; Bialek, A. (2017). &#34;Cause, Effect, and Correction of Field Spectroradiometer Interchannel Radiometric Steps.&#34; IEEE JSTARS 10(4): 1542-1551](https://ieeexplore.ieee.org/document/7819458)
