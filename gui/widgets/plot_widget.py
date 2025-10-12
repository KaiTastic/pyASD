"""
Plot widget for spectral data visualization
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QCheckBox, QPushButton
from PyQt6.QtCore import pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np


class PlotWidget(QWidget):
    """
    Widget for plotting spectral data from ASD files
    """

    PLOT_TYPES = {
        'Digital Number': 'digitalNumber',
        'Reflectance': 'reflectance',
        'Reflectance (1st Derivative)': 'reflectance1stDeriv',
        'Reflectance (2nd Derivative)': 'reflectance2ndDeriv',
        'Reflectance (3rd Derivative)': 'reflectance3rdDeriv',
        'White Reference': 'whiteReference',
        'Absolute Reflectance': 'absoluteReflectance',
        'Log(1/R)': 'log1R',
        'Log(1/R) (1st Derivative)': 'log1R1stDeriv',
        'Log(1/R) (2nd Derivative)': 'log1R2ndDeriv',
        'Radiance': 'radiance',
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.asd_file = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)

        # Control panel
        control_layout = QHBoxLayout()

        # Plot type selector
        control_layout.addWidget(QLabel("Data Type:"))
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(self.PLOT_TYPES.keys())
        self.plot_type_combo.currentTextChanged.connect(self.update_plot)
        control_layout.addWidget(self.plot_type_combo)

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

        # Clear plot button
        clear_btn = QPushButton("Clear Plot")
        clear_btn.clicked.connect(self.clear_plot)
        control_layout.addWidget(clear_btn)

        layout.addLayout(control_layout)

        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Create initial plot
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Wavelength (nm)')
        self.ax.set_ylabel('Value')
        self.ax.set_title('Spectral Data')
        self.ax.grid(True)

    def set_asd_file(self, asd_file):
        """
        Set the ASD file to display

        Args:
            asd_file: ASDFile object
        """
        self.asd_file = asd_file
        self.update_plot()

    def get_data_for_plot_type(self, plot_type_name):
        """
        Get data array for the selected plot type

        Args:
            plot_type_name: Display name of plot type

        Returns:
            tuple: (data, ylabel) or (None, None) if data not available
        """
        if self.asd_file is None:
            return None, None

        attr_name = self.PLOT_TYPES[plot_type_name]

        try:
            data = getattr(self.asd_file, attr_name, None)

            if data is None:
                return None, None

            # Determine y-axis label
            if 'derivative' in plot_type_name.lower():
                ylabel = f'{plot_type_name}'
            elif 'digital' in plot_type_name.lower():
                ylabel = 'Digital Number'
            elif 'log' in plot_type_name.lower():
                ylabel = 'Log(1/R)'
            elif 'radiance' in plot_type_name.lower():
                ylabel = 'Radiance (W/m²/sr/nm)'
            elif 'reflectance' in plot_type_name.lower():
                ylabel = 'Reflectance'
            else:
                ylabel = plot_type_name

            return data, ylabel

        except Exception as e:
            print(f"Error getting data for {plot_type_name}: {e}")
            return None, None

    def update_plot(self):
        """Update the plot with current settings"""
        if self.asd_file is None:
            return

        plot_type = self.plot_type_combo.currentText()
        data, ylabel = self.get_data_for_plot_type(plot_type)

        if data is None:
            self.ax.clear()
            self.ax.text(0.5, 0.5, f'Data not available for {plot_type}',
                        ha='center', va='center', transform=self.ax.transAxes,
                        fontsize=12, color='red')
            self.canvas.draw()
            return

        wavelengths = self.asd_file.wavelengths

        if wavelengths is None:
            self.ax.clear()
            self.ax.text(0.5, 0.5, 'Wavelength data not available',
                        ha='center', va='center', transform=self.ax.transAxes,
                        fontsize=12, color='red')
            self.canvas.draw()
            return

        # Clear and plot
        self.ax.clear()

        # Plot data
        self.ax.plot(wavelengths, data, 'b-', linewidth=1.5, label=plot_type)

        # Set labels and title
        self.ax.set_xlabel('Wavelength (nm)', fontsize=11)
        self.ax.set_ylabel(ylabel, fontsize=11)

        # Add file name to title
        filename = self.asd_file.filename if hasattr(self.asd_file, 'filename') else 'Unknown'
        self.ax.set_title(f'{plot_type} - {filename}', fontsize=12, fontweight='bold')

        # Grid
        if self.grid_checkbox.isChecked():
            self.ax.grid(True, alpha=0.3)

        # Legend
        if self.legend_checkbox.isChecked():
            self.ax.legend(loc='best')

        # Add metadata annotations if available
        if hasattr(self.asd_file, 'metadata') and self.asd_file.metadata:
            metadata = self.asd_file.metadata
            info_text = []

            if hasattr(metadata, 'instrumentModel'):
                info_text.append(f"Instrument: {metadata.instrumentModel}")
            if hasattr(metadata, 'channels'):
                info_text.append(f"Channels: {metadata.channels}")

            if info_text:
                self.ax.text(0.02, 0.98, '\n'.join(info_text),
                            transform=self.ax.transAxes,
                            fontsize=9, verticalalignment='top',
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        self.figure.tight_layout()
        self.canvas.draw()

    def clear_plot(self):
        """Clear the current plot"""
        self.asd_file = None
        self.ax.clear()
        self.ax.set_xlabel('Wavelength (nm)')
        self.ax.set_ylabel('Value')
        self.ax.set_title('Spectral Data')
        self.ax.grid(True)
        self.canvas.draw()

    def export_figure(self, filepath, dpi=300):
        """
        Export the current figure to a file

        Args:
            filepath: Path to save the figure
            dpi: Resolution in dots per inch
        """
        self.figure.savefig(filepath, dpi=dpi, bbox_inches='tight')
