# Generated from nlpql_parser.g4 by ANTLR 4.7.1
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\3")
        buf.write("\7\b\1\4\2\t\2\3\2\3\2\2\2\3\3\3\3\2\2\2\6\2\3\3\2\2\2")
        buf.write("\3\5\3\2\2\2\5\6\7#\2\2\6\4\3\2\2\2\3\2\2")
        return buf.getvalue()


class nlpql_parserLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    T__0 = 1

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'!'" ]

    symbolicNames = [ "<INVALID>",
 ]

    ruleNames = [ "T__0" ]

    grammarFileName = "nlpql_parser.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.7.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


