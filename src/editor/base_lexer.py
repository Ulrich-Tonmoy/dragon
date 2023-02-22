# STD
import re
import json
# Installed
from PyQt6.QtGui import *
from PyQt6.Qsci import QsciLexerCustom

# config type
DefaultConfig = dict[str, str, tuple[str, int]]


class BaseLexer(QsciLexerCustom):
    """ Base Lexer Class to Support Syntax Highlighting for all Languages """

    def __init__(self, language_name, editor, theme=None, default_config: DefaultConfig = None):
        super(BaseLexer, self).__init__(editor)

        self.editor = editor
        self.language_name = language_name
        self.theme_json = None
        if theme is None:
            self.theme = "./resources/static/data/theme.json"
        else:
            self.theme = theme
        self.token_list: list[str, str] = []
        self.keywords_list = []
        self.builtin_names = []
        if default_config is None:
            default_config: DefaultConfig = {}
            default_config["color"] = "#aab2bf"
            default_config["paper"] = "#282c34"
            default_config["font"] = ("Consolas", 14)

        self.setDefaultColor(QColor(default_config["color"]))
        self.setDefaultPaper(QColor(default_config["paper"]))
        self.setDefaultFont(
            QFont(default_config["font"][0], default_config["font"][1]))

        self._init_theme_variables()
        self._init_theme()

    def set_keywords(self, keywords: list[str]):
        """ Set list of strings that are considered keywords for a language"""
        self.keywords_list = keywords

    def set_builtin_names(self, builtin_names: list[str]):
        """ Set list of strings that are builtin keywords in a language"""
        self.builtin_names = builtin_names

    def _init_theme_variables(self):
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

        self.default_names = (
            "default",
            "keyword",
            "types",
            "string",
            "keyargs",
            "brackets",
            "comments",
            "constants",
            "functions",
            "classes",
            "function_def"
        )
        self.font_weights = {
            "thin": QFont.Weight.Thin,
            "extralight": QFont.Weight.ExtraLight,
            "light": QFont.Weight.Light,
            "normal": QFont.Weight.Normal,
            "medium": QFont.Weight.Medium,
            "demibold": QFont.Weight.DemiBold,
            "bold": QFont.Weight.Bold,
            "extrabold": QFont.Weight.ExtraBold,
            "black": QFont.Weight.Black,
        }

    def _init_theme(self):
        with open(self.theme, 'r')as f:
            self.theme_json = json.load(f)

        colors = self.theme_json['theme']["syntax"]

        for color in colors:
            name: str = list(color.keys())[0]
            if name not in self.default_names:
                print(f"{name} is not a valid style name!")
                continue
            for key, value in color[name].items():
                if key == "color":
                    self.setColor(QColor(value), getattr(self, name.upper()))
                elif key == "bg-color":
                    self.setPaper(QColor(value), getattr(self, name.upper()))
                elif key == "font":
                    try:
                        self.setFont(QFont(
                            value.get("family", "Consolas"),
                            value.get("font-size", 14),
                            self.font_weights.get(
                                value.get("font-weight", QFont.Weight.Normal)),
                            value.get("italic", False)
                        ), getattr(self, name.upper()))
                    except AttributeError as e:
                        print(f"Error setting theme {e}")

    def language(self) -> str:
        return self.language_name

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
        return ""

    def generate_token(self, text):
        p = re.compile(r"[*]\/|\/[*]|\s+|\w+|\W")

        # 'token_list' is a list of tuples: (token_name, token_len), ex: '(class, 5)'
        self.token_list = [(token, len(bytearray(token, "utf-8")))
                           for token in p.findall(text)]

    def next_token(self, skip: int = None):
        if len(self.token_list) > 0:
            if skip is not None and skip != 0:
                for _ in range(skip-1):
                    if len(self.token_list) > 0:
                        self.token_list.pop(0)
            return self.token_list.pop(0)
        else:
            return None

    def peek_token(self, n=0):
        try:
            return self.token_list[n]
        except IndexError:
            return ['']

    def skip_space_peek(self, skip=None):
        i = 0
        token = " "
        if skip is not None:
            i = skip
        while token[0].isspace():
            token = self.token_list[i]
            i += 1
        return token, i
