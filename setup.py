from setuptools import setup, find_packages


# This is a setup script for a Python package named "ASD_File_Reader".
# It uses setuptools to package the module and make it installable via pip.
# The script includes metadata such as the package name, version, author, description,
# and dependencies. It also specifies the minimum Python version required.


setup(
    name="ASD_File_Reader",  # Package name
    version="1.0.0",         # Version number
    author="Your Name",      # Author name
    author_email="your.email@example.com",  # Author email
    description="A Python package for reading ASD files",  # Short description
    long_description=open("README.md").read(),  # Long description from README file
    long_description_content_type="text/markdown",
    url="https://github.com/YourUsername/ASD_File_Reader",  # Project URL
    packages=find_packages(),  # Automatically find packages in the directory
    install_requires=[         # Dependencies
        "numpy>=1.0.0"
        ],
    classifiers=[              # Classifiers for PyPI
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",   # Minimum Python version required
)