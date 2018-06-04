# Generated from nlpql_lexer.g4 by ANTLR 4.7.1
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2J")
        buf.write("\u0315\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
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
        buf.write("L\4M\tM\4N\tN\4O\tO\4P\tP\4Q\tQ\3\2\3\2\3\2\3\2\3\2\3")
        buf.write("\2\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\4\3\4\3\4\3\4\3\4")
        buf.write("\3\4\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\6\3\6\3")
        buf.write("\6\3\6\3\6\3\6\3\6\3\6\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7")
        buf.write("\3\7\3\7\3\7\3\7\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3")
        buf.write("\b\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\n\3\n\3\n\3\n\3\n")
        buf.write("\3\n\3\n\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13")
        buf.write("\3\13\3\13\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3\r\3\r")
        buf.write("\3\r\3\r\3\r\3\r\3\r\3\r\3\16\3\16\3\16\3\16\3\16\3\16")
        buf.write("\3\16\3\16\3\16\3\16\3\16\3\16\3\17\3\17\3\17\3\17\3\17")
        buf.write("\3\17\3\17\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20")
        buf.write("\3\20\3\20\3\21\3\21\3\21\3\21\3\21\3\21\3\21\3\22\3\22")
        buf.write("\3\22\3\22\3\22\3\22\3\22\3\22\3\23\3\23\3\23\3\23\3\23")
        buf.write("\3\23\3\23\3\23\3\23\3\23\3\23\3\23\3\23\3\23\3\24\3\24")
        buf.write("\3\24\3\24\3\24\3\24\3\24\3\24\3\24\3\24\3\24\3\24\3\24")
        buf.write("\3\24\3\25\3\25\3\25\3\25\3\25\3\25\3\26\3\26\3\26\3\26")
        buf.write("\3\26\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27")
        buf.write("\3\27\3\27\3\30\3\30\3\30\3\30\3\30\3\30\3\30\3\30\3\30")
        buf.write("\3\30\3\30\3\30\3\30\3\31\3\31\3\31\3\31\3\32\3\32\3\32")
        buf.write("\3\32\3\32\3\32\3\32\3\32\3\33\3\33\3\33\3\33\3\33\3\33")
        buf.write("\3\33\3\33\3\33\3\34\3\34\3\34\3\34\3\34\3\34\3\34\3\34")
        buf.write("\3\34\3\34\5\34\u0197\n\34\3\35\3\35\3\35\3\35\3\35\3")
        buf.write("\35\5\35\u019f\n\35\3\36\3\36\3\36\3\36\5\36\u01a5\n\36")
        buf.write("\3\37\3\37\3\37\3\37\3\37\3\37\5\37\u01ad\n\37\3 \3 \3")
        buf.write("!\3!\3\"\3\"\3\"\3#\3#\3#\3$\3$\3$\3%\3%\3%\3%\5%\u01c0")
        buf.write("\n%\3&\3&\3&\3&\3&\3&\3&\3&\5&\u01ca\n&\3\'\3\'\3\'\3")
        buf.write("\'\3\'\3\'\3\'\3\'\3\'\3\'\3\'\3\'\3\'\3\'\5\'\u01da\n")
        buf.write("\'\3(\3(\3(\3)\3)\3*\3*\3+\3+\3,\3,\3-\3-\3.\3.\3/\3/")
        buf.write("\3\60\3\60\3\61\3\61\3\62\3\62\3\63\3\63\3\64\3\64\3\65")
        buf.write("\3\65\3\66\3\66\3\67\3\67\38\38\39\39\3:\3:\3:\5:\u0204")
        buf.write("\n:\3:\6:\u0207\n:\r:\16:\u0208\3:\5:\u020c\n:\5:\u020e")
        buf.write("\n:\3:\5:\u0211\n:\3;\3;\3;\3;\7;\u0217\n;\f;\16;\u021a")
        buf.write("\13;\3;\5;\u021d\n;\3;\5;\u0220\n;\3<\3<\7<\u0224\n<\f")
        buf.write("<\16<\u0227\13<\3<\3<\7<\u022b\n<\f<\16<\u022e\13<\3<")
        buf.write("\5<\u0231\n<\3<\5<\u0234\n<\3=\3=\3=\3=\7=\u023a\n=\f")
        buf.write("=\16=\u023d\13=\3=\5=\u0240\n=\3=\5=\u0243\n=\3>\3>\3")
        buf.write(">\5>\u0248\n>\3>\3>\5>\u024c\n>\3>\5>\u024f\n>\3>\5>\u0252")
        buf.write("\n>\3>\3>\3>\5>\u0257\n>\3>\5>\u025a\n>\5>\u025c\n>\3")
        buf.write("?\3?\3?\3?\5?\u0262\n?\3?\5?\u0265\n?\3?\3?\5?\u0269\n")
        buf.write("?\3?\3?\5?\u026d\n?\3?\3?\5?\u0271\n?\3@\3@\3@\3@\3@\3")
        buf.write("@\3@\3@\3@\3@\3@\3@\3@\3@\3@\3@\3@\3@\5@\u0285\n@\3A\3")
        buf.write("A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\5A\u0297\n")
        buf.write("A\3B\3B\3B\3B\5B\u029d\nB\3C\3C\3C\5C\u02a2\nC\3C\3C\3")
        buf.write("D\3D\3D\7D\u02a9\nD\fD\16D\u02ac\13D\3D\3D\3E\6E\u02b1")
        buf.write("\nE\rE\16E\u02b2\3E\3E\3F\3F\3F\3F\7F\u02bb\nF\fF\16F")
        buf.write("\u02be\13F\3F\3F\3F\3F\3F\3G\3G\3G\3G\7G\u02c9\nG\fG\16")
        buf.write("G\u02cc\13G\3G\3G\3H\3H\7H\u02d2\nH\fH\16H\u02d5\13H\3")
        buf.write("I\3I\3I\3J\3J\5J\u02dc\nJ\3J\3J\3K\3K\3K\3K\5K\u02e4\n")
        buf.write("K\3K\5K\u02e7\nK\3K\3K\3K\6K\u02ec\nK\rK\16K\u02ed\3K")
        buf.write("\3K\3K\3K\3K\5K\u02f5\nK\3L\3L\3L\7L\u02fa\nL\fL\16L\u02fd")
        buf.write("\13L\3L\5L\u0300\nL\3M\3M\3N\3N\7N\u0306\nN\fN\16N\u0309")
        buf.write("\13N\3N\5N\u030c\nN\3O\3O\5O\u0310\nO\3P\3P\3Q\3Q\3\u02bc")
        buf.write("\2R\3\3\5\4\7\5\t\6\13\7\r\b\17\t\21\n\23\13\25\f\27\r")
        buf.write("\31\16\33\17\35\20\37\21!\22#\23%\24\'\25)\26+\27-\30")
        buf.write("/\31\61\32\63\33\65\34\67\359\36;\37= ?!A\"C#E$G%I&K\'")
        buf.write("M(O)Q*S+U,W-Y.[/]\60_\61a\62c\63e\64g\65i\66k\67m8o9q")
        buf.write(":s;u<w=y>{?}@\177A\u0081B\u0083C\u0085D\u0087E\u0089F")
        buf.write("\u008bG\u008dH\u008fI\u0091J\u0093\2\u0095\2\u0097\2\u0099")
        buf.write("\2\u009b\2\u009d\2\u009f\2\u00a1\2\3\2\32\3\2\63;\4\2")
        buf.write("NNnn\4\2ZZzz\5\2\62;CHch\6\2\62;CHaach\3\2\629\4\2\62")
        buf.write("9aa\4\2DDdd\3\2\62\63\4\2\62\63aa\6\2FFHHffhh\4\2RRrr")
        buf.write("\4\2--//\6\2\f\f\17\17))^^\6\2\f\f\17\17$$^^\5\2\13\f")
        buf.write("\16\17\"\"\4\2\f\f\17\17\4\2GGgg\n\2$$))^^ddhhppttvv\3")
        buf.write("\2\62\65\3\2\62;\4\2\62;aa\6\2&&C\\aac|\6\2FFJJOO[[\2")
        buf.write("\u0348\2\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2")
        buf.write("\2\13\3\2\2\2\2\r\3\2\2\2\2\17\3\2\2\2\2\21\3\2\2\2\2")
        buf.write("\23\3\2\2\2\2\25\3\2\2\2\2\27\3\2\2\2\2\31\3\2\2\2\2\33")
        buf.write("\3\2\2\2\2\35\3\2\2\2\2\37\3\2\2\2\2!\3\2\2\2\2#\3\2\2")
        buf.write("\2\2%\3\2\2\2\2\'\3\2\2\2\2)\3\2\2\2\2+\3\2\2\2\2-\3\2")
        buf.write("\2\2\2/\3\2\2\2\2\61\3\2\2\2\2\63\3\2\2\2\2\65\3\2\2\2")
        buf.write("\2\67\3\2\2\2\29\3\2\2\2\2;\3\2\2\2\2=\3\2\2\2\2?\3\2")
        buf.write("\2\2\2A\3\2\2\2\2C\3\2\2\2\2E\3\2\2\2\2G\3\2\2\2\2I\3")
        buf.write("\2\2\2\2K\3\2\2\2\2M\3\2\2\2\2O\3\2\2\2\2Q\3\2\2\2\2S")
        buf.write("\3\2\2\2\2U\3\2\2\2\2W\3\2\2\2\2Y\3\2\2\2\2[\3\2\2\2\2")
        buf.write("]\3\2\2\2\2_\3\2\2\2\2a\3\2\2\2\2c\3\2\2\2\2e\3\2\2\2")
        buf.write("\2g\3\2\2\2\2i\3\2\2\2\2k\3\2\2\2\2m\3\2\2\2\2o\3\2\2")
        buf.write("\2\2q\3\2\2\2\2s\3\2\2\2\2u\3\2\2\2\2w\3\2\2\2\2y\3\2")
        buf.write("\2\2\2{\3\2\2\2\2}\3\2\2\2\2\177\3\2\2\2\2\u0081\3\2\2")
        buf.write("\2\2\u0083\3\2\2\2\2\u0085\3\2\2\2\2\u0087\3\2\2\2\2\u0089")
        buf.write("\3\2\2\2\2\u008b\3\2\2\2\2\u008d\3\2\2\2\2\u008f\3\2\2")
        buf.write("\2\2\u0091\3\2\2\2\3\u00a3\3\2\2\2\5\u00a9\3\2\2\2\7\u00b1")
        buf.write("\3\2\2\2\t\u00b7\3\2\2\2\13\u00c1\3\2\2\2\r\u00c9\3\2")
        buf.write("\2\2\17\u00d5\3\2\2\2\21\u00df\3\2\2\2\23\u00e7\3\2\2")
        buf.write("\2\25\u00ee\3\2\2\2\27\u00f9\3\2\2\2\31\u0102\3\2\2\2")
        buf.write("\33\u010a\3\2\2\2\35\u0116\3\2\2\2\37\u011d\3\2\2\2!\u0128")
        buf.write("\3\2\2\2#\u012f\3\2\2\2%\u0137\3\2\2\2\'\u0145\3\2\2\2")
        buf.write(")\u0153\3\2\2\2+\u0159\3\2\2\2-\u015e\3\2\2\2/\u016a\3")
        buf.write("\2\2\2\61\u0177\3\2\2\2\63\u017b\3\2\2\2\65\u0183\3\2")
        buf.write("\2\2\67\u0196\3\2\2\29\u019e\3\2\2\2;\u01a4\3\2\2\2=\u01ac")
        buf.write("\3\2\2\2?\u01ae\3\2\2\2A\u01b0\3\2\2\2C\u01b2\3\2\2\2")
        buf.write("E\u01b5\3\2\2\2G\u01b8\3\2\2\2I\u01bf\3\2\2\2K\u01c9\3")
        buf.write("\2\2\2M\u01d9\3\2\2\2O\u01db\3\2\2\2Q\u01de\3\2\2\2S\u01e0")
        buf.write("\3\2\2\2U\u01e2\3\2\2\2W\u01e4\3\2\2\2Y\u01e6\3\2\2\2")
        buf.write("[\u01e8\3\2\2\2]\u01ea\3\2\2\2_\u01ec\3\2\2\2a\u01ee\3")
        buf.write("\2\2\2c\u01f0\3\2\2\2e\u01f2\3\2\2\2g\u01f4\3\2\2\2i\u01f6")
        buf.write("\3\2\2\2k\u01f8\3\2\2\2m\u01fa\3\2\2\2o\u01fc\3\2\2\2")
        buf.write("q\u01fe\3\2\2\2s\u020d\3\2\2\2u\u0212\3\2\2\2w\u0221\3")
        buf.write("\2\2\2y\u0235\3\2\2\2{\u025b\3\2\2\2}\u025d\3\2\2\2\177")
        buf.write("\u0284\3\2\2\2\u0081\u0296\3\2\2\2\u0083\u029c\3\2\2\2")
        buf.write("\u0085\u029e\3\2\2\2\u0087\u02a5\3\2\2\2\u0089\u02b0\3")
        buf.write("\2\2\2\u008b\u02b6\3\2\2\2\u008d\u02c4\3\2\2\2\u008f\u02cf")
        buf.write("\3\2\2\2\u0091\u02d6\3\2\2\2\u0093\u02d9\3\2\2\2\u0095")
        buf.write("\u02f4\3\2\2\2\u0097\u02f6\3\2\2\2\u0099\u0301\3\2\2\2")
        buf.write("\u009b\u0303\3\2\2\2\u009d\u030f\3\2\2\2\u009f\u0311\3")
        buf.write("\2\2\2\u00a1\u0313\3\2\2\2\u00a3\u00a4\7f\2\2\u00a4\u00a5")
        buf.write("\7g\2\2\u00a5\u00a6\7d\2\2\u00a6\u00a7\7w\2\2\u00a7\u00a8")
        buf.write("\7i\2\2\u00a8\4\3\2\2\2\u00a9\u00aa\7f\2\2\u00aa\u00ab")
        buf.write("\7g\2\2\u00ab\u00ac\7h\2\2\u00ac\u00ad\7c\2\2\u00ad\u00ae")
        buf.write("\7w\2\2\u00ae\u00af\7n\2\2\u00af\u00b0\7v\2\2\u00b0\6")
        buf.write("\3\2\2\2\u00b1\u00b2\7h\2\2\u00b2\u00b3\7k\2\2\u00b3\u00b4")
        buf.write("\7p\2\2\u00b4\u00b5\7c\2\2\u00b5\u00b6\7n\2\2\u00b6\b")
        buf.write("\3\2\2\2\u00b7\u00b8\7r\2\2\u00b8\u00b9\7j\2\2\u00b9\u00ba")
        buf.write("\7g\2\2\u00ba\u00bb\7p\2\2\u00bb\u00bc\7q\2\2\u00bc\u00bd")
        buf.write("\7v\2\2\u00bd\u00be\7{\2\2\u00be\u00bf\7r\2\2\u00bf\u00c0")
        buf.write("\7g\2\2\u00c0\n\3\2\2\2\u00c1\u00c2\7x\2\2\u00c2\u00c3")
        buf.write("\7g\2\2\u00c3\u00c4\7t\2\2\u00c4\u00c5\7u\2\2\u00c5\u00c6")
        buf.write("\7k\2\2\u00c6\u00c7\7q\2\2\u00c7\u00c8\7p\2\2\u00c8\f")
        buf.write("\3\2\2\2\u00c9\u00ca\7f\2\2\u00ca\u00cb\7g\2\2\u00cb\u00cc")
        buf.write("\7u\2\2\u00cc\u00cd\7e\2\2\u00cd\u00ce\7t\2\2\u00ce\u00cf")
        buf.write("\7k\2\2\u00cf\u00d0\7r\2\2\u00d0\u00d1\7v\2\2\u00d1\u00d2")
        buf.write("\7k\2\2\u00d2\u00d3\7q\2\2\u00d3\u00d4\7p\2\2\u00d4\16")
        buf.write("\3\2\2\2\u00d5\u00d6\7f\2\2\u00d6\u00d7\7c\2\2\u00d7\u00d8")
        buf.write("\7v\2\2\u00d8\u00d9\7c\2\2\u00d9\u00da\7o\2\2\u00da\u00db")
        buf.write("\7q\2\2\u00db\u00dc\7f\2\2\u00dc\u00dd\7g\2\2\u00dd\u00de")
        buf.write("\7n\2\2\u00de\20\3\2\2\2\u00df\u00e0\7k\2\2\u00e0\u00e1")
        buf.write("\7p\2\2\u00e1\u00e2\7e\2\2\u00e2\u00e3\7n\2\2\u00e3\u00e4")
        buf.write("\7w\2\2\u00e4\u00e5\7f\2\2\u00e5\u00e6\7g\2\2\u00e6\22")
        buf.write("\3\2\2\2\u00e7\u00e8\7e\2\2\u00e8\u00e9\7c\2\2\u00e9\u00ea")
        buf.write("\7n\2\2\u00ea\u00eb\7n\2\2\u00eb\u00ec\7g\2\2\u00ec\u00ed")
        buf.write("\7f\2\2\u00ed\24\3\2\2\2\u00ee\u00ef\7e\2\2\u00ef\u00f0")
        buf.write("\7q\2\2\u00f0\u00f1\7f\2\2\u00f1\u00f2\7g\2\2\u00f2\u00f3")
        buf.write("\7u\2\2\u00f3\u00f4\7{\2\2\u00f4\u00f5\7u\2\2\u00f5\u00f6")
        buf.write("\7v\2\2\u00f6\u00f7\7g\2\2\u00f7\u00f8\7o\2\2\u00f8\26")
        buf.write("\3\2\2\2\u00f9\u00fa\7x\2\2\u00fa\u00fb\7c\2\2\u00fb\u00fc")
        buf.write("\7n\2\2\u00fc\u00fd\7w\2\2\u00fd\u00fe\7g\2\2\u00fe\u00ff")
        buf.write("\7u\2\2\u00ff\u0100\7g\2\2\u0100\u0101\7v\2\2\u0101\30")
        buf.write("\3\2\2\2\u0102\u0103\7v\2\2\u0103\u0104\7g\2\2\u0104\u0105")
        buf.write("\7t\2\2\u0105\u0106\7o\2\2\u0106\u0107\7u\2\2\u0107\u0108")
        buf.write("\7g\2\2\u0108\u0109\7v\2\2\u0109\32\3\2\2\2\u010a\u010b")
        buf.write("\7f\2\2\u010b\u010c\7q\2\2\u010c\u010d\7e\2\2\u010d\u010e")
        buf.write("\7w\2\2\u010e\u010f\7o\2\2\u010f\u0110\7g\2\2\u0110\u0111")
        buf.write("\7p\2\2\u0111\u0112\7v\2\2\u0112\u0113\7u\2\2\u0113\u0114")
        buf.write("\7g\2\2\u0114\u0115\7v\2\2\u0115\34\3\2\2\2\u0116\u0117")
        buf.write("\7e\2\2\u0117\u0118\7q\2\2\u0118\u0119\7j\2\2\u0119\u011a")
        buf.write("\7q\2\2\u011a\u011b\7t\2\2\u011b\u011c\7v\2\2\u011c\36")
        buf.write("\3\2\2\2\u011d\u011e\7r\2\2\u011e\u011f\7q\2\2\u011f\u0120")
        buf.write("\7r\2\2\u0120\u0121\7w\2\2\u0121\u0122\7n\2\2\u0122\u0123")
        buf.write("\7c\2\2\u0123\u0124\7v\2\2\u0124\u0125\7k\2\2\u0125\u0126")
        buf.write("\7q\2\2\u0126\u0127\7p\2\2\u0127 \3\2\2\2\u0128\u0129")
        buf.write("\7f\2\2\u0129\u012a\7g\2\2\u012a\u012b\7h\2\2\u012b\u012c")
        buf.write("\7k\2\2\u012c\u012d\7p\2\2\u012d\u012e\7g\2\2\u012e\"")
        buf.write("\3\2\2\2\u012f\u0130\7e\2\2\u0130\u0131\7q\2\2\u0131\u0132")
        buf.write("\7p\2\2\u0132\u0133\7v\2\2\u0133\u0134\7g\2\2\u0134\u0135")
        buf.write("\7z\2\2\u0135\u0136\7v\2\2\u0136$\3\2\2\2\u0137\u0138")
        buf.write("\7o\2\2\u0138\u0139\7k\2\2\u0139\u013a\7p\2\2\u013a\u013b")
        buf.write("\7k\2\2\u013b\u013c\7o\2\2\u013c\u013d\7w\2\2\u013d\u013e")
        buf.write("\7o\2\2\u013e\u013f\7a\2\2\u013f\u0140\7x\2\2\u0140\u0141")
        buf.write("\7c\2\2\u0141\u0142\7n\2\2\u0142\u0143\7w\2\2\u0143\u0144")
        buf.write("\7g\2\2\u0144&\3\2\2\2\u0145\u0146\7o\2\2\u0146\u0147")
        buf.write("\7c\2\2\u0147\u0148\7z\2\2\u0148\u0149\7k\2\2\u0149\u014a")
        buf.write("\7o\2\2\u014a\u014b\7w\2\2\u014b\u014c\7o\2\2\u014c\u014d")
        buf.write("\7a\2\2\u014d\u014e\7x\2\2\u014e\u014f\7c\2\2\u014f\u0150")
        buf.write("\7n\2\2\u0150\u0151\7w\2\2\u0151\u0152\7g\2\2\u0152(\3")
        buf.write("\2\2\2\u0153\u0154\7n\2\2\u0154\u0155\7k\2\2\u0155\u0156")
        buf.write("\7o\2\2\u0156\u0157\7k\2\2\u0157\u0158\7v\2\2\u0158*\3")
        buf.write("\2\2\2\u0159\u015a\7Q\2\2\u015a\u015b\7O\2\2\u015b\u015c")
        buf.write("\7Q\2\2\u015c\u015d\7R\2\2\u015d,\3\2\2\2\u015e\u015f")
        buf.write("\7E\2\2\u015f\u0160\7n\2\2\u0160\u0161\7c\2\2\u0161\u0162")
        buf.write("\7t\2\2\u0162\u0163\7k\2\2\u0163\u0164\7v\2\2\u0164\u0165")
        buf.write("\7{\2\2\u0165\u0166\7E\2\2\u0166\u0167\7q\2\2\u0167\u0168")
        buf.write("\7t\2\2\u0168\u0169\7g\2\2\u0169.\3\2\2\2\u016a\u016b")
        buf.write("\7Q\2\2\u016b\u016c\7J\2\2\u016c\u016d\7F\2\2\u016d\u016e")
        buf.write("\7U\2\2\u016e\u016f\7K\2\2\u016f\u0170\7J\2\2\u0170\u0171")
        buf.write("\7g\2\2\u0171\u0172\7n\2\2\u0172\u0173\7r\2\2\u0173\u0174")
        buf.write("\7g\2\2\u0174\u0175\7t\2\2\u0175\u0176\7u\2\2\u0176\60")
        buf.write("\3\2\2\2\u0177\u0178\7C\2\2\u0178\u0179\7n\2\2\u0179\u017a")
        buf.write("\7n\2\2\u017a\62\3\2\2\2\u017b\u017c\7R\2\2\u017c\u017d")
        buf.write("\7c\2\2\u017d\u017e\7v\2\2\u017e\u017f\7k\2\2\u017f\u0180")
        buf.write("\7g\2\2\u0180\u0181\7p\2\2\u0181\u0182\7v\2\2\u0182\64")
        buf.write("\3\2\2\2\u0183\u0184\7F\2\2\u0184\u0185\7q\2\2\u0185\u0186")
        buf.write("\7e\2\2\u0186\u0187\7w\2\2\u0187\u0188\7o\2\2\u0188\u0189")
        buf.write("\7g\2\2\u0189\u018a\7p\2\2\u018a\u018b\7v\2\2\u018b\66")
        buf.write("\3\2\2\2\u018c\u018d\7Y\2\2\u018d\u018e\7J\2\2\u018e\u018f")
        buf.write("\7G\2\2\u018f\u0190\7T\2\2\u0190\u0197\7G\2\2\u0191\u0192")
        buf.write("\7y\2\2\u0192\u0193\7j\2\2\u0193\u0194\7g\2\2\u0194\u0195")
        buf.write("\7t\2\2\u0195\u0197\7g\2\2\u0196\u018c\3\2\2\2\u0196\u0191")
        buf.write("\3\2\2\2\u01978\3\2\2\2\u0198\u0199\7C\2\2\u0199\u019a")
        buf.write("\7P\2\2\u019a\u019f\7F\2\2\u019b\u019c\7c\2\2\u019c\u019d")
        buf.write("\7p\2\2\u019d\u019f\7f\2\2\u019e\u0198\3\2\2\2\u019e\u019b")
        buf.write("\3\2\2\2\u019f:\3\2\2\2\u01a0\u01a1\7Q\2\2\u01a1\u01a5")
        buf.write("\7T\2\2\u01a2\u01a3\7q\2\2\u01a3\u01a5\7t\2\2\u01a4\u01a0")
        buf.write("\3\2\2\2\u01a4\u01a2\3\2\2\2\u01a5<\3\2\2\2\u01a6\u01a7")
        buf.write("\7P\2\2\u01a7\u01a8\7Q\2\2\u01a8\u01ad\7V\2\2\u01a9\u01aa")
        buf.write("\7p\2\2\u01aa\u01ab\7q\2\2\u01ab\u01ad\7v\2\2\u01ac\u01a6")
        buf.write("\3\2\2\2\u01ac\u01a9\3\2\2\2\u01ad>\3\2\2\2\u01ae\u01af")
        buf.write("\7@\2\2\u01af@\3\2\2\2\u01b0\u01b1\7>\2\2\u01b1B\3\2\2")
        buf.write("\2\u01b2\u01b3\7>\2\2\u01b3\u01b4\7?\2\2\u01b4D\3\2\2")
        buf.write("\2\u01b5\u01b6\7@\2\2\u01b6\u01b7\7?\2\2\u01b7F\3\2\2")
        buf.write("\2\u01b8\u01b9\7?\2\2\u01b9\u01ba\7?\2\2\u01baH\3\2\2")
        buf.write("\2\u01bb\u01bc\7k\2\2\u01bc\u01c0\7u\2\2\u01bd\u01be\7")
        buf.write("K\2\2\u01be\u01c0\7U\2\2\u01bf\u01bb\3\2\2\2\u01bf\u01bd")
        buf.write("\3\2\2\2\u01c0J\3\2\2\2\u01c1\u01c2\7n\2\2\u01c2\u01c3")
        buf.write("\7k\2\2\u01c3\u01c4\7m\2\2\u01c4\u01ca\7g\2\2\u01c5\u01c6")
        buf.write("\7N\2\2\u01c6\u01c7\7K\2\2\u01c7\u01c8\7M\2\2\u01c8\u01ca")
        buf.write("\7G\2\2\u01c9\u01c1\3\2\2\2\u01c9\u01c5\3\2\2\2\u01ca")
        buf.write("L\3\2\2\2\u01cb\u01cc\7d\2\2\u01cc\u01cd\7g\2\2\u01cd")
        buf.write("\u01ce\7v\2\2\u01ce\u01cf\7y\2\2\u01cf\u01d0\7g\2\2\u01d0")
        buf.write("\u01d1\7g\2\2\u01d1\u01da\7p\2\2\u01d2\u01d3\7D\2\2\u01d3")
        buf.write("\u01d4\7G\2\2\u01d4\u01d5\7V\2\2\u01d5\u01d6\7Y\2\2\u01d6")
        buf.write("\u01d7\7G\2\2\u01d7\u01d8\7G\2\2\u01d8\u01da\7P\2\2\u01d9")
        buf.write("\u01cb\3\2\2\2\u01d9\u01d2\3\2\2\2\u01daN\3\2\2\2\u01db")
        buf.write("\u01dc\7#\2\2\u01dc\u01dd\7?\2\2\u01ddP\3\2\2\2\u01de")
        buf.write("\u01df\7#\2\2\u01dfR\3\2\2\2\u01e0\u01e1\7-\2\2\u01e1")
        buf.write("T\3\2\2\2\u01e2\u01e3\7/\2\2\u01e3V\3\2\2\2\u01e4\u01e5")
        buf.write("\7,\2\2\u01e5X\3\2\2\2\u01e6\u01e7\7\61\2\2\u01e7Z\3\2")
        buf.write("\2\2\u01e8\u01e9\7`\2\2\u01e9\\\3\2\2\2\u01ea\u01eb\7")
        buf.write("\'\2\2\u01eb^\3\2\2\2\u01ec\u01ed\7=\2\2\u01ed`\3\2\2")
        buf.write("\2\u01ee\u01ef\7<\2\2\u01efb\3\2\2\2\u01f0\u01f1\7\60")
        buf.write("\2\2\u01f1d\3\2\2\2\u01f2\u01f3\7.\2\2\u01f3f\3\2\2\2")
        buf.write("\u01f4\u01f5\7*\2\2\u01f5h\3\2\2\2\u01f6\u01f7\7+\2\2")
        buf.write("\u01f7j\3\2\2\2\u01f8\u01f9\7]\2\2\u01f9l\3\2\2\2\u01fa")
        buf.write("\u01fb\7_\2\2\u01fbn\3\2\2\2\u01fc\u01fd\7}\2\2\u01fd")
        buf.write("p\3\2\2\2\u01fe\u01ff\7\177\2\2\u01ffr\3\2\2\2\u0200\u020e")
        buf.write("\7\62\2\2\u0201\u020b\t\2\2\2\u0202\u0204\5\u009bN\2\u0203")
        buf.write("\u0202\3\2\2\2\u0203\u0204\3\2\2\2\u0204\u020c\3\2\2\2")
        buf.write("\u0205\u0207\7a\2\2\u0206\u0205\3\2\2\2\u0207\u0208\3")
        buf.write("\2\2\2\u0208\u0206\3\2\2\2\u0208\u0209\3\2\2\2\u0209\u020a")
        buf.write("\3\2\2\2\u020a\u020c\5\u009bN\2\u020b\u0203\3\2\2\2\u020b")
        buf.write("\u0206\3\2\2\2\u020c\u020e\3\2\2\2\u020d\u0200\3\2\2\2")
        buf.write("\u020d\u0201\3\2\2\2\u020e\u0210\3\2\2\2\u020f\u0211\t")
        buf.write("\3\2\2\u0210\u020f\3\2\2\2\u0210\u0211\3\2\2\2\u0211t")
        buf.write("\3\2\2\2\u0212\u0213\7\62\2\2\u0213\u0214\t\4\2\2\u0214")
        buf.write("\u021c\t\5\2\2\u0215\u0217\t\6\2\2\u0216\u0215\3\2\2\2")
        buf.write("\u0217\u021a\3\2\2\2\u0218\u0216\3\2\2\2\u0218\u0219\3")
        buf.write("\2\2\2\u0219\u021b\3\2\2\2\u021a\u0218\3\2\2\2\u021b\u021d")
        buf.write("\t\5\2\2\u021c\u0218\3\2\2\2\u021c\u021d\3\2\2\2\u021d")
        buf.write("\u021f\3\2\2\2\u021e\u0220\t\3\2\2\u021f\u021e\3\2\2\2")
        buf.write("\u021f\u0220\3\2\2\2\u0220v\3\2\2\2\u0221\u0225\7\62\2")
        buf.write("\2\u0222\u0224\7a\2\2\u0223\u0222\3\2\2\2\u0224\u0227")
        buf.write("\3\2\2\2\u0225\u0223\3\2\2\2\u0225\u0226\3\2\2\2\u0226")
        buf.write("\u0228\3\2\2\2\u0227\u0225\3\2\2\2\u0228\u0230\t\7\2\2")
        buf.write("\u0229\u022b\t\b\2\2\u022a\u0229\3\2\2\2\u022b\u022e\3")
        buf.write("\2\2\2\u022c\u022a\3\2\2\2\u022c\u022d\3\2\2\2\u022d\u022f")
        buf.write("\3\2\2\2\u022e\u022c\3\2\2\2\u022f\u0231\t\7\2\2\u0230")
        buf.write("\u022c\3\2\2\2\u0230\u0231\3\2\2\2\u0231\u0233\3\2\2\2")
        buf.write("\u0232\u0234\t\3\2\2\u0233\u0232\3\2\2\2\u0233\u0234\3")
        buf.write("\2\2\2\u0234x\3\2\2\2\u0235\u0236\7\62\2\2\u0236\u0237")
        buf.write("\t\t\2\2\u0237\u023f\t\n\2\2\u0238\u023a\t\13\2\2\u0239")
        buf.write("\u0238\3\2\2\2\u023a\u023d\3\2\2\2\u023b\u0239\3\2\2\2")
        buf.write("\u023b\u023c\3\2\2\2\u023c\u023e\3\2\2\2\u023d\u023b\3")
        buf.write("\2\2\2\u023e\u0240\t\n\2\2\u023f\u023b\3\2\2\2\u023f\u0240")
        buf.write("\3\2\2\2\u0240\u0242\3\2\2\2\u0241\u0243\t\3\2\2\u0242")
        buf.write("\u0241\3\2\2\2\u0242\u0243\3\2\2\2\u0243z\3\2\2\2\u0244")
        buf.write("\u0245\5\u009bN\2\u0245\u0247\7\60\2\2\u0246\u0248\5\u009b")
        buf.write("N\2\u0247\u0246\3\2\2\2\u0247\u0248\3\2\2\2\u0248\u024c")
        buf.write("\3\2\2\2\u0249\u024a\7\60\2\2\u024a\u024c\5\u009bN\2\u024b")
        buf.write("\u0244\3\2\2\2\u024b\u0249\3\2\2\2\u024c\u024e\3\2\2\2")
        buf.write("\u024d\u024f\5\u0093J\2\u024e\u024d\3\2\2\2\u024e\u024f")
        buf.write("\3\2\2\2\u024f\u0251\3\2\2\2\u0250\u0252\t\f\2\2\u0251")
        buf.write("\u0250\3\2\2\2\u0251\u0252\3\2\2\2\u0252\u025c\3\2\2\2")
        buf.write("\u0253\u0259\5\u009bN\2\u0254\u0256\5\u0093J\2\u0255\u0257")
        buf.write("\t\f\2\2\u0256\u0255\3\2\2\2\u0256\u0257\3\2\2\2\u0257")
        buf.write("\u025a\3\2\2\2\u0258\u025a\t\f\2\2\u0259\u0254\3\2\2\2")
        buf.write("\u0259\u0258\3\2\2\2\u025a\u025c\3\2\2\2\u025b\u024b\3")
        buf.write("\2\2\2\u025b\u0253\3\2\2\2\u025c|\3\2\2\2\u025d\u025e")
        buf.write("\7\62\2\2\u025e\u0268\t\4\2\2\u025f\u0261\5\u0097L\2\u0260")
        buf.write("\u0262\7\60\2\2\u0261\u0260\3\2\2\2\u0261\u0262\3\2\2")
        buf.write("\2\u0262\u0269\3\2\2\2\u0263\u0265\5\u0097L\2\u0264\u0263")
        buf.write("\3\2\2\2\u0264\u0265\3\2\2\2\u0265\u0266\3\2\2\2\u0266")
        buf.write("\u0267\7\60\2\2\u0267\u0269\5\u0097L\2\u0268\u025f\3\2")
        buf.write("\2\2\u0268\u0264\3\2\2\2\u0269\u026a\3\2\2\2\u026a\u026c")
        buf.write("\t\r\2\2\u026b\u026d\t\16\2\2\u026c\u026b\3\2\2\2\u026c")
        buf.write("\u026d\3\2\2\2\u026d\u026e\3\2\2\2\u026e\u0270\5\u009b")
        buf.write("N\2\u026f\u0271\t\f\2\2\u0270\u026f\3\2\2\2\u0270\u0271")
        buf.write("\3\2\2\2\u0271~\3\2\2\2\u0272\u0273\7v\2\2\u0273\u0274")
        buf.write("\7t\2\2\u0274\u0275\7w\2\2\u0275\u0285\7g\2\2\u0276\u0277")
        buf.write("\7V\2\2\u0277\u0278\7T\2\2\u0278\u0279\7W\2\2\u0279\u0285")
        buf.write("\7G\2\2\u027a\u027b\7h\2\2\u027b\u027c\7c\2\2\u027c\u027d")
        buf.write("\7n\2\2\u027d\u027e\7u\2\2\u027e\u0285\7g\2\2\u027f\u0280")
        buf.write("\7H\2\2\u0280\u0281\7C\2\2\u0281\u0282\7N\2\2\u0282\u0283")
        buf.write("\7U\2\2\u0283\u0285\7G\2\2\u0284\u0272\3\2\2\2\u0284\u0276")
        buf.write("\3\2\2\2\u0284\u027a\3\2\2\2\u0284\u027f\3\2\2\2\u0285")
        buf.write("\u0080\3\2\2\2\u0286\u0287\7p\2\2\u0287\u0288\7w\2\2\u0288")
        buf.write("\u0289\7n\2\2\u0289\u0297\7n\2\2\u028a\u028b\7P\2\2\u028b")
        buf.write("\u028c\7W\2\2\u028c\u028d\7N\2\2\u028d\u0297\7N\2\2\u028e")
        buf.write("\u028f\7P\2\2\u028f\u0290\7q\2\2\u0290\u0291\7p\2\2\u0291")
        buf.write("\u0297\7g\2\2\u0292\u0293\7p\2\2\u0293\u0294\7q\2\2\u0294")
        buf.write("\u0295\7p\2\2\u0295\u0297\7g\2\2\u0296\u0286\3\2\2\2\u0296")
        buf.write("\u028a\3\2\2\2\u0296\u028e\3\2\2\2\u0296\u0292\3\2\2\2")
        buf.write("\u0297\u0082\3\2\2\2\u0298\u0299\7K\2\2\u0299\u029d\7")
        buf.write("P\2\2\u029a\u029b\7k\2\2\u029b\u029d\7p\2\2\u029c\u0298")
        buf.write("\3\2\2\2\u029c\u029a\3\2\2\2\u029d\u0084\3\2\2\2\u029e")
        buf.write("\u02a1\7)\2\2\u029f\u02a2\n\17\2\2\u02a0\u02a2\5\u0095")
        buf.write("K\2\u02a1\u029f\3\2\2\2\u02a1\u02a0\3\2\2\2\u02a2\u02a3")
        buf.write("\3\2\2\2\u02a3\u02a4\7)\2\2\u02a4\u0086\3\2\2\2\u02a5")
        buf.write("\u02aa\7$\2\2\u02a6\u02a9\n\20\2\2\u02a7\u02a9\5\u0095")
        buf.write("K\2\u02a8\u02a6\3\2\2\2\u02a8\u02a7\3\2\2\2\u02a9\u02ac")
        buf.write("\3\2\2\2\u02aa\u02a8\3\2\2\2\u02aa\u02ab\3\2\2\2\u02ab")
        buf.write("\u02ad\3\2\2\2\u02ac\u02aa\3\2\2\2\u02ad\u02ae\7$\2\2")
        buf.write("\u02ae\u0088\3\2\2\2\u02af\u02b1\t\21\2\2\u02b0\u02af")
        buf.write("\3\2\2\2\u02b1\u02b2\3\2\2\2\u02b2\u02b0\3\2\2\2\u02b2")
        buf.write("\u02b3\3\2\2\2\u02b3\u02b4\3\2\2\2\u02b4\u02b5\bE\2\2")
        buf.write("\u02b5\u008a\3\2\2\2\u02b6\u02b7\7\61\2\2\u02b7\u02b8")
        buf.write("\7,\2\2\u02b8\u02bc\3\2\2\2\u02b9\u02bb\13\2\2\2\u02ba")
        buf.write("\u02b9\3\2\2\2\u02bb\u02be\3\2\2\2\u02bc\u02bd\3\2\2\2")
        buf.write("\u02bc\u02ba\3\2\2\2\u02bd\u02bf\3\2\2\2\u02be\u02bc\3")
        buf.write("\2\2\2\u02bf\u02c0\7,\2\2\u02c0\u02c1\7\61\2\2\u02c1\u02c2")
        buf.write("\3\2\2\2\u02c2\u02c3\bF\2\2\u02c3\u008c\3\2\2\2\u02c4")
        buf.write("\u02c5\7\61\2\2\u02c5\u02c6\7\61\2\2\u02c6\u02ca\3\2\2")
        buf.write("\2\u02c7\u02c9\n\22\2\2\u02c8\u02c7\3\2\2\2\u02c9\u02cc")
        buf.write("\3\2\2\2\u02ca\u02c8\3\2\2\2\u02ca\u02cb\3\2\2\2\u02cb")
        buf.write("\u02cd\3\2\2\2\u02cc\u02ca\3\2\2\2\u02cd\u02ce\bG\2\2")
        buf.write("\u02ce\u008e\3\2\2\2\u02cf\u02d3\5\u009dO\2\u02d0\u02d2")
        buf.write("\5\u009dO\2\u02d1\u02d0\3\2\2\2\u02d2\u02d5\3\2\2\2\u02d3")
        buf.write("\u02d1\3\2\2\2\u02d3\u02d4\3\2\2\2\u02d4\u0090\3\2\2\2")
        buf.write("\u02d5\u02d3\3\2\2\2\u02d6\u02d7\5s:\2\u02d7\u02d8\5\u00a1")
        buf.write("Q\2\u02d8\u0092\3\2\2\2\u02d9\u02db\t\23\2\2\u02da\u02dc")
        buf.write("\t\16\2\2\u02db\u02da\3\2\2\2\u02db\u02dc\3\2\2\2\u02dc")
        buf.write("\u02dd\3\2\2\2\u02dd\u02de\5\u009bN\2\u02de\u0094\3\2")
        buf.write("\2\2\u02df\u02e0\7^\2\2\u02e0\u02f5\t\24\2\2\u02e1\u02e6")
        buf.write("\7^\2\2\u02e2\u02e4\t\25\2\2\u02e3\u02e2\3\2\2\2\u02e3")
        buf.write("\u02e4\3\2\2\2\u02e4\u02e5\3\2\2\2\u02e5\u02e7\t\7\2\2")
        buf.write("\u02e6\u02e3\3\2\2\2\u02e6\u02e7\3\2\2\2\u02e7\u02e8\3")
        buf.write("\2\2\2\u02e8\u02f5\t\7\2\2\u02e9\u02eb\7^\2\2\u02ea\u02ec")
        buf.write("\7w\2\2\u02eb\u02ea\3\2\2\2\u02ec\u02ed\3\2\2\2\u02ed")
        buf.write("\u02eb\3\2\2\2\u02ed\u02ee\3\2\2\2\u02ee\u02ef\3\2\2\2")
        buf.write("\u02ef\u02f0\5\u0099M\2\u02f0\u02f1\5\u0099M\2\u02f1\u02f2")
        buf.write("\5\u0099M\2\u02f2\u02f3\5\u0099M\2\u02f3\u02f5\3\2\2\2")
        buf.write("\u02f4\u02df\3\2\2\2\u02f4\u02e1\3\2\2\2\u02f4\u02e9\3")
        buf.write("\2\2\2\u02f5\u0096\3\2\2\2\u02f6\u02ff\5\u0099M\2\u02f7")
        buf.write("\u02fa\5\u0099M\2\u02f8\u02fa\7a\2\2\u02f9\u02f7\3\2\2")
        buf.write("\2\u02f9\u02f8\3\2\2\2\u02fa\u02fd\3\2\2\2\u02fb\u02f9")
        buf.write("\3\2\2\2\u02fb\u02fc\3\2\2\2\u02fc\u02fe\3\2\2\2\u02fd")
        buf.write("\u02fb\3\2\2\2\u02fe\u0300\5\u0099M\2\u02ff\u02fb\3\2")
        buf.write("\2\2\u02ff\u0300\3\2\2\2\u0300\u0098\3\2\2\2\u0301\u0302")
        buf.write("\t\5\2\2\u0302\u009a\3\2\2\2\u0303\u030b\t\26\2\2\u0304")
        buf.write("\u0306\t\27\2\2\u0305\u0304\3\2\2\2\u0306\u0309\3\2\2")
        buf.write("\2\u0307\u0305\3\2\2\2\u0307\u0308\3\2\2\2\u0308\u030a")
        buf.write("\3\2\2\2\u0309\u0307\3\2\2\2\u030a\u030c\t\26\2\2\u030b")
        buf.write("\u0307\3\2\2\2\u030b\u030c\3\2\2\2\u030c\u009c\3\2\2\2")
        buf.write("\u030d\u0310\5\u009fP\2\u030e\u0310\t\26\2\2\u030f\u030d")
        buf.write("\3\2\2\2\u030f\u030e\3\2\2\2\u0310\u009e\3\2\2\2\u0311")
        buf.write("\u0312\t\30\2\2\u0312\u00a0\3\2\2\2\u0313\u0314\t\31\2")
        buf.write("\2\u0314\u00a2\3\2\2\2:\2\u0196\u019e\u01a4\u01ac\u01bf")
        buf.write("\u01c9\u01d9\u0203\u0208\u020b\u020d\u0210\u0218\u021c")
        buf.write("\u021f\u0225\u022c\u0230\u0233\u023b\u023f\u0242\u0247")
        buf.write("\u024b\u024e\u0251\u0256\u0259\u025b\u0261\u0264\u0268")
        buf.write("\u026c\u0270\u0284\u0296\u029c\u02a1\u02a8\u02aa\u02b2")
        buf.write("\u02bc\u02ca\u02d3\u02db\u02e3\u02e6\u02ed\u02f4\u02f9")
        buf.write("\u02fb\u02ff\u0307\u030b\u030f\3\2\3\2")
        return buf.getvalue()


class nlpql_lexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    DEBUG = 1
    DEFAULT = 2
    FINAL = 3
    PHENOTYPE_NAME = 4
    VERSION = 5
    DESCRIPTION = 6
    DATAMODEL = 7
    INCLUDE = 8
    CALLED = 9
    CODE_SYSTEM = 10
    VALUE_SET = 11
    TERM_SET = 12
    DOCUMENT_SET = 13
    COHORT = 14
    POPULATION = 15
    DEFINE = 16
    CONTEXT = 17
    MIN_VALUE = 18
    MAX_VALUE = 19
    LIMIT = 20
    OMOP = 21
    CLARITY_CORE = 22
    OHDSI_HELPERS = 23
    ALL = 24
    PATIENT = 25
    DOCUMENT = 26
    WHERE = 27
    AND = 28
    OR = 29
    NOT = 30
    GT = 31
    LT = 32
    LTE = 33
    GTE = 34
    EQUAL = 35
    IS = 36
    LIKE = 37
    BETWEEN = 38
    NOT_EQUAL = 39
    BANG = 40
    PLUS = 41
    MINUS = 42
    MULT = 43
    DIV = 44
    CARET = 45
    MOD = 46
    SEMI = 47
    COLON = 48
    DOT = 49
    COMMA = 50
    L_PAREN = 51
    R_PAREN = 52
    L_BRACKET = 53
    R_BRACKET = 54
    L_CURLY = 55
    R_CURLY = 56
    DECIMAL = 57
    HEX = 58
    OCT = 59
    BINARY = 60
    FLOAT = 61
    HEX_FLOAT = 62
    BOOL = 63
    NULL = 64
    IN = 65
    CHAR = 66
    STRING = 67
    WS = 68
    COMMENT = 69
    LINE_COMMENT = 70
    IDENTIFIER = 71
    TIME = 72

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'debug'", "'default'", "'final'", "'phenotype'", "'version'", 
            "'description'", "'datamodel'", "'include'", "'called'", "'codesystem'", 
            "'valueset'", "'termset'", "'documentset'", "'cohort'", "'population'", 
            "'define'", "'context'", "'minimum_value'", "'maximum_value'", 
            "'limit'", "'OMOP'", "'ClarityCore'", "'OHDSIHelpers'", "'All'", 
            "'Patient'", "'Document'", "'>'", "'<'", "'<='", "'>='", "'=='", 
            "'!='", "'!'", "'+'", "'-'", "'*'", "'/'", "'^'", "'%'", "';'", 
            "':'", "'.'", "','", "'('", "')'", "'['", "']'", "'{'", "'}'" ]

    symbolicNames = [ "<INVALID>",
            "DEBUG", "DEFAULT", "FINAL", "PHENOTYPE_NAME", "VERSION", "DESCRIPTION", 
            "DATAMODEL", "INCLUDE", "CALLED", "CODE_SYSTEM", "VALUE_SET", 
            "TERM_SET", "DOCUMENT_SET", "COHORT", "POPULATION", "DEFINE", 
            "CONTEXT", "MIN_VALUE", "MAX_VALUE", "LIMIT", "OMOP", "CLARITY_CORE", 
            "OHDSI_HELPERS", "ALL", "PATIENT", "DOCUMENT", "WHERE", "AND", 
            "OR", "NOT", "GT", "LT", "LTE", "GTE", "EQUAL", "IS", "LIKE", 
            "BETWEEN", "NOT_EQUAL", "BANG", "PLUS", "MINUS", "MULT", "DIV", 
            "CARET", "MOD", "SEMI", "COLON", "DOT", "COMMA", "L_PAREN", 
            "R_PAREN", "L_BRACKET", "R_BRACKET", "L_CURLY", "R_CURLY", "DECIMAL", 
            "HEX", "OCT", "BINARY", "FLOAT", "HEX_FLOAT", "BOOL", "NULL", 
            "IN", "CHAR", "STRING", "WS", "COMMENT", "LINE_COMMENT", "IDENTIFIER", 
            "TIME" ]

    ruleNames = [ "DEBUG", "DEFAULT", "FINAL", "PHENOTYPE_NAME", "VERSION", 
                  "DESCRIPTION", "DATAMODEL", "INCLUDE", "CALLED", "CODE_SYSTEM", 
                  "VALUE_SET", "TERM_SET", "DOCUMENT_SET", "COHORT", "POPULATION", 
                  "DEFINE", "CONTEXT", "MIN_VALUE", "MAX_VALUE", "LIMIT", 
                  "OMOP", "CLARITY_CORE", "OHDSI_HELPERS", "ALL", "PATIENT", 
                  "DOCUMENT", "WHERE", "AND", "OR", "NOT", "GT", "LT", "LTE", 
                  "GTE", "EQUAL", "IS", "LIKE", "BETWEEN", "NOT_EQUAL", 
                  "BANG", "PLUS", "MINUS", "MULT", "DIV", "CARET", "MOD", 
                  "SEMI", "COLON", "DOT", "COMMA", "L_PAREN", "R_PAREN", 
                  "L_BRACKET", "R_BRACKET", "L_CURLY", "R_CURLY", "DECIMAL", 
                  "HEX", "OCT", "BINARY", "FLOAT", "HEX_FLOAT", "BOOL", 
                  "NULL", "IN", "CHAR", "STRING", "WS", "COMMENT", "LINE_COMMENT", 
                  "IDENTIFIER", "TIME", "ExponentPart", "EscapeSequence", 
                  "HexDigits", "HexDigit", "Digits", "LetterOrDigit", "Letter", 
                  "TimeUnit" ]

    grammarFileName = "nlpql_lexer.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.7.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


