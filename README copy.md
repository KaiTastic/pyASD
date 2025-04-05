### ASD Spectral File Reader

##### To cite this repository:

Cao, Kai. (2025). "ASD_File_Reader". https://github.com/KaiTastic/ASD_File_Reader

### Repository Introduction

The repo is create for reading the all versions of *.asd binary file in Python.

##### About the *.asd file

 The *.asd file supports for:

> ASD AgriSpec, ASD FieldSpec range, ASD FieldSpec 4 Hi-Res NG, ASD FieldSpec 4 Hi-Res, ASD FieldSpec 4 Standard-Res, ASD FieldSpec 4 Wide-Res, ASD HandHeld 2 Pro, ASD HandHeld 2, ASD LabSpec range, ASD LabSpec 4 Bench, ASD LabSpec 4 Hi-Res, ASD LabSpec 4 Standard-Res, ASD TerraSpec range, ASD TerraSpec 4 Hi-Res, ASD TerraSpec 4 Standard-Res.
> [ASD Inc., (2017). ASD File Format: Version 8 (Revision): 1-10. ](https://www.malvernpanalytical.com/en/learn/knowledge-center/user-manuals/asd-file-format-v8)

###   Description for Version 1.0.0 (ASD_File_Reader.py)

| ASD File Structure             | class ASDFile()                                      |
| ------------------------------ | ---------------------------------------------------- |
| Spectrum File Header           | self.asdFileVersion; self.metadata                   |
| Spectrum Data                  | self.spectrumData                                    |
| Reference File Header          | self.referenceFileHeader                             |
| Reference Data                 | self.referenceData                                   |
| Classifier Data                | self.classifierData                                  |
| Dependent Variables            | self.dependants                                      |
| Calibration Header             | self.calibrationHeader                               |
| Absolute/Base Calibration Data | self.calibrationSeriesABS; self.calibrationSeriesBSE |
| Lamp Calibration Data          | self.calibrationSeriesLMP                            |
| Fiber Optic Data               | self.calibrationSeriesFO                             |
| Audit Log                      | self.auditLog                                        |
| Signature                      | self.signature                                       |

#### Benchmark test

As shown in the folder `.\tests\`, besides the conventional tests for packing and unpacking of the byte stream, the unit test also conducted the benchmark test for the calculation of accurate precision  results with ASD Inc. official software **ViewSpecPro 6.2.0**, in the following aspects:

##### Tested

- @dn
- @reflectance, reflectanceNoDeriv, reflectance1stDeriv, reflectance2ndDeriv
- @absoluteReflectance
- @log1R, log1RNoDeriv, log1R1stDeriv, log1R2ndDeriv

##### **Not yet finished (to be completed):**

- @radiance
- @irradiance
- @parabolic_correction

### Upcoming Features:

#### Spectral Discontinuities Correction

Spectral discontinuities, or "step/jump", are the radiation steps in the spectral curve at the junction of the instrument, which will affect the quality of the spectral data. This correction module will provide the temperature-based **Hueni method** ([Hueni and Bialek, 2017]()) and the parabola-based **ASD Parabolic method** ([ASD Inc., 2015]()) to correct the jumps.

##### Code Description

###### Solve for external temperature based on empirical formula

By querying the `coeffs` table (`src\asd_temp_corr_coeffs.mat`), we can get the `a, b, c` values, and solve T according to the `eq. 8` in ([Hueni and Bialek, 2017]()).

#### File Format Converter:

Although the ASD Inc. official software **ViewSpecPro** has already offered the function "Process --> ASCII Export", to enhance the flexibility of ASD File Reader, the equivalent "ASCII Export" function, or a more powerful tool/module will be provided for further spectroscopy processing.



#### Reference

[ASD Inc., (2017). ASD File Format: Version 8 (Revision): 1-10. ](https://www.malvernpanalytical.com/en/learn/knowledge-center/user-manuals/asd-file-format-v8)

ASD Inc., Indico Version 7 File Format: 1-9.

ASD Inc., (2008). ViewSpec Pro User Manual: 1-24.

ASD Inc., (2015). FieldSpec 4 User Manual, pp. 1-10.

[Hueni, A. and A. Bialek, (2017). "Cause, Effect, and Correction of Field Spectroradiometer Interchannel Radiometric Steps." IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing 10(4): 1542-1551](https://ieeexplore.ieee.org/document/7819458).

