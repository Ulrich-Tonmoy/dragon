# STD
import keyword
import pkgutil
from pathlib import Path
# Installed
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.Qsci import *
# Custom
from editor.lexer import CustomLexer
from editor.autocomplete import AutoComplete
import resources


class Editor(QsciScintilla):
    def __init__(self, parent=None, path: Path = None, is_python_file=True):
        super(Editor, self).__init__(parent)
        self.path = path
        self.full_path = self.path.absolute()
        self.is_python_file = is_python_file

        self.cursorPositionChanged.connect(self.cursor_position_changed)

        # Encoding
        self.setUtf8(True)
        # Font
        self.window_font = QFont("FiraCode")
        self.window_font.setPointSize(12)
        self.setFont(self.window_font)

        # Brace matching
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)

        # Indentation
        self.setIndentationGuides(True)
        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(True)

        # AutoComplete
        self.setAutoCompletionSource(
            QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionUseSingle(
            QsciScintilla.AutoCompletionUseSingle.AcusNever)

        # Caret
        self.setCaretForegroundColor(QColor("#dedcdc"))
        self.setCaretLineVisible(True)
        self.setCaretWidth(2)
        self.setCaretLineBackgroundColor(QColor("#2c313c"))

        # EOL
        self.setEolMode(QsciScintilla.EolMode.EolWindows)
        self.setEolVisibility(False)

        # Lexer
        # theres a default lexer for many lang
        if self.is_python_file:
            self.py_lexer = CustomLexer(self)
            self.py_lexer.setDefaultFont(self.window_font)

            # API
            # https://qscintilla.com/
            self.api = QsciAPIs(self.py_lexer)
            self.auto_complete = AutoComplete(self.full_path, self.api)
            self.auto_complete.finished.connect(self.load_auto_complete)
            self.setLexer(self.py_lexer)
        else:
            self.setPaper(QColor("#282c34"))
            self.setColor(QColor("#abb2bf"))
            # for key in keyword.kwlist + dir(__builtins__):
            #     self.api.add(key)
            # for _, name, _ in pkgutil.iter_modules():
            #     self.api.add(name)

            self.api.prepare()

        # Line Number
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "0000")
        self.setMarginsForegroundColor(QColor("#ff888888"))
        self.setMarginsBackgroundColor(QColor("#282c34"))
        self.setMarginsFont(self.window_font)

        # Key Press Events
        # self.keyPressEvent = self.handle_key_press

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.modifiers() == Qt.KeyboardModifier.ControlModifier and e.key() == Qt.Key.Key_Space:
            self.autoCompleteFromAll()
        else:
            return super().keyPressEvent(e)

    def cursor_position_changed(self, line: int, index: int) -> None:
        if self.is_python_file:
            self.auto_complete.get_completions(line+1, index, self.text())

    def load_auto_complete(self):
        pass
