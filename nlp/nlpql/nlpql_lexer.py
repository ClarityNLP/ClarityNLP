# Generated from nlpql_lexer.g4 by ANTLR 4.7.1
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2K")
        buf.write("\u0321\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
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
        buf.write("L\4M\tM\4N\tN\4O\tO\4P\tP\4Q\tQ\4R\tR\3\2\3\2\3\2\3\2")
        buf.write("\3\2\3\2\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\4\3\4\3\4\3")
        buf.write("\4\3\4\3\4\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\6")
        buf.write("\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\7\3\7\3\7\3\7\3\7\3\7\3")
        buf.write("\7\3\7\3\7\3\7\3\7\3\7\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b")
        buf.write("\3\b\3\b\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\n\3\n\3\n\3")
        buf.write("\n\3\n\3\n\3\n\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3\13")
        buf.write("\3\13\3\13\3\13\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3")
        buf.write("\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\16\3\16\3\16\3\16\3\16")
        buf.write("\3\16\3\16\3\16\3\16\3\16\3\16\3\16\3\17\3\17\3\17\3\17")
        buf.write("\3\17\3\17\3\17\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\20")
        buf.write("\3\20\3\20\3\20\3\21\3\21\3\21\3\21\3\21\3\21\3\21\3\22")
        buf.write("\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\23\3\23\3\23\3\23")
        buf.write("\3\23\3\23\3\23\3\23\3\23\3\23\3\23\3\23\3\23\3\23\3\24")
        buf.write("\3\24\3\24\3\24\3\24\3\24\3\24\3\24\3\24\3\24\3\24\3\24")
        buf.write("\3\24\3\24\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25")
        buf.write("\3\25\3\26\3\26\3\26\3\26\3\26\3\26\3\27\3\27\3\27\3\27")
        buf.write("\3\27\3\30\3\30\3\30\3\30\3\30\3\30\3\30\3\30\3\30\3\30")
        buf.write("\3\30\3\30\3\31\3\31\3\31\3\31\3\31\3\31\3\31\3\31\3\31")
        buf.write("\3\31\3\31\3\31\3\31\3\32\3\32\3\32\3\32\3\33\3\33\3\33")
        buf.write("\3\33\3\33\3\33\3\33\3\33\3\34\3\34\3\34\3\34\3\34\3\34")
        buf.write("\3\34\3\34\3\34\3\35\3\35\3\35\3\35\3\35\3\35\3\35\3\35")
        buf.write("\3\35\3\35\5\35\u01a3\n\35\3\36\3\36\3\36\3\36\3\36\3")
        buf.write("\36\5\36\u01ab\n\36\3\37\3\37\3\37\3\37\5\37\u01b1\n\37")
        buf.write("\3 \3 \3 \3 \3 \3 \5 \u01b9\n \3!\3!\3\"\3\"\3#\3#\3#")
        buf.write("\3$\3$\3$\3%\3%\3%\3&\3&\3&\3&\5&\u01cc\n&\3\'\3\'\3\'")
        buf.write("\3\'\3\'\3\'\3\'\3\'\5\'\u01d6\n\'\3(\3(\3(\3(\3(\3(\3")
        buf.write("(\3(\3(\3(\3(\3(\3(\3(\5(\u01e6\n(\3)\3)\3)\3*\3*\3+\3")
        buf.write("+\3,\3,\3-\3-\3.\3.\3/\3/\3\60\3\60\3\61\3\61\3\62\3\62")
        buf.write("\3\63\3\63\3\64\3\64\3\65\3\65\3\66\3\66\3\67\3\67\38")
        buf.write("\38\39\39\3:\3:\3;\3;\3;\5;\u0210\n;\3;\6;\u0213\n;\r")
        buf.write(";\16;\u0214\3;\5;\u0218\n;\5;\u021a\n;\3;\5;\u021d\n;")
        buf.write("\3<\3<\3<\3<\7<\u0223\n<\f<\16<\u0226\13<\3<\5<\u0229")
        buf.write("\n<\3<\5<\u022c\n<\3=\3=\7=\u0230\n=\f=\16=\u0233\13=")
        buf.write("\3=\3=\7=\u0237\n=\f=\16=\u023a\13=\3=\5=\u023d\n=\3=")
        buf.write("\5=\u0240\n=\3>\3>\3>\3>\7>\u0246\n>\f>\16>\u0249\13>")
        buf.write("\3>\5>\u024c\n>\3>\5>\u024f\n>\3?\3?\3?\5?\u0254\n?\3")
        buf.write("?\3?\5?\u0258\n?\3?\5?\u025b\n?\3?\5?\u025e\n?\3?\3?\3")
        buf.write("?\5?\u0263\n?\3?\5?\u0266\n?\5?\u0268\n?\3@\3@\3@\3@\5")
        buf.write("@\u026e\n@\3@\5@\u0271\n@\3@\3@\5@\u0275\n@\3@\3@\5@\u0279")
        buf.write("\n@\3@\3@\5@\u027d\n@\3A\3A\3A\3A\3A\3A\3A\3A\3A\3A\3")
        buf.write("A\3A\3A\3A\3A\3A\3A\3A\5A\u0291\nA\3B\3B\3B\3B\3B\3B\3")
        buf.write("B\3B\3B\3B\3B\3B\3B\3B\3B\3B\5B\u02a3\nB\3C\3C\3C\3C\5")
        buf.write("C\u02a9\nC\3D\3D\3D\5D\u02ae\nD\3D\3D\3E\3E\3E\7E\u02b5")
        buf.write("\nE\fE\16E\u02b8\13E\3E\3E\3F\6F\u02bd\nF\rF\16F\u02be")
        buf.write("\3F\3F\3G\3G\3G\3G\7G\u02c7\nG\fG\16G\u02ca\13G\3G\3G")
        buf.write("\3G\3G\3G\3H\3H\3H\3H\7H\u02d5\nH\fH\16H\u02d8\13H\3H")
        buf.write("\3H\3I\3I\7I\u02de\nI\fI\16I\u02e1\13I\3J\3J\3J\3K\3K")
        buf.write("\5K\u02e8\nK\3K\3K\3L\3L\3L\3L\5L\u02f0\nL\3L\5L\u02f3")
        buf.write("\nL\3L\3L\3L\6L\u02f8\nL\rL\16L\u02f9\3L\3L\3L\3L\3L\5")
        buf.write("L\u0301\nL\3M\3M\3M\7M\u0306\nM\fM\16M\u0309\13M\3M\5")
        buf.write("M\u030c\nM\3N\3N\3O\3O\7O\u0312\nO\fO\16O\u0315\13O\3")
        buf.write("O\5O\u0318\nO\3P\3P\5P\u031c\nP\3Q\3Q\3R\3R\3\u02c8\2")
        buf.write("S\3\3\5\4\7\5\t\6\13\7\r\b\17\t\21\n\23\13\25\f\27\r\31")
        buf.write("\16\33\17\35\20\37\21!\22#\23%\24\'\25)\26+\27-\30/\31")
        buf.write("\61\32\63\33\65\34\67\359\36;\37= ?!A\"C#E$G%I&K\'M(O")
        buf.write(")Q*S+U,W-Y.[/]\60_\61a\62c\63e\64g\65i\66k\67m8o9q:s;")
        buf.write("u<w=y>{?}@\177A\u0081B\u0083C\u0085D\u0087E\u0089F\u008b")
        buf.write("G\u008dH\u008fI\u0091J\u0093K\u0095\2\u0097\2\u0099\2")
        buf.write("\u009b\2\u009d\2\u009f\2\u00a1\2\u00a3\2\3\2\32\3\2\63")
        buf.write(";\4\2NNnn\4\2ZZzz\5\2\62;CHch\6\2\62;CHaach\3\2\629\4")
        buf.write("\2\629aa\4\2DDdd\3\2\62\63\4\2\62\63aa\6\2FFHHffhh\4\2")
        buf.write("RRrr\4\2--//\6\2\f\f\17\17))^^\6\2\f\f\17\17$$^^\5\2\13")
        buf.write("\f\16\17\"\"\4\2\f\f\17\17\4\2GGgg\n\2$$))^^ddhhppttv")
        buf.write("v\3\2\62\65\3\2\62;\4\2\62;aa\6\2&&C\\aac|\6\2FFJJOO[")
        buf.write("[\2\u0354\2\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2")
        buf.write("\2\2\2\13\3\2\2\2\2\r\3\2\2\2\2\17\3\2\2\2\2\21\3\2\2")
        buf.write("\2\2\23\3\2\2\2\2\25\3\2\2\2\2\27\3\2\2\2\2\31\3\2\2\2")
        buf.write("\2\33\3\2\2\2\2\35\3\2\2\2\2\37\3\2\2\2\2!\3\2\2\2\2#")
        buf.write("\3\2\2\2\2%\3\2\2\2\2\'\3\2\2\2\2)\3\2\2\2\2+\3\2\2\2")
        buf.write("\2-\3\2\2\2\2/\3\2\2\2\2\61\3\2\2\2\2\63\3\2\2\2\2\65")
        buf.write("\3\2\2\2\2\67\3\2\2\2\29\3\2\2\2\2;\3\2\2\2\2=\3\2\2\2")
        buf.write("\2?\3\2\2\2\2A\3\2\2\2\2C\3\2\2\2\2E\3\2\2\2\2G\3\2\2")
        buf.write("\2\2I\3\2\2\2\2K\3\2\2\2\2M\3\2\2\2\2O\3\2\2\2\2Q\3\2")
        buf.write("\2\2\2S\3\2\2\2\2U\3\2\2\2\2W\3\2\2\2\2Y\3\2\2\2\2[\3")
        buf.write("\2\2\2\2]\3\2\2\2\2_\3\2\2\2\2a\3\2\2\2\2c\3\2\2\2\2e")
        buf.write("\3\2\2\2\2g\3\2\2\2\2i\3\2\2\2\2k\3\2\2\2\2m\3\2\2\2\2")
        buf.write("o\3\2\2\2\2q\3\2\2\2\2s\3\2\2\2\2u\3\2\2\2\2w\3\2\2\2")
        buf.write("\2y\3\2\2\2\2{\3\2\2\2\2}\3\2\2\2\2\177\3\2\2\2\2\u0081")
        buf.write("\3\2\2\2\2\u0083\3\2\2\2\2\u0085\3\2\2\2\2\u0087\3\2\2")
        buf.write("\2\2\u0089\3\2\2\2\2\u008b\3\2\2\2\2\u008d\3\2\2\2\2\u008f")
        buf.write("\3\2\2\2\2\u0091\3\2\2\2\2\u0093\3\2\2\2\3\u00a5\3\2\2")
        buf.write("\2\5\u00ab\3\2\2\2\7\u00b3\3\2\2\2\t\u00b9\3\2\2\2\13")
        buf.write("\u00c3\3\2\2\2\r\u00cb\3\2\2\2\17\u00d7\3\2\2\2\21\u00e1")
        buf.write("\3\2\2\2\23\u00e9\3\2\2\2\25\u00f0\3\2\2\2\27\u00fb\3")
        buf.write("\2\2\2\31\u0104\3\2\2\2\33\u010c\3\2\2\2\35\u0118\3\2")
        buf.write("\2\2\37\u011f\3\2\2\2!\u012a\3\2\2\2#\u0131\3\2\2\2%\u0139")
        buf.write("\3\2\2\2\'\u0147\3\2\2\2)\u0155\3\2\2\2+\u015f\3\2\2\2")
        buf.write("-\u0165\3\2\2\2/\u016a\3\2\2\2\61\u0176\3\2\2\2\63\u0183")
        buf.write("\3\2\2\2\65\u0187\3\2\2\2\67\u018f\3\2\2\29\u01a2\3\2")
        buf.write("\2\2;\u01aa\3\2\2\2=\u01b0\3\2\2\2?\u01b8\3\2\2\2A\u01ba")
        buf.write("\3\2\2\2C\u01bc\3\2\2\2E\u01be\3\2\2\2G\u01c1\3\2\2\2")
        buf.write("I\u01c4\3\2\2\2K\u01cb\3\2\2\2M\u01d5\3\2\2\2O\u01e5\3")
        buf.write("\2\2\2Q\u01e7\3\2\2\2S\u01ea\3\2\2\2U\u01ec\3\2\2\2W\u01ee")
        buf.write("\3\2\2\2Y\u01f0\3\2\2\2[\u01f2\3\2\2\2]\u01f4\3\2\2\2")
        buf.write("_\u01f6\3\2\2\2a\u01f8\3\2\2\2c\u01fa\3\2\2\2e\u01fc\3")
        buf.write("\2\2\2g\u01fe\3\2\2\2i\u0200\3\2\2\2k\u0202\3\2\2\2m\u0204")
        buf.write("\3\2\2\2o\u0206\3\2\2\2q\u0208\3\2\2\2s\u020a\3\2\2\2")
        buf.write("u\u0219\3\2\2\2w\u021e\3\2\2\2y\u022d\3\2\2\2{\u0241\3")
        buf.write("\2\2\2}\u0267\3\2\2\2\177\u0269\3\2\2\2\u0081\u0290\3")
        buf.write("\2\2\2\u0083\u02a2\3\2\2\2\u0085\u02a8\3\2\2\2\u0087\u02aa")
        buf.write("\3\2\2\2\u0089\u02b1\3\2\2\2\u008b\u02bc\3\2\2\2\u008d")
        buf.write("\u02c2\3\2\2\2\u008f\u02d0\3\2\2\2\u0091\u02db\3\2\2\2")
        buf.write("\u0093\u02e2\3\2\2\2\u0095\u02e5\3\2\2\2\u0097\u0300\3")
        buf.write("\2\2\2\u0099\u0302\3\2\2\2\u009b\u030d\3\2\2\2\u009d\u030f")
        buf.write("\3\2\2\2\u009f\u031b\3\2\2\2\u00a1\u031d\3\2\2\2\u00a3")
        buf.write("\u031f\3\2\2\2\u00a5\u00a6\7f\2\2\u00a6\u00a7\7g\2\2\u00a7")
        buf.write("\u00a8\7d\2\2\u00a8\u00a9\7w\2\2\u00a9\u00aa\7i\2\2\u00aa")
        buf.write("\4\3\2\2\2\u00ab\u00ac\7f\2\2\u00ac\u00ad\7g\2\2\u00ad")
        buf.write("\u00ae\7h\2\2\u00ae\u00af\7c\2\2\u00af\u00b0\7w\2\2\u00b0")
        buf.write("\u00b1\7n\2\2\u00b1\u00b2\7v\2\2\u00b2\6\3\2\2\2\u00b3")
        buf.write("\u00b4\7h\2\2\u00b4\u00b5\7k\2\2\u00b5\u00b6\7p\2\2\u00b6")
        buf.write("\u00b7\7c\2\2\u00b7\u00b8\7n\2\2\u00b8\b\3\2\2\2\u00b9")
        buf.write("\u00ba\7r\2\2\u00ba\u00bb\7j\2\2\u00bb\u00bc\7g\2\2\u00bc")
        buf.write("\u00bd\7p\2\2\u00bd\u00be\7q\2\2\u00be\u00bf\7v\2\2\u00bf")
        buf.write("\u00c0\7{\2\2\u00c0\u00c1\7r\2\2\u00c1\u00c2\7g\2\2\u00c2")
        buf.write("\n\3\2\2\2\u00c3\u00c4\7x\2\2\u00c4\u00c5\7g\2\2\u00c5")
        buf.write("\u00c6\7t\2\2\u00c6\u00c7\7u\2\2\u00c7\u00c8\7k\2\2\u00c8")
        buf.write("\u00c9\7q\2\2\u00c9\u00ca\7p\2\2\u00ca\f\3\2\2\2\u00cb")
        buf.write("\u00cc\7f\2\2\u00cc\u00cd\7g\2\2\u00cd\u00ce\7u\2\2\u00ce")
        buf.write("\u00cf\7e\2\2\u00cf\u00d0\7t\2\2\u00d0\u00d1\7k\2\2\u00d1")
        buf.write("\u00d2\7r\2\2\u00d2\u00d3\7v\2\2\u00d3\u00d4\7k\2\2\u00d4")
        buf.write("\u00d5\7q\2\2\u00d5\u00d6\7p\2\2\u00d6\16\3\2\2\2\u00d7")
        buf.write("\u00d8\7f\2\2\u00d8\u00d9\7c\2\2\u00d9\u00da\7v\2\2\u00da")
        buf.write("\u00db\7c\2\2\u00db\u00dc\7o\2\2\u00dc\u00dd\7q\2\2\u00dd")
        buf.write("\u00de\7f\2\2\u00de\u00df\7g\2\2\u00df\u00e0\7n\2\2\u00e0")
        buf.write("\20\3\2\2\2\u00e1\u00e2\7k\2\2\u00e2\u00e3\7p\2\2\u00e3")
        buf.write("\u00e4\7e\2\2\u00e4\u00e5\7n\2\2\u00e5\u00e6\7w\2\2\u00e6")
        buf.write("\u00e7\7f\2\2\u00e7\u00e8\7g\2\2\u00e8\22\3\2\2\2\u00e9")
        buf.write("\u00ea\7e\2\2\u00ea\u00eb\7c\2\2\u00eb\u00ec\7n\2\2\u00ec")
        buf.write("\u00ed\7n\2\2\u00ed\u00ee\7g\2\2\u00ee\u00ef\7f\2\2\u00ef")
        buf.write("\24\3\2\2\2\u00f0\u00f1\7e\2\2\u00f1\u00f2\7q\2\2\u00f2")
        buf.write("\u00f3\7f\2\2\u00f3\u00f4\7g\2\2\u00f4\u00f5\7u\2\2\u00f5")
        buf.write("\u00f6\7{\2\2\u00f6\u00f7\7u\2\2\u00f7\u00f8\7v\2\2\u00f8")
        buf.write("\u00f9\7g\2\2\u00f9\u00fa\7o\2\2\u00fa\26\3\2\2\2\u00fb")
        buf.write("\u00fc\7x\2\2\u00fc\u00fd\7c\2\2\u00fd\u00fe\7n\2\2\u00fe")
        buf.write("\u00ff\7w\2\2\u00ff\u0100\7g\2\2\u0100\u0101\7u\2\2\u0101")
        buf.write("\u0102\7g\2\2\u0102\u0103\7v\2\2\u0103\30\3\2\2\2\u0104")
        buf.write("\u0105\7v\2\2\u0105\u0106\7g\2\2\u0106\u0107\7t\2\2\u0107")
        buf.write("\u0108\7o\2\2\u0108\u0109\7u\2\2\u0109\u010a\7g\2\2\u010a")
        buf.write("\u010b\7v\2\2\u010b\32\3\2\2\2\u010c\u010d\7f\2\2\u010d")
        buf.write("\u010e\7q\2\2\u010e\u010f\7e\2\2\u010f\u0110\7w\2\2\u0110")
        buf.write("\u0111\7o\2\2\u0111\u0112\7g\2\2\u0112\u0113\7p\2\2\u0113")
        buf.write("\u0114\7v\2\2\u0114\u0115\7u\2\2\u0115\u0116\7g\2\2\u0116")
        buf.write("\u0117\7v\2\2\u0117\34\3\2\2\2\u0118\u0119\7e\2\2\u0119")
        buf.write("\u011a\7q\2\2\u011a\u011b\7j\2\2\u011b\u011c\7q\2\2\u011c")
        buf.write("\u011d\7t\2\2\u011d\u011e\7v\2\2\u011e\36\3\2\2\2\u011f")
        buf.write("\u0120\7r\2\2\u0120\u0121\7q\2\2\u0121\u0122\7r\2\2\u0122")
        buf.write("\u0123\7w\2\2\u0123\u0124\7n\2\2\u0124\u0125\7c\2\2\u0125")
        buf.write("\u0126\7v\2\2\u0126\u0127\7k\2\2\u0127\u0128\7q\2\2\u0128")
        buf.write("\u0129\7p\2\2\u0129 \3\2\2\2\u012a\u012b\7f\2\2\u012b")
        buf.write("\u012c\7g\2\2\u012c\u012d\7h\2\2\u012d\u012e\7k\2\2\u012e")
        buf.write("\u012f\7p\2\2\u012f\u0130\7g\2\2\u0130\"\3\2\2\2\u0131")
        buf.write("\u0132\7e\2\2\u0132\u0133\7q\2\2\u0133\u0134\7p\2\2\u0134")
        buf.write("\u0135\7v\2\2\u0135\u0136\7g\2\2\u0136\u0137\7z\2\2\u0137")
        buf.write("\u0138\7v\2\2\u0138$\3\2\2\2\u0139\u013a\7o\2\2\u013a")
        buf.write("\u013b\7k\2\2\u013b\u013c\7p\2\2\u013c\u013d\7k\2\2\u013d")
        buf.write("\u013e\7o\2\2\u013e\u013f\7w\2\2\u013f\u0140\7o\2\2\u0140")
        buf.write("\u0141\7a\2\2\u0141\u0142\7x\2\2\u0142\u0143\7c\2\2\u0143")
        buf.write("\u0144\7n\2\2\u0144\u0145\7w\2\2\u0145\u0146\7g\2\2\u0146")
        buf.write("&\3\2\2\2\u0147\u0148\7o\2\2\u0148\u0149\7c\2\2\u0149")
        buf.write("\u014a\7z\2\2\u014a\u014b\7k\2\2\u014b\u014c\7o\2\2\u014c")
        buf.write("\u014d\7w\2\2\u014d\u014e\7o\2\2\u014e\u014f\7a\2\2\u014f")
        buf.write("\u0150\7x\2\2\u0150\u0151\7c\2\2\u0151\u0152\7n\2\2\u0152")
        buf.write("\u0153\7w\2\2\u0153\u0154\7g\2\2\u0154(\3\2\2\2\u0155")
        buf.write("\u0156\7g\2\2\u0156\u0157\7p\2\2\u0157\u0158\7w\2\2\u0158")
        buf.write("\u0159\7o\2\2\u0159\u015a\7a\2\2\u015a\u015b\7n\2\2\u015b")
        buf.write("\u015c\7k\2\2\u015c\u015d\7u\2\2\u015d\u015e\7v\2\2\u015e")
        buf.write("*\3\2\2\2\u015f\u0160\7n\2\2\u0160\u0161\7k\2\2\u0161")
        buf.write("\u0162\7o\2\2\u0162\u0163\7k\2\2\u0163\u0164\7v\2\2\u0164")
        buf.write(",\3\2\2\2\u0165\u0166\7Q\2\2\u0166\u0167\7O\2\2\u0167")
        buf.write("\u0168\7Q\2\2\u0168\u0169\7R\2\2\u0169.\3\2\2\2\u016a")
        buf.write("\u016b\7E\2\2\u016b\u016c\7n\2\2\u016c\u016d\7c\2\2\u016d")
        buf.write("\u016e\7t\2\2\u016e\u016f\7k\2\2\u016f\u0170\7v\2\2\u0170")
        buf.write("\u0171\7{\2\2\u0171\u0172\7E\2\2\u0172\u0173\7q\2\2\u0173")
        buf.write("\u0174\7t\2\2\u0174\u0175\7g\2\2\u0175\60\3\2\2\2\u0176")
        buf.write("\u0177\7Q\2\2\u0177\u0178\7J\2\2\u0178\u0179\7F\2\2\u0179")
        buf.write("\u017a\7U\2\2\u017a\u017b\7K\2\2\u017b\u017c\7J\2\2\u017c")
        buf.write("\u017d\7g\2\2\u017d\u017e\7n\2\2\u017e\u017f\7r\2\2\u017f")
        buf.write("\u0180\7g\2\2\u0180\u0181\7t\2\2\u0181\u0182\7u\2\2\u0182")
        buf.write("\62\3\2\2\2\u0183\u0184\7C\2\2\u0184\u0185\7n\2\2\u0185")
        buf.write("\u0186\7n\2\2\u0186\64\3\2\2\2\u0187\u0188\7R\2\2\u0188")
        buf.write("\u0189\7c\2\2\u0189\u018a\7v\2\2\u018a\u018b\7k\2\2\u018b")
        buf.write("\u018c\7g\2\2\u018c\u018d\7p\2\2\u018d\u018e\7v\2\2\u018e")
        buf.write("\66\3\2\2\2\u018f\u0190\7F\2\2\u0190\u0191\7q\2\2\u0191")
        buf.write("\u0192\7e\2\2\u0192\u0193\7w\2\2\u0193\u0194\7o\2\2\u0194")
        buf.write("\u0195\7g\2\2\u0195\u0196\7p\2\2\u0196\u0197\7v\2\2\u0197")
        buf.write("8\3\2\2\2\u0198\u0199\7Y\2\2\u0199\u019a\7J\2\2\u019a")
        buf.write("\u019b\7G\2\2\u019b\u019c\7T\2\2\u019c\u01a3\7G\2\2\u019d")
        buf.write("\u019e\7y\2\2\u019e\u019f\7j\2\2\u019f\u01a0\7g\2\2\u01a0")
        buf.write("\u01a1\7t\2\2\u01a1\u01a3\7g\2\2\u01a2\u0198\3\2\2\2\u01a2")
        buf.write("\u019d\3\2\2\2\u01a3:\3\2\2\2\u01a4\u01a5\7C\2\2\u01a5")
        buf.write("\u01a6\7P\2\2\u01a6\u01ab\7F\2\2\u01a7\u01a8\7c\2\2\u01a8")
        buf.write("\u01a9\7p\2\2\u01a9\u01ab\7f\2\2\u01aa\u01a4\3\2\2\2\u01aa")
        buf.write("\u01a7\3\2\2\2\u01ab<\3\2\2\2\u01ac\u01ad\7Q\2\2\u01ad")
        buf.write("\u01b1\7T\2\2\u01ae\u01af\7q\2\2\u01af\u01b1\7t\2\2\u01b0")
        buf.write("\u01ac\3\2\2\2\u01b0\u01ae\3\2\2\2\u01b1>\3\2\2\2\u01b2")
        buf.write("\u01b3\7P\2\2\u01b3\u01b4\7Q\2\2\u01b4\u01b9\7V\2\2\u01b5")
        buf.write("\u01b6\7p\2\2\u01b6\u01b7\7q\2\2\u01b7\u01b9\7v\2\2\u01b8")
        buf.write("\u01b2\3\2\2\2\u01b8\u01b5\3\2\2\2\u01b9@\3\2\2\2\u01ba")
        buf.write("\u01bb\7@\2\2\u01bbB\3\2\2\2\u01bc\u01bd\7>\2\2\u01bd")
        buf.write("D\3\2\2\2\u01be\u01bf\7>\2\2\u01bf\u01c0\7?\2\2\u01c0")
        buf.write("F\3\2\2\2\u01c1\u01c2\7@\2\2\u01c2\u01c3\7?\2\2\u01c3")
        buf.write("H\3\2\2\2\u01c4\u01c5\7?\2\2\u01c5\u01c6\7?\2\2\u01c6")
        buf.write("J\3\2\2\2\u01c7\u01c8\7k\2\2\u01c8\u01cc\7u\2\2\u01c9")
        buf.write("\u01ca\7K\2\2\u01ca\u01cc\7U\2\2\u01cb\u01c7\3\2\2\2\u01cb")
        buf.write("\u01c9\3\2\2\2\u01ccL\3\2\2\2\u01cd\u01ce\7n\2\2\u01ce")
        buf.write("\u01cf\7k\2\2\u01cf\u01d0\7m\2\2\u01d0\u01d6\7g\2\2\u01d1")
        buf.write("\u01d2\7N\2\2\u01d2\u01d3\7K\2\2\u01d3\u01d4\7M\2\2\u01d4")
        buf.write("\u01d6\7G\2\2\u01d5\u01cd\3\2\2\2\u01d5\u01d1\3\2\2\2")
        buf.write("\u01d6N\3\2\2\2\u01d7\u01d8\7d\2\2\u01d8\u01d9\7g\2\2")
        buf.write("\u01d9\u01da\7v\2\2\u01da\u01db\7y\2\2\u01db\u01dc\7g")
        buf.write("\2\2\u01dc\u01dd\7g\2\2\u01dd\u01e6\7p\2\2\u01de\u01df")
        buf.write("\7D\2\2\u01df\u01e0\7G\2\2\u01e0\u01e1\7V\2\2\u01e1\u01e2")
        buf.write("\7Y\2\2\u01e2\u01e3\7G\2\2\u01e3\u01e4\7G\2\2\u01e4\u01e6")
        buf.write("\7P\2\2\u01e5\u01d7\3\2\2\2\u01e5\u01de\3\2\2\2\u01e6")
        buf.write("P\3\2\2\2\u01e7\u01e8\7#\2\2\u01e8\u01e9\7?\2\2\u01e9")
        buf.write("R\3\2\2\2\u01ea\u01eb\7#\2\2\u01ebT\3\2\2\2\u01ec\u01ed")
        buf.write("\7-\2\2\u01edV\3\2\2\2\u01ee\u01ef\7/\2\2\u01efX\3\2\2")
        buf.write("\2\u01f0\u01f1\7,\2\2\u01f1Z\3\2\2\2\u01f2\u01f3\7\61")
        buf.write("\2\2\u01f3\\\3\2\2\2\u01f4\u01f5\7`\2\2\u01f5^\3\2\2\2")
        buf.write("\u01f6\u01f7\7\'\2\2\u01f7`\3\2\2\2\u01f8\u01f9\7=\2\2")
        buf.write("\u01f9b\3\2\2\2\u01fa\u01fb\7<\2\2\u01fbd\3\2\2\2\u01fc")
        buf.write("\u01fd\7\60\2\2\u01fdf\3\2\2\2\u01fe\u01ff\7.\2\2\u01ff")
        buf.write("h\3\2\2\2\u0200\u0201\7*\2\2\u0201j\3\2\2\2\u0202\u0203")
        buf.write("\7+\2\2\u0203l\3\2\2\2\u0204\u0205\7]\2\2\u0205n\3\2\2")
        buf.write("\2\u0206\u0207\7_\2\2\u0207p\3\2\2\2\u0208\u0209\7}\2")
        buf.write("\2\u0209r\3\2\2\2\u020a\u020b\7\177\2\2\u020bt\3\2\2\2")
        buf.write("\u020c\u021a\7\62\2\2\u020d\u0217\t\2\2\2\u020e\u0210")
        buf.write("\5\u009dO\2\u020f\u020e\3\2\2\2\u020f\u0210\3\2\2\2\u0210")
        buf.write("\u0218\3\2\2\2\u0211\u0213\7a\2\2\u0212\u0211\3\2\2\2")
        buf.write("\u0213\u0214\3\2\2\2\u0214\u0212\3\2\2\2\u0214\u0215\3")
        buf.write("\2\2\2\u0215\u0216\3\2\2\2\u0216\u0218\5\u009dO\2\u0217")
        buf.write("\u020f\3\2\2\2\u0217\u0212\3\2\2\2\u0218\u021a\3\2\2\2")
        buf.write("\u0219\u020c\3\2\2\2\u0219\u020d\3\2\2\2\u021a\u021c\3")
        buf.write("\2\2\2\u021b\u021d\t\3\2\2\u021c\u021b\3\2\2\2\u021c\u021d")
        buf.write("\3\2\2\2\u021dv\3\2\2\2\u021e\u021f\7\62\2\2\u021f\u0220")
        buf.write("\t\4\2\2\u0220\u0228\t\5\2\2\u0221\u0223\t\6\2\2\u0222")
        buf.write("\u0221\3\2\2\2\u0223\u0226\3\2\2\2\u0224\u0222\3\2\2\2")
        buf.write("\u0224\u0225\3\2\2\2\u0225\u0227\3\2\2\2\u0226\u0224\3")
        buf.write("\2\2\2\u0227\u0229\t\5\2\2\u0228\u0224\3\2\2\2\u0228\u0229")
        buf.write("\3\2\2\2\u0229\u022b\3\2\2\2\u022a\u022c\t\3\2\2\u022b")
        buf.write("\u022a\3\2\2\2\u022b\u022c\3\2\2\2\u022cx\3\2\2\2\u022d")
        buf.write("\u0231\7\62\2\2\u022e\u0230\7a\2\2\u022f\u022e\3\2\2\2")
        buf.write("\u0230\u0233\3\2\2\2\u0231\u022f\3\2\2\2\u0231\u0232\3")
        buf.write("\2\2\2\u0232\u0234\3\2\2\2\u0233\u0231\3\2\2\2\u0234\u023c")
        buf.write("\t\7\2\2\u0235\u0237\t\b\2\2\u0236\u0235\3\2\2\2\u0237")
        buf.write("\u023a\3\2\2\2\u0238\u0236\3\2\2\2\u0238\u0239\3\2\2\2")
        buf.write("\u0239\u023b\3\2\2\2\u023a\u0238\3\2\2\2\u023b\u023d\t")
        buf.write("\7\2\2\u023c\u0238\3\2\2\2\u023c\u023d\3\2\2\2\u023d\u023f")
        buf.write("\3\2\2\2\u023e\u0240\t\3\2\2\u023f\u023e\3\2\2\2\u023f")
        buf.write("\u0240\3\2\2\2\u0240z\3\2\2\2\u0241\u0242\7\62\2\2\u0242")
        buf.write("\u0243\t\t\2\2\u0243\u024b\t\n\2\2\u0244\u0246\t\13\2")
        buf.write("\2\u0245\u0244\3\2\2\2\u0246\u0249\3\2\2\2\u0247\u0245")
        buf.write("\3\2\2\2\u0247\u0248\3\2\2\2\u0248\u024a\3\2\2\2\u0249")
        buf.write("\u0247\3\2\2\2\u024a\u024c\t\n\2\2\u024b\u0247\3\2\2\2")
        buf.write("\u024b\u024c\3\2\2\2\u024c\u024e\3\2\2\2\u024d\u024f\t")
        buf.write("\3\2\2\u024e\u024d\3\2\2\2\u024e\u024f\3\2\2\2\u024f|")
        buf.write("\3\2\2\2\u0250\u0251\5\u009dO\2\u0251\u0253\7\60\2\2\u0252")
        buf.write("\u0254\5\u009dO\2\u0253\u0252\3\2\2\2\u0253\u0254\3\2")
        buf.write("\2\2\u0254\u0258\3\2\2\2\u0255\u0256\7\60\2\2\u0256\u0258")
        buf.write("\5\u009dO\2\u0257\u0250\3\2\2\2\u0257\u0255\3\2\2\2\u0258")
        buf.write("\u025a\3\2\2\2\u0259\u025b\5\u0095K\2\u025a\u0259\3\2")
        buf.write("\2\2\u025a\u025b\3\2\2\2\u025b\u025d\3\2\2\2\u025c\u025e")
        buf.write("\t\f\2\2\u025d\u025c\3\2\2\2\u025d\u025e\3\2\2\2\u025e")
        buf.write("\u0268\3\2\2\2\u025f\u0265\5\u009dO\2\u0260\u0262\5\u0095")
        buf.write("K\2\u0261\u0263\t\f\2\2\u0262\u0261\3\2\2\2\u0262\u0263")
        buf.write("\3\2\2\2\u0263\u0266\3\2\2\2\u0264\u0266\t\f\2\2\u0265")
        buf.write("\u0260\3\2\2\2\u0265\u0264\3\2\2\2\u0266\u0268\3\2\2\2")
        buf.write("\u0267\u0257\3\2\2\2\u0267\u025f\3\2\2\2\u0268~\3\2\2")
        buf.write("\2\u0269\u026a\7\62\2\2\u026a\u0274\t\4\2\2\u026b\u026d")
        buf.write("\5\u0099M\2\u026c\u026e\7\60\2\2\u026d\u026c\3\2\2\2\u026d")
        buf.write("\u026e\3\2\2\2\u026e\u0275\3\2\2\2\u026f\u0271\5\u0099")
        buf.write("M\2\u0270\u026f\3\2\2\2\u0270\u0271\3\2\2\2\u0271\u0272")
        buf.write("\3\2\2\2\u0272\u0273\7\60\2\2\u0273\u0275\5\u0099M\2\u0274")
        buf.write("\u026b\3\2\2\2\u0274\u0270\3\2\2\2\u0275\u0276\3\2\2\2")
        buf.write("\u0276\u0278\t\r\2\2\u0277\u0279\t\16\2\2\u0278\u0277")
        buf.write("\3\2\2\2\u0278\u0279\3\2\2\2\u0279\u027a\3\2\2\2\u027a")
        buf.write("\u027c\5\u009dO\2\u027b\u027d\t\f\2\2\u027c\u027b\3\2")
        buf.write("\2\2\u027c\u027d\3\2\2\2\u027d\u0080\3\2\2\2\u027e\u027f")
        buf.write("\7v\2\2\u027f\u0280\7t\2\2\u0280\u0281\7w\2\2\u0281\u0291")
        buf.write("\7g\2\2\u0282\u0283\7V\2\2\u0283\u0284\7T\2\2\u0284\u0285")
        buf.write("\7W\2\2\u0285\u0291\7G\2\2\u0286\u0287\7h\2\2\u0287\u0288")
        buf.write("\7c\2\2\u0288\u0289\7n\2\2\u0289\u028a\7u\2\2\u028a\u0291")
        buf.write("\7g\2\2\u028b\u028c\7H\2\2\u028c\u028d\7C\2\2\u028d\u028e")
        buf.write("\7N\2\2\u028e\u028f\7U\2\2\u028f\u0291\7G\2\2\u0290\u027e")
        buf.write("\3\2\2\2\u0290\u0282\3\2\2\2\u0290\u0286\3\2\2\2\u0290")
        buf.write("\u028b\3\2\2\2\u0291\u0082\3\2\2\2\u0292\u0293\7p\2\2")
        buf.write("\u0293\u0294\7w\2\2\u0294\u0295\7n\2\2\u0295\u02a3\7n")
        buf.write("\2\2\u0296\u0297\7P\2\2\u0297\u0298\7W\2\2\u0298\u0299")
        buf.write("\7N\2\2\u0299\u02a3\7N\2\2\u029a\u029b\7P\2\2\u029b\u029c")
        buf.write("\7q\2\2\u029c\u029d\7p\2\2\u029d\u02a3\7g\2\2\u029e\u029f")
        buf.write("\7p\2\2\u029f\u02a0\7q\2\2\u02a0\u02a1\7p\2\2\u02a1\u02a3")
        buf.write("\7g\2\2\u02a2\u0292\3\2\2\2\u02a2\u0296\3\2\2\2\u02a2")
        buf.write("\u029a\3\2\2\2\u02a2\u029e\3\2\2\2\u02a3\u0084\3\2\2\2")
        buf.write("\u02a4\u02a5\7K\2\2\u02a5\u02a9\7P\2\2\u02a6\u02a7\7k")
        buf.write("\2\2\u02a7\u02a9\7p\2\2\u02a8\u02a4\3\2\2\2\u02a8\u02a6")
        buf.write("\3\2\2\2\u02a9\u0086\3\2\2\2\u02aa\u02ad\7)\2\2\u02ab")
        buf.write("\u02ae\n\17\2\2\u02ac\u02ae\5\u0097L\2\u02ad\u02ab\3\2")
        buf.write("\2\2\u02ad\u02ac\3\2\2\2\u02ae\u02af\3\2\2\2\u02af\u02b0")
        buf.write("\7)\2\2\u02b0\u0088\3\2\2\2\u02b1\u02b6\7$\2\2\u02b2\u02b5")
        buf.write("\n\20\2\2\u02b3\u02b5\5\u0097L\2\u02b4\u02b2\3\2\2\2\u02b4")
        buf.write("\u02b3\3\2\2\2\u02b5\u02b8\3\2\2\2\u02b6\u02b4\3\2\2\2")
        buf.write("\u02b6\u02b7\3\2\2\2\u02b7\u02b9\3\2\2\2\u02b8\u02b6\3")
        buf.write("\2\2\2\u02b9\u02ba\7$\2\2\u02ba\u008a\3\2\2\2\u02bb\u02bd")
        buf.write("\t\21\2\2\u02bc\u02bb\3\2\2\2\u02bd\u02be\3\2\2\2\u02be")
        buf.write("\u02bc\3\2\2\2\u02be\u02bf\3\2\2\2\u02bf\u02c0\3\2\2\2")
        buf.write("\u02c0\u02c1\bF\2\2\u02c1\u008c\3\2\2\2\u02c2\u02c3\7")
        buf.write("\61\2\2\u02c3\u02c4\7,\2\2\u02c4\u02c8\3\2\2\2\u02c5\u02c7")
        buf.write("\13\2\2\2\u02c6\u02c5\3\2\2\2\u02c7\u02ca\3\2\2\2\u02c8")
        buf.write("\u02c9\3\2\2\2\u02c8\u02c6\3\2\2\2\u02c9\u02cb\3\2\2\2")
        buf.write("\u02ca\u02c8\3\2\2\2\u02cb\u02cc\7,\2\2\u02cc\u02cd\7")
        buf.write("\61\2\2\u02cd\u02ce\3\2\2\2\u02ce\u02cf\bG\2\2\u02cf\u008e")
        buf.write("\3\2\2\2\u02d0\u02d1\7\61\2\2\u02d1\u02d2\7\61\2\2\u02d2")
        buf.write("\u02d6\3\2\2\2\u02d3\u02d5\n\22\2\2\u02d4\u02d3\3\2\2")
        buf.write("\2\u02d5\u02d8\3\2\2\2\u02d6\u02d4\3\2\2\2\u02d6\u02d7")
        buf.write("\3\2\2\2\u02d7\u02d9\3\2\2\2\u02d8\u02d6\3\2\2\2\u02d9")
        buf.write("\u02da\bH\2\2\u02da\u0090\3\2\2\2\u02db\u02df\5\u009f")
        buf.write("P\2\u02dc\u02de\5\u009fP\2\u02dd\u02dc\3\2\2\2\u02de\u02e1")
        buf.write("\3\2\2\2\u02df\u02dd\3\2\2\2\u02df\u02e0\3\2\2\2\u02e0")
        buf.write("\u0092\3\2\2\2\u02e1\u02df\3\2\2\2\u02e2\u02e3\5u;\2\u02e3")
        buf.write("\u02e4\5\u00a3R\2\u02e4\u0094\3\2\2\2\u02e5\u02e7\t\23")
        buf.write("\2\2\u02e6\u02e8\t\16\2\2\u02e7\u02e6\3\2\2\2\u02e7\u02e8")
        buf.write("\3\2\2\2\u02e8\u02e9\3\2\2\2\u02e9\u02ea\5\u009dO\2\u02ea")
        buf.write("\u0096\3\2\2\2\u02eb\u02ec\7^\2\2\u02ec\u0301\t\24\2\2")
        buf.write("\u02ed\u02f2\7^\2\2\u02ee\u02f0\t\25\2\2\u02ef\u02ee\3")
        buf.write("\2\2\2\u02ef\u02f0\3\2\2\2\u02f0\u02f1\3\2\2\2\u02f1\u02f3")
        buf.write("\t\7\2\2\u02f2\u02ef\3\2\2\2\u02f2\u02f3\3\2\2\2\u02f3")
        buf.write("\u02f4\3\2\2\2\u02f4\u0301\t\7\2\2\u02f5\u02f7\7^\2\2")
        buf.write("\u02f6\u02f8\7w\2\2\u02f7\u02f6\3\2\2\2\u02f8\u02f9\3")
        buf.write("\2\2\2\u02f9\u02f7\3\2\2\2\u02f9\u02fa\3\2\2\2\u02fa\u02fb")
        buf.write("\3\2\2\2\u02fb\u02fc\5\u009bN\2\u02fc\u02fd\5\u009bN\2")
        buf.write("\u02fd\u02fe\5\u009bN\2\u02fe\u02ff\5\u009bN\2\u02ff\u0301")
        buf.write("\3\2\2\2\u0300\u02eb\3\2\2\2\u0300\u02ed\3\2\2\2\u0300")
        buf.write("\u02f5\3\2\2\2\u0301\u0098\3\2\2\2\u0302\u030b\5\u009b")
        buf.write("N\2\u0303\u0306\5\u009bN\2\u0304\u0306\7a\2\2\u0305\u0303")
        buf.write("\3\2\2\2\u0305\u0304\3\2\2\2\u0306\u0309\3\2\2\2\u0307")
        buf.write("\u0305\3\2\2\2\u0307\u0308\3\2\2\2\u0308\u030a\3\2\2\2")
        buf.write("\u0309\u0307\3\2\2\2\u030a\u030c\5\u009bN\2\u030b\u0307")
        buf.write("\3\2\2\2\u030b\u030c\3\2\2\2\u030c\u009a\3\2\2\2\u030d")
        buf.write("\u030e\t\5\2\2\u030e\u009c\3\2\2\2\u030f\u0317\t\26\2")
        buf.write("\2\u0310\u0312\t\27\2\2\u0311\u0310\3\2\2\2\u0312\u0315")
        buf.write("\3\2\2\2\u0313\u0311\3\2\2\2\u0313\u0314\3\2\2\2\u0314")
        buf.write("\u0316\3\2\2\2\u0315\u0313\3\2\2\2\u0316\u0318\t\26\2")
        buf.write("\2\u0317\u0313\3\2\2\2\u0317\u0318\3\2\2\2\u0318\u009e")
        buf.write("\3\2\2\2\u0319\u031c\5\u00a1Q\2\u031a\u031c\t\26\2\2\u031b")
        buf.write("\u0319\3\2\2\2\u031b\u031a\3\2\2\2\u031c\u00a0\3\2\2\2")
        buf.write("\u031d\u031e\t\30\2\2\u031e\u00a2\3\2\2\2\u031f\u0320")
        buf.write("\t\31\2\2\u0320\u00a4\3\2\2\2:\2\u01a2\u01aa\u01b0\u01b8")
        buf.write("\u01cb\u01d5\u01e5\u020f\u0214\u0217\u0219\u021c\u0224")
        buf.write("\u0228\u022b\u0231\u0238\u023c\u023f\u0247\u024b\u024e")
        buf.write("\u0253\u0257\u025a\u025d\u0262\u0265\u0267\u026d\u0270")
        buf.write("\u0274\u0278\u027c\u0290\u02a2\u02a8\u02ad\u02b4\u02b6")
        buf.write("\u02be\u02c8\u02d6\u02df\u02e7\u02ef\u02f2\u02f9\u0300")
        buf.write("\u0305\u0307\u030b\u0313\u0317\u031b\3\2\3\2")
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
    ENUM_LIST = 20
    LIMIT = 21
    OMOP = 22
    CLARITY_CORE = 23
    OHDSI_HELPERS = 24
    ALL = 25
    PATIENT = 26
    DOCUMENT = 27
    WHERE = 28
    AND = 29
    OR = 30
    NOT = 31
    GT = 32
    LT = 33
    LTE = 34
    GTE = 35
    EQUAL = 36
    IS = 37
    LIKE = 38
    BETWEEN = 39
    NOT_EQUAL = 40
    BANG = 41
    PLUS = 42
    MINUS = 43
    MULT = 44
    DIV = 45
    CARET = 46
    MOD = 47
    SEMI = 48
    COLON = 49
    DOT = 50
    COMMA = 51
    L_PAREN = 52
    R_PAREN = 53
    L_BRACKET = 54
    R_BRACKET = 55
    L_CURLY = 56
    R_CURLY = 57
    DECIMAL = 58
    HEX = 59
    OCT = 60
    BINARY = 61
    FLOAT = 62
    HEX_FLOAT = 63
    BOOL = 64
    NULL = 65
    IN = 66
    CHAR = 67
    STRING = 68
    WS = 69
    COMMENT = 70
    LINE_COMMENT = 71
    IDENTIFIER = 72
    TIME = 73

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'debug'", "'default'", "'final'", "'phenotype'", "'version'", 
            "'description'", "'datamodel'", "'include'", "'called'", "'codesystem'", 
            "'valueset'", "'termset'", "'documentset'", "'cohort'", "'population'", 
            "'define'", "'context'", "'minimum_value'", "'maximum_value'", 
            "'enum_list'", "'limit'", "'OMOP'", "'ClarityCore'", "'OHDSIHelpers'", 
            "'All'", "'Patient'", "'Document'", "'>'", "'<'", "'<='", "'>='", 
            "'=='", "'!='", "'!'", "'+'", "'-'", "'*'", "'/'", "'^'", "'%'", 
            "';'", "':'", "'.'", "','", "'('", "')'", "'['", "']'", "'{'", 
            "'}'" ]

    symbolicNames = [ "<INVALID>",
            "DEBUG", "DEFAULT", "FINAL", "PHENOTYPE_NAME", "VERSION", "DESCRIPTION", 
            "DATAMODEL", "INCLUDE", "CALLED", "CODE_SYSTEM", "VALUE_SET", 
            "TERM_SET", "DOCUMENT_SET", "COHORT", "POPULATION", "DEFINE", 
            "CONTEXT", "MIN_VALUE", "MAX_VALUE", "ENUM_LIST", "LIMIT", "OMOP", 
            "CLARITY_CORE", "OHDSI_HELPERS", "ALL", "PATIENT", "DOCUMENT", 
            "WHERE", "AND", "OR", "NOT", "GT", "LT", "LTE", "GTE", "EQUAL", 
            "IS", "LIKE", "BETWEEN", "NOT_EQUAL", "BANG", "PLUS", "MINUS", 
            "MULT", "DIV", "CARET", "MOD", "SEMI", "COLON", "DOT", "COMMA", 
            "L_PAREN", "R_PAREN", "L_BRACKET", "R_BRACKET", "L_CURLY", "R_CURLY", 
            "DECIMAL", "HEX", "OCT", "BINARY", "FLOAT", "HEX_FLOAT", "BOOL", 
            "NULL", "IN", "CHAR", "STRING", "WS", "COMMENT", "LINE_COMMENT", 
            "IDENTIFIER", "TIME" ]

    ruleNames = [ "DEBUG", "DEFAULT", "FINAL", "PHENOTYPE_NAME", "VERSION", 
                  "DESCRIPTION", "DATAMODEL", "INCLUDE", "CALLED", "CODE_SYSTEM", 
                  "VALUE_SET", "TERM_SET", "DOCUMENT_SET", "COHORT", "POPULATION", 
                  "DEFINE", "CONTEXT", "MIN_VALUE", "MAX_VALUE", "ENUM_LIST", 
                  "LIMIT", "OMOP", "CLARITY_CORE", "OHDSI_HELPERS", "ALL", 
                  "PATIENT", "DOCUMENT", "WHERE", "AND", "OR", "NOT", "GT", 
                  "LT", "LTE", "GTE", "EQUAL", "IS", "LIKE", "BETWEEN", 
                  "NOT_EQUAL", "BANG", "PLUS", "MINUS", "MULT", "DIV", "CARET", 
                  "MOD", "SEMI", "COLON", "DOT", "COMMA", "L_PAREN", "R_PAREN", 
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


