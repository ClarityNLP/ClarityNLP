// Generated from /Users/charityhilton/repos/health-nlp/nlpql/nlpql_parser.g4 by ANTLR 4.7
import org.antlr.v4.runtime.tree.ParseTreeListener;

/**
 * This interface defines a complete listener for a parse tree produced by
 * {@link nlpql_parserParser}.
 */
public interface nlpql_parserListener extends ParseTreeListener {
	/**
	 * Enter a parse tree produced by {@link nlpql_parserParser#validExpression}.
	 * @param ctx the parse tree
	 */
	void enterValidExpression(nlpql_parserParser.ValidExpressionContext ctx);
	/**
	 * Exit a parse tree produced by {@link nlpql_parserParser#validExpression}.
	 * @param ctx the parse tree
	 */
	void exitValidExpression(nlpql_parserParser.ValidExpressionContext ctx);
	/**
	 * Enter a parse tree produced by {@link nlpql_parserParser#statement}.
	 * @param ctx the parse tree
	 */
	void enterStatement(nlpql_parserParser.StatementContext ctx);
	/**
	 * Exit a parse tree produced by {@link nlpql_parserParser#statement}.
	 * @param ctx the parse tree
	 */
	void exitStatement(nlpql_parserParser.StatementContext ctx);
	/**
	 * Enter a parse tree produced by {@link nlpql_parserParser#phenotypeName}.
	 * @param ctx the parse tree
	 */
	void enterPhenotypeName(nlpql_parserParser.PhenotypeNameContext ctx);
	/**
	 * Exit a parse tree produced by {@link nlpql_parserParser#phenotypeName}.
	 * @param ctx the parse tree
	 */
	void exitPhenotypeName(nlpql_parserParser.PhenotypeNameContext ctx);
	/**
	 * Enter a parse tree produced by {@link nlpql_parserParser#description}.
	 * @param ctx the parse tree
	 */
	void enterDescription(nlpql_parserParser.DescriptionContext ctx);
	/**
	 * Exit a parse tree produced by {@link nlpql_parserParser#description}.
	 * @param ctx the parse tree
	 */
	void exitDescription(nlpql_parserParser.DescriptionContext ctx);
	/**
	 * Enter a parse tree produced by {@link nlpql_parserParser#dataModel}.
	 * @param ctx the parse tree
	 */
	void enterDataModel(nlpql_parserParser.DataModelContext ctx);
	/**
	 * Exit a parse tree produced by {@link nlpql_parserParser#dataModel}.
	 * @param ctx the parse tree
	 */
	void exitDataModel(nlpql_parserParser.DataModelContext ctx);
	/**
	 * Enter a parse tree produced by {@link nlpql_parserParser#include}.
	 * @param ctx the parse tree
	 */
	void enterInclude(nlpql_parserParser.IncludeContext ctx);
	/**
	 * Exit a parse tree produced by {@link nlpql_parserParser#include}.
	 * @param ctx the parse tree
	 */
	void exitInclude(nlpql_parserParser.IncludeContext ctx);
	/**
	 * Enter a parse tree produced by {@link nlpql_parserParser#codeSystem}.
	 * @param ctx the parse tree
	 */
	void enterCodeSystem(nlpql_parserParser.CodeSystemContext ctx);
	/**
	 * Exit a parse tree produced by {@link nlpql_parserParser#codeSystem}.
	 * @param ctx the parse tree
	 */
	void exitCodeSystem(nlpql_parserParser.CodeSystemContext ctx);
	/**
	 * Enter a parse tree produced by {@link nlpql_parserParser#valueSet}.
	 * @param ctx the parse tree
	 */
	void enterValueSet(nlpql_parserParser.ValueSetContext ctx);
	/**
	 * Exit a parse tree produced by {@link nlpql_parserParser#valueSet}.
	 * @param ctx the parse tree
	 */
	void exitValueSet(nlpql_parserParser.ValueSetContext ctx);
	/**
	 * Enter a parse tree produced by {@link nlpql_parserParser#methodCall}.
	 * @param ctx the parse tree
	 */
	void enterMethodCall(nlpql_parserParser.MethodCallContext ctx);
	/**
	 * Exit a parse tree produced by {@link nlpql_parserParser#methodCall}.
	 * @param ctx the parse tree
	 */
	void exitMethodCall(nlpql_parserParser.MethodCallContext ctx);
	/**
	 * Enter a parse tree produced by {@link nlpql_parserParser#termSet}.
	 * @param ctx the parse tree
	 */
	void enterTermSet(nlpql_parserParser.TermSetContext ctx);
	/**
	 * Exit a parse tree produced by {@link nlpql_parserParser#termSet}.
	 * @param ctx the parse tree
	 */
	void exitTermSet(nlpql_parserParser.TermSetContext ctx);
	/**
	 * Enter a parse tree produced by {@link nlpql_parserParser#obj}.
	 * @param ctx the parse tree
	 */
	void enterObj(nlpql_parserParser.ObjContext ctx);
	/**
	 * Exit a parse tree produced by {@link nlpql_parserParser#obj}.
	 * @param ctx the parse tree
	 */
	void exitObj(nlpql_parserParser.ObjContext ctx);
	/**
	 * Enter a parse tree produced by {@link nlpql_parserParser#pair}.
	 * @param ctx the parse tree
	 */
	void enterPair(nlpql_parserParser.PairContext ctx);
	/**
	 * Exit a parse tree produced by {@link nlpql_parserParser#pair}.
	 * @param ctx the parse tree
	 */
	void exitPair(nlpql_parserParser.PairContext ctx);
	/**
	 * Enter a parse tree produced by {@link nlpql_parserParser#array}.
	 * @param ctx the parse tree
	 */
	void enterArray(nlpql_parserParser.ArrayContext ctx);
	/**
	 * Exit a parse tree produced by {@link nlpql_parserParser#array}.
	 * @param ctx the parse tree
	 */
	void exitArray(nlpql_parserParser.ArrayContext ctx);
	/**
	 * Enter a parse tree produced by {@link nlpql_parserParser#value}.
	 * @param ctx the parse tree
	 */
	void enterValue(nlpql_parserParser.ValueContext ctx);
	/**
	 * Exit a parse tree produced by {@link nlpql_parserParser#value}.
	 * @param ctx the parse tree
	 */
	void exitValue(nlpql_parserParser.ValueContext ctx);
}