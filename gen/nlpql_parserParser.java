// Generated from /Users/charityhilton/repos/health-nlp/nlpql/nlpql_parser.g4 by ANTLR 4.7
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.*;
import org.antlr.v4.runtime.tree.*;
import java.util.List;
import java.util.Iterator;
import java.util.ArrayList;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast"})
public class nlpql_parserParser extends Parser {
	static { RuntimeMetaData.checkVersion("4.7", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		PHENOTYPE_NAME=1, VERSION=2, DESCRIPTION=3, DATAMODEL=4, INCLUDE=5, CALLED=6, 
		CODE_SYSTEM=7, VALUE_SET=8, TERM_SET=9, OMOP=10, CLARITY_CORE=11, OHDSI_HELPERS=12, 
		SEMI=13, COLON=14, DOT=15, COMMA=16, L_PAREN=17, R_PAREN=18, L_BRACKET=19, 
		R_BRACKET=20, DECIMAL=21, HEX=22, OCT=23, BINARY=24, FLOAT=25, HEX_FLOAT=26, 
		BOOL=27, CHAR=28, STRING=29, WS=30, COMMENT=31, LINE_COMMENT=32, IDENTIFIER=33, 
		L_CURLY=34, R_CURLY=35, NULL=36;
	public static final int
		RULE_validExpression = 0, RULE_statement = 1, RULE_phenotypeName = 2, 
		RULE_description = 3, RULE_dataModel = 4, RULE_include = 5, RULE_codeSystem = 6, 
		RULE_valueSet = 7, RULE_methodCall = 8, RULE_termSet = 9, RULE_obj = 10, 
		RULE_pair = 11, RULE_array = 12, RULE_value = 13;
	public static final String[] ruleNames = {
		"validExpression", "statement", "phenotypeName", "description", "dataModel", 
		"include", "codeSystem", "valueSet", "methodCall", "termSet", "obj", "pair", 
		"array", "value"
	};

	private static final String[] _LITERAL_NAMES = {
		null, "'phenotype'", "'version'", "'description'", "'datamodel'", "'include'", 
		"'called'", "'codesystem'", "'valueset'", "'termset'", "'OMOP'", "'ClarityCore'", 
		"'OHDSIHelpers'", "';'", "':'", "'.'", "','", "'('", "')'", "'['", "']'"
	};
	private static final String[] _SYMBOLIC_NAMES = {
		null, "PHENOTYPE_NAME", "VERSION", "DESCRIPTION", "DATAMODEL", "INCLUDE", 
		"CALLED", "CODE_SYSTEM", "VALUE_SET", "TERM_SET", "OMOP", "CLARITY_CORE", 
		"OHDSI_HELPERS", "SEMI", "COLON", "DOT", "COMMA", "L_PAREN", "R_PAREN", 
		"L_BRACKET", "R_BRACKET", "DECIMAL", "HEX", "OCT", "BINARY", "FLOAT", 
		"HEX_FLOAT", "BOOL", "CHAR", "STRING", "WS", "COMMENT", "LINE_COMMENT", 
		"IDENTIFIER", "L_CURLY", "R_CURLY", "NULL"
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

	@Override
	public String getGrammarFileName() { return "nlpql_parser.g4"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public ATN getATN() { return _ATN; }

	public nlpql_parserParser(TokenStream input) {
		super(input);
		_interp = new ParserATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}
	public static class ValidExpressionContext extends ParserRuleContext {
		public TerminalNode EOF() { return getToken(nlpql_parserParser.EOF, 0); }
		public List<StatementContext> statement() {
			return getRuleContexts(StatementContext.class);
		}
		public StatementContext statement(int i) {
			return getRuleContext(StatementContext.class,i);
		}
		public ValidExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_validExpression; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).enterValidExpression(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).exitValidExpression(this);
		}
	}

	public final ValidExpressionContext validExpression() throws RecognitionException {
		ValidExpressionContext _localctx = new ValidExpressionContext(_ctx, getState());
		enterRule(_localctx, 0, RULE_validExpression);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(31);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << PHENOTYPE_NAME) | (1L << DESCRIPTION) | (1L << DATAMODEL) | (1L << INCLUDE) | (1L << CODE_SYSTEM) | (1L << VALUE_SET) | (1L << TERM_SET))) != 0)) {
				{
				{
				setState(28);
				statement();
				}
				}
				setState(33);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(34);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class StatementContext extends ParserRuleContext {
		public TerminalNode SEMI() { return getToken(nlpql_parserParser.SEMI, 0); }
		public PhenotypeNameContext phenotypeName() {
			return getRuleContext(PhenotypeNameContext.class,0);
		}
		public DescriptionContext description() {
			return getRuleContext(DescriptionContext.class,0);
		}
		public DataModelContext dataModel() {
			return getRuleContext(DataModelContext.class,0);
		}
		public IncludeContext include() {
			return getRuleContext(IncludeContext.class,0);
		}
		public CodeSystemContext codeSystem() {
			return getRuleContext(CodeSystemContext.class,0);
		}
		public ValueSetContext valueSet() {
			return getRuleContext(ValueSetContext.class,0);
		}
		public TermSetContext termSet() {
			return getRuleContext(TermSetContext.class,0);
		}
		public StatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_statement; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).enterStatement(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).exitStatement(this);
		}
	}

	public final StatementContext statement() throws RecognitionException {
		StatementContext _localctx = new StatementContext(_ctx, getState());
		enterRule(_localctx, 2, RULE_statement);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(43);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case PHENOTYPE_NAME:
				{
				setState(36);
				phenotypeName();
				}
				break;
			case DESCRIPTION:
				{
				setState(37);
				description();
				}
				break;
			case DATAMODEL:
				{
				setState(38);
				dataModel();
				}
				break;
			case INCLUDE:
				{
				setState(39);
				include();
				}
				break;
			case CODE_SYSTEM:
				{
				setState(40);
				codeSystem();
				}
				break;
			case VALUE_SET:
				{
				setState(41);
				valueSet();
				}
				break;
			case TERM_SET:
				{
				setState(42);
				termSet();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
			setState(45);
			match(SEMI);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class PhenotypeNameContext extends ParserRuleContext {
		public TerminalNode PHENOTYPE_NAME() { return getToken(nlpql_parserParser.PHENOTYPE_NAME, 0); }
		public List<TerminalNode> STRING() { return getTokens(nlpql_parserParser.STRING); }
		public TerminalNode STRING(int i) {
			return getToken(nlpql_parserParser.STRING, i);
		}
		public TerminalNode VERSION() { return getToken(nlpql_parserParser.VERSION, 0); }
		public PhenotypeNameContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_phenotypeName; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).enterPhenotypeName(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).exitPhenotypeName(this);
		}
	}

	public final PhenotypeNameContext phenotypeName() throws RecognitionException {
		PhenotypeNameContext _localctx = new PhenotypeNameContext(_ctx, getState());
		enterRule(_localctx, 4, RULE_phenotypeName);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(47);
			match(PHENOTYPE_NAME);
			setState(48);
			match(STRING);
			setState(50);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==VERSION) {
				{
				setState(49);
				match(VERSION);
				}
			}

			setState(53);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==STRING) {
				{
				setState(52);
				match(STRING);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class DescriptionContext extends ParserRuleContext {
		public TerminalNode DESCRIPTION() { return getToken(nlpql_parserParser.DESCRIPTION, 0); }
		public List<TerminalNode> STRING() { return getTokens(nlpql_parserParser.STRING); }
		public TerminalNode STRING(int i) {
			return getToken(nlpql_parserParser.STRING, i);
		}
		public TerminalNode VERSION() { return getToken(nlpql_parserParser.VERSION, 0); }
		public DescriptionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_description; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).enterDescription(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).exitDescription(this);
		}
	}

	public final DescriptionContext description() throws RecognitionException {
		DescriptionContext _localctx = new DescriptionContext(_ctx, getState());
		enterRule(_localctx, 6, RULE_description);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(55);
			match(DESCRIPTION);
			setState(56);
			match(STRING);
			setState(58);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==VERSION) {
				{
				setState(57);
				match(VERSION);
				}
			}

			setState(61);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==STRING) {
				{
				setState(60);
				match(STRING);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class DataModelContext extends ParserRuleContext {
		public TerminalNode DATAMODEL() { return getToken(nlpql_parserParser.DATAMODEL, 0); }
		public TerminalNode OMOP() { return getToken(nlpql_parserParser.OMOP, 0); }
		public List<TerminalNode> STRING() { return getTokens(nlpql_parserParser.STRING); }
		public TerminalNode STRING(int i) {
			return getToken(nlpql_parserParser.STRING, i);
		}
		public TerminalNode VERSION() { return getToken(nlpql_parserParser.VERSION, 0); }
		public DataModelContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_dataModel; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).enterDataModel(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).exitDataModel(this);
		}
	}

	public final DataModelContext dataModel() throws RecognitionException {
		DataModelContext _localctx = new DataModelContext(_ctx, getState());
		enterRule(_localctx, 8, RULE_dataModel);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(63);
			match(DATAMODEL);
			setState(64);
			_la = _input.LA(1);
			if ( !(_la==OMOP || _la==STRING) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			setState(66);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==VERSION) {
				{
				setState(65);
				match(VERSION);
				}
			}

			setState(69);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==STRING) {
				{
				setState(68);
				match(STRING);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class IncludeContext extends ParserRuleContext {
		public TerminalNode INCLUDE() { return getToken(nlpql_parserParser.INCLUDE, 0); }
		public TerminalNode CALLED() { return getToken(nlpql_parserParser.CALLED, 0); }
		public TerminalNode IDENTIFIER() { return getToken(nlpql_parserParser.IDENTIFIER, 0); }
		public TerminalNode CLARITY_CORE() { return getToken(nlpql_parserParser.CLARITY_CORE, 0); }
		public TerminalNode OHDSI_HELPERS() { return getToken(nlpql_parserParser.OHDSI_HELPERS, 0); }
		public List<TerminalNode> STRING() { return getTokens(nlpql_parserParser.STRING); }
		public TerminalNode STRING(int i) {
			return getToken(nlpql_parserParser.STRING, i);
		}
		public TerminalNode VERSION() { return getToken(nlpql_parserParser.VERSION, 0); }
		public IncludeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_include; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).enterInclude(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).exitInclude(this);
		}
	}

	public final IncludeContext include() throws RecognitionException {
		IncludeContext _localctx = new IncludeContext(_ctx, getState());
		enterRule(_localctx, 10, RULE_include);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(71);
			match(INCLUDE);
			setState(72);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << CLARITY_CORE) | (1L << OHDSI_HELPERS) | (1L << STRING))) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			setState(74);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==VERSION) {
				{
				setState(73);
				match(VERSION);
				}
			}

			setState(77);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==STRING) {
				{
				setState(76);
				match(STRING);
				}
			}

			setState(79);
			match(CALLED);
			setState(80);
			match(IDENTIFIER);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class CodeSystemContext extends ParserRuleContext {
		public TerminalNode CODE_SYSTEM() { return getToken(nlpql_parserParser.CODE_SYSTEM, 0); }
		public TerminalNode STRING() { return getToken(nlpql_parserParser.STRING, 0); }
		public TerminalNode COLON() { return getToken(nlpql_parserParser.COLON, 0); }
		public ValueContext value() {
			return getRuleContext(ValueContext.class,0);
		}
		public CodeSystemContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_codeSystem; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).enterCodeSystem(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).exitCodeSystem(this);
		}
	}

	public final CodeSystemContext codeSystem() throws RecognitionException {
		CodeSystemContext _localctx = new CodeSystemContext(_ctx, getState());
		enterRule(_localctx, 12, RULE_codeSystem);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(82);
			match(CODE_SYSTEM);
			setState(83);
			match(STRING);
			setState(84);
			match(COLON);
			setState(85);
			value();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ValueSetContext extends ParserRuleContext {
		public TerminalNode VALUE_SET() { return getToken(nlpql_parserParser.VALUE_SET, 0); }
		public TerminalNode STRING() { return getToken(nlpql_parserParser.STRING, 0); }
		public TerminalNode COLON() { return getToken(nlpql_parserParser.COLON, 0); }
		public MethodCallContext methodCall() {
			return getRuleContext(MethodCallContext.class,0);
		}
		public ValueSetContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_valueSet; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).enterValueSet(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).exitValueSet(this);
		}
	}

	public final ValueSetContext valueSet() throws RecognitionException {
		ValueSetContext _localctx = new ValueSetContext(_ctx, getState());
		enterRule(_localctx, 14, RULE_valueSet);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(87);
			match(VALUE_SET);
			setState(88);
			match(STRING);
			setState(89);
			match(COLON);
			setState(90);
			methodCall();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class MethodCallContext extends ParserRuleContext {
		public List<TerminalNode> IDENTIFIER() { return getTokens(nlpql_parserParser.IDENTIFIER); }
		public TerminalNode IDENTIFIER(int i) {
			return getToken(nlpql_parserParser.IDENTIFIER, i);
		}
		public TerminalNode DOT() { return getToken(nlpql_parserParser.DOT, 0); }
		public TerminalNode L_PAREN() { return getToken(nlpql_parserParser.L_PAREN, 0); }
		public ValueContext value() {
			return getRuleContext(ValueContext.class,0);
		}
		public TerminalNode R_PAREN() { return getToken(nlpql_parserParser.R_PAREN, 0); }
		public MethodCallContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_methodCall; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).enterMethodCall(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).exitMethodCall(this);
		}
	}

	public final MethodCallContext methodCall() throws RecognitionException {
		MethodCallContext _localctx = new MethodCallContext(_ctx, getState());
		enterRule(_localctx, 16, RULE_methodCall);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(92);
			match(IDENTIFIER);
			setState(93);
			match(DOT);
			setState(94);
			match(IDENTIFIER);
			setState(95);
			match(L_PAREN);
			setState(96);
			value();
			setState(97);
			match(R_PAREN);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class TermSetContext extends ParserRuleContext {
		public TerminalNode TERM_SET() { return getToken(nlpql_parserParser.TERM_SET, 0); }
		public List<TerminalNode> STRING() { return getTokens(nlpql_parserParser.STRING); }
		public TerminalNode STRING(int i) {
			return getToken(nlpql_parserParser.STRING, i);
		}
		public TerminalNode COLON() { return getToken(nlpql_parserParser.COLON, 0); }
		public ArrayContext array() {
			return getRuleContext(ArrayContext.class,0);
		}
		public TermSetContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_termSet; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).enterTermSet(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).exitTermSet(this);
		}
	}

	public final TermSetContext termSet() throws RecognitionException {
		TermSetContext _localctx = new TermSetContext(_ctx, getState());
		enterRule(_localctx, 18, RULE_termSet);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(99);
			match(TERM_SET);
			setState(100);
			match(STRING);
			setState(101);
			match(COLON);
			setState(104);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case L_BRACKET:
				{
				setState(102);
				array();
				}
				break;
			case STRING:
				{
				setState(103);
				match(STRING);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ObjContext extends ParserRuleContext {
		public TerminalNode L_CURLY() { return getToken(nlpql_parserParser.L_CURLY, 0); }
		public List<PairContext> pair() {
			return getRuleContexts(PairContext.class);
		}
		public PairContext pair(int i) {
			return getRuleContext(PairContext.class,i);
		}
		public TerminalNode R_CURLY() { return getToken(nlpql_parserParser.R_CURLY, 0); }
		public List<TerminalNode> COMMA() { return getTokens(nlpql_parserParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(nlpql_parserParser.COMMA, i);
		}
		public ObjContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_obj; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).enterObj(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).exitObj(this);
		}
	}

	public final ObjContext obj() throws RecognitionException {
		ObjContext _localctx = new ObjContext(_ctx, getState());
		enterRule(_localctx, 20, RULE_obj);
		int _la;
		try {
			setState(119);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,12,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(106);
				match(L_CURLY);
				setState(107);
				pair();
				setState(112);
				_errHandler.sync(this);
				_la = _input.LA(1);
				while (_la==COMMA) {
					{
					{
					setState(108);
					match(COMMA);
					setState(109);
					pair();
					}
					}
					setState(114);
					_errHandler.sync(this);
					_la = _input.LA(1);
				}
				setState(115);
				match(R_CURLY);
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(117);
				match(L_CURLY);
				setState(118);
				match(R_CURLY);
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class PairContext extends ParserRuleContext {
		public TerminalNode STRING() { return getToken(nlpql_parserParser.STRING, 0); }
		public TerminalNode COLON() { return getToken(nlpql_parserParser.COLON, 0); }
		public ValueContext value() {
			return getRuleContext(ValueContext.class,0);
		}
		public PairContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_pair; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).enterPair(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).exitPair(this);
		}
	}

	public final PairContext pair() throws RecognitionException {
		PairContext _localctx = new PairContext(_ctx, getState());
		enterRule(_localctx, 22, RULE_pair);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(121);
			match(STRING);
			setState(122);
			match(COLON);
			setState(123);
			value();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ArrayContext extends ParserRuleContext {
		public TerminalNode L_BRACKET() { return getToken(nlpql_parserParser.L_BRACKET, 0); }
		public List<ValueContext> value() {
			return getRuleContexts(ValueContext.class);
		}
		public ValueContext value(int i) {
			return getRuleContext(ValueContext.class,i);
		}
		public TerminalNode R_BRACKET() { return getToken(nlpql_parserParser.R_BRACKET, 0); }
		public List<TerminalNode> COMMA() { return getTokens(nlpql_parserParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(nlpql_parserParser.COMMA, i);
		}
		public ArrayContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_array; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).enterArray(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).exitArray(this);
		}
	}

	public final ArrayContext array() throws RecognitionException {
		ArrayContext _localctx = new ArrayContext(_ctx, getState());
		enterRule(_localctx, 24, RULE_array);
		int _la;
		try {
			setState(138);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,14,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(125);
				match(L_BRACKET);
				setState(126);
				value();
				setState(131);
				_errHandler.sync(this);
				_la = _input.LA(1);
				while (_la==COMMA) {
					{
					{
					setState(127);
					match(COMMA);
					setState(128);
					value();
					}
					}
					setState(133);
					_errHandler.sync(this);
					_la = _input.LA(1);
				}
				setState(134);
				match(R_BRACKET);
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(136);
				match(L_BRACKET);
				setState(137);
				match(R_BRACKET);
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ValueContext extends ParserRuleContext {
		public TerminalNode STRING() { return getToken(nlpql_parserParser.STRING, 0); }
		public TerminalNode DECIMAL() { return getToken(nlpql_parserParser.DECIMAL, 0); }
		public ObjContext obj() {
			return getRuleContext(ObjContext.class,0);
		}
		public ArrayContext array() {
			return getRuleContext(ArrayContext.class,0);
		}
		public TerminalNode BOOL() { return getToken(nlpql_parserParser.BOOL, 0); }
		public TerminalNode NULL() { return getToken(nlpql_parserParser.NULL, 0); }
		public ValueContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_value; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).enterValue(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof nlpql_parserListener ) ((nlpql_parserListener)listener).exitValue(this);
		}
	}

	public final ValueContext value() throws RecognitionException {
		ValueContext _localctx = new ValueContext(_ctx, getState());
		enterRule(_localctx, 26, RULE_value);
		try {
			setState(146);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case STRING:
				enterOuterAlt(_localctx, 1);
				{
				setState(140);
				match(STRING);
				}
				break;
			case DECIMAL:
				enterOuterAlt(_localctx, 2);
				{
				setState(141);
				match(DECIMAL);
				}
				break;
			case L_CURLY:
				enterOuterAlt(_localctx, 3);
				{
				setState(142);
				obj();
				}
				break;
			case L_BRACKET:
				enterOuterAlt(_localctx, 4);
				{
				setState(143);
				array();
				}
				break;
			case BOOL:
				enterOuterAlt(_localctx, 5);
				{
				setState(144);
				match(BOOL);
				}
				break;
			case NULL:
				enterOuterAlt(_localctx, 6);
				{
				setState(145);
				match(NULL);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static final String _serializedATN =
		"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3&\u0097\4\2\t\2\4"+
		"\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t"+
		"\13\4\f\t\f\4\r\t\r\4\16\t\16\4\17\t\17\3\2\7\2 \n\2\f\2\16\2#\13\2\3"+
		"\2\3\2\3\3\3\3\3\3\3\3\3\3\3\3\3\3\5\3.\n\3\3\3\3\3\3\4\3\4\3\4\5\4\65"+
		"\n\4\3\4\5\48\n\4\3\5\3\5\3\5\5\5=\n\5\3\5\5\5@\n\5\3\6\3\6\3\6\5\6E\n"+
		"\6\3\6\5\6H\n\6\3\7\3\7\3\7\5\7M\n\7\3\7\5\7P\n\7\3\7\3\7\3\7\3\b\3\b"+
		"\3\b\3\b\3\b\3\t\3\t\3\t\3\t\3\t\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\13\3\13"+
		"\3\13\3\13\3\13\5\13k\n\13\3\f\3\f\3\f\3\f\7\fq\n\f\f\f\16\ft\13\f\3\f"+
		"\3\f\3\f\3\f\5\fz\n\f\3\r\3\r\3\r\3\r\3\16\3\16\3\16\3\16\7\16\u0084\n"+
		"\16\f\16\16\16\u0087\13\16\3\16\3\16\3\16\3\16\5\16\u008d\n\16\3\17\3"+
		"\17\3\17\3\17\3\17\3\17\5\17\u0095\n\17\3\17\2\2\20\2\4\6\b\n\f\16\20"+
		"\22\24\26\30\32\34\2\4\4\2\f\f\37\37\4\2\r\16\37\37\2\u00a1\2!\3\2\2\2"+
		"\4-\3\2\2\2\6\61\3\2\2\2\b9\3\2\2\2\nA\3\2\2\2\fI\3\2\2\2\16T\3\2\2\2"+
		"\20Y\3\2\2\2\22^\3\2\2\2\24e\3\2\2\2\26y\3\2\2\2\30{\3\2\2\2\32\u008c"+
		"\3\2\2\2\34\u0094\3\2\2\2\36 \5\4\3\2\37\36\3\2\2\2 #\3\2\2\2!\37\3\2"+
		"\2\2!\"\3\2\2\2\"$\3\2\2\2#!\3\2\2\2$%\7\2\2\3%\3\3\2\2\2&.\5\6\4\2\'"+
		".\5\b\5\2(.\5\n\6\2).\5\f\7\2*.\5\16\b\2+.\5\20\t\2,.\5\24\13\2-&\3\2"+
		"\2\2-\'\3\2\2\2-(\3\2\2\2-)\3\2\2\2-*\3\2\2\2-+\3\2\2\2-,\3\2\2\2./\3"+
		"\2\2\2/\60\7\17\2\2\60\5\3\2\2\2\61\62\7\3\2\2\62\64\7\37\2\2\63\65\7"+
		"\4\2\2\64\63\3\2\2\2\64\65\3\2\2\2\65\67\3\2\2\2\668\7\37\2\2\67\66\3"+
		"\2\2\2\678\3\2\2\28\7\3\2\2\29:\7\5\2\2:<\7\37\2\2;=\7\4\2\2<;\3\2\2\2"+
		"<=\3\2\2\2=?\3\2\2\2>@\7\37\2\2?>\3\2\2\2?@\3\2\2\2@\t\3\2\2\2AB\7\6\2"+
		"\2BD\t\2\2\2CE\7\4\2\2DC\3\2\2\2DE\3\2\2\2EG\3\2\2\2FH\7\37\2\2GF\3\2"+
		"\2\2GH\3\2\2\2H\13\3\2\2\2IJ\7\7\2\2JL\t\3\2\2KM\7\4\2\2LK\3\2\2\2LM\3"+
		"\2\2\2MO\3\2\2\2NP\7\37\2\2ON\3\2\2\2OP\3\2\2\2PQ\3\2\2\2QR\7\b\2\2RS"+
		"\7#\2\2S\r\3\2\2\2TU\7\t\2\2UV\7\37\2\2VW\7\20\2\2WX\5\34\17\2X\17\3\2"+
		"\2\2YZ\7\n\2\2Z[\7\37\2\2[\\\7\20\2\2\\]\5\22\n\2]\21\3\2\2\2^_\7#\2\2"+
		"_`\7\21\2\2`a\7#\2\2ab\7\23\2\2bc\5\34\17\2cd\7\24\2\2d\23\3\2\2\2ef\7"+
		"\13\2\2fg\7\37\2\2gj\7\20\2\2hk\5\32\16\2ik\7\37\2\2jh\3\2\2\2ji\3\2\2"+
		"\2k\25\3\2\2\2lm\7$\2\2mr\5\30\r\2no\7\22\2\2oq\5\30\r\2pn\3\2\2\2qt\3"+
		"\2\2\2rp\3\2\2\2rs\3\2\2\2su\3\2\2\2tr\3\2\2\2uv\7%\2\2vz\3\2\2\2wx\7"+
		"$\2\2xz\7%\2\2yl\3\2\2\2yw\3\2\2\2z\27\3\2\2\2{|\7\37\2\2|}\7\20\2\2}"+
		"~\5\34\17\2~\31\3\2\2\2\177\u0080\7\25\2\2\u0080\u0085\5\34\17\2\u0081"+
		"\u0082\7\22\2\2\u0082\u0084\5\34\17\2\u0083\u0081\3\2\2\2\u0084\u0087"+
		"\3\2\2\2\u0085\u0083\3\2\2\2\u0085\u0086\3\2\2\2\u0086\u0088\3\2\2\2\u0087"+
		"\u0085\3\2\2\2\u0088\u0089\7\26\2\2\u0089\u008d\3\2\2\2\u008a\u008b\7"+
		"\25\2\2\u008b\u008d\7\26\2\2\u008c\177\3\2\2\2\u008c\u008a\3\2\2\2\u008d"+
		"\33\3\2\2\2\u008e\u0095\7\37\2\2\u008f\u0095\7\27\2\2\u0090\u0095\5\26"+
		"\f\2\u0091\u0095\5\32\16\2\u0092\u0095\7\35\2\2\u0093\u0095\7&\2\2\u0094"+
		"\u008e\3\2\2\2\u0094\u008f\3\2\2\2\u0094\u0090\3\2\2\2\u0094\u0091\3\2"+
		"\2\2\u0094\u0092\3\2\2\2\u0094\u0093\3\2\2\2\u0095\35\3\2\2\2\22!-\64"+
		"\67<?DGLOjry\u0085\u008c\u0094";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}