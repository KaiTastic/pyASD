"""
Export utilities for ASD data and plots
"""

import csv
import numpy as np
from datetime import datetime


class ExportManager:
    """
    Manager class for exporting ASD data to various formats
    """

    @staticmethod
    def export_to_csv(asd_file, filepath, data_types=None):
        """
        Export ASD data to CSV file

        Args:
            asd_file: ASDFile object
            filepath: Output file path
            data_types: List of data type names to export (e.g., ['reflectance', 'digitalNumber'])
                       If None, exports all available data types
        """
        if asd_file is None or asd_file.wavelengths is None:
            raise ValueError("No valid ASD file data to export")

        # Determine which data types to export
        available_types = {
            'wavelengths': asd_file.wavelengths,
            'digitalNumber': getattr(asd_file, 'digitalNumber', None),
            'reflectance': getattr(asd_file, 'reflectance', None),
            'reflectance1stDeriv': getattr(asd_file, 'reflectance1stDeriv', None),
            'reflectance2ndDeriv': getattr(asd_file, 'reflectance2ndDeriv', None),
            'reflectance3rdDeriv': getattr(asd_file, 'reflectance3rdDeriv', None),
            'whiteReference': getattr(asd_file, 'whiteReference', None),
            'absoluteReflectance': getattr(asd_file, 'absoluteReflectance', None),
            'log1R': getattr(asd_file, 'log1R', None),
            'log1R1stDeriv': getattr(asd_file, 'log1R1stDeriv', None),
            'log1R2ndDeriv': getattr(asd_file, 'log1R2ndDeriv', None),
            'radiance': getattr(asd_file, 'radiance', None),
        }

        # Filter out None values
        available_types = {k: v for k, v in available_types.items() if v is not None}

        # If specific data types requested, filter
        if data_types:
            export_types = {k: v for k, v in available_types.items()
                           if k in data_types or k == 'wavelengths'}
        else:
            export_types = available_types

        if 'wavelengths' not in export_types:
            raise ValueError("Wavelength data is required for export")

        # Write CSV
        with open(filepath, 'w', newline='') as csvfile:
            # Write header comment
            csvfile.write(f"# ASD File Export\n")
            csvfile.write(f"# Source: {getattr(asd_file, 'filename', 'Unknown')}\n")
            csvfile.write(f"# Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            if hasattr(asd_file, 'metadata') and asd_file.metadata:
                metadata = asd_file.metadata
                if hasattr(metadata, 'instrumentModel'):
                    csvfile.write(f"# Instrument: {metadata.instrumentModel}\n")
                if hasattr(metadata, 'channels'):
                    csvfile.write(f"# Channels: {metadata.channels}\n")

            csvfile.write("#\n")

            # Write data
            writer = csv.writer(csvfile)

            # Header row
            header = list(export_types.keys())
            writer.writerow(header)

            # Data rows
            num_rows = len(export_types['wavelengths'])
            for i in range(num_rows):
                row = []
                for col_name in header:
                    data = export_types[col_name]
                    if i < len(data):
                        value = data[i]
                        # Format numpy values
                        if isinstance(value, (np.integer, np.floating)):
                            value = float(value)
                        row.append(value)
                    else:
                        row.append('')
                writer.writerow(row)

    @staticmethod
    def export_metadata_to_txt(asd_file, filepath):
        """
        Export ASD file metadata to text file

        Args:
            asd_file: ASDFile object
            filepath: Output file path
        """
        if asd_file is None:
            raise ValueError("No valid ASD file to export")

        with open(filepath, 'w') as f:
            f.write("="*60 + "\n")
            f.write("ASD File Metadata Report\n")
            f.write("="*60 + "\n\n")

            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # File Attributes
            f.write("-" * 60 + "\n")
            f.write("File Attributes\n")
            f.write("-" * 60 + "\n")

            if hasattr(asd_file, 'filename'):
                f.write(f"File Name:          {asd_file.filename}\n")

            if hasattr(asd_file, 'filepath'):
                f.write(f"File Path:          {asd_file.filepath}\n")

            if hasattr(asd_file, 'filesize'):
                size_mb = asd_file.filesize / (1024 * 1024)
                f.write(f"File Size:          {asd_file.filesize:,} bytes ({size_mb:.2f} MB)\n")

            if hasattr(asd_file, 'creation_time'):
                f.write(f"Creation Time:      {asd_file.creation_time}\n")

            if hasattr(asd_file, 'modification_time'):
                f.write(f"Modification Time:  {asd_file.modification_time}\n")

            if hasattr(asd_file, 'hashMD5'):
                f.write(f"MD5:                {asd_file.hashMD5}\n")

            if hasattr(asd_file, 'hashSHA265'):
                f.write(f"SHA256:             {asd_file.hashSHA265}\n")

            # ASD Metadata
            if hasattr(asd_file, 'metadata') and asd_file.metadata:
                f.write("\n" + "-" * 60 + "\n")
                f.write("ASD Metadata\n")
                f.write("-" * 60 + "\n")

                metadata = asd_file.metadata

                if hasattr(asd_file, 'asdFileVersion'):
                    f.write(f"ASD File Version:   {asd_file.asdFileVersion}\n")

                if hasattr(metadata, 'instrumentModel'):
                    f.write(f"Instrument Model:   {metadata.instrumentModel}\n")

                if hasattr(metadata, 'instrumentType'):
                    f.write(f"Instrument Type:    {metadata.instrumentType}\n")

                if hasattr(metadata, 'channels'):
                    f.write(f"Channels:           {metadata.channels}\n")

                if hasattr(metadata, 'channel1Wavelength'):
                    f.write(f"Start Wavelength:   {metadata.channel1Wavelength} nm\n")

                if hasattr(metadata, 'wavelengthStep'):
                    f.write(f"Wavelength Step:    {metadata.wavelengthStep} nm\n")

                if hasattr(metadata, 'splice1_wavelength'):
                    f.write(f"Splice 1:           {metadata.splice1_wavelength} nm\n")

                if hasattr(metadata, 'splice2_wavelength'):
                    f.write(f"Splice 2:           {metadata.splice2_wavelength} nm\n")

                if hasattr(metadata, 'intergrationTime_ms'):
                    f.write(f"Integration Time:   {metadata.intergrationTime_ms}\n")

                if hasattr(metadata, 'swir1Gain'):
                    f.write(f"SWIR1 Gain:         {metadata.swir1Gain}\n")

                if hasattr(metadata, 'swir2Gain'):
                    f.write(f"SWIR2 Gain:         {metadata.swir2Gain}\n")

                if hasattr(metadata, 'spectrumTime'):
                    f.write(f"Spectrum Time:      {metadata.spectrumTime}\n")

                if hasattr(metadata, 'referenceTime'):
                    f.write(f"Reference Time:     {metadata.referenceTime}\n")

                if hasattr(metadata, 'dataType'):
                    f.write(f"Data Type:          {metadata.dataType}\n")

                # GPS Data
                if hasattr(metadata, 'gpsData') and metadata.gpsData:
                    f.write("\n  GPS Information:\n")
                    gps = metadata.gpsData

                    if hasattr(gps, 'latitude'):
                        f.write(f"    Latitude:       {gps.latitude:.6f}\n")

                    if hasattr(gps, 'longitude'):
                        f.write(f"    Longitude:      {gps.longitude:.6f}\n")

                    if hasattr(gps, 'altitude'):
                        f.write(f"    Altitude:       {gps.altitude} m\n")

            # Spectral Information
            if hasattr(asd_file, 'wavelengths') and asd_file.wavelengths is not None:
                f.write("\n" + "-" * 60 + "\n")
                f.write("Spectral Information\n")
                f.write("-" * 60 + "\n")

                wavelengths = asd_file.wavelengths
                f.write(f"Number of Bands:    {len(wavelengths)}\n")
                f.write(f"Wavelength Range:   {wavelengths[0]:.2f} - {wavelengths[-1]:.2f} nm\n")

                if len(wavelengths) > 1:
                    f.write(f"Spectral Resolution: {wavelengths[1] - wavelengths[0]:.2f} nm\n")

            # Available Data Types
            f.write("\n" + "-" * 60 + "\n")
            f.write("Available Data Types\n")
            f.write("-" * 60 + "\n")

            data_types = {
                'Digital Number': 'digitalNumber',
                'White Reference': 'whiteReference',
                'Reflectance': 'reflectance',
                'Reflectance (1st Deriv)': 'reflectance1stDeriv',
                'Reflectance (2nd Deriv)': 'reflectance2ndDeriv',
                'Reflectance (3rd Deriv)': 'reflectance3rdDeriv',
                'Absolute Reflectance': 'absoluteReflectance',
                'Log(1/R)': 'log1R',
                'Log(1/R) (1st Deriv)': 'log1R1stDeriv',
                'Log(1/R) (2nd Deriv)': 'log1R2ndDeriv',
                'Radiance': 'radiance',
            }

            for display_name, attr_name in data_types.items():
                try:
                    data = getattr(asd_file, attr_name, None)
                    status = "Available" if data is not None else "Not Available"
                    f.write(f"{display_name:30} {status}\n")
                except Exception:
                    f.write(f"{display_name:30} Error\n")

            f.write("\n" + "="*60 + "\n")
            f.write("End of Report\n")
            f.write("="*60 + "\n")

    @staticmethod
    def get_available_export_data_types(asd_file):
        """
        Get list of available data types for export

        Args:
            asd_file: ASDFile object

        Returns:
            dict: Dictionary of available data types {display_name: attr_name}
        """
        if asd_file is None:
            return {}

        data_types = {
            'Digital Number': 'digitalNumber',
            'White Reference': 'whiteReference',
            'Reflectance': 'reflectance',
            'Reflectance (1st Derivative)': 'reflectance1stDeriv',
            'Reflectance (2nd Derivative)': 'reflectance2ndDeriv',
            'Reflectance (3rd Derivative)': 'reflectance3rdDeriv',
            'Absolute Reflectance': 'absoluteReflectance',
            'Log(1/R)': 'log1R',
            'Log(1/R) (1st Derivative)': 'log1R1stDeriv',
            'Log(1/R) (2nd Derivative)': 'log1R2ndDeriv',
            'Radiance': 'radiance',
        }

        available = {}
        for display_name, attr_name in data_types.items():
            try:
                data = getattr(asd_file, attr_name, None)
                if data is not None:
                    available[display_name] = attr_name
            except Exception:
                pass

        return available
