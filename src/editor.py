import keyword
import pkgutil

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.Qsci import *

from lexer import CustomLexer
import resources


class Editor(QsciScintilla):
    def __init__(self, parent=None):
        super(Editor, self).__init__(parent)

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
        self.py_lexer = CustomLexer(self)
        self.py_lexer.setDefaultFont(self.window_font)

        # API
        # https://qscintilla.com/
        self.api = QsciAPIs(self.py_lexer)
        for key in keyword.kwlist + dir(__builtins__):
            self.api.add(key)
        for _, name, _ in pkgutil.iter_modules():
            self.api.add(name)

        self.api.prepare()
        self.setLexer(self.py_lexer)

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
