# STD
import os
import sys
from pathlib import Path
# Installed
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.Qsci import *
# Custom
from editor.editor import Editor
from fuzzy_finder import SearchItem, SearchWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.set_sidebar_color = "#282c34"

        self.init_ui()

        self.current_file = None
        self.current_open_sidebar = None

    def init_ui(self):
        # Window
        # self.setWindowIcon(QIcon("./src/icons/logo.png"))
        self.setWindowTitle("Dragon")
        self.resize(900, 700)

        # Style
        self.setStyleSheet(open("./src/static/css/style.qss", "r").read())
        self.window_font = QFont("FiraCode")
        self.window_font.setPointSize(12)
        self.setFont(self.window_font)

        self.set_up_menu()
        self.set_up_body()

        self.show()

    def set_up_menu(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")

        new_file = file_menu.addAction("New")
        new_file.setShortcut("Ctrl+N")
        new_file.triggered.connect(self.new_file)

        open_file = file_menu.addAction("Open File")
        open_file.setShortcut("Ctrl+O")
        open_file.triggered.connect(self.open_file)

        open_folder = file_menu.addAction("Open Folder")
        open_folder.setShortcut("Ctrl+F")
        open_folder.triggered.connect(self.open_folder)

        file_menu.addSeparator()

        save_file = file_menu.addAction("Save")
        save_file.setShortcut("Ctrl+S")
        save_file.triggered.connect(self.save_file)

        save_as = file_menu.addAction("Save As")
        save_as.setShortcut("Ctrl+Shift+S")
        save_as.triggered.connect(self.save_as)

        # Edit Menu
        edit_menu = menu_bar.addMenu("Edit")

        cut_action = edit_menu.addAction("Cut")
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut)

        copy_action = edit_menu.addAction("Copy")
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)

        paste_action = edit_menu.addAction("Paste")
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste)

        find_action = edit_menu.addAction("Find")
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.find)

    def get_editor(self, path: Path = None, is_python_file=True) -> QsciScintilla:
        editor = Editor(path=path, is_python_file=is_python_file)
        return editor

    def is_binary(self, path):
        '''
            check if file is binary
        '''
        with open(path, 'rb') as f:
            return b'\0' in f.read(1024)

    def set_new_tab(self, path: Path, is_new_file=False):
        editor = self.get_editor(path, path.suffix in {".py", ".pyw"})

        if is_new_file:
            self.tab_view.addTab(editor, "untitled")
            # self.setWindowTitle("untitled")
            self.statusBar().showMessage("Opened untitled")
            self.tab_view.setCurrentIndex(self.tab_view.count() - 1)
            self.current_file = None
            return

        if not path.is_file():
            return
        if self.is_binary(path):
            self.statusBar().showMessage("Cannot Open Binary File", 2000)
            return

        # Check if the file is already open
        for i in range(self.tab_view.count()):
            if self.tab_view.tabText(i) == path.name:
                self.tab_view.setCurrentIndex(i)
                self.current_file = path
                return

        # Create a new tab
        self.tab_view.addTab(editor, path.name)
        editor.setText(path.read_text())
        # self.setWindowTitle(path.name)
        self.current_file = path
        self.tab_view.setCurrentIndex(self.tab_view.count() - 1)
        self.statusBar().showMessage(f"Opened {path.name}", 2000)

    def set_cursor_pointer(self, e):
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_cursor_arrow(self, e):
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def get_side_bar_label(self, path, name):
        label = QLabel()
        label.setPixmap(QPixmap(path).scaled(QSize(30, 30)))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(self.window_font)
        label.mousePressEvent = lambda e: self.toggle_tab(e, name)
        # Change cursor on hover
        label.enterEvent = self.set_cursor_pointer
        label.leaveEvent = self.set_cursor_arrow
        return label

    def get_frame(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.NoFrame)
        frame.setFrameShadow(QFrame.Shadow.Plain)
        frame.setContentsMargins(0, 0, 0, 0)
        frame.setStyleSheet('''
            QFrame{
                background-color: #21252b;
                border-radius: 5px;
                border: none;
                padding: 5px;
                color: #D3D3D3;
            }
            QFrame:hover{
                color: white;
            }
        ''')
        return frame

    def set_up_body(self):
        # Body
        body_frame = QFrame()
        body_frame.setFrameShape(QFrame.Shape.StyledPanel)
        body_frame.setFrameShadow(QFrame.Shadow.Plain)
        body_frame.setLineWidth(0)
        body_frame.setMidLineWidth(0)
        body_frame.setContentsMargins(0, 0, 0, 0)
        body_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        body_frame.setLayout(body)

        ##########################################
        ############## Sidebar View ##############
        self.side_bar = QFrame()
        self.side_bar.setFrameShape(QFrame.Shape.StyledPanel)
        self.side_bar.setFrameShadow(QFrame.Shadow.Plain)
        self.side_bar.setStyleSheet(f'''
            background-color: {self.set_sidebar_color};
        ''')
        side_bar_layout = QVBoxLayout()
        side_bar_layout.setContentsMargins(5, 10, 5, 0)
        side_bar_layout.setSpacing(0)
        side_bar_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        self.side_bar.setLayout(side_bar_layout)

        # SetUp Labels (sidebar icons)
        folder_label = self.get_side_bar_label(
            "./src/static/icons/folder-icon-blue.svg", "file-manager")
        side_bar_layout.addWidget(folder_label)

        search_label = self.get_side_bar_label(
            "./src/static/icons/search-icon.svg", "search-manager")
        side_bar_layout.addWidget(search_label)

        self.side_bar.setLayout(side_bar_layout)

        # Split View
        self.h_split = QSplitter(Qt.Orientation.Horizontal)

        ###############################################
        ############## File Manager View ##############
        # frame and layout to hold tree view (File Manager)
        self.file_manager_frame = self.get_frame()
        self.file_manager_frame.setMaximumWidth(400)
        self.file_manager_frame.setMinimumWidth(150)

        tree_frame_layout = QVBoxLayout()
        tree_frame_layout.setContentsMargins(0, 0, 0, 0)
        tree_frame_layout.setSpacing(0)

        # Create file system model to show in tree
        self.model = QFileSystemModel()
        self.model.setRootPath(os.getcwd())

        # File system filters
        self.model.setFilter(
            QDir.Filter.NoDotAndDotDot | QDir.Filter.AllDirs | QDir.Filter.Files)

        ############################################
        ############## File Tree View ##############
        self.tree_view = QTreeView()
        self.tree_view.setFont(QFont("FiraCode", 13))
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(os.getcwd()))
        self.tree_view.setSelectionMode(
            QTreeView.SelectionMode.SingleSelection)
        self.tree_view.setSelectionBehavior(
            QTreeView.SelectionBehavior.SelectRows)
        self.tree_view.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)

        # Add Custom Context Menu
        self.tree_view.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(
            self.tree_view_context_menu)

        # Handling Click
        self.tree_view.clicked.connect(self.tree_view_clicked)
        self.tree_view.setIndentation(10)
        self.tree_view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Hide other column except name
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)

        #########################################
        ############## Search View ##############
        self.search_frame = self.get_frame()
        self.search_frame.setMaximumWidth(400)
        self.search_frame.setMinimumWidth(150)

        search_layout = QVBoxLayout()
        search_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        search_layout.setContentsMargins(0, 10, 0, 0)
        search_layout.setSpacing(0)

        search_input = QLineEdit()
        search_input.setPlaceholderText("Search...")
        search_input.setFont(self.window_font)
        search_input.setAlignment(Qt.AlignmentFlag.AlignTop)
        search_input.setStyleSheet("""
        QLineEdit{
            background-color: #21252b;
            border-radius: 5px;
            border: 1px solid #d3d3d3;
            padding: 5px;
            color: #D3D3D3;
        }
        QLineEdit:hover{
            color: white;
        }
        """)

        ############## CheckBox##############
        self.search_checkbox = QCheckBox("Search in modules")
        self.search_checkbox.setFont(self.window_font)
        self.search_checkbox.setStyleSheet(
            """color: white; margin-bottom: 10px""")

        self.search_worker = SearchWorker()
        self.search_worker.finished.connect(self.search_finished)
        search_input.textChanged.connect(
            lambda text: self.search_worker.update(
                text,
                self.model.rootDirectory().absolutePath(),
                self.search_checkbox.isChecked()
            )
        )

        ################################################
        ############## Search Result View ##############
        self.search_list_view = QListWidget()
        self.search_list_view.setFont(QFont("FiraCode", 13))
        self.search_list_view.setStyleSheet("""
        QListWidget{
            background-color: #21252b;
            border-radius: 5px;
            border: 1px solid #d3d3d3;
            padding: 5px;
            color: #d3d3d3;
        }
        """)
        self.search_list_view.itemClicked.connect(
            self.search_list_view_clicked)

        search_layout.addWidget(self.search_checkbox)
        search_layout.addWidget(search_input)
        search_layout.addSpacerItem(QSpacerItem(
            5, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))
        search_layout.addWidget(self.search_list_view)
        self.search_frame.setLayout(search_layout)

        # Setup Layout
        tree_frame_layout.addWidget(self.tree_view)
        self.file_manager_frame.setLayout(tree_frame_layout)

        ######################################
        ############## Tab View ##############
        # Tab Widget to add editor to
        self.tab_view = QTabWidget()
        self.tab_view.setContentsMargins(0, 0, 0, 0)
        self.tab_view.setTabsClosable(True)
        self.tab_view.setMovable(True)
        self.tab_view.setDocumentMode(True)
        self.tab_view.tabCloseRequested.connect(self.close_tab)

        # Add Tree View and Tab View
        self.h_split.addWidget(self.file_manager_frame)
        self.h_split.addWidget(self.tab_view)

        body.addWidget(self.side_bar)
        body.addWidget(self.h_split)
        body_frame.setLayout(body)

        self.setCentralWidget(body_frame)

    def search_finished(self, items):
        self.search_list_view.clear()
        for i in items:
            self.search_list_view.addItem(i)

    def search_list_view_clicked(self, item: SearchItem):
        self.set_new_tab(Path(item.full_path))
        editor: Editor = self.tab_view.currentWidget()
        editor.setCursorPosition(item.line_no, item.end)
        editor.setFocus()

    def close_tab(self, index):
        self.tab_view.removeTab(index)

    def toggle_tab(self, e, type_):
        if type_ == "file-manager":
            if not (self.file_manager_frame in self.h_split.children()):
                self.h_split.replaceWidget(0, self.file_manager_frame)
        elif type_ == "search-manager":
            if not (self.search_frame in self.h_split.children()):
                self.h_split.replaceWidget(0, self.search_frame)
        if self.current_open_sidebar == type_:
            frame = self.h_split.children()[0]
            if frame.isHidden():
                frame.show()
            else:
                frame.hide()
        self.current_open_sidebar = type_

    def tree_view_context_menu(self, pos):
        ...

    def tree_view_clicked(self, index: QModelIndex):
        path = self.model.filePath(index)
        p = Path(path)
        self.set_new_tab(p)

    def new_file(self):
        self.set_new_tab(None, is_new_file=True)

    def open_file(self):
        ops = QFileDialog.Option.DontUseNativeDialog
        new_file, _ = QFileDialog.getOpenFileName(
            self, "Pick a File", "", "All Files (*);;Python Files (*.py);", options=ops)

        if new_file == "":
            self.statusBar().showMessage("Cancelled", 2000)
            return
        f = Path(new_file)
        self.set_new_tab(f)

    def open_folder(self):
        ops = QFileDialog.Option.DontUseNativeDialog
        new_folder = QFileDialog.getExistingDirectory(
            self, "Pick a Folder", "", options=ops)
        if new_folder:
            self.model.setRootPath(new_folder)
            self.tree_view.setRootIndex(self.model.index(new_folder))
            self.statusBar().showMessage(
                f"Opened {new_folder}", 2000)

    def save_file(self):
        if self.current_file is None and self.tab_view.count() > 0:
            self.save_as()

        editor = self.tab_view.currentWidget()
        self.current_file.write_text(editor.text())
        self.statusBar().showMessage(f"Saved {self.current_file.name}", 2000)

    def save_as(self):
        editor = self.tab_view.currentWidget()
        if editor is None:
            return

        file_path = QFileDialog.getSaveFileName(
            self, "Save As", os.getcwd())[0]
        if file_path == "":
            self.statusBar().showMessage("Cancelled", 2000)
            return
        path = Path(file_path)
        path.write_text(editor.text())
        self.tab_view.setTabText(self.tab_view.currentIndex(), path.name)
        self.statusBar().showMessage(f"Saved {path.name}", 2000)
        self.current_file = path

    def cut(self):
        editor = self.tab_view.currentWidget()
        if editor is not None:
            editor.cut()

    def copy(self):
        editor = self.tab_view.currentWidget()
        if editor is not None:
            editor.copy()

    def paste(self):
        ...

    def find(self):
        ...


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec())
