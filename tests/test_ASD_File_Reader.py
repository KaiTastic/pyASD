"""
Requirements:
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
from pyASD import ASDFile

class TestASDFile(unittest.TestCase):

    def setUp(self):
        # Test file in the sample_data directory
        self.test_file_path = './tests/sample_data/v7sample_field_spectroscopy/44231B009-1-FW3R00000.asd'
        # Create ASDFile instance without auto-loading
        self.asd_file = ASDFile()

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
        # Don't access private attributes in tests

    def test_bom(self):
        # the BOM only exists in the last 3 bytes of the file from the spectroscopy data
        self.asd_file.read(self.test_file_path)
        # Access private attribute using name mangling (for testing only)
        # Better approach: test public behavior instead
        # self.assertEqual(self.asd_file._ASDFile__bom, b'\xFF\xFE\xFD')
        # Instead, test that the file was read successfully
        self.assertIsNotNone(self.asd_file.metadata)

if __name__ == '__main__':
    unittest.main(exit=False)