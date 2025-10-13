"""
Multi-plot canvas for displaying multiple spectral plots

Phase 2 - Supports 7 layout modes:
- 1×1 (Single)
- 1×2 (Horizontal 2)
- 2×1 (Vertical 2)
- 2×2 (Grid 2×2)
- 1×3 (Horizontal 3)
- 3×1 (Vertical 3)
- 2×3 (Grid 2×3)
"""

import os
import logging
from enum import Enum
from typing import List, Tuple, Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QPushButton, QComboBox, QCheckBox, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class LayoutMode(Enum):
    """Layout mode enumeration"""
    SINGLE = "1x1"          # Single plot
    HORIZONTAL_2 = "1x2"    # Horizontal 2
    VERTICAL_2 = "2x1"      # Vertical 2
    GRID_2x2 = "2x2"        # 2×2 grid
    HORIZONTAL_3 = "1x3"    # Horizontal 3
    VERTICAL_3 = "3x1"      # Vertical 3
    GRID_2x3 = "2x3"        # 2×3 grid


class SyncManager:
    """
    Subplot synchronization manager

    Handles synchronization of zoom, cursor, and pan across multiple subplots
    """

    def __init__(self):
        self.subplots = []
        self.sync_zoom = True
        self.sync_cursor = True
        self.sync_pan = False

    def register_subplot(self, subplot):
        """Register a subplot"""
        self.subplots.append(subplot)

    def clear(self):
        """Clear all registered subplots"""
        self.subplots.clear()

    def sync_zoom_to_all(self, source_row: int, source_col: int, xlim, ylim):
        """Synchronize zoom to all subplots"""
        if not self.sync_zoom:
            return

        for subplot in self.subplots:
            # Skip source subplot
            if subplot.row == source_row and subplot.col == source_col:
                continue

            # Sync X-axis (wavelength is always the same)
            if xlim and subplot.ax:
                subplot.ax.set_xlim(xlim)
                subplot.canvas.draw_idle()

    def sync_cursor_to_all(self, source_row: int, source_col: int, x: float, y: float):
        """Synchronize cursor to all subplots"""
        if not self.sync_cursor:
            return

        for subplot in self.subplots:
            # Skip source subplot
            if subplot.row == source_row and subplot.col == source_col:
                continue

            # Remove old cursor line
            if hasattr(subplot, '_sync_cursor_line') and subplot.ax:
                try:
                    subplot._sync_cursor_line.remove()
                except:
                    pass

            # Draw new cursor line
            if subplot.ax:
                subplot._sync_cursor_line = subplot.ax.axvline(
                    x, color='red', linestyle='--', alpha=0.5, linewidth=1
                )
                subplot.canvas.draw_idle()


class SubPlotControlBar(QWidget):
    """
    Subplot control bar

    Displayed at the top of each subplot
    """

    file_changed = pyqtSignal(str)
    data_type_changed = pyqtSignal(str)
    clear_requested = pyqtSignal()

    def __init__(self, row: int, col: int):
        super().__init__()
        self.row = row
        self.col = col

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(5)

        # Position label
        pos_label = QLabel(f"[{row},{col}]")
        pos_label.setStyleSheet("color: gray; font-size: 9px; font-family: monospace;")
        layout.addWidget(pos_label)

        # File selection
        layout.addWidget(QLabel("File:"))
        self.file_combo = QComboBox()
        self.file_combo.setMaximumWidth(120)
        self.file_combo.currentTextChanged.connect(self.file_changed)
        layout.addWidget(self.file_combo)

        # Data type selection
        layout.addWidget(QLabel("Type:"))
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
        self.data_type_combo.setMaximumWidth(100)
        self.data_type_combo.currentTextChanged.connect(self.data_type_changed)
        layout.addWidget(self.data_type_combo)

        layout.addStretch()

        # Cursor position display
        self.cursor_label = QLabel("")
        self.cursor_label.setStyleSheet("font-size: 9px; color: #555;")
        layout.addWidget(self.cursor_label)

        # Clear button
        self.clear_btn = QPushButton("✕")
        self.clear_btn.setMaximumWidth(20)
        self.clear_btn.setMaximumHeight(18)
        self.clear_btn.setToolTip("Clear this subplot")
        self.clear_btn.clicked.connect(self.clear_requested)
        layout.addWidget(self.clear_btn)

    def update_file_list(self, files: List[str]):
        """Update file list"""
        self.file_combo.clear()
        self.file_combo.addItems([os.path.basename(f) for f in files])

    def set_current_file(self, filename: str):
        """Set current file"""
        index = self.file_combo.findText(os.path.basename(filename))
        if index >= 0:
            self.file_combo.setCurrentIndex(index)

    def set_current_data_type(self, data_type: str):
        """Set current data type"""
        index = self.data_type_combo.findText(data_type)
        if index >= 0:
            self.data_type_combo.setCurrentIndex(index)

    def update_cursor_position(self, x: float, y: float):
        """Update cursor position display"""
        self.cursor_label.setText(f"λ={x:.1f}nm, y={y:.4f}")


class SubPlotWidget(QWidget):
    """
    Single subplot widget

    Features:
    - matplotlib plotting
    - Independent control bar
    - Data loading
    - Event emission
    """

    zoom_changed = pyqtSignal(int, int, object, object)  # row, col, xlim, ylim
    cursor_moved = pyqtSignal(int, int, float, float)    # row, col, x, y
    selected = pyqtSignal()

    def __init__(self, row: int, col: int):
        super().__init__()
        self.row = row
        self.col = col
        self.current_file = None
        self.current_data_type = None

        self._init_ui()
        self._setup_interactions()

    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # Subplot control bar
        self.control_bar = SubPlotControlBar(self.row, self.col)
        self.control_bar.file_changed.connect(self._on_file_changed)
        self.control_bar.data_type_changed.connect(self._on_data_type_changed)
        self.control_bar.clear_requested.connect(self.clear)
        layout.addWidget(self.control_bar)

        # matplotlib figure
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # Set style
        self.ax.set_facecolor('#f8f8f8')
        self.ax.grid(True, alpha=0.3, linestyle='--')

        layout.addWidget(self.canvas)

        # Toolbar (optional display)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setMaximumHeight(30)
        layout.addWidget(self.toolbar)

        # Focus style
        self.setAutoFillBackground(True)
        self._update_focus_style(False)

    def _setup_interactions(self):
        """Setup interactions"""
        # matplotlib events
        self.canvas.mpl_connect('button_press_event', self._on_mouse_press)
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
        self.canvas.mpl_connect('scroll_event', self._on_mouse_scroll)

        # Focus events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def focusInEvent(self, event):
        """Gain focus"""
        super().focusInEvent(event)
        self._update_focus_style(True)
        self.selected.emit()

    def focusOutEvent(self, event):
        """Lose focus"""
        super().focusOutEvent(event)
        self._update_focus_style(False)

    def _update_focus_style(self, focused: bool):
        """Update focus style"""
        if focused:
            self.setStyleSheet("SubPlotWidget { border: 2px solid #2196F3; }")
        else:
            self.setStyleSheet("SubPlotWidget { border: 1px solid #ccc; }")

    def load_data(self, asd_file, data_type: str):
        """
        Load data to subplot

        Args:
            asd_file: ASD file object
            data_type: Data type (e.g., 'reflectance')
        """
        from pyASDReader import ASDFile

        self.current_file = asd_file
        self.current_data_type = data_type

        # Update control bar
        self.control_bar.set_current_file(asd_file.filepath)
        self.control_bar.set_current_data_type(data_type)

        # Get data
        wavelengths = asd_file.wavelengths
        data = getattr(asd_file, data_type, None)

        if data is None or wavelengths is None:
            self._show_no_data_message(data_type)
            return

        # Clear and plot
        self.ax.clear()
        self.ax.plot(wavelengths, data, 'b-', linewidth=1.5, label=data_type)

        # Set labels
        self.ax.set_xlabel('Wavelength (nm)', fontsize=10)
        self.ax.set_ylabel(self._get_ylabel(data_type), fontsize=10)
        self.ax.set_title(f"{os.path.basename(asd_file.filepath)}\n{data_type}",
                         fontsize=10, fontweight='bold')

        # Grid and legend
        self.ax.grid(True, alpha=0.3, linestyle='--')
        self.ax.legend(loc='best', fontsize=8)

        # Update canvas
        self.figure.tight_layout()
        self.canvas.draw()

    def _show_no_data_message(self, data_type: str):
        """Show no data message"""
        self.ax.clear()
        self.ax.text(0.5, 0.5, f"No data available for\n{data_type}",
                    ha='center', va='center', transform=self.ax.transAxes,
                    fontsize=12, color='gray')
        self.ax.axis('off')
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

    def _on_mouse_press(self, event):
        """Mouse click"""
        if event.inaxes == self.ax:
            self.setFocus()

    def _on_mouse_move(self, event):
        """Mouse move"""
        if event.inaxes == self.ax and event.xdata and event.ydata:
            # Emit cursor position
            self.cursor_moved.emit(self.row, self.col, event.xdata, event.ydata)

            # Update control bar display
            self.control_bar.update_cursor_position(event.xdata, event.ydata)

    def _on_mouse_scroll(self, event):
        """Mouse scroll (zoom)"""
        if event.inaxes == self.ax:
            # Emit signal after zoom
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            self.zoom_changed.emit(self.row, self.col, xlim, ylim)

    def _on_file_changed(self, filename: str):
        """File changed in combo box"""
        # TODO: Implement file change handling
        pass

    def _on_data_type_changed(self, data_type: str):
        """Data type changed in combo box"""
        if self.current_file:
            self.load_data(self.current_file, data_type)

    def clear(self):
        """Clear subplot"""
        self.current_file = None
        self.current_data_type = None
        self.ax.clear()
        self.ax.text(0.5, 0.5, 'Empty',
                    ha='center', va='center', transform=self.ax.transAxes,
                    fontsize=14, color='lightgray')
        self.ax.axis('off')
        self.canvas.draw()


class MultiPlotControlBar(QWidget):
    """
    Multi-plot layout control bar
    """

    layout_changed = pyqtSignal(LayoutMode)
    sync_zoom_changed = pyqtSignal(bool)
    sync_cursor_changed = pyqtSignal(bool)
    sync_pan_changed = pyqtSignal(bool)
    reset_all_requested = pyqtSignal()
    export_all_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Layout selection
        layout.addWidget(QLabel("Layout:"))

        self.layout_buttons = {}
        layouts = [
            ("1×1", LayoutMode.SINGLE),
            ("1×2", LayoutMode.HORIZONTAL_2),
            ("2×1", LayoutMode.VERTICAL_2),
            ("2×2", LayoutMode.GRID_2x2),
            ("1×3", LayoutMode.HORIZONTAL_3),
            ("3×1", LayoutMode.VERTICAL_3),
            ("2×3", LayoutMode.GRID_2x3),
        ]

        for text, mode in layouts:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setMaximumWidth(45)
            btn.clicked.connect(lambda checked, m=mode:
                              self._on_layout_button_clicked(m))
            self.layout_buttons[mode] = btn
            layout.addWidget(btn)

        # Default select single plot
        self.layout_buttons[LayoutMode.SINGLE].setChecked(True)

        layout.addSpacing(20)

        # Sync controls
        layout.addWidget(QLabel("Sync:"))

        self.sync_zoom_check = QCheckBox("Zoom")
        self.sync_zoom_check.setChecked(True)
        self.sync_zoom_check.stateChanged.connect(
            lambda state: self.sync_zoom_changed.emit(state == Qt.CheckState.Checked)
        )
        layout.addWidget(self.sync_zoom_check)

        self.sync_cursor_check = QCheckBox("Cursor")
        self.sync_cursor_check.setChecked(True)
        self.sync_cursor_check.stateChanged.connect(
            lambda state: self.sync_cursor_changed.emit(state == Qt.CheckState.Checked)
        )
        layout.addWidget(self.sync_cursor_check)

        self.sync_pan_check = QCheckBox("Pan")
        self.sync_pan_check.stateChanged.connect(
            lambda state: self.sync_pan_changed.emit(state == Qt.CheckState.Checked)
        )
        layout.addWidget(self.sync_pan_check)

        layout.addSpacing(20)

        # Global operations
        self.reset_all_btn = QPushButton("Reset All")
        self.reset_all_btn.clicked.connect(self.reset_all_requested)
        layout.addWidget(self.reset_all_btn)

        self.export_all_btn = QPushButton("Export All")
        self.export_all_btn.clicked.connect(self.export_all_requested)
        layout.addWidget(self.export_all_btn)

        layout.addStretch()

    def _on_layout_button_clicked(self, mode: LayoutMode):
        """Layout button clicked"""
        # Uncheck other buttons
        for m, btn in self.layout_buttons.items():
            btn.setChecked(m == mode)

        self.layout_changed.emit(mode)


class MultiPlotCanvas(QWidget):
    """
    Multi-plot layout canvas

    Core features:
    - Manage multiple subplots
    - Dynamic layout switching
    - Sync control
    - Data distribution
    """

    layout_changed = pyqtSignal(LayoutMode)
    subplot_selected = pyqtSignal(int, int)  # row, col

    def __init__(self):
        super().__init__()
        self.subplots = []
        self.current_layout = LayoutMode.SINGLE
        self.sync_manager = SyncManager()
        self.loaded_files = []  # Cache of loaded files

        self._init_ui()

    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Control bar
        self.control_bar = MultiPlotControlBar()
        self.control_bar.layout_changed.connect(self.set_layout_mode)
        self.control_bar.sync_zoom_changed.connect(self._on_sync_zoom_changed)
        self.control_bar.sync_cursor_changed.connect(self._on_sync_cursor_changed)
        self.control_bar.sync_pan_changed.connect(self._on_sync_pan_changed)
        self.control_bar.reset_all_requested.connect(self._on_reset_all)
        self.control_bar.export_all_requested.connect(self._on_export_all)
        layout.addWidget(self.control_bar)

        # Canvas container
        self.canvas_container = QWidget()
        self.canvas_layout = QGridLayout(self.canvas_container)
        self.canvas_layout.setSpacing(5)
        layout.addWidget(self.canvas_container)

        # Initialize with single plot
        self.set_layout_mode(LayoutMode.SINGLE)

    def set_layout_mode(self, mode: LayoutMode):
        """Switch layout mode"""
        if mode == self.current_layout:
            return

        self.current_layout = mode
        self._rebuild_layout()
        self.layout_changed.emit(mode)

    def _rebuild_layout(self):
        """Rebuild layout"""
        # Save current subplot states
        old_data = self._save_subplot_states()

        # Clear existing subplots
        self._clear_subplots()

        # Create new layout
        rows, cols = self._get_grid_size(self.current_layout)

        for row in range(rows):
            for col in range(cols):
                subplot = SubPlotWidget(row, col)

                # Connect signals
                subplot.zoom_changed.connect(self._on_subplot_zoom_changed)
                subplot.cursor_moved.connect(self._on_subplot_cursor_moved)
                subplot.selected.connect(lambda r=row, c=col:
                                       self.subplot_selected.emit(r, c))

                # Add to layout
                self.canvas_layout.addWidget(subplot, row, col)
                self.subplots.append(subplot)

                # Register to sync manager
                self.sync_manager.register_subplot(subplot)

        # Restore data (if possible)
        self._restore_subplot_states(old_data)

    def _get_grid_size(self, mode: LayoutMode) -> Tuple[int, int]:
        """Get grid size"""
        layout_grids = {
            LayoutMode.SINGLE: (1, 1),
            LayoutMode.HORIZONTAL_2: (1, 2),
            LayoutMode.VERTICAL_2: (2, 1),
            LayoutMode.GRID_2x2: (2, 2),
            LayoutMode.HORIZONTAL_3: (1, 3),
            LayoutMode.VERTICAL_3: (3, 1),
            LayoutMode.GRID_2x3: (2, 3),
        }
        return layout_grids.get(mode, (1, 1))

    def _clear_subplots(self):
        """Clear all subplots"""
        for subplot in self.subplots:
            self.canvas_layout.removeWidget(subplot)
            subplot.deleteLater()
        self.subplots.clear()
        self.sync_manager.clear()

    def _save_subplot_states(self) -> List[dict]:
        """Save subplot states"""
        states = []
        for subplot in self.subplots:
            state = {
                'file': subplot.current_file,
                'data_type': subplot.current_data_type,
                'xlim': subplot.ax.get_xlim() if subplot.ax else None,
                'ylim': subplot.ax.get_ylim() if subplot.ax else None,
            }
            states.append(state)
        return states

    def _restore_subplot_states(self, states: List[dict]):
        """Restore subplot states"""
        for i, subplot in enumerate(self.subplots):
            if i < len(states):
                state = states[i]
                if state['file'] and state['data_type']:
                    subplot.load_data(state['file'], state['data_type'])
                    if state['xlim']:
                        subplot.ax.set_xlim(state['xlim'])
                    if state['ylim']:
                        subplot.ax.set_ylim(state['ylim'])
                    subplot.canvas.draw()

    def load_files_to_subplots(self, files: List[str], data_type: str = 'reflectance'):
        """
        Batch load files to subplots

        Args:
            files: List of file paths
            data_type: Data type
        """
        from pyASDReader import ASDFile

        for i, filepath in enumerate(files):
            if i >= len(self.subplots):
                break

            try:
                asd_file = ASDFile(filepath)
                subplot = self.subplots[i]
                subplot.load_data(asd_file, data_type)
            except Exception as e:
                logger.error(f"Failed to load {filepath}: {e}")

    def _on_subplot_zoom_changed(self, row: int, col: int, xlim, ylim):
        """Subplot zoom changed"""
        if self.sync_manager.sync_zoom:
            self.sync_manager.sync_zoom_to_all(row, col, xlim, ylim)

    def _on_subplot_cursor_moved(self, row: int, col: int, x: float, y: float):
        """Subplot cursor moved"""
        if self.sync_manager.sync_cursor:
            self.sync_manager.sync_cursor_to_all(row, col, x, y)

    def _on_sync_zoom_changed(self, enabled: bool):
        """Sync zoom changed"""
        self.sync_manager.sync_zoom = enabled

    def _on_sync_cursor_changed(self, enabled: bool):
        """Sync cursor changed"""
        self.sync_manager.sync_cursor = enabled

    def _on_sync_pan_changed(self, enabled: bool):
        """Sync pan changed"""
        self.sync_manager.sync_pan = enabled

    def _on_reset_all(self):
        """Reset all subplots"""
        for subplot in self.subplots:
            if subplot.ax:
                subplot.ax.autoscale()
                subplot.canvas.draw()

    def _on_export_all(self):
        """Export all subplots"""
        # TODO: Implement export all functionality
        logger.info("Export all subplots")

    def export_all_subplots(self, filepath: str, dpi: int = 300):
        """
        Export all subplots to a single file

        Args:
            filepath: Path to save the file
            dpi: Resolution in dots per inch
        """
        if not self.subplots:
            return

        # Get grid size
        rows, cols = self._get_grid_size(self.current_layout)

        # Create a new figure with the same layout
        fig = Figure(figsize=(cols * 6, rows * 4), dpi=100)

        # Copy each subplot to the new figure
        for idx, subplot in enumerate(self.subplots):
            if subplot.current_file is None:
                continue

            # Calculate position in grid
            row = idx // cols
            col = idx % cols

            # Create subplot in new figure
            ax = fig.add_subplot(rows, cols, idx + 1)

            # Get data from original subplot
            wavelengths = subplot.current_file.wavelengths
            data = getattr(subplot.current_file, subplot.current_data_type, None)

            if data is not None and wavelengths is not None:
                # Plot data
                ax.plot(wavelengths, data, 'b-', linewidth=1.5)
                ax.set_xlabel('Wavelength (nm)', fontsize=10)
                ax.set_ylabel(subplot._get_ylabel(subplot.current_data_type), fontsize=10)
                ax.set_title(f"{os.path.basename(subplot.current_file.filepath)}\n{subplot.current_data_type}",
                           fontsize=10, fontweight='bold')
                ax.grid(True, alpha=0.3, linestyle='--')

        # Tight layout and save
        fig.tight_layout()
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
        plt.close(fig)

    def clear_all(self):
        """Clear all subplots"""
        for subplot in self.subplots:
            subplot.clear()
