#!/usr/bin/env python3
"""
A parser for NLPQL expressions. An NLPQL expression is everything in an NLPQL
'define' statement after the 'where' and before the semicolon.

For instance, in the define statement:

    define hasSepsis:
        where hasFever AND hasSepsisSymptoms;

the expression is 'hasFever AND hasSepsisSymptoms'.
"""

from sly import Parser
from claritynlp_logging import log, ERROR, DEBUG


try:
    from data_access.expr_lexer import NlpqlExpressionLexer
except Exception as e:
    from expr_lexer import NlpqlExpressionLexer

# parser output format (either postfix or infix)
_POSTFIX = False

_TOKEN_MAP = {
    '+':'PLUS',
    '-':'MINUS',
    '*':'MULT',
    '/':'DIV',
    '%':'MOD',
    '^':'EXP',
    '>=':'GE',
    '>':'GT',
    '<=':'LE',
    '<':'LT',
    '==':'EQ',
    '!=':'NE',
    'or':'OR',
    'OR':'OR',
    'and':'AND',
    'AND':'AND',
    'not':'NOT',
    'NOT':'NOT'
}

NLPQL_EXPR_OPERATORS       = _TOKEN_MAP.keys()
NLPQL_EXPR_OPSTRINGS       = list(set(_TOKEN_MAP.values()))
NLPQL_EXPR_OPSTRINGS_LC    = [op.lower() for op in NLPQL_EXPR_OPSTRINGS]
NLPQL_EXPR_LOGIC_OPERATORS = ['or', 'OR', 'and', 'AND', 'not', 'NOT']

_TOKEN_NOT = 'NOT'
_TOKEN_AND = 'AND'
_TOKEN_ANDNOT = 'ANDNOT'


###############################################################################
def _get_logic_ops(infix_expr):
    """
    Return a list of all logic ops (OR, AND, NOT) in the given expression.
    """

    operator_set = set()
    tokens = infix_expr.split()
    for t in tokens:
        if t in NLPQL_EXPR_LOGIC_OPERATORS:
            operator_set.add(t.lower())

    return list(operator_set)


###############################################################################
def _strip_parens(expr):
    """
    Return the expression with any leading/trailing parens stripped.
    All tokens are separated by whitespace.
    """

    start = 0
    pos = expr.find('(')
    if -1 != pos:
        start += 2

    end = len(expr)
    pos = expr.rfind(')')
    if -1 != pos:
        end -= 2
    assert end > start
    return expr[start:end]


###############################################################################
class NlpqlExpressionParser(Parser):

    #debugfile = 'parser_debug.txt'
    
    # get tokens from lexer
    tokens = NlpqlExpressionLexer.tokens

    # precedence table of terminal symbols; precedence increases 
    precedence = (
#        ('left', MIXED),
        ('left', OR),
        ('left', AND),
        ('left', NOT),
        ('left', LT, LE, GT, GE, NE, EQ),
        ('left', PLUS, MINUS),
        ('left', MULT, DIV),
        ('left', MOD),
        ('right', EXP),
    )
    
    """

    nlpql_expr : nlpql_expr +  nlpql_expr
               | nlpql_expr -  nlpql_expr
               | nlpql_expr *  nlpql_expr
               | nlpql_expr /  nlpql_expr
               | nlpql_expr %  nlpql_expr
               | nlpql_expr ^  nlpql_expr
               | nlpql_expr >= nlpql_expr
               | nlpql_expr >  nlpql_expr
               | nlpql_expr <= nlpql_expr
               | nlpql_expr <  nlpql_expr
               | nlpql_expr == nlpql_expr
               | nlpql_expr != nlpql_expr
               | nlpql_expr OR nlpql_expr
               | nlpql_expr AND nlpql_expr
               | nlpql_expr NOT nlpql_expr  # equivalent to A AND NOT B
               | term

    term   : NUM_LITERAL
           | VARIABLE
           | NLPQL_FEATURE
           | LPAREN nlpql_expr RPAREN


    """
    
    @_('nlpql_expr PLUS   nlpql_expr',
       'nlpql_expr MINUS  nlpql_expr',
       'nlpql_expr MULT   nlpql_expr',
       'nlpql_expr DIV    nlpql_expr',
       'nlpql_expr MOD    nlpql_expr',
       'nlpql_expr EXP    nlpql_expr',
       'nlpql_expr GE     nlpql_expr',
       'nlpql_expr GT     nlpql_expr',
       'nlpql_expr LE     nlpql_expr',
       'nlpql_expr LT     nlpql_expr',
       'nlpql_expr EQ     nlpql_expr',
       'nlpql_expr NE     nlpql_expr'
    )
    def nlpql_expr(self, p):
        op_text = _TOKEN_MAP[ p[1] ]
        if _POSTFIX:
            return '{0} {1} {2}'.format(p[0], p[2], op_text)
        else:
            return '( {0} {1} {2} )'.format(p[0], op_text, p[2])

    @_('nlpql_expr OR     nlpql_expr',
       'nlpql_expr AND    nlpql_expr',
       'nlpql_expr NOT    nlpql_expr'
    )
    def nlpql_expr(self, p):
        p0 = p[0]
        p2 = p[2]
        op_text = _TOKEN_MAP[ p[1] ]
        if _TOKEN_NOT == op_text:
            op_text = _TOKEN_ANDNOT
        p0_is_logic = -1 == p0.find('.')
        p2_is_logic = -1 == p2.find('.')
                    
        # log('         p0: "{0}"'.format(p0))
        # log('p0_is_logic: {0}'.format(p0_is_logic))
        # log('         p2: "{0}"'.format(p2))
        # log('p2_is_logic: {0}'.format(p2_is_logic))

        if p0_is_logic and p2_is_logic:
            operators0 = _get_logic_ops(p0)
            operators2 = _get_logic_ops(p2)
            ok = False
            if 1 == len(operators0) + len(operators2):
                if 1 == len(operators0):
                    op = operators0[0]
                else:
                    op = operators2[0]
                ok = True
            elif 1 == len(operators0) and 1 == len(operators2) and operators0[0] == operators2[0]:
               op = operators0[0]
               ok = True
            if ok:
                op1 = p[1].lower()
                if op1 == op:
                    #log('*** COMBINATION POSSIBLE ***')
                    # strip parens from p0 and p2
                    p0 = _strip_parens(p0)
                    p2 = _strip_parens(p2)

        if _POSTFIX:
            if _TOKEN_ANDNOT == op_text:
                return '{0} {1} {2} {3}'.format(p0, p2, _TOKEN_NOT, _TOKEN_AND)
            else:
                return '{0} {1} {2}'.format(p0, p2, op_text)
        else:
            if _TOKEN_ANDNOT == op_text:
                return '( {0} {1} {2} {3} )'.format(p0, _TOKEN_AND, _TOKEN_NOT, p2)
            else:
                return '( {0} {1} {2} )'.format(p0, op_text, p2)
        
    @_('term')
    def nlpql_expr(self, p):
        return '{0}'.format(p.term)

    @_('NUM_LITERAL')
    def term(self, p):
        return '{0}'.format(p.NUM_LITERAL)

    @_('VARIABLE')
    def term(self, p):
        return '{0}'.format(p.VARIABLE)

    @_('NLPQL_FEATURE')
    def term(self, p):
        return '{0}'.format(p.NLPQL_FEATURE)
    
    @_('LPAREN nlpql_expr RPAREN')
    def term(self, p):
        return '{0}'.format(p.nlpql_expr)

    def error(self, p):
        msg = '{0}'.format(p)
        raise SyntaxError(msg)
        
