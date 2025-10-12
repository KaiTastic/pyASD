"""
File browser panel with tree structure and checkboxes
"""

import os
import logging
from typing import List
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTreeWidget, QTreeWidgetItem,
                              QStyle, QMenu, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

logger = logging.getLogger(__name__)


class FileTreeControlBar(QWidget):
    """
    File tree control bar

    Provides quick actions: select all, clear all, refresh, expand, collapse
    """

    select_all_clicked = pyqtSignal()
    clear_all_clicked = pyqtSignal()
    refresh_clicked = pyqtSignal()
    expand_all_clicked = pyqtSignal()
    collapse_all_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Select all button
        self.select_all_btn = QPushButton("All")
        self.select_all_btn.setMaximumWidth(50)
        self.select_all_btn.setToolTip("Select all files in tree")
        self.select_all_btn.clicked.connect(self.select_all_clicked)
        layout.addWidget(self.select_all_btn)

        # Clear all button
        self.clear_all_btn = QPushButton("Clear")
        self.clear_all_btn.setMaximumWidth(50)
        self.clear_all_btn.setToolTip("Deselect all files")
        self.clear_all_btn.clicked.connect(self.clear_all_clicked)
        layout.addWidget(self.clear_all_btn)

        # Refresh button
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setMaximumWidth(30)
        self.refresh_btn.setToolTip("Refresh file tree")
        self.refresh_btn.clicked.connect(self.refresh_clicked)
        layout.addWidget(self.refresh_btn)

        # Expand/collapse buttons
        self.expand_btn = QPushButton("Expand")
        self.expand_btn.setMaximumWidth(60)
        self.expand_btn.setToolTip("Expand all folders")
        self.expand_btn.clicked.connect(self.expand_all_clicked)
        layout.addWidget(self.expand_btn)

        self.collapse_btn = QPushButton("Collapse")
        self.collapse_btn.setMaximumWidth(65)
        self.collapse_btn.setToolTip("Collapse all folders")
        self.collapse_btn.clicked.connect(self.collapse_all_clicked)
        layout.addWidget(self.collapse_btn)

        layout.addStretch()


class SelectedFilesInfoBar(QWidget):
    """
    Selected files info bar

    Displays number of selected files and batch operation buttons
    """

    compare_clicked = pyqtSignal()
    overlay_clicked = pyqtSignal()
    batch_export_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Info label
        self.info_label = QLabel("Selected: 0 files")
        self.info_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        layout.addWidget(self.info_label)

        # Button row
        button_layout = QHBoxLayout()

        # Compare button
        self.compare_btn = QPushButton("Compare")
        self.compare_btn.setToolTip("Compare selected files side by side")
        self.compare_btn.setEnabled(False)
        self.compare_btn.clicked.connect(self.compare_clicked)
        button_layout.addWidget(self.compare_btn)

        # Overlay button
        self.overlay_btn = QPushButton("Overlay")
        self.overlay_btn.setToolTip("Overlay selected spectra on one plot")
        self.overlay_btn.setEnabled(False)
        self.overlay_btn.clicked.connect(self.overlay_clicked)
        button_layout.addWidget(self.overlay_btn)

        # Batch export button
        self.export_btn = QPushButton("Export")
        self.export_btn.setToolTip("Batch export selected files")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.batch_export_clicked)
        button_layout.addWidget(self.export_btn)

        layout.addLayout(button_layout)

    def update_info(self, count: int):
        """
        Update selected files count display

        Args:
            count: Number of selected files
        """
        self.info_label.setText(f"Selected: {count} file{'s' if count != 1 else ''}")

        # Enable/disable buttons based on count
        has_files = count > 0
        has_multiple = count >= 2

        self.compare_btn.setEnabled(has_multiple)
        self.overlay_btn.setEnabled(has_multiple)
        self.export_btn.setEnabled(has_files)


class FileTreeWidget(QTreeWidget):
    """
    Tree widget with checkboxes for file selection

    Implements tri-state checkbox logic:
    - Checked: All children are checked
    - Unchecked: All children are unchecked
    - PartiallyChecked: Some children are checked
    """

    files_checked = pyqtSignal(list)           # List of checked files changed
    file_double_clicked = pyqtSignal(str)      # File double-clicked

    def __init__(self):
        super().__init__()
        self.current_root = None
        self._init_ui()
        self._setup_interactions()

    def _init_ui(self):
        """Initialize UI"""
        # Column settings
        self.setHeaderLabels(["Name", "Size", "Type"])
        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 80)
        self.setColumnWidth(2, 60)

        # Style
        self.setAlternatingRowColors(True)
        self.setAnimated(True)
        self.setIndentation(20)

        # Enable drag & drop
        self.setDragEnabled(False)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _setup_interactions(self):
        """Setup interactions"""
        # Double click event
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

        # Checkbox state changed
        self.itemChanged.connect(self._handle_check_state_changed)

    def load_directory(self, directory: str):
        """
        Load directory

        Args:
            directory: Directory path
        """
        self.clear()
        self.current_root = directory

        if not os.path.isdir(directory):
            return

        # Create root node
        root_item = QTreeWidgetItem(self)
        root_item.setText(0, os.path.basename(directory))
        root_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        root_item.setData(0, Qt.ItemDataRole.UserRole, directory)
        root_item.setData(0, Qt.ItemDataRole.UserRole + 1, "folder")
        root_item.setCheckState(0, Qt.CheckState.Unchecked)

        # Recursively load subdirectories and files
        self._load_directory_recursive(directory, root_item)

        # Expand root node
        root_item.setExpanded(True)

    def _load_directory_recursive(self, directory: str, parent_item: QTreeWidgetItem):
        """
        Recursively load directory

        Args:
            directory: Directory path
            parent_item: Parent tree item
        """
        try:
            # Get all files and folders
            entries = os.listdir(directory)

            # Separate folders and files
            folders = []
            files = []

            for entry in entries:
                full_path = os.path.join(directory, entry)
                if os.path.isdir(full_path):
                    folders.append(entry)
                elif entry.endswith('.asd'):
                    files.append(entry)

            # Add folders first
            for folder in sorted(folders):
                folder_path = os.path.join(directory, folder)
                folder_item = QTreeWidgetItem(parent_item)
                folder_item.setText(0, folder)
                folder_item.setIcon(0, self.style().standardIcon(
                    QStyle.StandardPixmap.SP_DirIcon))
                folder_item.setData(0, Qt.ItemDataRole.UserRole, folder_path)
                folder_item.setData(0, Qt.ItemDataRole.UserRole + 1, "folder")
                folder_item.setCheckState(0, Qt.CheckState.Unchecked)

                # Recursively load subdirectory
                self._load_directory_recursive(folder_path, folder_item)

                # Update folder display (show file count)
                file_count = self._count_asd_files(folder_path)
                if file_count > 0:
                    folder_item.setText(0, f"{folder} ({file_count})")

            # Add files
            for filename in sorted(files):
                filepath = os.path.join(directory, filename)
                file_item = QTreeWidgetItem(parent_item)
                file_item.setText(0, filename)
                file_item.setIcon(0, self.style().standardIcon(
                    QStyle.StandardPixmap.SP_FileIcon))

                # File size
                try:
                    size = os.path.getsize(filepath)
                    size_str = self._format_size(size)
                    file_item.setText(1, size_str)
                except:
                    file_item.setText(1, "--")

                file_item.setText(2, "ASD")
                file_item.setData(0, Qt.ItemDataRole.UserRole, filepath)
                file_item.setData(0, Qt.ItemDataRole.UserRole + 1, "file")
                file_item.setCheckState(0, Qt.CheckState.Unchecked)

        except Exception as e:
            logger.warning(f"Failed to load directory {directory}: {e}")

    def _count_asd_files(self, directory: str) -> int:
        """Recursively count .asd files in directory"""
        count = 0
        try:
            for entry in os.listdir(directory):
                full_path = os.path.join(directory, entry)
                if os.path.isdir(full_path):
                    count += self._count_asd_files(full_path)
                elif entry.endswith('.asd'):
                    count += 1
        except:
            pass
        return count

    def _format_size(self, size: int) -> str:
        """Format file size"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/1024/1024:.1f} MB"

    def _handle_check_state_changed(self, item: QTreeWidgetItem, column: int):
        """
        Handle checkbox state change

        Implements tri-state logic:
        1. Child node changes -> update parent
        2. Parent node changes -> update all children
        """
        if column != 0:
            return

        # Temporarily disconnect signal to avoid recursion
        self.itemChanged.disconnect(self._handle_check_state_changed)

        try:
            item_type = item.data(0, Qt.ItemDataRole.UserRole + 1)
            new_state = item.checkState(0)

            if item_type == "folder":
                # Folder node changed -> update all children
                self._set_children_check_state(item, new_state)

            # Update parent node state
            self._update_parent_check_state(item)

            # Emit signal
            checked_files = self.get_checked_files()
            self.files_checked.emit(checked_files)

        finally:
            # Reconnect signal
            self.itemChanged.connect(self._handle_check_state_changed)

    def _set_children_check_state(self, parent: QTreeWidgetItem, state: Qt.CheckState):
        """
        Recursively set check state for all children

        Args:
            parent: Parent item
            state: Target state
        """
        for i in range(parent.childCount()):
            child = parent.child(i)
            child.setCheckState(0, state)

            # If child is a folder, recurse
            if child.data(0, Qt.ItemDataRole.UserRole + 1) == "folder":
                self._set_children_check_state(child, state)

    def _update_parent_check_state(self, item: QTreeWidgetItem):
        """
        Update parent node check state upwards

        Tri-state logic:
        - All children checked -> Checked
        - All children unchecked -> Unchecked
        - Some children checked -> PartiallyChecked

        Args:
            item: Child item
        """
        parent = item.parent()
        if not parent:
            return

        # Count children states
        checked_count = 0
        unchecked_count = 0
        partial_count = 0
        total_count = parent.childCount()

        for i in range(total_count):
            child = parent.child(i)
            state = child.checkState(0)
            if state == Qt.CheckState.Checked:
                checked_count += 1
            elif state == Qt.CheckState.Unchecked:
                unchecked_count += 1
            elif state == Qt.CheckState.PartiallyChecked:
                partial_count += 1

        # Set parent state based on children
        if checked_count == total_count:
            parent.setCheckState(0, Qt.CheckState.Checked)
        elif unchecked_count == total_count:
            parent.setCheckState(0, Qt.CheckState.Unchecked)
        else:
            parent.setCheckState(0, Qt.CheckState.PartiallyChecked)

        # Recursively update parent's parent
        self._update_parent_check_state(parent)

    def get_checked_files(self) -> List[str]:
        """
        Get all checked file paths

        Returns:
            List of checked file paths
        """
        files = []

        def collect_checked_files(item: QTreeWidgetItem):
            """Recursively collect checked files"""
            item_type = item.data(0, Qt.ItemDataRole.UserRole + 1)

            if item_type == "file" and item.checkState(0) == Qt.CheckState.Checked:
                filepath = item.data(0, Qt.ItemDataRole.UserRole)
                files.append(filepath)

            # Recurse through children
            for i in range(item.childCount()):
                collect_checked_files(item.child(i))

        # Start from root
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            collect_checked_files(root.child(i))

        return files

    def set_all_checked(self, checked: bool):
        """
        Set check state for all files

        Args:
            checked: True=check, False=uncheck
        """
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked

        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            item.setCheckState(0, state)

    def refresh(self):
        """Refresh current directory"""
        if self.current_root:
            self.load_directory(self.current_root)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Double click event"""
        item_type = item.data(0, Qt.ItemDataRole.UserRole + 1)
        if item_type == "file":
            filepath = item.data(0, Qt.ItemDataRole.UserRole)
            self.file_double_clicked.emit(filepath)

    def _show_context_menu(self, position):
        """Show context menu"""
        item = self.itemAt(position)
        if not item:
            return

        menu = QMenu()
        item_type = item.data(0, Qt.ItemDataRole.UserRole + 1)

        if item_type == "file":
            # File context menu
            open_action = menu.addAction("Open")
            open_action.triggered.connect(lambda: self._open_file(item))

            menu.addSeparator()

            load_action = menu.addAction("Load to Plot")
            compare_action = menu.addAction("Compare with...")

            menu.addSeparator()

            export_action = menu.addAction("Export...")
            properties_action = menu.addAction("Properties")

            menu.addSeparator()

            show_folder_action = menu.addAction("Show in Folder")
            show_folder_action.triggered.connect(lambda: self._show_in_folder(item))

        else:
            # Folder context menu
            select_all_action = menu.addAction("Select All Files")
            select_all_action.triggered.connect(lambda: self._select_all_in_folder(item))

            deselect_all_action = menu.addAction("Deselect All Files")
            deselect_all_action.triggered.connect(lambda: self._deselect_all_in_folder(item))

            menu.addSeparator()

            expand_action = menu.addAction("Expand All")
            expand_action.triggered.connect(lambda: item.setExpanded(True))

            collapse_action = menu.addAction("Collapse All")
            collapse_action.triggered.connect(lambda: item.setExpanded(False))

            menu.addSeparator()

            batch_export_action = menu.addAction("Batch Export...")

        menu.exec(self.viewport().mapToGlobal(position))

    def _open_file(self, item: QTreeWidgetItem):
        """Open file"""
        filepath = item.data(0, Qt.ItemDataRole.UserRole)
        self.file_double_clicked.emit(filepath)

    def _show_in_folder(self, item: QTreeWidgetItem):
        """Show in system file manager"""
        filepath = item.data(0, Qt.ItemDataRole.UserRole)
        import subprocess
        import platform

        if platform.system() == "Windows":
            subprocess.run(['explorer', '/select,', filepath])
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(['open', '-R', filepath])
        else:  # Linux
            subprocess.run(['xdg-open', os.path.dirname(filepath)])

    def _select_all_in_folder(self, item: QTreeWidgetItem):
        """Select all files in folder"""
        item.setCheckState(0, Qt.CheckState.Checked)

    def _deselect_all_in_folder(self, item: QTreeWidgetItem):
        """Deselect all files in folder"""
        item.setCheckState(0, Qt.CheckState.Unchecked)

    # Drag & drop support
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Drop event"""
        urls = event.mimeData().urls()

        for url in urls:
            path = url.toLocalFile()
            if os.path.isdir(path):
                # If folder, load the folder
                self.load_directory(path)
                break
            elif path.endswith('.asd'):
                # If single file, emit signal
                self.file_double_clicked.emit(path)


class FilePanel(QWidget):
    """
    Tree-based file browser panel (with checkboxes)

    Features:
    - Tree folder structure
    - Tri-state checkbox selection
    - Batch operations
    - Drag & drop support
    """

    # Signals
    file_checked = pyqtSignal(str, bool)  # File check state changed
    files_checked = pyqtSignal(list)       # Checked files list changed
    file_selected = pyqtSignal(str)        # File double-clicked (for compatibility)
    folder_changed = pyqtSignal(str)       # Folder changed

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title = QLabel("<b>📁 File Browser</b>")
        layout.addWidget(title)

        # Control bar
        self.control_bar = FileTreeControlBar()
        self.control_bar.select_all_clicked.connect(self._select_all)
        self.control_bar.clear_all_clicked.connect(self._clear_all)
        self.control_bar.refresh_clicked.connect(self._refresh_tree)
        self.control_bar.expand_all_clicked.connect(self._expand_all)
        self.control_bar.collapse_all_clicked.connect(self._collapse_all)
        layout.addWidget(self.control_bar)

        # Tree widget
        self.tree_widget = FileTreeWidget()
        self.tree_widget.files_checked.connect(self._on_files_checked)
        self.tree_widget.file_double_clicked.connect(self._on_file_double_clicked)
        layout.addWidget(self.tree_widget)

        # Selected files info bar
        self.info_bar = SelectedFilesInfoBar()
        self.info_bar.compare_clicked.connect(self._on_compare_clicked)
        self.info_bar.overlay_clicked.connect(self._on_overlay_clicked)
        self.info_bar.batch_export_clicked.connect(self._on_batch_export_clicked)
        layout.addWidget(self.info_bar)

    def load_directory(self, directory: str):
        """Load directory"""
        self.tree_widget.load_directory(directory)
        self.folder_changed.emit(directory)

    def open_file_dialog(self):
        """Open file dialog"""
        from PyQt6.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open ASD File",
            "",
            "ASD Files (*.asd);;All Files (*.*)"
        )
        if filepath:
            self.file_selected.emit(filepath)

    def open_folder_dialog(self):
        """Open folder dialog"""
        from PyQt6.QtWidgets import QFileDialog
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if directory:
            self.load_directory(directory)

    def get_checked_files(self) -> List[str]:
        """Get all checked files"""
        return self.tree_widget.get_checked_files()

    def _select_all(self):
        """Select all"""
        self.tree_widget.set_all_checked(True)

    def _clear_all(self):
        """Clear selection"""
        self.tree_widget.set_all_checked(False)

    def _refresh_tree(self):
        """Refresh tree"""
        self.tree_widget.refresh()

    def _expand_all(self):
        """Expand all"""
        self.tree_widget.expandAll()

    def _collapse_all(self):
        """Collapse all"""
        self.tree_widget.collapseAll()

    def _on_files_checked(self, files: List[str]):
        """Checked files changed"""
        self.info_bar.update_info(len(files))
        self.files_checked.emit(files)

    def _on_file_double_clicked(self, filepath: str):
        """File double-clicked"""
        self.file_selected.emit(filepath)

    def _on_compare_clicked(self):
        """
        Compare button clicked

        Loads checked files in side-by-side layout for comparison
        """
        files = self.get_checked_files()
        if len(files) < 2:
            QMessageBox.warning(self, "Warning",
                              "Please select at least 2 files to compare")
            return

        # Emit signal to load files for comparison
        # The main window will handle the actual comparison display
        self.files_checked.emit(files)
        logger.info(f"Compare {len(files)} files in side-by-side layout")

    def _on_overlay_clicked(self):
        """
        Overlay button clicked

        Opens overlay plot dialog showing all checked files on one plot
        """
        files = self.get_checked_files()
        if len(files) < 2:
            QMessageBox.warning(self, "Warning",
                              "Please select at least 2 files to overlay")
            return

        try:
            # Load all ASD files
            from pyASDReader import ASDFile
            from gui.widgets.overlay_plot_widget import OverlayPlotDialog

            asd_files = []
            failed_files = []

            for filepath in files:
                try:
                    asd_file = ASDFile(filepath)
                    asd_files.append(asd_file)
                except Exception as e:
                    failed_files.append(os.path.basename(filepath))
                    logger.error(f"Failed to load {filepath}: {e}")

            if not asd_files:
                QMessageBox.critical(self, "Error",
                                   "Failed to load any of the selected files")
                return

            if failed_files:
                QMessageBox.warning(self, "Partial Load",
                                  f"Failed to load {len(failed_files)} file(s):\n" +
                                  "\n".join(failed_files[:5]) +
                                  ("\n..." if len(failed_files) > 5 else ""))

            # Open overlay dialog
            dialog = OverlayPlotDialog(asd_files, self)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error",
                               f"Failed to create overlay plot:\n{str(e)}")
            logger.error(f"Overlay plot error: {e}")

    def _on_batch_export_clicked(self):
        """
        Batch export button clicked

        Opens batch export dialog for exporting multiple files
        """
        files = self.get_checked_files()
        if not files:
            QMessageBox.warning(self, "Warning",
                              "Please select files to export")
            return

        try:
            from gui.widgets.batch_export_dialog import BatchExportDialog

            dialog = BatchExportDialog(files, self)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error",
                               f"Failed to open batch export dialog:\n{str(e)}")
            logger.error(f"Batch export dialog error: {e}")
