"""
Package ASD: Version Lite
Module: ASD_File_Reader.py

Requirements:`
This module contains tests for the ASDFile class in the ASD_File_Reader module.
"""

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

import unittest
from src.version_lite.ASD_File_Reader import ASDFile

class TestASDFile(unittest.TestCase):

    def setUp(self):
        # Test file in the SampleDatßa directory
        self.test_file_path = './tests/SampleData/44231B009-1-FW3R00000.asd'
        self.asd_file = ASDFile(self.test_file_path)

    def test_read_file_exists(self):
        # Assuming you have a valid test file
        self.assertFalse(self.asd_file.read('non_existent_file.asd'))

    def test_read_file_success(self):
        # Assuming you have a valid test file
        self.assertTrue(self.asd_file.read(self.test_file_path))

    def test_read_file_metadata(self):
        # Assuming you have a valid test file
        self.asd_file.read(self.test_file_path)
        self.assertIsNotNone(self.asd_file.metadata)
        print(self.asd_file.metadata)
        print(self.asd_file.__asdFileStream)

    def test___bom(self):
        # the BOM only exists in the last 3 bytes of the file from the spectroscopy data
        self.asd_file.read(self.test_file_path)
        self.assertEqual(self.asd_file.__bom, b'\xFF\xFE\xFD')

if __name__ == '__main__':
    unittest.main(exit=False)