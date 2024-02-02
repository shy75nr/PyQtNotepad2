class PythonHighlighter(QSyntaxHighlighter):
    Rules = []
    Formats = {}

    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)

        self.initializeFormats()

        KEYWORDS = ["and", "as", "assert", "break", "class",
                    "continue", "def", "del", "elif", "else", "except",
                    "exec", "finally", "for", "from", "global", "if",
                    "import", "in", "is", "lambda", "not", "or", "pass",
                    "raise", "return", "try", "while", "with",
                    "yield", "False", "True", "None"]
        BUILTINS = ["abs", "all", "any", "basestring", "bool", "print",
                    "callable", "chr", "classmethod", "cmp", "compile",
                    "complex", "delattr", "dict", "dir", "divmod",
                    "enumerate", "eval", "execfile", "exit", "file",
                    "filter", "float", "frozenset", "getattr", "globals",
                    "hasattr", "hex", "id", "int", "isinstance",
                    "issubclass", "iter", "len", "list", "locals", "map",
                    "max", "min", "object", "oct", "open", "ord", "pow",
                    "property", "range", "reduce", "repr", "reversed",
                    "round", "set", "setattr", "slice", "sorted",
                    "staticmethod", "str", "sum", "super", "tuple", "type",
                    "vars", "zip"]
        CONSTANTS = ['ArithmeticError', 'AssertionError', 'AttributeError', 'BaseException', 'BlockingIOError',
                     'BrokenPipeError', 'BufferError', 'BytesWarning', 'ChildProcessError', 'ConnectionAbortedError',
                     'ConnectionError', 'ConnectionRefusedError', 'ConnectionResetError', 'DeprecationWarning',
                     'EOFError', 'Ellipsis', 'EnvironmentError', 'Exception', 'FileExistsError', 'FileNotFoundError',
                     'FloatingPointError', 'FutureWarning', 'GeneratorExit', 'IOError', 'ImportError', 'ImportWarning',
                     'IndentationError', 'IndexError', 'InterruptedError', 'IsADirectoryError', 'KeyError',
                     'KeyboardInterrupt', 'LookupError', 'MemoryError', 'ModuleNotFoundError', 'NameError',
                     'NotADirectoryError', 'NotImplemented', 'NotImplementedError', 'OSError', 'OverflowError',
                     'PendingDeprecationWarning', 'PermissionError', 'ProcessLookupError', 'RecursionError',
                     'ReferenceError', 'ResourceWarning', 'RuntimeError', 'RuntimeWarning', 'StopAsyncIteration',
                     'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError', 'SystemExit', 'TabError',
                     'TimeoutError', 'TypeError', 'UnboundLocalError', 'UnicodeDecodeError', 'UnicodeEncodeError',
                     'UnicodeError', 'UnicodeTranslateError', 'UnicodeWarning', 'UserWarning', 'ValueError', 'Warning',
                     'ZeroDivisionError', '__IPYTHON__', '__build_class__', '__debug__', '__doc__', '__import__',
                     '__loader__', '__name__', '__package__', '__spec__', ]
        MAGIC = ['__abs__', '__add__', '__and__', '__bool__', '__ceil__', '__class__', '__delattr__', '__dir__',
                 '__divmod__', '__doc__', '__eq__', '__float__', '__floor__', '__floordiv__', '__format__', '__ge__',
                 '__getattribute__', '__getnewargs__', '__gt__', '__hash__', '__index__', '__init__',
                 '__init_subclass__', '__int__', '__invert__', '__le__', '__lshift__', '__lt__', '__mod__', '__mul__',
                 '__ne__', '__neg__', '__new__', '__or__', '__pos__', '__pow__', '__radd__', '__rand__', '__rdivmod__',
                 '__reduce__', '__reduce_ex__', '__repr__', '__rfloordiv__', '__rlshift__', '__rmod__', '__rmul__',
                 '__ror__', '__round__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__', '__rtruediv__',
                 '__rxor__', '__setattr__', '__sizeof__', '__str__', '__sub__', '__subclasshook__', '__truediv__',
                 '__trunc__', '__xor__']
        PythonHighlighter.Rules.append((QRegExp(
            "|".join([r"\b%s\b" % magic for magic in MAGIC])), "magic"))
        PythonHighlighter.Rules.append((QRegExp(
            "|".join([r"\b%s\b" % keyword for keyword in KEYWORDS])),
                                        "keyword"))
        PythonHighlighter.Rules.append((QRegExp(
            "|".join([r"\b%s\b" % builtin for builtin in BUILTINS])),
                                        "builtin"))
        PythonHighlighter.Rules.append((QRegExp(
            "|".join([r"\b%s\b" % constant
                      for constant in CONSTANTS])), "constant"))
        PythonHighlighter.Rules.append((QRegExp(
            r"\b[+-]?[0-9]+[lL]?\b"
            r"|\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b"
            r"|\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b"),
                                        "number"))
        PythonHighlighter.Rules.append((QRegExp(
            r"\bPyQt4\b|\bQt?[A-Z][a-z]\w+\b"), "pyqt"))
        PythonHighlighter.Rules.append((QRegExp(r"\b@\w+\b"),
                                        "decorator"))
        stringRe = QRegExp(r"""(?:'[^']*'|"[^"]*")""")
        stringRe.setMinimal(True)
        PythonHighlighter.Rules.append((stringRe, "string"))
        self.stringRe = QRegExp(r"""(:?"["]".*"["]"|'''.*''')""")
        self.stringRe.setMinimal(True)
        PythonHighlighter.Rules.append((self.stringRe, "string"))
        self.tripleSingleRe = QRegExp(r"""'''(?!")""")
        self.tripleDoubleRe = QRegExp(r'''"""(?!')''')

    @staticmethod
    def initializeFormats():
        baseFormat = QTextCharFormat()
        baseFormat.setFontFamily("Jetbrains Mono")
        baseFormat.setFontPointSize(12)
        for name, color in (("normal", Qt.black),
                            ("keyword", '#CB7631'), ("builtin", '#7E86BB'),
                            ("constant", 'purple'),
                            ("decorator", Qt.darkBlue), ("comment", Qt.gray),
                            ("string", Qt.darkGreen), ("number", Qt.blue),
                            ("error", Qt.red), ("pyqt", Qt.darkCyan), ("magic", "#AD03AD")):
            format = QTextCharFormat(baseFormat)
            format.setForeground(QColor(color))
            format.setFontWeight(QFont.Bold)
            if name == "comment":
                format.setFontItalic(True)
            PythonHighlighter.Formats[name] = format

    def highlightBlock(self, text):
        NORMAL, TRIPLESINGLE, TRIPLEDOUBLE, ERROR = range(4)

        textLength = len(text)
        prevState = self.previousBlockState()
        self.setFormat(0, textLength,
                       PythonHighlighter.Formats["normal"])

        if text.startswith("Traceback") or text.startswith("Error: "):
            self.setCurrentBlockState(ERROR)
            self.setFormat(0, textLength,
                           PythonHighlighter.Formats["error"])
            return
        if (prevState == ERROR and
                not (text.startswith(sys.ps1) or text.startswith("#"))):
            self.setCurrentBlockState(ERROR)
            self.setFormat(0, textLength,
                           PythonHighlighter.Formats["error"])
            return

        for regex, format in PythonHighlighter.Rules:
            i = regex.indexIn(text)
            while i >= 0:
                length = regex.matchedLength()
                self.setFormat(i, length,
                               PythonHighlighter.Formats[format])
                i = regex.indexIn(text, i + length)

        # Slow but good quality highlighting for comments. For more
        # speed, comment this out and add the following to __init__:
        # PythonHighlighter.Rules.append((QRegExp(r"#.*"), "comment"))
        if not text:
            pass
        elif text[0] == "#":
            self.setFormat(0, len(text),
                           PythonHighlighter.Formats["comment"])
        else:
            stack = []
            for i, c in enumerate(text):
                if c in ('"', "'"):
                    if stack and stack[-1] == c:
                        stack.pop()
                    else:
                        stack.append(c)
                elif c == "#" and len(stack) == 0:
                    self.setFormat(i, len(text),
                                   PythonHighlighter.Formats["comment"])
                    break

        self.setCurrentBlockState(NORMAL)

        if self.stringRe.indexIn(text) != -1:
            return
        # This is fooled by triple quotes inside single quoted strings
        for i, state in ((self.tripleSingleRe.indexIn(text),
                          TRIPLESINGLE),
                         (self.tripleDoubleRe.indexIn(text),
                          TRIPLEDOUBLE)):
            if self.previousBlockState() == state:
                if i == -1:
                    i = text.length()
                    self.setCurrentBlockState(state)
                self.setFormat(0, i + 3,
                               PythonHighlighter.Formats["string"])
            elif i > -1:
                self.setCurrentBlockState(state)
                self.setFormat(i, text.length(),
                               PythonHighlighter.Formats["string"])