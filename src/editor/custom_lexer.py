# STD
import keyword
import types
import builtins
# Custom
from editor.base_lexer import BaseLexer


class CustomLexer(BaseLexer):
    """ Custom Lexer for Python"""

    def __init__(self, editor):
        super(CustomLexer, self).__init__("python", editor)

        # keywords
        self.keywords_list = keyword.kwlist
        self.builtin_functions_name = [name for name, obj in vars(
            builtins).items() if isinstance(obj, types.BuiltinFunctionType)]

    def styleText(self, start: int, end: int) -> None:
        self.startStyling(start)

        text = self.editor.text()[start:end]
        self.generate_token(text)
        string_flag = False
        comment_flag = False

        while True:
            current_token = self.next_token()
            if current_token is None:
                break
            token: str = current_token[0]
            token_len: int = current_token[1]

            # if comment_flag:
            #     self.setStyling(current_token[1], self.COMMENTS)
            #     if token == "\n" or token == "\r\n" or token == "\r" or token == "\r\t":
            #         comment_flag = False
            #     continue
            if string_flag:
                self.setStyling(token_len, self.STRING)
                if token == "'" or token == '"':
                    string_flag = False
                continue
            if token == "class":
                name, next_index = self.skip_space_peek()
                bracket_or_colon, _ = self.skip_space_peek(next_index)
                if name[0].isidentifier() and bracket_or_colon[0] in (":", "("):
                    self.setStyling(token_len, self.KEYWORD)
                    _ = self.next_token(next_index)
                    self.setStyling(name[1]+1, self.CLASSES)
                    continue
                else:
                    self.setStyling(token_len, self.KEYWORD)
                    continue
            elif token == "def":
                name, next_index = self.skip_space_peek()
                if name[0].isidentifier():
                    self.setStyling(token_len, self.CLASSES)
                    _ = self.next_token(next_index)
                    self.setStyling(name[1]+1, self.FUNCTION_DEF)
                    continue
                else:
                    self.setStyling(token_len, self.KEYWORD)
                    continue
            elif token in self.keywords_list:
                self.setStyling(token_len, self.KEYWORD)
            elif token.strip() == "." and self.peek_token()[0].isidentifier():
                self.setStyling(token_len, self.DEFAULT)
                current_token = self.next_token()
                token: str = current_token[0]
                token_len: int = current_token[1]
                if self.peek_token()[0] == "(":
                    self.setStyling(token_len, self.FUNCTIONS)
                else:
                    self.setStyling(token_len, self.DEFAULT)
                continue
            elif token.isnumeric() or token == 'self':
                self.setStyling(token_len, self.CONSTANTS)
            elif token in ["(", ")", "{", "}", "[", "]"]:
                self.setStyling(token_len, self.BRACKETS)
            elif token == "'" or token == '"':
                self.setStyling(token_len, self.STRING)
                string_flag = True
            # elif token == '#':
            #     self.setStyling(token_len, self.COMMENTS)
            #     comment_flag = True
            elif token in self.builtin_functions_name or token in ['+', '-', '*', '/', '%', '=', '<', '>']:
                self.setStyling(token_len, self.TYPES)
            else:
                self.setStyling(token_len, self.DEFAULT)
