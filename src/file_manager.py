# STD
import os
import shutil
from pathlib import Path
# Installed
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.Qsci import *
# Custom
from editor.editor import Editor


class FileManager(QTreeView):
    def __init__(self, tab_view, set_new_tab=None,  main_window=None):
        super(FileManager, self).__init__(None)

        self.set_new_tab = set_new_tab
        self.tab_view = tab_view
        self.main_window = main_window

        ##########################################
        ################ Renaming ################

        self.manager_font = QFont("FiraCode", 13)

        self.model: QFileSystemModel = QFileSystemModel()
        self.model.setRootPath(os.getcwd())

        # Filesystem filters
        self.model.setFilter(
            QDir.Filter.NoDotAndDotDot | QDir.Filter.AllDirs |
            QDir.Filter.Files | QDir.Filter.Drives)
        self.model.setReadOnly(False)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.setFont(self.manager_font)
        self.setModel(self.model)
        self.setRootIndex(self.model.index(os.getcwd()))
        self.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QTreeView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)

        # Add Custom Context Menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # Handling Click
        self.clicked.connect(self.tree_view_clicked)
        self.setIndentation(10)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Hide other column except name
        self.setHeaderHidden(True)
        self.setColumnHidden(1, True)
        self.setColumnHidden(2, True)
        self.setColumnHidden(3, True)

        # Enable drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)

        # Enable file renaming
        self.prev_name = None
        self.is_renaming = False
        self.current_edit_index = None
        self.itemDelegate().closeEditor.connect(self.on_close_editor)

    def on_close_editor(self, editor: QLineEdit):
        if self.is_renaming:
            self.rename_file_with_index()

    def show_context_menu(self, pos):
        index = self.indexAt(pos)
        menu = QMenu()
        menu.addAction("New File").setShortcut("Ctrl+N")
        menu.addAction("New Folder").setShortcut("Ctrl+Shift+N")

        if index.column() == 0:
            menu.addSeparator()

            menu.addAction("Rename").setShortcut("Ctrl+R")
            menu.addAction("Delete").setShortcut("Ctrl+D")

        action = menu.exec(self.viewport().mapToGlobal(pos))
        if not action:
            return
        if action.text() == "New File":
            self.action_new_file(index)
        if action.text() == "New Folder":
            self.action_new_folder(index)
        if action.text() == "Rename":
            self.action_rename(index)
        if action.text() == "Delete":
            self.action_delete(index)
        else:
            pass

    def rename_file_with_index(self):
        new_name = self.model.fileName(self.current_edit_index)
        if self.prev_name == new_name:
            return

        # From all open tabs find the one with old name
        for editor in self.tab_view.findChildren(Editor):
            if editor.path.name == self.prev_name:
                editor.path = editor.path.parent / new_name
                self.tab_view.setTabText(
                    self.tab_view.indexOf(editor), new_name)
                self.tab_view.repaint()
                editor.full_path = editor.path.absolute()
                self.main_window.current_file = editor.path
                break

    def show_dialog(self, title, message) -> int:
        dialog = QMessageBox(self)
        dialog.setFont(self.manager_font)
        dialog.font().setPointSize(14)
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(QIcon("./src/resources/editor-icons/trash.svg"))
        dialog.setText(message)
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dialog.setDefaultButton(QMessageBox.StandardButton.No)
        dialog.setIcon(QMessageBox.Icon.Warning)
        return dialog.exec()

    def action_new_file(self, index):
        root_path = self.model.rootPath()
        if index.column() != -1:
            if self.model.isDir(index):
                self.expand(index)
                root_path = self.model.filePath(index)

        f = Path(root_path) / "file"
        count = 1
        while f.exists():
            f = Path(f.parent / f"file{count}")
            count += 1
        f.touch()
        _index = self.model.index(str(f.absolute()))
        self.edit(_index)

    def action_new_folder(self, index):
        root_path = self.model.rootPath()
        if index.column() != -1:
            if self.model.isDir(index):
                self.expand(index)
                root_path = self.model.filePath(index)

        f = Path(root_path) / "New Folder"
        count = 1
        while f.exists():
            f = Path(f.parent / f"New Folder{count}")
            count += 1
        f.mkdir()
        _index = self.model.index(str(f.absolute()))
        self.edit(_index)

    def action_rename(self, index):
        self.edit(index)
        self.prev_name = self.model.fileName(index)
        self.is_renaming = True
        self.current_edit_index = index

    def delete_file(self, path: Path):
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    def action_delete(self, index):
        file_name = self.model.fileName(index)
        dialog = self.show_dialog(
            "Delete", f"Are you sure you want to delete {file_name}"
        )
        if dialog == QMessageBox.StandardButton.Yes:
            if self.selectionModel().selectedRows():
                for i in self.selectionModel().selectedRows():
                    path = Path(self.model.filePath(i))
                    self.delete_file(path)
                    for editor in self.tab_view.findChildren(Editor):
                        if editor.path.name == path.name:
                            self.tab_view.removeTab(
                                self.tab_view.indexOf(editor))

    def tree_view_clicked(self, index: QModelIndex):
        path = self.model.filePath(index)
        p = Path(path)
        self.set_new_tab(p)

    # Drag & Drop functionality
    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QDropEvent) -> None:
        root_path = Path(self.model.rootPath())
        if e.mimeData().hasUrls():
            for url in e.mimeData().urls():
                path = Path(url.toLocalFile())
                if path.is_dir():
                    shutil.move(path, root_path / path.name)
                else:
                    shutil.move(path, root_path / path.name)
        e.accept()

        return super().dropEvent(e)
