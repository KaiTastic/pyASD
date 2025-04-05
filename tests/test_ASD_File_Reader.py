"""
Requirements:
This module contains tests for the ASDFile class in the ASD_File_Reader module.
"""


import os
import unittest
import struct
from datetime import datetime, timedelta
from src.ASD_File_Reader import ASDFile
# Constants
from src.constant import *


# Sample Data directory
from .test_data import (all_asd_data_files)


def setUpModule():
    """
    This function is called once before any tests in the module are run.
    It can be used to set up any resources needed for the tests.
    """
    global all_asd_data_files


    # Acquire the current working directory
    current_working_directory = os.getcwd()

    # Test file in the SampleData directory
    # all_asd_data_files = [os.path.join(current_working_directory, file_name) for file_name in all_asd_data_files]
    # print(all_asd_data_files)


class TestASDFile(unittest.TestCase):

    def setUp(self):
    
        # Test file in the SampleData directory
        # self.asd_file = ASDFile()
        pass

    # NOTE: Test for the read() method
    def test_000_00_file_paths_exist(self):

        # List of all sample data file paths to check if they exist
        for file_path in all_asd_data_files:
            with self.subTest(file_path):
                self.assertTrue(os.path.exists(file_path), f"File does not exist: {file_path}")

    def test_001_00_init(self):
        # Check if the ASDFile object is initialized correctly
        asd_file=ASDFile()
        self.assertIsNotNone(asd_file)
        # Check if the file path is set correctly
        # Check if the file stream is None initially
        for file_path in all_asd_data_files:
            with self.subTest(file_path):
                asd_file=ASDFile(file_path)
                self.assertIsNotNone(asd_file.metadata)
                self.assertIsNotNone(asd_file.spectrumData)
                self.assertIsNotNone(asd_file.referenceFileHeader)
                self.assertIsNotNone(asd_file.referenceData)
                self.assertIsNotNone(asd_file.classifierData)
                self.assertIsNotNone(asd_file._ASDFile__asdFileStream)
                self.assertEqual(type(asd_file._ASDFile__asdFileStream), bytes)

    # NOTE: Test for the "read()"" method
    def test_001_01_read(self):

        # 1 Assuming you have a valid test file
        for file_path in all_asd_data_files:
            with self.subTest(file_path):
                # Create an ASDFile object
                asd_file = ASDFile(file_path)
                offset = asd_file._ASDFile__parse_metadata(3)
                # Check if the metadata is read successfully
                self.assertIsNotNone(asd_file.metadata)
                # Check if the file version is read successfully
                self.assertIsNotNone(asd_file.metadata.asdFileVersion)
                # Check if the spectrum data is read successfully
                self.assertIsNotNone(asd_file.spectrumData)
                # Check if the reference file header is read successfully
                self.assertIsNotNone(asd_file.referenceFileHeader)
                # Check if the reference data is read successfully
                self.assertIsNotNone(asd_file.referenceData)
                # Check if the classifier data is read successfully
                self.assertIsNotNone(asd_file.classifierData)

        # 2 Assuming you have a invalid test file
        asd_file = ASDFile()
        self.assertFalse(asd_file.read('non_existent_file.asd'))
        # Check if the metadata is None
        self.assertIsNone(asd_file.metadata)
        # Check if the spectrum data is None
        self.assertIsNone(asd_file.spectrumData)
        # Check if the reference file header is None
        self.assertIsNone(asd_file.referenceFileHeader)
    
    # NOTE: Test for the "read()" method and the file version
    def test_001_02_read_file_version(self):

        # 1 Assuming you have a valid test file
        for file_path in all_asd_data_files:
            with self.subTest(file_path):
                asd_file = ASDFile(file_path)
                # Check if the file version is read successfully
                self.assertIsNotNone(asd_file.metadata.asdFileVersion)
                # Check if the file version is correct
                self.assertEqual(asd_file.metadata.asdFileVersion, FileVersion_e.FILE_VERSION_7)
        
        # 2 Assuming you have a invalid test file: not exist
        asd_file = ASDFile()
        # Check if the file is read successfully
        self.assertFalse(asd_file.read('non_existent_file.asd'))
        # Check if the metadata is None
        self.assertIsNone(asd_file.metadata)
        # Check if the spectrum data is None
        self.assertIsNone(asd_file.spectrumData)
        # Check if the reference file header is None
        self.assertIsNone(asd_file.referenceFileHeader)

        # 2 Assuming you have a invalid test file: None
        asd_file = ASDFile()
        # Check if the file is read successfully
        self.assertFalse(asd_file.read(None))
        # Check if the metadata is None
        self.assertIsNone(asd_file.metadata)
        # Check if the spectrum data is None
        self.assertIsNone(asd_file.spectrumData)
        # Check if the reference file header is None
        self.assertIsNone(asd_file.referenceFileHeader)


    # NOTE: Test for the "update()" method
    def test_002_00_update(self):
        pass

    # NOTE: Test for the "write()"" method
    def test_003_00_write(self):
        pass


#! Decorator testing is divided into 3 parts
#! 1. Directly test the decorator
#! 2. Use Mock objects to test the decorator
#! 3. Disassemble the decorator logic for testing

# NOTE: 1. Directly test the decorator
class TestASDFileCheckOffsetDecorator(unittest.TestCase):
    
    def setUp(self):
        # Setup a mock ASDFile object
        self.asd_file = ASDFile("full_file_path")
        self.asd_file._ASDFile__asdFileStream = b'\x00' * 100

    # Mock a function to test the decorator
    def test_001_00_decorator_functionality(self):

        # Mock the __check_offset decorator
        @ASDFile._ASDFile__check_offset
        def mock_function(self, offset):
            return "Valid Offset"
        
        # NOTE: The offset is set to a integer value, None
        # Test with a valid offset
        offset = 50
        self.assertEqual(mock_function(self.asd_file, offset), "Valid Offset")
        # Test with an invalid offset (greater than stream length)
        offset = 150
        self.assertEqual(mock_function(self.asd_file, offset), (None, None))
        # Test with an invalid offset (negative value)
        offset = -1
        self.assertEqual(mock_function(self.asd_file, offset), (None, None))
        # Test with an invalid offset (None)
        offset = None
        self.assertEqual(mock_function(self.asd_file, offset), (None, None))
        offset = ""
        self.assertEqual(mock_function(self.asd_file, offset), (None, None))


#! Test for the byte packing and unpacking functions:
"""
The aspects to be tested are:
1. **Basic Functionality**:
    - Ensure that the functions for packing and unpacking work correctly for standard inputs.
2. **Boundary Conditions**:
    - Test with minimum and maximum values for integers.
    - Test with empty strings and maximum length strings.
3. **Data Consistency**:
    - Verify that data remains consistent after packing and unpacking.
4. **Exception Handling**:
    - Check how the functions handle invalid inputs, such as incorrect data types or corrupted byte streams.
5. **Performance**:
    - Assess performance with large data sets.
6. **Complex Data Structures**:
    - Test with more complex data structures, such as nested dictionaries or lists.
7. **Edge Cases**:
    - Test with edge cases, such as packing and unpacking with special characters or null bytes.
"""

class TestASDFileParseMetadata(unittest.TestCase):

    def test_001_parse_metadata(self):
        # Check if the ASDFile object is initialized correctly
        asd_file=ASDFile()
        self.assertIsNotNone(asd_file)
        # Check if metadata is parsed correctly with every file
        for file_path in all_asd_data_files:
            with self.subTest(file_path):
                with open(file_path, 'rb') as f:
                    asd_file._ASDFile__asdFileStream = f.read()
                    # Check if the file stream is set correctly
                    self.assertIsNotNone(asd_file._ASDFile__asdFileStream)
                    self.assertEqual(type(asd_file._ASDFile__asdFileStream), bytes)
                    # Check if the metadata is set correctly
                    offset = asd_file._ASDFile__parse_metadata(3)
                    # Assertions
                    self.assertIsNotNone(asd_file.metadata)
                    self.assertEqual(offset, 484)

                    # Check if the file version is set correctly
                    self.assertIsNotNone(asd_file.metadata.asdFileVersion)

                    # Check if the comments are set correctly
                    self.assertIsNotNone(asd_file.metadata.comments)
                    self.assertEqual(type(asd_file.metadata.comments), bytes)

                    # Check if when_datetime is set correctly
                    self.assertIsNotNone(asd_file.metadata.when_datetime)
                    self.assertEqual(type(asd_file.metadata.when_datetime), datetime)

                    # Check if the daylighSaving is set correctly
                    self.assertIsNotNone(asd_file.metadata.daylighSavingsFlag)
                    self.assertEqual(type(asd_file.metadata.daylighSavingsFlag), int)
                    # NOTE: The daylighSaving is set to 0 or 1
                    # TODO: validate the content
                    self.assertIn(asd_file.metadata.daylighSavingsFlag, [0, 1])

                    # Check if the program version is set correctly
                    self.assertIsNotNone(asd_file.metadata.programVersion)
                    self.assertEqual(type(asd_file.metadata.programVersion), str)
                    self.assertIn(asd_file.metadata.programVersion, ["6.4", "6.0", "5.7", "5.6"])

                    # Check if the file version is set correctly
                    self.assertIsNotNone(asd_file.metadata.asdFileVersion)
                    self.assertEqual(type(asd_file.metadata.asdFileVersion), FileVersion_e)
                    # NOTE: 文件版本目前有 6，7，8
                    self.assertIn(asd_file.metadata.asdFileVersion.value, [6, 7, 8])

                    # Check if the iTime is set correctly
                    self.assertIsNotNone(asd_file.metadata.iTime)
                    self.assertEqual(type(asd_file.metadata.iTime), int)
                    # print(asd_file.metadata.iTime)
                    self.assertIn(asd_file.metadata.iTime, [0])


                    # Check if the darkCorrected is set correctly
                    self.assertIsNotNone(asd_file.metadata.darkCorrected)
                    self.assertEqual(type(asd_file.metadata.darkCorrected), bool)
                    self.assertIn(asd_file.metadata.darkCorrected, [True])

                    # Check if the darkTime is set correctly
                    self.assertIsNotNone(asd_file.metadata.darkTime)
                    self.assertEqual(type(asd_file.metadata.darkTime), datetime)
                    # TODO: validate the content

                    # Check if the dataType is set correctly
                    self.assertIsNotNone(asd_file.metadata.dataType)
                    self.assertEqual(type(asd_file.metadata.dataType), DataType_e)
                    self.assertIn(asd_file.metadata.dataType.value, [0, 1, 2])

                    # Check if the refercenceTime

                    # referenceTime
                    self.assertIsNotNone(asd_file.metadata.referenceTime)
                    self.assertEqual(type(asd_file.metadata.referenceTime), datetime)
                    # TODO: validate the content

                    # channel1Wavelength
                    self.assertIsNotNone(asd_file.metadata.channel1Wavelength)
                    self.assertEqual(type(asd_file.metadata.channel1Wavelength), float)
                    self.assertEqual(asd_file.metadata.channel1Wavelength, 350.0)

                    # wavelengthStep
                    self.assertIsNotNone(asd_file.metadata.wavelengthStep)
                    self.assertEqual(type(asd_file.metadata.wavelengthStep), float)
                    self.assertEqual(asd_file.metadata.wavelengthStep, 1.0)

                    # dataFormat
                    self.assertIsNotNone(asd_file.metadata.dataFormat)
                    self.assertEqual(type(asd_file.metadata.dataFormat), DataFormat_e)
                    self.assertIn(asd_file.metadata.dataFormat.value, [0, 2])

                    # old_darkCurrentCount
                    self.assertIsNotNone(asd_file.metadata.old_darkCurrentCount)
                    self.assertEqual(type(asd_file.metadata.old_darkCurrentCount), int)
                    self.assertEqual(asd_file.metadata.old_darkCurrentCount, 0)

                    # old_refCount
                    self.assertIsNotNone(asd_file.metadata.old_refCount)
                    self.assertEqual(type(asd_file.metadata.old_refCount), int)
                    self.assertEqual(asd_file.metadata.old_refCount, 0)

                    # old_sampleCount
                    self.assertIsNotNone(asd_file.metadata.old_sampleCount)
                    self.assertEqual(type(asd_file.metadata.old_sampleCount), int)
                    self.assertEqual(asd_file.metadata.old_sampleCount, 0)

                    # application
                    self.assertIsNotNone(asd_file.metadata.application)
                    self.assertEqual(type(asd_file.metadata.application), int)
                    self.assertIn(asd_file.metadata.application, [0, 6])

                    # channels
                    self.assertIsNotNone(asd_file.metadata.channels)
                    self.assertEqual(type(asd_file.metadata.channels), int)
                    self.assertIn(asd_file.metadata.channels, [2151.0])

                    # appData
                    self.assertIsNotNone(asd_file.metadata.appData)
                    self.assertEqual(type(asd_file.metadata.appData), bytes)
                    # TODO: validate the content

                    # gpsData
                    self.assertIsNotNone(asd_file.metadata.gpsData)
                    self.assertEqual(type(asd_file.metadata.gpsData), bytes)
                    # TODO: validate the content

                    # intergrationTime_ms
                    self.assertIsNotNone(asd_file.metadata.intergrationTime_ms)
                    self.assertEqual(type(asd_file.metadata.intergrationTime_ms), IT_ms_e)
                    # TODO: validate the content

                    # fo
                    self.assertIsNotNone(asd_file.metadata.fo)
                    self.assertEqual(type(asd_file.metadata.fo), int)
                    # TODO: validate the content

                    # darkCurrentCorrention
                    self.assertIsNotNone(asd_file.metadata.darkCurrentCorrention)
                    self.assertEqual(type(asd_file.metadata.darkCurrentCorrention), int)
                    # TODO: validate the content

                    # calibrationSeries
                    self.assertIsNotNone(asd_file.metadata.calibrationSeries)
                    self.assertEqual(type(asd_file.metadata.calibrationSeries), CalibrationType_e)
                    # TODO: validate the content

                    # instrumentNum
                    self.assertIsNotNone(asd_file.metadata.instrumentNum)
                    self.assertEqual(type(asd_file.metadata.instrumentNum), int)
                    # TODO: validate the content

                    # yMin
                    self.assertIsNotNone(asd_file.metadata.yMin)
                    self.assertEqual(type(asd_file.metadata.yMin), float)
                    # TODO: validate the content

                    # yMax
                    self.assertIsNotNone(asd_file.metadata.yMax)
                    self.assertEqual(type(asd_file.metadata.yMax), float)
                    # TODO: validate the content

                    # xMin
                    self.assertIsNotNone(asd_file.metadata.xMin)
                    self.assertEqual(type(asd_file.metadata.xMin), float)
                    # TODO: validate the content

                    # xMax
                    self.assertIsNotNone(asd_file.metadata.xMax)
                    self.assertEqual(type(asd_file.metadata.xMax), float)
                    # TODO: validate the content

                    # ipNumBits
                    self.assertIsNotNone(asd_file.metadata.ipNumBits)
                    self.assertEqual(type(asd_file.metadata.ipNumBits), int)
                    # TODO: validate the content

                    # xMode
                    self.assertIsNotNone(asd_file.metadata.xMode)
                    self.assertEqual(type(asd_file.metadata.xMode), int)
                    # TODO: validate the content

                    # flags1
                    self.assertIsNotNone(asd_file.metadata.flags1)
                    self.assertEqual(type(asd_file.metadata.flags1), int)
                    # TODO: validate the content

                    # NOTE: flags2: SaturationError_e
                    self.assertIsNotNone(asd_file.metadata.flags2)
                    self.assertEqual(type(asd_file.metadata.flags2), list)
                    if asd_file.metadata.flags2 != []:
                        for flag in asd_file.metadata.flags2:
                            self.assertIn(flag.value, [1, 2, 4, 8, 16])

                    # flags3
                    self.assertIsNotNone(asd_file.metadata.flags3)
                    self.assertEqual(type(asd_file.metadata.flags3), int)
                    # TODO: validate the content

                    # flags4
                    self.assertIsNotNone(asd_file.metadata.flags4)
                    self.assertEqual(type(asd_file.metadata.flags4), int)
                    # TODO: validate the content

                    # darkCurrentCount
                    self.assertIsNotNone(asd_file.metadata.darkCurrentCount)
                    self.assertEqual(type(asd_file.metadata.darkCurrentCount), int)
                    # TODO: validate the content

                    # refCount
                    self.assertIsNotNone(asd_file.metadata.refCount)
                    self.assertEqual(type(asd_file.metadata.refCount), int)
                    # TODO: validate the content

                    # sampleCount
                    self.assertIsNotNone(asd_file.metadata.sampleCount)
                    self.assertEqual(type(asd_file.metadata.sampleCount), int)
                    # TODO: validate the content

                    # instrument
                    self.assertIsNotNone(asd_file.metadata.instrument)
                    self.assertEqual(type(asd_file.metadata.instrument), InstrumentType_e)
                    # TODO: validate the content

                    # calBulbID
                    self.assertIsNotNone(asd_file.metadata.calBulbID)
                    self.assertEqual(type(asd_file.metadata.calBulbID), int)
                    # TODO: validate the content

                    # swir1Gain
                    self.assertIsNotNone(asd_file.metadata.swir1Gain)
                    self.assertEqual(type(asd_file.metadata.swir1Gain), int)
                    # TODO: validate the content

                    # swir2Gain
                    self.assertIsNotNone(asd_file.metadata.swir2Gain)
                    self.assertEqual(type(asd_file.metadata.swir2Gain), int)
                    # TODO: validate the content

                    # swir1Offset
                    self.assertIsNotNone(asd_file.metadata.swir1Offset)
                    self.assertEqual(type(asd_file.metadata.swir1Offset), int)
                    # TODO: validate the content

                    # swir2Offset
                    self.assertIsNotNone(asd_file.metadata.swir2Offset)
                    self.assertEqual(type(asd_file.metadata.swir2Offset), int)
                    # TODO: validate the content

                    # splice1_wavelength
                    self.assertIsNotNone(asd_file.metadata.splice1_wavelength)
                    self.assertEqual(type(asd_file.metadata.splice1_wavelength), float)
                    # TODO: validate the content

                    # splice2_wavelength
                    self.assertIsNotNone(asd_file.metadata.splice2_wavelength)
                    self.assertEqual(type(asd_file.metadata.splice2_wavelength), float)
                    # TODO: validate the content

                    # smartDetectorType
                    self.assertIsNotNone(asd_file.metadata.smartDetectorType)
                    self.assertEqual(type(asd_file.metadata.smartDetectorType), bytes)
                    # TODO: validate the content

                    # spare1
                    self.assertIsNotNone(asd_file.metadata.spare1)
                    self.assertEqual(type(asd_file.metadata.spare1), int)
                    # TODO: validate the content

                    # spare2
                    self.assertIsNotNone(asd_file.metadata.spare2)
                    self.assertEqual(type(asd_file.metadata.spare2), int)
                    # TODO: validate the content

                    # spare3
                    self.assertIsNotNone(asd_file.metadata.spare3)
                    self.assertEqual(type(asd_file.metadata.spare3), int)
                    # TODO: validate the content

                    # spare4
                    self.assertIsNotNone(asd_file.metadata.spare4)
                    self.assertEqual(type(asd_file.metadata.spare4), int)
                    # TODO: validate the content

                    # spare5
                    self.assertIsNotNone(asd_file.metadata.spare5)
                    self.assertEqual(type(asd_file.metadata.spare5), int)
                    # TODO: validate the content


class TestASDFileParseSpectrumData(unittest.TestCase):

    def test_001_parse_spectrum_data(self):
        # Check if the ASDFile object is initialized correctly
        asd_file=ASDFile()
        self.assertIsNotNone(asd_file)
        # Check if the file path is set correctly
        # Check if the file stream is None initially
        for file_path in all_asd_data_files:
            with self.subTest(file_path):
                with open(file_path, 'rb') as f:
                    asd_file._ASDFile__asdFileStream = f.read()
                    # Check if the file stream is set correctly
                    self.assertIsNotNone(asd_file._ASDFile__asdFileStream)
                    self.assertEqual(type(asd_file._ASDFile__asdFileStream), bytes)
                    # Check if the metadata is set correctly
                    asd_file._ASDFile__parse_metadata(3)

                    # Check if the spectrum data is set correctly
                    offset = asd_file._ASDFile__parse_spectrumData(484)
                    # Assertions
                    self.assertIsNotNone(asd_file.spectrumData)
                    self.assertEqual(offset, 17692)

class TestASDFileParseReferenceFileHeader(unittest.TestCase):

    def setUp(self):
        # Check if the ASDFile object is initialized correctly
        self.asd_file=ASDFile()
        self.assertIsNotNone(self.asd_file)

    def tearDown(self):
        # Clean up the ASDFile object
        del self.asd_file

    def test_001_parse_reference_file_header(self):
        # Check if the file stream is None initially
        for file_path in all_asd_data_files:
            with self.subTest(file_path):
                with open(file_path, 'rb') as f:
                    self.asd_file._ASDFile__asdFileStream = f.read()
                    # Check if the file stream is set correctly
                    self.assertIsNotNone(self.asd_file._ASDFile__asdFileStream)
                    self.assertEqual(type(self.asd_file._ASDFile__asdFileStream), bytes)
                    # Check if the metadata is set correctly
                    self.asd_file._ASDFile__parse_metadata(3)

                    # Check if the reference file header is set correctly
                    offset = self.asd_file._ASDFile__parse_referenceFileHeader(17692)

                    # Assertions
                    self.assertIsNotNone(self.asd_file.referenceFileHeader)
                    # TODO: Check if the reference file header offset
                    # self.assertEqual(offset, 17712)

    def test_002_read_reference_file_header(self):
        # read and parse the reference file header
        for file_path in all_asd_data_files:
            with self.subTest(file_path):
                self.asd_file.read(file_path)
                # Check if the reference file header is set correctly
                self.assertIsNotNone(self.asd_file.referenceFileHeader)
                # self.asd_file.referenceFileHeader

                # referenceFlag
                self.assertIsNotNone(self.asd_file.referenceFileHeader.referenceFlag)
                self.assertEqual(type(self.asd_file.referenceFileHeader.referenceFlag), bool)
                self.assertIn(self.asd_file.referenceFileHeader.referenceFlag, [True, False])

                # NOTE: referenceTime: double float
                self.assertIsNotNone(self.asd_file.referenceFileHeader.referenceTime)
                self.assertEqual(type(self.asd_file.referenceFileHeader.referenceTime), datetime)
                # print(self.asd_file.referenceFileHeader.referenceTime)


                # NOTE: spectrumTime: double float
                self.assertIsNotNone(self.asd_file.referenceFileHeader.spectrumTime)
                self.assertEqual(type(self.asd_file.referenceFileHeader.spectrumTime), datetime)
                # print(self.asd_file.referenceFileHeader.spectrumTime)

                # NOTE: the reference tiem is not equal to the spectrum time
                self.assertNotEqual(self.asd_file.referenceFileHeader.referenceTime, self.asd_file.referenceFileHeader.spectrumTime)

                # referenceDescription
                self.assertIsNotNone(self.asd_file.referenceFileHeader.referenceDescription)
                self.assertEqual(type(self.asd_file.referenceFileHeader.referenceDescription), str)

                # byteStream
                self.assertIsNotNone(self.asd_file.referenceFileHeader.byteStream)

                # byteStreamLength


class TestASDFileParseReferenceData(unittest.TestCase):

    def setUp(self):
        # Check if the ASDFile object is initialized correctly
        self.asd_file=ASDFile()
        self.assertIsNotNone(self.asd_file)

    def tearDown(self):
        # Clean up the ASDFile object
        del self.asd_file

    def test_001_parse_reference_data(self):

        # Test files in the SampleData directory
        for file_path in all_asd_data_files:
            with self.subTest(file_path):
                with open(file_path, 'rb') as f:
                    asd_file = ASDFile(file_path)
                    asd_file._ASDFile__asdFileStream = f.read()
                    # Check if the file stream is set correctly
                    self.assertIsNotNone(asd_file._ASDFile__asdFileStream)
                    self.assertEqual(type(asd_file._ASDFile__asdFileStream), bytes)
                    # Check if the metadata is set correctly
                    asd_file._ASDFile__parse_metadata(3)

                    # Check if the reference data is set correctly
                    offset = asd_file._ASDFile__parse_referenceData(17712)
                    # Assertions
                    self.assertIsNotNone(asd_file.referenceData)
                    self.assertEqual(offset, 34920)

                asd_file = ASDFile(file_path)
                with open(file_path, 'rb') as f:
                    asd_file._ASDFile__asdFileStream = f.read()
                    asd_file._ASDFile__parse_metadata(3)

                    #! May not start with 17712
                    # Check if the reference data is set correctly
                    # offset = asd_file._ASDFile__parse_referenceData(17712)
                    # self.assertIsNotNone(asd_file.referenceData)
                    # self.assertEqual(offset, 34920)


class TestASDFileParseClassifierData(unittest.TestCase):

    def setUp(self):
        # Check if the ASDFile object is initialized correctly
        self.asd_file=ASDFile()
        self.assertIsNotNone(self.asd_file)

    def tearDown(self):
        # Clean up the ASDFile object
        del self.asd_file

    def test_001_parse_classifier_data(self):
        # Check if the file stream is None initially
        for file_path in all_asd_data_files:
            with self.subTest(file_path):
                self.asd_file.read(file_path)

                # Assertions
                self.assertIsNotNone(self.asd_file.classifierData)
                # TODO: Check if the Classifier Data offset
                # self.assertEqual(offset, 17712)

                # yCode
                self.assertIsNotNone(self.asd_file.classifierData.yCode)
                self.assertEqual(type(self.asd_file.classifierData.yCode), int)

                # yModelType
                self.assertIsNotNone(self.asd_file.classifierData.yModelType)
                self.assertEqual(type(self.asd_file.classifierData.yModelType), int)
                self.assertIn(self.asd_file.classifierData.yModelType, [0, 2])

                # title_str
                self.assertIsNotNone(self.asd_file.classifierData.title)
                self.assertEqual(type(self.asd_file.classifierData.title), str)

                # subtitle_str
                self.assertIsNotNone(self.asd_file.classifierData.subtitle)
                self.assertEqual(type(self.asd_file.classifierData.subtitle), str)
                
                # productName_str
                self.assertIsNotNone(self.asd_file.classifierData.productName)
                self.assertEqual(type(self.asd_file.classifierData.productName), str)
                
                # vendor_str
                self.assertIsNotNone(self.asd_file.classifierData.vendor)
                self.assertEqual(type(self.asd_file.classifierData.vendor), str)

                # lotNumber_str
                self.assertIsNotNone(self.asd_file.classifierData.lotNumber)
                self.assertEqual(type(self.asd_file.classifierData.lotNumber), str)

                # sample__str
                self.assertIsNotNone(self.asd_file.classifierData.sample)
                self.assertEqual(type(self.asd_file.classifierData.sample), str)

                # modelName_str
                self.assertIsNotNone(self.asd_file.classifierData.modelName)
                self.assertEqual(type(self.asd_file.classifierData.modelName), str)

                # operator_str
                self.assertIsNotNone(self.asd_file.classifierData.operator)
                self.assertEqual(type(self.asd_file.classifierData.operator), str)
                
                # dateTime_str
                self.assertIsNotNone(self.asd_file.classifierData.dateTime)
                self.assertEqual(type(self.asd_file.classifierData.dateTime), str)

                # instrument_str
                self.assertIsNotNone(self.asd_file.classifierData.instrument)
                self.assertEqual(type(self.asd_file.classifierData.instrument), str)

                # serialNumber_str
                self.assertIsNotNone(self.asd_file.classifierData.serialNumber)
                self.assertEqual(type(self.asd_file.classifierData.serialNumber), str)

                # displayMode_str
                self.assertIsNotNone(self.asd_file.classifierData.displayMode)
                self.assertEqual(type(self.asd_file.classifierData.displayMode), str)

                # comments_str
                self.assertIsNotNone(self.asd_file.classifierData.comments)
                self.assertEqual(type(self.asd_file.classifierData.comments), str)
                
                # units_str
                self.assertIsNotNone(self.asd_file.classifierData.units)
                self.assertEqual(type(self.asd_file.classifierData.units), str)

                # filename_str
                self.assertIsNotNone(self.asd_file.classifierData.filename)
                self.assertEqual(type(self.asd_file.classifierData.filename), str)

                # username_str
                self.assertIsNotNone(self.asd_file.classifierData.username)
                self.assertEqual(type(self.asd_file.classifierData.username), str)

                # reserved1_str
                self.assertIsNotNone(self.asd_file.classifierData.reserved1)
                self.assertEqual(type(self.asd_file.classifierData.reserved1), str)

                # reserved2_str
                self.assertIsNotNone(self.asd_file.classifierData.reserved2)
                self.assertEqual(type(self.asd_file.classifierData.reserved2), str)
                
                # reserved3_str
                self.assertIsNotNone(self.asd_file.classifierData.reserved3)
                self.assertEqual(type(self.asd_file.classifierData.reserved3), str)

                # reserved4_str
                self.assertIsNotNone(self.asd_file.classifierData.reserved4)
                self.assertEqual(type(self.asd_file.classifierData.reserved4), str)

                # constituantCount_int
                self.assertIsNotNone(self.asd_file.classifierData.constituantCount)
                self.assertEqual(type(self.asd_file.classifierData.constituantCount), int)
                self.assertIn(self.asd_file.classifierData.constituantCount, [0, 1])


class TestASDFileParseDependentVariables(unittest.TestCase):

    def setUp(self):
        # Check if the ASDFile object is initialized correctly
        self.asd_file=ASDFile()
        self.assertIsNotNone(self.asd_file)

    def tearDown(self):
        # Clean up the ASDFile object
        del self.asd_file

    def test_001_parse_dependent_variable(self):
        for file_path in all_asd_data_files:
            with self.subTest(file_path):
                self.asd_file.read(file_path)
                # NOTE: The dependent variables are only available in version 7 and above
                if self.asd_file.metadata.asdFileVersion.value >= 7:

                    # Assertions
                    self.assertIsNotNone(self.asd_file.dependants)

                    # saveDependentVariables
                    self.assertIsNotNone(self.asd_file.dependants.saveDependentVariables)
                    self.assertEqual(type(self.asd_file.dependants.saveDependentVariables), bool)

                    # dependentVariableCount
                    self.assertIsNotNone(self.asd_file.dependants.dependentVariableCount)
                    self.assertEqual(type(self.asd_file.dependants.dependentVariableCount), int)
                    # dependentVariableLabels
                    self.assertIsNotNone(self.asd_file.dependants.dependentVariableLabels)
                    self.assertEqual(type(self.asd_file.dependants.dependentVariableLabels), list)
                    # dependentVariableValue
                    self.assertIsNotNone(self.asd_file.dependants.dependentVariableValue)
                    self.assertEqual(type(self.asd_file.dependants.dependentVariableValue), list)


class TestASDFileParsecalibrationHeader(unittest.TestCase):

    def setUp(self):
        # Check if the ASDFile object is initialized correctly
        self.asd_file=ASDFile()
        self.assertIsNotNone(self.asd_file)

    def tearDown(self):
        # Clean up the ASDFile object
        del self.asd_file

    def test_001_parse_calibration_data(self):
        for file_path in all_asd_data_files:
            with self.subTest(file_path):
                self.asd_file.read(file_path)
                # NOTE: The dependent variables are only available in version 7 and above
                if self.asd_file.metadata.asdFileVersion.value >= 7:

                    # calibrationNum
                    self.assertIsNotNone(self.asd_file.calibrationHeader.calibrationNum)
                    self.assertEqual(type(self.asd_file.calibrationHeader.calibrationNum), int)

                    # calibrationSeries
                    self.assertIsNotNone(self.asd_file.calibrationHeader.calibrationSeries)
                    self.assertEqual(type(self.asd_file.calibrationHeader.calibrationSeries), list)

                    if self.asd_file.calibrationHeader.calibrationSeries != []:
                        for series in self.asd_file.calibrationHeader.calibrationSeries:
                            cbtype_e, name, cbIntergrationTime, cbSwir1Gain, cbWwir2Gain = series

                            # cbtype_e
                            self.assertIsNotNone(cbtype_e)
                            self.assertEqual(type(cbtype_e), CalibrationType_e)

                            # name
                            self.assertIsNotNone(name)
                            self.assertEqual(type(name), bytes)

                            # cbIntergrationTime
                            self.assertIsNotNone(cbIntergrationTime)
                            self.assertEqual(type(cbIntergrationTime), IT_ms_e)

                            # cbSwir1Gain
                            self.assertIsNotNone(cbSwir1Gain)
                            self.assertEqual(type(cbSwir1Gain), int)

                            # cbWwir2Gain
                            self.assertIsNotNone(cbWwir2Gain)
                            self.assertEqual(type(cbWwir2Gain), int)



class TestASDFileParseAuditLog(unittest.TestCase):

    def setUp(self):
        # Check if the ASDFile object is initialized correctly
        self.asd_file=ASDFile()
        self.assertIsNotNone(self.asd_file)

    def tearDown(self):
        # Clean up the ASDFile object
        del self.asd_file

    def test_001_parse_audit_log(self):
        for file_path in all_asd_data_files:
            with self.subTest(file_path):
                self.asd_file.read(file_path)
                # NOTE: The dependent variables are only available in version 7 and above
                if self.asd_file.metadata.asdFileVersion.value >= 7:
                    # Assertions
                    # NOTE: Probebly the audit log is not available in all files
                    if self.asd_file.auditLog is not None:

                        # auditCount
                        self.assertIsNotNone(self.asd_file.auditLog.auditCount)
                        self.assertEqual(type(self.asd_file.auditLog.auditCount), int)

                        # auditEvents
                        self.assertIsNotNone(self.asd_file.auditLog.auditEvents)
                        self.assertEqual(type(self.asd_file.auditLog.auditEvents), list)



class TestASDFileParseSignature(unittest.TestCase):

    def setUp(self):
        # Check if the ASDFile object is initialized correctly
        self.asd_file=ASDFile()
        self.assertIsNotNone(self.asd_file)

    def tearDown(self):
        # Clean up the ASDFile object
        del self.asd_file

    def test_001_parse_signature(self):
        for file_path in all_asd_data_files:
            with self.subTest(file_path):
                self.asd_file.read(file_path)
                # NOTE: The dependent variables are only available in version 7 and above
                if self.asd_file.metadata.asdFileVersion.value >= 7:
                    # Assertions
                    # NOTE: Probebly the audit log is not available in all files
                    if self.asd_file.signature is not None:

                        # signed
                        self.assertIsNotNone(self.asd_file.signature.signed)
                        self.assertEqual(type(self.asd_file.signature.signed), int)

                        # signatureTime
                        # TODO: to be parsed as timestamp in the main code
                        self.assertIsNotNone(self.asd_file.signature.signatureTime)
                        self.assertEqual(type(self.asd_file.signature.signatureTime), datetime)
                        print(self.asd_file.signature.signatureTime)


                        # userDomain
                        self.assertIsNotNone(self.asd_file.signature.userDomain)
                        self.assertEqual(type(self.asd_file.signature.userDomain), str)

                        # userLogin
                        self.assertIsNotNone(self.asd_file.signature.userLogin)
                        self.assertEqual(type(self.asd_file.signature.userLogin), str)

                        # userName
                        self.assertIsNotNone(self.asd_file.signature.userName)
                        self.assertEqual(type(self.asd_file.signature.userName), str)

                        # source
                        self.assertIsNotNone(self.asd_file.signature.source)
                        self.assertEqual(type(self.asd_file.signature.source), str)

                        # reason
                        self.assertIsNotNone(self.asd_file.signature.reason)
                        self.assertEqual(type(self.asd_file.signature.reason), str)

                        # notes
                        self.assertIsNotNone(self.asd_file.signature.notes)
                        self.assertEqual(type(self.asd_file.signature.notes), str)

                        # publicKey
                        self.assertIsNotNone(self.asd_file.signature.publicKey)
                        self.assertEqual(type(self.asd_file.signature.publicKey), str)

                        # signature
                        self.assertIsNotNone(self.asd_file.signature.signature)
                        self.assertEqual(type(self.asd_file.signature.signature), str)

# TODO: to be completed
class TestASDFileParseSpectralData(unittest.TestCase):

    def setUp(self):
        # Check if the ASDFile object is initialized correctly
        self.asd_file=ASDFile()
        self.assertIsNotNone(self.asd_file)

    def tearDown(self):
        # Clean up the ASDFile object
        del self.asd_file

    def test_001_parse_spectral_data(self):
        pass


# TODO: to be completed
class TestASDFileParseConstituentType(unittest.TestCase):

    def setUp(self):
        # Check if the ASDFile object is initialized correctly
        self.asd_file=ASDFile()
        self.assertIsNotNone(self.asd_file)

    def tearDown(self):
        # Clean up the ASDFile object
        del self.asd_file

    def test_001_parse_constituent_type(self):
        pass


# TODO: to be completed
class TestASDFileParseBSTR(unittest.TestCase):

    def setUp(self):
        # Check if the ASDFile object is initialized correctly
        self.asd_file=ASDFile()
        self.assertIsNotNone(self.asd_file)

    def tearDown(self):
        # Clean up the ASDFile object
        del self.asd_file

    def test_001_parse_bstr(self):
        pass


# TODO: to be completed
# class TestASDFileParseBool(unittest.TestCase):

    def setUp(self):
        # Check if the ASDFile object is initialized correctly
        self.asd_file=ASDFile()
        self.assertIsNotNone(self.asd_file)

    def tearDown(self):
        # Clean up the ASDFile object
        del self.asd_file

    def test_001_parse_bool(self):
        pass


# TODO: to be completed
class TestASDFileParseAuditEvents(unittest.TestCase):

    def setUp(self):
        # Check if the ASDFile object is initialized correctly
        self.asd_file=ASDFile()
        self.assertIsNotNone(self.asd_file)

    def tearDown(self):
        # Clean up the ASDFile object
        del self.asd_file

    def test_001_parse_audit_events(self):
        pass


# TODO: to be completed
class TestASDFileValidateFileVersion(unittest.TestCase):

    def setUp(self):
        # Check if the ASDFile object is initialized correctly
        self.asd_file=ASDFile()
        self.assertIsNotNone(self.asd_file)

    def tearDown(self):
        # Clean up the ASDFile object
        del self.asd_file

    def test_001_validate_file_version(self):
        pass


# TODO: to be completed
class TestASDFileParseeVersion(unittest.TestCase):

    def setUp(self):
        # Check if the ASDFile object is initialized correctly
        self.asd_file=ASDFile()
        self.assertIsNotNone(self.asd_file)

    def tearDown(self):
        # Clean up the ASDFile object
        del self.asd_file

    def test_001_parse_version(self):
        pass


# TODO: to be completed
class TestASDFileParseASDFileWhen(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_asd_file_when(self):
        pass


# TODO: to be completed
class TestASDFileParseGPS(unittest.TestCase):

    def setUp(self):
        # Check if the ASDFile object is initialized correctly
        self.asd_file=ASDFile()
        self.assertIsNotNone(self.asd_file)

    def tearDown(self):
        # Clean up the ASDFile object
        del self.asd_file

    def test_parse_asd_file_gps(self):
        for file_path in all_asd_data_files:
            with self.subTest(file_path):
                self.asd_file.read(file_path)

                self.asd_file._ASDFile__parse_metadata(3)
                # Check if the GPS data is set correctly
                if self.asd_file.metadata.gpsData:
                    # print(self.asd_file.metadata.gpsData)
                    gpsData = self.asd_file._ASDFile__parse_gps(self.asd_file.metadata.gpsData)

                    # Assertions
                    self.assertIsNotNone(gpsData)

                    # trueHeading
                    # speed
                    # latitude
                    # longitude
                    # altitude
                    # lock
                    # hardwareMode
                    # ss
                    # mm
                    # hh
                    # flags1
                    # flags2
                    # satellites
                    # filler


# TODO: not applied in the main code
class TestASDFileSmartDetector(unittest.TestCase):

    def setUp(self):
        # Setup a mock ASDFile object
        self.asd_file = ASDFile()
        # self.asd_file._ASDFile__asdFileStream = b'\x00' * 100

    def test_parse_asd_file_smart_detector(self):
        # Mock the __parse_smart_detector method
        # offset = self.asd_file._ASDFile__parse_SmartDetector(0)
        pass


# TODO: not applied in the main code
class TestASDFileSaturationError(unittest.TestCase):

    def setUp(self):
        # Setup a mock ASDFile object
        self.asd_file = ASDFile()
        self.asd_file._ASDFile__asdFileStream = b'\x00' * 100

    def test_parse_saturation_rrror(self):
        # Mock the __parse_smart_detector method
        offset = self.asd_file._ASDFile__parseSaturationError(0)


# TODO: to be completed
class TestASDFileParseTimeOLE(unittest.TestCase):
    
    def setUp(self):
        # Check if the ASDFile object is initialized correctly
        self.asd_file=ASDFile()

    def test_parse_saturation_error(self):
        pass


#! To be complete
class TestASDFileBenchmark(unittest.TestCase):

    def setUp(self):
        # Setup a mock ASDFile object
        self.asd_file = ASDFile()
        self.asd_file._ASDFile__asdFileStream = b'\x00' * 100

    def Test_001_001_DigitalNumber(self):
        # Mock the __parse_digital_number method
        offset = self.asd_file._ASDFile__parse_digital_number(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.digitalNumber)
        self.assertEqual(offset, 484)

    def Test_001_002_WhiteReference(self):
        # Mock the __parse_white_reference method
        offset = self.asd_file._ASDFile__parse_white_reference(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.whiteReference)
        self.assertEqual(offset, 484)

    def Test_001_003_Reflectance(self):
        # Mock the __parse_reflectance method
        offset = self.asd_file._ASDFile__parse_reflectance(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.reflectance)
        self.assertEqual(offset, 484)

    def Test_001_004_Reflectance1stDeriv(self):
        # Mock the __parse_reflectance_1st_derivative method
        offset = self.asd_file._ASDFile__parse_reflectance_1st_derivative(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.reflectance1stDeriv)
        self.assertEqual(offset, 484)

    def Test_001_005_Reflectance2ndDeriv(self):
        # Mock the __parse_reflectance_2nd_derivative method
        offset = self.asd_file._ASDFile__parse_reflectance_2nd_derivative(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.reflectance2ndDeriv)
        self.assertEqual(offset, 484)

    def Test_001_006_Reflectance3rdDeriv(self):
        # Mock the __parse_reflectance_3rd_derivative method
        offset = self.asd_file._ASDFile__parse_reflectance_3rd_derivative(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.reflectance3rdDeriv)
        self.assertEqual(offset, 484)


    def Test_001_007_Transmitance(self):
        # Mock the __parse_transmitance method
        offset = self.asd_file._ASDFile__parse_transmitance(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.transmitance)
        self.assertEqual(offset, 484)

    def Test_001_008_NormaliseSpectrum(self):
        # Mock the __parse_normalise_spectrum method
        offset = self.asd_file._ASDFile__parse_normalise_spectrum(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.normaliseSpectrum)
        self.assertEqual(offset, 484)

    def Test_001_009_Derivative(self):
        # Mock the __parse_derivative method
        offset = self.asd_file._ASDFile__parse_derivative(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.derivative)
        self.assertEqual(offset, 484)

    def Test_001_010_AbsoluteReflectance(self):
        # Mock the __parse_absolute_reflectance method
        offset = self.asd_file._ASDFile__parse_absolute_reflectance(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.absoluteReflectance)
        self.assertEqual(offset, 484)

    def Test_001_011_Log1R(self):
        # Mock the __parse_log1R method
        offset = self.asd_file._ASDFile__parse_log1R(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.log1R)
        self.assertEqual(offset, 484)

    def Test_001_012_Log1T(self):
        # Mock the __parse_log1T method
        offset = self.asd_file._ASDFile__parse_log1T(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.log1T)
        self.assertEqual(offset, 484)

    def Test_001_012_Log1RNoderiv(self):
        # Mock the __parse_log1R_noderiv method
        offset = self.asd_file._ASDFile__parse_log1R_noderiv(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.log1R_noderiv)
        self.assertEqual(offset, 484)

    def Test_001_013_Log1R1stDeriv(self):
        # Mock the __parse_log1R_1st_deriv method
        offset = self.asd_file._ASDFile__parse_log1R_1st_deriv(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.log1R_1st_deriv)
        self.assertEqual(offset, 484)

    def Test_001_014_Log1R2ndDeriv(self):
        # Mock the __parse_log1R_2nd_deriv method
        offset = self.asd_file._ASDFile__parse_log1R_2nd_deriv(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.log1R_2nd_deriv)
        self.assertEqual(offset, 484)

    def Test_001_015_radiance(self):
        # Mock the __parse_radiance method
        offset = self.asd_file._ASDFile__parse_radiance(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.radiance)
        self.assertEqual(offset, 484)

    def Test_001_016_calc_irradiance(self):
        # Mock the __parse_calc_irradiance method
        offset = self.asd_file._ASDFile__parse_calc_irradiance(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.calcIrradiance)
        self.assertEqual(offset, 484)

    def Test_001_017_calc_parabolic_correction(self):
        # Mock the __parse_calc_parabolic_correction method
        offset = self.asd_file._ASDFile__parse_calc_parabolic_correction(0)

        # Assertions
        self.assertIsNotNone(self.asd_file.metadata.calcParabolicCorrection)
        self.assertEqual(offset, 484)



if __name__ == '__main__':
    unittest.main(exit=False)