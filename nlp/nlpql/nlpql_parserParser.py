# Generated from nlpql_parser.g4 by ANTLR 4.7.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys

def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3I")
        buf.write("\u0182\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\4\16")
        buf.write("\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22\4\23\t\23")
        buf.write("\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30\4\31")
        buf.write("\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35\4\36\t\36")
        buf.write("\4\37\t\37\4 \t \4!\t!\4\"\t\"\4#\t#\4$\t$\4%\t%\4&\t")
        buf.write("&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t+\4,\t,\3\2\7\2Z\n\2\f")
        buf.write("\2\16\2]\13\2\3\2\3\2\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3")
        buf.write("\3\3\3\3\3\3\3\3\3\3\5\3n\n\3\3\3\3\3\3\4\3\4\3\5\3\5")
        buf.write("\3\5\3\6\3\6\3\7\3\7\3\7\5\7|\n\7\3\b\3\b\3\b\3\t\3\t")
        buf.write("\3\t\5\t\u0084\n\t\3\n\3\n\3\n\5\n\u0089\n\n\3\n\3\n\3")
        buf.write("\n\3\13\3\13\3\13\3\f\3\f\3\f\3\r\3\r\3\r\3\16\3\16\3")
        buf.write("\16\3\17\3\17\3\17\3\20\5\20\u009e\n\20\3\20\3\20\3\20")
        buf.write("\3\21\3\21\3\21\3\22\3\22\5\22\u00a8\n\22\3\22\3\22\3")
        buf.write("\22\3\22\3\23\3\23\5\23\u00b0\n\23\3\24\3\24\3\25\3\25")
        buf.write("\3\26\3\26\3\27\3\27\3\27\3\30\3\30\3\30\3\30\3\30\3\30")
        buf.write("\5\30\u00c1\n\30\3\30\3\30\3\30\3\30\7\30\u00c7\n\30\f")
        buf.write("\30\16\30\u00ca\13\30\3\31\3\31\3\32\3\32\3\32\5\32\u00d1")
        buf.write("\n\32\3\32\3\32\3\33\3\33\3\33\3\33\3\33\3\33\3\33\3\33")
        buf.write("\3\33\5\33\u00de\n\33\3\33\3\33\3\33\3\33\3\33\3\33\3")
        buf.write("\33\5\33\u00e7\n\33\3\33\3\33\3\33\3\33\3\33\3\33\3\33")
        buf.write("\3\33\3\33\3\33\5\33\u00f3\n\33\3\33\3\33\3\33\5\33\u00f8")
        buf.write("\n\33\7\33\u00fa\n\33\f\33\16\33\u00fd\13\33\3\34\5\34")
        buf.write("\u0100\n\34\3\34\3\34\3\35\3\35\3\35\3\35\3\35\3\35\3")
        buf.write("\35\3\35\3\35\7\35\u010d\n\35\f\35\16\35\u0110\13\35\3")
        buf.write("\35\3\35\5\35\u0114\n\35\3\36\3\36\3\37\3\37\3 \3 \3 ")
        buf.write("\3 \3 \3 \3 \3 \3 \3 \3 \3 \5 \u0126\n \3!\3!\3\"\3\"")
        buf.write("\3\"\3\"\3\"\7\"\u012f\n\"\f\"\16\"\u0132\13\"\3\"\3\"")
        buf.write("\3#\3#\3#\7#\u0139\n#\f#\16#\u013c\13#\3$\3$\3$\3$\3%")
        buf.write("\3%\3%\3%\5%\u0146\n%\3&\3&\3\'\3\'\3\'\3\'\7\'\u014e")
        buf.write("\n\'\f\'\16\'\u0151\13\'\3\'\3\'\3\'\3\'\5\'\u0157\n\'")
        buf.write("\3(\3(\5(\u015b\n(\3(\3(\3(\3)\3)\3)\3)\3*\3*\3+\3+\3")
        buf.write("+\3+\7+\u016a\n+\f+\16+\u016d\13+\3+\3+\3+\3+\5+\u0173")
        buf.write("\n+\3,\3,\3,\3,\3,\3,\3,\3,\3,\3,\3,\5,\u0180\n,\3,\2")
        buf.write("\4.\64-\2\4\6\b\n\f\16\20\22\24\26\30\32\34\36 \"$&(*")
        buf.write(",.\60\62\64\668:<>@BDFHJLNPRTV\2\n\4\2\26\26DD\4\2\27")
        buf.write("\30DD\3\2\32\33\4\2\37\37))\3\2\35\36\3\2\4\5\4\2\26\26")
        buf.write("HH\5\2\t\t\f\21\24\25\2\u0197\2[\3\2\2\2\4m\3\2\2\2\6")
        buf.write("q\3\2\2\2\bs\3\2\2\2\nv\3\2\2\2\fx\3\2\2\2\16}\3\2\2\2")
        buf.write("\20\u0080\3\2\2\2\22\u0085\3\2\2\2\24\u008d\3\2\2\2\26")
        buf.write("\u0090\3\2\2\2\30\u0093\3\2\2\2\32\u0096\3\2\2\2\34\u0099")
        buf.write("\3\2\2\2\36\u009d\3\2\2\2 \u00a2\3\2\2\2\"\u00a5\3\2\2")
        buf.write("\2$\u00af\3\2\2\2&\u00b1\3\2\2\2(\u00b3\3\2\2\2*\u00b5")
        buf.write("\3\2\2\2,\u00b7\3\2\2\2.\u00c0\3\2\2\2\60\u00cb\3\2\2")
        buf.write("\2\62\u00cd\3\2\2\2\64\u00d4\3\2\2\2\66\u00ff\3\2\2\2")
        buf.write("8\u0113\3\2\2\2:\u0115\3\2\2\2<\u0117\3\2\2\2>\u0125\3")
        buf.write("\2\2\2@\u0127\3\2\2\2B\u0129\3\2\2\2D\u0135\3\2\2\2F\u013d")
        buf.write("\3\2\2\2H\u0141\3\2\2\2J\u0147\3\2\2\2L\u0156\3\2\2\2")
        buf.write("N\u015a\3\2\2\2P\u015f\3\2\2\2R\u0163\3\2\2\2T\u0172\3")
        buf.write("\2\2\2V\u017f\3\2\2\2XZ\5\4\3\2YX\3\2\2\2Z]\3\2\2\2[Y")
        buf.write("\3\2\2\2[\\\3\2\2\2\\^\3\2\2\2][\3\2\2\2^_\7\2\2\3_\3")
        buf.write("\3\2\2\2`n\5\f\7\2an\5\16\b\2bn\5\20\t\2cn\5\22\n\2dn")
        buf.write("\5\24\13\2en\5\26\f\2fn\5\32\16\2gn\5\30\r\2hn\5\34\17")
        buf.write("\2in\5\36\20\2jn\5\"\22\2kn\5 \21\2ln\5\6\4\2m`\3\2\2")
        buf.write("\2ma\3\2\2\2mb\3\2\2\2mc\3\2\2\2md\3\2\2\2me\3\2\2\2m")
        buf.write("f\3\2\2\2mg\3\2\2\2mh\3\2\2\2mi\3\2\2\2mj\3\2\2\2mk\3")
        buf.write("\2\2\2ml\3\2\2\2no\3\2\2\2op\7\60\2\2p\5\3\2\2\2qr\7\3")
        buf.write("\2\2r\7\3\2\2\2st\7\7\2\2tu\5\n\6\2u\t\3\2\2\2vw\7D\2")
        buf.write("\2w\13\3\2\2\2xy\7\6\2\2y{\7D\2\2z|\5\b\5\2{z\3\2\2\2")
        buf.write("{|\3\2\2\2|\r\3\2\2\2}~\7\b\2\2~\177\7D\2\2\177\17\3\2")
        buf.write("\2\2\u0080\u0081\7\t\2\2\u0081\u0083\t\2\2\2\u0082\u0084")
        buf.write("\5\b\5\2\u0083\u0082\3\2\2\2\u0083\u0084\3\2\2\2\u0084")
        buf.write("\21\3\2\2\2\u0085\u0086\7\n\2\2\u0086\u0088\t\3\2\2\u0087")
        buf.write("\u0089\5\b\5\2\u0088\u0087\3\2\2\2\u0088\u0089\3\2\2\2")
        buf.write("\u0089\u008a\3\2\2\2\u008a\u008b\7\13\2\2\u008b\u008c")
        buf.write("\7H\2\2\u008c\23\3\2\2\2\u008d\u008e\7\f\2\2\u008e\u008f")
        buf.write("\5P)\2\u008f\25\3\2\2\2\u0090\u0091\7\r\2\2\u0091\u0092")
        buf.write("\5F$\2\u0092\27\3\2\2\2\u0093\u0094\7\17\2\2\u0094\u0095")
        buf.write("\5F$\2\u0095\31\3\2\2\2\u0096\u0097\7\16\2\2\u0097\u0098")
        buf.write("\5H%\2\u0098\33\3\2\2\2\u0099\u009a\7\20\2\2\u009a\u009b")
        buf.write("\5F$\2\u009b\35\3\2\2\2\u009c\u009e\7\4\2\2\u009d\u009c")
        buf.write("\3\2\2\2\u009d\u009e\3\2\2\2\u009e\u009f\3\2\2\2\u009f")
        buf.write("\u00a0\7\21\2\2\u00a0\u00a1\7H\2\2\u00a1\37\3\2\2\2\u00a2")
        buf.write("\u00a3\7\23\2\2\u00a3\u00a4\t\4\2\2\u00a4!\3\2\2\2\u00a5")
        buf.write("\u00a7\7\22\2\2\u00a6\u00a8\5&\24\2\u00a7\u00a6\3\2\2")
        buf.write("\2\u00a7\u00a8\3\2\2\2\u00a8\u00a9\3\2\2\2\u00a9\u00aa")
        buf.write("\5(\25\2\u00aa\u00ab\7\61\2\2\u00ab\u00ac\5$\23\2\u00ac")
        buf.write("#\3\2\2\2\u00ad\u00b0\5,\27\2\u00ae\u00b0\5*\26\2\u00af")
        buf.write("\u00ad\3\2\2\2\u00af\u00ae\3\2\2\2\u00b0%\3\2\2\2\u00b1")
        buf.write("\u00b2\7\5\2\2\u00b2\'\3\2\2\2\u00b3\u00b4\7H\2\2\u00b4")
        buf.write(")\3\2\2\2\u00b5\u00b6\5B\"\2\u00b6+\3\2\2\2\u00b7\u00b8")
        buf.write("\7\34\2\2\u00b8\u00b9\5.\30\2\u00b9-\3\2\2\2\u00ba\u00bb")
        buf.write("\b\30\1\2\u00bb\u00bc\5\60\31\2\u00bc\u00bd\5.\30\6\u00bd")
        buf.write("\u00c1\3\2\2\2\u00be\u00c1\5\62\32\2\u00bf\u00c1\5\64")
        buf.write("\33\2\u00c0\u00ba\3\2\2\2\u00c0\u00be\3\2\2\2\u00c0\u00bf")
        buf.write("\3\2\2\2\u00c1\u00c8\3\2\2\2\u00c2\u00c3\f\5\2\2\u00c3")
        buf.write("\u00c4\5<\37\2\u00c4\u00c5\5.\30\6\u00c5\u00c7\3\2\2\2")
        buf.write("\u00c6\u00c2\3\2\2\2\u00c7\u00ca\3\2\2\2\u00c8\u00c6\3")
        buf.write("\2\2\2\u00c8\u00c9\3\2\2\2\u00c9/\3\2\2\2\u00ca\u00c8")
        buf.write("\3\2\2\2\u00cb\u00cc\t\5\2\2\u00cc\61\3\2\2\2\u00cd\u00ce")
        buf.write("\5\64\33\2\u00ce\u00d0\7%\2\2\u00cf\u00d1\7\37\2\2\u00d0")
        buf.write("\u00cf\3\2\2\2\u00d0\u00d1\3\2\2\2\u00d1\u00d2\3\2\2\2")
        buf.write("\u00d2\u00d3\7@\2\2\u00d3\63\3\2\2\2\u00d4\u00d5\b\33")
        buf.write("\1\2\u00d5\u00d6\58\35\2\u00d6\u00fb\3\2\2\2\u00d7\u00d8")
        buf.write("\f\6\2\2\u00d8\u00d9\5> \2\u00d9\u00da\5\64\33\7\u00da")
        buf.write("\u00fa\3\2\2\2\u00db\u00dd\f\5\2\2\u00dc\u00de\7\37\2")
        buf.write("\2\u00dd\u00dc\3\2\2\2\u00dd\u00de\3\2\2\2\u00de\u00df")
        buf.write("\3\2\2\2\u00df\u00e0\7\'\2\2\u00e0\u00e1\5\64\33\2\u00e1")
        buf.write("\u00e2\7\35\2\2\u00e2\u00e3\5\64\33\6\u00e3\u00fa\3\2")
        buf.write("\2\2\u00e4\u00e6\f\b\2\2\u00e5\u00e7\7\37\2\2\u00e6\u00e5")
        buf.write("\3\2\2\2\u00e6\u00e7\3\2\2\2\u00e7\u00e8\3\2\2\2\u00e8")
        buf.write("\u00e9\7B\2\2\u00e9\u00ea\7\64\2\2\u00ea\u00eb\5.\30\2")
        buf.write("\u00eb\u00ec\7\65\2\2\u00ec\u00fa\3\2\2\2\u00ed\u00ee")
        buf.write("\f\7\2\2\u00ee\u00ef\7%\2\2\u00ef\u00fa\5\66\34\2\u00f0")
        buf.write("\u00f2\f\4\2\2\u00f1\u00f3\7\37\2\2\u00f2\u00f1\3\2\2")
        buf.write("\2\u00f2\u00f3\3\2\2\2\u00f3\u00f4\3\2\2\2\u00f4\u00f5")
        buf.write("\7&\2\2\u00f5\u00f7\5\64\33\2\u00f6\u00f8\7D\2\2\u00f7")
        buf.write("\u00f6\3\2\2\2\u00f7\u00f8\3\2\2\2\u00f8\u00fa\3\2\2\2")
        buf.write("\u00f9\u00d7\3\2\2\2\u00f9\u00db\3\2\2\2\u00f9\u00e4\3")
        buf.write("\2\2\2\u00f9\u00ed\3\2\2\2\u00f9\u00f0\3\2\2\2\u00fa\u00fd")
        buf.write("\3\2\2\2\u00fb\u00f9\3\2\2\2\u00fb\u00fc\3\2\2\2\u00fc")
        buf.write("\65\3\2\2\2\u00fd\u00fb\3\2\2\2\u00fe\u0100\7\37\2\2\u00ff")
        buf.write("\u00fe\3\2\2\2\u00ff\u0100\3\2\2\2\u0100\u0101\3\2\2\2")
        buf.write("\u0101\u0102\7A\2\2\u0102\67\3\2\2\2\u0103\u0114\5V,\2")
        buf.write("\u0104\u0114\5B\"\2\u0105\u0106\5:\36\2\u0106\u0107\5")
        buf.write("8\35\2\u0107\u0114\3\2\2\2\u0108\u0109\7\64\2\2\u0109")
        buf.write("\u010e\5.\30\2\u010a\u010b\7\63\2\2\u010b\u010d\5.\30")
        buf.write("\2\u010c\u010a\3\2\2\2\u010d\u0110\3\2\2\2\u010e\u010c")
        buf.write("\3\2\2\2\u010e\u010f\3\2\2\2\u010f\u0111\3\2\2\2\u0110")
        buf.write("\u010e\3\2\2\2\u0111\u0112\7\65\2\2\u0112\u0114\3\2\2")
        buf.write("\2\u0113\u0103\3\2\2\2\u0113\u0104\3\2\2\2\u0113\u0105")
        buf.write("\3\2\2\2\u0113\u0108\3\2\2\2\u01149\3\2\2\2\u0115\u0116")
        buf.write("\7\37\2\2\u0116;\3\2\2\2\u0117\u0118\t\6\2\2\u0118=\3")
        buf.write("\2\2\2\u0119\u0126\7 \2\2\u011a\u0126\7!\2\2\u011b\u0126")
        buf.write("\7#\2\2\u011c\u0126\7\"\2\2\u011d\u0126\7$\2\2\u011e\u011f")
        buf.write("\7(\2\2\u011f\u0126\7*\2\2\u0120\u0126\7+\2\2\u0121\u0126")
        buf.write("\7,\2\2\u0122\u0126\7-\2\2\u0123\u0126\7.\2\2\u0124\u0126")
        buf.write("\7/\2\2\u0125\u0119\3\2\2\2\u0125\u011a\3\2\2\2\u0125")
        buf.write("\u011b\3\2\2\2\u0125\u011c\3\2\2\2\u0125\u011d\3\2\2\2")
        buf.write("\u0125\u011e\3\2\2\2\u0125\u0120\3\2\2\2\u0125\u0121\3")
        buf.write("\2\2\2\u0125\u0122\3\2\2\2\u0125\u0123\3\2\2\2\u0125\u0124")
        buf.write("\3\2\2\2\u0126?\3\2\2\2\u0127\u0128\5V,\2\u0128A\3\2\2")
        buf.write("\2\u0129\u012a\5D#\2\u012a\u012b\7\64\2\2\u012b\u0130")
        buf.write("\5V,\2\u012c\u012d\7\63\2\2\u012d\u012f\5V,\2\u012e\u012c")
        buf.write("\3\2\2\2\u012f\u0132\3\2\2\2\u0130\u012e\3\2\2\2\u0130")
        buf.write("\u0131\3\2\2\2\u0131\u0133\3\2\2\2\u0132\u0130\3\2\2\2")
        buf.write("\u0133\u0134\7\65\2\2\u0134C\3\2\2\2\u0135\u013a\7H\2")
        buf.write("\2\u0136\u0137\7\62\2\2\u0137\u0139\7H\2\2\u0138\u0136")
        buf.write("\3\2\2\2\u0139\u013c\3\2\2\2\u013a\u0138\3\2\2\2\u013a")
        buf.write("\u013b\3\2\2\2\u013bE\3\2\2\2\u013c\u013a\3\2\2\2\u013d")
        buf.write("\u013e\7H\2\2\u013e\u013f\7\61\2\2\u013f\u0140\5B\"\2")
        buf.write("\u0140G\3\2\2\2\u0141\u0142\7H\2\2\u0142\u0145\7\61\2")
        buf.write("\2\u0143\u0146\5T+\2\u0144\u0146\7D\2\2\u0145\u0143\3")
        buf.write("\2\2\2\u0145\u0144\3\2\2\2\u0146I\3\2\2\2\u0147\u0148")
        buf.write("\t\7\2\2\u0148K\3\2\2\2\u0149\u014a\78\2\2\u014a\u014f")
        buf.write("\5N(\2\u014b\u014c\7\63\2\2\u014c\u014e\5N(\2\u014d\u014b")
        buf.write("\3\2\2\2\u014e\u0151\3\2\2\2\u014f\u014d\3\2\2\2\u014f")
        buf.write("\u0150\3\2\2\2\u0150\u0152\3\2\2\2\u0151\u014f\3\2\2\2")
        buf.write("\u0152\u0153\79\2\2\u0153\u0157\3\2\2\2\u0154\u0155\7")
        buf.write("8\2\2\u0155\u0157\79\2\2\u0156\u0149\3\2\2\2\u0156\u0154")
        buf.write("\3\2\2\2\u0157M\3\2\2\2\u0158\u015b\7D\2\2\u0159\u015b")
        buf.write("\5R*\2\u015a\u0158\3\2\2\2\u015a\u0159\3\2\2\2\u015b\u015c")
        buf.write("\3\2\2\2\u015c\u015d\7\61\2\2\u015d\u015e\5V,\2\u015e")
        buf.write("O\3\2\2\2\u015f\u0160\t\b\2\2\u0160\u0161\7\61\2\2\u0161")
        buf.write("\u0162\5V,\2\u0162Q\3\2\2\2\u0163\u0164\t\t\2\2\u0164")
        buf.write("S\3\2\2\2\u0165\u0166\7\66\2\2\u0166\u016b\5V,\2\u0167")
        buf.write("\u0168\7\63\2\2\u0168\u016a\5V,\2\u0169\u0167\3\2\2\2")
        buf.write("\u016a\u016d\3\2\2\2\u016b\u0169\3\2\2\2\u016b\u016c\3")
        buf.write("\2\2\2\u016c\u016e\3\2\2\2\u016d\u016b\3\2\2\2\u016e\u016f")
        buf.write("\7\67\2\2\u016f\u0173\3\2\2\2\u0170\u0171\7\66\2\2\u0171")
        buf.write("\u0173\7\67\2\2\u0172\u0165\3\2\2\2\u0172\u0170\3\2\2")
        buf.write("\2\u0173U\3\2\2\2\u0174\u0180\7D\2\2\u0175\u0180\7:\2")
        buf.write("\2\u0176\u0180\7>\2\2\u0177\u0180\5L\'\2\u0178\u0180\5")
        buf.write("T+\2\u0179\u0180\7@\2\2\u017a\u0180\7A\2\2\u017b\u0180")
        buf.write("\7\31\2\2\u017c\u0180\7H\2\2\u017d\u0180\5D#\2\u017e\u0180")
        buf.write("\7I\2\2\u017f\u0174\3\2\2\2\u017f\u0175\3\2\2\2\u017f")
        buf.write("\u0176\3\2\2\2\u017f\u0177\3\2\2\2\u017f\u0178\3\2\2\2")
        buf.write("\u017f\u0179\3\2\2\2\u017f\u017a\3\2\2\2\u017f\u017b\3")
        buf.write("\2\2\2\u017f\u017c\3\2\2\2\u017f\u017d\3\2\2\2\u017f\u017e")
        buf.write("\3\2\2\2\u0180W\3\2\2\2 [m{\u0083\u0088\u009d\u00a7\u00af")
        buf.write("\u00c0\u00c8\u00d0\u00dd\u00e6\u00f2\u00f7\u00f9\u00fb")
        buf.write("\u00ff\u010e\u0113\u0125\u0130\u013a\u0145\u014f\u0156")
        buf.write("\u015a\u016b\u0172\u017f")
        return buf.getvalue()


class nlpql_parserParser ( Parser ):

    grammarFileName = "nlpql_parser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'debug'", "'default'", "'final'", "'phenotype'", 
                     "'version'", "'description'", "'datamodel'", "'include'", 
                     "'called'", "'codesystem'", "'valueset'", "'termset'", 
                     "'documentset'", "'cohort'", "'population'", "'define'", 
                     "'context'", "'minimum_value'", "'maximum_value'", 
                     "'OMOP'", "'ClarityCore'", "'OHDSIHelpers'", "'All'", 
                     "'Patient'", "'Document'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'>'", "'<'", "'<='", "'>='", 
                     "'=='", "<INVALID>", "<INVALID>", "<INVALID>", "'!='", 
                     "'!'", "'+'", "'-'", "'*'", "'/'", "'^'", "'%'", "';'", 
                     "':'", "'.'", "','", "'('", "')'", "'['", "']'", "'{'", 
                     "'}'" ]

    symbolicNames = [ "<INVALID>", "DEBUG", "DEFAULT", "FINAL", "PHENOTYPE_NAME", 
                      "VERSION", "DESCRIPTION", "DATAMODEL", "INCLUDE", 
                      "CALLED", "CODE_SYSTEM", "VALUE_SET", "TERM_SET", 
                      "DOCUMENT_SET", "COHORT", "POPULATION", "DEFINE", 
                      "CONTEXT", "MIN_VALUE", "MAX_VALUE", "OMOP", "CLARITY_CORE", 
                      "OHDSI_HELPERS", "ALL", "PATIENT", "DOCUMENT", "WHERE", 
                      "AND", "OR", "NOT", "GT", "LT", "LTE", "GTE", "EQUAL", 
                      "IS", "LIKE", "BETWEEN", "NOT_EQUAL", "BANG", "PLUS", 
                      "MINUS", "MULT", "DIV", "CARET", "MOD", "SEMI", "COLON", 
                      "DOT", "COMMA", "L_PAREN", "R_PAREN", "L_BRACKET", 
                      "R_BRACKET", "L_CURLY", "R_CURLY", "DECIMAL", "HEX", 
                      "OCT", "BINARY", "FLOAT", "HEX_FLOAT", "BOOL", "NULL", 
                      "IN", "CHAR", "STRING", "WS", "COMMENT", "LINE_COMMENT", 
                      "IDENTIFIER", "TIME" ]

    RULE_validExpression = 0
    RULE_statement = 1
    RULE_debugger = 2
    RULE_version = 3
    RULE_versionValue = 4
    RULE_phenotypeName = 5
    RULE_description = 6
    RULE_dataModel = 7
    RULE_include = 8
    RULE_codeSystem = 9
    RULE_valueSet = 10
    RULE_documentSet = 11
    RULE_termSet = 12
    RULE_cohort = 13
    RULE_population = 14
    RULE_context = 15
    RULE_define = 16
    RULE_defineSubject = 17
    RULE_finalModifier = 18
    RULE_defineName = 19
    RULE_dataEntity = 20
    RULE_operation = 21
    RULE_expression = 22
    RULE_notOperator = 23
    RULE_predicateBoolean = 24
    RULE_predicate = 25
    RULE_nullNotnull = 26
    RULE_expressionAtom = 27
    RULE_unaryOperator = 28
    RULE_logicalOperator = 29
    RULE_comparisonOperator = 30
    RULE_operand = 31
    RULE_methodCall = 32
    RULE_qualifiedName = 33
    RULE_pairMethod = 34
    RULE_pairArray = 35
    RULE_modifiers = 36
    RULE_obj = 37
    RULE_pair = 38
    RULE_identifierPair = 39
    RULE_named = 40
    RULE_array = 41
    RULE_value = 42

    ruleNames =  [ "validExpression", "statement", "debugger", "version", 
                   "versionValue", "phenotypeName", "description", "dataModel", 
                   "include", "codeSystem", "valueSet", "documentSet", "termSet", 
                   "cohort", "population", "context", "define", "defineSubject", 
                   "finalModifier", "defineName", "dataEntity", "operation", 
                   "expression", "notOperator", "predicateBoolean", "predicate", 
                   "nullNotnull", "expressionAtom", "unaryOperator", "logicalOperator", 
                   "comparisonOperator", "operand", "methodCall", "qualifiedName", 
                   "pairMethod", "pairArray", "modifiers", "obj", "pair", 
                   "identifierPair", "named", "array", "value" ]

    EOF = Token.EOF
    DEBUG=1
    DEFAULT=2
    FINAL=3
    PHENOTYPE_NAME=4
    VERSION=5
    DESCRIPTION=6
    DATAMODEL=7
    INCLUDE=8
    CALLED=9
    CODE_SYSTEM=10
    VALUE_SET=11
    TERM_SET=12
    DOCUMENT_SET=13
    COHORT=14
    POPULATION=15
    DEFINE=16
    CONTEXT=17
    MIN_VALUE=18
    MAX_VALUE=19
    OMOP=20
    CLARITY_CORE=21
    OHDSI_HELPERS=22
    ALL=23
    PATIENT=24
    DOCUMENT=25
    WHERE=26
    AND=27
    OR=28
    NOT=29
    GT=30
    LT=31
    LTE=32
    GTE=33
    EQUAL=34
    IS=35
    LIKE=36
    BETWEEN=37
    NOT_EQUAL=38
    BANG=39
    PLUS=40
    MINUS=41
    MULT=42
    DIV=43
    CARET=44
    MOD=45
    SEMI=46
    COLON=47
    DOT=48
    COMMA=49
    L_PAREN=50
    R_PAREN=51
    L_BRACKET=52
    R_BRACKET=53
    L_CURLY=54
    R_CURLY=55
    DECIMAL=56
    HEX=57
    OCT=58
    BINARY=59
    FLOAT=60
    HEX_FLOAT=61
    BOOL=62
    NULL=63
    IN=64
    CHAR=65
    STRING=66
    WS=67
    COMMENT=68
    LINE_COMMENT=69
    IDENTIFIER=70
    TIME=71

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
            self.state = 89
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << nlpql_parserParser.DEBUG) | (1 << nlpql_parserParser.DEFAULT) | (1 << nlpql_parserParser.PHENOTYPE_NAME) | (1 << nlpql_parserParser.DESCRIPTION) | (1 << nlpql_parserParser.DATAMODEL) | (1 << nlpql_parserParser.INCLUDE) | (1 << nlpql_parserParser.CODE_SYSTEM) | (1 << nlpql_parserParser.VALUE_SET) | (1 << nlpql_parserParser.TERM_SET) | (1 << nlpql_parserParser.DOCUMENT_SET) | (1 << nlpql_parserParser.COHORT) | (1 << nlpql_parserParser.POPULATION) | (1 << nlpql_parserParser.DEFINE) | (1 << nlpql_parserParser.CONTEXT))) != 0):
                self.state = 86
                self.statement()
                self.state = 91
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 92
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


        def documentSet(self):
            return self.getTypedRuleContext(nlpql_parserParser.DocumentSetContext,0)


        def cohort(self):
            return self.getTypedRuleContext(nlpql_parserParser.CohortContext,0)


        def population(self):
            return self.getTypedRuleContext(nlpql_parserParser.PopulationContext,0)


        def define(self):
            return self.getTypedRuleContext(nlpql_parserParser.DefineContext,0)


        def context(self):
            return self.getTypedRuleContext(nlpql_parserParser.ContextContext,0)


        def debugger(self):
            return self.getTypedRuleContext(nlpql_parserParser.DebuggerContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_statement




    def statement(self):

        localctx = nlpql_parserParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_statement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 107
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [nlpql_parserParser.PHENOTYPE_NAME]:
                self.state = 94
                self.phenotypeName()
                pass
            elif token in [nlpql_parserParser.DESCRIPTION]:
                self.state = 95
                self.description()
                pass
            elif token in [nlpql_parserParser.DATAMODEL]:
                self.state = 96
                self.dataModel()
                pass
            elif token in [nlpql_parserParser.INCLUDE]:
                self.state = 97
                self.include()
                pass
            elif token in [nlpql_parserParser.CODE_SYSTEM]:
                self.state = 98
                self.codeSystem()
                pass
            elif token in [nlpql_parserParser.VALUE_SET]:
                self.state = 99
                self.valueSet()
                pass
            elif token in [nlpql_parserParser.TERM_SET]:
                self.state = 100
                self.termSet()
                pass
            elif token in [nlpql_parserParser.DOCUMENT_SET]:
                self.state = 101
                self.documentSet()
                pass
            elif token in [nlpql_parserParser.COHORT]:
                self.state = 102
                self.cohort()
                pass
            elif token in [nlpql_parserParser.DEFAULT, nlpql_parserParser.POPULATION]:
                self.state = 103
                self.population()
                pass
            elif token in [nlpql_parserParser.DEFINE]:
                self.state = 104
                self.define()
                pass
            elif token in [nlpql_parserParser.CONTEXT]:
                self.state = 105
                self.context()
                pass
            elif token in [nlpql_parserParser.DEBUG]:
                self.state = 106
                self.debugger()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 109
            self.match(nlpql_parserParser.SEMI)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DebuggerContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DEBUG(self):
            return self.getToken(nlpql_parserParser.DEBUG, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_debugger




    def debugger(self):

        localctx = nlpql_parserParser.DebuggerContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_debugger)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 111
            self.match(nlpql_parserParser.DEBUG)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class VersionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def VERSION(self):
            return self.getToken(nlpql_parserParser.VERSION, 0)

        def versionValue(self):
            return self.getTypedRuleContext(nlpql_parserParser.VersionValueContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_version




    def version(self):

        localctx = nlpql_parserParser.VersionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_version)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 113
            self.match(nlpql_parserParser.VERSION)
            self.state = 114
            self.versionValue()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class VersionValueContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(nlpql_parserParser.STRING, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_versionValue




    def versionValue(self):

        localctx = nlpql_parserParser.VersionValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_versionValue)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 116
            self.match(nlpql_parserParser.STRING)
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

        def STRING(self):
            return self.getToken(nlpql_parserParser.STRING, 0)

        def version(self):
            return self.getTypedRuleContext(nlpql_parserParser.VersionContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_phenotypeName




    def phenotypeName(self):

        localctx = nlpql_parserParser.PhenotypeNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_phenotypeName)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 118
            self.match(nlpql_parserParser.PHENOTYPE_NAME)
            self.state = 119
            self.match(nlpql_parserParser.STRING)
            self.state = 121
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.VERSION:
                self.state = 120
                self.version()


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

        def STRING(self):
            return self.getToken(nlpql_parserParser.STRING, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_description




    def description(self):

        localctx = nlpql_parserParser.DescriptionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_description)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 123
            self.match(nlpql_parserParser.DESCRIPTION)
            self.state = 124
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

        def STRING(self):
            return self.getToken(nlpql_parserParser.STRING, 0)

        def version(self):
            return self.getTypedRuleContext(nlpql_parserParser.VersionContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_dataModel




    def dataModel(self):

        localctx = nlpql_parserParser.DataModelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_dataModel)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 126
            self.match(nlpql_parserParser.DATAMODEL)
            self.state = 127
            _la = self._input.LA(1)
            if not(_la==nlpql_parserParser.OMOP or _la==nlpql_parserParser.STRING):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 129
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.VERSION:
                self.state = 128
                self.version()


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

        def STRING(self):
            return self.getToken(nlpql_parserParser.STRING, 0)

        def version(self):
            return self.getTypedRuleContext(nlpql_parserParser.VersionContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_include




    def include(self):

        localctx = nlpql_parserParser.IncludeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_include)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 131
            self.match(nlpql_parserParser.INCLUDE)
            self.state = 132
            _la = self._input.LA(1)
            if not(((((_la - 21)) & ~0x3f) == 0 and ((1 << (_la - 21)) & ((1 << (nlpql_parserParser.CLARITY_CORE - 21)) | (1 << (nlpql_parserParser.OHDSI_HELPERS - 21)) | (1 << (nlpql_parserParser.STRING - 21)))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 134
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.VERSION:
                self.state = 133
                self.version()


            self.state = 136
            self.match(nlpql_parserParser.CALLED)
            self.state = 137
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

        def identifierPair(self):
            return self.getTypedRuleContext(nlpql_parserParser.IdentifierPairContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_codeSystem




    def codeSystem(self):

        localctx = nlpql_parserParser.CodeSystemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_codeSystem)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 139
            self.match(nlpql_parserParser.CODE_SYSTEM)
            self.state = 140
            self.identifierPair()
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

        def pairMethod(self):
            return self.getTypedRuleContext(nlpql_parserParser.PairMethodContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_valueSet




    def valueSet(self):

        localctx = nlpql_parserParser.ValueSetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_valueSet)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 142
            self.match(nlpql_parserParser.VALUE_SET)
            self.state = 143
            self.pairMethod()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DocumentSetContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DOCUMENT_SET(self):
            return self.getToken(nlpql_parserParser.DOCUMENT_SET, 0)

        def pairMethod(self):
            return self.getTypedRuleContext(nlpql_parserParser.PairMethodContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_documentSet




    def documentSet(self):

        localctx = nlpql_parserParser.DocumentSetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_documentSet)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 145
            self.match(nlpql_parserParser.DOCUMENT_SET)
            self.state = 146
            self.pairMethod()
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

        def pairArray(self):
            return self.getTypedRuleContext(nlpql_parserParser.PairArrayContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_termSet




    def termSet(self):

        localctx = nlpql_parserParser.TermSetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_termSet)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 148
            self.match(nlpql_parserParser.TERM_SET)
            self.state = 149
            self.pairArray()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class CohortContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COHORT(self):
            return self.getToken(nlpql_parserParser.COHORT, 0)

        def pairMethod(self):
            return self.getTypedRuleContext(nlpql_parserParser.PairMethodContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_cohort




    def cohort(self):

        localctx = nlpql_parserParser.CohortContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_cohort)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 151
            self.match(nlpql_parserParser.COHORT)
            self.state = 152
            self.pairMethod()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PopulationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def POPULATION(self):
            return self.getToken(nlpql_parserParser.POPULATION, 0)

        def IDENTIFIER(self):
            return self.getToken(nlpql_parserParser.IDENTIFIER, 0)

        def DEFAULT(self):
            return self.getToken(nlpql_parserParser.DEFAULT, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_population




    def population(self):

        localctx = nlpql_parserParser.PopulationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_population)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 155
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.DEFAULT:
                self.state = 154
                self.match(nlpql_parserParser.DEFAULT)


            self.state = 157
            self.match(nlpql_parserParser.POPULATION)
            self.state = 158
            self.match(nlpql_parserParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ContextContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONTEXT(self):
            return self.getToken(nlpql_parserParser.CONTEXT, 0)

        def PATIENT(self):
            return self.getToken(nlpql_parserParser.PATIENT, 0)

        def DOCUMENT(self):
            return self.getToken(nlpql_parserParser.DOCUMENT, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_context




    def context(self):

        localctx = nlpql_parserParser.ContextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_context)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 160
            self.match(nlpql_parserParser.CONTEXT)
            self.state = 161
            _la = self._input.LA(1)
            if not(_la==nlpql_parserParser.PATIENT or _la==nlpql_parserParser.DOCUMENT):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DefineContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DEFINE(self):
            return self.getToken(nlpql_parserParser.DEFINE, 0)

        def defineName(self):
            return self.getTypedRuleContext(nlpql_parserParser.DefineNameContext,0)


        def COLON(self):
            return self.getToken(nlpql_parserParser.COLON, 0)

        def defineSubject(self):
            return self.getTypedRuleContext(nlpql_parserParser.DefineSubjectContext,0)


        def finalModifier(self):
            return self.getTypedRuleContext(nlpql_parserParser.FinalModifierContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_define




    def define(self):

        localctx = nlpql_parserParser.DefineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_define)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 163
            self.match(nlpql_parserParser.DEFINE)
            self.state = 165
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.FINAL:
                self.state = 164
                self.finalModifier()


            self.state = 167
            self.defineName()
            self.state = 168
            self.match(nlpql_parserParser.COLON)
            self.state = 169
            self.defineSubject()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DefineSubjectContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def operation(self):
            return self.getTypedRuleContext(nlpql_parserParser.OperationContext,0)


        def dataEntity(self):
            return self.getTypedRuleContext(nlpql_parserParser.DataEntityContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_defineSubject




    def defineSubject(self):

        localctx = nlpql_parserParser.DefineSubjectContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_defineSubject)
        try:
            self.state = 173
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [nlpql_parserParser.WHERE]:
                self.enterOuterAlt(localctx, 1)
                self.state = 171
                self.operation()
                pass
            elif token in [nlpql_parserParser.IDENTIFIER]:
                self.enterOuterAlt(localctx, 2)
                self.state = 172
                self.dataEntity()
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

    class FinalModifierContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FINAL(self):
            return self.getToken(nlpql_parserParser.FINAL, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_finalModifier




    def finalModifier(self):

        localctx = nlpql_parserParser.FinalModifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_finalModifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 175
            self.match(nlpql_parserParser.FINAL)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DefineNameContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(nlpql_parserParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_defineName




    def defineName(self):

        localctx = nlpql_parserParser.DefineNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_defineName)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 177
            self.match(nlpql_parserParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DataEntityContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def methodCall(self):
            return self.getTypedRuleContext(nlpql_parserParser.MethodCallContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_dataEntity




    def dataEntity(self):

        localctx = nlpql_parserParser.DataEntityContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_dataEntity)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 179
            self.methodCall()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class OperationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHERE(self):
            return self.getToken(nlpql_parserParser.WHERE, 0)

        def expression(self):
            return self.getTypedRuleContext(nlpql_parserParser.ExpressionContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_operation




    def operation(self):

        localctx = nlpql_parserParser.OperationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_operation)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 181
            self.match(nlpql_parserParser.WHERE)
            self.state = 182
            self.expression(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ExpressionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def notOperator(self):
            return self.getTypedRuleContext(nlpql_parserParser.NotOperatorContext,0)


        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(nlpql_parserParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(nlpql_parserParser.ExpressionContext,i)


        def predicateBoolean(self):
            return self.getTypedRuleContext(nlpql_parserParser.PredicateBooleanContext,0)


        def predicate(self):
            return self.getTypedRuleContext(nlpql_parserParser.PredicateContext,0)


        def logicalOperator(self):
            return self.getTypedRuleContext(nlpql_parserParser.LogicalOperatorContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_expression



    def expression(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = nlpql_parserParser.ExpressionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 44
        self.enterRecursionRule(localctx, 44, self.RULE_expression, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 190
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,8,self._ctx)
            if la_ == 1:
                self.state = 185
                self.notOperator()
                self.state = 186
                self.expression(4)
                pass

            elif la_ == 2:
                self.state = 188
                self.predicateBoolean()
                pass

            elif la_ == 3:
                self.state = 189
                self.predicate(0)
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 198
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,9,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = nlpql_parserParser.ExpressionContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                    self.state = 192
                    if not self.precpred(self._ctx, 3):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                    self.state = 193
                    self.logicalOperator()
                    self.state = 194
                    self.expression(4) 
                self.state = 200
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,9,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx

    class NotOperatorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NOT(self):
            return self.getToken(nlpql_parserParser.NOT, 0)

        def BANG(self):
            return self.getToken(nlpql_parserParser.BANG, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_notOperator




    def notOperator(self):

        localctx = nlpql_parserParser.NotOperatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_notOperator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 201
            _la = self._input.LA(1)
            if not(_la==nlpql_parserParser.NOT or _la==nlpql_parserParser.BANG):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PredicateBooleanContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def predicate(self):
            return self.getTypedRuleContext(nlpql_parserParser.PredicateContext,0)


        def IS(self):
            return self.getToken(nlpql_parserParser.IS, 0)

        def BOOL(self):
            return self.getToken(nlpql_parserParser.BOOL, 0)

        def NOT(self):
            return self.getToken(nlpql_parserParser.NOT, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_predicateBoolean




    def predicateBoolean(self):

        localctx = nlpql_parserParser.PredicateBooleanContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_predicateBoolean)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 203
            self.predicate(0)
            self.state = 204
            self.match(nlpql_parserParser.IS)
            self.state = 206
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.NOT:
                self.state = 205
                self.match(nlpql_parserParser.NOT)


            self.state = 208
            self.match(nlpql_parserParser.BOOL)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PredicateContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.left = None # PredicateContext
            self.right = None # PredicateContext

        def expressionAtom(self):
            return self.getTypedRuleContext(nlpql_parserParser.ExpressionAtomContext,0)


        def comparisonOperator(self):
            return self.getTypedRuleContext(nlpql_parserParser.ComparisonOperatorContext,0)


        def predicate(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(nlpql_parserParser.PredicateContext)
            else:
                return self.getTypedRuleContext(nlpql_parserParser.PredicateContext,i)


        def BETWEEN(self):
            return self.getToken(nlpql_parserParser.BETWEEN, 0)

        def AND(self):
            return self.getToken(nlpql_parserParser.AND, 0)

        def NOT(self):
            return self.getToken(nlpql_parserParser.NOT, 0)

        def IN(self):
            return self.getToken(nlpql_parserParser.IN, 0)

        def L_PAREN(self):
            return self.getToken(nlpql_parserParser.L_PAREN, 0)

        def R_PAREN(self):
            return self.getToken(nlpql_parserParser.R_PAREN, 0)

        def expression(self):
            return self.getTypedRuleContext(nlpql_parserParser.ExpressionContext,0)


        def IS(self):
            return self.getToken(nlpql_parserParser.IS, 0)

        def nullNotnull(self):
            return self.getTypedRuleContext(nlpql_parserParser.NullNotnullContext,0)


        def LIKE(self):
            return self.getToken(nlpql_parserParser.LIKE, 0)

        def STRING(self):
            return self.getToken(nlpql_parserParser.STRING, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_predicate



    def predicate(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = nlpql_parserParser.PredicateContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 50
        self.enterRecursionRule(localctx, 50, self.RULE_predicate, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 211
            self.expressionAtom()
            self._ctx.stop = self._input.LT(-1)
            self.state = 249
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,16,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 247
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,15,self._ctx)
                    if la_ == 1:
                        localctx = nlpql_parserParser.PredicateContext(self, _parentctx, _parentState)
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_predicate)
                        self.state = 213
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 214
                        self.comparisonOperator()
                        self.state = 215
                        localctx.right = self.predicate(5)
                        pass

                    elif la_ == 2:
                        localctx = nlpql_parserParser.PredicateContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_predicate)
                        self.state = 217
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 219
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if _la==nlpql_parserParser.NOT:
                            self.state = 218
                            self.match(nlpql_parserParser.NOT)


                        self.state = 221
                        self.match(nlpql_parserParser.BETWEEN)
                        self.state = 222
                        self.predicate(0)
                        self.state = 223
                        self.match(nlpql_parserParser.AND)
                        self.state = 224
                        self.predicate(4)
                        pass

                    elif la_ == 3:
                        localctx = nlpql_parserParser.PredicateContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_predicate)
                        self.state = 226
                        if not self.precpred(self._ctx, 6):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 6)")
                        self.state = 228
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if _la==nlpql_parserParser.NOT:
                            self.state = 227
                            self.match(nlpql_parserParser.NOT)


                        self.state = 230
                        self.match(nlpql_parserParser.IN)
                        self.state = 231
                        self.match(nlpql_parserParser.L_PAREN)

                        self.state = 232
                        self.expression(0)
                        self.state = 233
                        self.match(nlpql_parserParser.R_PAREN)
                        pass

                    elif la_ == 4:
                        localctx = nlpql_parserParser.PredicateContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_predicate)
                        self.state = 235
                        if not self.precpred(self._ctx, 5):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 5)")
                        self.state = 236
                        self.match(nlpql_parserParser.IS)
                        self.state = 237
                        self.nullNotnull()
                        pass

                    elif la_ == 5:
                        localctx = nlpql_parserParser.PredicateContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_predicate)
                        self.state = 238
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 240
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if _la==nlpql_parserParser.NOT:
                            self.state = 239
                            self.match(nlpql_parserParser.NOT)


                        self.state = 242
                        self.match(nlpql_parserParser.LIKE)
                        self.state = 243
                        self.predicate(0)
                        self.state = 245
                        self._errHandler.sync(self)
                        la_ = self._interp.adaptivePredict(self._input,14,self._ctx)
                        if la_ == 1:
                            self.state = 244
                            self.match(nlpql_parserParser.STRING)


                        pass

             
                self.state = 251
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,16,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx

    class NullNotnullContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NULL(self):
            return self.getToken(nlpql_parserParser.NULL, 0)

        def NOT(self):
            return self.getToken(nlpql_parserParser.NOT, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_nullNotnull




    def nullNotnull(self):

        localctx = nlpql_parserParser.NullNotnullContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_nullNotnull)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 253
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.NOT:
                self.state = 252
                self.match(nlpql_parserParser.NOT)


            self.state = 255
            self.match(nlpql_parserParser.NULL)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ExpressionAtomContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def value(self):
            return self.getTypedRuleContext(nlpql_parserParser.ValueContext,0)


        def methodCall(self):
            return self.getTypedRuleContext(nlpql_parserParser.MethodCallContext,0)


        def unaryOperator(self):
            return self.getTypedRuleContext(nlpql_parserParser.UnaryOperatorContext,0)


        def expressionAtom(self):
            return self.getTypedRuleContext(nlpql_parserParser.ExpressionAtomContext,0)


        def L_PAREN(self):
            return self.getToken(nlpql_parserParser.L_PAREN, 0)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(nlpql_parserParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(nlpql_parserParser.ExpressionContext,i)


        def R_PAREN(self):
            return self.getToken(nlpql_parserParser.R_PAREN, 0)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(nlpql_parserParser.COMMA)
            else:
                return self.getToken(nlpql_parserParser.COMMA, i)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_expressionAtom




    def expressionAtom(self):

        localctx = nlpql_parserParser.ExpressionAtomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_expressionAtom)
        self._la = 0 # Token type
        try:
            self.state = 273
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,19,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 257
                self.value()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 258
                self.methodCall()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 259
                self.unaryOperator()
                self.state = 260
                self.expressionAtom()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 262
                self.match(nlpql_parserParser.L_PAREN)
                self.state = 263
                self.expression(0)
                self.state = 268
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==nlpql_parserParser.COMMA:
                    self.state = 264
                    self.match(nlpql_parserParser.COMMA)
                    self.state = 265
                    self.expression(0)
                    self.state = 270
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 271
                self.match(nlpql_parserParser.R_PAREN)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class UnaryOperatorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NOT(self):
            return self.getToken(nlpql_parserParser.NOT, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_unaryOperator




    def unaryOperator(self):

        localctx = nlpql_parserParser.UnaryOperatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_unaryOperator)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 275
            self.match(nlpql_parserParser.NOT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class LogicalOperatorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def AND(self):
            return self.getToken(nlpql_parserParser.AND, 0)

        def OR(self):
            return self.getToken(nlpql_parserParser.OR, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_logicalOperator




    def logicalOperator(self):

        localctx = nlpql_parserParser.LogicalOperatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_logicalOperator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 277
            _la = self._input.LA(1)
            if not(_la==nlpql_parserParser.AND or _la==nlpql_parserParser.OR):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ComparisonOperatorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def GT(self):
            return self.getToken(nlpql_parserParser.GT, 0)

        def LT(self):
            return self.getToken(nlpql_parserParser.LT, 0)

        def GTE(self):
            return self.getToken(nlpql_parserParser.GTE, 0)

        def LTE(self):
            return self.getToken(nlpql_parserParser.LTE, 0)

        def EQUAL(self):
            return self.getToken(nlpql_parserParser.EQUAL, 0)

        def NOT_EQUAL(self):
            return self.getToken(nlpql_parserParser.NOT_EQUAL, 0)

        def PLUS(self):
            return self.getToken(nlpql_parserParser.PLUS, 0)

        def MINUS(self):
            return self.getToken(nlpql_parserParser.MINUS, 0)

        def MULT(self):
            return self.getToken(nlpql_parserParser.MULT, 0)

        def DIV(self):
            return self.getToken(nlpql_parserParser.DIV, 0)

        def CARET(self):
            return self.getToken(nlpql_parserParser.CARET, 0)

        def MOD(self):
            return self.getToken(nlpql_parserParser.MOD, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_comparisonOperator




    def comparisonOperator(self):

        localctx = nlpql_parserParser.ComparisonOperatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_comparisonOperator)
        try:
            self.state = 291
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [nlpql_parserParser.GT]:
                self.enterOuterAlt(localctx, 1)
                self.state = 279
                self.match(nlpql_parserParser.GT)
                pass
            elif token in [nlpql_parserParser.LT]:
                self.enterOuterAlt(localctx, 2)
                self.state = 280
                self.match(nlpql_parserParser.LT)
                pass
            elif token in [nlpql_parserParser.GTE]:
                self.enterOuterAlt(localctx, 3)
                self.state = 281
                self.match(nlpql_parserParser.GTE)
                pass
            elif token in [nlpql_parserParser.LTE]:
                self.enterOuterAlt(localctx, 4)
                self.state = 282
                self.match(nlpql_parserParser.LTE)
                pass
            elif token in [nlpql_parserParser.EQUAL]:
                self.enterOuterAlt(localctx, 5)
                self.state = 283
                self.match(nlpql_parserParser.EQUAL)
                pass
            elif token in [nlpql_parserParser.NOT_EQUAL]:
                self.enterOuterAlt(localctx, 6)
                self.state = 284
                self.match(nlpql_parserParser.NOT_EQUAL)
                self.state = 285
                self.match(nlpql_parserParser.PLUS)
                pass
            elif token in [nlpql_parserParser.MINUS]:
                self.enterOuterAlt(localctx, 7)
                self.state = 286
                self.match(nlpql_parserParser.MINUS)
                pass
            elif token in [nlpql_parserParser.MULT]:
                self.enterOuterAlt(localctx, 8)
                self.state = 287
                self.match(nlpql_parserParser.MULT)
                pass
            elif token in [nlpql_parserParser.DIV]:
                self.enterOuterAlt(localctx, 9)
                self.state = 288
                self.match(nlpql_parserParser.DIV)
                pass
            elif token in [nlpql_parserParser.CARET]:
                self.enterOuterAlt(localctx, 10)
                self.state = 289
                self.match(nlpql_parserParser.CARET)
                pass
            elif token in [nlpql_parserParser.MOD]:
                self.enterOuterAlt(localctx, 11)
                self.state = 290
                self.match(nlpql_parserParser.MOD)
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

    class OperandContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def value(self):
            return self.getTypedRuleContext(nlpql_parserParser.ValueContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_operand




    def operand(self):

        localctx = nlpql_parserParser.OperandContext(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_operand)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 293
            self.value()
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

        def qualifiedName(self):
            return self.getTypedRuleContext(nlpql_parserParser.QualifiedNameContext,0)


        def L_PAREN(self):
            return self.getToken(nlpql_parserParser.L_PAREN, 0)

        def value(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(nlpql_parserParser.ValueContext)
            else:
                return self.getTypedRuleContext(nlpql_parserParser.ValueContext,i)


        def R_PAREN(self):
            return self.getToken(nlpql_parserParser.R_PAREN, 0)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(nlpql_parserParser.COMMA)
            else:
                return self.getToken(nlpql_parserParser.COMMA, i)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_methodCall




    def methodCall(self):

        localctx = nlpql_parserParser.MethodCallContext(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_methodCall)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 295
            self.qualifiedName()
            self.state = 296
            self.match(nlpql_parserParser.L_PAREN)
            self.state = 297
            self.value()
            self.state = 302
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==nlpql_parserParser.COMMA:
                self.state = 298
                self.match(nlpql_parserParser.COMMA)
                self.state = 299
                self.value()
                self.state = 304
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 305
            self.match(nlpql_parserParser.R_PAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class QualifiedNameContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self, i:int=None):
            if i is None:
                return self.getTokens(nlpql_parserParser.IDENTIFIER)
            else:
                return self.getToken(nlpql_parserParser.IDENTIFIER, i)

        def DOT(self, i:int=None):
            if i is None:
                return self.getTokens(nlpql_parserParser.DOT)
            else:
                return self.getToken(nlpql_parserParser.DOT, i)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_qualifiedName




    def qualifiedName(self):

        localctx = nlpql_parserParser.QualifiedNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 66, self.RULE_qualifiedName)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 307
            self.match(nlpql_parserParser.IDENTIFIER)
            self.state = 312
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,22,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 308
                    self.match(nlpql_parserParser.DOT)
                    self.state = 309
                    self.match(nlpql_parserParser.IDENTIFIER) 
                self.state = 314
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,22,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PairMethodContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(nlpql_parserParser.IDENTIFIER, 0)

        def COLON(self):
            return self.getToken(nlpql_parserParser.COLON, 0)

        def methodCall(self):
            return self.getTypedRuleContext(nlpql_parserParser.MethodCallContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_pairMethod




    def pairMethod(self):

        localctx = nlpql_parserParser.PairMethodContext(self, self._ctx, self.state)
        self.enterRule(localctx, 68, self.RULE_pairMethod)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 315
            self.match(nlpql_parserParser.IDENTIFIER)
            self.state = 316
            self.match(nlpql_parserParser.COLON)
            self.state = 317
            self.methodCall()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PairArrayContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(nlpql_parserParser.IDENTIFIER, 0)

        def COLON(self):
            return self.getToken(nlpql_parserParser.COLON, 0)

        def array(self):
            return self.getTypedRuleContext(nlpql_parserParser.ArrayContext,0)


        def STRING(self):
            return self.getToken(nlpql_parserParser.STRING, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_pairArray




    def pairArray(self):

        localctx = nlpql_parserParser.PairArrayContext(self, self._ctx, self.state)
        self.enterRule(localctx, 70, self.RULE_pairArray)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 319
            self.match(nlpql_parserParser.IDENTIFIER)
            self.state = 320
            self.match(nlpql_parserParser.COLON)
            self.state = 323
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [nlpql_parserParser.L_BRACKET]:
                self.state = 321
                self.array()
                pass
            elif token in [nlpql_parserParser.STRING]:
                self.state = 322
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

    class ModifiersContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DEFAULT(self):
            return self.getToken(nlpql_parserParser.DEFAULT, 0)

        def FINAL(self):
            return self.getToken(nlpql_parserParser.FINAL, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_modifiers




    def modifiers(self):

        localctx = nlpql_parserParser.ModifiersContext(self, self._ctx, self.state)
        self.enterRule(localctx, 72, self.RULE_modifiers)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 325
            _la = self._input.LA(1)
            if not(_la==nlpql_parserParser.DEFAULT or _la==nlpql_parserParser.FINAL):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
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
        self.enterRule(localctx, 74, self.RULE_obj)
        self._la = 0 # Token type
        try:
            self.state = 340
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,25,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 327
                self.match(nlpql_parserParser.L_CURLY)
                self.state = 328
                self.pair()
                self.state = 333
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==nlpql_parserParser.COMMA:
                    self.state = 329
                    self.match(nlpql_parserParser.COMMA)
                    self.state = 330
                    self.pair()
                    self.state = 335
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 336
                self.match(nlpql_parserParser.R_CURLY)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 338
                self.match(nlpql_parserParser.L_CURLY)
                self.state = 339
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

        def COLON(self):
            return self.getToken(nlpql_parserParser.COLON, 0)

        def value(self):
            return self.getTypedRuleContext(nlpql_parserParser.ValueContext,0)


        def STRING(self):
            return self.getToken(nlpql_parserParser.STRING, 0)

        def named(self):
            return self.getTypedRuleContext(nlpql_parserParser.NamedContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_pair




    def pair(self):

        localctx = nlpql_parserParser.PairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 76, self.RULE_pair)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 344
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [nlpql_parserParser.STRING]:
                self.state = 342
                self.match(nlpql_parserParser.STRING)
                pass
            elif token in [nlpql_parserParser.DATAMODEL, nlpql_parserParser.CODE_SYSTEM, nlpql_parserParser.VALUE_SET, nlpql_parserParser.TERM_SET, nlpql_parserParser.DOCUMENT_SET, nlpql_parserParser.COHORT, nlpql_parserParser.POPULATION, nlpql_parserParser.MIN_VALUE, nlpql_parserParser.MAX_VALUE]:
                self.state = 343
                self.named()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 346
            self.match(nlpql_parserParser.COLON)
            self.state = 347
            self.value()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class IdentifierPairContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLON(self):
            return self.getToken(nlpql_parserParser.COLON, 0)

        def value(self):
            return self.getTypedRuleContext(nlpql_parserParser.ValueContext,0)


        def IDENTIFIER(self):
            return self.getToken(nlpql_parserParser.IDENTIFIER, 0)

        def OMOP(self):
            return self.getToken(nlpql_parserParser.OMOP, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_identifierPair




    def identifierPair(self):

        localctx = nlpql_parserParser.IdentifierPairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 78, self.RULE_identifierPair)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 349
            _la = self._input.LA(1)
            if not(_la==nlpql_parserParser.OMOP or _la==nlpql_parserParser.IDENTIFIER):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 350
            self.match(nlpql_parserParser.COLON)
            self.state = 351
            self.value()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class NamedContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def MIN_VALUE(self):
            return self.getToken(nlpql_parserParser.MIN_VALUE, 0)

        def MAX_VALUE(self):
            return self.getToken(nlpql_parserParser.MAX_VALUE, 0)

        def CODE_SYSTEM(self):
            return self.getToken(nlpql_parserParser.CODE_SYSTEM, 0)

        def VALUE_SET(self):
            return self.getToken(nlpql_parserParser.VALUE_SET, 0)

        def TERM_SET(self):
            return self.getToken(nlpql_parserParser.TERM_SET, 0)

        def DOCUMENT_SET(self):
            return self.getToken(nlpql_parserParser.DOCUMENT_SET, 0)

        def COHORT(self):
            return self.getToken(nlpql_parserParser.COHORT, 0)

        def POPULATION(self):
            return self.getToken(nlpql_parserParser.POPULATION, 0)

        def DATAMODEL(self):
            return self.getToken(nlpql_parserParser.DATAMODEL, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_named




    def named(self):

        localctx = nlpql_parserParser.NamedContext(self, self._ctx, self.state)
        self.enterRule(localctx, 80, self.RULE_named)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 353
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << nlpql_parserParser.DATAMODEL) | (1 << nlpql_parserParser.CODE_SYSTEM) | (1 << nlpql_parserParser.VALUE_SET) | (1 << nlpql_parserParser.TERM_SET) | (1 << nlpql_parserParser.DOCUMENT_SET) | (1 << nlpql_parserParser.COHORT) | (1 << nlpql_parserParser.POPULATION) | (1 << nlpql_parserParser.MIN_VALUE) | (1 << nlpql_parserParser.MAX_VALUE))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
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
        self.enterRule(localctx, 82, self.RULE_array)
        self._la = 0 # Token type
        try:
            self.state = 368
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,28,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 355
                self.match(nlpql_parserParser.L_BRACKET)
                self.state = 356
                self.value()
                self.state = 361
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==nlpql_parserParser.COMMA:
                    self.state = 357
                    self.match(nlpql_parserParser.COMMA)
                    self.state = 358
                    self.value()
                    self.state = 363
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 364
                self.match(nlpql_parserParser.R_BRACKET)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 366
                self.match(nlpql_parserParser.L_BRACKET)
                self.state = 367
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

        def FLOAT(self):
            return self.getToken(nlpql_parserParser.FLOAT, 0)

        def obj(self):
            return self.getTypedRuleContext(nlpql_parserParser.ObjContext,0)


        def array(self):
            return self.getTypedRuleContext(nlpql_parserParser.ArrayContext,0)


        def BOOL(self):
            return self.getToken(nlpql_parserParser.BOOL, 0)

        def NULL(self):
            return self.getToken(nlpql_parserParser.NULL, 0)

        def ALL(self):
            return self.getToken(nlpql_parserParser.ALL, 0)

        def IDENTIFIER(self):
            return self.getToken(nlpql_parserParser.IDENTIFIER, 0)

        def qualifiedName(self):
            return self.getTypedRuleContext(nlpql_parserParser.QualifiedNameContext,0)


        def TIME(self):
            return self.getToken(nlpql_parserParser.TIME, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_value




    def value(self):

        localctx = nlpql_parserParser.ValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 84, self.RULE_value)
        try:
            self.state = 381
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,29,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 370
                self.match(nlpql_parserParser.STRING)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 371
                self.match(nlpql_parserParser.DECIMAL)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 372
                self.match(nlpql_parserParser.FLOAT)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 373
                self.obj()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 374
                self.array()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 375
                self.match(nlpql_parserParser.BOOL)
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 376
                self.match(nlpql_parserParser.NULL)
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 377
                self.match(nlpql_parserParser.ALL)
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 378
                self.match(nlpql_parserParser.IDENTIFIER)
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 379
                self.qualifiedName()
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 380
                self.match(nlpql_parserParser.TIME)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[22] = self.expression_sempred
        self._predicates[25] = self.predicate_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expression_sempred(self, localctx:ExpressionContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 3)
         

    def predicate_sempred(self, localctx:PredicateContext, predIndex:int):
            if predIndex == 1:
                return self.precpred(self._ctx, 4)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 3)
         

            if predIndex == 3:
                return self.precpred(self._ctx, 6)
         

            if predIndex == 4:
                return self.precpred(self._ctx, 5)
         

            if predIndex == 5:
                return self.precpred(self._ctx, 2)
         




