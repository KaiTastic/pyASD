"""
Requirements:
This module contains tests for the FileAttributes class in the file_attributes module.
"""

import os
import unittest
import tempfile
from pyASDReader.file_attributes import FileAttributes
from .test_data import all_asd_data_files


class TestFileAttributes(unittest.TestCase):

    def setUp(self):
        if len(all_asd_data_files) > 0:
            self.test_file_path = all_asd_data_files[0]
        else:
            self.test_file_path = None
        self.temp_file = None

    def tearDown(self):
        if self.temp_file and os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_001_init_with_valid_file(self):
        if self.test_file_path:
            file_attr = FileAttributes(self.test_file_path)
            self.assertIsNotNone(file_attr)
            self.assertEqual(file_attr.filepath, self.test_file_path)
            self.assertIsNotNone(file_attr.filename)
            self.assertIsNotNone(file_attr.filesize)
            self.assertIsNotNone(file_attr.filetype)

    def test_002_init_with_invalid_file(self):
        with self.assertRaises(FileNotFoundError):
            FileAttributes("non_existent_file.txt")

    def test_003_read_method(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            self.temp_file = f.name
            test_content = "test content for reading"
            f.write(test_content)

        file_attr = FileAttributes(self.temp_file)
        content = file_attr.read()
        self.assertIsNotNone(content)
        self.assertEqual(content, test_content)

    def test_004_write_method(self):
        if self.test_file_path:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                self.temp_file = f.name
                f.write("test content")

            file_attr = FileAttributes(self.temp_file)
            new_content = "new test content"
            file_attr.write(new_content)

            with open(self.temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertEqual(content, new_content)

    def test_005_delete_method(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_path = f.name
            f.write("test content")

        file_attr = FileAttributes(temp_path)
        self.assertTrue(os.path.exists(temp_path))
        file_attr.delete()
        self.assertFalse(os.path.exists(temp_path))

    def test_006_delete_nonexistent_file(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_path = f.name
            f.write("test content")

        file_attr = FileAttributes(temp_path)
        os.remove(temp_path)

        with self.assertRaises(FileNotFoundError):
            file_attr.delete()

    def test_007_hashMD5_property(self):
        if self.test_file_path:
            file_attr = FileAttributes(self.test_file_path)
            hash_md5 = file_attr.hashMD5
            self.assertIsNotNone(hash_md5)
            self.assertEqual(type(hash_md5), str)
            self.assertEqual(len(hash_md5), 32)

    def test_008_hashSHA265_property(self):
        if self.test_file_path:
            file_attr = FileAttributes(self.test_file_path)
            hash_sha256 = file_attr.hashSHA265
            self.assertIsNotNone(hash_sha256)
            self.assertEqual(type(hash_sha256), str)
            self.assertEqual(len(hash_sha256), 64)

    def test_009_str_method(self):
        if self.test_file_path:
            file_attr = FileAttributes(self.test_file_path)
            str_repr = str(file_attr)
            self.assertIsNotNone(str_repr)
            self.assertIn(file_attr.filename, str_repr)
            self.assertIn(file_attr.filepath, str_repr)
            self.assertIn("MD5", str_repr)
            self.assertIn("SHA265", str_repr)

    def test_010_set_file_name(self):
        if self.test_file_path:
            file_attr = FileAttributes(self.test_file_path)
            new_name = "new_filename.asd"
            file_attr.set_file_name(new_name)
            self.assertEqual(os.path.basename(file_attr.filepath), new_name)

    def test_011_set_file_path(self):
        if self.test_file_path:
            file_attr = FileAttributes(self.test_file_path)
            new_path = "/tmp/new_path/test.asd"
            file_attr.set_file_path(new_path)
            self.assertEqual(file_attr.filepath, new_path)
            self.assertEqual(file_attr.filename, "test.asd")

    def test_012_file_attributes(self):
        if self.test_file_path:
            file_attr = FileAttributes(self.test_file_path)
            self.assertIsNotNone(file_attr.creation_time)
            self.assertIsNotNone(file_attr.modification_time)
            self.assertIsNotNone(file_attr.access_time)
            self.assertIsNotNone(file_attr.file_permission)
            self.assertIsNotNone(file_attr.dirname)


if __name__ == '__main__':
    unittest.main(exit=False)
