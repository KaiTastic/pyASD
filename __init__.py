import ASD_File_Reader

main_version = 1
major_version = 0
minor_version = 1
__version__ = f"{main_version}.{major_version}.{minor_version}"


# Set up Global logger for the package
import os
import logging
from .src.loggerSetup import setup_logging
logFile=os.path.join(os.path.dirname(__file__), 'ASD_File_Reader.log')
# setup_logging(logFile, log_level=logging.CRITICAL) 
# setup_logging(logFile, log_level=logging.DEBUG)
setup_logging(logFile, log_level=logging.INFO)
globalLogger = logging.getLogger('Global Logger')


__all__ = ["ASDFile"]
