# Generated from nlpql_parser.g4 by ANTLR 4.7.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys

def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3&")
        buf.write("\u0097\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\4\16")
        buf.write("\t\16\4\17\t\17\3\2\7\2 \n\2\f\2\16\2#\13\2\3\2\3\2\3")
        buf.write("\3\3\3\3\3\3\3\3\3\3\3\3\3\5\3.\n\3\3\3\3\3\3\4\3\4\3")
        buf.write("\4\5\4\65\n\4\3\4\5\48\n\4\3\5\3\5\3\5\5\5=\n\5\3\5\5")
        buf.write("\5@\n\5\3\6\3\6\3\6\5\6E\n\6\3\6\5\6H\n\6\3\7\3\7\3\7")
        buf.write("\5\7M\n\7\3\7\5\7P\n\7\3\7\3\7\3\7\3\b\3\b\3\b\3\b\3\b")
        buf.write("\3\t\3\t\3\t\3\t\3\t\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\13")
        buf.write("\3\13\3\13\3\13\3\13\5\13k\n\13\3\f\3\f\3\f\3\f\7\fq\n")
        buf.write("\f\f\f\16\ft\13\f\3\f\3\f\3\f\3\f\5\fz\n\f\3\r\3\r\3\r")
        buf.write("\3\r\3\16\3\16\3\16\3\16\7\16\u0084\n\16\f\16\16\16\u0087")
        buf.write("\13\16\3\16\3\16\3\16\3\16\5\16\u008d\n\16\3\17\3\17\3")
        buf.write("\17\3\17\3\17\3\17\5\17\u0095\n\17\3\17\2\2\20\2\4\6\b")
        buf.write("\n\f\16\20\22\24\26\30\32\34\2\4\4\2\f\f\"\"\4\2\r\16")
        buf.write("\"\"\2\u00a1\2!\3\2\2\2\4-\3\2\2\2\6\61\3\2\2\2\b9\3\2")
        buf.write("\2\2\nA\3\2\2\2\fI\3\2\2\2\16T\3\2\2\2\20Y\3\2\2\2\22")
        buf.write("^\3\2\2\2\24e\3\2\2\2\26y\3\2\2\2\30{\3\2\2\2\32\u008c")
        buf.write("\3\2\2\2\34\u0094\3\2\2\2\36 \5\4\3\2\37\36\3\2\2\2 #")
        buf.write("\3\2\2\2!\37\3\2\2\2!\"\3\2\2\2\"$\3\2\2\2#!\3\2\2\2$")
        buf.write("%\7\2\2\3%\3\3\2\2\2&.\5\6\4\2\'.\5\b\5\2(.\5\n\6\2).")
        buf.write("\5\f\7\2*.\5\16\b\2+.\5\20\t\2,.\5\24\13\2-&\3\2\2\2-")
        buf.write("\'\3\2\2\2-(\3\2\2\2-)\3\2\2\2-*\3\2\2\2-+\3\2\2\2-,\3")
        buf.write("\2\2\2./\3\2\2\2/\60\7\17\2\2\60\5\3\2\2\2\61\62\7\3\2")
        buf.write("\2\62\64\7\"\2\2\63\65\7\4\2\2\64\63\3\2\2\2\64\65\3\2")
        buf.write("\2\2\65\67\3\2\2\2\668\7\"\2\2\67\66\3\2\2\2\678\3\2\2")
        buf.write("\28\7\3\2\2\29:\7\5\2\2:<\7\"\2\2;=\7\4\2\2<;\3\2\2\2")
        buf.write("<=\3\2\2\2=?\3\2\2\2>@\7\"\2\2?>\3\2\2\2?@\3\2\2\2@\t")
        buf.write("\3\2\2\2AB\7\6\2\2BD\t\2\2\2CE\7\4\2\2DC\3\2\2\2DE\3\2")
        buf.write("\2\2EG\3\2\2\2FH\7\"\2\2GF\3\2\2\2GH\3\2\2\2H\13\3\2\2")
        buf.write("\2IJ\7\7\2\2JL\t\3\2\2KM\7\4\2\2LK\3\2\2\2LM\3\2\2\2M")
        buf.write("O\3\2\2\2NP\7\"\2\2ON\3\2\2\2OP\3\2\2\2PQ\3\2\2\2QR\7")
        buf.write("\b\2\2RS\7&\2\2S\r\3\2\2\2TU\7\t\2\2UV\7\"\2\2VW\7\20")
        buf.write("\2\2WX\5\34\17\2X\17\3\2\2\2YZ\7\n\2\2Z[\7\"\2\2[\\\7")
        buf.write("\20\2\2\\]\5\22\n\2]\21\3\2\2\2^_\7&\2\2_`\7\21\2\2`a")
        buf.write("\7&\2\2ab\7\23\2\2bc\5\34\17\2cd\7\24\2\2d\23\3\2\2\2")
        buf.write("ef\7\13\2\2fg\7\"\2\2gj\7\20\2\2hk\5\32\16\2ik\7\"\2\2")
        buf.write("jh\3\2\2\2ji\3\2\2\2k\25\3\2\2\2lm\7\27\2\2mr\5\30\r\2")
        buf.write("no\7\22\2\2oq\5\30\r\2pn\3\2\2\2qt\3\2\2\2rp\3\2\2\2r")
        buf.write("s\3\2\2\2su\3\2\2\2tr\3\2\2\2uv\7\30\2\2vz\3\2\2\2wx\7")
        buf.write("\27\2\2xz\7\30\2\2yl\3\2\2\2yw\3\2\2\2z\27\3\2\2\2{|\7")
        buf.write("\"\2\2|}\7\20\2\2}~\5\34\17\2~\31\3\2\2\2\177\u0080\7")
        buf.write("\25\2\2\u0080\u0085\5\34\17\2\u0081\u0082\7\22\2\2\u0082")
        buf.write("\u0084\5\34\17\2\u0083\u0081\3\2\2\2\u0084\u0087\3\2\2")
        buf.write("\2\u0085\u0083\3\2\2\2\u0085\u0086\3\2\2\2\u0086\u0088")
        buf.write("\3\2\2\2\u0087\u0085\3\2\2\2\u0088\u0089\7\26\2\2\u0089")
        buf.write("\u008d\3\2\2\2\u008a\u008b\7\25\2\2\u008b\u008d\7\26\2")
        buf.write("\2\u008c\177\3\2\2\2\u008c\u008a\3\2\2\2\u008d\33\3\2")
        buf.write("\2\2\u008e\u0095\7\"\2\2\u008f\u0095\7\31\2\2\u0090\u0095")
        buf.write("\5\26\f\2\u0091\u0095\5\32\16\2\u0092\u0095\7\37\2\2\u0093")
        buf.write("\u0095\7 \2\2\u0094\u008e\3\2\2\2\u0094\u008f\3\2\2\2")
        buf.write("\u0094\u0090\3\2\2\2\u0094\u0091\3\2\2\2\u0094\u0092\3")
        buf.write("\2\2\2\u0094\u0093\3\2\2\2\u0095\35\3\2\2\2\22!-\64\67")
        buf.write("<?DGLOjry\u0085\u008c\u0094")
        return buf.getvalue()


class nlpql_parserParser ( Parser ):

    grammarFileName = "nlpql_parser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'phenotype'", "'version'", "'description'", 
                     "'datamodel'", "'include'", "'called'", "'codesystem'", 
                     "'valueset'", "'termset'", "'OMOP'", "'ClarityCore'", 
                     "'OHDSIHelpers'", "';'", "':'", "'.'", "','", "'('", 
                     "')'", "'['", "']'", "'{'", "'}'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'null'" ]

    symbolicNames = [ "<INVALID>", "PHENOTYPE_NAME", "VERSION", "DESCRIPTION", 
                      "DATAMODEL", "INCLUDE", "CALLED", "CODE_SYSTEM", "VALUE_SET", 
                      "TERM_SET", "OMOP", "CLARITY_CORE", "OHDSI_HELPERS", 
                      "SEMI", "COLON", "DOT", "COMMA", "L_PAREN", "R_PAREN", 
                      "L_BRACKET", "R_BRACKET", "L_CURLY", "R_CURLY", "DECIMAL", 
                      "HEX", "OCT", "BINARY", "FLOAT", "HEX_FLOAT", "BOOL", 
                      "NULL", "CHAR", "STRING", "WS", "COMMENT", "LINE_COMMENT", 
                      "IDENTIFIER" ]

    RULE_validExpression = 0
    RULE_statement = 1
    RULE_phenotypeName = 2
    RULE_description = 3
    RULE_dataModel = 4
    RULE_include = 5
    RULE_codeSystem = 6
    RULE_valueSet = 7
    RULE_methodCall = 8
    RULE_termSet = 9
    RULE_obj = 10
    RULE_pair = 11
    RULE_array = 12
    RULE_value = 13

    ruleNames =  [ "validExpression", "statement", "phenotypeName", "description", 
                   "dataModel", "include", "codeSystem", "valueSet", "methodCall", 
                   "termSet", "obj", "pair", "array", "value" ]

    EOF = Token.EOF
    PHENOTYPE_NAME=1
    VERSION=2
    DESCRIPTION=3
    DATAMODEL=4
    INCLUDE=5
    CALLED=6
    CODE_SYSTEM=7
    VALUE_SET=8
    TERM_SET=9
    OMOP=10
    CLARITY_CORE=11
    OHDSI_HELPERS=12
    SEMI=13
    COLON=14
    DOT=15
    COMMA=16
    L_PAREN=17
    R_PAREN=18
    L_BRACKET=19
    R_BRACKET=20
    L_CURLY=21
    R_CURLY=22
    DECIMAL=23
    HEX=24
    OCT=25
    BINARY=26
    FLOAT=27
    HEX_FLOAT=28
    BOOL=29
    NULL=30
    CHAR=31
    STRING=32
    WS=33
    COMMENT=34
    LINE_COMMENT=35
    IDENTIFIER=36

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.7.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



    class ValidExpressionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(nlpql_parserParser.EOF, 0)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(nlpql_parserParser.StatementContext)
            else:
                return self.getTypedRuleContext(nlpql_parserParser.StatementContext,i)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_validExpression




    def validExpression(self):

        localctx = nlpql_parserParser.ValidExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_validExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 31
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << nlpql_parserParser.PHENOTYPE_NAME) | (1 << nlpql_parserParser.DESCRIPTION) | (1 << nlpql_parserParser.DATAMODEL) | (1 << nlpql_parserParser.INCLUDE) | (1 << nlpql_parserParser.CODE_SYSTEM) | (1 << nlpql_parserParser.VALUE_SET) | (1 << nlpql_parserParser.TERM_SET))) != 0):
                self.state = 28
                self.statement()
                self.state = 33
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 34
            self.match(nlpql_parserParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class StatementContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SEMI(self):
            return self.getToken(nlpql_parserParser.SEMI, 0)

        def phenotypeName(self):
            return self.getTypedRuleContext(nlpql_parserParser.PhenotypeNameContext,0)


        def description(self):
            return self.getTypedRuleContext(nlpql_parserParser.DescriptionContext,0)


        def dataModel(self):
            return self.getTypedRuleContext(nlpql_parserParser.DataModelContext,0)


        def include(self):
            return self.getTypedRuleContext(nlpql_parserParser.IncludeContext,0)


        def codeSystem(self):
            return self.getTypedRuleContext(nlpql_parserParser.CodeSystemContext,0)


        def valueSet(self):
            return self.getTypedRuleContext(nlpql_parserParser.ValueSetContext,0)


        def termSet(self):
            return self.getTypedRuleContext(nlpql_parserParser.TermSetContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_statement




    def statement(self):

        localctx = nlpql_parserParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_statement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 43
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [nlpql_parserParser.PHENOTYPE_NAME]:
                self.state = 36
                self.phenotypeName()
                pass
            elif token in [nlpql_parserParser.DESCRIPTION]:
                self.state = 37
                self.description()
                pass
            elif token in [nlpql_parserParser.DATAMODEL]:
                self.state = 38
                self.dataModel()
                pass
            elif token in [nlpql_parserParser.INCLUDE]:
                self.state = 39
                self.include()
                pass
            elif token in [nlpql_parserParser.CODE_SYSTEM]:
                self.state = 40
                self.codeSystem()
                pass
            elif token in [nlpql_parserParser.VALUE_SET]:
                self.state = 41
                self.valueSet()
                pass
            elif token in [nlpql_parserParser.TERM_SET]:
                self.state = 42
                self.termSet()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 45
            self.match(nlpql_parserParser.SEMI)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PhenotypeNameContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PHENOTYPE_NAME(self):
            return self.getToken(nlpql_parserParser.PHENOTYPE_NAME, 0)

        def STRING(self, i:int=None):
            if i is None:
                return self.getTokens(nlpql_parserParser.STRING)
            else:
                return self.getToken(nlpql_parserParser.STRING, i)

        def VERSION(self):
            return self.getToken(nlpql_parserParser.VERSION, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_phenotypeName




    def phenotypeName(self):

        localctx = nlpql_parserParser.PhenotypeNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_phenotypeName)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 47
            self.match(nlpql_parserParser.PHENOTYPE_NAME)
            self.state = 48
            self.match(nlpql_parserParser.STRING)
            self.state = 50
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.VERSION:
                self.state = 49
                self.match(nlpql_parserParser.VERSION)


            self.state = 53
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.STRING:
                self.state = 52
                self.match(nlpql_parserParser.STRING)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DescriptionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DESCRIPTION(self):
            return self.getToken(nlpql_parserParser.DESCRIPTION, 0)

        def STRING(self, i:int=None):
            if i is None:
                return self.getTokens(nlpql_parserParser.STRING)
            else:
                return self.getToken(nlpql_parserParser.STRING, i)

        def VERSION(self):
            return self.getToken(nlpql_parserParser.VERSION, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_description




    def description(self):

        localctx = nlpql_parserParser.DescriptionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_description)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 55
            self.match(nlpql_parserParser.DESCRIPTION)
            self.state = 56
            self.match(nlpql_parserParser.STRING)
            self.state = 58
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.VERSION:
                self.state = 57
                self.match(nlpql_parserParser.VERSION)


            self.state = 61
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.STRING:
                self.state = 60
                self.match(nlpql_parserParser.STRING)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DataModelContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DATAMODEL(self):
            return self.getToken(nlpql_parserParser.DATAMODEL, 0)

        def OMOP(self):
            return self.getToken(nlpql_parserParser.OMOP, 0)

        def STRING(self, i:int=None):
            if i is None:
                return self.getTokens(nlpql_parserParser.STRING)
            else:
                return self.getToken(nlpql_parserParser.STRING, i)

        def VERSION(self):
            return self.getToken(nlpql_parserParser.VERSION, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_dataModel




    def dataModel(self):

        localctx = nlpql_parserParser.DataModelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_dataModel)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 63
            self.match(nlpql_parserParser.DATAMODEL)
            self.state = 64
            _la = self._input.LA(1)
            if not(_la==nlpql_parserParser.OMOP or _la==nlpql_parserParser.STRING):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 66
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.VERSION:
                self.state = 65
                self.match(nlpql_parserParser.VERSION)


            self.state = 69
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.STRING:
                self.state = 68
                self.match(nlpql_parserParser.STRING)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class IncludeContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INCLUDE(self):
            return self.getToken(nlpql_parserParser.INCLUDE, 0)

        def CALLED(self):
            return self.getToken(nlpql_parserParser.CALLED, 0)

        def IDENTIFIER(self):
            return self.getToken(nlpql_parserParser.IDENTIFIER, 0)

        def CLARITY_CORE(self):
            return self.getToken(nlpql_parserParser.CLARITY_CORE, 0)

        def OHDSI_HELPERS(self):
            return self.getToken(nlpql_parserParser.OHDSI_HELPERS, 0)

        def STRING(self, i:int=None):
            if i is None:
                return self.getTokens(nlpql_parserParser.STRING)
            else:
                return self.getToken(nlpql_parserParser.STRING, i)

        def VERSION(self):
            return self.getToken(nlpql_parserParser.VERSION, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_include




    def include(self):

        localctx = nlpql_parserParser.IncludeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_include)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 71
            self.match(nlpql_parserParser.INCLUDE)
            self.state = 72
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << nlpql_parserParser.CLARITY_CORE) | (1 << nlpql_parserParser.OHDSI_HELPERS) | (1 << nlpql_parserParser.STRING))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 74
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.VERSION:
                self.state = 73
                self.match(nlpql_parserParser.VERSION)


            self.state = 77
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.STRING:
                self.state = 76
                self.match(nlpql_parserParser.STRING)


            self.state = 79
            self.match(nlpql_parserParser.CALLED)
            self.state = 80
            self.match(nlpql_parserParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class CodeSystemContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CODE_SYSTEM(self):
            return self.getToken(nlpql_parserParser.CODE_SYSTEM, 0)

        def STRING(self):
            return self.getToken(nlpql_parserParser.STRING, 0)

        def COLON(self):
            return self.getToken(nlpql_parserParser.COLON, 0)

        def value(self):
            return self.getTypedRuleContext(nlpql_parserParser.ValueContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_codeSystem




    def codeSystem(self):

        localctx = nlpql_parserParser.CodeSystemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_codeSystem)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 82
            self.match(nlpql_parserParser.CODE_SYSTEM)
            self.state = 83
            self.match(nlpql_parserParser.STRING)
            self.state = 84
            self.match(nlpql_parserParser.COLON)
            self.state = 85
            self.value()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ValueSetContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def VALUE_SET(self):
            return self.getToken(nlpql_parserParser.VALUE_SET, 0)

        def STRING(self):
            return self.getToken(nlpql_parserParser.STRING, 0)

        def COLON(self):
            return self.getToken(nlpql_parserParser.COLON, 0)

        def methodCall(self):
            return self.getTypedRuleContext(nlpql_parserParser.MethodCallContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_valueSet




    def valueSet(self):

        localctx = nlpql_parserParser.ValueSetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_valueSet)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 87
            self.match(nlpql_parserParser.VALUE_SET)
            self.state = 88
            self.match(nlpql_parserParser.STRING)
            self.state = 89
            self.match(nlpql_parserParser.COLON)
            self.state = 90
            self.methodCall()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class MethodCallContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self, i:int=None):
            if i is None:
                return self.getTokens(nlpql_parserParser.IDENTIFIER)
            else:
                return self.getToken(nlpql_parserParser.IDENTIFIER, i)

        def DOT(self):
            return self.getToken(nlpql_parserParser.DOT, 0)

        def L_PAREN(self):
            return self.getToken(nlpql_parserParser.L_PAREN, 0)

        def value(self):
            return self.getTypedRuleContext(nlpql_parserParser.ValueContext,0)


        def R_PAREN(self):
            return self.getToken(nlpql_parserParser.R_PAREN, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_methodCall




    def methodCall(self):

        localctx = nlpql_parserParser.MethodCallContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_methodCall)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 92
            self.match(nlpql_parserParser.IDENTIFIER)
            self.state = 93
            self.match(nlpql_parserParser.DOT)
            self.state = 94
            self.match(nlpql_parserParser.IDENTIFIER)
            self.state = 95
            self.match(nlpql_parserParser.L_PAREN)
            self.state = 96
            self.value()
            self.state = 97
            self.match(nlpql_parserParser.R_PAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class TermSetContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TERM_SET(self):
            return self.getToken(nlpql_parserParser.TERM_SET, 0)

        def STRING(self, i:int=None):
            if i is None:
                return self.getTokens(nlpql_parserParser.STRING)
            else:
                return self.getToken(nlpql_parserParser.STRING, i)

        def COLON(self):
            return self.getToken(nlpql_parserParser.COLON, 0)

        def array(self):
            return self.getTypedRuleContext(nlpql_parserParser.ArrayContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_termSet




    def termSet(self):

        localctx = nlpql_parserParser.TermSetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_termSet)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 99
            self.match(nlpql_parserParser.TERM_SET)
            self.state = 100
            self.match(nlpql_parserParser.STRING)
            self.state = 101
            self.match(nlpql_parserParser.COLON)
            self.state = 104
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [nlpql_parserParser.L_BRACKET]:
                self.state = 102
                self.array()
                pass
            elif token in [nlpql_parserParser.STRING]:
                self.state = 103
                self.match(nlpql_parserParser.STRING)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ObjContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def L_CURLY(self):
            return self.getToken(nlpql_parserParser.L_CURLY, 0)

        def pair(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(nlpql_parserParser.PairContext)
            else:
                return self.getTypedRuleContext(nlpql_parserParser.PairContext,i)


        def R_CURLY(self):
            return self.getToken(nlpql_parserParser.R_CURLY, 0)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(nlpql_parserParser.COMMA)
            else:
                return self.getToken(nlpql_parserParser.COMMA, i)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_obj




    def obj(self):

        localctx = nlpql_parserParser.ObjContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_obj)
        self._la = 0 # Token type
        try:
            self.state = 119
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,12,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 106
                self.match(nlpql_parserParser.L_CURLY)
                self.state = 107
                self.pair()
                self.state = 112
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==nlpql_parserParser.COMMA:
                    self.state = 108
                    self.match(nlpql_parserParser.COMMA)
                    self.state = 109
                    self.pair()
                    self.state = 114
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 115
                self.match(nlpql_parserParser.R_CURLY)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 117
                self.match(nlpql_parserParser.L_CURLY)
                self.state = 118
                self.match(nlpql_parserParser.R_CURLY)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PairContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(nlpql_parserParser.STRING, 0)

        def COLON(self):
            return self.getToken(nlpql_parserParser.COLON, 0)

        def value(self):
            return self.getTypedRuleContext(nlpql_parserParser.ValueContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_pair




    def pair(self):

        localctx = nlpql_parserParser.PairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_pair)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 121
            self.match(nlpql_parserParser.STRING)
            self.state = 122
            self.match(nlpql_parserParser.COLON)
            self.state = 123
            self.value()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ArrayContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def L_BRACKET(self):
            return self.getToken(nlpql_parserParser.L_BRACKET, 0)

        def value(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(nlpql_parserParser.ValueContext)
            else:
                return self.getTypedRuleContext(nlpql_parserParser.ValueContext,i)


        def R_BRACKET(self):
            return self.getToken(nlpql_parserParser.R_BRACKET, 0)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(nlpql_parserParser.COMMA)
            else:
                return self.getToken(nlpql_parserParser.COMMA, i)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_array




    def array(self):

        localctx = nlpql_parserParser.ArrayContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_array)
        self._la = 0 # Token type
        try:
            self.state = 138
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,14,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 125
                self.match(nlpql_parserParser.L_BRACKET)
                self.state = 126
                self.value()
                self.state = 131
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==nlpql_parserParser.COMMA:
                    self.state = 127
                    self.match(nlpql_parserParser.COMMA)
                    self.state = 128
                    self.value()
                    self.state = 133
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 134
                self.match(nlpql_parserParser.R_BRACKET)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 136
                self.match(nlpql_parserParser.L_BRACKET)
                self.state = 137
                self.match(nlpql_parserParser.R_BRACKET)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ValueContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(nlpql_parserParser.STRING, 0)

        def DECIMAL(self):
            return self.getToken(nlpql_parserParser.DECIMAL, 0)

        def obj(self):
            return self.getTypedRuleContext(nlpql_parserParser.ObjContext,0)


        def array(self):
            return self.getTypedRuleContext(nlpql_parserParser.ArrayContext,0)


        def BOOL(self):
            return self.getToken(nlpql_parserParser.BOOL, 0)

        def NULL(self):
            return self.getToken(nlpql_parserParser.NULL, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_value




    def value(self):

        localctx = nlpql_parserParser.ValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_value)
        try:
            self.state = 146
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [nlpql_parserParser.STRING]:
                self.enterOuterAlt(localctx, 1)
                self.state = 140
                self.match(nlpql_parserParser.STRING)
                pass
            elif token in [nlpql_parserParser.DECIMAL]:
                self.enterOuterAlt(localctx, 2)
                self.state = 141
                self.match(nlpql_parserParser.DECIMAL)
                pass
            elif token in [nlpql_parserParser.L_CURLY]:
                self.enterOuterAlt(localctx, 3)
                self.state = 142
                self.obj()
                pass
            elif token in [nlpql_parserParser.L_BRACKET]:
                self.enterOuterAlt(localctx, 4)
                self.state = 143
                self.array()
                pass
            elif token in [nlpql_parserParser.BOOL]:
                self.enterOuterAlt(localctx, 5)
                self.state = 144
                self.match(nlpql_parserParser.BOOL)
                pass
            elif token in [nlpql_parserParser.NULL]:
                self.enterOuterAlt(localctx, 6)
                self.state = 145
                self.match(nlpql_parserParser.NULL)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





