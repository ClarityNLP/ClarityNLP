# Generated from nlpql_parser.g4 by ANTLR 4.9
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3W")
        buf.write("\u0199\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\4\16")
        buf.write("\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22\4\23\t\23")
        buf.write("\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30\4\31")
        buf.write("\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35\4\36\t\36")
        buf.write("\4\37\t\37\4 \t \4!\t!\4\"\t\"\4#\t#\4$\t$\4%\t%\4&\t")
        buf.write("&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t+\4,\t,\4-\t-\4.\t.\4")
        buf.write("/\t/\3\2\7\2`\n\2\f\2\16\2c\13\2\3\2\3\2\3\3\3\3\3\3\3")
        buf.write("\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\5\3u\n\3\3")
        buf.write("\3\3\3\3\4\3\4\3\5\3\5\3\5\3\6\3\6\3\6\3\7\3\7\3\b\3\b")
        buf.write("\3\b\5\b\u0086\n\b\3\t\3\t\3\t\3\n\3\n\3\n\5\n\u008e\n")
        buf.write("\n\3\13\3\13\3\13\5\13\u0093\n\13\3\13\3\13\3\13\3\f\3")
        buf.write("\f\3\f\3\r\3\r\3\r\3\16\3\16\3\16\3\17\3\17\3\17\3\20")
        buf.write("\3\20\3\20\3\21\5\21\u00a8\n\21\3\21\3\21\3\21\3\22\3")
        buf.write("\22\3\22\3\23\3\23\5\23\u00b2\n\23\3\23\3\23\3\23\3\23")
        buf.write("\3\24\3\24\3\24\5\24\u00bb\n\24\3\25\3\25\3\26\3\26\3")
        buf.write("\27\3\27\3\30\3\30\3\30\3\31\3\31\3\31\3\31\3\31\3\31")
        buf.write("\5\31\u00cc\n\31\3\31\3\31\3\31\3\31\7\31\u00d2\n\31\f")
        buf.write("\31\16\31\u00d5\13\31\3\32\3\32\3\33\3\33\3\33\5\33\u00dc")
        buf.write("\n\33\3\33\3\33\3\34\3\34\3\34\3\34\3\34\3\34\3\34\3\34")
        buf.write("\3\34\5\34\u00e9\n\34\3\34\3\34\3\34\3\34\3\34\3\34\3")
        buf.write("\34\5\34\u00f2\n\34\3\34\3\34\3\34\3\34\3\34\3\34\3\34")
        buf.write("\3\34\3\34\3\34\5\34\u00fe\n\34\3\34\3\34\3\34\5\34\u0103")
        buf.write("\n\34\7\34\u0105\n\34\f\34\16\34\u0108\13\34\3\35\5\35")
        buf.write("\u010b\n\35\3\35\3\35\3\36\3\36\3\36\3\36\3\36\3\36\3")
        buf.write("\36\3\36\3\36\7\36\u0118\n\36\f\36\16\36\u011b\13\36\3")
        buf.write("\36\3\36\5\36\u011f\n\36\3\37\3\37\3 \3 \3!\3!\3!\3!\3")
        buf.write("!\3!\3!\3!\3!\3!\3!\3!\5!\u0131\n!\3\"\3\"\3#\3#\3#\3")
        buf.write("#\3#\7#\u013a\n#\f#\16#\u013d\13#\3#\3#\3$\3$\3$\7$\u0144")
        buf.write("\n$\f$\16$\u0147\13$\3%\3%\3%\3%\3&\3&\3&\3&\5&\u0151")
        buf.write("\n&\3\'\3\'\3(\3(\5(\u0157\n(\3)\3)\3)\3*\3*\3*\3*\7*")
        buf.write("\u0160\n*\f*\16*\u0163\13*\3*\3*\3*\3*\5*\u0169\n*\3+")
        buf.write("\3+\5+\u016d\n+\3+\3+\3+\3,\3,\3,\3,\3-\3-\3.\3.\3.\3")
        buf.write(".\7.\u017c\n.\f.\16.\u017f\13.\3.\3.\3.\3.\3.\3.\3.\3")
        buf.write(".\5.\u0189\n.\3/\3/\3/\3/\3/\3/\3/\3/\3/\3/\3/\3/\5/\u0197")
        buf.write("\n/\3/\2\4\60\66\60\2\4\6\b\n\f\16\20\22\24\26\30\32\34")
        buf.write("\36 \"$&(*,.\60\62\64\668:<>@BDFHJLNPRTVXZ\\\2\n\4\2\"")
        buf.write("\"QQ\4\2#$QQ\3\2&\'\4\2++\65\65\3\2)+\3\2\4\5\4\2\"\"")
        buf.write("VV\6\2\t\t\f\30\33\35\37!\2\u01b0\2a\3\2\2\2\4t\3\2\2")
        buf.write("\2\6x\3\2\2\2\bz\3\2\2\2\n}\3\2\2\2\f\u0080\3\2\2\2\16")
        buf.write("\u0082\3\2\2\2\20\u0087\3\2\2\2\22\u008a\3\2\2\2\24\u008f")
        buf.write("\3\2\2\2\26\u0097\3\2\2\2\30\u009a\3\2\2\2\32\u009d\3")
        buf.write("\2\2\2\34\u00a0\3\2\2\2\36\u00a3\3\2\2\2 \u00a7\3\2\2")
        buf.write("\2\"\u00ac\3\2\2\2$\u00af\3\2\2\2&\u00ba\3\2\2\2(\u00bc")
        buf.write("\3\2\2\2*\u00be\3\2\2\2,\u00c0\3\2\2\2.\u00c2\3\2\2\2")
        buf.write("\60\u00cb\3\2\2\2\62\u00d6\3\2\2\2\64\u00d8\3\2\2\2\66")
        buf.write("\u00df\3\2\2\28\u010a\3\2\2\2:\u011e\3\2\2\2<\u0120\3")
        buf.write("\2\2\2>\u0122\3\2\2\2@\u0130\3\2\2\2B\u0132\3\2\2\2D\u0134")
        buf.write("\3\2\2\2F\u0140\3\2\2\2H\u0148\3\2\2\2J\u014c\3\2\2\2")
        buf.write("L\u0152\3\2\2\2N\u0154\3\2\2\2P\u0158\3\2\2\2R\u0168\3")
        buf.write("\2\2\2T\u016c\3\2\2\2V\u0171\3\2\2\2X\u0175\3\2\2\2Z\u0188")
        buf.write("\3\2\2\2\\\u0196\3\2\2\2^`\5\4\3\2_^\3\2\2\2`c\3\2\2\2")
        buf.write("a_\3\2\2\2ab\3\2\2\2bd\3\2\2\2ca\3\2\2\2de\7\2\2\3e\3")
        buf.write("\3\2\2\2fu\5\16\b\2gu\5\20\t\2hu\5\22\n\2iu\5\24\13\2")
        buf.write("ju\5\26\f\2ku\5\30\r\2lu\5\34\17\2mu\5\32\16\2nu\5\36")
        buf.write("\20\2ou\5 \21\2pu\5$\23\2qu\5\"\22\2ru\5\6\4\2su\5\b\5")
        buf.write("\2tf\3\2\2\2tg\3\2\2\2th\3\2\2\2ti\3\2\2\2tj\3\2\2\2t")
        buf.write("k\3\2\2\2tl\3\2\2\2tm\3\2\2\2tn\3\2\2\2to\3\2\2\2tp\3")
        buf.write("\2\2\2tq\3\2\2\2tr\3\2\2\2ts\3\2\2\2uv\3\2\2\2vw\7<\2")
        buf.write("\2w\5\3\2\2\2xy\7\3\2\2y\7\3\2\2\2z{\7\36\2\2{|\7F\2\2")
        buf.write("|\t\3\2\2\2}~\7\7\2\2~\177\5\f\7\2\177\13\3\2\2\2\u0080")
        buf.write("\u0081\7Q\2\2\u0081\r\3\2\2\2\u0082\u0083\7\6\2\2\u0083")
        buf.write("\u0085\7Q\2\2\u0084\u0086\5\n\6\2\u0085\u0084\3\2\2\2")
        buf.write("\u0085\u0086\3\2\2\2\u0086\17\3\2\2\2\u0087\u0088\7\b")
        buf.write("\2\2\u0088\u0089\7Q\2\2\u0089\21\3\2\2\2\u008a\u008b\7")
        buf.write("\t\2\2\u008b\u008d\t\2\2\2\u008c\u008e\5\n\6\2\u008d\u008c")
        buf.write("\3\2\2\2\u008d\u008e\3\2\2\2\u008e\23\3\2\2\2\u008f\u0090")
        buf.write("\7\n\2\2\u0090\u0092\t\3\2\2\u0091\u0093\5\n\6\2\u0092")
        buf.write("\u0091\3\2\2\2\u0092\u0093\3\2\2\2\u0093\u0094\3\2\2\2")
        buf.write("\u0094\u0095\7\13\2\2\u0095\u0096\7V\2\2\u0096\25\3\2")
        buf.write("\2\2\u0097\u0098\7\r\2\2\u0098\u0099\5V,\2\u0099\27\3")
        buf.write("\2\2\2\u009a\u009b\7\16\2\2\u009b\u009c\5H%\2\u009c\31")
        buf.write("\3\2\2\2\u009d\u009e\7\26\2\2\u009e\u009f\5H%\2\u009f")
        buf.write("\33\3\2\2\2\u00a0\u00a1\7\17\2\2\u00a1\u00a2\5J&\2\u00a2")
        buf.write("\35\3\2\2\2\u00a3\u00a4\7\27\2\2\u00a4\u00a5\5H%\2\u00a5")
        buf.write("\37\3\2\2\2\u00a6\u00a8\7\4\2\2\u00a7\u00a6\3\2\2\2\u00a7")
        buf.write("\u00a8\3\2\2\2\u00a8\u00a9\3\2\2\2\u00a9\u00aa\7\30\2")
        buf.write("\2\u00aa\u00ab\7V\2\2\u00ab!\3\2\2\2\u00ac\u00ad\7\32")
        buf.write("\2\2\u00ad\u00ae\t\4\2\2\u00ae#\3\2\2\2\u00af\u00b1\7")
        buf.write("\31\2\2\u00b0\u00b2\5(\25\2\u00b1\u00b0\3\2\2\2\u00b1")
        buf.write("\u00b2\3\2\2\2\u00b2\u00b3\3\2\2\2\u00b3\u00b4\5*\26\2")
        buf.write("\u00b4\u00b5\7=\2\2\u00b5\u00b6\5&\24\2\u00b6%\3\2\2\2")
        buf.write("\u00b7\u00bb\5.\30\2\u00b8\u00bb\5,\27\2\u00b9\u00bb\5")
        buf.write("N(\2\u00ba\u00b7\3\2\2\2\u00ba\u00b8\3\2\2\2\u00ba\u00b9")
        buf.write("\3\2\2\2\u00bb\'\3\2\2\2\u00bc\u00bd\7\5\2\2\u00bd)\3")
        buf.write("\2\2\2\u00be\u00bf\7V\2\2\u00bf+\3\2\2\2\u00c0\u00c1\5")
        buf.write("D#\2\u00c1-\3\2\2\2\u00c2\u00c3\7(\2\2\u00c3\u00c4\5\60")
        buf.write("\31\2\u00c4/\3\2\2\2\u00c5\u00c6\b\31\1\2\u00c6\u00c7")
        buf.write("\5\62\32\2\u00c7\u00c8\5\60\31\6\u00c8\u00cc\3\2\2\2\u00c9")
        buf.write("\u00cc\5\64\33\2\u00ca\u00cc\5\66\34\2\u00cb\u00c5\3\2")
        buf.write("\2\2\u00cb\u00c9\3\2\2\2\u00cb\u00ca\3\2\2\2\u00cc\u00d3")
        buf.write("\3\2\2\2\u00cd\u00ce\f\5\2\2\u00ce\u00cf\5> \2\u00cf\u00d0")
        buf.write("\5\60\31\6\u00d0\u00d2\3\2\2\2\u00d1\u00cd\3\2\2\2\u00d2")
        buf.write("\u00d5\3\2\2\2\u00d3\u00d1\3\2\2\2\u00d3\u00d4\3\2\2\2")
        buf.write("\u00d4\61\3\2\2\2\u00d5\u00d3\3\2\2\2\u00d6\u00d7\t\5")
        buf.write("\2\2\u00d7\63\3\2\2\2\u00d8\u00d9\5\66\34\2\u00d9\u00db")
        buf.write("\7\61\2\2\u00da\u00dc\7+\2\2\u00db\u00da\3\2\2\2\u00db")
        buf.write("\u00dc\3\2\2\2\u00dc\u00dd\3\2\2\2\u00dd\u00de\7L\2\2")
        buf.write("\u00de\65\3\2\2\2\u00df\u00e0\b\34\1\2\u00e0\u00e1\5:")
        buf.write("\36\2\u00e1\u0106\3\2\2\2\u00e2\u00e3\f\6\2\2\u00e3\u00e4")
        buf.write("\5@!\2\u00e4\u00e5\5\66\34\7\u00e5\u0105\3\2\2\2\u00e6")
        buf.write("\u00e8\f\5\2\2\u00e7\u00e9\7+\2\2\u00e8\u00e7\3\2\2\2")
        buf.write("\u00e8\u00e9\3\2\2\2\u00e9\u00ea\3\2\2\2\u00ea\u00eb\7")
        buf.write("\63\2\2\u00eb\u00ec\5\66\34\2\u00ec\u00ed\7)\2\2\u00ed")
        buf.write("\u00ee\5\66\34\6\u00ee\u0105\3\2\2\2\u00ef\u00f1\f\b\2")
        buf.write("\2\u00f0\u00f2\7+\2\2\u00f1\u00f0\3\2\2\2\u00f1\u00f2")
        buf.write("\3\2\2\2\u00f2\u00f3\3\2\2\2\u00f3\u00f4\7O\2\2\u00f4")
        buf.write("\u00f5\7@\2\2\u00f5\u00f6\5\60\31\2\u00f6\u00f7\7A\2\2")
        buf.write("\u00f7\u0105\3\2\2\2\u00f8\u00f9\f\7\2\2\u00f9\u00fa\7")
        buf.write("\61\2\2\u00fa\u0105\58\35\2\u00fb\u00fd\f\4\2\2\u00fc")
        buf.write("\u00fe\7+\2\2\u00fd\u00fc\3\2\2\2\u00fd\u00fe\3\2\2\2")
        buf.write("\u00fe\u00ff\3\2\2\2\u00ff\u0100\7\62\2\2\u0100\u0102")
        buf.write("\5\66\34\2\u0101\u0103\7Q\2\2\u0102\u0101\3\2\2\2\u0102")
        buf.write("\u0103\3\2\2\2\u0103\u0105\3\2\2\2\u0104\u00e2\3\2\2\2")
        buf.write("\u0104\u00e6\3\2\2\2\u0104\u00ef\3\2\2\2\u0104\u00f8\3")
        buf.write("\2\2\2\u0104\u00fb\3\2\2\2\u0105\u0108\3\2\2\2\u0106\u0104")
        buf.write("\3\2\2\2\u0106\u0107\3\2\2\2\u0107\67\3\2\2\2\u0108\u0106")
        buf.write("\3\2\2\2\u0109\u010b\7+\2\2\u010a\u0109\3\2\2\2\u010a")
        buf.write("\u010b\3\2\2\2\u010b\u010c\3\2\2\2\u010c\u010d\7M\2\2")
        buf.write("\u010d9\3\2\2\2\u010e\u011f\5\\/\2\u010f\u011f\5D#\2\u0110")
        buf.write("\u0111\5<\37\2\u0111\u0112\5:\36\2\u0112\u011f\3\2\2\2")
        buf.write("\u0113\u0114\7@\2\2\u0114\u0119\5\60\31\2\u0115\u0116")
        buf.write("\7?\2\2\u0116\u0118\5\60\31\2\u0117\u0115\3\2\2\2\u0118")
        buf.write("\u011b\3\2\2\2\u0119\u0117\3\2\2\2\u0119\u011a\3\2\2\2")
        buf.write("\u011a\u011c\3\2\2\2\u011b\u0119\3\2\2\2\u011c\u011d\7")
        buf.write("A\2\2\u011d\u011f\3\2\2\2\u011e\u010e\3\2\2\2\u011e\u010f")
        buf.write("\3\2\2\2\u011e\u0110\3\2\2\2\u011e\u0113\3\2\2\2\u011f")
        buf.write(";\3\2\2\2\u0120\u0121\7+\2\2\u0121=\3\2\2\2\u0122\u0123")
        buf.write("\t\6\2\2\u0123?\3\2\2\2\u0124\u0131\7,\2\2\u0125\u0131")
        buf.write("\7-\2\2\u0126\u0131\7/\2\2\u0127\u0131\7.\2\2\u0128\u0131")
        buf.write("\7\60\2\2\u0129\u012a\7\64\2\2\u012a\u0131\7\66\2\2\u012b")
        buf.write("\u0131\7\67\2\2\u012c\u0131\78\2\2\u012d\u0131\79\2\2")
        buf.write("\u012e\u0131\7:\2\2\u012f\u0131\7;\2\2\u0130\u0124\3\2")
        buf.write("\2\2\u0130\u0125\3\2\2\2\u0130\u0126\3\2\2\2\u0130\u0127")
        buf.write("\3\2\2\2\u0130\u0128\3\2\2\2\u0130\u0129\3\2\2\2\u0130")
        buf.write("\u012b\3\2\2\2\u0130\u012c\3\2\2\2\u0130\u012d\3\2\2\2")
        buf.write("\u0130\u012e\3\2\2\2\u0130\u012f\3\2\2\2\u0131A\3\2\2")
        buf.write("\2\u0132\u0133\5\\/\2\u0133C\3\2\2\2\u0134\u0135\5F$\2")
        buf.write("\u0135\u0136\7@\2\2\u0136\u013b\5\\/\2\u0137\u0138\7?")
        buf.write("\2\2\u0138\u013a\5\\/\2\u0139\u0137\3\2\2\2\u013a\u013d")
        buf.write("\3\2\2\2\u013b\u0139\3\2\2\2\u013b\u013c\3\2\2\2\u013c")
        buf.write("\u013e\3\2\2\2\u013d\u013b\3\2\2\2\u013e\u013f\7A\2\2")
        buf.write("\u013fE\3\2\2\2\u0140\u0145\7V\2\2\u0141\u0142\7>\2\2")
        buf.write("\u0142\u0144\7V\2\2\u0143\u0141\3\2\2\2\u0144\u0147\3")
        buf.write("\2\2\2\u0145\u0143\3\2\2\2\u0145\u0146\3\2\2\2\u0146G")
        buf.write("\3\2\2\2\u0147\u0145\3\2\2\2\u0148\u0149\7V\2\2\u0149")
        buf.write("\u014a\7=\2\2\u014a\u014b\5D#\2\u014bI\3\2\2\2\u014c\u014d")
        buf.write("\7V\2\2\u014d\u0150\7=\2\2\u014e\u0151\5Z.\2\u014f\u0151")
        buf.write("\7Q\2\2\u0150\u014e\3\2\2\2\u0150\u014f\3\2\2\2\u0151")
        buf.write("K\3\2\2\2\u0152\u0153\t\7\2\2\u0153M\3\2\2\2\u0154\u0156")
        buf.write("\5P)\2\u0155\u0157\5.\30\2\u0156\u0155\3\2\2\2\u0156\u0157")
        buf.write("\3\2\2\2\u0157O\3\2\2\2\u0158\u0159\7N\2\2\u0159\u015a")
        buf.write("\5R*\2\u015aQ\3\2\2\2\u015b\u015c\7D\2\2\u015c\u0161\5")
        buf.write("T+\2\u015d\u015e\7?\2\2\u015e\u0160\5T+\2\u015f\u015d")
        buf.write("\3\2\2\2\u0160\u0163\3\2\2\2\u0161\u015f\3\2\2\2\u0161")
        buf.write("\u0162\3\2\2\2\u0162\u0164\3\2\2\2\u0163\u0161\3\2\2\2")
        buf.write("\u0164\u0165\7E\2\2\u0165\u0169\3\2\2\2\u0166\u0167\7")
        buf.write("D\2\2\u0167\u0169\7E\2\2\u0168\u015b\3\2\2\2\u0168\u0166")
        buf.write("\3\2\2\2\u0169S\3\2\2\2\u016a\u016d\7Q\2\2\u016b\u016d")
        buf.write("\5X-\2\u016c\u016a\3\2\2\2\u016c\u016b\3\2\2\2\u016d\u016e")
        buf.write("\3\2\2\2\u016e\u016f\7=\2\2\u016f\u0170\5\\/\2\u0170U")
        buf.write("\3\2\2\2\u0171\u0172\t\b\2\2\u0172\u0173\7=\2\2\u0173")
        buf.write("\u0174\5\\/\2\u0174W\3\2\2\2\u0175\u0176\t\t\2\2\u0176")
        buf.write("Y\3\2\2\2\u0177\u0178\7B\2\2\u0178\u017d\5\\/\2\u0179")
        buf.write("\u017a\7?\2\2\u017a\u017c\5\\/\2\u017b\u0179\3\2\2\2\u017c")
        buf.write("\u017f\3\2\2\2\u017d\u017b\3\2\2\2\u017d\u017e\3\2\2\2")
        buf.write("\u017e\u0180\3\2\2\2\u017f\u017d\3\2\2\2\u0180\u0181\7")
        buf.write("C\2\2\u0181\u0189\3\2\2\2\u0182\u0183\7B\2\2\u0183\u0189")
        buf.write("\7C\2\2\u0184\u0185\7B\2\2\u0185\u0186\5P)\2\u0186\u0187")
        buf.write("\7C\2\2\u0187\u0189\3\2\2\2\u0188\u0177\3\2\2\2\u0188")
        buf.write("\u0182\3\2\2\2\u0188\u0184\3\2\2\2\u0189[\3\2\2\2\u018a")
        buf.write("\u0197\7Q\2\2\u018b\u0197\7R\2\2\u018c\u0197\7F\2\2\u018d")
        buf.write("\u0197\7J\2\2\u018e\u0197\5R*\2\u018f\u0197\5Z.\2\u0190")
        buf.write("\u0197\7L\2\2\u0191\u0197\7M\2\2\u0192\u0197\7%\2\2\u0193")
        buf.write("\u0197\7V\2\2\u0194\u0197\5F$\2\u0195\u0197\7W\2\2\u0196")
        buf.write("\u018a\3\2\2\2\u0196\u018b\3\2\2\2\u0196\u018c\3\2\2\2")
        buf.write("\u0196\u018d\3\2\2\2\u0196\u018e\3\2\2\2\u0196\u018f\3")
        buf.write("\2\2\2\u0196\u0190\3\2\2\2\u0196\u0191\3\2\2\2\u0196\u0192")
        buf.write("\3\2\2\2\u0196\u0193\3\2\2\2\u0196\u0194\3\2\2\2\u0196")
        buf.write("\u0195\3\2\2\2\u0197]\3\2\2\2!at\u0085\u008d\u0092\u00a7")
        buf.write("\u00b1\u00ba\u00cb\u00d3\u00db\u00e8\u00f1\u00fd\u0102")
        buf.write("\u0104\u0106\u010a\u0119\u011e\u0130\u013b\u0145\u0150")
        buf.write("\u0156\u0161\u0168\u016c\u017d\u0188\u0196")
        return buf.getvalue()


class nlpql_parserParser ( Parser ):

    grammarFileName = "nlpql_parser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'debug'", "'default'", "'final'", "'phenotype'", 
                     "'version'", "'description'", "'datamodel'", "'include'", 
                     "'called'", "'code'", "'codesystem'", "'valueset'", 
                     "'termset'", "'excluded_termset'", "'report_types'", 
                     "'report_tags'", "'filter_query'", "'query'", "'source'", 
                     "'documentset'", "'cohort'", "'population'", "'define'", 
                     "'context'", "'minimum_value'", "'maximum_value'", 
                     "'enum_list'", "'limit'", "'cql'", "'cql_source'", 
                     "'display_name'", "'OMOP'", "'ClarityCore'", "'OHDSIHelpers'", 
                     "'All'", "'Patient'", "'Document'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'>'", "'<'", "'<='", "'>='", 
                     "'=='", "<INVALID>", "<INVALID>", "<INVALID>", "'!='", 
                     "'!'", "'+'", "'-'", "'*'", "'/'", "'^'", "'%'", "';'", 
                     "':'", "'.'", "','", "'('", "')'", "'['", "']'", "'{'", 
                     "'}'" ]

    symbolicNames = [ "<INVALID>", "DEBUG", "DEFAULT", "FINAL", "PHENOTYPE_NAME", 
                      "VERSION", "DESCRIPTION", "DATAMODEL", "INCLUDE", 
                      "CALLED", "CODE", "CODE_SYSTEM", "VALUE_SET", "TERM_SET", 
                      "EXCLUDED_TERM_SET", "REPORT_TYPES", "REPORT_TAGS", 
                      "FILTER_QUERY", "QUERY", "SOURCE", "DOCUMENT_SET", 
                      "COHORT", "POPULATION", "DEFINE", "CONTEXT", "MIN_VALUE", 
                      "MAX_VALUE", "ENUM_LIST", "LIMIT", "CQL", "CQL_SOURCE", 
                      "DISPLAY_NAME", "OMOP", "CLARITY_CORE", "OHDSI_HELPERS", 
                      "ALL", "PATIENT", "DOCUMENT", "WHERE", "AND", "OR", 
                      "NOT", "GT", "LT", "LTE", "GTE", "EQUAL", "IS", "LIKE", 
                      "BETWEEN", "NOT_EQUAL", "BANG", "PLUS", "MINUS", "MULT", 
                      "DIV", "CARET", "MOD", "SEMI", "COLON", "DOT", "COMMA", 
                      "L_PAREN", "R_PAREN", "L_BRACKET", "R_BRACKET", "L_CURLY", 
                      "R_CURLY", "DECIMAL", "HEX", "OCT", "BINARY", "FLOAT", 
                      "HEX_FLOAT", "BOOL", "NULL", "TUPLE_NAME", "IN", "CHAR", 
                      "STRING", "LONG_STRING", "WS", "COMMENT", "LINE_COMMENT", 
                      "IDENTIFIER", "TIME" ]

    RULE_validExpression = 0
    RULE_statement = 1
    RULE_debugger = 2
    RULE_limit = 3
    RULE_version = 4
    RULE_versionValue = 5
    RULE_phenotypeName = 6
    RULE_description = 7
    RULE_dataModel = 8
    RULE_include = 9
    RULE_codeSystem = 10
    RULE_valueSet = 11
    RULE_documentSet = 12
    RULE_termSet = 13
    RULE_cohort = 14
    RULE_population = 15
    RULE_context = 16
    RULE_define = 17
    RULE_defineSubject = 18
    RULE_finalModifier = 19
    RULE_defineName = 20
    RULE_dataEntity = 21
    RULE_operation = 22
    RULE_expression = 23
    RULE_notOperator = 24
    RULE_predicateBoolean = 25
    RULE_predicate = 26
    RULE_nullNotnull = 27
    RULE_expressionAtom = 28
    RULE_unaryOperator = 29
    RULE_logicalOperator = 30
    RULE_comparisonOperator = 31
    RULE_operand = 32
    RULE_methodCall = 33
    RULE_qualifiedName = 34
    RULE_pairMethod = 35
    RULE_pairArray = 36
    RULE_modifiers = 37
    RULE_tupleOperation = 38
    RULE_tuple_ = 39
    RULE_obj = 40
    RULE_pair = 41
    RULE_identifierPair = 42
    RULE_named = 43
    RULE_array = 44
    RULE_value = 45

    ruleNames =  [ "validExpression", "statement", "debugger", "limit", 
                   "version", "versionValue", "phenotypeName", "description", 
                   "dataModel", "include", "codeSystem", "valueSet", "documentSet", 
                   "termSet", "cohort", "population", "context", "define", 
                   "defineSubject", "finalModifier", "defineName", "dataEntity", 
                   "operation", "expression", "notOperator", "predicateBoolean", 
                   "predicate", "nullNotnull", "expressionAtom", "unaryOperator", 
                   "logicalOperator", "comparisonOperator", "operand", "methodCall", 
                   "qualifiedName", "pairMethod", "pairArray", "modifiers", 
                   "tupleOperation", "tuple_", "obj", "pair", "identifierPair", 
                   "named", "array", "value" ]

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
    CODE=10
    CODE_SYSTEM=11
    VALUE_SET=12
    TERM_SET=13
    EXCLUDED_TERM_SET=14
    REPORT_TYPES=15
    REPORT_TAGS=16
    FILTER_QUERY=17
    QUERY=18
    SOURCE=19
    DOCUMENT_SET=20
    COHORT=21
    POPULATION=22
    DEFINE=23
    CONTEXT=24
    MIN_VALUE=25
    MAX_VALUE=26
    ENUM_LIST=27
    LIMIT=28
    CQL=29
    CQL_SOURCE=30
    DISPLAY_NAME=31
    OMOP=32
    CLARITY_CORE=33
    OHDSI_HELPERS=34
    ALL=35
    PATIENT=36
    DOCUMENT=37
    WHERE=38
    AND=39
    OR=40
    NOT=41
    GT=42
    LT=43
    LTE=44
    GTE=45
    EQUAL=46
    IS=47
    LIKE=48
    BETWEEN=49
    NOT_EQUAL=50
    BANG=51
    PLUS=52
    MINUS=53
    MULT=54
    DIV=55
    CARET=56
    MOD=57
    SEMI=58
    COLON=59
    DOT=60
    COMMA=61
    L_PAREN=62
    R_PAREN=63
    L_BRACKET=64
    R_BRACKET=65
    L_CURLY=66
    R_CURLY=67
    DECIMAL=68
    HEX=69
    OCT=70
    BINARY=71
    FLOAT=72
    HEX_FLOAT=73
    BOOL=74
    NULL=75
    TUPLE_NAME=76
    IN=77
    CHAR=78
    STRING=79
    LONG_STRING=80
    WS=81
    COMMENT=82
    LINE_COMMENT=83
    IDENTIFIER=84
    TIME=85

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9")
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
            self.state = 95
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << nlpql_parserParser.DEBUG) | (1 << nlpql_parserParser.DEFAULT) | (1 << nlpql_parserParser.PHENOTYPE_NAME) | (1 << nlpql_parserParser.DESCRIPTION) | (1 << nlpql_parserParser.DATAMODEL) | (1 << nlpql_parserParser.INCLUDE) | (1 << nlpql_parserParser.CODE_SYSTEM) | (1 << nlpql_parserParser.VALUE_SET) | (1 << nlpql_parserParser.TERM_SET) | (1 << nlpql_parserParser.DOCUMENT_SET) | (1 << nlpql_parserParser.COHORT) | (1 << nlpql_parserParser.POPULATION) | (1 << nlpql_parserParser.DEFINE) | (1 << nlpql_parserParser.CONTEXT) | (1 << nlpql_parserParser.LIMIT))) != 0):
                self.state = 92
                self.statement()
                self.state = 97
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 98
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


        def limit(self):
            return self.getTypedRuleContext(nlpql_parserParser.LimitContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_statement




    def statement(self):

        localctx = nlpql_parserParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_statement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 114
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [nlpql_parserParser.PHENOTYPE_NAME]:
                self.state = 100
                self.phenotypeName()
                pass
            elif token in [nlpql_parserParser.DESCRIPTION]:
                self.state = 101
                self.description()
                pass
            elif token in [nlpql_parserParser.DATAMODEL]:
                self.state = 102
                self.dataModel()
                pass
            elif token in [nlpql_parserParser.INCLUDE]:
                self.state = 103
                self.include()
                pass
            elif token in [nlpql_parserParser.CODE_SYSTEM]:
                self.state = 104
                self.codeSystem()
                pass
            elif token in [nlpql_parserParser.VALUE_SET]:
                self.state = 105
                self.valueSet()
                pass
            elif token in [nlpql_parserParser.TERM_SET]:
                self.state = 106
                self.termSet()
                pass
            elif token in [nlpql_parserParser.DOCUMENT_SET]:
                self.state = 107
                self.documentSet()
                pass
            elif token in [nlpql_parserParser.COHORT]:
                self.state = 108
                self.cohort()
                pass
            elif token in [nlpql_parserParser.DEFAULT, nlpql_parserParser.POPULATION]:
                self.state = 109
                self.population()
                pass
            elif token in [nlpql_parserParser.DEFINE]:
                self.state = 110
                self.define()
                pass
            elif token in [nlpql_parserParser.CONTEXT]:
                self.state = 111
                self.context()
                pass
            elif token in [nlpql_parserParser.DEBUG]:
                self.state = 112
                self.debugger()
                pass
            elif token in [nlpql_parserParser.LIMIT]:
                self.state = 113
                self.limit()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 116
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
            self.state = 118
            self.match(nlpql_parserParser.DEBUG)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LimitContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LIMIT(self):
            return self.getToken(nlpql_parserParser.LIMIT, 0)

        def DECIMAL(self):
            return self.getToken(nlpql_parserParser.DECIMAL, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_limit




    def limit(self):

        localctx = nlpql_parserParser.LimitContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_limit)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 120
            self.match(nlpql_parserParser.LIMIT)
            self.state = 121
            self.match(nlpql_parserParser.DECIMAL)
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
        self.enterRule(localctx, 8, self.RULE_version)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 123
            self.match(nlpql_parserParser.VERSION)
            self.state = 124
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
        self.enterRule(localctx, 10, self.RULE_versionValue)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 126
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
        self.enterRule(localctx, 12, self.RULE_phenotypeName)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 128
            self.match(nlpql_parserParser.PHENOTYPE_NAME)
            self.state = 129
            self.match(nlpql_parserParser.STRING)
            self.state = 131
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.VERSION:
                self.state = 130
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
        self.enterRule(localctx, 14, self.RULE_description)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 133
            self.match(nlpql_parserParser.DESCRIPTION)
            self.state = 134
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
        self.enterRule(localctx, 16, self.RULE_dataModel)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 136
            self.match(nlpql_parserParser.DATAMODEL)
            self.state = 137
            _la = self._input.LA(1)
            if not(_la==nlpql_parserParser.OMOP or _la==nlpql_parserParser.STRING):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 139
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.VERSION:
                self.state = 138
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
        self.enterRule(localctx, 18, self.RULE_include)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 141
            self.match(nlpql_parserParser.INCLUDE)
            self.state = 142
            _la = self._input.LA(1)
            if not(((((_la - 33)) & ~0x3f) == 0 and ((1 << (_la - 33)) & ((1 << (nlpql_parserParser.CLARITY_CORE - 33)) | (1 << (nlpql_parserParser.OHDSI_HELPERS - 33)) | (1 << (nlpql_parserParser.STRING - 33)))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 144
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.VERSION:
                self.state = 143
                self.version()


            self.state = 146
            self.match(nlpql_parserParser.CALLED)
            self.state = 147
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
        self.enterRule(localctx, 20, self.RULE_codeSystem)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 149
            self.match(nlpql_parserParser.CODE_SYSTEM)
            self.state = 150
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
        self.enterRule(localctx, 22, self.RULE_valueSet)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 152
            self.match(nlpql_parserParser.VALUE_SET)
            self.state = 153
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
        self.enterRule(localctx, 24, self.RULE_documentSet)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 155
            self.match(nlpql_parserParser.DOCUMENT_SET)
            self.state = 156
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
        self.enterRule(localctx, 26, self.RULE_termSet)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 158
            self.match(nlpql_parserParser.TERM_SET)
            self.state = 159
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
        self.enterRule(localctx, 28, self.RULE_cohort)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 161
            self.match(nlpql_parserParser.COHORT)
            self.state = 162
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
        self.enterRule(localctx, 30, self.RULE_population)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 165
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.DEFAULT:
                self.state = 164
                self.match(nlpql_parserParser.DEFAULT)


            self.state = 167
            self.match(nlpql_parserParser.POPULATION)
            self.state = 168
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
        self.enterRule(localctx, 32, self.RULE_context)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 170
            self.match(nlpql_parserParser.CONTEXT)
            self.state = 171
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
        self.enterRule(localctx, 34, self.RULE_define)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 173
            self.match(nlpql_parserParser.DEFINE)
            self.state = 175
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.FINAL:
                self.state = 174
                self.finalModifier()


            self.state = 177
            self.defineName()
            self.state = 178
            self.match(nlpql_parserParser.COLON)
            self.state = 179
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


        def tupleOperation(self):
            return self.getTypedRuleContext(nlpql_parserParser.TupleOperationContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_defineSubject




    def defineSubject(self):

        localctx = nlpql_parserParser.DefineSubjectContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_defineSubject)
        try:
            self.state = 184
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [nlpql_parserParser.WHERE]:
                self.enterOuterAlt(localctx, 1)
                self.state = 181
                self.operation()
                pass
            elif token in [nlpql_parserParser.IDENTIFIER]:
                self.enterOuterAlt(localctx, 2)
                self.state = 182
                self.dataEntity()
                pass
            elif token in [nlpql_parserParser.TUPLE_NAME]:
                self.enterOuterAlt(localctx, 3)
                self.state = 183
                self.tupleOperation()
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
        self.enterRule(localctx, 38, self.RULE_finalModifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 186
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
        self.enterRule(localctx, 40, self.RULE_defineName)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 188
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
        self.enterRule(localctx, 42, self.RULE_dataEntity)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 190
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
        self.enterRule(localctx, 44, self.RULE_operation)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 192
            self.match(nlpql_parserParser.WHERE)
            self.state = 193
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
        _startState = 46
        self.enterRecursionRule(localctx, 46, self.RULE_expression, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 201
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,8,self._ctx)
            if la_ == 1:
                self.state = 196
                self.notOperator()
                self.state = 197
                self.expression(4)
                pass

            elif la_ == 2:
                self.state = 199
                self.predicateBoolean()
                pass

            elif la_ == 3:
                self.state = 200
                self.predicate(0)
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 209
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,9,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = nlpql_parserParser.ExpressionContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                    self.state = 203
                    if not self.precpred(self._ctx, 3):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                    self.state = 204
                    self.logicalOperator()
                    self.state = 205
                    self.expression(4) 
                self.state = 211
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
        self.enterRule(localctx, 48, self.RULE_notOperator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 212
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
        self.enterRule(localctx, 50, self.RULE_predicateBoolean)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 214
            self.predicate(0)
            self.state = 215
            self.match(nlpql_parserParser.IS)
            self.state = 217
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.NOT:
                self.state = 216
                self.match(nlpql_parserParser.NOT)


            self.state = 219
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
        _startState = 52
        self.enterRecursionRule(localctx, 52, self.RULE_predicate, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 222
            self.expressionAtom()
            self._ctx.stop = self._input.LT(-1)
            self.state = 260
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,16,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 258
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,15,self._ctx)
                    if la_ == 1:
                        localctx = nlpql_parserParser.PredicateContext(self, _parentctx, _parentState)
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_predicate)
                        self.state = 224
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 225
                        self.comparisonOperator()
                        self.state = 226
                        localctx.right = self.predicate(5)
                        pass

                    elif la_ == 2:
                        localctx = nlpql_parserParser.PredicateContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_predicate)
                        self.state = 228
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 230
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if _la==nlpql_parserParser.NOT:
                            self.state = 229
                            self.match(nlpql_parserParser.NOT)


                        self.state = 232
                        self.match(nlpql_parserParser.BETWEEN)
                        self.state = 233
                        self.predicate(0)
                        self.state = 234
                        self.match(nlpql_parserParser.AND)
                        self.state = 235
                        self.predicate(4)
                        pass

                    elif la_ == 3:
                        localctx = nlpql_parserParser.PredicateContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_predicate)
                        self.state = 237
                        if not self.precpred(self._ctx, 6):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 6)")
                        self.state = 239
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if _la==nlpql_parserParser.NOT:
                            self.state = 238
                            self.match(nlpql_parserParser.NOT)


                        self.state = 241
                        self.match(nlpql_parserParser.IN)
                        self.state = 242
                        self.match(nlpql_parserParser.L_PAREN)

                        self.state = 243
                        self.expression(0)
                        self.state = 244
                        self.match(nlpql_parserParser.R_PAREN)
                        pass

                    elif la_ == 4:
                        localctx = nlpql_parserParser.PredicateContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_predicate)
                        self.state = 246
                        if not self.precpred(self._ctx, 5):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 5)")
                        self.state = 247
                        self.match(nlpql_parserParser.IS)
                        self.state = 248
                        self.nullNotnull()
                        pass

                    elif la_ == 5:
                        localctx = nlpql_parserParser.PredicateContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_predicate)
                        self.state = 249
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 251
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if _la==nlpql_parserParser.NOT:
                            self.state = 250
                            self.match(nlpql_parserParser.NOT)


                        self.state = 253
                        self.match(nlpql_parserParser.LIKE)
                        self.state = 254
                        self.predicate(0)
                        self.state = 256
                        self._errHandler.sync(self)
                        la_ = self._interp.adaptivePredict(self._input,14,self._ctx)
                        if la_ == 1:
                            self.state = 255
                            self.match(nlpql_parserParser.STRING)


                        pass

             
                self.state = 262
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
        self.enterRule(localctx, 54, self.RULE_nullNotnull)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 264
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.NOT:
                self.state = 263
                self.match(nlpql_parserParser.NOT)


            self.state = 266
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
        self.enterRule(localctx, 56, self.RULE_expressionAtom)
        self._la = 0 # Token type
        try:
            self.state = 284
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,19,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 268
                self.value()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 269
                self.methodCall()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 270
                self.unaryOperator()
                self.state = 271
                self.expressionAtom()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 273
                self.match(nlpql_parserParser.L_PAREN)
                self.state = 274
                self.expression(0)
                self.state = 279
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==nlpql_parserParser.COMMA:
                    self.state = 275
                    self.match(nlpql_parserParser.COMMA)
                    self.state = 276
                    self.expression(0)
                    self.state = 281
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 282
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
        self.enterRule(localctx, 58, self.RULE_unaryOperator)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 286
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

        def NOT(self):
            return self.getToken(nlpql_parserParser.NOT, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_logicalOperator




    def logicalOperator(self):

        localctx = nlpql_parserParser.LogicalOperatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_logicalOperator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 288
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << nlpql_parserParser.AND) | (1 << nlpql_parserParser.OR) | (1 << nlpql_parserParser.NOT))) != 0)):
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
        self.enterRule(localctx, 62, self.RULE_comparisonOperator)
        try:
            self.state = 302
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [nlpql_parserParser.GT]:
                self.enterOuterAlt(localctx, 1)
                self.state = 290
                self.match(nlpql_parserParser.GT)
                pass
            elif token in [nlpql_parserParser.LT]:
                self.enterOuterAlt(localctx, 2)
                self.state = 291
                self.match(nlpql_parserParser.LT)
                pass
            elif token in [nlpql_parserParser.GTE]:
                self.enterOuterAlt(localctx, 3)
                self.state = 292
                self.match(nlpql_parserParser.GTE)
                pass
            elif token in [nlpql_parserParser.LTE]:
                self.enterOuterAlt(localctx, 4)
                self.state = 293
                self.match(nlpql_parserParser.LTE)
                pass
            elif token in [nlpql_parserParser.EQUAL]:
                self.enterOuterAlt(localctx, 5)
                self.state = 294
                self.match(nlpql_parserParser.EQUAL)
                pass
            elif token in [nlpql_parserParser.NOT_EQUAL]:
                self.enterOuterAlt(localctx, 6)
                self.state = 295
                self.match(nlpql_parserParser.NOT_EQUAL)
                self.state = 296
                self.match(nlpql_parserParser.PLUS)
                pass
            elif token in [nlpql_parserParser.MINUS]:
                self.enterOuterAlt(localctx, 7)
                self.state = 297
                self.match(nlpql_parserParser.MINUS)
                pass
            elif token in [nlpql_parserParser.MULT]:
                self.enterOuterAlt(localctx, 8)
                self.state = 298
                self.match(nlpql_parserParser.MULT)
                pass
            elif token in [nlpql_parserParser.DIV]:
                self.enterOuterAlt(localctx, 9)
                self.state = 299
                self.match(nlpql_parserParser.DIV)
                pass
            elif token in [nlpql_parserParser.CARET]:
                self.enterOuterAlt(localctx, 10)
                self.state = 300
                self.match(nlpql_parserParser.CARET)
                pass
            elif token in [nlpql_parserParser.MOD]:
                self.enterOuterAlt(localctx, 11)
                self.state = 301
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
        self.enterRule(localctx, 64, self.RULE_operand)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 304
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
        self.enterRule(localctx, 66, self.RULE_methodCall)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 306
            self.qualifiedName()
            self.state = 307
            self.match(nlpql_parserParser.L_PAREN)
            self.state = 308
            self.value()
            self.state = 313
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==nlpql_parserParser.COMMA:
                self.state = 309
                self.match(nlpql_parserParser.COMMA)
                self.state = 310
                self.value()
                self.state = 315
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 316
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
        self.enterRule(localctx, 68, self.RULE_qualifiedName)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 318
            self.match(nlpql_parserParser.IDENTIFIER)
            self.state = 323
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,22,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 319
                    self.match(nlpql_parserParser.DOT)
                    self.state = 320
                    self.match(nlpql_parserParser.IDENTIFIER) 
                self.state = 325
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
        self.enterRule(localctx, 70, self.RULE_pairMethod)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 326
            self.match(nlpql_parserParser.IDENTIFIER)
            self.state = 327
            self.match(nlpql_parserParser.COLON)
            self.state = 328
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
        self.enterRule(localctx, 72, self.RULE_pairArray)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 330
            self.match(nlpql_parserParser.IDENTIFIER)
            self.state = 331
            self.match(nlpql_parserParser.COLON)
            self.state = 334
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [nlpql_parserParser.L_BRACKET]:
                self.state = 332
                self.array()
                pass
            elif token in [nlpql_parserParser.STRING]:
                self.state = 333
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
        self.enterRule(localctx, 74, self.RULE_modifiers)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 336
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


    class TupleOperationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def tuple_(self):
            return self.getTypedRuleContext(nlpql_parserParser.Tuple_Context,0)


        def operation(self):
            return self.getTypedRuleContext(nlpql_parserParser.OperationContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_tupleOperation




    def tupleOperation(self):

        localctx = nlpql_parserParser.TupleOperationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 76, self.RULE_tupleOperation)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 338
            self.tuple_()
            self.state = 340
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.WHERE:
                self.state = 339
                self.operation()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Tuple_Context(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TUPLE_NAME(self):
            return self.getToken(nlpql_parserParser.TUPLE_NAME, 0)

        def obj(self):
            return self.getTypedRuleContext(nlpql_parserParser.ObjContext,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_tuple_




    def tuple_(self):

        localctx = nlpql_parserParser.Tuple_Context(self, self._ctx, self.state)
        self.enterRule(localctx, 78, self.RULE_tuple_)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 342
            self.match(nlpql_parserParser.TUPLE_NAME)
            self.state = 343
            self.obj()
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
        self.enterRule(localctx, 80, self.RULE_obj)
        self._la = 0 # Token type
        try:
            self.state = 358
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,26,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 345
                self.match(nlpql_parserParser.L_CURLY)
                self.state = 346
                self.pair()
                self.state = 351
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==nlpql_parserParser.COMMA:
                    self.state = 347
                    self.match(nlpql_parserParser.COMMA)
                    self.state = 348
                    self.pair()
                    self.state = 353
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 354
                self.match(nlpql_parserParser.R_CURLY)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 356
                self.match(nlpql_parserParser.L_CURLY)
                self.state = 357
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
        self.enterRule(localctx, 82, self.RULE_pair)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 362
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [nlpql_parserParser.STRING]:
                self.state = 360
                self.match(nlpql_parserParser.STRING)
                pass
            elif token in [nlpql_parserParser.DATAMODEL, nlpql_parserParser.CODE, nlpql_parserParser.CODE_SYSTEM, nlpql_parserParser.VALUE_SET, nlpql_parserParser.TERM_SET, nlpql_parserParser.EXCLUDED_TERM_SET, nlpql_parserParser.REPORT_TYPES, nlpql_parserParser.REPORT_TAGS, nlpql_parserParser.FILTER_QUERY, nlpql_parserParser.QUERY, nlpql_parserParser.SOURCE, nlpql_parserParser.DOCUMENT_SET, nlpql_parserParser.COHORT, nlpql_parserParser.POPULATION, nlpql_parserParser.MIN_VALUE, nlpql_parserParser.MAX_VALUE, nlpql_parserParser.ENUM_LIST, nlpql_parserParser.CQL, nlpql_parserParser.CQL_SOURCE, nlpql_parserParser.DISPLAY_NAME]:
                self.state = 361
                self.named()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 364
            self.match(nlpql_parserParser.COLON)
            self.state = 365
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
        self.enterRule(localctx, 84, self.RULE_identifierPair)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 367
            _la = self._input.LA(1)
            if not(_la==nlpql_parserParser.OMOP or _la==nlpql_parserParser.IDENTIFIER):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 368
            self.match(nlpql_parserParser.COLON)
            self.state = 369
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

        def CODE(self):
            return self.getToken(nlpql_parserParser.CODE, 0)

        def CODE_SYSTEM(self):
            return self.getToken(nlpql_parserParser.CODE_SYSTEM, 0)

        def MIN_VALUE(self):
            return self.getToken(nlpql_parserParser.MIN_VALUE, 0)

        def MAX_VALUE(self):
            return self.getToken(nlpql_parserParser.MAX_VALUE, 0)

        def ENUM_LIST(self):
            return self.getToken(nlpql_parserParser.ENUM_LIST, 0)

        def VALUE_SET(self):
            return self.getToken(nlpql_parserParser.VALUE_SET, 0)

        def TERM_SET(self):
            return self.getToken(nlpql_parserParser.TERM_SET, 0)

        def EXCLUDED_TERM_SET(self):
            return self.getToken(nlpql_parserParser.EXCLUDED_TERM_SET, 0)

        def DOCUMENT_SET(self):
            return self.getToken(nlpql_parserParser.DOCUMENT_SET, 0)

        def COHORT(self):
            return self.getToken(nlpql_parserParser.COHORT, 0)

        def POPULATION(self):
            return self.getToken(nlpql_parserParser.POPULATION, 0)

        def DATAMODEL(self):
            return self.getToken(nlpql_parserParser.DATAMODEL, 0)

        def REPORT_TYPES(self):
            return self.getToken(nlpql_parserParser.REPORT_TYPES, 0)

        def REPORT_TAGS(self):
            return self.getToken(nlpql_parserParser.REPORT_TAGS, 0)

        def SOURCE(self):
            return self.getToken(nlpql_parserParser.SOURCE, 0)

        def FILTER_QUERY(self):
            return self.getToken(nlpql_parserParser.FILTER_QUERY, 0)

        def QUERY(self):
            return self.getToken(nlpql_parserParser.QUERY, 0)

        def CQL(self):
            return self.getToken(nlpql_parserParser.CQL, 0)

        def CQL_SOURCE(self):
            return self.getToken(nlpql_parserParser.CQL_SOURCE, 0)

        def DISPLAY_NAME(self):
            return self.getToken(nlpql_parserParser.DISPLAY_NAME, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_named




    def named(self):

        localctx = nlpql_parserParser.NamedContext(self, self._ctx, self.state)
        self.enterRule(localctx, 86, self.RULE_named)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 371
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << nlpql_parserParser.DATAMODEL) | (1 << nlpql_parserParser.CODE) | (1 << nlpql_parserParser.CODE_SYSTEM) | (1 << nlpql_parserParser.VALUE_SET) | (1 << nlpql_parserParser.TERM_SET) | (1 << nlpql_parserParser.EXCLUDED_TERM_SET) | (1 << nlpql_parserParser.REPORT_TYPES) | (1 << nlpql_parserParser.REPORT_TAGS) | (1 << nlpql_parserParser.FILTER_QUERY) | (1 << nlpql_parserParser.QUERY) | (1 << nlpql_parserParser.SOURCE) | (1 << nlpql_parserParser.DOCUMENT_SET) | (1 << nlpql_parserParser.COHORT) | (1 << nlpql_parserParser.POPULATION) | (1 << nlpql_parserParser.MIN_VALUE) | (1 << nlpql_parserParser.MAX_VALUE) | (1 << nlpql_parserParser.ENUM_LIST) | (1 << nlpql_parserParser.CQL) | (1 << nlpql_parserParser.CQL_SOURCE) | (1 << nlpql_parserParser.DISPLAY_NAME))) != 0)):
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

        def tuple_(self):
            return self.getTypedRuleContext(nlpql_parserParser.Tuple_Context,0)


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_array




    def array(self):

        localctx = nlpql_parserParser.ArrayContext(self, self._ctx, self.state)
        self.enterRule(localctx, 88, self.RULE_array)
        self._la = 0 # Token type
        try:
            self.state = 390
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,29,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 373
                self.match(nlpql_parserParser.L_BRACKET)
                self.state = 374
                self.value()
                self.state = 379
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==nlpql_parserParser.COMMA:
                    self.state = 375
                    self.match(nlpql_parserParser.COMMA)
                    self.state = 376
                    self.value()
                    self.state = 381
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 382
                self.match(nlpql_parserParser.R_BRACKET)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 384
                self.match(nlpql_parserParser.L_BRACKET)
                self.state = 385
                self.match(nlpql_parserParser.R_BRACKET)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 386
                self.match(nlpql_parserParser.L_BRACKET)
                self.state = 387
                self.tuple_()
                self.state = 388
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

        def LONG_STRING(self):
            return self.getToken(nlpql_parserParser.LONG_STRING, 0)

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
        self.enterRule(localctx, 90, self.RULE_value)
        try:
            self.state = 404
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,30,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 392
                self.match(nlpql_parserParser.STRING)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 393
                self.match(nlpql_parserParser.LONG_STRING)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 394
                self.match(nlpql_parserParser.DECIMAL)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 395
                self.match(nlpql_parserParser.FLOAT)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 396
                self.obj()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 397
                self.array()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 398
                self.match(nlpql_parserParser.BOOL)
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 399
                self.match(nlpql_parserParser.NULL)
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 400
                self.match(nlpql_parserParser.ALL)
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 401
                self.match(nlpql_parserParser.IDENTIFIER)
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 402
                self.qualifiedName()
                pass

            elif la_ == 12:
                self.enterOuterAlt(localctx, 12)
                self.state = 403
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
        self._predicates[23] = self.expression_sempred
        self._predicates[26] = self.predicate_sempred
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
         




