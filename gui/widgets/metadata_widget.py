"""
Metadata display widget for ASD files
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
                              QLabel, QGroupBox, QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt


class MetadataWidget(QWidget):
    """
    Widget for displaying ASD file metadata in a tree structure
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.asd_file = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("<b>File Information</b>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Tree widget for metadata
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Property", "Value"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setColumnWidth(0, 200)
        layout.addWidget(self.tree)

        # Button layout
        btn_layout = QHBoxLayout()

        # Expand/Collapse buttons
        expand_btn = QPushButton("Expand All")
        expand_btn.clicked.connect(self.tree.expandAll)
        btn_layout.addWidget(expand_btn)

        collapse_btn = QPushButton("Collapse All")
        collapse_btn.clicked.connect(self.tree.collapseAll)
        btn_layout.addWidget(collapse_btn)

        layout.addLayout(btn_layout)

    def set_asd_file(self, asd_file):
        """
        Set the ASD file and display its metadata

        Args:
            asd_file: ASDFile object
        """
        self.asd_file = asd_file
        self.update_metadata()

    def update_metadata(self):
        """Update the metadata display"""
        self.tree.clear()

        if self.asd_file is None:
            return

        # File Attributes Section
        file_attr = QTreeWidgetItem(self.tree, ["File Attributes", ""])
        self._add_file_attributes(file_attr)

        # Metadata Section
        if hasattr(self.asd_file, 'metadata') and self.asd_file.metadata:
            metadata_item = QTreeWidgetItem(self.tree, ["ASD Metadata", ""])
            self._add_metadata(metadata_item)

        # Spectral Data Info
        if hasattr(self.asd_file, 'wavelengths') and self.asd_file.wavelengths is not None:
            spectral_item = QTreeWidgetItem(self.tree, ["Spectral Information", ""])
            self._add_spectral_info(spectral_item)

        # Available Data Types
        data_types_item = QTreeWidgetItem(self.tree, ["Available Data Types", ""])
        self._add_available_data_types(data_types_item)

        # Expand all by default
        self.tree.expandAll()

    def _add_file_attributes(self, parent_item):
        """Add file attribute information"""
        if not hasattr(self.asd_file, 'filename'):
            return

        self._add_tree_item(parent_item, "File Name", self.asd_file.filename)

        if hasattr(self.asd_file, 'filepath'):
            self._add_tree_item(parent_item, "File Path", self.asd_file.filepath)

        if hasattr(self.asd_file, 'filesize'):
            size_mb = self.asd_file.filesize / (1024 * 1024)
            self._add_tree_item(parent_item, "File Size", f"{self.asd_file.filesize:,} bytes ({size_mb:.2f} MB)")

        if hasattr(self.asd_file, 'creation_time'):
            self._add_tree_item(parent_item, "Creation Time", str(self.asd_file.creation_time))

        if hasattr(self.asd_file, 'modification_time'):
            self._add_tree_item(parent_item, "Modification Time", str(self.asd_file.modification_time))

        if hasattr(self.asd_file, 'hashMD5'):
            self._add_tree_item(parent_item, "MD5", self.asd_file.hashMD5)

        if hasattr(self.asd_file, 'hashSHA265'):
            self._add_tree_item(parent_item, "SHA256", self.asd_file.hashSHA265)

    def _add_metadata(self, parent_item):
        """Add ASD metadata information"""
        metadata = self.asd_file.metadata

        # File version
        if hasattr(metadata, 'fileVersion'):
            self._add_tree_item(parent_item, "File Version", str(metadata.fileVersion))

        if hasattr(self.asd_file, 'asdFileVersion'):
            self._add_tree_item(parent_item, "ASD File Version", str(self.asd_file.asdFileVersion))

        # Instrument information
        instrument_item = QTreeWidgetItem(parent_item, ["Instrument", ""])

        if hasattr(metadata, 'instrumentModel'):
            self._add_tree_item(instrument_item, "Model", str(metadata.instrumentModel))

        if hasattr(metadata, 'instrumentType'):
            self._add_tree_item(instrument_item, "Type", str(metadata.instrumentType))

        if hasattr(metadata, 'instrument'):
            self._add_tree_item(instrument_item, "Instrument", str(metadata.instrument))

        # Spectral parameters
        spectral_params = QTreeWidgetItem(parent_item, ["Spectral Parameters", ""])

        if hasattr(metadata, 'channels'):
            self._add_tree_item(spectral_params, "Channels", str(metadata.channels))

        if hasattr(metadata, 'channel1Wavelength'):
            self._add_tree_item(spectral_params, "Start Wavelength", f"{metadata.channel1Wavelength} nm")

        if hasattr(metadata, 'wavelengthStep'):
            self._add_tree_item(spectral_params, "Wavelength Step", f"{metadata.wavelengthStep} nm")

        if hasattr(metadata, 'splice1_wavelength'):
            self._add_tree_item(spectral_params, "Splice 1", f"{metadata.splice1_wavelength} nm")

        if hasattr(metadata, 'splice2_wavelength'):
            self._add_tree_item(spectral_params, "Splice 2", f"{metadata.splice2_wavelength} nm")

        # Acquisition parameters
        if hasattr(metadata, 'intergrationTime_ms') or hasattr(metadata, 'swir1Gain') or hasattr(metadata, 'swir2Gain'):
            acq_params = QTreeWidgetItem(parent_item, ["Acquisition Parameters", ""])

            if hasattr(metadata, 'intergrationTime_ms'):
                self._add_tree_item(acq_params, "Integration Time", str(metadata.intergrationTime_ms))

            if hasattr(metadata, 'swir1Gain'):
                self._add_tree_item(acq_params, "SWIR1 Gain", str(metadata.swir1Gain))

            if hasattr(metadata, 'swir2Gain'):
                self._add_tree_item(acq_params, "SWIR2 Gain", str(metadata.swir2Gain))

        # GPS information
        if hasattr(metadata, 'gpsData'):
            gps = metadata.gpsData
            if gps:
                gps_item = QTreeWidgetItem(parent_item, ["GPS Data", ""])

                if hasattr(gps, 'latitude'):
                    self._add_tree_item(gps_item, "Latitude", f"{gps.latitude:.6f}")

                if hasattr(gps, 'longitude'):
                    self._add_tree_item(gps_item, "Longitude", f"{gps.longitude:.6f}")

                if hasattr(gps, 'altitude'):
                    self._add_tree_item(gps_item, "Altitude", f"{gps.altitude} m")

        # Time information
        if hasattr(metadata, 'spectrumTime'):
            self._add_tree_item(parent_item, "Spectrum Time", str(metadata.spectrumTime))

        if hasattr(metadata, 'referenceTime'):
            self._add_tree_item(parent_item, "Reference Time", str(metadata.referenceTime))

        # Data type
        if hasattr(metadata, 'dataType'):
            self._add_tree_item(parent_item, "Data Type", str(metadata.dataType))

    def _add_spectral_info(self, parent_item):
        """Add spectral data information"""
        wavelengths = self.asd_file.wavelengths

        self._add_tree_item(parent_item, "Number of Bands", str(len(wavelengths)))
        self._add_tree_item(parent_item, "Wavelength Range",
                          f"{wavelengths[0]:.2f} - {wavelengths[-1]:.2f} nm")
        self._add_tree_item(parent_item, "Spectral Resolution",
                          f"{wavelengths[1] - wavelengths[0]:.2f} nm" if len(wavelengths) > 1 else "N/A")

    def _add_available_data_types(self, parent_item):
        """Check and display available data types"""
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
                data = getattr(self.asd_file, attr_name, None)
                status = "Available" if data is not None else "Not Available"
                color = "green" if data is not None else "red"

                item = QTreeWidgetItem(parent_item, [display_name, status])
                item.setForeground(1, Qt.GlobalColor.darkGreen if data is not None else Qt.GlobalColor.darkRed)
            except Exception:
                item = QTreeWidgetItem(parent_item, [display_name, "Error"])
                item.setForeground(1, Qt.GlobalColor.red)

    def _add_tree_item(self, parent, name, value):
        """Helper method to add a tree item"""
        QTreeWidgetItem(parent, [name, str(value)])

    def clear(self):
        """Clear the metadata display"""
        self.tree.clear()
        self.asd_file = None
