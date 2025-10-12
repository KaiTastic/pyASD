"""
File management panel for ASD file browser
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QListWidget, QLabel, QFileDialog, QMessageBox)
from PyQt6.QtCore import pyqtSignal, Qt
import os


class FilePanel(QWidget):
    """
    Widget for managing file operations and recent files
    """

    file_selected = pyqtSignal(str)  # Emits file path when a file is selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.recent_files = []
        self.max_recent_files = 10
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("<b>File Manager</b>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Button layout
        btn_layout = QHBoxLayout()

        # Open file button
        self.open_btn = QPushButton("Open File...")
        self.open_btn.clicked.connect(self.open_file_dialog)
        btn_layout.addWidget(self.open_btn)

        # Open folder button
        self.open_folder_btn = QPushButton("Open Folder...")
        self.open_folder_btn.clicked.connect(self.open_folder_dialog)
        btn_layout.addWidget(self.open_folder_btn)

        layout.addLayout(btn_layout)

        # Recent files list
        recent_label = QLabel("Recent Files:")
        layout.addWidget(recent_label)

        self.recent_files_list = QListWidget()
        self.recent_files_list.itemDoubleClicked.connect(self.on_recent_file_double_clicked)
        self.recent_files_list.setAlternatingRowColors(True)
        layout.addWidget(self.recent_files_list)

        # Clear recent files button
        clear_btn = QPushButton("Clear Recent Files")
        clear_btn.clicked.connect(self.clear_recent_files)
        layout.addWidget(clear_btn)

        # Current file info label
        self.current_file_label = QLabel("No file loaded")
        self.current_file_label.setWordWrap(True)
        self.current_file_label.setStyleSheet("QLabel { padding: 5px; background-color: #f0f0f0; border-radius: 3px; }")
        layout.addWidget(self.current_file_label)

    def open_file_dialog(self):
        """Open file dialog to select an ASD file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open ASD File",
            "",
            "ASD Files (*.asd);;All Files (*.*)"
        )

        if file_path:
            self.load_file(file_path)

    def open_folder_dialog(self):
        """Open folder dialog to browse ASD files"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder with ASD Files",
            ""
        )

        if folder_path:
            self.load_folder(folder_path)

    def load_file(self, file_path):
        """
        Load a file and emit signal

        Args:
            file_path: Path to the ASD file
        """
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found",
                              f"File not found:\n{file_path}")
            return

        if not file_path.lower().endswith('.asd'):
            reply = QMessageBox.question(
                self,
                "Non-ASD File",
                f"The selected file does not have .asd extension.\nDo you want to try to open it anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # Add to recent files
        self.add_recent_file(file_path)

        # Update current file label
        self.current_file_label.setText(f"Current: {os.path.basename(file_path)}")

        # Emit signal
        self.file_selected.emit(file_path)

    def load_folder(self, folder_path):
        """
        Load all ASD files from a folder

        Args:
            folder_path: Path to the folder
        """
        try:
            asd_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.asd')]

            if not asd_files:
                QMessageBox.information(self, "No ASD Files",
                                      f"No .asd files found in:\n{folder_path}")
                return

            # Add all files to recent files
            for filename in asd_files:
                full_path = os.path.join(folder_path, filename)
                self.add_recent_file(full_path)

            QMessageBox.information(self, "Folder Loaded",
                                  f"Found {len(asd_files)} ASD file(s) in the folder.\n"
                                  f"Double-click a file in the Recent Files list to open it.")

        except Exception as e:
            QMessageBox.critical(self, "Error",
                               f"Error loading folder:\n{str(e)}")

    def add_recent_file(self, file_path):
        """
        Add a file to the recent files list

        Args:
            file_path: Path to the file
        """
        # Remove if already exists
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)

        # Add to beginning
        self.recent_files.insert(0, file_path)

        # Limit size
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]

        # Update display
        self.update_recent_files_display()

    def update_recent_files_display(self):
        """Update the recent files list widget"""
        self.recent_files_list.clear()

        for file_path in self.recent_files:
            # Display filename with path as tooltip
            filename = os.path.basename(file_path)
            item = self.recent_files_list.addItem(filename)
            self.recent_files_list.item(self.recent_files_list.count() - 1).setToolTip(file_path)

    def on_recent_file_double_clicked(self, item):
        """Handle double-click on recent file"""
        index = self.recent_files_list.row(item)
        if 0 <= index < len(self.recent_files):
            file_path = self.recent_files[index]
            self.load_file(file_path)

    def clear_recent_files(self):
        """Clear the recent files list"""
        reply = QMessageBox.question(
            self,
            "Clear Recent Files",
            "Are you sure you want to clear the recent files list?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.recent_files.clear()
            self.update_recent_files_display()

    def get_recent_files(self):
        """Get the list of recent files"""
        return self.recent_files.copy()

    def set_recent_files(self, files):
        """
        Set the recent files list

        Args:
            files: List of file paths
        """
        self.recent_files = files[:self.max_recent_files]
        self.update_recent_files_display()
