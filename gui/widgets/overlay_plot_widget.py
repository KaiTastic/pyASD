"""
Overlay plot widget for displaying multiple spectra on a single plot
"""

import os
import logging
from typing import List
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QComboBox, QCheckBox, QPushButton, QDialog,
                              QDialogButtonBox)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np

logger = logging.getLogger(__name__)


class OverlayPlotDialog(QDialog):
    """
    Dialog for displaying multiple spectra overlaid on a single plot
    """

    # Color cycle for different spectra
    COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    def __init__(self, asd_files: List, parent=None):
        super().__init__(parent)
        self.asd_files = asd_files
        self.setWindowTitle(f"Overlay Plot - {len(asd_files)} Files")
        self.setGeometry(100, 100, 1200, 800)
        self._init_ui()
        self.update_plot()

    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)

        # Control panel
        control_layout = QHBoxLayout()

        # Data type selector
        control_layout.addWidget(QLabel("Data Type:"))
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems([
            'digitalNumber',
            'reflectance',
            'reflectance1stDeriv',
            'reflectance2ndDeriv',
            'reflectance3rdDeriv',
            'whiteReference',
            'absoluteReflectance',
            'log1R',
            'log1R1stDeriv',
            'log1R2ndDeriv',
            'radiance',
        ])
        self.data_type_combo.setCurrentText('reflectance')
        self.data_type_combo.currentTextChanged.connect(self.update_plot)
        control_layout.addWidget(self.data_type_combo)

        # Show grid checkbox
        self.grid_checkbox = QCheckBox("Show Grid")
        self.grid_checkbox.setChecked(True)
        self.grid_checkbox.stateChanged.connect(self.update_plot)
        control_layout.addWidget(self.grid_checkbox)

        # Show legend checkbox
        self.legend_checkbox = QCheckBox("Show Legend")
        self.legend_checkbox.setChecked(True)
        self.legend_checkbox.stateChanged.connect(self.update_plot)
        control_layout.addWidget(self.legend_checkbox)

        control_layout.addStretch()

        # Statistics checkbox
        self.stats_checkbox = QCheckBox("Show Statistics")
        self.stats_checkbox.setChecked(False)
        self.stats_checkbox.stateChanged.connect(self.update_plot)
        control_layout.addWidget(self.stats_checkbox)

        # Export button
        export_btn = QPushButton("Export Plot")
        export_btn.clicked.connect(self._export_plot)
        control_layout.addWidget(export_btn)

        layout.addLayout(control_layout)

        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.info_label)

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)

        # Create plot axes
        self.ax = self.figure.add_subplot(111)

    def update_plot(self):
        """Update the overlay plot"""
        self.ax.clear()

        data_type = self.data_type_combo.currentText()
        plotted_count = 0
        all_data = []

        # Plot each spectrum
        for idx, asd_file in enumerate(self.asd_files):
            wavelengths = asd_file.wavelengths
            data = getattr(asd_file, data_type, None)

            if data is None or wavelengths is None:
                continue

            # Get color from cycle
            color = self.COLORS[idx % len(self.COLORS)]

            # Plot with label
            filename = os.path.basename(asd_file.filepath)
            self.ax.plot(wavelengths, data, color=color, linewidth=1.5,
                        label=filename, alpha=0.8)

            all_data.append(data)
            plotted_count += 1

        if plotted_count == 0:
            self.ax.text(0.5, 0.5, f'No data available for {data_type}',
                        ha='center', va='center', transform=self.ax.transAxes,
                        fontsize=12, color='red')
            self.canvas.draw()
            return

        # Add statistics if requested
        if self.stats_checkbox.isChecked() and all_data:
            all_data_array = np.array(all_data)
            mean_data = np.mean(all_data_array, axis=0)
            std_data = np.std(all_data_array, axis=0)

            # Plot mean
            self.ax.plot(wavelengths, mean_data, 'k--', linewidth=2,
                        label='Mean', alpha=0.7)

            # Plot std deviation band
            self.ax.fill_between(wavelengths,
                                mean_data - std_data,
                                mean_data + std_data,
                                color='gray', alpha=0.2,
                                label='±1 Std Dev')

        # Set labels and title
        self.ax.set_xlabel('Wavelength (nm)', fontsize=12)
        self.ax.set_ylabel(self._get_ylabel(data_type), fontsize=12)
        self.ax.set_title(f'Overlay Plot: {data_type}\n({plotted_count} spectra)',
                         fontsize=14, fontweight='bold')

        # Grid
        if self.grid_checkbox.isChecked():
            self.ax.grid(True, alpha=0.3, linestyle='--')

        # Legend
        if self.legend_checkbox.isChecked():
            # Place legend outside plot area for better visibility
            self.ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),
                          fontsize=9)

        # Update info label
        self.info_label.setText(f"Displaying {plotted_count} of {len(self.asd_files)} spectra")

        self.figure.tight_layout()
        self.canvas.draw()

    def _get_ylabel(self, data_type: str) -> str:
        """Get Y-axis label"""
        ylabel_map = {
            'digitalNumber': 'Digital Number',
            'reflectance': 'Reflectance',
            'reflectance1stDeriv': '1st Derivative',
            'reflectance2ndDeriv': '2nd Derivative',
            'reflectance3rdDeriv': '3rd Derivative',
            'whiteReference': 'White Reference',
            'absoluteReflectance': 'Absolute Reflectance',
            'log1R': 'Log(1/R)',
            'log1R1stDeriv': 'Log(1/R) 1st Derivative',
            'log1R2ndDeriv': 'Log(1/R) 2nd Derivative',
            'radiance': 'Radiance (W/m²/sr/nm)',
        }
        return ylabel_map.get(data_type, data_type)

    def _export_plot(self):
        """Export the overlay plot"""
        from PyQt6.QtWidgets import QFileDialog

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Overlay Plot",
            "overlay_plot.png",
            "PNG Files (*.png);;SVG Files (*.svg);;PDF Files (*.pdf);;All Files (*.*)"
        )

        if filepath:
            try:
                self.figure.savefig(filepath, dpi=300, bbox_inches='tight')
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Export Successful",
                                      f"Plot exported to:\n{filepath}")
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Export Failed",
                                   f"Failed to export plot:\n{str(e)}")
