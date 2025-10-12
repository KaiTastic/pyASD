"""
Main window for pyASDReader GUI application
"""

import sys
import os
from typing import List
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QSplitter, QMenuBar, QMenu, QFileDialog,
                              QMessageBox, QStatusBar, QDialog, QDialogButtonBox,
                              QListWidget, QLabel, QCheckBox, QScrollArea)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyASDReader import ASDFile
from gui.widgets import PlotWidget, MetadataWidget, FilePanel
from gui.widgets.properties_panel import PropertiesPanel
from gui.widgets.multi_plot_canvas import MultiPlotCanvas, LayoutMode
from gui.utils import ExportManager


class DataTypeSelectionDialog(QDialog):
    """Dialog for selecting data types to export"""

    def __init__(self, available_types, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Data Types to Export")
        self.available_types = available_types
        self.selected_types = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        label = QLabel("Select the data types you want to export:")
        layout.addWidget(label)

        # Create checkboxes for each data type
        self.checkboxes = {}
        for display_name, attr_name in self.available_types.items():
            checkbox = QCheckBox(display_name)
            checkbox.setChecked(True)  # Default to all selected
            self.checkboxes[attr_name] = checkbox
            layout.addWidget(checkbox)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_types(self):
        """Get list of selected data type attribute names"""
        selected = []
        for attr_name, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                selected.append(attr_name)
        return selected


class MainWindow(QMainWindow):
    """
    Main application window for pyASDReader GUI
    """

    def __init__(self):
        super().__init__()
        self.current_asd_file = None
        self.settings = QSettings("pyASDReader", "GUI")
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Initialize the user interface - Three-column layout"""
        self.setWindowTitle("pyASDReader - ASD File Viewer")
        self.setGeometry(100, 100, 1600, 900)

        # Create central widget with splitter layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Create main splitter (horizontal) - Three columns
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: File browser
        self.file_panel = FilePanel()
        self.file_panel.file_selected.connect(self.load_asd_file)
        self.file_panel.files_checked.connect(self._on_files_checked)
        main_splitter.addWidget(self.file_panel)

        # Center panel: Multi-plot canvas (main work area)
        self.multi_plot_canvas = MultiPlotCanvas()
        main_splitter.addWidget(self.multi_plot_canvas)

        # Keep reference to plot_widget for compatibility
        # Single plot mode uses first subplot
        self.plot_widget = None

        # Right panel: Properties panel
        self.properties_panel = PropertiesPanel()
        main_splitter.addWidget(self.properties_panel)

        # Set initial sizes for three columns
        # Left: 280px, Center: 800px (flexible), Right: 320px
        main_splitter.setSizes([280, 800, 320])

        # Allow left and right panels to collapse
        main_splitter.setCollapsible(0, True)  # Left panel can collapse
        main_splitter.setCollapsible(1, False)  # Center panel cannot collapse
        main_splitter.setCollapsible(2, True)  # Right panel can collapse

        main_layout.addWidget(main_splitter)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Create menu bar (after widgets are created)
        self.create_menu_bar()

    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open File...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.file_panel.open_file_dialog)
        file_menu.addAction(open_action)

        open_folder_action = QAction("Open &Folder...", self)
        open_folder_action.setShortcut("Ctrl+Shift+O")
        open_folder_action.triggered.connect(self.file_panel.open_folder_dialog)
        file_menu.addAction(open_folder_action)

        file_menu.addSeparator()

        close_action = QAction("&Close File", self)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(self.close_current_file)
        file_menu.addAction(close_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Export menu
        export_menu = menubar.addMenu("&Export")

        export_csv_action = QAction("Export Data to &CSV...", self)
        export_csv_action.triggered.connect(self.export_to_csv)
        export_menu.addAction(export_csv_action)

        export_metadata_action = QAction("Export &Metadata to TXT...", self)
        export_metadata_action.triggered.connect(self.export_metadata)
        export_menu.addAction(export_metadata_action)

        export_menu.addSeparator()

        export_plot_png_action = QAction("Export Plot as &PNG...", self)
        export_plot_png_action.triggered.connect(lambda: self.export_plot('png'))
        export_menu.addAction(export_plot_png_action)

        export_plot_svg_action = QAction("Export Plot as &SVG...", self)
        export_plot_svg_action.triggered.connect(lambda: self.export_plot('svg'))
        export_menu.addAction(export_plot_svg_action)

        export_plot_pdf_action = QAction("Export Plot as P&DF...", self)
        export_plot_pdf_action.triggered.connect(lambda: self.export_plot('pdf'))
        export_menu.addAction(export_plot_pdf_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        refresh_action = QAction("&Refresh Plots", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_all_plots)
        view_menu.addAction(refresh_action)

        clear_plot_action = QAction("&Clear All Plots", self)
        clear_plot_action.triggered.connect(self._clear_all_plots)
        view_menu.addAction(clear_plot_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def load_asd_file(self, filepath):
        """
        Load an ASD file (single file mode)

        Args:
            filepath: Path to the ASD file
        """
        try:
            self.status_bar.showMessage(f"Loading {os.path.basename(filepath)}...")

            # Load the file
            asd_file = ASDFile(filepath)

            # Update current file
            self.current_asd_file = asd_file

            # Load to first subplot
            if self.multi_plot_canvas.subplots:
                self.multi_plot_canvas.subplots[0].load_data(asd_file, 'reflectance')

            # Update properties panel
            self.properties_panel.set_asd_file(asd_file)

            self.status_bar.showMessage(f"Loaded: {os.path.basename(filepath)}", 5000)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Loading File",
                f"Failed to load ASD file:\n{filepath}\n\nError: {str(e)}"
            )
            self.status_bar.showMessage("Error loading file", 5000)

    def _on_files_checked(self, files: List[str]):
        """
        Handle multiple files checked in file browser

        Automatically switch to appropriate layout based on file count
        """
        if not files:
            return

        num_files = len(files)

        # Select appropriate layout
        if num_files == 1:
            layout_mode = LayoutMode.SINGLE
        elif num_files == 2:
            layout_mode = LayoutMode.HORIZONTAL_2
        elif num_files == 3:
            layout_mode = LayoutMode.HORIZONTAL_3
        elif num_files == 4:
            layout_mode = LayoutMode.GRID_2x2
        elif num_files <= 6:
            layout_mode = LayoutMode.GRID_2x3
        else:
            # Too many files, only load first 6
            files = files[:6]
            layout_mode = LayoutMode.GRID_2x3
            QMessageBox.information(
                self,
                "Too Many Files",
                f"Only first 6 files will be displayed.\nTotal selected: {num_files}"
            )

        # Switch layout and load files
        self.multi_plot_canvas.set_layout_mode(layout_mode)
        self.multi_plot_canvas.load_files_to_subplots(files, 'reflectance')

        self.status_bar.showMessage(f"Loaded {len(files)} files in {layout_mode.value} layout", 5000)

    def close_current_file(self):
        """Close the currently loaded file"""
        self.current_asd_file = None
        self.multi_plot_canvas.clear_all()
        self.properties_panel.clear()
        self.status_bar.showMessage("File closed", 3000)

    def _refresh_all_plots(self):
        """Refresh all plots"""
        for subplot in self.multi_plot_canvas.subplots:
            if subplot.ax:
                subplot.canvas.draw()
        self.status_bar.showMessage("Plots refreshed", 2000)

    def _clear_all_plots(self):
        """Clear all plots"""
        self.multi_plot_canvas.clear_all()
        self.status_bar.showMessage("All plots cleared", 2000)

    def export_to_csv(self):
        """Export current data to CSV"""
        if self.current_asd_file is None:
            QMessageBox.warning(self, "No File Loaded",
                              "Please load an ASD file first.")
            return

        # Get available data types
        available_types = ExportManager.get_available_export_data_types(self.current_asd_file)

        if not available_types:
            QMessageBox.warning(self, "No Data Available",
                              "No exportable data available in the current file.")
            return

        # Show data type selection dialog
        dialog = DataTypeSelectionDialog(available_types, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        selected_types = dialog.get_selected_types()

        if not selected_types:
            QMessageBox.warning(self, "No Data Selected",
                              "Please select at least one data type to export.")
            return

        # Get save file path
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export to CSV",
            f"{os.path.splitext(self.current_asd_file.filename)[0]}_export.csv",
            "CSV Files (*.csv);;All Files (*.*)"
        )

        if not filepath:
            return

        try:
            ExportManager.export_to_csv(self.current_asd_file, filepath, selected_types)
            QMessageBox.information(self, "Export Successful",
                                  f"Data exported successfully to:\n{filepath}")
            self.status_bar.showMessage(f"Exported to {os.path.basename(filepath)}", 5000)

        except Exception as e:
            QMessageBox.critical(self, "Export Failed",
                               f"Failed to export data:\n{str(e)}")

    def export_metadata(self):
        """Export metadata to text file"""
        if self.current_asd_file is None:
            QMessageBox.warning(self, "No File Loaded",
                              "Please load an ASD file first.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Metadata",
            f"{os.path.splitext(self.current_asd_file.filename)[0]}_metadata.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )

        if not filepath:
            return

        try:
            ExportManager.export_metadata_to_txt(self.current_asd_file, filepath)
            QMessageBox.information(self, "Export Successful",
                                  f"Metadata exported successfully to:\n{filepath}")
            self.status_bar.showMessage(f"Exported metadata to {os.path.basename(filepath)}", 5000)

        except Exception as e:
            QMessageBox.critical(self, "Export Failed",
                               f"Failed to export metadata:\n{str(e)}")

    def export_plot(self, format_type):
        """
        Export current plots

        Args:
            format_type: File format ('png', 'svg', 'pdf')
        """
        if not self.multi_plot_canvas.subplots:
            QMessageBox.warning(self, "No Plot",
                              "No plots to export.")
            return

        format_upper = format_type.upper()
        filter_str = f"{format_upper} Files (*.{format_type});;All Files (*.*)"

        default_name = "multiplot" if len(self.multi_plot_canvas.subplots) > 1 else "plot"

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            f"Export Plots as {format_upper}",
            f"{default_name}.{format_type}",
            filter_str
        )

        if not filepath:
            return

        try:
            # Export first subplot's figure (for now)
            # TODO: Export combined figure for multiple subplots
            if self.multi_plot_canvas.subplots:
                first_subplot = self.multi_plot_canvas.subplots[0]
                first_subplot.figure.savefig(filepath, dpi=300, bbox_inches='tight')

            QMessageBox.information(self, "Export Successful",
                                  f"Plot exported successfully to:\n{filepath}")
            self.status_bar.showMessage(f"Exported plot to {os.path.basename(filepath)}", 5000)

        except Exception as e:
            QMessageBox.critical(self, "Export Failed",
                               f"Failed to export plot:\n{str(e)}")

    def show_about_dialog(self):
        """Show about dialog"""
        about_text = """
        <h2>pyASDReader GUI</h2>
        <p>A graphical user interface for viewing and analyzing ASD spectral files.</p>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Features:</b></p>
        <ul>
            <li>Load and visualize ASD files (all versions v1-v8)</li>
            <li>View file metadata and spectral information</li>
            <li>Plot various data types (DN, Reflectance, Derivatives, etc.)</li>
            <li>Export data to CSV and plots to PNG/SVG/PDF</li>
        </ul>
        <p><b>Library:</b> pyASDReader</p>
        <p><b>Author:</b> Kai Cao</p>
        """

        QMessageBox.about(self, "About pyASDReader GUI", about_text)

    def load_settings(self):
        """Load application settings"""
        # Restore last opened directory
        last_dir = self.settings.value("last_directory", "")
        if last_dir and os.path.isdir(last_dir):
            self.file_panel.load_directory(last_dir)

        # Restore window geometry
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def save_settings(self):
        """Save application settings"""
        # Save last opened directory
        if hasattr(self.file_panel.tree_widget, 'current_root') and self.file_panel.tree_widget.current_root:
            self.settings.setValue("last_directory", self.file_panel.tree_widget.current_root)

        # Save window geometry
        self.settings.setValue("geometry", self.saveGeometry())

    def closeEvent(self, event):
        """Handle window close event"""
        self.save_settings()
        event.accept()
