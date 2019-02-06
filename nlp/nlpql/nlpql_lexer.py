# Generated from nlpql_lexer.g4 by ANTLR 4.7.1
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2L")
        buf.write("\u0328\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
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
        buf.write("L\4M\tM\4N\tN\4O\tO\4P\tP\4Q\tQ\4R\tR\4S\tS\3\2\3\2\3")
        buf.write("\2\3\2\3\2\3\2\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\4\3\4")
        buf.write("\3\4\3\4\3\4\3\4\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3")
        buf.write("\5\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\7\3\7\3\7\3\7\3\7")
        buf.write("\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\b\3\b\3\b\3\b\3\b\3\b\3")
        buf.write("\b\3\b\3\b\3\b\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\n\3\n")
        buf.write("\3\n\3\n\3\n\3\n\3\n\3\13\3\13\3\13\3\13\3\13\3\f\3\f")
        buf.write("\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3\r\3\r\3\r\3\r\3")
        buf.write("\r\3\r\3\r\3\r\3\r\3\16\3\16\3\16\3\16\3\16\3\16\3\16")
        buf.write("\3\16\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17\3\17")
        buf.write("\3\17\3\17\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\21\3\21")
        buf.write("\3\21\3\21\3\21\3\21\3\21\3\21\3\21\3\21\3\21\3\22\3\22")
        buf.write("\3\22\3\22\3\22\3\22\3\22\3\23\3\23\3\23\3\23\3\23\3\23")
        buf.write("\3\23\3\23\3\24\3\24\3\24\3\24\3\24\3\24\3\24\3\24\3\24")
        buf.write("\3\24\3\24\3\24\3\24\3\24\3\25\3\25\3\25\3\25\3\25\3\25")
        buf.write("\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\26\3\26\3\26")
        buf.write("\3\26\3\26\3\26\3\26\3\26\3\26\3\26\3\27\3\27\3\27\3\27")
        buf.write("\3\27\3\27\3\30\3\30\3\30\3\30\3\30\3\31\3\31\3\31\3\31")
        buf.write("\3\31\3\31\3\31\3\31\3\31\3\31\3\31\3\31\3\32\3\32\3\32")
        buf.write("\3\32\3\32\3\32\3\32\3\32\3\32\3\32\3\32\3\32\3\32\3\33")
        buf.write("\3\33\3\33\3\33\3\34\3\34\3\34\3\34\3\34\3\34\3\34\3\34")
        buf.write("\3\35\3\35\3\35\3\35\3\35\3\35\3\35\3\35\3\35\3\36\3\36")
        buf.write("\3\36\3\36\3\36\3\36\3\36\3\36\3\36\3\36\5\36\u01aa\n")
        buf.write("\36\3\37\3\37\3\37\3\37\3\37\3\37\5\37\u01b2\n\37\3 \3")
        buf.write(" \3 \3 \5 \u01b8\n \3!\3!\3!\3!\3!\3!\5!\u01c0\n!\3\"")
        buf.write("\3\"\3#\3#\3$\3$\3$\3%\3%\3%\3&\3&\3&\3\'\3\'\3\'\3\'")
        buf.write("\5\'\u01d3\n\'\3(\3(\3(\3(\3(\3(\3(\3(\5(\u01dd\n(\3)")
        buf.write("\3)\3)\3)\3)\3)\3)\3)\3)\3)\3)\3)\3)\3)\5)\u01ed\n)\3")
        buf.write("*\3*\3*\3+\3+\3,\3,\3-\3-\3.\3.\3/\3/\3\60\3\60\3\61\3")
        buf.write("\61\3\62\3\62\3\63\3\63\3\64\3\64\3\65\3\65\3\66\3\66")
        buf.write("\3\67\3\67\38\38\39\39\3:\3:\3;\3;\3<\3<\3<\5<\u0217\n")
        buf.write("<\3<\6<\u021a\n<\r<\16<\u021b\3<\5<\u021f\n<\5<\u0221")
        buf.write("\n<\3<\5<\u0224\n<\3=\3=\3=\3=\7=\u022a\n=\f=\16=\u022d")
        buf.write("\13=\3=\5=\u0230\n=\3=\5=\u0233\n=\3>\3>\7>\u0237\n>\f")
        buf.write(">\16>\u023a\13>\3>\3>\7>\u023e\n>\f>\16>\u0241\13>\3>")
        buf.write("\5>\u0244\n>\3>\5>\u0247\n>\3?\3?\3?\3?\7?\u024d\n?\f")
        buf.write("?\16?\u0250\13?\3?\5?\u0253\n?\3?\5?\u0256\n?\3@\3@\3")
        buf.write("@\5@\u025b\n@\3@\3@\5@\u025f\n@\3@\5@\u0262\n@\3@\5@\u0265")
        buf.write("\n@\3@\3@\3@\5@\u026a\n@\3@\5@\u026d\n@\5@\u026f\n@\3")
        buf.write("A\3A\3A\3A\5A\u0275\nA\3A\5A\u0278\nA\3A\3A\5A\u027c\n")
        buf.write("A\3A\3A\5A\u0280\nA\3A\3A\5A\u0284\nA\3B\3B\3B\3B\3B\3")
        buf.write("B\3B\3B\3B\3B\3B\3B\3B\3B\3B\3B\3B\3B\5B\u0298\nB\3C\3")
        buf.write("C\3C\3C\3C\3C\3C\3C\3C\3C\3C\3C\3C\3C\3C\3C\5C\u02aa\n")
        buf.write("C\3D\3D\3D\3D\5D\u02b0\nD\3E\3E\3E\5E\u02b5\nE\3E\3E\3")
        buf.write("F\3F\3F\7F\u02bc\nF\fF\16F\u02bf\13F\3F\3F\3G\6G\u02c4")
        buf.write("\nG\rG\16G\u02c5\3G\3G\3H\3H\3H\3H\7H\u02ce\nH\fH\16H")
        buf.write("\u02d1\13H\3H\3H\3H\3H\3H\3I\3I\3I\3I\7I\u02dc\nI\fI\16")
        buf.write("I\u02df\13I\3I\3I\3J\3J\7J\u02e5\nJ\fJ\16J\u02e8\13J\3")
        buf.write("K\3K\3K\3L\3L\5L\u02ef\nL\3L\3L\3M\3M\3M\3M\5M\u02f7\n")
        buf.write("M\3M\5M\u02fa\nM\3M\3M\3M\6M\u02ff\nM\rM\16M\u0300\3M")
        buf.write("\3M\3M\3M\3M\5M\u0308\nM\3N\3N\3N\7N\u030d\nN\fN\16N\u0310")
        buf.write("\13N\3N\5N\u0313\nN\3O\3O\3P\3P\7P\u0319\nP\fP\16P\u031c")
        buf.write("\13P\3P\5P\u031f\nP\3Q\3Q\5Q\u0323\nQ\3R\3R\3S\3S\3\u02cf")
        buf.write("\2T\3\3\5\4\7\5\t\6\13\7\r\b\17\t\21\n\23\13\25\f\27\r")
        buf.write("\31\16\33\17\35\20\37\21!\22#\23%\24\'\25)\26+\27-\30")
        buf.write("/\31\61\32\63\33\65\34\67\359\36;\37= ?!A\"C#E$G%I&K\'")
        buf.write("M(O)Q*S+U,W-Y.[/]\60_\61a\62c\63e\64g\65i\66k\67m8o9q")
        buf.write(":s;u<w=y>{?}@\177A\u0081B\u0083C\u0085D\u0087E\u0089F")
        buf.write("\u008bG\u008dH\u008fI\u0091J\u0093K\u0095L\u0097\2\u0099")
        buf.write("\2\u009b\2\u009d\2\u009f\2\u00a1\2\u00a3\2\u00a5\2\3\2")
        buf.write("\32\3\2\63;\4\2NNnn\4\2ZZzz\5\2\62;CHch\6\2\62;CHaach")
        buf.write("\3\2\629\4\2\629aa\4\2DDdd\3\2\62\63\4\2\62\63aa\6\2F")
        buf.write("FHHffhh\4\2RRrr\4\2--//\6\2\f\f\17\17))^^\6\2\f\f\17\17")
        buf.write("$$^^\5\2\13\f\16\17\"\"\4\2\f\f\17\17\4\2GGgg\n\2$$))")
        buf.write("^^ddhhppttvv\3\2\62\65\3\2\62;\4\2\62;aa\6\2&&C\\aac|")
        buf.write("\6\2FFJJOO[[\2\u035b\2\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2")
        buf.write("\2\2\t\3\2\2\2\2\13\3\2\2\2\2\r\3\2\2\2\2\17\3\2\2\2\2")
        buf.write("\21\3\2\2\2\2\23\3\2\2\2\2\25\3\2\2\2\2\27\3\2\2\2\2\31")
        buf.write("\3\2\2\2\2\33\3\2\2\2\2\35\3\2\2\2\2\37\3\2\2\2\2!\3\2")
        buf.write("\2\2\2#\3\2\2\2\2%\3\2\2\2\2\'\3\2\2\2\2)\3\2\2\2\2+\3")
        buf.write("\2\2\2\2-\3\2\2\2\2/\3\2\2\2\2\61\3\2\2\2\2\63\3\2\2\2")
        buf.write("\2\65\3\2\2\2\2\67\3\2\2\2\29\3\2\2\2\2;\3\2\2\2\2=\3")
        buf.write("\2\2\2\2?\3\2\2\2\2A\3\2\2\2\2C\3\2\2\2\2E\3\2\2\2\2G")
        buf.write("\3\2\2\2\2I\3\2\2\2\2K\3\2\2\2\2M\3\2\2\2\2O\3\2\2\2\2")
        buf.write("Q\3\2\2\2\2S\3\2\2\2\2U\3\2\2\2\2W\3\2\2\2\2Y\3\2\2\2")
        buf.write("\2[\3\2\2\2\2]\3\2\2\2\2_\3\2\2\2\2a\3\2\2\2\2c\3\2\2")
        buf.write("\2\2e\3\2\2\2\2g\3\2\2\2\2i\3\2\2\2\2k\3\2\2\2\2m\3\2")
        buf.write("\2\2\2o\3\2\2\2\2q\3\2\2\2\2s\3\2\2\2\2u\3\2\2\2\2w\3")
        buf.write("\2\2\2\2y\3\2\2\2\2{\3\2\2\2\2}\3\2\2\2\2\177\3\2\2\2")
        buf.write("\2\u0081\3\2\2\2\2\u0083\3\2\2\2\2\u0085\3\2\2\2\2\u0087")
        buf.write("\3\2\2\2\2\u0089\3\2\2\2\2\u008b\3\2\2\2\2\u008d\3\2\2")
        buf.write("\2\2\u008f\3\2\2\2\2\u0091\3\2\2\2\2\u0093\3\2\2\2\2\u0095")
        buf.write("\3\2\2\2\3\u00a7\3\2\2\2\5\u00ad\3\2\2\2\7\u00b5\3\2\2")
        buf.write("\2\t\u00bb\3\2\2\2\13\u00c5\3\2\2\2\r\u00cd\3\2\2\2\17")
        buf.write("\u00d9\3\2\2\2\21\u00e3\3\2\2\2\23\u00eb\3\2\2\2\25\u00f2")
        buf.write("\3\2\2\2\27\u00f7\3\2\2\2\31\u0102\3\2\2\2\33\u010b\3")
        buf.write("\2\2\2\35\u0113\3\2\2\2\37\u011f\3\2\2\2!\u0126\3\2\2")
        buf.write("\2#\u0131\3\2\2\2%\u0138\3\2\2\2\'\u0140\3\2\2\2)\u014e")
        buf.write("\3\2\2\2+\u015c\3\2\2\2-\u0166\3\2\2\2/\u016c\3\2\2\2")
        buf.write("\61\u0171\3\2\2\2\63\u017d\3\2\2\2\65\u018a\3\2\2\2\67")
        buf.write("\u018e\3\2\2\29\u0196\3\2\2\2;\u01a9\3\2\2\2=\u01b1\3")
        buf.write("\2\2\2?\u01b7\3\2\2\2A\u01bf\3\2\2\2C\u01c1\3\2\2\2E\u01c3")
        buf.write("\3\2\2\2G\u01c5\3\2\2\2I\u01c8\3\2\2\2K\u01cb\3\2\2\2")
        buf.write("M\u01d2\3\2\2\2O\u01dc\3\2\2\2Q\u01ec\3\2\2\2S\u01ee\3")
        buf.write("\2\2\2U\u01f1\3\2\2\2W\u01f3\3\2\2\2Y\u01f5\3\2\2\2[\u01f7")
        buf.write("\3\2\2\2]\u01f9\3\2\2\2_\u01fb\3\2\2\2a\u01fd\3\2\2\2")
        buf.write("c\u01ff\3\2\2\2e\u0201\3\2\2\2g\u0203\3\2\2\2i\u0205\3")
        buf.write("\2\2\2k\u0207\3\2\2\2m\u0209\3\2\2\2o\u020b\3\2\2\2q\u020d")
        buf.write("\3\2\2\2s\u020f\3\2\2\2u\u0211\3\2\2\2w\u0220\3\2\2\2")
        buf.write("y\u0225\3\2\2\2{\u0234\3\2\2\2}\u0248\3\2\2\2\177\u026e")
        buf.write("\3\2\2\2\u0081\u0270\3\2\2\2\u0083\u0297\3\2\2\2\u0085")
        buf.write("\u02a9\3\2\2\2\u0087\u02af\3\2\2\2\u0089\u02b1\3\2\2\2")
        buf.write("\u008b\u02b8\3\2\2\2\u008d\u02c3\3\2\2\2\u008f\u02c9\3")
        buf.write("\2\2\2\u0091\u02d7\3\2\2\2\u0093\u02e2\3\2\2\2\u0095\u02e9")
        buf.write("\3\2\2\2\u0097\u02ec\3\2\2\2\u0099\u0307\3\2\2\2\u009b")
        buf.write("\u0309\3\2\2\2\u009d\u0314\3\2\2\2\u009f\u0316\3\2\2\2")
        buf.write("\u00a1\u0322\3\2\2\2\u00a3\u0324\3\2\2\2\u00a5\u0326\3")
        buf.write("\2\2\2\u00a7\u00a8\7f\2\2\u00a8\u00a9\7g\2\2\u00a9\u00aa")
        buf.write("\7d\2\2\u00aa\u00ab\7w\2\2\u00ab\u00ac\7i\2\2\u00ac\4")
        buf.write("\3\2\2\2\u00ad\u00ae\7f\2\2\u00ae\u00af\7g\2\2\u00af\u00b0")
        buf.write("\7h\2\2\u00b0\u00b1\7c\2\2\u00b1\u00b2\7w\2\2\u00b2\u00b3")
        buf.write("\7n\2\2\u00b3\u00b4\7v\2\2\u00b4\6\3\2\2\2\u00b5\u00b6")
        buf.write("\7h\2\2\u00b6\u00b7\7k\2\2\u00b7\u00b8\7p\2\2\u00b8\u00b9")
        buf.write("\7c\2\2\u00b9\u00ba\7n\2\2\u00ba\b\3\2\2\2\u00bb\u00bc")
        buf.write("\7r\2\2\u00bc\u00bd\7j\2\2\u00bd\u00be\7g\2\2\u00be\u00bf")
        buf.write("\7p\2\2\u00bf\u00c0\7q\2\2\u00c0\u00c1\7v\2\2\u00c1\u00c2")
        buf.write("\7{\2\2\u00c2\u00c3\7r\2\2\u00c3\u00c4\7g\2\2\u00c4\n")
        buf.write("\3\2\2\2\u00c5\u00c6\7x\2\2\u00c6\u00c7\7g\2\2\u00c7\u00c8")
        buf.write("\7t\2\2\u00c8\u00c9\7u\2\2\u00c9\u00ca\7k\2\2\u00ca\u00cb")
        buf.write("\7q\2\2\u00cb\u00cc\7p\2\2\u00cc\f\3\2\2\2\u00cd\u00ce")
        buf.write("\7f\2\2\u00ce\u00cf\7g\2\2\u00cf\u00d0\7u\2\2\u00d0\u00d1")
        buf.write("\7e\2\2\u00d1\u00d2\7t\2\2\u00d2\u00d3\7k\2\2\u00d3\u00d4")
        buf.write("\7r\2\2\u00d4\u00d5\7v\2\2\u00d5\u00d6\7k\2\2\u00d6\u00d7")
        buf.write("\7q\2\2\u00d7\u00d8\7p\2\2\u00d8\16\3\2\2\2\u00d9\u00da")
        buf.write("\7f\2\2\u00da\u00db\7c\2\2\u00db\u00dc\7v\2\2\u00dc\u00dd")
        buf.write("\7c\2\2\u00dd\u00de\7o\2\2\u00de\u00df\7q\2\2\u00df\u00e0")
        buf.write("\7f\2\2\u00e0\u00e1\7g\2\2\u00e1\u00e2\7n\2\2\u00e2\20")
        buf.write("\3\2\2\2\u00e3\u00e4\7k\2\2\u00e4\u00e5\7p\2\2\u00e5\u00e6")
        buf.write("\7e\2\2\u00e6\u00e7\7n\2\2\u00e7\u00e8\7w\2\2\u00e8\u00e9")
        buf.write("\7f\2\2\u00e9\u00ea\7g\2\2\u00ea\22\3\2\2\2\u00eb\u00ec")
        buf.write("\7e\2\2\u00ec\u00ed\7c\2\2\u00ed\u00ee\7n\2\2\u00ee\u00ef")
        buf.write("\7n\2\2\u00ef\u00f0\7g\2\2\u00f0\u00f1\7f\2\2\u00f1\24")
        buf.write("\3\2\2\2\u00f2\u00f3\7e\2\2\u00f3\u00f4\7q\2\2\u00f4\u00f5")
        buf.write("\7f\2\2\u00f5\u00f6\7g\2\2\u00f6\26\3\2\2\2\u00f7\u00f8")
        buf.write("\7e\2\2\u00f8\u00f9\7q\2\2\u00f9\u00fa\7f\2\2\u00fa\u00fb")
        buf.write("\7g\2\2\u00fb\u00fc\7u\2\2\u00fc\u00fd\7{\2\2\u00fd\u00fe")
        buf.write("\7u\2\2\u00fe\u00ff\7v\2\2\u00ff\u0100\7g\2\2\u0100\u0101")
        buf.write("\7o\2\2\u0101\30\3\2\2\2\u0102\u0103\7x\2\2\u0103\u0104")
        buf.write("\7c\2\2\u0104\u0105\7n\2\2\u0105\u0106\7w\2\2\u0106\u0107")
        buf.write("\7g\2\2\u0107\u0108\7u\2\2\u0108\u0109\7g\2\2\u0109\u010a")
        buf.write("\7v\2\2\u010a\32\3\2\2\2\u010b\u010c\7v\2\2\u010c\u010d")
        buf.write("\7g\2\2\u010d\u010e\7t\2\2\u010e\u010f\7o\2\2\u010f\u0110")
        buf.write("\7u\2\2\u0110\u0111\7g\2\2\u0111\u0112\7v\2\2\u0112\34")
        buf.write("\3\2\2\2\u0113\u0114\7f\2\2\u0114\u0115\7q\2\2\u0115\u0116")
        buf.write("\7e\2\2\u0116\u0117\7w\2\2\u0117\u0118\7o\2\2\u0118\u0119")
        buf.write("\7g\2\2\u0119\u011a\7p\2\2\u011a\u011b\7v\2\2\u011b\u011c")
        buf.write("\7u\2\2\u011c\u011d\7g\2\2\u011d\u011e\7v\2\2\u011e\36")
        buf.write("\3\2\2\2\u011f\u0120\7e\2\2\u0120\u0121\7q\2\2\u0121\u0122")
        buf.write("\7j\2\2\u0122\u0123\7q\2\2\u0123\u0124\7t\2\2\u0124\u0125")
        buf.write("\7v\2\2\u0125 \3\2\2\2\u0126\u0127\7r\2\2\u0127\u0128")
        buf.write("\7q\2\2\u0128\u0129\7r\2\2\u0129\u012a\7w\2\2\u012a\u012b")
        buf.write("\7n\2\2\u012b\u012c\7c\2\2\u012c\u012d\7v\2\2\u012d\u012e")
        buf.write("\7k\2\2\u012e\u012f\7q\2\2\u012f\u0130\7p\2\2\u0130\"")
        buf.write("\3\2\2\2\u0131\u0132\7f\2\2\u0132\u0133\7g\2\2\u0133\u0134")
        buf.write("\7h\2\2\u0134\u0135\7k\2\2\u0135\u0136\7p\2\2\u0136\u0137")
        buf.write("\7g\2\2\u0137$\3\2\2\2\u0138\u0139\7e\2\2\u0139\u013a")
        buf.write("\7q\2\2\u013a\u013b\7p\2\2\u013b\u013c\7v\2\2\u013c\u013d")
        buf.write("\7g\2\2\u013d\u013e\7z\2\2\u013e\u013f\7v\2\2\u013f&\3")
        buf.write("\2\2\2\u0140\u0141\7o\2\2\u0141\u0142\7k\2\2\u0142\u0143")
        buf.write("\7p\2\2\u0143\u0144\7k\2\2\u0144\u0145\7o\2\2\u0145\u0146")
        buf.write("\7w\2\2\u0146\u0147\7o\2\2\u0147\u0148\7a\2\2\u0148\u0149")
        buf.write("\7x\2\2\u0149\u014a\7c\2\2\u014a\u014b\7n\2\2\u014b\u014c")
        buf.write("\7w\2\2\u014c\u014d\7g\2\2\u014d(\3\2\2\2\u014e\u014f")
        buf.write("\7o\2\2\u014f\u0150\7c\2\2\u0150\u0151\7z\2\2\u0151\u0152")
        buf.write("\7k\2\2\u0152\u0153\7o\2\2\u0153\u0154\7w\2\2\u0154\u0155")
        buf.write("\7o\2\2\u0155\u0156\7a\2\2\u0156\u0157\7x\2\2\u0157\u0158")
        buf.write("\7c\2\2\u0158\u0159\7n\2\2\u0159\u015a\7w\2\2\u015a\u015b")
        buf.write("\7g\2\2\u015b*\3\2\2\2\u015c\u015d\7g\2\2\u015d\u015e")
        buf.write("\7p\2\2\u015e\u015f\7w\2\2\u015f\u0160\7o\2\2\u0160\u0161")
        buf.write("\7a\2\2\u0161\u0162\7n\2\2\u0162\u0163\7k\2\2\u0163\u0164")
        buf.write("\7u\2\2\u0164\u0165\7v\2\2\u0165,\3\2\2\2\u0166\u0167")
        buf.write("\7n\2\2\u0167\u0168\7k\2\2\u0168\u0169\7o\2\2\u0169\u016a")
        buf.write("\7k\2\2\u016a\u016b\7v\2\2\u016b.\3\2\2\2\u016c\u016d")
        buf.write("\7Q\2\2\u016d\u016e\7O\2\2\u016e\u016f\7Q\2\2\u016f\u0170")
        buf.write("\7R\2\2\u0170\60\3\2\2\2\u0171\u0172\7E\2\2\u0172\u0173")
        buf.write("\7n\2\2\u0173\u0174\7c\2\2\u0174\u0175\7t\2\2\u0175\u0176")
        buf.write("\7k\2\2\u0176\u0177\7v\2\2\u0177\u0178\7{\2\2\u0178\u0179")
        buf.write("\7E\2\2\u0179\u017a\7q\2\2\u017a\u017b\7t\2\2\u017b\u017c")
        buf.write("\7g\2\2\u017c\62\3\2\2\2\u017d\u017e\7Q\2\2\u017e\u017f")
        buf.write("\7J\2\2\u017f\u0180\7F\2\2\u0180\u0181\7U\2\2\u0181\u0182")
        buf.write("\7K\2\2\u0182\u0183\7J\2\2\u0183\u0184\7g\2\2\u0184\u0185")
        buf.write("\7n\2\2\u0185\u0186\7r\2\2\u0186\u0187\7g\2\2\u0187\u0188")
        buf.write("\7t\2\2\u0188\u0189\7u\2\2\u0189\64\3\2\2\2\u018a\u018b")
        buf.write("\7C\2\2\u018b\u018c\7n\2\2\u018c\u018d\7n\2\2\u018d\66")
        buf.write("\3\2\2\2\u018e\u018f\7R\2\2\u018f\u0190\7c\2\2\u0190\u0191")
        buf.write("\7v\2\2\u0191\u0192\7k\2\2\u0192\u0193\7g\2\2\u0193\u0194")
        buf.write("\7p\2\2\u0194\u0195\7v\2\2\u01958\3\2\2\2\u0196\u0197")
        buf.write("\7F\2\2\u0197\u0198\7q\2\2\u0198\u0199\7e\2\2\u0199\u019a")
        buf.write("\7w\2\2\u019a\u019b\7o\2\2\u019b\u019c\7g\2\2\u019c\u019d")
        buf.write("\7p\2\2\u019d\u019e\7v\2\2\u019e:\3\2\2\2\u019f\u01a0")
        buf.write("\7Y\2\2\u01a0\u01a1\7J\2\2\u01a1\u01a2\7G\2\2\u01a2\u01a3")
        buf.write("\7T\2\2\u01a3\u01aa\7G\2\2\u01a4\u01a5\7y\2\2\u01a5\u01a6")
        buf.write("\7j\2\2\u01a6\u01a7\7g\2\2\u01a7\u01a8\7t\2\2\u01a8\u01aa")
        buf.write("\7g\2\2\u01a9\u019f\3\2\2\2\u01a9\u01a4\3\2\2\2\u01aa")
        buf.write("<\3\2\2\2\u01ab\u01ac\7C\2\2\u01ac\u01ad\7P\2\2\u01ad")
        buf.write("\u01b2\7F\2\2\u01ae\u01af\7c\2\2\u01af\u01b0\7p\2\2\u01b0")
        buf.write("\u01b2\7f\2\2\u01b1\u01ab\3\2\2\2\u01b1\u01ae\3\2\2\2")
        buf.write("\u01b2>\3\2\2\2\u01b3\u01b4\7Q\2\2\u01b4\u01b8\7T\2\2")
        buf.write("\u01b5\u01b6\7q\2\2\u01b6\u01b8\7t\2\2\u01b7\u01b3\3\2")
        buf.write("\2\2\u01b7\u01b5\3\2\2\2\u01b8@\3\2\2\2\u01b9\u01ba\7")
        buf.write("P\2\2\u01ba\u01bb\7Q\2\2\u01bb\u01c0\7V\2\2\u01bc\u01bd")
        buf.write("\7p\2\2\u01bd\u01be\7q\2\2\u01be\u01c0\7v\2\2\u01bf\u01b9")
        buf.write("\3\2\2\2\u01bf\u01bc\3\2\2\2\u01c0B\3\2\2\2\u01c1\u01c2")
        buf.write("\7@\2\2\u01c2D\3\2\2\2\u01c3\u01c4\7>\2\2\u01c4F\3\2\2")
        buf.write("\2\u01c5\u01c6\7>\2\2\u01c6\u01c7\7?\2\2\u01c7H\3\2\2")
        buf.write("\2\u01c8\u01c9\7@\2\2\u01c9\u01ca\7?\2\2\u01caJ\3\2\2")
        buf.write("\2\u01cb\u01cc\7?\2\2\u01cc\u01cd\7?\2\2\u01cdL\3\2\2")
        buf.write("\2\u01ce\u01cf\7k\2\2\u01cf\u01d3\7u\2\2\u01d0\u01d1\7")
        buf.write("K\2\2\u01d1\u01d3\7U\2\2\u01d2\u01ce\3\2\2\2\u01d2\u01d0")
        buf.write("\3\2\2\2\u01d3N\3\2\2\2\u01d4\u01d5\7n\2\2\u01d5\u01d6")
        buf.write("\7k\2\2\u01d6\u01d7\7m\2\2\u01d7\u01dd\7g\2\2\u01d8\u01d9")
        buf.write("\7N\2\2\u01d9\u01da\7K\2\2\u01da\u01db\7M\2\2\u01db\u01dd")
        buf.write("\7G\2\2\u01dc\u01d4\3\2\2\2\u01dc\u01d8\3\2\2\2\u01dd")
        buf.write("P\3\2\2\2\u01de\u01df\7d\2\2\u01df\u01e0\7g\2\2\u01e0")
        buf.write("\u01e1\7v\2\2\u01e1\u01e2\7y\2\2\u01e2\u01e3\7g\2\2\u01e3")
        buf.write("\u01e4\7g\2\2\u01e4\u01ed\7p\2\2\u01e5\u01e6\7D\2\2\u01e6")
        buf.write("\u01e7\7G\2\2\u01e7\u01e8\7V\2\2\u01e8\u01e9\7Y\2\2\u01e9")
        buf.write("\u01ea\7G\2\2\u01ea\u01eb\7G\2\2\u01eb\u01ed\7P\2\2\u01ec")
        buf.write("\u01de\3\2\2\2\u01ec\u01e5\3\2\2\2\u01edR\3\2\2\2\u01ee")
        buf.write("\u01ef\7#\2\2\u01ef\u01f0\7?\2\2\u01f0T\3\2\2\2\u01f1")
        buf.write("\u01f2\7#\2\2\u01f2V\3\2\2\2\u01f3\u01f4\7-\2\2\u01f4")
        buf.write("X\3\2\2\2\u01f5\u01f6\7/\2\2\u01f6Z\3\2\2\2\u01f7\u01f8")
        buf.write("\7,\2\2\u01f8\\\3\2\2\2\u01f9\u01fa\7\61\2\2\u01fa^\3")
        buf.write("\2\2\2\u01fb\u01fc\7`\2\2\u01fc`\3\2\2\2\u01fd\u01fe\7")
        buf.write("\'\2\2\u01feb\3\2\2\2\u01ff\u0200\7=\2\2\u0200d\3\2\2")
        buf.write("\2\u0201\u0202\7<\2\2\u0202f\3\2\2\2\u0203\u0204\7\60")
        buf.write("\2\2\u0204h\3\2\2\2\u0205\u0206\7.\2\2\u0206j\3\2\2\2")
        buf.write("\u0207\u0208\7*\2\2\u0208l\3\2\2\2\u0209\u020a\7+\2\2")
        buf.write("\u020an\3\2\2\2\u020b\u020c\7]\2\2\u020cp\3\2\2\2\u020d")
        buf.write("\u020e\7_\2\2\u020er\3\2\2\2\u020f\u0210\7}\2\2\u0210")
        buf.write("t\3\2\2\2\u0211\u0212\7\177\2\2\u0212v\3\2\2\2\u0213\u0221")
        buf.write("\7\62\2\2\u0214\u021e\t\2\2\2\u0215\u0217\5\u009fP\2\u0216")
        buf.write("\u0215\3\2\2\2\u0216\u0217\3\2\2\2\u0217\u021f\3\2\2\2")
        buf.write("\u0218\u021a\7a\2\2\u0219\u0218\3\2\2\2\u021a\u021b\3")
        buf.write("\2\2\2\u021b\u0219\3\2\2\2\u021b\u021c\3\2\2\2\u021c\u021d")
        buf.write("\3\2\2\2\u021d\u021f\5\u009fP\2\u021e\u0216\3\2\2\2\u021e")
        buf.write("\u0219\3\2\2\2\u021f\u0221\3\2\2\2\u0220\u0213\3\2\2\2")
        buf.write("\u0220\u0214\3\2\2\2\u0221\u0223\3\2\2\2\u0222\u0224\t")
        buf.write("\3\2\2\u0223\u0222\3\2\2\2\u0223\u0224\3\2\2\2\u0224x")
        buf.write("\3\2\2\2\u0225\u0226\7\62\2\2\u0226\u0227\t\4\2\2\u0227")
        buf.write("\u022f\t\5\2\2\u0228\u022a\t\6\2\2\u0229\u0228\3\2\2\2")
        buf.write("\u022a\u022d\3\2\2\2\u022b\u0229\3\2\2\2\u022b\u022c\3")
        buf.write("\2\2\2\u022c\u022e\3\2\2\2\u022d\u022b\3\2\2\2\u022e\u0230")
        buf.write("\t\5\2\2\u022f\u022b\3\2\2\2\u022f\u0230\3\2\2\2\u0230")
        buf.write("\u0232\3\2\2\2\u0231\u0233\t\3\2\2\u0232\u0231\3\2\2\2")
        buf.write("\u0232\u0233\3\2\2\2\u0233z\3\2\2\2\u0234\u0238\7\62\2")
        buf.write("\2\u0235\u0237\7a\2\2\u0236\u0235\3\2\2\2\u0237\u023a")
        buf.write("\3\2\2\2\u0238\u0236\3\2\2\2\u0238\u0239\3\2\2\2\u0239")
        buf.write("\u023b\3\2\2\2\u023a\u0238\3\2\2\2\u023b\u0243\t\7\2\2")
        buf.write("\u023c\u023e\t\b\2\2\u023d\u023c\3\2\2\2\u023e\u0241\3")
        buf.write("\2\2\2\u023f\u023d\3\2\2\2\u023f\u0240\3\2\2\2\u0240\u0242")
        buf.write("\3\2\2\2\u0241\u023f\3\2\2\2\u0242\u0244\t\7\2\2\u0243")
        buf.write("\u023f\3\2\2\2\u0243\u0244\3\2\2\2\u0244\u0246\3\2\2\2")
        buf.write("\u0245\u0247\t\3\2\2\u0246\u0245\3\2\2\2\u0246\u0247\3")
        buf.write("\2\2\2\u0247|\3\2\2\2\u0248\u0249\7\62\2\2\u0249\u024a")
        buf.write("\t\t\2\2\u024a\u0252\t\n\2\2\u024b\u024d\t\13\2\2\u024c")
        buf.write("\u024b\3\2\2\2\u024d\u0250\3\2\2\2\u024e\u024c\3\2\2\2")
        buf.write("\u024e\u024f\3\2\2\2\u024f\u0251\3\2\2\2\u0250\u024e\3")
        buf.write("\2\2\2\u0251\u0253\t\n\2\2\u0252\u024e\3\2\2\2\u0252\u0253")
        buf.write("\3\2\2\2\u0253\u0255\3\2\2\2\u0254\u0256\t\3\2\2\u0255")
        buf.write("\u0254\3\2\2\2\u0255\u0256\3\2\2\2\u0256~\3\2\2\2\u0257")
        buf.write("\u0258\5\u009fP\2\u0258\u025a\7\60\2\2\u0259\u025b\5\u009f")
        buf.write("P\2\u025a\u0259\3\2\2\2\u025a\u025b\3\2\2\2\u025b\u025f")
        buf.write("\3\2\2\2\u025c\u025d\7\60\2\2\u025d\u025f\5\u009fP\2\u025e")
        buf.write("\u0257\3\2\2\2\u025e\u025c\3\2\2\2\u025f\u0261\3\2\2\2")
        buf.write("\u0260\u0262\5\u0097L\2\u0261\u0260\3\2\2\2\u0261\u0262")
        buf.write("\3\2\2\2\u0262\u0264\3\2\2\2\u0263\u0265\t\f\2\2\u0264")
        buf.write("\u0263\3\2\2\2\u0264\u0265\3\2\2\2\u0265\u026f\3\2\2\2")
        buf.write("\u0266\u026c\5\u009fP\2\u0267\u0269\5\u0097L\2\u0268\u026a")
        buf.write("\t\f\2\2\u0269\u0268\3\2\2\2\u0269\u026a\3\2\2\2\u026a")
        buf.write("\u026d\3\2\2\2\u026b\u026d\t\f\2\2\u026c\u0267\3\2\2\2")
        buf.write("\u026c\u026b\3\2\2\2\u026d\u026f\3\2\2\2\u026e\u025e\3")
        buf.write("\2\2\2\u026e\u0266\3\2\2\2\u026f\u0080\3\2\2\2\u0270\u0271")
        buf.write("\7\62\2\2\u0271\u027b\t\4\2\2\u0272\u0274\5\u009bN\2\u0273")
        buf.write("\u0275\7\60\2\2\u0274\u0273\3\2\2\2\u0274\u0275\3\2\2")
        buf.write("\2\u0275\u027c\3\2\2\2\u0276\u0278\5\u009bN\2\u0277\u0276")
        buf.write("\3\2\2\2\u0277\u0278\3\2\2\2\u0278\u0279\3\2\2\2\u0279")
        buf.write("\u027a\7\60\2\2\u027a\u027c\5\u009bN\2\u027b\u0272\3\2")
        buf.write("\2\2\u027b\u0277\3\2\2\2\u027c\u027d\3\2\2\2\u027d\u027f")
        buf.write("\t\r\2\2\u027e\u0280\t\16\2\2\u027f\u027e\3\2\2\2\u027f")
        buf.write("\u0280\3\2\2\2\u0280\u0281\3\2\2\2\u0281\u0283\5\u009f")
        buf.write("P\2\u0282\u0284\t\f\2\2\u0283\u0282\3\2\2\2\u0283\u0284")
        buf.write("\3\2\2\2\u0284\u0082\3\2\2\2\u0285\u0286\7v\2\2\u0286")
        buf.write("\u0287\7t\2\2\u0287\u0288\7w\2\2\u0288\u0298\7g\2\2\u0289")
        buf.write("\u028a\7V\2\2\u028a\u028b\7T\2\2\u028b\u028c\7W\2\2\u028c")
        buf.write("\u0298\7G\2\2\u028d\u028e\7h\2\2\u028e\u028f\7c\2\2\u028f")
        buf.write("\u0290\7n\2\2\u0290\u0291\7u\2\2\u0291\u0298\7g\2\2\u0292")
        buf.write("\u0293\7H\2\2\u0293\u0294\7C\2\2\u0294\u0295\7N\2\2\u0295")
        buf.write("\u0296\7U\2\2\u0296\u0298\7G\2\2\u0297\u0285\3\2\2\2\u0297")
        buf.write("\u0289\3\2\2\2\u0297\u028d\3\2\2\2\u0297\u0292\3\2\2\2")
        buf.write("\u0298\u0084\3\2\2\2\u0299\u029a\7p\2\2\u029a\u029b\7")
        buf.write("w\2\2\u029b\u029c\7n\2\2\u029c\u02aa\7n\2\2\u029d\u029e")
        buf.write("\7P\2\2\u029e\u029f\7W\2\2\u029f\u02a0\7N\2\2\u02a0\u02aa")
        buf.write("\7N\2\2\u02a1\u02a2\7P\2\2\u02a2\u02a3\7q\2\2\u02a3\u02a4")
        buf.write("\7p\2\2\u02a4\u02aa\7g\2\2\u02a5\u02a6\7p\2\2\u02a6\u02a7")
        buf.write("\7q\2\2\u02a7\u02a8\7p\2\2\u02a8\u02aa\7g\2\2\u02a9\u0299")
        buf.write("\3\2\2\2\u02a9\u029d\3\2\2\2\u02a9\u02a1\3\2\2\2\u02a9")
        buf.write("\u02a5\3\2\2\2\u02aa\u0086\3\2\2\2\u02ab\u02ac\7K\2\2")
        buf.write("\u02ac\u02b0\7P\2\2\u02ad\u02ae\7k\2\2\u02ae\u02b0\7p")
        buf.write("\2\2\u02af\u02ab\3\2\2\2\u02af\u02ad\3\2\2\2\u02b0\u0088")
        buf.write("\3\2\2\2\u02b1\u02b4\7)\2\2\u02b2\u02b5\n\17\2\2\u02b3")
        buf.write("\u02b5\5\u0099M\2\u02b4\u02b2\3\2\2\2\u02b4\u02b3\3\2")
        buf.write("\2\2\u02b5\u02b6\3\2\2\2\u02b6\u02b7\7)\2\2\u02b7\u008a")
        buf.write("\3\2\2\2\u02b8\u02bd\7$\2\2\u02b9\u02bc\n\20\2\2\u02ba")
        buf.write("\u02bc\5\u0099M\2\u02bb\u02b9\3\2\2\2\u02bb\u02ba\3\2")
        buf.write("\2\2\u02bc\u02bf\3\2\2\2\u02bd\u02bb\3\2\2\2\u02bd\u02be")
        buf.write("\3\2\2\2\u02be\u02c0\3\2\2\2\u02bf\u02bd\3\2\2\2\u02c0")
        buf.write("\u02c1\7$\2\2\u02c1\u008c\3\2\2\2\u02c2\u02c4\t\21\2\2")
        buf.write("\u02c3\u02c2\3\2\2\2\u02c4\u02c5\3\2\2\2\u02c5\u02c3\3")
        buf.write("\2\2\2\u02c5\u02c6\3\2\2\2\u02c6\u02c7\3\2\2\2\u02c7\u02c8")
        buf.write("\bG\2\2\u02c8\u008e\3\2\2\2\u02c9\u02ca\7\61\2\2\u02ca")
        buf.write("\u02cb\7,\2\2\u02cb\u02cf\3\2\2\2\u02cc\u02ce\13\2\2\2")
        buf.write("\u02cd\u02cc\3\2\2\2\u02ce\u02d1\3\2\2\2\u02cf\u02d0\3")
        buf.write("\2\2\2\u02cf\u02cd\3\2\2\2\u02d0\u02d2\3\2\2\2\u02d1\u02cf")
        buf.write("\3\2\2\2\u02d2\u02d3\7,\2\2\u02d3\u02d4\7\61\2\2\u02d4")
        buf.write("\u02d5\3\2\2\2\u02d5\u02d6\bH\2\2\u02d6\u0090\3\2\2\2")
        buf.write("\u02d7\u02d8\7\61\2\2\u02d8\u02d9\7\61\2\2\u02d9\u02dd")
        buf.write("\3\2\2\2\u02da\u02dc\n\22\2\2\u02db\u02da\3\2\2\2\u02dc")
        buf.write("\u02df\3\2\2\2\u02dd\u02db\3\2\2\2\u02dd\u02de\3\2\2\2")
        buf.write("\u02de\u02e0\3\2\2\2\u02df\u02dd\3\2\2\2\u02e0\u02e1\b")
        buf.write("I\2\2\u02e1\u0092\3\2\2\2\u02e2\u02e6\5\u00a1Q\2\u02e3")
        buf.write("\u02e5\5\u00a1Q\2\u02e4\u02e3\3\2\2\2\u02e5\u02e8\3\2")
        buf.write("\2\2\u02e6\u02e4\3\2\2\2\u02e6\u02e7\3\2\2\2\u02e7\u0094")
        buf.write("\3\2\2\2\u02e8\u02e6\3\2\2\2\u02e9\u02ea\5w<\2\u02ea\u02eb")
        buf.write("\5\u00a5S\2\u02eb\u0096\3\2\2\2\u02ec\u02ee\t\23\2\2\u02ed")
        buf.write("\u02ef\t\16\2\2\u02ee\u02ed\3\2\2\2\u02ee\u02ef\3\2\2")
        buf.write("\2\u02ef\u02f0\3\2\2\2\u02f0\u02f1\5\u009fP\2\u02f1\u0098")
        buf.write("\3\2\2\2\u02f2\u02f3\7^\2\2\u02f3\u0308\t\24\2\2\u02f4")
        buf.write("\u02f9\7^\2\2\u02f5\u02f7\t\25\2\2\u02f6\u02f5\3\2\2\2")
        buf.write("\u02f6\u02f7\3\2\2\2\u02f7\u02f8\3\2\2\2\u02f8\u02fa\t")
        buf.write("\7\2\2\u02f9\u02f6\3\2\2\2\u02f9\u02fa\3\2\2\2\u02fa\u02fb")
        buf.write("\3\2\2\2\u02fb\u0308\t\7\2\2\u02fc\u02fe\7^\2\2\u02fd")
        buf.write("\u02ff\7w\2\2\u02fe\u02fd\3\2\2\2\u02ff\u0300\3\2\2\2")
        buf.write("\u0300\u02fe\3\2\2\2\u0300\u0301\3\2\2\2\u0301\u0302\3")
        buf.write("\2\2\2\u0302\u0303\5\u009dO\2\u0303\u0304\5\u009dO\2\u0304")
        buf.write("\u0305\5\u009dO\2\u0305\u0306\5\u009dO\2\u0306\u0308\3")
        buf.write("\2\2\2\u0307\u02f2\3\2\2\2\u0307\u02f4\3\2\2\2\u0307\u02fc")
        buf.write("\3\2\2\2\u0308\u009a\3\2\2\2\u0309\u0312\5\u009dO\2\u030a")
        buf.write("\u030d\5\u009dO\2\u030b\u030d\7a\2\2\u030c\u030a\3\2\2")
        buf.write("\2\u030c\u030b\3\2\2\2\u030d\u0310\3\2\2\2\u030e\u030c")
        buf.write("\3\2\2\2\u030e\u030f\3\2\2\2\u030f\u0311\3\2\2\2\u0310")
        buf.write("\u030e\3\2\2\2\u0311\u0313\5\u009dO\2\u0312\u030e\3\2")
        buf.write("\2\2\u0312\u0313\3\2\2\2\u0313\u009c\3\2\2\2\u0314\u0315")
        buf.write("\t\5\2\2\u0315\u009e\3\2\2\2\u0316\u031e\t\26\2\2\u0317")
        buf.write("\u0319\t\27\2\2\u0318\u0317\3\2\2\2\u0319\u031c\3\2\2")
        buf.write("\2\u031a\u0318\3\2\2\2\u031a\u031b\3\2\2\2\u031b\u031d")
        buf.write("\3\2\2\2\u031c\u031a\3\2\2\2\u031d\u031f\t\26\2\2\u031e")
        buf.write("\u031a\3\2\2\2\u031e\u031f\3\2\2\2\u031f\u00a0\3\2\2\2")
        buf.write("\u0320\u0323\5\u00a3R\2\u0321\u0323\t\26\2\2\u0322\u0320")
        buf.write("\3\2\2\2\u0322\u0321\3\2\2\2\u0323\u00a2\3\2\2\2\u0324")
        buf.write("\u0325\t\30\2\2\u0325\u00a4\3\2\2\2\u0326\u0327\t\31\2")
        buf.write("\2\u0327\u00a6\3\2\2\2:\2\u01a9\u01b1\u01b7\u01bf\u01d2")
        buf.write("\u01dc\u01ec\u0216\u021b\u021e\u0220\u0223\u022b\u022f")
        buf.write("\u0232\u0238\u023f\u0243\u0246\u024e\u0252\u0255\u025a")
        buf.write("\u025e\u0261\u0264\u0269\u026c\u026e\u0274\u0277\u027b")
        buf.write("\u027f\u0283\u0297\u02a9\u02af\u02b4\u02bb\u02bd\u02c5")
        buf.write("\u02cf\u02dd\u02e6\u02ee\u02f6\u02f9\u0300\u0307\u030c")
        buf.write("\u030e\u0312\u031a\u031e\u0322\3\2\3\2")
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
    CODE = 10
    CODE_SYSTEM = 11
    VALUE_SET = 12
    TERM_SET = 13
    DOCUMENT_SET = 14
    COHORT = 15
    POPULATION = 16
    DEFINE = 17
    CONTEXT = 18
    MIN_VALUE = 19
    MAX_VALUE = 20
    ENUM_LIST = 21
    LIMIT = 22
    OMOP = 23
    CLARITY_CORE = 24
    OHDSI_HELPERS = 25
    ALL = 26
    PATIENT = 27
    DOCUMENT = 28
    WHERE = 29
    AND = 30
    OR = 31
    NOT = 32
    GT = 33
    LT = 34
    LTE = 35
    GTE = 36
    EQUAL = 37
    IS = 38
    LIKE = 39
    BETWEEN = 40
    NOT_EQUAL = 41
    BANG = 42
    PLUS = 43
    MINUS = 44
    MULT = 45
    DIV = 46
    CARET = 47
    MOD = 48
    SEMI = 49
    COLON = 50
    DOT = 51
    COMMA = 52
    L_PAREN = 53
    R_PAREN = 54
    L_BRACKET = 55
    R_BRACKET = 56
    L_CURLY = 57
    R_CURLY = 58
    DECIMAL = 59
    HEX = 60
    OCT = 61
    BINARY = 62
    FLOAT = 63
    HEX_FLOAT = 64
    BOOL = 65
    NULL = 66
    IN = 67
    CHAR = 68
    STRING = 69
    WS = 70
    COMMENT = 71
    LINE_COMMENT = 72
    IDENTIFIER = 73
    TIME = 74

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'debug'", "'default'", "'final'", "'phenotype'", "'version'", 
            "'description'", "'datamodel'", "'include'", "'called'", "'code'", 
            "'codesystem'", "'valueset'", "'termset'", "'documentset'", 
            "'cohort'", "'population'", "'define'", "'context'", "'minimum_value'", 
            "'maximum_value'", "'enum_list'", "'limit'", "'OMOP'", "'ClarityCore'", 
            "'OHDSIHelpers'", "'All'", "'Patient'", "'Document'", "'>'", 
            "'<'", "'<='", "'>='", "'=='", "'!='", "'!'", "'+'", "'-'", 
            "'*'", "'/'", "'^'", "'%'", "';'", "':'", "'.'", "','", "'('", 
            "')'", "'['", "']'", "'{'", "'}'" ]

    symbolicNames = [ "<INVALID>",
            "DEBUG", "DEFAULT", "FINAL", "PHENOTYPE_NAME", "VERSION", "DESCRIPTION", 
            "DATAMODEL", "INCLUDE", "CALLED", "CODE", "CODE_SYSTEM", "VALUE_SET", 
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
                  "DESCRIPTION", "DATAMODEL", "INCLUDE", "CALLED", "CODE", 
                  "CODE_SYSTEM", "VALUE_SET", "TERM_SET", "DOCUMENT_SET", 
                  "COHORT", "POPULATION", "DEFINE", "CONTEXT", "MIN_VALUE", 
                  "MAX_VALUE", "ENUM_LIST", "LIMIT", "OMOP", "CLARITY_CORE", 
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


