#!/usr/bin/env python3
"""
A basic lexer for non-nested CQL Tuples. Built with sly, a python version
of Lex and Yacc.

Github page for the sly project: https://github.com/dabeaz/sly
"""

import os
import re
import sys
from sly import Lexer, Parser
from collections import OrderedDict


###############################################################################
class TupleLexer(Lexer):

    # token names
    tokens = {
        TUPLE_HEADER, LBRACKET, RBRACKET, VARIABLE,
        QSTRING, PLUS, COMMA, COLON, #NUMBER
    }

    # ignorable characters
    ignore = ' \t'

    TUPLE_HEADER = r'(T|t)uple'
    
    # quoted string with either single or double quotes
    QSTRING = r'(' + r'"[^"]+"' + r')|(' + r"'[^']+'" + r')'
    
    # floating point and integer literals, also scientific notation
    #NUMBER = r'[-+]?(\d+\.\d*|\.\d+|\d+)([eE][-+]?\d+)?'
    
    # variables have the form feature.field
    VARIABLE = r'[a-zA-Z_][a-zA-Z0-9$_]*\.[a-zA-Z_][a-zA-Z0-9$_]*'    

    LBRACKET = r'\{'
    RBRACKET = r'\}'
    PLUS     = r'\+'
    COMMA    = r','
    COLON    = r':'

    # track line numbers
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print('Line {0}: Bad character {1}'.format(self.lineno, t.value[0]))
        self.index += 1


###############################################################################
class TupleParser(Parser):
    """

    Grammar for non-nested tuples:

        tuple: Tuple { statement_list }

        statement_list : statement COMMA statement_list
                       | statement

        statement : quoted_string COLON expr

        expr : expr PLUS expr
             | quoted_string
             | variable          # has the form a.b, such as Temperature.value
    
    """

    tokens = TupleLexer.tokens

    tuple_statements = []
    tuple_map = OrderedDict()

    @_('TUPLE_HEADER LBRACKET statement_list RBRACKET')
    def tuple(self, p):
        # keep only the statement list
        return p.statement_list
    
    @_('statement COMMA statement_list')
    def statement_list(self, p):
        return '{0} , {1}'.format(p[0], p[2])

    @_('statement')
    def statement_list(self, p):
        self.tuple_statements.append(p.statement)
        return '{0}'.format(p.statement)
    
    @_('QSTRING COLON expr')
    def statement(self, p):
        self.tuple_map[p.QSTRING] = p.expr
        return '{0} : {1}'.format(p.QSTRING, p.expr)

    @_('QSTRING')
    def expr(self, p):
        return '{0}'.format(p.QSTRING)

    @_('VARIABLE')
    def expr(self, p):
        return '{0}'.format(p.VARIABLE)

    @_('expr PLUS expr')
    def expr(self, p):
        # strip quotes, concatenate, restore quotes
        p_0 = re.sub(r'[\"]', '', p[0])
        p_0 = re.sub(r'[\']', '', p_0)
        p_2 = re.sub(r'[\"]', '', p[2])
        p_2 = re.sub(r'[\']', '', p_2)

        #print('p_0: {0}'.format(p_0))
        #print('p_2: {0}'.format(p_2))
        # string concatenation
        return '"{0}{1}"'.format(p_0, p_2)

        
###############################################################################
if __name__ == '__main__':

    EXPRESSIONS = [
        'Tuple { }',
        'WBC.value',
        '3.14159',
        '"this is a quoted string"',
        '"this, string, contains, commas"',
        '"key1" : "string value"',
        '"key2" : WBC.value',
        '"key3" : "this is the WBC value" + WBC.value',
        '"key4" : "str1" + WBC.value + "str2" + Temp.value',
    ]

    lexer = TupleLexer()
    for i, e in enumerate(EXPRESSIONS):
        print('[{0:3}]: {1}'.format(i, e))
        for tok in lexer.tokenize(e):
            print(tok)
        print()

    STATEMENTS = [
        """Tuple { 
               "key5" : "value5",
               "key6" : "value6",
               "key7" : "value7"
           }""",
        """Tuple { 
               "key8"  : "WBC value: " + WBC.value,
               "key9"  : Temperature.value + " " + "is the temp value",
               "key10" : "the WBC value: " + WBC.value + " " + "temp value: " + Temperature.value
           }""",
        """Tuple {
               "QuestionConcept": "22112145",
               "Question":"How large was was the prostatic mass?",
               "AnswerType": "String",
               "Answer" : ProstateVolumeMeasurement.dimension_X + " x " + 
                   ProstateVolumeMeasurement.dimension_Y + " x " + 
                   ProstateVolumeMeasurement.dimension_Z + " "   + 
                   ProstateVolumeMeasurement.units
            }"""
        
    ]

    parser = TupleParser()
    for i, s in enumerate(STATEMENTS):
        s = re.sub(r'\s+', ' ', s)
        print('STATEMENT: {0}'.format(s))
        try:
            result = parser.parse(lexer.tokenize(s))
            print('\t{0}'.format(result))
        except EOFError:
            break

    # print('TUPLE STATEMENTS: ')
    # for s in parser.tuple_statements:
    #     print(s)
        
    print('TUPLE MAP: ')
    for k,v in parser.tuple_map.items():
        print('{0} => {1}'.format(k, v))
