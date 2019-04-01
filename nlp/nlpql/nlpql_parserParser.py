# Generated from nlpql_parser.g4 by ANTLR 4.7.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys

def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3M")
        buf.write("\u0190\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\4\16")
        buf.write("\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22\4\23\t\23")
        buf.write("\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30\4\31")
        buf.write("\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35\4\36\t\36")
        buf.write("\4\37\t\37\4 \t \4!\t!\4\"\t\"\4#\t#\4$\t$\4%\t%\4&\t")
        buf.write("&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t+\4,\t,\4-\t-\4.\t.\3")
        buf.write("\2\7\2^\n\2\f\2\16\2a\13\2\3\2\3\2\3\3\3\3\3\3\3\3\3\3")
        buf.write("\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\5\3u\n\3")
        buf.write("\3\3\3\3\3\4\3\4\3\5\3\5\3\5\3\6\3\6\3\6\3\7\3\7\3\b\3")
        buf.write("\b\3\b\5\b\u0086\n\b\3\t\3\t\3\t\3\n\3\n\3\n\5\n\u008e")
        buf.write("\n\n\3\13\3\13\3\13\5\13\u0093\n\13\3\13\3\13\3\13\3\f")
        buf.write("\3\f\3\f\3\r\3\r\3\r\3\16\3\16\3\16\3\17\3\17\3\17\3\20")
        buf.write("\3\20\3\20\3\21\5\21\u00a8\n\21\3\21\3\21\3\21\3\22\3")
        buf.write("\22\3\22\3\23\3\23\5\23\u00b2\n\23\3\23\3\23\3\23\3\23")
        buf.write("\3\24\3\24\5\24\u00ba\n\24\3\25\3\25\3\26\3\26\3\27\3")
        buf.write("\27\3\30\3\30\3\30\3\31\3\31\3\31\3\31\3\31\3\31\5\31")
        buf.write("\u00cb\n\31\3\31\3\31\3\31\3\31\7\31\u00d1\n\31\f\31\16")
        buf.write("\31\u00d4\13\31\3\32\3\32\3\33\3\33\3\33\5\33\u00db\n")
        buf.write("\33\3\33\3\33\3\34\3\34\3\34\3\34\3\34\3\34\3\34\3\34")
        buf.write("\3\34\5\34\u00e8\n\34\3\34\3\34\3\34\3\34\3\34\3\34\3")
        buf.write("\34\5\34\u00f1\n\34\3\34\3\34\3\34\3\34\3\34\3\34\3\34")
        buf.write("\3\34\3\34\3\34\5\34\u00fd\n\34\3\34\3\34\3\34\5\34\u0102")
        buf.write("\n\34\7\34\u0104\n\34\f\34\16\34\u0107\13\34\3\35\5\35")
        buf.write("\u010a\n\35\3\35\3\35\3\36\3\36\3\36\3\36\3\36\3\36\3")
        buf.write("\36\3\36\3\36\7\36\u0117\n\36\f\36\16\36\u011a\13\36\3")
        buf.write("\36\3\36\5\36\u011e\n\36\3\37\3\37\3 \3 \3!\3!\3!\3!\3")
        buf.write("!\3!\3!\3!\3!\3!\3!\3!\5!\u0130\n!\3\"\3\"\3#\3#\3#\3")
        buf.write("#\3#\7#\u0139\n#\f#\16#\u013c\13#\3#\3#\3$\3$\3$\7$\u0143")
        buf.write("\n$\f$\16$\u0146\13$\3%\3%\3%\3%\3&\3&\3&\3&\5&\u0150")
        buf.write("\n&\3\'\3\'\3(\3(\3(\3(\7(\u0158\n(\f(\16(\u015b\13(\3")
        buf.write("(\3(\3(\3(\5(\u0161\n(\3)\3)\5)\u0165\n)\3)\3)\3)\3*\3")
        buf.write("*\3*\3*\3+\3+\3,\3,\3,\3,\7,\u0174\n,\f,\16,\u0177\13")
        buf.write(",\3,\3,\3,\3,\5,\u017d\n,\3-\3-\3-\3-\3-\3-\3-\3-\3-\3")
        buf.write("-\3-\5-\u018a\n-\3.\3.\3.\3.\3.\2\4\60\66/\2\4\6\b\n\f")
        buf.write("\16\20\22\24\26\30\32\34\36 \"$&(*,.\60\62\64\668:<>@")
        buf.write("BDFHJLNPRTVXZ\2\n\4\2\32\32HH\4\2\33\34HH\3\2\36\37\4")
        buf.write("\2##--\3\2!\"\3\2\4\5\4\2\32\32LL\5\2\t\t\f\22\25\27\2")
        buf.write("\u01a6\2_\3\2\2\2\4t\3\2\2\2\6x\3\2\2\2\bz\3\2\2\2\n}")
        buf.write("\3\2\2\2\f\u0080\3\2\2\2\16\u0082\3\2\2\2\20\u0087\3\2")
        buf.write("\2\2\22\u008a\3\2\2\2\24\u008f\3\2\2\2\26\u0097\3\2\2")
        buf.write("\2\30\u009a\3\2\2\2\32\u009d\3\2\2\2\34\u00a0\3\2\2\2")
        buf.write("\36\u00a3\3\2\2\2 \u00a7\3\2\2\2\"\u00ac\3\2\2\2$\u00af")
        buf.write("\3\2\2\2&\u00b9\3\2\2\2(\u00bb\3\2\2\2*\u00bd\3\2\2\2")
        buf.write(",\u00bf\3\2\2\2.\u00c1\3\2\2\2\60\u00ca\3\2\2\2\62\u00d5")
        buf.write("\3\2\2\2\64\u00d7\3\2\2\2\66\u00de\3\2\2\28\u0109\3\2")
        buf.write("\2\2:\u011d\3\2\2\2<\u011f\3\2\2\2>\u0121\3\2\2\2@\u012f")
        buf.write("\3\2\2\2B\u0131\3\2\2\2D\u0133\3\2\2\2F\u013f\3\2\2\2")
        buf.write("H\u0147\3\2\2\2J\u014b\3\2\2\2L\u0151\3\2\2\2N\u0160\3")
        buf.write("\2\2\2P\u0164\3\2\2\2R\u0169\3\2\2\2T\u016d\3\2\2\2V\u017c")
        buf.write("\3\2\2\2X\u0189\3\2\2\2Z\u018b\3\2\2\2\\^\5\4\3\2]\\\3")
        buf.write("\2\2\2^a\3\2\2\2_]\3\2\2\2_`\3\2\2\2`b\3\2\2\2a_\3\2\2")
        buf.write("\2bc\7\2\2\3c\3\3\2\2\2du\5\16\b\2eu\5\20\t\2fu\5\22\n")
        buf.write("\2gu\5\24\13\2hu\5\26\f\2iu\5\30\r\2ju\5\34\17\2ku\5\32")
        buf.write("\16\2lu\5\36\20\2mu\5 \21\2nu\5$\23\2ou\5\"\22\2pu\5\6")
        buf.write("\4\2qu\5\b\5\2ru\5Z.\2su\3\2\2\2td\3\2\2\2te\3\2\2\2t")
        buf.write("f\3\2\2\2tg\3\2\2\2th\3\2\2\2ti\3\2\2\2tj\3\2\2\2tk\3")
        buf.write("\2\2\2tl\3\2\2\2tm\3\2\2\2tn\3\2\2\2to\3\2\2\2tp\3\2\2")
        buf.write("\2tq\3\2\2\2tr\3\2\2\2ts\3\2\2\2uv\3\2\2\2vw\7\64\2\2")
        buf.write("w\5\3\2\2\2xy\7\3\2\2y\7\3\2\2\2z{\7\30\2\2{|\7>\2\2|")
        buf.write("\t\3\2\2\2}~\7\7\2\2~\177\5\f\7\2\177\13\3\2\2\2\u0080")
        buf.write("\u0081\7H\2\2\u0081\r\3\2\2\2\u0082\u0083\7\6\2\2\u0083")
        buf.write("\u0085\7H\2\2\u0084\u0086\5\n\6\2\u0085\u0084\3\2\2\2")
        buf.write("\u0085\u0086\3\2\2\2\u0086\17\3\2\2\2\u0087\u0088\7\b")
        buf.write("\2\2\u0088\u0089\7H\2\2\u0089\21\3\2\2\2\u008a\u008b\7")
        buf.write("\t\2\2\u008b\u008d\t\2\2\2\u008c\u008e\5\n\6\2\u008d\u008c")
        buf.write("\3\2\2\2\u008d\u008e\3\2\2\2\u008e\23\3\2\2\2\u008f\u0090")
        buf.write("\7\n\2\2\u0090\u0092\t\3\2\2\u0091\u0093\5\n\6\2\u0092")
        buf.write("\u0091\3\2\2\2\u0092\u0093\3\2\2\2\u0093\u0094\3\2\2\2")
        buf.write("\u0094\u0095\7\13\2\2\u0095\u0096\7L\2\2\u0096\25\3\2")
        buf.write("\2\2\u0097\u0098\7\r\2\2\u0098\u0099\5R*\2\u0099\27\3")
        buf.write("\2\2\2\u009a\u009b\7\16\2\2\u009b\u009c\5H%\2\u009c\31")
        buf.write("\3\2\2\2\u009d\u009e\7\20\2\2\u009e\u009f\5H%\2\u009f")
        buf.write("\33\3\2\2\2\u00a0\u00a1\7\17\2\2\u00a1\u00a2\5J&\2\u00a2")
        buf.write("\35\3\2\2\2\u00a3\u00a4\7\21\2\2\u00a4\u00a5\5H%\2\u00a5")
        buf.write("\37\3\2\2\2\u00a6\u00a8\7\4\2\2\u00a7\u00a6\3\2\2\2\u00a7")
        buf.write("\u00a8\3\2\2\2\u00a8\u00a9\3\2\2\2\u00a9\u00aa\7\22\2")
        buf.write("\2\u00aa\u00ab\7L\2\2\u00ab!\3\2\2\2\u00ac\u00ad\7\24")
        buf.write("\2\2\u00ad\u00ae\t\4\2\2\u00ae#\3\2\2\2\u00af\u00b1\7")
        buf.write("\23\2\2\u00b0\u00b2\5(\25\2\u00b1\u00b0\3\2\2\2\u00b1")
        buf.write("\u00b2\3\2\2\2\u00b2\u00b3\3\2\2\2\u00b3\u00b4\5*\26\2")
        buf.write("\u00b4\u00b5\7\65\2\2\u00b5\u00b6\5&\24\2\u00b6%\3\2\2")
        buf.write("\2\u00b7\u00ba\5.\30\2\u00b8\u00ba\5,\27\2\u00b9\u00b7")
        buf.write("\3\2\2\2\u00b9\u00b8\3\2\2\2\u00ba\'\3\2\2\2\u00bb\u00bc")
        buf.write("\7\5\2\2\u00bc)\3\2\2\2\u00bd\u00be\7L\2\2\u00be+\3\2")
        buf.write("\2\2\u00bf\u00c0\5D#\2\u00c0-\3\2\2\2\u00c1\u00c2\7 \2")
        buf.write("\2\u00c2\u00c3\5\60\31\2\u00c3/\3\2\2\2\u00c4\u00c5\b")
        buf.write("\31\1\2\u00c5\u00c6\5\62\32\2\u00c6\u00c7\5\60\31\6\u00c7")
        buf.write("\u00cb\3\2\2\2\u00c8\u00cb\5\64\33\2\u00c9\u00cb\5\66")
        buf.write("\34\2\u00ca\u00c4\3\2\2\2\u00ca\u00c8\3\2\2\2\u00ca\u00c9")
        buf.write("\3\2\2\2\u00cb\u00d2\3\2\2\2\u00cc\u00cd\f\5\2\2\u00cd")
        buf.write("\u00ce\5> \2\u00ce\u00cf\5\60\31\6\u00cf\u00d1\3\2\2\2")
        buf.write("\u00d0\u00cc\3\2\2\2\u00d1\u00d4\3\2\2\2\u00d2\u00d0\3")
        buf.write("\2\2\2\u00d2\u00d3\3\2\2\2\u00d3\61\3\2\2\2\u00d4\u00d2")
        buf.write("\3\2\2\2\u00d5\u00d6\t\5\2\2\u00d6\63\3\2\2\2\u00d7\u00d8")
        buf.write("\5\66\34\2\u00d8\u00da\7)\2\2\u00d9\u00db\7#\2\2\u00da")
        buf.write("\u00d9\3\2\2\2\u00da\u00db\3\2\2\2\u00db\u00dc\3\2\2\2")
        buf.write("\u00dc\u00dd\7D\2\2\u00dd\65\3\2\2\2\u00de\u00df\b\34")
        buf.write("\1\2\u00df\u00e0\5:\36\2\u00e0\u0105\3\2\2\2\u00e1\u00e2")
        buf.write("\f\6\2\2\u00e2\u00e3\5@!\2\u00e3\u00e4\5\66\34\7\u00e4")
        buf.write("\u0104\3\2\2\2\u00e5\u00e7\f\5\2\2\u00e6\u00e8\7#\2\2")
        buf.write("\u00e7\u00e6\3\2\2\2\u00e7\u00e8\3\2\2\2\u00e8\u00e9\3")
        buf.write("\2\2\2\u00e9\u00ea\7+\2\2\u00ea\u00eb\5\66\34\2\u00eb")
        buf.write("\u00ec\7!\2\2\u00ec\u00ed\5\66\34\6\u00ed\u0104\3\2\2")
        buf.write("\2\u00ee\u00f0\f\b\2\2\u00ef\u00f1\7#\2\2\u00f0\u00ef")
        buf.write("\3\2\2\2\u00f0\u00f1\3\2\2\2\u00f1\u00f2\3\2\2\2\u00f2")
        buf.write("\u00f3\7F\2\2\u00f3\u00f4\78\2\2\u00f4\u00f5\5\60\31\2")
        buf.write("\u00f5\u00f6\79\2\2\u00f6\u0104\3\2\2\2\u00f7\u00f8\f")
        buf.write("\7\2\2\u00f8\u00f9\7)\2\2\u00f9\u0104\58\35\2\u00fa\u00fc")
        buf.write("\f\4\2\2\u00fb\u00fd\7#\2\2\u00fc\u00fb\3\2\2\2\u00fc")
        buf.write("\u00fd\3\2\2\2\u00fd\u00fe\3\2\2\2\u00fe\u00ff\7*\2\2")
        buf.write("\u00ff\u0101\5\66\34\2\u0100\u0102\7H\2\2\u0101\u0100")
        buf.write("\3\2\2\2\u0101\u0102\3\2\2\2\u0102\u0104\3\2\2\2\u0103")
        buf.write("\u00e1\3\2\2\2\u0103\u00e5\3\2\2\2\u0103\u00ee\3\2\2\2")
        buf.write("\u0103\u00f7\3\2\2\2\u0103\u00fa\3\2\2\2\u0104\u0107\3")
        buf.write("\2\2\2\u0105\u0103\3\2\2\2\u0105\u0106\3\2\2\2\u0106\67")
        buf.write("\3\2\2\2\u0107\u0105\3\2\2\2\u0108\u010a\7#\2\2\u0109")
        buf.write("\u0108\3\2\2\2\u0109\u010a\3\2\2\2\u010a\u010b\3\2\2\2")
        buf.write("\u010b\u010c\7E\2\2\u010c9\3\2\2\2\u010d\u011e\5X-\2\u010e")
        buf.write("\u011e\5D#\2\u010f\u0110\5<\37\2\u0110\u0111\5:\36\2\u0111")
        buf.write("\u011e\3\2\2\2\u0112\u0113\78\2\2\u0113\u0118\5\60\31")
        buf.write("\2\u0114\u0115\7\67\2\2\u0115\u0117\5\60\31\2\u0116\u0114")
        buf.write("\3\2\2\2\u0117\u011a\3\2\2\2\u0118\u0116\3\2\2\2\u0118")
        buf.write("\u0119\3\2\2\2\u0119\u011b\3\2\2\2\u011a\u0118\3\2\2\2")
        buf.write("\u011b\u011c\79\2\2\u011c\u011e\3\2\2\2\u011d\u010d\3")
        buf.write("\2\2\2\u011d\u010e\3\2\2\2\u011d\u010f\3\2\2\2\u011d\u0112")
        buf.write("\3\2\2\2\u011e;\3\2\2\2\u011f\u0120\7#\2\2\u0120=\3\2")
        buf.write("\2\2\u0121\u0122\t\6\2\2\u0122?\3\2\2\2\u0123\u0130\7")
        buf.write("$\2\2\u0124\u0130\7%\2\2\u0125\u0130\7\'\2\2\u0126\u0130")
        buf.write("\7&\2\2\u0127\u0130\7(\2\2\u0128\u0129\7,\2\2\u0129\u0130")
        buf.write("\7.\2\2\u012a\u0130\7/\2\2\u012b\u0130\7\60\2\2\u012c")
        buf.write("\u0130\7\61\2\2\u012d\u0130\7\62\2\2\u012e\u0130\7\63")
        buf.write("\2\2\u012f\u0123\3\2\2\2\u012f\u0124\3\2\2\2\u012f\u0125")
        buf.write("\3\2\2\2\u012f\u0126\3\2\2\2\u012f\u0127\3\2\2\2\u012f")
        buf.write("\u0128\3\2\2\2\u012f\u012a\3\2\2\2\u012f\u012b\3\2\2\2")
        buf.write("\u012f\u012c\3\2\2\2\u012f\u012d\3\2\2\2\u012f\u012e\3")
        buf.write("\2\2\2\u0130A\3\2\2\2\u0131\u0132\5X-\2\u0132C\3\2\2\2")
        buf.write("\u0133\u0134\5F$\2\u0134\u0135\78\2\2\u0135\u013a\5X-")
        buf.write("\2\u0136\u0137\7\67\2\2\u0137\u0139\5X-\2\u0138\u0136")
        buf.write("\3\2\2\2\u0139\u013c\3\2\2\2\u013a\u0138\3\2\2\2\u013a")
        buf.write("\u013b\3\2\2\2\u013b\u013d\3\2\2\2\u013c\u013a\3\2\2\2")
        buf.write("\u013d\u013e\79\2\2\u013eE\3\2\2\2\u013f\u0144\7L\2\2")
        buf.write("\u0140\u0141\7\66\2\2\u0141\u0143\7L\2\2\u0142\u0140\3")
        buf.write("\2\2\2\u0143\u0146\3\2\2\2\u0144\u0142\3\2\2\2\u0144\u0145")
        buf.write("\3\2\2\2\u0145G\3\2\2\2\u0146\u0144\3\2\2\2\u0147\u0148")
        buf.write("\7L\2\2\u0148\u0149\7\65\2\2\u0149\u014a\5D#\2\u014aI")
        buf.write("\3\2\2\2\u014b\u014c\7L\2\2\u014c\u014f\7\65\2\2\u014d")
        buf.write("\u0150\5V,\2\u014e\u0150\7H\2\2\u014f\u014d\3\2\2\2\u014f")
        buf.write("\u014e\3\2\2\2\u0150K\3\2\2\2\u0151\u0152\t\7\2\2\u0152")
        buf.write("M\3\2\2\2\u0153\u0154\7<\2\2\u0154\u0159\5P)\2\u0155\u0156")
        buf.write("\7\67\2\2\u0156\u0158\5P)\2\u0157\u0155\3\2\2\2\u0158")
        buf.write("\u015b\3\2\2\2\u0159\u0157\3\2\2\2\u0159\u015a\3\2\2\2")
        buf.write("\u015a\u015c\3\2\2\2\u015b\u0159\3\2\2\2\u015c\u015d\7")
        buf.write("=\2\2\u015d\u0161\3\2\2\2\u015e\u015f\7<\2\2\u015f\u0161")
        buf.write("\7=\2\2\u0160\u0153\3\2\2\2\u0160\u015e\3\2\2\2\u0161")
        buf.write("O\3\2\2\2\u0162\u0165\7H\2\2\u0163\u0165\5T+\2\u0164\u0162")
        buf.write("\3\2\2\2\u0164\u0163\3\2\2\2\u0165\u0166\3\2\2\2\u0166")
        buf.write("\u0167\7\65\2\2\u0167\u0168\5X-\2\u0168Q\3\2\2\2\u0169")
        buf.write("\u016a\t\b\2\2\u016a\u016b\7\65\2\2\u016b\u016c\5X-\2")
        buf.write("\u016cS\3\2\2\2\u016d\u016e\t\t\2\2\u016eU\3\2\2\2\u016f")
        buf.write("\u0170\7:\2\2\u0170\u0175\5X-\2\u0171\u0172\7\67\2\2\u0172")
        buf.write("\u0174\5X-\2\u0173\u0171\3\2\2\2\u0174\u0177\3\2\2\2\u0175")
        buf.write("\u0173\3\2\2\2\u0175\u0176\3\2\2\2\u0176\u0178\3\2\2\2")
        buf.write("\u0177\u0175\3\2\2\2\u0178\u0179\7;\2\2\u0179\u017d\3")
        buf.write("\2\2\2\u017a\u017b\7:\2\2\u017b\u017d\7;\2\2\u017c\u016f")
        buf.write("\3\2\2\2\u017c\u017a\3\2\2\2\u017dW\3\2\2\2\u017e\u018a")
        buf.write("\7H\2\2\u017f\u018a\7>\2\2\u0180\u018a\7B\2\2\u0181\u018a")
        buf.write("\5N(\2\u0182\u018a\5V,\2\u0183\u018a\7D\2\2\u0184\u018a")
        buf.write("\7E\2\2\u0185\u018a\7\35\2\2\u0186\u018a\7L\2\2\u0187")
        buf.write("\u018a\5F$\2\u0188\u018a\7M\2\2\u0189\u017e\3\2\2\2\u0189")
        buf.write("\u017f\3\2\2\2\u0189\u0180\3\2\2\2\u0189\u0181\3\2\2\2")
        buf.write("\u0189\u0182\3\2\2\2\u0189\u0183\3\2\2\2\u0189\u0184\3")
        buf.write("\2\2\2\u0189\u0185\3\2\2\2\u0189\u0186\3\2\2\2\u0189\u0187")
        buf.write("\3\2\2\2\u0189\u0188\3\2\2\2\u018aY\3\2\2\2\u018b\u018c")
        buf.write("\7\31\2\2\u018c\u018d\7\65\2\2\u018d\u018e\7D\2\2\u018e")
        buf.write("[\3\2\2\2 _t\u0085\u008d\u0092\u00a7\u00b1\u00b9\u00ca")
        buf.write("\u00d2\u00da\u00e7\u00f0\u00fc\u0101\u0103\u0105\u0109")
        buf.write("\u0118\u011d\u012f\u013a\u0144\u014f\u0159\u0160\u0164")
        buf.write("\u0175\u017c\u0189")
        return buf.getvalue()


class nlpql_parserParser ( Parser ):

    grammarFileName = "nlpql_parser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'debug'", "'default'", "'final'", "'phenotype'", 
                     "'version'", "'description'", "'datamodel'", "'include'", 
                     "'called'", "'code'", "'codesystem'", "'valueset'", 
                     "'termset'", "'documentset'", "'cohort'", "'population'", 
                     "'define'", "'context'", "'minimum_value'", "'maximum_value'", 
                     "'enum_list'", "'limit'", "'output_feature_matrix'", 
                     "'OMOP'", "'ClarityCore'", "'OHDSIHelpers'", "'All'", 
                     "'Patient'", "'Document'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'>'", "'<'", "'<='", "'>='", 
                     "'=='", "<INVALID>", "<INVALID>", "<INVALID>", "'!='", 
                     "'!'", "'+'", "'-'", "'*'", "'/'", "'^'", "'%'", "';'", 
                     "':'", "'.'", "','", "'('", "')'", "'['", "']'", "'{'", 
                     "'}'" ]

    symbolicNames = [ "<INVALID>", "DEBUG", "DEFAULT", "FINAL", "PHENOTYPE_NAME", 
                      "VERSION", "DESCRIPTION", "DATAMODEL", "INCLUDE", 
                      "CALLED", "CODE", "CODE_SYSTEM", "VALUE_SET", "TERM_SET", 
                      "DOCUMENT_SET", "COHORT", "POPULATION", "DEFINE", 
                      "CONTEXT", "MIN_VALUE", "MAX_VALUE", "ENUM_LIST", 
                      "LIMIT", "OUTPUT_FEATURE_MATRIX", "OMOP", "CLARITY_CORE", 
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
    RULE_obj = 38
    RULE_pair = 39
    RULE_identifierPair = 40
    RULE_named = 41
    RULE_array = 42
    RULE_value = 43
    RULE_outputFeatureMatrix = 44

    ruleNames =  [ "validExpression", "statement", "debugger", "limit", 
                   "version", "versionValue", "phenotypeName", "description", 
                   "dataModel", "include", "codeSystem", "valueSet", "documentSet", 
                   "termSet", "cohort", "population", "context", "define", 
                   "defineSubject", "finalModifier", "defineName", "dataEntity", 
                   "operation", "expression", "notOperator", "predicateBoolean", 
                   "predicate", "nullNotnull", "expressionAtom", "unaryOperator", 
                   "logicalOperator", "comparisonOperator", "operand", "methodCall", 
                   "qualifiedName", "pairMethod", "pairArray", "modifiers", 
                   "obj", "pair", "identifierPair", "named", "array", "value", 
                   "outputFeatureMatrix" ]

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
    DOCUMENT_SET=14
    COHORT=15
    POPULATION=16
    DEFINE=17
    CONTEXT=18
    MIN_VALUE=19
    MAX_VALUE=20
    ENUM_LIST=21
    LIMIT=22
    OUTPUT_FEATURE_MATRIX=23
    OMOP=24
    CLARITY_CORE=25
    OHDSI_HELPERS=26
    ALL=27
    PATIENT=28
    DOCUMENT=29
    WHERE=30
    AND=31
    OR=32
    NOT=33
    GT=34
    LT=35
    LTE=36
    GTE=37
    EQUAL=38
    IS=39
    LIKE=40
    BETWEEN=41
    NOT_EQUAL=42
    BANG=43
    PLUS=44
    MINUS=45
    MULT=46
    DIV=47
    CARET=48
    MOD=49
    SEMI=50
    COLON=51
    DOT=52
    COMMA=53
    L_PAREN=54
    R_PAREN=55
    L_BRACKET=56
    R_BRACKET=57
    L_CURLY=58
    R_CURLY=59
    DECIMAL=60
    HEX=61
    OCT=62
    BINARY=63
    FLOAT=64
    HEX_FLOAT=65
    BOOL=66
    NULL=67
    IN=68
    CHAR=69
    STRING=70
    WS=71
    COMMENT=72
    LINE_COMMENT=73
    IDENTIFIER=74
    TIME=75

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
            self.state = 93
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << nlpql_parserParser.DEBUG) | (1 << nlpql_parserParser.DEFAULT) | (1 << nlpql_parserParser.PHENOTYPE_NAME) | (1 << nlpql_parserParser.DESCRIPTION) | (1 << nlpql_parserParser.DATAMODEL) | (1 << nlpql_parserParser.INCLUDE) | (1 << nlpql_parserParser.CODE_SYSTEM) | (1 << nlpql_parserParser.VALUE_SET) | (1 << nlpql_parserParser.TERM_SET) | (1 << nlpql_parserParser.DOCUMENT_SET) | (1 << nlpql_parserParser.COHORT) | (1 << nlpql_parserParser.POPULATION) | (1 << nlpql_parserParser.DEFINE) | (1 << nlpql_parserParser.CONTEXT) | (1 << nlpql_parserParser.LIMIT) | (1 << nlpql_parserParser.OUTPUT_FEATURE_MATRIX) | (1 << nlpql_parserParser.SEMI))) != 0):
                self.state = 90
                self.statement()
                self.state = 95
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 96
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


        def outputFeatureMatrix(self):
            return self.getTypedRuleContext(nlpql_parserParser.OutputFeatureMatrixContext,0)


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
                self.state = 98
                self.phenotypeName()
                pass
            elif token in [nlpql_parserParser.DESCRIPTION]:
                self.state = 99
                self.description()
                pass
            elif token in [nlpql_parserParser.DATAMODEL]:
                self.state = 100
                self.dataModel()
                pass
            elif token in [nlpql_parserParser.INCLUDE]:
                self.state = 101
                self.include()
                pass
            elif token in [nlpql_parserParser.CODE_SYSTEM]:
                self.state = 102
                self.codeSystem()
                pass
            elif token in [nlpql_parserParser.VALUE_SET]:
                self.state = 103
                self.valueSet()
                pass
            elif token in [nlpql_parserParser.TERM_SET]:
                self.state = 104
                self.termSet()
                pass
            elif token in [nlpql_parserParser.DOCUMENT_SET]:
                self.state = 105
                self.documentSet()
                pass
            elif token in [nlpql_parserParser.COHORT]:
                self.state = 106
                self.cohort()
                pass
            elif token in [nlpql_parserParser.DEFAULT, nlpql_parserParser.POPULATION]:
                self.state = 107
                self.population()
                pass
            elif token in [nlpql_parserParser.DEFINE]:
                self.state = 108
                self.define()
                pass
            elif token in [nlpql_parserParser.CONTEXT]:
                self.state = 109
                self.context()
                pass
            elif token in [nlpql_parserParser.DEBUG]:
                self.state = 110
                self.debugger()
                pass
            elif token in [nlpql_parserParser.LIMIT]:
                self.state = 111
                self.limit()
                pass
            elif token in [nlpql_parserParser.OUTPUT_FEATURE_MATRIX]:
                self.state = 112
                self.outputFeatureMatrix()
                pass
            elif token in [nlpql_parserParser.SEMI]:
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
            if not(((((_la - 25)) & ~0x3f) == 0 and ((1 << (_la - 25)) & ((1 << (nlpql_parserParser.CLARITY_CORE - 25)) | (1 << (nlpql_parserParser.OHDSI_HELPERS - 25)) | (1 << (nlpql_parserParser.STRING - 25)))) != 0)):
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


        def getRuleIndex(self):
            return nlpql_parserParser.RULE_defineSubject




    def defineSubject(self):

        localctx = nlpql_parserParser.DefineSubjectContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_defineSubject)
        try:
            self.state = 183
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
            self.state = 185
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
            self.state = 187
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
            self.state = 189
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
            self.state = 191
            self.match(nlpql_parserParser.WHERE)
            self.state = 192
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
            self.state = 200
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,8,self._ctx)
            if la_ == 1:
                self.state = 195
                self.notOperator()
                self.state = 196
                self.expression(4)
                pass

            elif la_ == 2:
                self.state = 198
                self.predicateBoolean()
                pass

            elif la_ == 3:
                self.state = 199
                self.predicate(0)
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 208
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,9,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = nlpql_parserParser.ExpressionContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                    self.state = 202
                    if not self.precpred(self._ctx, 3):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                    self.state = 203
                    self.logicalOperator()
                    self.state = 204
                    self.expression(4) 
                self.state = 210
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
            self.state = 211
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
            self.state = 213
            self.predicate(0)
            self.state = 214
            self.match(nlpql_parserParser.IS)
            self.state = 216
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.NOT:
                self.state = 215
                self.match(nlpql_parserParser.NOT)


            self.state = 218
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
            self.state = 221
            self.expressionAtom()
            self._ctx.stop = self._input.LT(-1)
            self.state = 259
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,16,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 257
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,15,self._ctx)
                    if la_ == 1:
                        localctx = nlpql_parserParser.PredicateContext(self, _parentctx, _parentState)
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_predicate)
                        self.state = 223
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 224
                        self.comparisonOperator()
                        self.state = 225
                        localctx.right = self.predicate(5)
                        pass

                    elif la_ == 2:
                        localctx = nlpql_parserParser.PredicateContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_predicate)
                        self.state = 227
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 229
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if _la==nlpql_parserParser.NOT:
                            self.state = 228
                            self.match(nlpql_parserParser.NOT)


                        self.state = 231
                        self.match(nlpql_parserParser.BETWEEN)
                        self.state = 232
                        self.predicate(0)
                        self.state = 233
                        self.match(nlpql_parserParser.AND)
                        self.state = 234
                        self.predicate(4)
                        pass

                    elif la_ == 3:
                        localctx = nlpql_parserParser.PredicateContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_predicate)
                        self.state = 236
                        if not self.precpred(self._ctx, 6):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 6)")
                        self.state = 238
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if _la==nlpql_parserParser.NOT:
                            self.state = 237
                            self.match(nlpql_parserParser.NOT)


                        self.state = 240
                        self.match(nlpql_parserParser.IN)
                        self.state = 241
                        self.match(nlpql_parserParser.L_PAREN)

                        self.state = 242
                        self.expression(0)
                        self.state = 243
                        self.match(nlpql_parserParser.R_PAREN)
                        pass

                    elif la_ == 4:
                        localctx = nlpql_parserParser.PredicateContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_predicate)
                        self.state = 245
                        if not self.precpred(self._ctx, 5):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 5)")
                        self.state = 246
                        self.match(nlpql_parserParser.IS)
                        self.state = 247
                        self.nullNotnull()
                        pass

                    elif la_ == 5:
                        localctx = nlpql_parserParser.PredicateContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_predicate)
                        self.state = 248
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 250
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if _la==nlpql_parserParser.NOT:
                            self.state = 249
                            self.match(nlpql_parserParser.NOT)


                        self.state = 252
                        self.match(nlpql_parserParser.LIKE)
                        self.state = 253
                        self.predicate(0)
                        self.state = 255
                        self._errHandler.sync(self)
                        la_ = self._interp.adaptivePredict(self._input,14,self._ctx)
                        if la_ == 1:
                            self.state = 254
                            self.match(nlpql_parserParser.STRING)


                        pass

             
                self.state = 261
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
            self.state = 263
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==nlpql_parserParser.NOT:
                self.state = 262
                self.match(nlpql_parserParser.NOT)


            self.state = 265
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
            self.state = 283
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,19,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 267
                self.value()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 268
                self.methodCall()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 269
                self.unaryOperator()
                self.state = 270
                self.expressionAtom()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 272
                self.match(nlpql_parserParser.L_PAREN)
                self.state = 273
                self.expression(0)
                self.state = 278
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==nlpql_parserParser.COMMA:
                    self.state = 274
                    self.match(nlpql_parserParser.COMMA)
                    self.state = 275
                    self.expression(0)
                    self.state = 280
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 281
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
            self.state = 285
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
        self.enterRule(localctx, 60, self.RULE_logicalOperator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 287
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
        self.enterRule(localctx, 62, self.RULE_comparisonOperator)
        try:
            self.state = 301
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [nlpql_parserParser.GT]:
                self.enterOuterAlt(localctx, 1)
                self.state = 289
                self.match(nlpql_parserParser.GT)
                pass
            elif token in [nlpql_parserParser.LT]:
                self.enterOuterAlt(localctx, 2)
                self.state = 290
                self.match(nlpql_parserParser.LT)
                pass
            elif token in [nlpql_parserParser.GTE]:
                self.enterOuterAlt(localctx, 3)
                self.state = 291
                self.match(nlpql_parserParser.GTE)
                pass
            elif token in [nlpql_parserParser.LTE]:
                self.enterOuterAlt(localctx, 4)
                self.state = 292
                self.match(nlpql_parserParser.LTE)
                pass
            elif token in [nlpql_parserParser.EQUAL]:
                self.enterOuterAlt(localctx, 5)
                self.state = 293
                self.match(nlpql_parserParser.EQUAL)
                pass
            elif token in [nlpql_parserParser.NOT_EQUAL]:
                self.enterOuterAlt(localctx, 6)
                self.state = 294
                self.match(nlpql_parserParser.NOT_EQUAL)
                self.state = 295
                self.match(nlpql_parserParser.PLUS)
                pass
            elif token in [nlpql_parserParser.MINUS]:
                self.enterOuterAlt(localctx, 7)
                self.state = 296
                self.match(nlpql_parserParser.MINUS)
                pass
            elif token in [nlpql_parserParser.MULT]:
                self.enterOuterAlt(localctx, 8)
                self.state = 297
                self.match(nlpql_parserParser.MULT)
                pass
            elif token in [nlpql_parserParser.DIV]:
                self.enterOuterAlt(localctx, 9)
                self.state = 298
                self.match(nlpql_parserParser.DIV)
                pass
            elif token in [nlpql_parserParser.CARET]:
                self.enterOuterAlt(localctx, 10)
                self.state = 299
                self.match(nlpql_parserParser.CARET)
                pass
            elif token in [nlpql_parserParser.MOD]:
                self.enterOuterAlt(localctx, 11)
                self.state = 300
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
            self.state = 303
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
            self.state = 305
            self.qualifiedName()
            self.state = 306
            self.match(nlpql_parserParser.L_PAREN)
            self.state = 307
            self.value()
            self.state = 312
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==nlpql_parserParser.COMMA:
                self.state = 308
                self.match(nlpql_parserParser.COMMA)
                self.state = 309
                self.value()
                self.state = 314
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 315
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
            self.state = 317
            self.match(nlpql_parserParser.IDENTIFIER)
            self.state = 322
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,22,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 318
                    self.match(nlpql_parserParser.DOT)
                    self.state = 319
                    self.match(nlpql_parserParser.IDENTIFIER) 
                self.state = 324
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
            self.state = 325
            self.match(nlpql_parserParser.IDENTIFIER)
            self.state = 326
            self.match(nlpql_parserParser.COLON)
            self.state = 327
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
            self.state = 329
            self.match(nlpql_parserParser.IDENTIFIER)
            self.state = 330
            self.match(nlpql_parserParser.COLON)
            self.state = 333
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [nlpql_parserParser.L_BRACKET]:
                self.state = 331
                self.array()
                pass
            elif token in [nlpql_parserParser.STRING]:
                self.state = 332
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
            self.state = 335
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
        self.enterRule(localctx, 76, self.RULE_obj)
        self._la = 0 # Token type
        try:
            self.state = 350
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,25,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 337
                self.match(nlpql_parserParser.L_CURLY)
                self.state = 338
                self.pair()
                self.state = 343
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==nlpql_parserParser.COMMA:
                    self.state = 339
                    self.match(nlpql_parserParser.COMMA)
                    self.state = 340
                    self.pair()
                    self.state = 345
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 346
                self.match(nlpql_parserParser.R_CURLY)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 348
                self.match(nlpql_parserParser.L_CURLY)
                self.state = 349
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
        self.enterRule(localctx, 78, self.RULE_pair)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 354
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [nlpql_parserParser.STRING]:
                self.state = 352
                self.match(nlpql_parserParser.STRING)
                pass
            elif token in [nlpql_parserParser.DATAMODEL, nlpql_parserParser.CODE, nlpql_parserParser.CODE_SYSTEM, nlpql_parserParser.VALUE_SET, nlpql_parserParser.TERM_SET, nlpql_parserParser.DOCUMENT_SET, nlpql_parserParser.COHORT, nlpql_parserParser.POPULATION, nlpql_parserParser.MIN_VALUE, nlpql_parserParser.MAX_VALUE, nlpql_parserParser.ENUM_LIST]:
                self.state = 353
                self.named()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 356
            self.match(nlpql_parserParser.COLON)
            self.state = 357
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
        self.enterRule(localctx, 80, self.RULE_identifierPair)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 359
            _la = self._input.LA(1)
            if not(_la==nlpql_parserParser.OMOP or _la==nlpql_parserParser.IDENTIFIER):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 360
            self.match(nlpql_parserParser.COLON)
            self.state = 361
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
        self.enterRule(localctx, 82, self.RULE_named)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 363
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << nlpql_parserParser.DATAMODEL) | (1 << nlpql_parserParser.CODE) | (1 << nlpql_parserParser.CODE_SYSTEM) | (1 << nlpql_parserParser.VALUE_SET) | (1 << nlpql_parserParser.TERM_SET) | (1 << nlpql_parserParser.DOCUMENT_SET) | (1 << nlpql_parserParser.COHORT) | (1 << nlpql_parserParser.POPULATION) | (1 << nlpql_parserParser.MIN_VALUE) | (1 << nlpql_parserParser.MAX_VALUE) | (1 << nlpql_parserParser.ENUM_LIST))) != 0)):
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
        self.enterRule(localctx, 84, self.RULE_array)
        self._la = 0 # Token type
        try:
            self.state = 378
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,28,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 365
                self.match(nlpql_parserParser.L_BRACKET)
                self.state = 366
                self.value()
                self.state = 371
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==nlpql_parserParser.COMMA:
                    self.state = 367
                    self.match(nlpql_parserParser.COMMA)
                    self.state = 368
                    self.value()
                    self.state = 373
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 374
                self.match(nlpql_parserParser.R_BRACKET)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 376
                self.match(nlpql_parserParser.L_BRACKET)
                self.state = 377
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
        self.enterRule(localctx, 86, self.RULE_value)
        try:
            self.state = 391
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,29,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 380
                self.match(nlpql_parserParser.STRING)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 381
                self.match(nlpql_parserParser.DECIMAL)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 382
                self.match(nlpql_parserParser.FLOAT)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 383
                self.obj()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 384
                self.array()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 385
                self.match(nlpql_parserParser.BOOL)
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 386
                self.match(nlpql_parserParser.NULL)
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 387
                self.match(nlpql_parserParser.ALL)
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 388
                self.match(nlpql_parserParser.IDENTIFIER)
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 389
                self.qualifiedName()
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 390
                self.match(nlpql_parserParser.TIME)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class OutputFeatureMatrixContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OUTPUT_FEATURE_MATRIX(self):
            return self.getToken(nlpql_parserParser.OUTPUT_FEATURE_MATRIX, 0)

        def COLON(self):
            return self.getToken(nlpql_parserParser.COLON, 0)

        def BOOL(self):
            return self.getToken(nlpql_parserParser.BOOL, 0)

        def getRuleIndex(self):
            return nlpql_parserParser.RULE_outputFeatureMatrix




    def outputFeatureMatrix(self):

        localctx = nlpql_parserParser.OutputFeatureMatrixContext(self, self._ctx, self.state)
        self.enterRule(localctx, 88, self.RULE_outputFeatureMatrix)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 393
            self.match(nlpql_parserParser.OUTPUT_FEATURE_MATRIX)
            self.state = 394
            self.match(nlpql_parserParser.COLON)
            self.state = 395
            self.match(nlpql_parserParser.BOOL)
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
         




