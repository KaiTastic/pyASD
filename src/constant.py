"""
The constant values for the ASD file format
"""
from enum import Enum


# metadata.fileVersion: ASD File Version, at byte offset 0
class FileVersion_e(Enum):
    FILE_VERSION_INVALID = 0
    FILE_VERSION_1 = 1
    FILE_VERSION_2 = 2
    FILE_VERSION_3 = 3
    FILE_VERSION_4 = 4
    FILE_VERSION_5 = 5
    FILE_VERSION_6 = 6
    FILE_VERSION_7 = 7
    FILE_VERSION_8 = 8

# metadata.instrument: Instrument type that created spectrum, at byte offset 431
class InstrumentType_e(Enum):
    UNKNOWN_INSTRUMENT = 0
    PSII_INSTRUMENT = 1
    LSVNIR_INSTRUMENT = 2
    FSVNIR_INSTRUMENT = 3
    FSFR_INSTRUMENT = 4
    FSNIR_INSTRUMENT = 5
    CHEM_INSTRUMENT = 6
    LAB_SPEC_PRO = 7
    HAND_HELD_INSTRUMENT = 10

class InstrumentModel_e(Enum):
    itVnir = 1
    # itDual
    itSwir1 = 4
    itVnirSwir1 = 5
    itSwir2 = 8
    itVnirSwir2 = 9
    itSwir1Swir2 = 12
    itVnirSwir1Swir2 = 13

# metadata.dataType: Spectrum type, at byte offset 186
class SpectraType_e(Enum):
    RAW = 0
    REFLECTANCE = 1
    RADIANCE = 2
    NO_UNITS = 3
    IRRADIANCE = 4
    QUALITY_INDEX = 5

class SignatureState_e(Enum):
    SIGNED_INVALID = -1
    UN_SIGNED = 0
    SIGNED = 1
    # VERIFIED = 2
    # NOT_VERIFIED = 3

class AuditLogType_e(Enum):
    AUDIT_EVENT_ELEMENT = "Audit_Event"
    AUDIT_APPLICATION_ELEMENT = "Audit_Application"
    AUDIT_APP_VERSION_ELEMENT = "Audit_AppVersion"
    AUDIT_FUNCTION_ELEMENT = "Audit_Function"
    AUDIT_SOURCE_ELEMENT = "Audit_Source"
    AUDIT_LOGIN_ELEMENT = "Audit_Login"
    AUDIT_NAME_ELEMENT = "Audit_Name"
    AUDIT_TIME_ELEMENT = "Audit_Time"
    AUDIT_NOTES_ELEMENT = "Audit_Notes"

class IT_ms_e(Enum):
    Invalid = 0         # 0 ms, not inluded in the original manual and codes, added by Kai Cao
    ms_8 = 8            # 8 ms, not inluded in the original manual and codes, added by Kai Cao
    ms_8_5 = 9
    ms_17 = 17
    ms_34 = 34
    ms_68 = 68
    ms_136 = 136
    ms_272 = 272
    ms_544 = 544
    ms_1088 = 1088
    ms_2176 = 2176
    ms_4352 = 4352
    ms_8704 = 8704
    ms_17408 = 17408
    ms_34816 = 34816
    ms_69632 = 69632
    ms_139264 = 139264
    ms_278528 = 278528
    ms_557056 = 557056

# metadata.dataFormat: Spectrum data format, at byte offset 199
class DataFormat_e(Enum):
    df_FLOAT = 0
    df_INTEGER = 1
    df_DOUBLE = 2
    df_UNKNOWN = 3

# metadata.calibrationSeries: Calibration type, at byte offset 432
class CalibrationType_e(Enum):
    cb_ABSOLUTE = 0         # ABS, Absolute Reflectance File;
    cb_BASE = 1             # BSE, Base File
    cb_LAMP = 2             # LMP, Lamp File
    cb_FIBER = 3            # FO, Fiber Optic File
    cb_UNKNOWN = 4          # Unknown Calibration Series

class DataType_e(Enum):
    dt_RAW_TYPE = 0          # Raw Spectrum File
    dt_REF_TYPE = 1          # Reflectance File
    dt_RAD_TYPE = 2          # Radiance File
    dt_NOUNITS_TYPE = 3      # No Units File
    dt_IRRAD_TYPE = 4        # Irradiance File
    dt_QI_TYPE = 5           # Quality Index File
    dt_TRANS_TYPE = 6        # Transmittance File
    dt_UNKNOWN_TYPE = 7      # Unknown File
    dt_ABS_TYPE = 8          # Absolute Reflectance File
    # dt_ADF_TYPE
    # dt_ADC_TYPE
    # dt_MTF_TYPE
    # dt_MTC_TYPE
    # dt_RTF_TYPE
    # dt_RTC_TYPE
    # dt_SBF_TYPE
    # dt_SBC_TYPE

# Classifier Data Type
class ClassiferDataType_e(Enum):
    SAM = 0
    GALACTIC = 1
    CAMOPREDICT = 2
    CAMOCLASSIFY = 3
    PCAZ = 4
    INFOMETRIX = 5

# Error types for flags2 in the metadata
class SaturationError_e(Enum):
    VNIR_SATURATION = 1         # Vnir Saturation    0 0 0 0  0 0 0 1   0x01
    SWIR1_SATURATION = 2        # Swir1 Saturation   0 0 0 0  0 0 1 0   0x02
    SWIR2_SATURATION = 4        # Swir2 Saturation   0 0 0 0  0 1 0 0   0x04
    SWIR1_TEC_ALARM = 8         # Swir1 Tec Alarm    0 0 0 0  1 0 0 0   0x08
    SWIR2_TEC_ALARM = 16        # Swir2 Tec Alarm    0 0 0 1  0 0 0 0   0x16
