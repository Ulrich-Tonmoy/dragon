# STD
import re
import keyword
import types
import builtins
# Installed
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.Qsci import QsciLexerCustom, QsciScintilla


class CustomLexer(QsciLexerCustom):
    def __init__(self, parent):
        super(CustomLexer, self).__init__(parent)

        self.default_color = "#aab2bf"
        self.paper_color = "#282c34"
        # Default Settings
        self.setDefaultColor(QColor(self.default_color))
        self.setDefaultPaper(QColor(self.paper_color))
        self.setDefaultFont(QFont("Consolas", 14))

        # keywords
        self.KEYWORD_LIST = keyword.kwlist
        self.builtin_functions_name = [name for name, obj in vars(
            builtins).items() if isinstance(obj, types.BuiltinFunctionType)]

        # Color per style
        self.DEFAULT = 0
        self.KEYWORD = 1
        self.TYPES = 2
        self.STRING = 3
        self.KEYARGS = 4
        self.BRACKETS = 5
        self.COMMENTS = 6
        self.CONSTANTS = 7
        self.FUNCTIONS = 8
        self.CLASSES = 9
        self.FUNCTION_DEF = 10

        # Styles
        self.setColor(QColor(self.default_color), self.DEFAULT)
        self.setColor(QColor("#c678dd"), self.KEYWORD)
        self.setColor(QColor("#56b6c2"), self.TYPES)
        self.setColor(QColor("#98c379"), self.STRING)
        self.setColor(QColor("#c678dd"), self.KEYARGS)
        self.setColor(QColor("#c678dd"), self.BRACKETS)
        self.setColor(QColor("#777777"), self.COMMENTS)
        self.setColor(QColor("#d19a5e"), self.CONSTANTS)
        self.setColor(QColor("#61afd1"), self.FUNCTIONS)
        self.setColor(QColor("#c68f55"), self.CLASSES)
        self.setColor(QColor("#61afd1"), self.FUNCTION_DEF)

        # Paper color
        self.setPaper(QColor(self.paper_color), self.DEFAULT)
        self.setPaper(QColor(self.paper_color), self.KEYWORD)
        self.setPaper(QColor(self.paper_color), self.TYPES)
        self.setPaper(QColor(self.paper_color), self.STRING)
        self.setPaper(QColor(self.paper_color), self.KEYARGS)
        self.setPaper(QColor(self.paper_color), self.BRACKETS)
        self.setPaper(QColor(self.paper_color), self.COMMENTS)
        self.setPaper(QColor(self.paper_color), self.CONSTANTS)
        self.setPaper(QColor(self.paper_color), self.FUNCTIONS)
        self.setPaper(QColor(self.paper_color), self.CLASSES)
        self.setPaper(QColor(self.paper_color), self.FUNCTION_DEF)

        # Font
        self.setFont(
            QFont("Consolas", 14, weight=QFont.Weight.Bold), self.DEFAULT)
        self.setFont(
            QFont("Consolas", 14, weight=QFont.Weight.Bold), self.KEYWORD)
        self.setFont(
            QFont("Consolas", 14, weight=QFont.Weight.Bold), self.CLASSES)
        self.setFont(QFont("Consolas", 14, weight=QFont.Weight.Bold),
                     self.FUNCTION_DEF)

    def language(self) -> str:
        return "CustomLexer"

    def description(self, style: int) -> str:
        if style == self.DEFAULT:
            return "DEFAULT"
        elif style == self.KEYWORD:
            return "KEYWORD"
        elif style == self.TYPES:
            return "TYPES"
        elif style == self.STRING:
            return "STRING"
        elif style == self.KEYARGS:
            return "KEYARGS"
        elif style == self.BRACKETS:
            return "BRACKETS"
        elif style == self.COMMENTS:
            return "COMMENTS"
        elif style == self.CONSTANTS:
            return "CONSTANTS"
        elif style == self.FUNCTIONS:
            return "FUNCTIONS"
        elif style == self.CLASSES:
            return "CLASSES"
        elif style == self.FUNCTION_DEF:
            return "FUNCTION_DEF"
        else:
            return ""

    def get_tokens(self, text) -> list[str, int]:
        # 3. Tokenize the text
        p = re.compile(r"[*]\/|\/[*]|\s+|\w+|\W")

        # 'token_list' is a list of tuples: (token_name, token_len), ex: '(class, 5)'
        return [(token, len(bytearray(token, "utf-8")))
                for token in p.findall(text)]

    def styleText(self, start: int, end: int) -> None:
        self.startStyling(start)
        editor: QsciScintilla = self.parent()
        text = editor.text()[start:end]
        tokens_list = self.get_tokens(text)
        string_flag = False

        if start > 0:
            previous_style_nr = editor.SendScintilla(
                editor.SCI_GETSTYLEAT, start-1)
            if previous_style_nr == self.STRING:
                string_flag = False

        def next_token(skip: int = None):
            if len(tokens_list) > 0:
                if skip is not None and skip != 0:
                    for _ in range(skip-1):
                        if len(tokens_list) > 0:
                            tokens_list.pop(0)
                return tokens_list.pop(0)
            else:
                return None

        def peek_token(n=0):
            try:
                return tokens_list[n]
            except IndexError:
                return ['']

        def skip_space_peek(skip=None):
            i = 0
            token = (' ')
            if skip is not None:
                i = skip
            while token[0].isspace():
                token = peek_token(i)
                i += 1
            return token, i

        while True:
            current_token = next_token()
            if current_token is None:
                break
            token: str = current_token[0]
            token_len: int = current_token[1]

            if string_flag:
                self.setStyling(token_len, self.STRING)
                if token == "'" or token == '"':
                    string_flag = False
                continue
            if token == "class":
                name, next_index = skip_space_peek()
                bracket_or_colon, _ = skip_space_peek(next_index)
                if name[0].isidentifier() and bracket_or_colon[0] in (":", "("):
                    self.setStyling(token_len, self.KEYWORD)
                    _ = next_token(next_index)
                    self.setStyling(name[1]+1, self.CLASSES)
                    continue
                else:
                    self.setStyling(token_len, self.KEYWORD)
                    continue
            elif token == "def":
                name, next_index = skip_space_peek()
                if name[0].isidentifier():
                    self.setStyling(token_len, self.CLASSES)
                    _ = next_token(next_index)
                    self.setStyling(name[1]+1, self.FUNCTION_DEF)
                    continue
                else:
                    self.setStyling(token_len, self.KEYWORD)
                    continue
            elif token in self.KEYWORD_LIST:
                self.setStyling(token_len, self.KEYWORD)
            elif token.isnumeric() or token == 'self':
                self.setStyling(token_len, self.CONSTANTS)
            elif token in ["(", ")", "{", "}", "[", "]"]:
                self.setStyling(token_len, self.BRACKETS)
            elif token == "'" or token == '"':
                self.setStyling(token_len, self.STRING)
                string_flag = True
            elif token in self.builtin_functions_name or token in ['+', '-', '*', '/', '%', '=', '<', '>']:
                self.setStyling(token_len, self.TYPES)
            else:
                self.setStyling(token_len, self.DEFAULT)
