"""
pyASD - A Python library for reading and parsing ASD binary spectral files

This package provides tools for reading all versions of ASD spectral files
from various ASD spectroradiometer models.
"""

from ._version import __version__
from .asd_file_reader import ASDFile
from .constant import (
    FileVersion_e,
    InstrumentType_e,
    InstrumentModel_e,
    SpectraType_e,
    SignatureState_e,
    AuditLogType_e,
    DataType_e,
    DataFormat_e,
    IT_ms_e,
    CalibrationType_e,
    SaturationError_e,
    ClassiferDataType_e,
)

__all__ = [
    "__version__",
    "ASDFile",
    # Enums from constant module
    "FileVersion_e",
    "InstrumentType_e",
    "InstrumentModel_e",
    "SpectraType_e",
    "SignatureState_e",
    "AuditLogType_e",
    "DataType_e",
    "DataFormat_e",
    "IT_ms_e",
    "CalibrationType_e",
    "SaturationError_e",
    "ClassiferDataType_e",
]
