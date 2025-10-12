"""
Statistics widget for displaying spectral data statistics
"""

import numpy as np
from typing import Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QFormLayout,
                              QLabel, QScrollArea)
from PyQt6.QtCore import Qt
from pyASDReader import ASDFile


class StatisticsWidget(QScrollArea):
    """
    Widget for displaying statistics of spectral data

    Shows:
    - Global statistics (min, max, mean, std, median)
    - Per-band statistics (VNIR, SWIR1, SWIR2)
    - Signal-to-noise ratio estimates
    """

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI"""
        content = QWidget()
        layout = QVBoxLayout(content)

        # Global statistics group
        global_group = QGroupBox("Global Statistics")
        global_layout = QFormLayout()

        self.min_label = QLabel("--")
        global_layout.addRow("Minimum:", self.min_label)

        self.max_label = QLabel("--")
        global_layout.addRow("Maximum:", self.max_label)

        self.mean_label = QLabel("--")
        global_layout.addRow("Mean:", self.mean_label)

        self.median_label = QLabel("--")
        global_layout.addRow("Median:", self.median_label)

        self.std_label = QLabel("--")
        global_layout.addRow("Std Deviation:", self.std_label)

        self.range_label = QLabel("--")
        global_layout.addRow("Range:", self.range_label)

        global_group.setLayout(global_layout)
        layout.addWidget(global_group)

        # Per-band statistics
        band_group = QGroupBox("Per-Band Statistics")
        band_layout = QVBoxLayout()

        # VNIR band
        self.vnir_group = QGroupBox("VNIR (350-1000 nm)")
        vnir_layout = QFormLayout()
        self.vnir_mean_label = QLabel("--")
        vnir_layout.addRow("Mean:", self.vnir_mean_label)
        self.vnir_std_label = QLabel("--")
        vnir_layout.addRow("Std Dev:", self.vnir_std_label)
        self.vnir_group.setLayout(vnir_layout)
        band_layout.addWidget(self.vnir_group)

        # SWIR1 band
        self.swir1_group = QGroupBox("SWIR1 (1000-1800 nm)")
        swir1_layout = QFormLayout()
        self.swir1_mean_label = QLabel("--")
        swir1_layout.addRow("Mean:", self.swir1_mean_label)
        self.swir1_std_label = QLabel("--")
        swir1_layout.addRow("Std Dev:", self.swir1_std_label)
        self.swir1_group.setLayout(swir1_layout)
        band_layout.addWidget(self.swir1_group)

        # SWIR2 band
        self.swir2_group = QGroupBox("SWIR2 (1800-2500 nm)")
        swir2_layout = QFormLayout()
        self.swir2_mean_label = QLabel("--")
        swir2_layout.addRow("Mean:", self.swir2_mean_label)
        self.swir2_std_label = QLabel("--")
        swir2_layout.addRow("Std Dev:", self.swir2_std_label)
        self.swir2_group.setLayout(swir2_layout)
        band_layout.addWidget(self.swir2_group)

        band_group.setLayout(band_layout)
        layout.addWidget(band_group)

        # Signal quality
        quality_group = QGroupBox("Signal Quality")
        quality_layout = QFormLayout()

        self.snr_label = QLabel("--")
        quality_layout.addRow("SNR Estimate:", self.snr_label)

        self.saturation_label = QLabel("--")
        quality_layout.addRow("Saturation:", self.saturation_label)

        quality_group.setLayout(quality_layout)
        layout.addWidget(quality_group)

        layout.addStretch()
        self.setWidget(content)

    def update_statistics(self, asd_file: Optional[ASDFile], data_type: str = 'reflectance'):
        """
        Update statistics for given ASD file and data type

        Args:
            asd_file: ASD file object
            data_type: Type of data to calculate statistics for
        """
        if asd_file is None:
            self.clear()
            return

        wavelengths = asd_file.wavelengths
        data = getattr(asd_file, data_type, None)

        if data is None or wavelengths is None:
            self.clear()
            return

        # Global statistics
        self.min_label.setText(f"{np.min(data):.6f}")
        self.max_label.setText(f"{np.max(data):.6f}")
        self.mean_label.setText(f"{np.mean(data):.6f}")
        self.median_label.setText(f"{np.median(data):.6f}")
        self.std_label.setText(f"{np.std(data):.6f}")
        self.range_label.setText(f"{np.max(data) - np.min(data):.6f}")

        # Per-band statistics
        self._calculate_band_statistics(wavelengths, data)

        # Signal quality
        self._calculate_signal_quality(data, data_type)

    def _calculate_band_statistics(self, wavelengths: np.ndarray, data: np.ndarray):
        """Calculate per-band statistics"""
        # VNIR (350-1000 nm)
        vnir_mask = (wavelengths >= 350) & (wavelengths <= 1000)
        if np.any(vnir_mask):
            vnir_data = data[vnir_mask]
            self.vnir_mean_label.setText(f"{np.mean(vnir_data):.6f}")
            self.vnir_std_label.setText(f"{np.std(vnir_data):.6f}")
        else:
            self.vnir_mean_label.setText("N/A")
            self.vnir_std_label.setText("N/A")

        # SWIR1 (1000-1800 nm)
        swir1_mask = (wavelengths > 1000) & (wavelengths <= 1800)
        if np.any(swir1_mask):
            swir1_data = data[swir1_mask]
            self.swir1_mean_label.setText(f"{np.mean(swir1_data):.6f}")
            self.swir1_std_label.setText(f"{np.std(swir1_data):.6f}")
        else:
            self.swir1_mean_label.setText("N/A")
            self.swir1_std_label.setText("N/A")

        # SWIR2 (1800-2500 nm)
        swir2_mask = (wavelengths > 1800) & (wavelengths <= 2500)
        if np.any(swir2_mask):
            swir2_data = data[swir2_mask]
            self.swir2_mean_label.setText(f"{np.mean(swir2_data):.6f}")
            self.swir2_std_label.setText(f"{np.std(swir2_data):.6f}")
        else:
            self.swir2_mean_label.setText("N/A")
            self.swir2_std_label.setText("N/A")

    def _calculate_signal_quality(self, data: np.ndarray, data_type: str):
        """Calculate signal quality metrics"""
        # SNR estimate (mean / std)
        mean_val = np.mean(data)
        std_val = np.std(data)

        if std_val > 0:
            snr = mean_val / std_val
            self.snr_label.setText(f"{snr:.2f}")
        else:
            self.snr_label.setText("N/A")

        # Check for saturation
        # For reflectance, values should be between 0 and 1
        # For DN, check if values are at max (typically 65535 for 16-bit)
        if data_type == 'reflectance' or 'reflectance' in data_type.lower():
            saturated = np.sum(data >= 1.0)
            total = len(data)
            saturation_pct = (saturated / total) * 100
            self.saturation_label.setText(f"{saturation_pct:.2f}% ({saturated}/{total} channels)")
        elif data_type == 'digitalNumber':
            # Check for 16-bit saturation
            saturated = np.sum(data >= 65535)
            total = len(data)
            saturation_pct = (saturated / total) * 100
            self.saturation_label.setText(f"{saturation_pct:.2f}% ({saturated}/{total} channels)")
        else:
            self.saturation_label.setText("N/A")

    def clear(self):
        """Clear all statistics"""
        self.min_label.setText("--")
        self.max_label.setText("--")
        self.mean_label.setText("--")
        self.median_label.setText("--")
        self.std_label.setText("--")
        self.range_label.setText("--")

        self.vnir_mean_label.setText("--")
        self.vnir_std_label.setText("--")
        self.swir1_mean_label.setText("--")
        self.swir1_std_label.setText("--")
        self.swir2_mean_label.setText("--")
        self.swir2_std_label.setText("--")

        self.snr_label.setText("--")
        self.saturation_label.setText("--")
