"""
Properties panel for displaying file information, metadata, and data types

Phase 1 - Simplified version with 3 tabs:
- Tab 1: File Information
- Tab 2: Metadata (reuse existing MetadataWidget)
- Tab 3: Available Data Types
"""

import os
from typing import Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QScrollArea,
                              QLabel, QGroupBox, QFormLayout, QPushButton,
                              QHBoxLayout, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from pyASDReader import ASDFile


class FileInfoTab(QScrollArea):
    """
    File information tab (Phase 1 - Simplified)

    Displays basic file information:
    - Name, path, size
    - Creation/modification times
    - ASD file version
    """

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)

        # Basic information group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()

        self.name_label = QLabel("--")
        basic_layout.addRow("Name:", self.name_label)

        self.path_label = QLabel("--")
        self.path_label.setWordWrap(True)
        self.path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        basic_layout.addRow("Path:", self.path_label)

        self.size_label = QLabel("--")
        basic_layout.addRow("Size:", self.size_label)

        self.created_label = QLabel("--")
        basic_layout.addRow("Created:", self.created_label)

        self.modified_label = QLabel("--")
        basic_layout.addRow("Modified:", self.modified_label)

        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)

        # ASD format information
        format_group = QGroupBox("ASD Format")
        format_layout = QFormLayout()

        self.version_label = QLabel("--")
        format_layout.addRow("File Version:", self.version_label)

        self.channels_label = QLabel("--")
        format_layout.addRow("Channels:", self.channels_label)

        self.wavelength_range_label = QLabel("--")
        format_layout.addRow("Wavelength Range:", self.wavelength_range_label)

        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.copy_btn = QPushButton("Copy Info")
        self.copy_btn.clicked.connect(self._copy_info)
        button_layout.addWidget(self.copy_btn)

        self.show_dir_btn = QPushButton("Show in Folder")
        self.show_dir_btn.clicked.connect(self._show_in_folder)
        button_layout.addWidget(self.show_dir_btn)

        layout.addLayout(button_layout)

        layout.addStretch()
        self.setWidget(content)

        self.current_filepath = None

    def display(self, asd_file: ASDFile):
        """Display file information"""
        self.current_filepath = asd_file.filepath

        # Basic info
        self.name_label.setText(os.path.basename(asd_file.filepath))
        self.path_label.setText(str(asd_file.filepath))

        try:
            size = os.path.getsize(asd_file.filepath)
            size_str = self._format_size(size)
            self.size_label.setText(size_str)
        except:
            self.size_label.setText("--")

        # Timestamps
        try:
            import time
            ctime = os.path.getctime(asd_file.filepath)
            mtime = os.path.getmtime(asd_file.filepath)
            self.created_label.setText(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ctime)))
            self.modified_label.setText(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime)))
        except:
            self.created_label.setText("--")
            self.modified_label.setText("--")

        # ASD format info
        self.version_label.setText(f"v{asd_file.asdFileVersion.value}")

        if asd_file.wavelengths is not None:
            self.channels_label.setText(str(len(asd_file.wavelengths)))
            wl_range = f"{asd_file.wavelengths[0]:.1f} - {asd_file.wavelengths[-1]:.1f} nm"
            self.wavelength_range_label.setText(wl_range)
        else:
            self.channels_label.setText("--")
            self.wavelength_range_label.setText("--")

    def clear(self):
        """Clear all labels"""
        self.name_label.setText("--")
        self.path_label.setText("--")
        self.size_label.setText("--")
        self.created_label.setText("--")
        self.modified_label.setText("--")
        self.version_label.setText("--")
        self.channels_label.setText("--")
        self.wavelength_range_label.setText("--")
        self.current_filepath = None

    def _format_size(self, size: int) -> str:
        """Format file size"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/1024/1024:.1f} MB"

    def _copy_info(self):
        """Copy file info to clipboard"""
        if not self.current_filepath:
            return

        from PyQt6.QtWidgets import QApplication
        info = f"""File: {self.name_label.text()}
Path: {self.path_label.text()}
Size: {self.size_label.text()}
Created: {self.created_label.text()}
Modified: {self.modified_label.text()}
Version: {self.version_label.text()}
Channels: {self.channels_label.text()}
Wavelength Range: {self.wavelength_range_label.text()}"""

        QApplication.clipboard().setText(info)

    def _show_in_folder(self):
        """Show file in system file manager"""
        if not self.current_filepath:
            return

        import subprocess
        import platform

        if platform.system() == "Windows":
            subprocess.run(['explorer', '/select,', self.current_filepath])
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(['open', '-R', self.current_filepath])
        else:  # Linux
            subprocess.run(['xdg-open', os.path.dirname(self.current_filepath)])


class DataTypesTab(QScrollArea):
    """
    Data types availability tab (Phase 1 - Simplified)

    Shows which data types are available in the current file
    """

    load_requested = pyqtSignal(str)  # data_type

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)

        content = QWidget()
        self.layout = QVBoxLayout(content)

        # Title
        title = QLabel("<b>Available Data Types</b>")
        self.layout.addWidget(title)

        # Data type checkboxes
        self.data_type_widgets = {}

        data_types = [
            ('digitalNumber', 'Digital Number (DN)'),
            ('whiteReference', 'White Reference'),
            ('reflectance', 'Reflectance'),
            ('reflectance1stDeriv', 'Reflectance (1st Derivative)'),
            ('reflectance2ndDeriv', 'Reflectance (2nd Derivative)'),
            ('reflectance3rdDeriv', 'Reflectance (3rd Derivative)'),
            ('absoluteReflectance', 'Absolute Reflectance'),
            ('log1R', 'Log(1/R)'),
            ('log1R1stDeriv', 'Log(1/R) 1st Derivative'),
            ('log1R2ndDeriv', 'Log(1/R) 2nd Derivative'),
            ('radiance', 'Radiance'),
        ]

        for data_type, display_name in data_types:
            widget = DataTypeItemWidget(data_type, display_name)
            widget.load_clicked.connect(lambda dt=data_type: self.load_requested.emit(dt))
            self.data_type_widgets[data_type] = widget
            self.layout.addWidget(widget)

        self.layout.addStretch()
        self.setWidget(content)

    def display(self, asd_file: ASDFile):
        """Display data type availability"""
        for data_type, widget in self.data_type_widgets.items():
            data = getattr(asd_file, data_type, None)
            available = data is not None
            widget.set_available(available)

    def clear(self):
        """Clear all data type status"""
        for widget in self.data_type_widgets.values():
            widget.set_available(False)


class DataTypeItemWidget(QWidget):
    """Single data type item widget"""

    load_clicked = pyqtSignal()

    def __init__(self, data_type: str, display_name: str):
        super().__init__()
        self.data_type = data_type

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        # Status icon
        self.status_icon = QLabel("❓")
        layout.addWidget(self.status_icon)

        # Name
        name_label = QLabel(display_name)
        layout.addWidget(name_label)

        layout.addStretch()

        # Load button
        self.load_btn = QPushButton("Load")
        self.load_btn.setMaximumWidth(60)
        self.load_btn.clicked.connect(self.load_clicked)
        layout.addWidget(self.load_btn)

    def set_available(self, available: bool):
        """Set availability status"""
        if available:
            self.status_icon.setText("✅")
            self.load_btn.setEnabled(True)
        else:
            self.status_icon.setText("❌")
            self.load_btn.setEnabled(False)


class PropertiesPanel(QWidget):
    """
    Properties panel (Phase 1 - Simplified version)

    Contains 3 tabs:
    - File Information
    - Metadata (reuses MetadataWidget)
    - Data Types
    """

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title = QLabel("<b>Properties</b>")
        layout.addWidget(title)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)

        # Tab 1: File Information
        self.file_info_tab = FileInfoTab()
        self.tabs.addTab(self.file_info_tab, "File")

        # Tab 2: Metadata (import existing widget)
        from gui.widgets.metadata_widget import MetadataWidget
        self.metadata_tab = MetadataWidget()
        self.tabs.addTab(self.metadata_tab, "Metadata")

        # Tab 3: Data Types
        self.data_types_tab = DataTypesTab()
        self.tabs.addTab(self.data_types_tab, "Data Types")

        layout.addWidget(self.tabs)

    def set_asd_file(self, asd_file: ASDFile):
        """Set current ASD file and update all tabs"""
        self.file_info_tab.display(asd_file)
        self.metadata_tab.set_asd_file(asd_file)
        self.data_types_tab.display(asd_file)

    def clear(self):
        """Clear all tabs"""
        self.file_info_tab.clear()
        self.metadata_tab.clear()
        self.data_types_tab.clear()
