// Generated from /Users/charityhilton/repos/health-nlp/nlpql/nlpql_lexer.g4 by ANTLR 4.7
import org.antlr.v4.runtime.Lexer;
import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.Token;
import org.antlr.v4.runtime.TokenStream;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.misc.*;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast"})
public class nlpql_lexer extends Lexer {
	static { RuntimeMetaData.checkVersion("4.7", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		PHENOTYPE_NAME=1, VERSION=2, DESCRIPTION=3, NEWLINE=4, WHITESPACE=5, LETTER_DIGIT=6, 
		LETTER_DIGIT_SPACE=7, DIGIT=8, VALID_VALUE=9, VALID_DIGIT=10, DOUBLE_QUOTE=11, 
		SINGLE_QUOTE=12, LPAREN=13, RPAREN=14, LBRACE=15, RBRACE=16, LBRACK=17, 
		RBRACK=18, SEMI=19, COMMA=20, DOT=21, ASSIGN=22, GT=23, LT=24, BANG=25, 
		TILDE=26, QUESTION=27, COLON=28, EQUAL=29, LE=30, GE=31, NOTEQUAL=32, 
		AND=33, OR=34, INC=35, DEC=36, ADD=37, SUB=38, MUL=39, DIV=40, BITAND=41, 
		BITOR=42, CARET=43, COMMENT=44, LINE_COMMENT=45;
	public static String[] channelNames = {
		"DEFAULT_TOKEN_CHANNEL", "HIDDEN"
	};

	public static String[] modeNames = {
		"DEFAULT_MODE"
	};

	public static final String[] ruleNames = {
		"PHENOTYPE_NAME", "VERSION", "DESCRIPTION", "NEWLINE", "WHITESPACE", "LETTER_DIGIT", 
		"LETTER_DIGIT_SPACE", "DIGIT", "VALID_VALUE", "VALID_DIGIT", "DOUBLE_QUOTE", 
		"SINGLE_QUOTE", "LPAREN", "RPAREN", "LBRACE", "RBRACE", "LBRACK", "RBRACK", 
		"SEMI", "COMMA", "DOT", "ASSIGN", "GT", "LT", "BANG", "TILDE", "QUESTION", 
		"COLON", "EQUAL", "LE", "GE", "NOTEQUAL", "AND", "OR", "INC", "DEC", "ADD", 
		"SUB", "MUL", "DIV", "BITAND", "BITOR", "CARET", "COMMENT", "LINE_COMMENT"
	};

	private static final String[] _LITERAL_NAMES = {
		null, null, "'version'", "'description'", null, null, "'[0-9a-zA-Z]'", 
		"'[0-9a-zA-Z \t]'", "'[0-9]'", null, null, null, null, "'('", "')'", "'{'", 
		"'}'", "'['", "']'", "';'", "','", "'.'", "'='", "'>'", "'<'", "'!'", 
		"'~'", "'?'", "':'", "'=='", "'<='", "'>='", "'!='", "'&&'", "'||'", "'++'", 
		"'--'", "'+'", "'-'", "'*'", "'/'", "'&'", "'|'", "'^'"
	};
	private static final String[] _SYMBOLIC_NAMES = {
		null, "PHENOTYPE_NAME", "VERSION", "DESCRIPTION", "NEWLINE", "WHITESPACE", 
		"LETTER_DIGIT", "LETTER_DIGIT_SPACE", "DIGIT", "VALID_VALUE", "VALID_DIGIT", 
		"DOUBLE_QUOTE", "SINGLE_QUOTE", "LPAREN", "RPAREN", "LBRACE", "RBRACE", 
		"LBRACK", "RBRACK", "SEMI", "COMMA", "DOT", "ASSIGN", "GT", "LT", "BANG", 
		"TILDE", "QUESTION", "COLON", "EQUAL", "LE", "GE", "NOTEQUAL", "AND", 
		"OR", "INC", "DEC", "ADD", "SUB", "MUL", "DIV", "BITAND", "BITOR", "CARET", 
		"COMMENT", "LINE_COMMENT"
	};
	public static final Vocabulary VOCABULARY = new VocabularyImpl(_LITERAL_NAMES, _SYMBOLIC_NAMES);

	/**
	 * @deprecated Use {@link #VOCABULARY} instead.
	 */
	@Deprecated
	public static final String[] tokenNames;
	static {
		tokenNames = new String[_SYMBOLIC_NAMES.length];
		for (int i = 0; i < tokenNames.length; i++) {
			tokenNames[i] = VOCABULARY.getLiteralName(i);
			if (tokenNames[i] == null) {
				tokenNames[i] = VOCABULARY.getSymbolicName(i);
			}

			if (tokenNames[i] == null) {
				tokenNames[i] = "<INVALID>";
			}
		}
	}

	@Override
	@Deprecated
	public String[] getTokenNames() {
		return tokenNames;
	}

	@Override

	public Vocabulary getVocabulary() {
		return VOCABULARY;
	}


	public nlpql_lexer(CharStream input) {
		super(input);
		_interp = new LexerATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}

	@Override
	public String getGrammarFileName() { return "nlpql_lexer.g4"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public String[] getChannelNames() { return channelNames; }

	@Override
	public String[] getModeNames() { return modeNames; }

	@Override
	public ATN getATN() { return _ATN; }

	public static final String _serializedATN =
		"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2/\u012d\b\1\4\2\t"+
		"\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13"+
		"\t\13\4\f\t\f\4\r\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22"+
		"\4\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30\4\31\t\31"+
		"\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35\4\36\t\36\4\37\t\37\4 \t \4!"+
		"\t!\4\"\t\"\4#\t#\4$\t$\4%\t%\4&\t&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t+\4"+
		",\t,\4-\t-\4.\t.\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3"+
		"\2\3\2\3\2\3\2\3\2\5\2p\n\2\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\4\3\4\3"+
		"\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\5\6\5\u0087\n\5\r\5\16\5\u0088"+
		"\3\6\3\6\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\b\3\b\3\b\3"+
		"\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\t\3\t\3\t\3\t\3\t\3\t\3\n"+
		"\3\n\5\n\u00af\n\n\3\n\3\n\3\n\5\n\u00b4\n\n\3\n\3\n\5\n\u00b8\n\n\3\13"+
		"\3\13\5\13\u00bc\n\13\3\13\3\13\3\13\5\13\u00c1\n\13\3\13\3\13\5\13\u00c5"+
		"\n\13\3\f\3\f\3\f\3\f\3\r\3\r\3\r\3\r\3\16\3\16\3\17\3\17\3\20\3\20\3"+
		"\21\3\21\3\22\3\22\3\23\3\23\3\24\3\24\3\25\3\25\3\26\3\26\3\27\3\27\3"+
		"\30\3\30\3\31\3\31\3\32\3\32\3\33\3\33\3\34\3\34\3\35\3\35\3\36\3\36\3"+
		"\36\3\37\3\37\3\37\3 \3 \3 \3!\3!\3!\3\"\3\"\3\"\3#\3#\3#\3$\3$\3$\3%"+
		"\3%\3%\3&\3&\3\'\3\'\3(\3(\3)\3)\3*\3*\3+\3+\3,\3,\3-\3-\3-\3-\7-\u0119"+
		"\n-\f-\16-\u011c\13-\3-\3-\3-\3-\3-\3.\3.\3.\3.\7.\u0127\n.\f.\16.\u012a"+
		"\13.\3.\3.\3\u011a\2/\3\3\5\4\7\5\t\6\13\7\r\b\17\t\21\n\23\13\25\f\27"+
		"\r\31\16\33\17\35\20\37\21!\22#\23%\24\'\25)\26+\27-\30/\31\61\32\63\33"+
		"\65\34\67\359\36;\37= ?!A\"C#E$G%I&K\'M(O)Q*S+U,W-Y.[/\3\2\4\4\2\f\f\17"+
		"\17\4\2\13\13\"\"\2\u0138\2\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2"+
		"\2\2\2\13\3\2\2\2\2\r\3\2\2\2\2\17\3\2\2\2\2\21\3\2\2\2\2\23\3\2\2\2\2"+
		"\25\3\2\2\2\2\27\3\2\2\2\2\31\3\2\2\2\2\33\3\2\2\2\2\35\3\2\2\2\2\37\3"+
		"\2\2\2\2!\3\2\2\2\2#\3\2\2\2\2%\3\2\2\2\2\'\3\2\2\2\2)\3\2\2\2\2+\3\2"+
		"\2\2\2-\3\2\2\2\2/\3\2\2\2\2\61\3\2\2\2\2\63\3\2\2\2\2\65\3\2\2\2\2\67"+
		"\3\2\2\2\29\3\2\2\2\2;\3\2\2\2\2=\3\2\2\2\2?\3\2\2\2\2A\3\2\2\2\2C\3\2"+
		"\2\2\2E\3\2\2\2\2G\3\2\2\2\2I\3\2\2\2\2K\3\2\2\2\2M\3\2\2\2\2O\3\2\2\2"+
		"\2Q\3\2\2\2\2S\3\2\2\2\2U\3\2\2\2\2W\3\2\2\2\2Y\3\2\2\2\2[\3\2\2\2\3o"+
		"\3\2\2\2\5q\3\2\2\2\7y\3\2\2\2\t\u0086\3\2\2\2\13\u008a\3\2\2\2\r\u008c"+
		"\3\2\2\2\17\u0098\3\2\2\2\21\u00a6\3\2\2\2\23\u00ae\3\2\2\2\25\u00bb\3"+
		"\2\2\2\27\u00c6\3\2\2\2\31\u00ca\3\2\2\2\33\u00ce\3\2\2\2\35\u00d0\3\2"+
		"\2\2\37\u00d2\3\2\2\2!\u00d4\3\2\2\2#\u00d6\3\2\2\2%\u00d8\3\2\2\2\'\u00da"+
		"\3\2\2\2)\u00dc\3\2\2\2+\u00de\3\2\2\2-\u00e0\3\2\2\2/\u00e2\3\2\2\2\61"+
		"\u00e4\3\2\2\2\63\u00e6\3\2\2\2\65\u00e8\3\2\2\2\67\u00ea\3\2\2\29\u00ec"+
		"\3\2\2\2;\u00ee\3\2\2\2=\u00f1\3\2\2\2?\u00f4\3\2\2\2A\u00f7\3\2\2\2C"+
		"\u00fa\3\2\2\2E\u00fd\3\2\2\2G\u0100\3\2\2\2I\u0103\3\2\2\2K\u0106\3\2"+
		"\2\2M\u0108\3\2\2\2O\u010a\3\2\2\2Q\u010c\3\2\2\2S\u010e\3\2\2\2U\u0110"+
		"\3\2\2\2W\u0112\3\2\2\2Y\u0114\3\2\2\2[\u0122\3\2\2\2]^\7r\2\2^_\7j\2"+
		"\2_`\7g\2\2`a\7p\2\2ab\7q\2\2bc\7v\2\2cd\7{\2\2de\7r\2\2ep\7g\2\2fg\7"+
		"n\2\2gh\7k\2\2hi\7d\2\2ij\7t\2\2jk\7c\2\2kl\7t\2\2lm\7{\2\2mn\3\2\2\2"+
		"np\5\13\6\2o]\3\2\2\2of\3\2\2\2p\4\3\2\2\2qr\7x\2\2rs\7g\2\2st\7t\2\2"+
		"tu\7u\2\2uv\7k\2\2vw\7q\2\2wx\7p\2\2x\6\3\2\2\2yz\7f\2\2z{\7g\2\2{|\7"+
		"u\2\2|}\7e\2\2}~\7t\2\2~\177\7k\2\2\177\u0080\7r\2\2\u0080\u0081\7v\2"+
		"\2\u0081\u0082\7k\2\2\u0082\u0083\7q\2\2\u0083\u0084\7p\2\2\u0084\b\3"+
		"\2\2\2\u0085\u0087\t\2\2\2\u0086\u0085\3\2\2\2\u0087\u0088\3\2\2\2\u0088"+
		"\u0086\3\2\2\2\u0088\u0089\3\2\2\2\u0089\n\3\2\2\2\u008a\u008b\t\3\2\2"+
		"\u008b\f\3\2\2\2\u008c\u008d\7]\2\2\u008d\u008e\7\62\2\2\u008e\u008f\7"+
		"/\2\2\u008f\u0090\7;\2\2\u0090\u0091\7c\2\2\u0091\u0092\7/\2\2\u0092\u0093"+
		"\7|\2\2\u0093\u0094\7C\2\2\u0094\u0095\7/\2\2\u0095\u0096\7\\\2\2\u0096"+
		"\u0097\7_\2\2\u0097\16\3\2\2\2\u0098\u0099\7]\2\2\u0099\u009a\7\62\2\2"+
		"\u009a\u009b\7/\2\2\u009b\u009c\7;\2\2\u009c\u009d\7c\2\2\u009d\u009e"+
		"\7/\2\2\u009e\u009f\7|\2\2\u009f\u00a0\7C\2\2\u00a0\u00a1\7/\2\2\u00a1"+
		"\u00a2\7\\\2\2\u00a2\u00a3\7\"\2\2\u00a3\u00a4\7\13\2\2\u00a4\u00a5\7"+
		"_\2\2\u00a5\20\3\2\2\2\u00a6\u00a7\7]\2\2\u00a7\u00a8\7\62\2\2\u00a8\u00a9"+
		"\7/\2\2\u00a9\u00aa\7;\2\2\u00aa\u00ab\7_\2\2\u00ab\22\3\2\2\2\u00ac\u00af"+
		"\5\27\f\2\u00ad\u00af\5\31\r\2\u00ae\u00ac\3\2\2\2\u00ae\u00ad\3\2\2\2"+
		"\u00af\u00b0\3\2\2\2\u00b0\u00b3\5\17\b\2\u00b1\u00b4\5\27\f\2\u00b2\u00b4"+
		"\5\31\r\2\u00b3\u00b1\3\2\2\2\u00b3\u00b2\3\2\2\2\u00b4\u00b7\3\2\2\2"+
		"\u00b5\u00b8\5\13\6\2\u00b6\u00b8\5\t\5\2\u00b7\u00b5\3\2\2\2\u00b7\u00b6"+
		"\3\2\2\2\u00b8\24\3\2\2\2\u00b9\u00bc\5\27\f\2\u00ba\u00bc\5\31\r\2\u00bb"+
		"\u00b9\3\2\2\2\u00bb\u00ba\3\2\2\2\u00bb\u00bc\3\2\2\2\u00bc\u00bd\3\2"+
		"\2\2\u00bd\u00c0\5\21\t\2\u00be\u00c1\5\27\f\2\u00bf\u00c1\5\31\r\2\u00c0"+
		"\u00be\3\2\2\2\u00c0\u00bf\3\2\2\2\u00c0\u00c1\3\2\2\2\u00c1\u00c4\3\2"+
		"\2\2\u00c2\u00c5\5\13\6\2\u00c3\u00c5\5\t\5\2\u00c4\u00c2\3\2\2\2\u00c4"+
		"\u00c3\3\2\2\2\u00c5\26\3\2\2\2\u00c6\u00c7\7$\2\2\u00c7\u00c8\5\23\n"+
		"\2\u00c8\u00c9\7$\2\2\u00c9\30\3\2\2\2\u00ca\u00cb\7)\2\2\u00cb\u00cc"+
		"\5\23\n\2\u00cc\u00cd\7)\2\2\u00cd\32\3\2\2\2\u00ce\u00cf\7*\2\2\u00cf"+
		"\34\3\2\2\2\u00d0\u00d1\7+\2\2\u00d1\36\3\2\2\2\u00d2\u00d3\7}\2\2\u00d3"+
		" \3\2\2\2\u00d4\u00d5\7\177\2\2\u00d5\"\3\2\2\2\u00d6\u00d7\7]\2\2\u00d7"+
		"$\3\2\2\2\u00d8\u00d9\7_\2\2\u00d9&\3\2\2\2\u00da\u00db\7=\2\2\u00db("+
		"\3\2\2\2\u00dc\u00dd\7.\2\2\u00dd*\3\2\2\2\u00de\u00df\7\60\2\2\u00df"+
		",\3\2\2\2\u00e0\u00e1\7?\2\2\u00e1.\3\2\2\2\u00e2\u00e3\7@\2\2\u00e3\60"+
		"\3\2\2\2\u00e4\u00e5\7>\2\2\u00e5\62\3\2\2\2\u00e6\u00e7\7#\2\2\u00e7"+
		"\64\3\2\2\2\u00e8\u00e9\7\u0080\2\2\u00e9\66\3\2\2\2\u00ea\u00eb\7A\2"+
		"\2\u00eb8\3\2\2\2\u00ec\u00ed\7<\2\2\u00ed:\3\2\2\2\u00ee\u00ef\7?\2\2"+
		"\u00ef\u00f0\7?\2\2\u00f0<\3\2\2\2\u00f1\u00f2\7>\2\2\u00f2\u00f3\7?\2"+
		"\2\u00f3>\3\2\2\2\u00f4\u00f5\7@\2\2\u00f5\u00f6\7?\2\2\u00f6@\3\2\2\2"+
		"\u00f7\u00f8\7#\2\2\u00f8\u00f9\7?\2\2\u00f9B\3\2\2\2\u00fa\u00fb\7(\2"+
		"\2\u00fb\u00fc\7(\2\2\u00fcD\3\2\2\2\u00fd\u00fe\7~\2\2\u00fe\u00ff\7"+
		"~\2\2\u00ffF\3\2\2\2\u0100\u0101\7-\2\2\u0101\u0102\7-\2\2\u0102H\3\2"+
		"\2\2\u0103\u0104\7/\2\2\u0104\u0105\7/\2\2\u0105J\3\2\2\2\u0106\u0107"+
		"\7-\2\2\u0107L\3\2\2\2\u0108\u0109\7/\2\2\u0109N\3\2\2\2\u010a\u010b\7"+
		",\2\2\u010bP\3\2\2\2\u010c\u010d\7\61\2\2\u010dR\3\2\2\2\u010e\u010f\7"+
		"(\2\2\u010fT\3\2\2\2\u0110\u0111\7~\2\2\u0111V\3\2\2\2\u0112\u0113\7`"+
		"\2\2\u0113X\3\2\2\2\u0114\u0115\7\61\2\2\u0115\u0116\7,\2\2\u0116\u011a"+
		"\3\2\2\2\u0117\u0119\13\2\2\2\u0118\u0117\3\2\2\2\u0119\u011c\3\2\2\2"+
		"\u011a\u011b\3\2\2\2\u011a\u0118\3\2\2\2\u011b\u011d\3\2\2\2\u011c\u011a"+
		"\3\2\2\2\u011d\u011e\7,\2\2\u011e\u011f\7\61\2\2\u011f\u0120\3\2\2\2\u0120"+
		"\u0121\b-\2\2\u0121Z\3\2\2\2\u0122\u0123\7\61\2\2\u0123\u0124\7\61\2\2"+
		"\u0124\u0128\3\2\2\2\u0125\u0127\n\2\2\2\u0126\u0125\3\2\2\2\u0127\u012a"+
		"\3\2\2\2\u0128\u0126\3\2\2\2\u0128\u0129\3\2\2\2\u0129\u012b\3\2\2\2\u012a"+
		"\u0128\3\2\2\2\u012b\u012c\b.\2\2\u012c\\\3\2\2\2\r\2o\u0088\u00ae\u00b3"+
		"\u00b7\u00bb\u00c0\u00c4\u011a\u0128\3\2\3\2";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}