#!/usr/bin/env python3
"""
A basic lexer for NLPQL expressions.
"""

from sly import Lexer
from claritynlp_logging import log, ERROR, DEBUG


###############################################################################
class NlpqlExpressionLexer(Lexer):

    # token names
    tokens = {
        NUM_LITERAL, NLPQL_FEATURE, VARIABLE, LPAREN, RPAREN,
        PLUS, MINUS, MULT, DIV, EQ, NE, LE, LT, GE, GT, MOD, EXP,
        AND, OR, NOT
    }

    literals = { ';' }

    # ignorable characters
    ignore = ' \t'

    # floating point and integer literals, also scientific notation
    NUM_LITERAL = r'[-+]?(\d+\.\d*|\.\d+|\d+)([eE][-+]?\d+)?'

    LPAREN   = r'\('
    RPAREN   = r'\)'
    PLUS     = r'\+'
    MINUS    = r'-'
    MULT     = r'\*'
    DIV      = r'/'
    EQ       = r'=='
    NE       = r'!='
    LE       = r'<='
    LT       = r'<'
    GE       = r'>='
    GT       = r'>'
    MOD      = r'%'
    EXP      = r'\^'
    OR       = r'(or|OR)'
    AND      = r'(and|AND)'
    NOT      = r'(not|NOT)'

    # variables have the form nlpql_feature.field_name
    VARIABLE = r'[a-zA-Z_][a-zA-Z0-9$_]*\.[a-zA-Z_][a-zA-Z0-9$_]*'
    NLPQL_FEATURE = r'[a-zA-Z_][a-zA-Z0-9$_]*'
    
    def NUM_LITERAL(self, t):
        pos = t.value.find('.')
        if -1 != pos:
            # float
            t.value = float(t.value)
        else:
            t.value = int(t.value)
        return t

    # track line numbers
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        log('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        self.index += 1


###############################################################################
if __name__ == '__main__':

    EXPRESSIONS = [
        '42',
        '-42',
        '3.14',
        '3.',
        '.234',
        'nlpql',
        'nlpql.feature',
        'Temperature.value >= 100.4',
        'hasRigors OR hasTachycardia',
        'hasRigors NOT hasTachycardia',
        '(hasRigors AND hasTachycardia)',
        'Temperature.value % 3 ^ 2',
        '6.022e23',
        '6.626e-34',
        '6.67e-11',
    ]

    counter = 1
    lexer = NlpqlExpressionLexer()
    for e in EXPRESSIONS:
        log('[{0:3}]: {1}'.format(counter, e))
        for tok in lexer.tokenize(e):
            log(tok)
        log()
        counter += 1
