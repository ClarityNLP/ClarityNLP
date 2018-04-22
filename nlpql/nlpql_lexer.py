# Generated from nlpql_lexer.g4 by ANTLR 4.7.1
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2H")
        buf.write("\u0305\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
        buf.write("\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r")
        buf.write("\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22\4\23")
        buf.write("\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30")
        buf.write("\4\31\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35\4\36")
        buf.write("\t\36\4\37\t\37\4 \t \4!\t!\4\"\t\"\4#\t#\4$\t$\4%\t%")
        buf.write("\4&\t&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t+\4,\t,\4-\t-\4.")
        buf.write("\t.\4/\t/\4\60\t\60\4\61\t\61\4\62\t\62\4\63\t\63\4\64")
        buf.write("\t\64\4\65\t\65\4\66\t\66\4\67\t\67\48\t8\49\t9\4:\t:")
        buf.write("\4;\t;\4<\t<\4=\t=\4>\t>\4?\t?\4@\t@\4A\tA\4B\tB\4C\t")
        buf.write("C\4D\tD\4E\tE\4F\tF\4G\tG\4H\tH\4I\tI\4J\tJ\4K\tK\4L\t")
        buf.write("L\4M\tM\4N\tN\4O\tO\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3")
        buf.write("\3\3\3\3\3\3\3\3\3\3\3\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4")
        buf.write("\3\4\3\4\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\6\3\6\3\6\3")
        buf.write("\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\7\3\7\3\7\3\7\3\7")
        buf.write("\3\7\3\7\3\7\3\7\3\7\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3")
        buf.write("\t\3\t\3\t\3\t\3\t\3\t\3\t\3\n\3\n\3\n\3\n\3\n\3\n\3\n")
        buf.write("\3\n\3\n\3\n\3\n\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3")
        buf.write("\13\3\13\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3\r\3\r\3\r\3")
        buf.write("\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\16\3\16\3\16\3\16")
        buf.write("\3\16\3\16\3\16\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17")
        buf.write("\3\17\3\17\3\17\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\21")
        buf.write("\3\21\3\21\3\21\3\21\3\21\3\21\3\21\3\22\3\22\3\22\3\22")
        buf.write("\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\23")
        buf.write("\3\23\3\23\3\23\3\23\3\23\3\23\3\23\3\23\3\23\3\23\3\23")
        buf.write("\3\23\3\23\3\24\3\24\3\24\3\24\3\24\3\25\3\25\3\25\3\25")
        buf.write("\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\26\3\26\3\26")
        buf.write("\3\26\3\26\3\26\3\26\3\26\3\26\3\26\3\26\3\26\3\26\3\27")
        buf.write("\3\27\3\27\3\27\3\30\3\30\3\30\3\30\3\30\3\30\3\30\3\30")
        buf.write("\3\31\3\31\3\31\3\31\3\31\3\31\3\31\3\31\3\31\3\32\3\32")
        buf.write("\3\32\3\32\3\32\3\32\3\32\3\32\3\32\3\32\5\32\u0187\n")
        buf.write("\32\3\33\3\33\3\33\3\33\3\33\3\33\5\33\u018f\n\33\3\34")
        buf.write("\3\34\3\34\3\34\5\34\u0195\n\34\3\35\3\35\3\35\3\35\3")
        buf.write("\35\3\35\5\35\u019d\n\35\3\36\3\36\3\37\3\37\3 \3 \3 ")
        buf.write("\3!\3!\3!\3\"\3\"\3\"\3#\3#\3#\3#\5#\u01b0\n#\3$\3$\3")
        buf.write("$\3$\3$\3$\3$\3$\5$\u01ba\n$\3%\3%\3%\3%\3%\3%\3%\3%\3")
        buf.write("%\3%\3%\3%\3%\3%\5%\u01ca\n%\3&\3&\3&\3\'\3\'\3(\3(\3")
        buf.write(")\3)\3*\3*\3+\3+\3,\3,\3-\3-\3.\3.\3/\3/\3\60\3\60\3\61")
        buf.write("\3\61\3\62\3\62\3\63\3\63\3\64\3\64\3\65\3\65\3\66\3\66")
        buf.write("\3\67\3\67\38\38\38\58\u01f4\n8\38\68\u01f7\n8\r8\168")
        buf.write("\u01f8\38\58\u01fc\n8\58\u01fe\n8\38\58\u0201\n8\39\3")
        buf.write("9\39\39\79\u0207\n9\f9\169\u020a\139\39\59\u020d\n9\3")
        buf.write("9\59\u0210\n9\3:\3:\7:\u0214\n:\f:\16:\u0217\13:\3:\3")
        buf.write(":\7:\u021b\n:\f:\16:\u021e\13:\3:\5:\u0221\n:\3:\5:\u0224")
        buf.write("\n:\3;\3;\3;\3;\7;\u022a\n;\f;\16;\u022d\13;\3;\5;\u0230")
        buf.write("\n;\3;\5;\u0233\n;\3<\3<\3<\5<\u0238\n<\3<\3<\5<\u023c")
        buf.write("\n<\3<\5<\u023f\n<\3<\5<\u0242\n<\3<\3<\3<\5<\u0247\n")
        buf.write("<\3<\5<\u024a\n<\5<\u024c\n<\3=\3=\3=\3=\5=\u0252\n=\3")
        buf.write("=\5=\u0255\n=\3=\3=\5=\u0259\n=\3=\3=\5=\u025d\n=\3=\3")
        buf.write("=\5=\u0261\n=\3>\3>\3>\3>\3>\3>\3>\3>\3>\3>\3>\3>\3>\3")
        buf.write(">\3>\3>\3>\3>\5>\u0275\n>\3?\3?\3?\3?\3?\3?\3?\3?\3?\3")
        buf.write("?\3?\3?\3?\3?\3?\3?\5?\u0287\n?\3@\3@\3@\3@\5@\u028d\n")
        buf.write("@\3A\3A\3A\5A\u0292\nA\3A\3A\3B\3B\3B\7B\u0299\nB\fB\16")
        buf.write("B\u029c\13B\3B\3B\3C\6C\u02a1\nC\rC\16C\u02a2\3C\3C\3")
        buf.write("D\3D\3D\3D\7D\u02ab\nD\fD\16D\u02ae\13D\3D\3D\3D\3D\3")
        buf.write("D\3E\3E\3E\3E\7E\u02b9\nE\fE\16E\u02bc\13E\3E\3E\3F\3")
        buf.write("F\7F\u02c2\nF\fF\16F\u02c5\13F\3G\3G\3G\3H\3H\5H\u02cc")
        buf.write("\nH\3H\3H\3I\3I\3I\3I\5I\u02d4\nI\3I\5I\u02d7\nI\3I\3")
        buf.write("I\3I\6I\u02dc\nI\rI\16I\u02dd\3I\3I\3I\3I\3I\5I\u02e5")
        buf.write("\nI\3J\3J\3J\7J\u02ea\nJ\fJ\16J\u02ed\13J\3J\5J\u02f0")
        buf.write("\nJ\3K\3K\3L\3L\7L\u02f6\nL\fL\16L\u02f9\13L\3L\5L\u02fc")
        buf.write("\nL\3M\3M\5M\u0300\nM\3N\3N\3O\3O\3\u02ac\2P\3\3\5\4\7")
        buf.write("\5\t\6\13\7\r\b\17\t\21\n\23\13\25\f\27\r\31\16\33\17")
        buf.write("\35\20\37\21!\22#\23%\24\'\25)\26+\27-\30/\31\61\32\63")
        buf.write("\33\65\34\67\359\36;\37= ?!A\"C#E$G%I&K\'M(O)Q*S+U,W-")
        buf.write("Y.[/]\60_\61a\62c\63e\64g\65i\66k\67m8o9q:s;u<w=y>{?}")
        buf.write("@\177A\u0081B\u0083C\u0085D\u0087E\u0089F\u008bG\u008d")
        buf.write("H\u008f\2\u0091\2\u0093\2\u0095\2\u0097\2\u0099\2\u009b")
        buf.write("\2\u009d\2\3\2\32\3\2\63;\4\2NNnn\4\2ZZzz\5\2\62;CHch")
        buf.write("\6\2\62;CHaach\3\2\629\4\2\629aa\4\2DDdd\3\2\62\63\4\2")
        buf.write("\62\63aa\6\2FFHHffhh\4\2RRrr\4\2--//\6\2\f\f\17\17))^")
        buf.write("^\6\2\f\f\17\17$$^^\5\2\13\f\16\17\"\"\4\2\f\f\17\17\4")
        buf.write("\2GGgg\n\2$$))^^ddhhppttvv\3\2\62\65\3\2\62;\4\2\62;a")
        buf.write("a\6\2&&C\\aac|\6\2FFJJOO[[\2\u0338\2\3\3\2\2\2\2\5\3\2")
        buf.write("\2\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3\2\2\2\2\r\3\2\2\2")
        buf.write("\2\17\3\2\2\2\2\21\3\2\2\2\2\23\3\2\2\2\2\25\3\2\2\2\2")
        buf.write("\27\3\2\2\2\2\31\3\2\2\2\2\33\3\2\2\2\2\35\3\2\2\2\2\37")
        buf.write("\3\2\2\2\2!\3\2\2\2\2#\3\2\2\2\2%\3\2\2\2\2\'\3\2\2\2")
        buf.write("\2)\3\2\2\2\2+\3\2\2\2\2-\3\2\2\2\2/\3\2\2\2\2\61\3\2")
        buf.write("\2\2\2\63\3\2\2\2\2\65\3\2\2\2\2\67\3\2\2\2\29\3\2\2\2")
        buf.write("\2;\3\2\2\2\2=\3\2\2\2\2?\3\2\2\2\2A\3\2\2\2\2C\3\2\2")
        buf.write("\2\2E\3\2\2\2\2G\3\2\2\2\2I\3\2\2\2\2K\3\2\2\2\2M\3\2")
        buf.write("\2\2\2O\3\2\2\2\2Q\3\2\2\2\2S\3\2\2\2\2U\3\2\2\2\2W\3")
        buf.write("\2\2\2\2Y\3\2\2\2\2[\3\2\2\2\2]\3\2\2\2\2_\3\2\2\2\2a")
        buf.write("\3\2\2\2\2c\3\2\2\2\2e\3\2\2\2\2g\3\2\2\2\2i\3\2\2\2\2")
        buf.write("k\3\2\2\2\2m\3\2\2\2\2o\3\2\2\2\2q\3\2\2\2\2s\3\2\2\2")
        buf.write("\2u\3\2\2\2\2w\3\2\2\2\2y\3\2\2\2\2{\3\2\2\2\2}\3\2\2")
        buf.write("\2\2\177\3\2\2\2\2\u0081\3\2\2\2\2\u0083\3\2\2\2\2\u0085")
        buf.write("\3\2\2\2\2\u0087\3\2\2\2\2\u0089\3\2\2\2\2\u008b\3\2\2")
        buf.write("\2\2\u008d\3\2\2\2\3\u009f\3\2\2\2\5\u00a7\3\2\2\2\7\u00ad")
        buf.write("\3\2\2\2\t\u00b7\3\2\2\2\13\u00bf\3\2\2\2\r\u00cb\3\2")
        buf.write("\2\2\17\u00d5\3\2\2\2\21\u00dd\3\2\2\2\23\u00e4\3\2\2")
        buf.write("\2\25\u00ef\3\2\2\2\27\u00f8\3\2\2\2\31\u0100\3\2\2\2")
        buf.write("\33\u010c\3\2\2\2\35\u0113\3\2\2\2\37\u011e\3\2\2\2!\u0125")
        buf.write("\3\2\2\2#\u012d\3\2\2\2%\u013b\3\2\2\2\'\u0149\3\2\2\2")
        buf.write(")\u014e\3\2\2\2+\u015a\3\2\2\2-\u0167\3\2\2\2/\u016b\3")
        buf.write("\2\2\2\61\u0173\3\2\2\2\63\u0186\3\2\2\2\65\u018e\3\2")
        buf.write("\2\2\67\u0194\3\2\2\29\u019c\3\2\2\2;\u019e\3\2\2\2=\u01a0")
        buf.write("\3\2\2\2?\u01a2\3\2\2\2A\u01a5\3\2\2\2C\u01a8\3\2\2\2")
        buf.write("E\u01af\3\2\2\2G\u01b9\3\2\2\2I\u01c9\3\2\2\2K\u01cb\3")
        buf.write("\2\2\2M\u01ce\3\2\2\2O\u01d0\3\2\2\2Q\u01d2\3\2\2\2S\u01d4")
        buf.write("\3\2\2\2U\u01d6\3\2\2\2W\u01d8\3\2\2\2Y\u01da\3\2\2\2")
        buf.write("[\u01dc\3\2\2\2]\u01de\3\2\2\2_\u01e0\3\2\2\2a\u01e2\3")
        buf.write("\2\2\2c\u01e4\3\2\2\2e\u01e6\3\2\2\2g\u01e8\3\2\2\2i\u01ea")
        buf.write("\3\2\2\2k\u01ec\3\2\2\2m\u01ee\3\2\2\2o\u01fd\3\2\2\2")
        buf.write("q\u0202\3\2\2\2s\u0211\3\2\2\2u\u0225\3\2\2\2w\u024b\3")
        buf.write("\2\2\2y\u024d\3\2\2\2{\u0274\3\2\2\2}\u0286\3\2\2\2\177")
        buf.write("\u028c\3\2\2\2\u0081\u028e\3\2\2\2\u0083\u0295\3\2\2\2")
        buf.write("\u0085\u02a0\3\2\2\2\u0087\u02a6\3\2\2\2\u0089\u02b4\3")
        buf.write("\2\2\2\u008b\u02bf\3\2\2\2\u008d\u02c6\3\2\2\2\u008f\u02c9")
        buf.write("\3\2\2\2\u0091\u02e4\3\2\2\2\u0093\u02e6\3\2\2\2\u0095")
        buf.write("\u02f1\3\2\2\2\u0097\u02f3\3\2\2\2\u0099\u02ff\3\2\2\2")
        buf.write("\u009b\u0301\3\2\2\2\u009d\u0303\3\2\2\2\u009f\u00a0\7")
        buf.write("f\2\2\u00a0\u00a1\7g\2\2\u00a1\u00a2\7h\2\2\u00a2\u00a3")
        buf.write("\7c\2\2\u00a3\u00a4\7w\2\2\u00a4\u00a5\7n\2\2\u00a5\u00a6")
        buf.write("\7v\2\2\u00a6\4\3\2\2\2\u00a7\u00a8\7h\2\2\u00a8\u00a9")
        buf.write("\7k\2\2\u00a9\u00aa\7p\2\2\u00aa\u00ab\7c\2\2\u00ab\u00ac")
        buf.write("\7n\2\2\u00ac\6\3\2\2\2\u00ad\u00ae\7r\2\2\u00ae\u00af")
        buf.write("\7j\2\2\u00af\u00b0\7g\2\2\u00b0\u00b1\7p\2\2\u00b1\u00b2")
        buf.write("\7q\2\2\u00b2\u00b3\7v\2\2\u00b3\u00b4\7{\2\2\u00b4\u00b5")
        buf.write("\7r\2\2\u00b5\u00b6\7g\2\2\u00b6\b\3\2\2\2\u00b7\u00b8")
        buf.write("\7x\2\2\u00b8\u00b9\7g\2\2\u00b9\u00ba\7t\2\2\u00ba\u00bb")
        buf.write("\7u\2\2\u00bb\u00bc\7k\2\2\u00bc\u00bd\7q\2\2\u00bd\u00be")
        buf.write("\7p\2\2\u00be\n\3\2\2\2\u00bf\u00c0\7f\2\2\u00c0\u00c1")
        buf.write("\7g\2\2\u00c1\u00c2\7u\2\2\u00c2\u00c3\7e\2\2\u00c3\u00c4")
        buf.write("\7t\2\2\u00c4\u00c5\7k\2\2\u00c5\u00c6\7r\2\2\u00c6\u00c7")
        buf.write("\7v\2\2\u00c7\u00c8\7k\2\2\u00c8\u00c9\7q\2\2\u00c9\u00ca")
        buf.write("\7p\2\2\u00ca\f\3\2\2\2\u00cb\u00cc\7f\2\2\u00cc\u00cd")
        buf.write("\7c\2\2\u00cd\u00ce\7v\2\2\u00ce\u00cf\7c\2\2\u00cf\u00d0")
        buf.write("\7o\2\2\u00d0\u00d1\7q\2\2\u00d1\u00d2\7f\2\2\u00d2\u00d3")
        buf.write("\7g\2\2\u00d3\u00d4\7n\2\2\u00d4\16\3\2\2\2\u00d5\u00d6")
        buf.write("\7k\2\2\u00d6\u00d7\7p\2\2\u00d7\u00d8\7e\2\2\u00d8\u00d9")
        buf.write("\7n\2\2\u00d9\u00da\7w\2\2\u00da\u00db\7f\2\2\u00db\u00dc")
        buf.write("\7g\2\2\u00dc\20\3\2\2\2\u00dd\u00de\7e\2\2\u00de\u00df")
        buf.write("\7c\2\2\u00df\u00e0\7n\2\2\u00e0\u00e1\7n\2\2\u00e1\u00e2")
        buf.write("\7g\2\2\u00e2\u00e3\7f\2\2\u00e3\22\3\2\2\2\u00e4\u00e5")
        buf.write("\7e\2\2\u00e5\u00e6\7q\2\2\u00e6\u00e7\7f\2\2\u00e7\u00e8")
        buf.write("\7g\2\2\u00e8\u00e9\7u\2\2\u00e9\u00ea\7{\2\2\u00ea\u00eb")
        buf.write("\7u\2\2\u00eb\u00ec\7v\2\2\u00ec\u00ed\7g\2\2\u00ed\u00ee")
        buf.write("\7o\2\2\u00ee\24\3\2\2\2\u00ef\u00f0\7x\2\2\u00f0\u00f1")
        buf.write("\7c\2\2\u00f1\u00f2\7n\2\2\u00f2\u00f3\7w\2\2\u00f3\u00f4")
        buf.write("\7g\2\2\u00f4\u00f5\7u\2\2\u00f5\u00f6\7g\2\2\u00f6\u00f7")
        buf.write("\7v\2\2\u00f7\26\3\2\2\2\u00f8\u00f9\7v\2\2\u00f9\u00fa")
        buf.write("\7g\2\2\u00fa\u00fb\7t\2\2\u00fb\u00fc\7o\2\2\u00fc\u00fd")
        buf.write("\7u\2\2\u00fd\u00fe\7g\2\2\u00fe\u00ff\7v\2\2\u00ff\30")
        buf.write("\3\2\2\2\u0100\u0101\7f\2\2\u0101\u0102\7q\2\2\u0102\u0103")
        buf.write("\7e\2\2\u0103\u0104\7w\2\2\u0104\u0105\7o\2\2\u0105\u0106")
        buf.write("\7g\2\2\u0106\u0107\7p\2\2\u0107\u0108\7v\2\2\u0108\u0109")
        buf.write("\7u\2\2\u0109\u010a\7g\2\2\u010a\u010b\7v\2\2\u010b\32")
        buf.write("\3\2\2\2\u010c\u010d\7e\2\2\u010d\u010e\7q\2\2\u010e\u010f")
        buf.write("\7j\2\2\u010f\u0110\7q\2\2\u0110\u0111\7t\2\2\u0111\u0112")
        buf.write("\7v\2\2\u0112\34\3\2\2\2\u0113\u0114\7r\2\2\u0114\u0115")
        buf.write("\7q\2\2\u0115\u0116\7r\2\2\u0116\u0117\7w\2\2\u0117\u0118")
        buf.write("\7n\2\2\u0118\u0119\7c\2\2\u0119\u011a\7v\2\2\u011a\u011b")
        buf.write("\7k\2\2\u011b\u011c\7q\2\2\u011c\u011d\7p\2\2\u011d\36")
        buf.write("\3\2\2\2\u011e\u011f\7f\2\2\u011f\u0120\7g\2\2\u0120\u0121")
        buf.write("\7h\2\2\u0121\u0122\7k\2\2\u0122\u0123\7p\2\2\u0123\u0124")
        buf.write("\7g\2\2\u0124 \3\2\2\2\u0125\u0126\7e\2\2\u0126\u0127")
        buf.write("\7q\2\2\u0127\u0128\7p\2\2\u0128\u0129\7v\2\2\u0129\u012a")
        buf.write("\7g\2\2\u012a\u012b\7z\2\2\u012b\u012c\7v\2\2\u012c\"")
        buf.write("\3\2\2\2\u012d\u012e\7o\2\2\u012e\u012f\7k\2\2\u012f\u0130")
        buf.write("\7p\2\2\u0130\u0131\7k\2\2\u0131\u0132\7o\2\2\u0132\u0133")
        buf.write("\7w\2\2\u0133\u0134\7o\2\2\u0134\u0135\7a\2\2\u0135\u0136")
        buf.write("\7x\2\2\u0136\u0137\7c\2\2\u0137\u0138\7n\2\2\u0138\u0139")
        buf.write("\7w\2\2\u0139\u013a\7g\2\2\u013a$\3\2\2\2\u013b\u013c")
        buf.write("\7o\2\2\u013c\u013d\7c\2\2\u013d\u013e\7z\2\2\u013e\u013f")
        buf.write("\7k\2\2\u013f\u0140\7o\2\2\u0140\u0141\7w\2\2\u0141\u0142")
        buf.write("\7o\2\2\u0142\u0143\7a\2\2\u0143\u0144\7x\2\2\u0144\u0145")
        buf.write("\7c\2\2\u0145\u0146\7n\2\2\u0146\u0147\7w\2\2\u0147\u0148")
        buf.write("\7g\2\2\u0148&\3\2\2\2\u0149\u014a\7Q\2\2\u014a\u014b")
        buf.write("\7O\2\2\u014b\u014c\7Q\2\2\u014c\u014d\7R\2\2\u014d(\3")
        buf.write("\2\2\2\u014e\u014f\7E\2\2\u014f\u0150\7n\2\2\u0150\u0151")
        buf.write("\7c\2\2\u0151\u0152\7t\2\2\u0152\u0153\7k\2\2\u0153\u0154")
        buf.write("\7v\2\2\u0154\u0155\7{\2\2\u0155\u0156\7E\2\2\u0156\u0157")
        buf.write("\7q\2\2\u0157\u0158\7t\2\2\u0158\u0159\7g\2\2\u0159*\3")
        buf.write("\2\2\2\u015a\u015b\7Q\2\2\u015b\u015c\7J\2\2\u015c\u015d")
        buf.write("\7F\2\2\u015d\u015e\7U\2\2\u015e\u015f\7K\2\2\u015f\u0160")
        buf.write("\7J\2\2\u0160\u0161\7g\2\2\u0161\u0162\7n\2\2\u0162\u0163")
        buf.write("\7r\2\2\u0163\u0164\7g\2\2\u0164\u0165\7t\2\2\u0165\u0166")
        buf.write("\7u\2\2\u0166,\3\2\2\2\u0167\u0168\7C\2\2\u0168\u0169")
        buf.write("\7n\2\2\u0169\u016a\7n\2\2\u016a.\3\2\2\2\u016b\u016c")
        buf.write("\7R\2\2\u016c\u016d\7c\2\2\u016d\u016e\7v\2\2\u016e\u016f")
        buf.write("\7k\2\2\u016f\u0170\7g\2\2\u0170\u0171\7p\2\2\u0171\u0172")
        buf.write("\7v\2\2\u0172\60\3\2\2\2\u0173\u0174\7F\2\2\u0174\u0175")
        buf.write("\7q\2\2\u0175\u0176\7e\2\2\u0176\u0177\7w\2\2\u0177\u0178")
        buf.write("\7o\2\2\u0178\u0179\7g\2\2\u0179\u017a\7p\2\2\u017a\u017b")
        buf.write("\7v\2\2\u017b\62\3\2\2\2\u017c\u017d\7Y\2\2\u017d\u017e")
        buf.write("\7J\2\2\u017e\u017f\7G\2\2\u017f\u0180\7T\2\2\u0180\u0187")
        buf.write("\7G\2\2\u0181\u0182\7y\2\2\u0182\u0183\7j\2\2\u0183\u0184")
        buf.write("\7g\2\2\u0184\u0185\7t\2\2\u0185\u0187\7g\2\2\u0186\u017c")
        buf.write("\3\2\2\2\u0186\u0181\3\2\2\2\u0187\64\3\2\2\2\u0188\u0189")
        buf.write("\7C\2\2\u0189\u018a\7P\2\2\u018a\u018f\7F\2\2\u018b\u018c")
        buf.write("\7c\2\2\u018c\u018d\7p\2\2\u018d\u018f\7f\2\2\u018e\u0188")
        buf.write("\3\2\2\2\u018e\u018b\3\2\2\2\u018f\66\3\2\2\2\u0190\u0191")
        buf.write("\7Q\2\2\u0191\u0195\7T\2\2\u0192\u0193\7q\2\2\u0193\u0195")
        buf.write("\7t\2\2\u0194\u0190\3\2\2\2\u0194\u0192\3\2\2\2\u0195")
        buf.write("8\3\2\2\2\u0196\u0197\7P\2\2\u0197\u0198\7Q\2\2\u0198")
        buf.write("\u019d\7V\2\2\u0199\u019a\7p\2\2\u019a\u019b\7q\2\2\u019b")
        buf.write("\u019d\7v\2\2\u019c\u0196\3\2\2\2\u019c\u0199\3\2\2\2")
        buf.write("\u019d:\3\2\2\2\u019e\u019f\7@\2\2\u019f<\3\2\2\2\u01a0")
        buf.write("\u01a1\7>\2\2\u01a1>\3\2\2\2\u01a2\u01a3\7>\2\2\u01a3")
        buf.write("\u01a4\7?\2\2\u01a4@\3\2\2\2\u01a5\u01a6\7@\2\2\u01a6")
        buf.write("\u01a7\7?\2\2\u01a7B\3\2\2\2\u01a8\u01a9\7?\2\2\u01a9")
        buf.write("\u01aa\7?\2\2\u01aaD\3\2\2\2\u01ab\u01ac\7k\2\2\u01ac")
        buf.write("\u01b0\7u\2\2\u01ad\u01ae\7K\2\2\u01ae\u01b0\7U\2\2\u01af")
        buf.write("\u01ab\3\2\2\2\u01af\u01ad\3\2\2\2\u01b0F\3\2\2\2\u01b1")
        buf.write("\u01b2\7n\2\2\u01b2\u01b3\7k\2\2\u01b3\u01b4\7m\2\2\u01b4")
        buf.write("\u01ba\7g\2\2\u01b5\u01b6\7N\2\2\u01b6\u01b7\7K\2\2\u01b7")
        buf.write("\u01b8\7M\2\2\u01b8\u01ba\7G\2\2\u01b9\u01b1\3\2\2\2\u01b9")
        buf.write("\u01b5\3\2\2\2\u01baH\3\2\2\2\u01bb\u01bc\7d\2\2\u01bc")
        buf.write("\u01bd\7g\2\2\u01bd\u01be\7v\2\2\u01be\u01bf\7y\2\2\u01bf")
        buf.write("\u01c0\7g\2\2\u01c0\u01c1\7g\2\2\u01c1\u01ca\7p\2\2\u01c2")
        buf.write("\u01c3\7D\2\2\u01c3\u01c4\7G\2\2\u01c4\u01c5\7V\2\2\u01c5")
        buf.write("\u01c6\7Y\2\2\u01c6\u01c7\7G\2\2\u01c7\u01c8\7G\2\2\u01c8")
        buf.write("\u01ca\7P\2\2\u01c9\u01bb\3\2\2\2\u01c9\u01c2\3\2\2\2")
        buf.write("\u01caJ\3\2\2\2\u01cb\u01cc\7#\2\2\u01cc\u01cd\7?\2\2")
        buf.write("\u01cdL\3\2\2\2\u01ce\u01cf\7#\2\2\u01cfN\3\2\2\2\u01d0")
        buf.write("\u01d1\7-\2\2\u01d1P\3\2\2\2\u01d2\u01d3\7/\2\2\u01d3")
        buf.write("R\3\2\2\2\u01d4\u01d5\7,\2\2\u01d5T\3\2\2\2\u01d6\u01d7")
        buf.write("\7\61\2\2\u01d7V\3\2\2\2\u01d8\u01d9\7`\2\2\u01d9X\3\2")
        buf.write("\2\2\u01da\u01db\7\'\2\2\u01dbZ\3\2\2\2\u01dc\u01dd\7")
        buf.write("=\2\2\u01dd\\\3\2\2\2\u01de\u01df\7<\2\2\u01df^\3\2\2")
        buf.write("\2\u01e0\u01e1\7\60\2\2\u01e1`\3\2\2\2\u01e2\u01e3\7.")
        buf.write("\2\2\u01e3b\3\2\2\2\u01e4\u01e5\7*\2\2\u01e5d\3\2\2\2")
        buf.write("\u01e6\u01e7\7+\2\2\u01e7f\3\2\2\2\u01e8\u01e9\7]\2\2")
        buf.write("\u01e9h\3\2\2\2\u01ea\u01eb\7_\2\2\u01ebj\3\2\2\2\u01ec")
        buf.write("\u01ed\7}\2\2\u01edl\3\2\2\2\u01ee\u01ef\7\177\2\2\u01ef")
        buf.write("n\3\2\2\2\u01f0\u01fe\7\62\2\2\u01f1\u01fb\t\2\2\2\u01f2")
        buf.write("\u01f4\5\u0097L\2\u01f3\u01f2\3\2\2\2\u01f3\u01f4\3\2")
        buf.write("\2\2\u01f4\u01fc\3\2\2\2\u01f5\u01f7\7a\2\2\u01f6\u01f5")
        buf.write("\3\2\2\2\u01f7\u01f8\3\2\2\2\u01f8\u01f6\3\2\2\2\u01f8")
        buf.write("\u01f9\3\2\2\2\u01f9\u01fa\3\2\2\2\u01fa\u01fc\5\u0097")
        buf.write("L\2\u01fb\u01f3\3\2\2\2\u01fb\u01f6\3\2\2\2\u01fc\u01fe")
        buf.write("\3\2\2\2\u01fd\u01f0\3\2\2\2\u01fd\u01f1\3\2\2\2\u01fe")
        buf.write("\u0200\3\2\2\2\u01ff\u0201\t\3\2\2\u0200\u01ff\3\2\2\2")
        buf.write("\u0200\u0201\3\2\2\2\u0201p\3\2\2\2\u0202\u0203\7\62\2")
        buf.write("\2\u0203\u0204\t\4\2\2\u0204\u020c\t\5\2\2\u0205\u0207")
        buf.write("\t\6\2\2\u0206\u0205\3\2\2\2\u0207\u020a\3\2\2\2\u0208")
        buf.write("\u0206\3\2\2\2\u0208\u0209\3\2\2\2\u0209\u020b\3\2\2\2")
        buf.write("\u020a\u0208\3\2\2\2\u020b\u020d\t\5\2\2\u020c\u0208\3")
        buf.write("\2\2\2\u020c\u020d\3\2\2\2\u020d\u020f\3\2\2\2\u020e\u0210")
        buf.write("\t\3\2\2\u020f\u020e\3\2\2\2\u020f\u0210\3\2\2\2\u0210")
        buf.write("r\3\2\2\2\u0211\u0215\7\62\2\2\u0212\u0214\7a\2\2\u0213")
        buf.write("\u0212\3\2\2\2\u0214\u0217\3\2\2\2\u0215\u0213\3\2\2\2")
        buf.write("\u0215\u0216\3\2\2\2\u0216\u0218\3\2\2\2\u0217\u0215\3")
        buf.write("\2\2\2\u0218\u0220\t\7\2\2\u0219\u021b\t\b\2\2\u021a\u0219")
        buf.write("\3\2\2\2\u021b\u021e\3\2\2\2\u021c\u021a\3\2\2\2\u021c")
        buf.write("\u021d\3\2\2\2\u021d\u021f\3\2\2\2\u021e\u021c\3\2\2\2")
        buf.write("\u021f\u0221\t\7\2\2\u0220\u021c\3\2\2\2\u0220\u0221\3")
        buf.write("\2\2\2\u0221\u0223\3\2\2\2\u0222\u0224\t\3\2\2\u0223\u0222")
        buf.write("\3\2\2\2\u0223\u0224\3\2\2\2\u0224t\3\2\2\2\u0225\u0226")
        buf.write("\7\62\2\2\u0226\u0227\t\t\2\2\u0227\u022f\t\n\2\2\u0228")
        buf.write("\u022a\t\13\2\2\u0229\u0228\3\2\2\2\u022a\u022d\3\2\2")
        buf.write("\2\u022b\u0229\3\2\2\2\u022b\u022c\3\2\2\2\u022c\u022e")
        buf.write("\3\2\2\2\u022d\u022b\3\2\2\2\u022e\u0230\t\n\2\2\u022f")
        buf.write("\u022b\3\2\2\2\u022f\u0230\3\2\2\2\u0230\u0232\3\2\2\2")
        buf.write("\u0231\u0233\t\3\2\2\u0232\u0231\3\2\2\2\u0232\u0233\3")
        buf.write("\2\2\2\u0233v\3\2\2\2\u0234\u0235\5\u0097L\2\u0235\u0237")
        buf.write("\7\60\2\2\u0236\u0238\5\u0097L\2\u0237\u0236\3\2\2\2\u0237")
        buf.write("\u0238\3\2\2\2\u0238\u023c\3\2\2\2\u0239\u023a\7\60\2")
        buf.write("\2\u023a\u023c\5\u0097L\2\u023b\u0234\3\2\2\2\u023b\u0239")
        buf.write("\3\2\2\2\u023c\u023e\3\2\2\2\u023d\u023f\5\u008fH\2\u023e")
        buf.write("\u023d\3\2\2\2\u023e\u023f\3\2\2\2\u023f\u0241\3\2\2\2")
        buf.write("\u0240\u0242\t\f\2\2\u0241\u0240\3\2\2\2\u0241\u0242\3")
        buf.write("\2\2\2\u0242\u024c\3\2\2\2\u0243\u0249\5\u0097L\2\u0244")
        buf.write("\u0246\5\u008fH\2\u0245\u0247\t\f\2\2\u0246\u0245\3\2")
        buf.write("\2\2\u0246\u0247\3\2\2\2\u0247\u024a\3\2\2\2\u0248\u024a")
        buf.write("\t\f\2\2\u0249\u0244\3\2\2\2\u0249\u0248\3\2\2\2\u024a")
        buf.write("\u024c\3\2\2\2\u024b\u023b\3\2\2\2\u024b\u0243\3\2\2\2")
        buf.write("\u024cx\3\2\2\2\u024d\u024e\7\62\2\2\u024e\u0258\t\4\2")
        buf.write("\2\u024f\u0251\5\u0093J\2\u0250\u0252\7\60\2\2\u0251\u0250")
        buf.write("\3\2\2\2\u0251\u0252\3\2\2\2\u0252\u0259\3\2\2\2\u0253")
        buf.write("\u0255\5\u0093J\2\u0254\u0253\3\2\2\2\u0254\u0255\3\2")
        buf.write("\2\2\u0255\u0256\3\2\2\2\u0256\u0257\7\60\2\2\u0257\u0259")
        buf.write("\5\u0093J\2\u0258\u024f\3\2\2\2\u0258\u0254\3\2\2\2\u0259")
        buf.write("\u025a\3\2\2\2\u025a\u025c\t\r\2\2\u025b\u025d\t\16\2")
        buf.write("\2\u025c\u025b\3\2\2\2\u025c\u025d\3\2\2\2\u025d\u025e")
        buf.write("\3\2\2\2\u025e\u0260\5\u0097L\2\u025f\u0261\t\f\2\2\u0260")
        buf.write("\u025f\3\2\2\2\u0260\u0261\3\2\2\2\u0261z\3\2\2\2\u0262")
        buf.write("\u0263\7v\2\2\u0263\u0264\7t\2\2\u0264\u0265\7w\2\2\u0265")
        buf.write("\u0275\7g\2\2\u0266\u0267\7V\2\2\u0267\u0268\7T\2\2\u0268")
        buf.write("\u0269\7W\2\2\u0269\u0275\7G\2\2\u026a\u026b\7h\2\2\u026b")
        buf.write("\u026c\7c\2\2\u026c\u026d\7n\2\2\u026d\u026e\7u\2\2\u026e")
        buf.write("\u0275\7g\2\2\u026f\u0270\7H\2\2\u0270\u0271\7C\2\2\u0271")
        buf.write("\u0272\7N\2\2\u0272\u0273\7U\2\2\u0273\u0275\7G\2\2\u0274")
        buf.write("\u0262\3\2\2\2\u0274\u0266\3\2\2\2\u0274\u026a\3\2\2\2")
        buf.write("\u0274\u026f\3\2\2\2\u0275|\3\2\2\2\u0276\u0277\7p\2\2")
        buf.write("\u0277\u0278\7w\2\2\u0278\u0279\7n\2\2\u0279\u0287\7n")
        buf.write("\2\2\u027a\u027b\7P\2\2\u027b\u027c\7W\2\2\u027c\u027d")
        buf.write("\7N\2\2\u027d\u0287\7N\2\2\u027e\u027f\7P\2\2\u027f\u0280")
        buf.write("\7q\2\2\u0280\u0281\7p\2\2\u0281\u0287\7g\2\2\u0282\u0283")
        buf.write("\7p\2\2\u0283\u0284\7q\2\2\u0284\u0285\7p\2\2\u0285\u0287")
        buf.write("\7g\2\2\u0286\u0276\3\2\2\2\u0286\u027a\3\2\2\2\u0286")
        buf.write("\u027e\3\2\2\2\u0286\u0282\3\2\2\2\u0287~\3\2\2\2\u0288")
        buf.write("\u0289\7K\2\2\u0289\u028d\7P\2\2\u028a\u028b\7k\2\2\u028b")
        buf.write("\u028d\7p\2\2\u028c\u0288\3\2\2\2\u028c\u028a\3\2\2\2")
        buf.write("\u028d\u0080\3\2\2\2\u028e\u0291\7)\2\2\u028f\u0292\n")
        buf.write("\17\2\2\u0290\u0292\5\u0091I\2\u0291\u028f\3\2\2\2\u0291")
        buf.write("\u0290\3\2\2\2\u0292\u0293\3\2\2\2\u0293\u0294\7)\2\2")
        buf.write("\u0294\u0082\3\2\2\2\u0295\u029a\7$\2\2\u0296\u0299\n")
        buf.write("\20\2\2\u0297\u0299\5\u0091I\2\u0298\u0296\3\2\2\2\u0298")
        buf.write("\u0297\3\2\2\2\u0299\u029c\3\2\2\2\u029a\u0298\3\2\2\2")
        buf.write("\u029a\u029b\3\2\2\2\u029b\u029d\3\2\2\2\u029c\u029a\3")
        buf.write("\2\2\2\u029d\u029e\7$\2\2\u029e\u0084\3\2\2\2\u029f\u02a1")
        buf.write("\t\21\2\2\u02a0\u029f\3\2\2\2\u02a1\u02a2\3\2\2\2\u02a2")
        buf.write("\u02a0\3\2\2\2\u02a2\u02a3\3\2\2\2\u02a3\u02a4\3\2\2\2")
        buf.write("\u02a4\u02a5\bC\2\2\u02a5\u0086\3\2\2\2\u02a6\u02a7\7")
        buf.write("\61\2\2\u02a7\u02a8\7,\2\2\u02a8\u02ac\3\2\2\2\u02a9\u02ab")
        buf.write("\13\2\2\2\u02aa\u02a9\3\2\2\2\u02ab\u02ae\3\2\2\2\u02ac")
        buf.write("\u02ad\3\2\2\2\u02ac\u02aa\3\2\2\2\u02ad\u02af\3\2\2\2")
        buf.write("\u02ae\u02ac\3\2\2\2\u02af\u02b0\7,\2\2\u02b0\u02b1\7")
        buf.write("\61\2\2\u02b1\u02b2\3\2\2\2\u02b2\u02b3\bD\2\2\u02b3\u0088")
        buf.write("\3\2\2\2\u02b4\u02b5\7\61\2\2\u02b5\u02b6\7\61\2\2\u02b6")
        buf.write("\u02ba\3\2\2\2\u02b7\u02b9\n\22\2\2\u02b8\u02b7\3\2\2")
        buf.write("\2\u02b9\u02bc\3\2\2\2\u02ba\u02b8\3\2\2\2\u02ba\u02bb")
        buf.write("\3\2\2\2\u02bb\u02bd\3\2\2\2\u02bc\u02ba\3\2\2\2\u02bd")
        buf.write("\u02be\bE\2\2\u02be\u008a\3\2\2\2\u02bf\u02c3\5\u0099")
        buf.write("M\2\u02c0\u02c2\5\u0099M\2\u02c1\u02c0\3\2\2\2\u02c2\u02c5")
        buf.write("\3\2\2\2\u02c3\u02c1\3\2\2\2\u02c3\u02c4\3\2\2\2\u02c4")
        buf.write("\u008c\3\2\2\2\u02c5\u02c3\3\2\2\2\u02c6\u02c7\5o8\2\u02c7")
        buf.write("\u02c8\5\u009dO\2\u02c8\u008e\3\2\2\2\u02c9\u02cb\t\23")
        buf.write("\2\2\u02ca\u02cc\t\16\2\2\u02cb\u02ca\3\2\2\2\u02cb\u02cc")
        buf.write("\3\2\2\2\u02cc\u02cd\3\2\2\2\u02cd\u02ce\5\u0097L\2\u02ce")
        buf.write("\u0090\3\2\2\2\u02cf\u02d0\7^\2\2\u02d0\u02e5\t\24\2\2")
        buf.write("\u02d1\u02d6\7^\2\2\u02d2\u02d4\t\25\2\2\u02d3\u02d2\3")
        buf.write("\2\2\2\u02d3\u02d4\3\2\2\2\u02d4\u02d5\3\2\2\2\u02d5\u02d7")
        buf.write("\t\7\2\2\u02d6\u02d3\3\2\2\2\u02d6\u02d7\3\2\2\2\u02d7")
        buf.write("\u02d8\3\2\2\2\u02d8\u02e5\t\7\2\2\u02d9\u02db\7^\2\2")
        buf.write("\u02da\u02dc\7w\2\2\u02db\u02da\3\2\2\2\u02dc\u02dd\3")
        buf.write("\2\2\2\u02dd\u02db\3\2\2\2\u02dd\u02de\3\2\2\2\u02de\u02df")
        buf.write("\3\2\2\2\u02df\u02e0\5\u0095K\2\u02e0\u02e1\5\u0095K\2")
        buf.write("\u02e1\u02e2\5\u0095K\2\u02e2\u02e3\5\u0095K\2\u02e3\u02e5")
        buf.write("\3\2\2\2\u02e4\u02cf\3\2\2\2\u02e4\u02d1\3\2\2\2\u02e4")
        buf.write("\u02d9\3\2\2\2\u02e5\u0092\3\2\2\2\u02e6\u02ef\5\u0095")
        buf.write("K\2\u02e7\u02ea\5\u0095K\2\u02e8\u02ea\7a\2\2\u02e9\u02e7")
        buf.write("\3\2\2\2\u02e9\u02e8\3\2\2\2\u02ea\u02ed\3\2\2\2\u02eb")
        buf.write("\u02e9\3\2\2\2\u02eb\u02ec\3\2\2\2\u02ec\u02ee\3\2\2\2")
        buf.write("\u02ed\u02eb\3\2\2\2\u02ee\u02f0\5\u0095K\2\u02ef\u02eb")
        buf.write("\3\2\2\2\u02ef\u02f0\3\2\2\2\u02f0\u0094\3\2\2\2\u02f1")
        buf.write("\u02f2\t\5\2\2\u02f2\u0096\3\2\2\2\u02f3\u02fb\t\26\2")
        buf.write("\2\u02f4\u02f6\t\27\2\2\u02f5\u02f4\3\2\2\2\u02f6\u02f9")
        buf.write("\3\2\2\2\u02f7\u02f5\3\2\2\2\u02f7\u02f8\3\2\2\2\u02f8")
        buf.write("\u02fa\3\2\2\2\u02f9\u02f7\3\2\2\2\u02fa\u02fc\t\26\2")
        buf.write("\2\u02fb\u02f7\3\2\2\2\u02fb\u02fc\3\2\2\2\u02fc\u0098")
        buf.write("\3\2\2\2\u02fd\u0300\5\u009bN\2\u02fe\u0300\t\26\2\2\u02ff")
        buf.write("\u02fd\3\2\2\2\u02ff\u02fe\3\2\2\2\u0300\u009a\3\2\2\2")
        buf.write("\u0301\u0302\t\30\2\2\u0302\u009c\3\2\2\2\u0303\u0304")
        buf.write("\t\31\2\2\u0304\u009e\3\2\2\2:\2\u0186\u018e\u0194\u019c")
        buf.write("\u01af\u01b9\u01c9\u01f3\u01f8\u01fb\u01fd\u0200\u0208")
        buf.write("\u020c\u020f\u0215\u021c\u0220\u0223\u022b\u022f\u0232")
        buf.write("\u0237\u023b\u023e\u0241\u0246\u0249\u024b\u0251\u0254")
        buf.write("\u0258\u025c\u0260\u0274\u0286\u028c\u0291\u0298\u029a")
        buf.write("\u02a2\u02ac\u02ba\u02c3\u02cb\u02d3\u02d6\u02dd\u02e4")
        buf.write("\u02e9\u02eb\u02ef\u02f7\u02fb\u02ff\3\2\3\2")
        return buf.getvalue()


class nlpql_lexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    DEFAULT = 1
    FINAL = 2
    PHENOTYPE_NAME = 3
    VERSION = 4
    DESCRIPTION = 5
    DATAMODEL = 6
    INCLUDE = 7
    CALLED = 8
    CODE_SYSTEM = 9
    VALUE_SET = 10
    TERM_SET = 11
    DOCUMENT_SET = 12
    COHORT = 13
    POPULATION = 14
    DEFINE = 15
    CONTEXT = 16
    MIN_VALUE = 17
    MAX_VALUE = 18
    OMOP = 19
    CLARITY_CORE = 20
    OHDSI_HELPERS = 21
    ALL = 22
    PATIENT = 23
    DOCUMENT = 24
    WHERE = 25
    AND = 26
    OR = 27
    NOT = 28
    GT = 29
    LT = 30
    LTE = 31
    GTE = 32
    EQUAL = 33
    IS = 34
    LIKE = 35
    BETWEEN = 36
    NOT_EQUAL = 37
    BANG = 38
    PLUS = 39
    MINUS = 40
    MULT = 41
    DIV = 42
    CARET = 43
    MOD = 44
    SEMI = 45
    COLON = 46
    DOT = 47
    COMMA = 48
    L_PAREN = 49
    R_PAREN = 50
    L_BRACKET = 51
    R_BRACKET = 52
    L_CURLY = 53
    R_CURLY = 54
    DECIMAL = 55
    HEX = 56
    OCT = 57
    BINARY = 58
    FLOAT = 59
    HEX_FLOAT = 60
    BOOL = 61
    NULL = 62
    IN = 63
    CHAR = 64
    STRING = 65
    WS = 66
    COMMENT = 67
    LINE_COMMENT = 68
    IDENTIFIER = 69
    TIME = 70

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'default'", "'final'", "'phenotype'", "'version'", "'description'", 
            "'datamodel'", "'include'", "'called'", "'codesystem'", "'valueset'", 
            "'termset'", "'documentset'", "'cohort'", "'population'", "'define'", 
            "'context'", "'minimum_value'", "'maximum_value'", "'OMOP'", 
            "'ClarityCore'", "'OHDSIHelpers'", "'All'", "'Patient'", "'Document'", 
            "'>'", "'<'", "'<='", "'>='", "'=='", "'!='", "'!'", "'+'", 
            "'-'", "'*'", "'/'", "'^'", "'%'", "';'", "':'", "'.'", "','", 
            "'('", "')'", "'['", "']'", "'{'", "'}'" ]

    symbolicNames = [ "<INVALID>",
            "DEFAULT", "FINAL", "PHENOTYPE_NAME", "VERSION", "DESCRIPTION", 
            "DATAMODEL", "INCLUDE", "CALLED", "CODE_SYSTEM", "VALUE_SET", 
            "TERM_SET", "DOCUMENT_SET", "COHORT", "POPULATION", "DEFINE", 
            "CONTEXT", "MIN_VALUE", "MAX_VALUE", "OMOP", "CLARITY_CORE", 
            "OHDSI_HELPERS", "ALL", "PATIENT", "DOCUMENT", "WHERE", "AND", 
            "OR", "NOT", "GT", "LT", "LTE", "GTE", "EQUAL", "IS", "LIKE", 
            "BETWEEN", "NOT_EQUAL", "BANG", "PLUS", "MINUS", "MULT", "DIV", 
            "CARET", "MOD", "SEMI", "COLON", "DOT", "COMMA", "L_PAREN", 
            "R_PAREN", "L_BRACKET", "R_BRACKET", "L_CURLY", "R_CURLY", "DECIMAL", 
            "HEX", "OCT", "BINARY", "FLOAT", "HEX_FLOAT", "BOOL", "NULL", 
            "IN", "CHAR", "STRING", "WS", "COMMENT", "LINE_COMMENT", "IDENTIFIER", 
            "TIME" ]

    ruleNames = [ "DEFAULT", "FINAL", "PHENOTYPE_NAME", "VERSION", "DESCRIPTION", 
                  "DATAMODEL", "INCLUDE", "CALLED", "CODE_SYSTEM", "VALUE_SET", 
                  "TERM_SET", "DOCUMENT_SET", "COHORT", "POPULATION", "DEFINE", 
                  "CONTEXT", "MIN_VALUE", "MAX_VALUE", "OMOP", "CLARITY_CORE", 
                  "OHDSI_HELPERS", "ALL", "PATIENT", "DOCUMENT", "WHERE", 
                  "AND", "OR", "NOT", "GT", "LT", "LTE", "GTE", "EQUAL", 
                  "IS", "LIKE", "BETWEEN", "NOT_EQUAL", "BANG", "PLUS", 
                  "MINUS", "MULT", "DIV", "CARET", "MOD", "SEMI", "COLON", 
                  "DOT", "COMMA", "L_PAREN", "R_PAREN", "L_BRACKET", "R_BRACKET", 
                  "L_CURLY", "R_CURLY", "DECIMAL", "HEX", "OCT", "BINARY", 
                  "FLOAT", "HEX_FLOAT", "BOOL", "NULL", "IN", "CHAR", "STRING", 
                  "WS", "COMMENT", "LINE_COMMENT", "IDENTIFIER", "TIME", 
                  "ExponentPart", "EscapeSequence", "HexDigits", "HexDigit", 
                  "Digits", "LetterOrDigit", "Letter", "TimeUnit" ]

    grammarFileName = "nlpql_lexer.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.7.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


