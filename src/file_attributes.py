"""
File attribute class includes the following aspects: 
        • File attributes include: file name, path, size, creation time, modification time, access time, file type, etc.
        • Some basic operations can be provided for files, such as reading, writing, deleting, etc.
        • File permission settings may need support (such as read-only, executable, etc.).

Main function description:
    1. Initialization method (__init__): Receive the file path, check whether the file exists, and then get the basic information of the file (such as name, size, creation time, modification time, access time, etc.).
    2. Get file type (get_file_type): Get the file type by the file extension.
    3. Read file (read_file): Read the file's content and return it.
    4. Write file (write_to_file): Write the content to the file, overwriting the original content.
    5. Delete file (delete_file): Delete the file in the specified path.
    6. Print basic information of the file (__str__): Returns brief information of the file, which is convenient for viewing the properties of the file.

3. To be added:
• More properties such as file permissions, file owners, and file locking mechanisms.
• Support file reading and writing in different encoding formats.
• Error handling mechanisms to ensure robustness in abnormal situations.
"""


import os
import time
import hashlib


class FileAttributes(object):
    def __init__(self, filepath):

        if os.path.exists(filepath) and os.path.isfile(filepath):
            self.filepath = filepath
        else:
            print(f"File \'{filepath}\' do not exist.")
            exception = FileNotFoundError(f"File \'{filepath}\' do not exist.")
            raise exception
            
        # Basic file attributes
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.filesize = os.path.getsize(filepath)
        self.filetype = os.path.splitext(filepath)[1]
        self.dirname = os.path.dirname(filepath)
        self.creation_time = time.ctime(os.path.getctime(filepath))
        self.modification_time = time.ctime(os.path.getmtime(filepath))
        self.access_time = time.ctime(os.path.getatime(filepath))
        self.file_permission = os.stat(filepath).st_mode
        self._data = self.__get_data()
        self._hashMD5 = None
        self._hashSHA265 = None
    
    def __get_data(self):
        with open(self.filepath, 'rb') as file:
            return file.read()
    
    def delete(self):
        if os.path.exists(self.filepath) and os.path.isfile(self.filepath):
            os.remove(self.filepath)
        else:
            print(f"File delete fail: file \'{self.filepath}\' do not exist")
            raise FileNotFoundError(f"File \'{self.filepath}\' do not exist")
    
    def read(self):
        if os.path.exists(self.filepath) and os.path.isfile(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as file:
                return file.read()
    
    def write(self, content):
        if os.path.exists(self.filepath) and os.path.isfile(self.filepath):
            with open(self.filepath, 'w', encoding='utf-8') as file:
                file.write(content)

    # def save(self):
    #     with open(self.filepath, 'wb') as file:
    #         file.write(content)

    # def saveAS(self, filepath):
    #     with open(filepath, 'wb') as file:
    #         file.write(filepath)

    def set_file_name(self, new_name):
        self.file_name = new_name
        self.file_path = os.path.join(os.path.dirname(self.file_path), new_name)
    
    def set_file_path(self, new_path):
        self.file_path = new_path
        self.file_name = os.path.basename(new_path)

    def __str__(self):
        return f"File Name: \t\t{self.filename}\n" \
               f"File Path: \t\t{self.filepath}\n" \
               f"File Size: \t\t{self.filesize} bytes\n" \
               f"Creation Time: \t\t{self.creation_time}\n" \
               f"Modification Time: \t{self.modification_time}\n" \
               f"Access Time: \t\t{self.access_time}\n" \
               f"File type: \t\t{self.filetype}\n"\
               f"MD5: \t\t\t{self.hashMD5}\n" \
               f"SHA265: \t\t{self.hashSHA265}"

    @property
    def hashMD5(self):
        if self._hashMD5 is None:
            self._hashMD5 = hashlib.md5(self._data).hexdigest()
        return self._hashMD5
    
    @property
    def hashSHA265(self):
        if self._hashSHA265 is None:
            self._hashSHA265 = hashlib.sha256(self._data).hexdigest()
        return self._hashSHA265


if __name__ == '__main__':
    pass