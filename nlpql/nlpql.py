import antlr4
if __name__ is not None and "." in __name__:
    from .nlpql_parserParser import *
    from .nlpql_lexer import *
else:
    from nlpql_parserParser import *
    from nlpql_lexer import *


def handle_expression(expr):
    for child in expr.getChildren():
        if type(child) == nlpql_parserParser.StatementContext:
            statement_members = child.getChildren()
            for stmt in statement_members:
                if not type(stmt) == antlr4.tree.Tree.TerminalNodeImpl:
                    print(type(stmt))
                    print(stmt)

    print("done with NLPQL expression")


def run_parser(nlpql_txt: str):
    lexer = nlpql_lexer(antlr4.InputStream(nlpql_txt))
    stream = antlr4.CommonTokenStream(lexer)
    parser = nlpql_parserParser(stream)
    tree = parser.validExpression()
    handle_expression(tree)


if __name__ == '__main__':
    with open('samples/simple.nlpql') as f:
        nlpql_txt = f.read()
        run_parser(nlpql_txt)
