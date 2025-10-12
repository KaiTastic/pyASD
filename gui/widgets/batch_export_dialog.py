"""
Batch export dialog for exporting multiple ASD files
"""

import os
import logging
from typing import List
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QGroupBox, QCheckBox, QRadioButton, QButtonGroup,
                              QPushButton, QFileDialog, QProgressBar,
                              QMessageBox, QScrollArea, QWidget, QLineEdit,
                              QDialogButtonBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

logger = logging.getLogger(__name__)


class BatchExportWorker(QThread):
    """
    Worker thread for batch export operations
    """

    progress = pyqtSignal(int, str)  # progress percentage, current file
    finished = pyqtSignal(int, int)  # success_count, total_count
    error = pyqtSignal(str, str)     # filename, error_message

    def __init__(self, files, output_dir, data_types, export_format, parent=None):
        super().__init__(parent)
        self.files = files
        self.output_dir = output_dir
        self.data_types = data_types
        self.export_format = export_format
        self._is_cancelled = False

    def run(self):
        """Run batch export"""
        from pyASDReader import ASDFile
        from gui.utils import ExportManager

        success_count = 0
        total = len(self.files)

        for idx, filepath in enumerate(self.files):
            if self._is_cancelled:
                break

            try:
                # Update progress
                filename = os.path.basename(filepath)
                progress_pct = int((idx / total) * 100)
                self.progress.emit(progress_pct, filename)

                # Load file
                asd_file = ASDFile(filepath)

                # Generate output filename
                base_name = os.path.splitext(filename)[0]
                output_file = os.path.join(self.output_dir, f"{base_name}_export.{self.export_format}")

                # Export based on format
                if self.export_format == 'csv':
                    ExportManager.export_to_csv(asd_file, output_file, self.data_types)
                elif self.export_format == 'txt':
                    ExportManager.export_metadata_to_txt(asd_file, output_file)

                success_count += 1

            except Exception as e:
                error_msg = str(e)
                self.error.emit(os.path.basename(filepath), error_msg)
                logger.error(f"Failed to export {filepath}: {e}")

        # Final progress
        self.progress.emit(100, "Complete")
        self.finished.emit(success_count, total)

    def cancel(self):
        """Cancel the export operation"""
        self._is_cancelled = True


class BatchExportDialog(QDialog):
    """
    Dialog for batch exporting multiple ASD files
    """

    def __init__(self, files: List[str], parent=None):
        super().__init__(parent)
        self.files = files
        self.output_dir = None
        self.worker = None
        self.setWindowTitle(f"Batch Export - {len(files)} Files")
        self.setGeometry(100, 100, 600, 500)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)

        # File info
        info_label = QLabel(f"<b>Selected {len(self.files)} file(s) for export</b>")
        layout.addWidget(info_label)

        # Export format group
        format_group = QGroupBox("Export Format")
        format_layout = QVBoxLayout()

        self.format_group = QButtonGroup()

        self.csv_radio = QRadioButton("CSV (Spectral Data)")
        self.csv_radio.setChecked(True)
        self.format_group.addButton(self.csv_radio, 0)
        format_layout.addWidget(self.csv_radio)

        self.txt_radio = QRadioButton("TXT (Metadata Only)")
        self.format_group.addButton(self.txt_radio, 1)
        format_layout.addWidget(self.txt_radio)

        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        # Data types selection (for CSV export)
        self.data_types_group = QGroupBox("Data Types to Export (CSV only)")
        data_types_layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        self.data_type_checkboxes = {}
        data_types = [
            ('digitalNumber', 'Digital Number (DN)'),
            ('whiteReference', 'White Reference'),
            ('reflectance', 'Reflectance'),
            ('reflectanceNoDeriv', 'Reflectance (No Derivative)'),
            ('reflectance1stDeriv', 'Reflectance (1st Derivative)'),
            ('reflectance2ndDeriv', 'Reflectance (2nd Derivative)'),
            ('reflectance3rdDeriv', 'Reflectance (3rd Derivative)'),
            ('absoluteReflectance', 'Absolute Reflectance'),
            ('log1R', 'Log(1/R)'),
            ('log1RNoDeriv', 'Log(1/R) No Derivative'),
            ('log1R1stDeriv', 'Log(1/R) 1st Derivative'),
            ('log1R2ndDeriv', 'Log(1/R) 2nd Derivative'),
            ('radiance', 'Radiance'),
        ]

        for attr_name, display_name in data_types:
            checkbox = QCheckBox(display_name)
            # Check common ones by default
            if attr_name in ['reflectance', 'digitalNumber']:
                checkbox.setChecked(True)
            self.data_type_checkboxes[attr_name] = checkbox
            scroll_layout.addWidget(checkbox)

        scroll.setWidget(scroll_content)
        data_types_layout.addWidget(scroll)

        # Select all / Deselect all buttons
        button_row = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all_data_types)
        button_row.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self._deselect_all_data_types)
        button_row.addWidget(deselect_all_btn)

        data_types_layout.addLayout(button_row)
        self.data_types_group.setLayout(data_types_layout)
        layout.addWidget(self.data_types_group)

        # Connect format change to enable/disable data types
        self.csv_radio.toggled.connect(lambda checked: self.data_types_group.setEnabled(checked))

        # Output directory selection
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Directory:"))

        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setReadOnly(True)
        self.output_dir_edit.setPlaceholderText("Select output directory...")
        output_layout.addWidget(self.output_dir_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._select_output_dir)
        output_layout.addWidget(browse_btn)

        layout.addLayout(output_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.export_btn = QPushButton("Start Export")
        self.export_btn.clicked.connect(self._start_export)
        button_layout.addWidget(self.export_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._cancel_export)
        self.cancel_btn.setEnabled(False)
        button_layout.addWidget(self.cancel_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _select_all_data_types(self):
        """Select all data types"""
        for checkbox in self.data_type_checkboxes.values():
            checkbox.setChecked(True)

    def _deselect_all_data_types(self):
        """Deselect all data types"""
        for checkbox in self.data_type_checkboxes.values():
            checkbox.setChecked(False)

    def _select_output_dir(self):
        """Select output directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            "",
            QFileDialog.Option.ShowDirsOnly
        )

        if directory:
            self.output_dir = directory
            self.output_dir_edit.setText(directory)

    def _start_export(self):
        """Start batch export"""
        # Validate output directory
        if not self.output_dir:
            QMessageBox.warning(self, "No Output Directory",
                              "Please select an output directory first.")
            return

        # Get export format
        export_format = 'csv' if self.csv_radio.isChecked() else 'txt'

        # Get selected data types (for CSV)
        selected_types = []
        if export_format == 'csv':
            for attr_name, checkbox in self.data_type_checkboxes.items():
                if checkbox.isChecked():
                    selected_types.append(attr_name)

            if not selected_types:
                QMessageBox.warning(self, "No Data Types Selected",
                                  "Please select at least one data type to export.")
                return

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setVisible(True)
        self.progress_label.setText("Starting export...")

        # Disable export button, enable cancel
        self.export_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)

        # Create and start worker thread
        self.worker = BatchExportWorker(
            self.files,
            self.output_dir,
            selected_types,
            export_format
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _cancel_export(self):
        """Cancel export"""
        if self.worker:
            self.worker.cancel()
            self.cancel_btn.setEnabled(False)

    def _on_progress(self, percentage: int, filename: str):
        """Update progress"""
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(f"Exporting: {filename}")

    def _on_finished(self, success_count: int, total_count: int):
        """Handle export finished"""
        self.progress_label.setText(f"Export complete: {success_count}/{total_count} files")
        self.export_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

        QMessageBox.information(self, "Export Complete",
                              f"Successfully exported {success_count} out of {total_count} files.")

    def _on_error(self, filename: str, error_msg: str):
        """Handle export error"""
        logger.warning(f"Export error for {filename}: {error_msg}")
