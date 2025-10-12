#!/usr/bin/env python3
"""
Main entry point for pyASDReader GUI application

Usage:
    python main.py [file.asd]

Arguments:
    file.asd: Optional ASD file to open on startup
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Main function to launch the GUI application"""
    app = QApplication(sys.argv)
    app.setApplicationName("pyASDReader")
    app.setOrganizationName("pyASDReader")

    window = MainWindow()
    window.show()

    # If a file path is provided as argument, load it
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        window.load_asd_file(filepath)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
