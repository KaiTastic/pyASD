# pyASDReader GUI

A graphical user interface for viewing and analyzing ASD spectral files.

## Features

- **File Management**
  - Tree-based file browser with checkboxes for multi-file selection
  - Open individual ASD files or browse folders
  - Recent files list for quick access
  - Tri-state checkbox selection for folders and files
  - Expand/collapse folder tree
  - Drag-and-drop support

- **Multi-Plot Canvas (NEW)**
  - 7 layout modes: 1×1, 1×2, 2×1, 2×2, 1×3, 3×1, 2×3
  - Compare files side-by-side automatically
  - Independent data type selection per subplot
  - Synchronized zoom and cursor across plots
  - Export all subplots as a single image

- **Data Visualization**
  - Interactive spectral plots using matplotlib
  - Multiple data types:
    - Digital Number (DN)
    - Reflectance (with 1st, 2nd, and 3rd derivatives)
    - White Reference
    - Absolute Reflectance
    - Log(1/R) (with derivatives)
    - Radiance (when available)
  - Zoom, pan, and other matplotlib tools
  - Customizable grid and legend

- **Spectrum Comparison (NEW)**
  - **Compare Mode**: View multiple files side-by-side
  - **Overlay Mode**: Plot multiple spectra on one graph with:
    - Different colors for each spectrum
    - Mean and standard deviation overlay
    - Statistics display
    - Easy export functionality

- **Metadata Display**
  - 7 comprehensive tabs:
    - File Information (name, path, size, timestamps)
    - Metadata (GPS, acquisition parameters)
    - Data Types (availability and quick load)
    - Calibration (v7+ calibration data)
    - History (v8+ audit log)
    - System (instrument and spectral configuration)
    - **Statistics (NEW)**: Real-time spectrum statistics
      - Global statistics (min, max, mean, std, median, range)
      - Per-band statistics (VNIR, SWIR1, SWIR2)
      - Signal quality metrics (SNR, saturation)

- **Export Capabilities**
  - Export data to CSV (select specific data types)
  - Export metadata to text file
  - Export plots as PNG, SVG, or PDF
  - Export multi-plot layouts as single image
  - **Batch Export (NEW)**: Export multiple files at once
    - CSV or TXT format
    - Configurable data type selection
    - Progress tracking
    - Error reporting

## Installation

### Install GUI dependencies

```bash
# Install with GUI dependencies
pip install -e ".[gui]"

# Or install all dependencies
pip install -e ".[all]"
```

### Dependencies

- PyQt6 >= 6.4.0
- matplotlib >= 3.5.0
- numpy >= 1.20.0 (already required by base package)

## Usage

### Launch the GUI

```bash
# From the project root directory
python main.py

# Or with a file to open
python main.py path/to/file.asd
```

### Using the Interface

1. **Browse and Select Files**
   - Click "Open Folder..." (Ctrl+Shift+O) to load a directory tree
   - Check boxes next to files to select them
   - Use "All", "Clear", "Expand", "Collapse" buttons for quick navigation

2. **Compare Multiple Files**
   - **Side-by-Side**: Check 2-6 files, they load automatically in multi-plot layout
   - **Overlay**: Check 2+ files and click "Overlay" button to see all on one plot
   - **Statistics**: Enable "Show Statistics" in overlay mode for mean/std dev

3. **Single File Viewing**
   - Double-click a file to view it in detail
   - Select data type from dropdown menu
   - View statistics in the Properties panel (Statistics tab)

4. **Export Options**
   - **Single Export**: Use Export menu to save current data or plots
   - **Batch Export**: Check multiple files and click "Export" button
     - Choose CSV (spectral data) or TXT (metadata)
     - Select which data types to export
     - Track progress with progress bar

5. **Multi-Plot Controls**
   - Use layout buttons to switch between different grid arrangements
   - Enable/disable sync for zoom, cursor, or pan
   - Export all plots as single image via Export → Export Plot

### Keyboard Shortcuts

- `Ctrl+O` - Open file
- `Ctrl+Shift+O` - Open folder
- `Ctrl+W` - Close current file
- `Ctrl+Q` - Quit application
- `F5` - Refresh plot

### New Workflow Examples

**Example 1: Comparing Field Measurements**
1. Open folder with multiple `.asd` files
2. Check 4 files you want to compare
3. They automatically load in 2×2 grid
4. Enable "Sync Zoom" to zoom all plots together
5. Export as single PNG via Export → Export Plot as PNG

**Example 2: Analyzing Spectrum Statistics**
1. Double-click a file to load it
2. Click "Statistics" tab in Properties panel
3. View global and per-band statistics
4. Check SNR and saturation levels
5. Switch data types to compare statistics

**Example 3: Batch Processing**
1. Open folder with 50+ files
2. Check all files (use "All" button)
3. Click "Export" button in file panel
4. Select CSV format and desired data types
5. Choose output directory
6. Click "Start Export" and monitor progress

## Project Structure

```
gui/
├── __init__.py                    # GUI module initialization
├── main_window.py                 # Main application window (3-column layout)
├── widgets/                       # Custom widgets
│   ├── __init__.py
│   ├── plot_widget.py             # Single spectral plot widget
│   ├── metadata_widget.py         # Metadata display widget
│   ├── file_panel.py              # File browser with tree and checkboxes
│   ├── multi_plot_canvas.py       # Multi-plot layout canvas (NEW)
│   ├── properties_panel.py        # Properties panel with 7 tabs (NEW)
│   ├── overlay_plot_widget.py     # Overlay plot dialog (NEW)
│   ├── batch_export_dialog.py     # Batch export dialog (NEW)
│   └── statistics_widget.py       # Statistics display widget (NEW)
└── utils/                         # Utility modules
    ├── __init__.py
    └── export_utils.py            # Export functionality

main.py                            # Application entry point
```

## Supported File Versions

The GUI supports all ASD file versions (v1-v8) supported by the pyASDReader library.

## Troubleshooting

### GUI won't start

- Ensure PyQt6 is installed: `pip install PyQt6`
- Check for Python version >= 3.8

### Plots not displaying

- Ensure matplotlib is installed: `pip install matplotlib`
- Try refreshing the plot (F5)

### Data type shows "Not Available"

- Some data types require specific file versions
- Check the metadata to see file version
- Reflectance requires reference data (v2+)
- Absolute reflectance requires calibration data (v7+)

## Development

### Adding New Features

The GUI is designed to be modular and extensible:

- **New plot types**: Add to `PlotWidget.PLOT_TYPES` dictionary
- **New export formats**: Extend `ExportManager` class
- **New widgets**: Create in `gui/widgets/` directory
- **New properties tabs**: Add to `PropertiesPanel` class
- **New comparison modes**: Extend `OverlayPlotDialog` or create new dialog

### Recent Improvements (Phase 4)

**Priority 1: Internationalization**
- ✅ Replaced Chinese button text with English
- All UI elements now in English

**Priority 2: Complete Features**
- ✅ Multi-plot export (export all subplots as single image)
- ✅ Compare mode (side-by-side viewing)
- ✅ Overlay mode (multiple spectra on one plot with statistics)
- ✅ Batch export dialog (CSV/TXT with progress tracking)

**Priority 3: Enhanced Features**
- ✅ Statistics panel (global, per-band, and quality metrics)
- ⏳ Plot customization (colors, styles) - Partially implemented in overlay mode

### Testing

```bash
# Test imports
python -c "from gui.widgets import PlotWidget, MetadataWidget, FilePanel, OverlayPlotDialog, BatchExportDialog"

# Syntax check
python -m py_compile gui/**/*.py

# Test multi-plot functionality
python test_multiplot.py

# Test GUI with sample data
python main.py tests/sample_data/v8sample/
```

## License

Same as pyASDReader library (MIT License)

## Credits

Built on top of the pyASDReader library by Kai Cao.
