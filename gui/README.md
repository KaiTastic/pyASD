# pyASDReader GUI

A graphical user interface for viewing and analyzing ASD spectral files.

## Features

- **File Management**
  - Open individual ASD files or browse folders
  - Recent files list for quick access
  - Drag-and-drop support (coming soon)

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

- **Metadata Display**
  - Comprehensive file information
  - Instrument details
  - GPS data (when available)
  - Spectral parameters
  - Available data types

- **Export Capabilities**
  - Export data to CSV (select specific data types)
  - Export metadata to text file
  - Export plots as PNG, SVG, or PDF

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

1. **Open a File**
   - Click "Open File..." button or use File menu (Ctrl+O)
   - Or open a folder to browse multiple files (Ctrl+Shift+O)

2. **View Data**
   - Select data type from dropdown menu
   - Plot updates automatically
   - Use matplotlib toolbar for zoom/pan

3. **View Metadata**
   - File information displayed in left panel
   - Expand/collapse sections as needed

4. **Export Data**
   - Use Export menu to save data or plots
   - Choose specific data types for CSV export
   - Export plots in various formats

### Keyboard Shortcuts

- `Ctrl+O` - Open file
- `Ctrl+Shift+O` - Open folder
- `Ctrl+W` - Close current file
- `Ctrl+Q` - Quit application
- `F5` - Refresh plot

## Project Structure

```
gui/
├── __init__.py              # GUI module initialization
├── main_window.py           # Main application window
├── widgets/                 # Custom widgets
│   ├── __init__.py
│   ├── plot_widget.py       # Spectral plot widget
│   ├── metadata_widget.py   # Metadata display widget
│   └── file_panel.py        # File management panel
└── utils/                   # Utility modules
    ├── __init__.py
    └── export_utils.py      # Export functionality

main.py                      # Application entry point
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

### Testing

```bash
# Test imports
python -c "from gui.widgets import PlotWidget, MetadataWidget, FilePanel"

# Syntax check
python -m py_compile gui/**/*.py
```

## License

Same as pyASDReader library (MIT License)

## Credits

Built on top of the pyASDReader library by Kai Cao.
