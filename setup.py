from setuptools import setup, find_packages


# This is a setup script for a Python package named "ASD_File_Reader".
# It uses setuptools to package the module and make it installable via pip.
# The script includes metadata such as the package name, version, author, description,
# and dependencies. It also specifies the minimum Python version required.


setup(
    name="ASD_File_Reader",  # Package name
    version="1.0.1",         # Version number
    author="Kai Cao",        # Author name
    author_email="caokai_cgs@163.com",  # Author email
    description="A Python library for reading and parsing all versions of ASD binary spectral files",  # Short description
    long_description=open("README.md").read(),  # Long description from README file
    long_description_content_type="text/markdown",
    url="https://github.com/KaiTastic/ASD_File_Reader",  # Project URL
    packages=find_packages(),  # Automatically find packages in the directory
    install_requires=[         # Dependencies
        "numpy>=1.0.0"
        ],
    classifiers=[              # Classifiers for PyPI
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",   # Minimum Python version required
    keywords="ASD spectral files spectroradiometer remote sensing",
    project_urls={
        "Bug Reports": "https://github.com/KaiTastic/ASD_File_Reader/issues",
        "Source": "https://github.com/KaiTastic/ASD_File_Reader",
        "Documentation": "https://github.com/KaiTastic/ASD_File_Reader#readme",
        "Changelog": "https://github.com/KaiTastic/ASD_File_Reader/blob/main/CHANGELOG.md",
    },
)