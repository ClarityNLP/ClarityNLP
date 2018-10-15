#!/usr/bin/env python3
"""



OVERVIEW:



The code in this module evaluates mathematical expressions that appear in NLPQL
'where' statements. Each statement is comprised of one or more expressions that
evaluate to a Boolean result. The expressions can be linked by comparison or
logical operators, and they can be parenthesized in the usual way to enforce
precedence or evaluation order. Some examples:

    not (A or B)
    (A or B or C) and D
    (x >= 5 and z <= 20) or (x >= 45 and y < 55) and (x > Z)
    (A / 2) ^ 3 < D * E * F * G * H
    etc.

The expression is assumed to have already been validated by the NLPQL parser,
which means that parentheses are balanced, the operators and variables are
known, and that the statement obeys valid mathematical syntax.

This module converts the expression to a set of MongoDB aggregation commands
and executes the command against a MongoDB collection. The document ids of all
documents satisfying the expression are returned to the caller in a list.



USAGE:



There is a single exported function called 'run' having this signature:


    run(mongo_collection_obj, infix_expr)


The 'mongo_collection_obj' argument is a pymongo object representing the
desired collection. This object can be created externally to this module as
follows:

    mongo_client_obj     = pymongo.MongoClient(mongo_host, mongo_port)
    mongo_db_obj         = mongo_client_obj[db_name]
    mongo_collection_obj = mongo_db_obj[collection_name]

The collection object is created externally to avoid the penalty of recreation
for each expression evaluation.

The 'infix_expr' argument is an infix string with whitespace separating
operators and operands. The expressions above are valid input, as is this:

    'D > A + (B * C)'

This next expression is invalid, since the '*' operator has no whitespace 
surrounding it:

    'D > A + (B*C)'

No assumptions are made about spaces separating parentheses from the operators
and operands.  So any of these forms are acceptable:

    'D > A + ( B * C )'
    'D > A + (B * C )'
    'D > A + ( B * C)'


The 'run' function returns a list of MongoDB document ids (the _id field) for
all documents that satisfy the expression.

Given a list of document IDs, the full documents can be retrieved from the
database with this query:

    cursor = collection.find({'_id' : {'$in' : doc_id_list}})



TESTING:



Run the self-tests from the command line as follows:

    python3 ./mongo_eval.py --selftest

No output should be generated if all tests pass.

The command line interface also accepts expressions and prints the associated
MongoDB aggregation command to stdout.  For instance, the command

    python3 ./mongo_eval.py --expression  'D > A + (B * C)'

generates this output:

Expression: D > A + (B * C)
   Postfix: ['D', 'A', 'B', 'C', '*', '+', '>']
   Command: 
{
    "$project": {
        "value": {
            "$gt": [
                "$D",
                {
                    "$add": [
                        "$A",
                        {
                            "$multiply": [
                                "$B",
                                "$C"
                            ]
                        }
                    ]
                }
            ]
        }
    }
}


Help for the command line interface can be obtained via this command:

    python3 ./mongo_eval --help

Extensive debugging info can be generated with the --debug option.



LIMITATIONS:


Currently only mathematical operations are supported. Database operations
involving syntax such as 'predicate IS NOT? NULL',
'predicate NOT? LIKE predicate (STRING)?' are not yet supported.



"""

import re
import ast
import sys
import json
import optparse
from pymongo import MongoClient
from collections import OrderedDict

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

_MODULE_NAME = 'mongo_eval.py'

# set to True to enable debug output
_TRACE = True

# operators in an NLPQL 'where' expression
_str_op = r'\A(==|!=|<=|>=|and|or|not|[-+/*%\^<>])\Z'
_regex_operator = re.compile(_str_op, re.IGNORECASE)

# quoted string literal
_str_string_literal = r'\A[\'\"][^\'\"]+[\'\"]\Z'
_regex_string_literal = re.compile(_str_string_literal, re.IGNORECASE)

# NLPQL numeric literal operand
_str_numeric_literal = r'\A[-+]?(\d+\.\d+|\.\d+|\d+)\Z'
_regex_numeric_literal = re.compile(_str_numeric_literal)

_str_identifier = r'[a-zA-Z$_][a-zA-Z$_0-9]*'
_regex_identifier = re.compile(_str_identifier, re.IGNORECASE)

_str_feature_and_value = r'(?P<nlpql_feature>' + _str_identifier + r')' +\
                         r'\.' +\
                         r'(?P<value>' + _str_identifier + r')'
_regex_feature_and_value = re.compile(_str_feature_and_value, re.IGNORECASE)

# operator precedence, matches python's rules
_PRECEDENCE_MAP = {
    '(':0,
    ')':0,
    'or':1,
    'and':2,
    'not':3,
    '<':4,
    '<=':4,
    '>':4,
    '>=':4,
    '!=':4,
    '==':4,
    '+':9,
    '-':9,
    '*':10,
    '/':10,
    '%':10,
    '^':12,
}

# unary operators
_UNITARY_OPS = ['not']

# operators with right-to-left associativity
_R_TO_L_OPS = ['^'] # exponentiation

# convert from operator symbol to MongoDB aggregation command
# (the unary operator 'not' is handled separately)
_MONGO_OPS = {
    'or':'$or',
    'and':'$and',
    '==':'$eq',
    '!=':'$ne',
    '>':'$gt',
    '<':'$lt',
    '>=':'$gte',
    '<=':'$lte',
    '+':'$add',
    '-':'$subtract',
    '*':'$multiply',
    '/':'$divide',
    '%':'$mod',
    '^':'$pow',
}

_LEFT_PARENS     = '('
_RIGHT_PARENS    = ')'
_EMPTY_JSON      = '[]'
_EMPTY_LIST      = []
_UNKNOWN         = 'UNKNOWN'
_OPERATOR        = 'OPERATOR'
_IDENTIFIER      = 'IDENTIFIER'
_VARIABLE        = 'VARIABLE'
_NUMERIC_LITERAL = 'NUMERIC_LITERAL'
_EXPR_MATH       = 'MATH'
_EXPR_LOGIC      = 'LOGIC'


###############################################################################
def _is_pure_mathematical_expr(infix_tokens):
    """
    Return a Boolean result indicating whether the given infix expression
    is a pure mathematical expression.

    Pure mathematical expressions consist entirely of terms of the form:

            nlpql_feature.value
            operator
            numeric_literal

    These expressions involve a single nlpql_feature, so that all variables
    can be found in the same 'row' of the intermediate result (mongo document).
    The condition of being all in the same row means that no joins are needed
    to evaluate the final result.

    """

    nlpql_feature_set = set()
    
    for token in infix_tokens:
        if _LEFT_PARENS == token or _RIGHT_PARENS == token:
            continue
        match = _regex_feature_and_value.match(token)
        if match:
            nlpql_feature = match.group('nlpql_feature')
            nlpql_feature_set.add(nlpql_feature)
            continue
        match = _regex_operator.match(token)
        if match:
            continue
        match = _regex_numeric_literal.match(token)
        if match:
            continue

        # if here, not a pure mathematical expression
        return _EMPTY_LIST

    if 1 == len(nlpql_feature_set):
        # return new tokens with the nlpql_feature prepended and stripped
        # from the individual tokens
        new_infix_tokens = []
        new_infix_tokens.append('(')
        new_infix_tokens.append('nlpql_feature')
        new_infix_tokens.append('==')
        new_infix_tokens.append('{0}'.format(nlpql_feature_set.pop()))
        new_infix_tokens.append(')')
        new_infix_tokens.append('and')
        new_infix_tokens.append('(')
        for token in infix_tokens:
            match = _regex_feature_and_value.match(token)
            if match:
                value = match.group('value')
                new_infix_tokens.append(value)
            else:
                new_infix_tokens.append(token)
        new_infix_tokens.append(')')
        return new_infix_tokens
    else:
        return EMPTY_LIST
    

###############################################################################
def _is_logic_expr(infix_tokens):
    """
    Return a Boolean result indicating whether the given infix expression
    is a pure logic expression. 

    Pure logic expressions consist entirely of terms of the form:

        identifier
        n-way 'and'
        n-way 'or'
        expressions involving 'not' TBD

    These expressions do NOT involve numeric literals or terms of the form
    nlpql_feature.value.

    These expressions involve multiple nlpql_features, so that they span
    multiple 'rows' of the intermediate result file.

    """

    operator_set = set()
    
    for token in infix_tokens:
        if _LEFT_PARENS == token or _RIGHT_PARENS == token:
            continue
        match = _regex_operator.match(token)
        if match:
            op_text = match.group()
            if 'and' == op_text or 'or' == op_text: # #or 'not' == op_text:
                operator_set.add(op_text)
                continue
        match = _regex_identifier.match(token)
        if match:
            continue

        # if here, not a pure logic expression
        return _EMPTY_LIST

    if 1 == len(operator_set):
        # rewrite for Mongo evaluation
        new_infix_tokens = []
        for token in infix_tokens:
            match = _regex_operator.match(token)
            if match:
                # explictly match operators (and, or, and not could be confused
                # with identifiers)
                new_infix_tokens.append(token)
                continue
            match = _regex_identifier.match(token)
            if match:
                new_infix_tokens.append('(')
                new_infix_tokens.append('nlpql_feature')
                new_infix_tokens.append('==')
                new_infix_tokens.append(token)
                new_infix_tokens.append(')')
            else:
                new_infix_tokens.append(token)
        return new_infix_tokens
    else:
        return _EMPTY_LIST

    
###############################################################################
def _get_token_type(token):
    """
    Test the form of the token and return whether it is a numeric literal,
    operator, etc.

    """

    match = _regex_feature_and_value.match(token)
    if match:
        return _VARIABLE
    match = _regex_numeric_literal.match(token)
    if match:
        return _NUMERIC_LITERAL
    match = _regex_operator.match(token)
    if match:
        return _OPERATOR
    match = _regex_identifier.match(token)
    if match:
        return _IDENTIFIER
    
    return UNKNOWN


###############################################################################
def _tokenize(expr):
    """
    Convert an infix expression of the form A OP1 B OP2 C ... into 
    individual tokens for the operands and operators. The expression is assumed
    to have been already parsed by ANTLR, so parens are assumed to be balanced
    and the operators and operands are assumed to be separated by whitespace.
    Parentheses may also be included in the expression and are not necessarily
    assumed to be separated by whitespace.
    """

    # split on whitespace
    tokens1 = re.split(r'[\s]+', expr)
    
    # separate any parentheses into their own tokens
    tokens1 = [t.strip() for t in tokens1]
    tokens = []
    for token in tokens1:
        t = token

        # tokenize leading parens, if any
        while t.startswith(_LEFT_PARENS):
            tokens.append(_LEFT_PARENS)
            t = t[1:]

        # nothing left if token was only left parens
        if 0 == len(t):
            continue

        # tokenize trailing parens, if any
        pos = t.find(_RIGHT_PARENS)
        if -1 != pos:
            before = t[:pos]
            if len(before) > 0:
                tokens.append(before)
            tokens.append(_RIGHT_PARENS)
            t = t[pos+1:]
            parens_count = len(t)
            for i in range(parens_count):
                assert _RIGHT_PARENS == t[i]
                tokens.append(_RIGHT_PARENS)
                t = t[1:]
        
        if len(t) > 0:
            tokens.append(t)

    if _TRACE: print('Tokenization: {0}'.format(tokens))
    return tokens


###############################################################################
def _is_operator(token):
    """
    Return True if token is a valid NLPQL operator, False if not.
    """

    matchobj = _regex_operator.match(token)
    return matchobj is not None


###############################################################################
def _is_operand(token):
    """
    Return True if token is an operand, False if not.
    """

    return (token != _LEFT_PARENS)  and   \
           (token != _RIGHT_PARENS) and   \
           (not _is_operator(token))
    
    
###############################################################################
def _is_numeric_literal(token):
    """
    Return True if token is a valid NLPQL numeric literal, False if not.
    """

    matchobj = _regex_numeric_literal.match(token)
    return matchobj is not None


###############################################################################
def _is_string_literal(token):
    """
    Return True if token is a valid string literal, False if not.
    """

    matchobj = _regex_string_literal.match(token)
    return matchobj is not None


###############################################################################
def _precedence(operator_token):
    """
    Return the numeric precedence value of the given operator token.
    """

    if _TRACE:
        print('\tsearching for operator token ->' \
              '{0}<- in precedence map'.format(operator_token))
    assert operator_token in _PRECEDENCE_MAP
    return _PRECEDENCE_MAP[operator_token]
    

###############################################################################
def _print_status(operator_stack, postfix_expr):
    """
    Print current state to stdout. Used for debugging.
    """

    print('\tSTATUS: ')
    print('\t\toperator_stack: {0}'.format(operator_stack))
    print('\t\t       postfix: {0}'.format(postfix_expr))


###############################################################################
def _infix_to_postfix(infix_tokens):
    """
    Convert an infix expression of the form A OP1 B OP2 C ... into the
    equivalent postfix form. Parentheses may also be present and are assumed
    to be balanced. Operators and operands are assumed to be separated by
    whitespace. No assumptions are made about spaces between parentheses and
    either operands or operators.

    Returns a list of token strings in postfix order. Parentheses are
    separated into individual tokens.

    Example:

    The infix expression

       'D > A + (B * C)'

    gets converted to this list of token strings in postfix form:

       ['D', 'A', 'B', 'C', '*', '+', '>']

    """

    postfix_expr = []
    operator_stack = []

    for token in infix_tokens:
        if _is_operand(token):
            # operands are accepted in order of occurrence
            postfix_expr.append(token)
            if _TRACE: print("\tfound operand '{0}'".format(token))
        else:
            token = token.lower()
            if _TRACE: print("\tfound operator '{0}'".format(token))
            if token == _RIGHT_PARENS:
                # pop all operators back to and including the left parens
                # push all onto the postfix expression excluding parens
                assert len(operator_stack) > 0
                token = operator_stack.pop()
                while token != _LEFT_PARENS:
                    postfix_expr.append(token)
                    token = operator_stack.pop()
            elif 0 == len(operator_stack) or token == _LEFT_PARENS:
                # new scope, so just accept operator
                operator_stack.append(token)
            else:
                # need to check operator precedence to determine action
                finished = False
                while not finished:
                    finished = True
                    stacktop = operator_stack[-1]
                    p1 = _precedence(token)
                    p2 = _precedence(stacktop)
                    if p1 > p2:
                        # accept higher precedence operator
                        if _TRACE:
                            print('\t{0} precedence gt {1}'.format(token, stacktop))
                        operator_stack.append(token)
                    elif p1 == p2:
                        # equal precedence, so check associativity
                        if _TRACE:
                            print('\t{0} precedence eq to {1}'.format(token, stacktop))
                        if token in _R_TO_L_OPS:
                            # right-to-left associativity, push new operand
                            operator_stack.append(token)
                        else:
                            # left-to-right associativity
                            # pop stacktop, append to postfix, push new operand
                            stacktop = operator_stack.pop()
                            postfix_expr.append(stacktop)
                            operator_stack.append(token)
                    else:
                        # lower precedence, so pop stacktop and try again
                        if _TRACE:
                            print('\t{0} precedence lt {1}'.format(token, stacktop))
                        stacktop = operator_stack.pop()
                        postfix_expr.append(stacktop)
                        if len(operator_stack) > 0:
                            finished = False
                        else:
                            # shortcut for empty stack
                            operator_stack.append(token)
                            
                    if _TRACE: _print_status(operator_stack, postfix_expr)
                            
        if _TRACE: _print_status(operator_stack, postfix_expr)

    # pop all remaining operators and append to postfix expression
    while operator_stack:
        token = operator_stack.pop()
        if token == _LEFT_PARENS or token == _RIGHT_PARENS:
            continue
        else:
            postfix_expr.append(token)

    if _TRACE: print('Postfix: {0}'.format(postfix_expr))
    return postfix_expr


###############################################################################
def _format_operand(operand):
    """
    Construct the appropriate MongoDB syntax for an operand in an aggregation
    clause. Compound operators need to be surrounded by curly brackets, 
    numeric literals are unchanged, and variables need a '$' prepended.
    """

    if ':' in operand:
        # surround expressions with curly brackets
        operand = '{{{0}}}'.format(operand)
    elif _is_numeric_literal(operand):
        pass
    elif _is_string_literal(operand):
        pass
    else:
        # variable name, so prepend '$'
        operand = '"${0}"'.format(operand)
        
    return operand


###############################################################################
def _mongo_format(operator, op1, op2=None):
    """
    Format a MongoDB aggregation expression for an operator and two operands.
    """
    
    if 'not' == operator:
        template = '"$not" : [{0}]'
    else:
        opstring = '"{0}"'.format(_MONGO_OPS[operator])
        template = opstring + ' : [{0}, {1}]'
        
    op1 = _format_operand(op1)
    
    if op2 is None:
        result = template.format(op1)
    else:
        op2 = _format_operand(op2)
        result = template.format(op1, op2)

    return result
    

###############################################################################
def _to_mongo_command(postfix_tokens, match_filters: dict, expr_type):
    """
    Convert a tokenized postfix expression into a form for execution by
    the MongoDB aggregation engine. See chapter 7 of 'MongoDB: The Definitive
    Guide' 2nd ed., by K. Chodorow for an introduction to Mongo aggregation.

    The 'tokens' argument is a list of strings representing a postfix
    expression.

    The conversion can be accomplished by 'evaluating' the postfix expression
    and generating the appropriate MongoDB commands. The result is a JSON
    string.
    """

    PROJECT_PREAMBLE  = '{ "$project" : { "value" : {'
    PROJECT_POSTAMBLE = '}}}'

    MATCH_PREAMBLE  = '{ "$match" : {'
    MATCH_POSTAMBLE = '}}'

    stack = list()
    mongo_commands = list()

    # place job_id filter first (along with any others), to (hopefully) reduce
    # the workload for the evaluator
    if match_filters:
        match_string = ''
        for k in match_filters.keys():
            if len(match_string) > 0:
                match_string = match_string + ", "
            val = str(match_filters[k])
            if type(match_filters[k]) == str:
                val = '"' + val + '"'
            match_string = match_string + '"' + k + '":' + val
        mongo_commands.append(MATCH_PREAMBLE + match_string + MATCH_POSTAMBLE)

    if _EXPR_MATH == expr_type:
        
        for token in postfix_tokens:
            if not _is_operator(token):
                stack.append(token)
            else:
                if token in _UNITARY_OPS:
                    op = stack.pop()
                    result = _mongo_format(token, op)
                else:
                    op2 = stack.pop()
                    op1 = stack.pop()
                    result = _mongo_format(token, op1, op2)
                stack.append(result)

        # only a single element should remain on the stack
        if 1 == len(stack):
            mongo_commands.append(PROJECT_PREAMBLE + stack[0] + PROJECT_POSTAMBLE)
        else:
            err_msg = 'mongo_eval: invalid expression: {0}'.format(postfix_tokens)
            print(err_msg)
            mongo_commands.append(_EMPTY_JSON)

    elif _EXPR_LOGIC == expr_type:
        # TBD
        pass
            
    return mongo_commands


###############################################################################
def _mongo_evaluate(json_commands, mongo_collection_obj):
    """
    Execute the aggregation JSON command string and return a list of _ids of 
    all documents that satisfy the query.
    """
    
    if len(json_commands) == 0:
        return []

    # convert the json_command string to an object by evaluating it and
    # instantiating an OrderedDict (need to maintain argument order)
    pipeline_obj = [OrderedDict(ast.literal_eval(j)) for j in json_commands]
    cursor = mongo_collection_obj.aggregate(pipeline_obj)
            
    # keep all doc ids for which the aggregation result is True
    doc_ids = [doc['_id'] for doc in cursor if doc['value']]

    return doc_ids    


###############################################################################
def is_mongo_computable(infix_expr):
    """
    Return a Boolean result indicating whether MongoDB aggregation can evaluate
    the given infix expression. The infix expression is assumed to consist of
    terms separated by whitespace. This expression has been validated by the
    NLPQL parser, so all parens are balanced and it conforms to proper NLPQL
    syntax.
    """

    infix_tokens   = _tokenize(infix_expr)
    #postfix_tokens = _infix_to_postfix(infix_tokens)

    # # symbolically evaluate the postfix expression
    # stack = []
    # for token in postfix_tokens:
    #     if not _is_operator(token):
    #         token_type = _get_token_type(token)
    #         stack.append(token_type)
    #     else:
    #         if token in _UNITARY_OPS:
    #             op = stack.pop()
    #             result = _symbolic_evaluate(token, op)
    #         else:
    #             op2 = stack.pop()
    #             op1 = stack.pop()
    #             result = _symbolic_evaluate(token, op1, op2)
    #         stack.append(result)

    if _TRACE:
        print('called _is_mongo_computable: ')
    
    new_infix_tokens = _is_pure_mathematical_expr(infix_tokens)
    if len(new_infix_tokens) > 0:
        new_infix_tokens.append(_EXPR_MATH)
        if _TRACE:
            print('\tREWRITTEN MATH EXPR: {0}'.format(new_infix_tokens))
        return new_infix_tokens

    new_infix_tokens = _is_logic_expr(infix_tokens)
    if len(new_infix_tokens) > 0:
        new_infix_tokens.append(_EXPR_LOGIC)
        if _TRACE:
            print('\tREWRITTEN LOGIC EXPR: {0}'.format(new_infix_tokens))
        return new_infix_tokens
    
    # some others that can be evaluated:
    #     isolated N-way provider assertion AND
    #     isolated N-way provider assertion OR
    #     the above with NOT?
    #     N-way AND provider assertion OR'd with pure_math expression(s)
    #     N-way OR  provider assertion OR'd with pure_math expression(s)
    
    return _EMPTY_LIST


###############################################################################
def run(mongo_collection_obj, infix_expr, match_filters: dict=None):
    """
    Evaluate the given infix expression, generate a MongoDB aggregation
    command from it, execute the command against the specified collection,
    and return a list of _ids for all documents satisfying the expression.

    The infix_expr is a string that is assumed to have survived the NLPQL
    parsing process, so the syntax is assumed to be correct.

    Also assumed is that whitespace separates operators from operands.
    No assumption is made about whitespace and parentheses.

    Create the mongo_collection_obj external to this function as follows:

        mongo_client_obj     = MongoClient(mongo_host, mongo_port)
        mongo_db_obj         = mongo_client_obj[db_name]
        mongo_collection_obj = mongo_db_obj[collection_name]

    """

    if match_filters is None:
        # --selftest path
        match_filters = dict()
        infix_tokens = _tokenize(infix_expr)
        expr_type = _EXPR_MATH

    else:
        # tokenize the input expression string and add nlpql_feature filters
        if str == type(infix_expr):
            infix_tokens = is_mongo_computable(infix_expr)
            if 0 == len(infix_tokens):
                return []
        else:
            assert list == type(infix_expr)
            infix_tokens = infix_expr

        assert len(infix_tokens) > 0
        assert _EXPR_MATH == infix_tokens[-1] or _EXPR_LOGIC == infix_tokens[-1]

        # strip the expression type token
        expr_type = infix_tokens[-1]
        infix_tokens = infix_tokens[:-1]
    
    postfix_tokens = _infix_to_postfix(infix_tokens)
    mongo_commands = _to_mongo_command(postfix_tokens, match_filters, expr_type)
    if _TRACE: print('command: {0}'.format(mongo_commands))
    doc_ids = _mongo_evaluate(mongo_commands, mongo_collection_obj)

    return doc_ids


###############################################################################
def _run_tests():

    COLLECTION_NAME = 'eval_test'
    
    variables = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    data = []
    for i in range(1,21):
        values = [(i+j) for j in range(0, len(variables))]
        data.append({item[0]:item[1] for item in list(zip(variables, values))})

    if _TRACE:
        print('DATA: ')
        for elem in data:
            print(elem)

    TEST_EXPRESSIONS = [
        # operators and operands must be separated by whitespace
        'not (A >= 8)',
        'B + D * F < 400',
        'not ( 0 == C % 5 ) and not ( 0 == D % 3)',
        '(A >= 5 and D <= 20) or (F >= 23 and H <= 27 and G == 25)',
        '5 * H >= A ^ 2',
        'E % 15 < 10',
        'A == 19 and B == 20 and C == 21 or (E < 15 and H > 10 and (G >= 11 and G <= 14))',
        'B != 10 and C != 12 and D != 13',
        'A > 4 and B < 16 and C > 7 and D < 16',
        '2 * H - 3 == F + G',
        'A ^ (D % B) < 2 * (H + D)',
        'not (A < 5 or B > 10 and C < 15 or D > 20) or G == 22 or F == 25 and not H == 8',
        '(((A * B) - (2 * C)) > (1 * H) )',
        '(A / 2) ^ 3 ^ 2  < D * E * F * G * H',
    ]
    
    # connect to the local mongo instance
    mongo_client_obj = MongoClient()

    # use the 'test' database
    mongo_db_obj = mongo_client_obj['test']

    mongo_collection_obj = mongo_db_obj[COLLECTION_NAME]
    
    # insert the data
    mongo_db_obj.drop_collection(COLLECTION_NAME)
    result = mongo_collection_obj.insert_many(data)

    # get all docs for result checking
    cursor = mongo_collection_obj.find()

    # run the tests
    for expr in TEST_EXPRESSIONS:
        if _TRACE: print('expression: {0}'.format(expr))

        # no match filters needed for math testing
        doc_ids = run(mongo_collection_obj, expr)
        
        if _TRACE: print('results: ')

        # extract variable values from each doc, substitute, and evaluate
        expr_save = expr
        for doc in cursor:
            if _TRACE: print('\t{0}'.format(doc))

            # restore the original expression
            expr = expr_save

            # substitute values of each variable occurring in expr
            for var in variables:
                if var in expr:
                    val = doc[var]
                    expr = expr.replace(var, str(val))

            # convert '^' to python '**' operator
            if '^' in expr:
                expr = expr.replace('^', '**')
                
            if _TRACE: print('\tevaluation: {0}'.format(expr))
            result = eval(expr)

            if doc['_id'] in doc_ids:
                if _TRACE: print('\t\tTRUE')
                assert result
            else:
                if _TRACE: print('\t\tFALSE')
                assert not result
        cursor.rewind()
    
    mongo_db_obj.drop_collection(COLLECTION_NAME)


    # need to handle this:
    # define final baseAfibCases:
    #     where patientsWithAfibTerms NOT transplantPatients;

    # assign pure math results to separate variables
    # final expression must either be:
    #     logical ops between existing nlpql_features
    #     pure math expression
    
    INFIX_EXPRESSIONS = [
        'Temperature.value >= 100.4',
        'mm.dimension_X >= 5 or mm.dimension_Y >= 5 or mm.dimension_Z >= 5',
        'hasFever or hasSepsisSymptoms',
        #'patientsWithAfibTerms not transplantPatients',
        'A and B and C and D'
    ]

    for infix_expr in INFIX_EXPRESSIONS:
        print('expr: ' + infix_expr)
        assert is_mongo_computable(infix_expr)
    

###############################################################################
def _get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
def _show_help():
    print(_get_version())
    print("""
    USAGE: python3 ./{0} -e <quoted_string> [-dhvz]

    OPTIONS:

        -e, --expression     <quoted string>     Expression to evaluate.

            Operators and operands must be separated by whitespace. 
            Parentheses do not have to be separated by whitespace from the
            nearest operator or operand.

            Examples:

                '(A or B) and C'
                '(x >= 5 and z <= 20) or (x >= 45 and y < 55)'

    FLAGS:

        -d, --debug          Enable debug output.
        -h, --help           Print this information and exit.
        -v, --version        Print version information and exit.
        -z, --selftest       Run self-tests and exit.

    """.format(_MODULE_NAME))
    

###############################################################################
if __name__ == '__main__':

    optparser = optparse.OptionParser(add_help_option=False)
    optparser.add_option('-e', '--expression', action='store',
                         dest='expression')
    optparser.add_option('-v', '--version', action='store_true',
                         dest='get_version')
    optparser.add_option('-d', '--debug', action='store_true',
                         dest='debug', default=False)
    optparser.add_option('-h', '--help', action='store_true',
                         dest='show_help', default=False)
    optparser.add_option('-z', '--selftest', action='store_true',
                         dest='selftest', default=False)

    opts, other = optparser.parse_args(sys.argv)

    if 1 == len(sys.argv) or opts.show_help:
        _show_help()
        sys.exit(0)

    if opts.get_version:
        print(_get_version())
        sys.exit(0)

    if opts.debug:
        _TRACE = True

    if opts.selftest:
        _run_tests()
        sys.exit(0)

    if not opts.expression:
        print('An expression must be specified on the command line.')
        sys.exit(-1)
        
    expr = opts.expression
        
    print('Expression: {0}'.format(expr))
    postfix_expr = _infix_to_postfix(expr)
    print('   Postfix: {0}'.format(postfix_expr))
    json_result = _to_mongo_command(postfix_expr, {})
    if _EMPTY_JSON != json_result:
        json_data = json.loads(json_result)
        print('   Command: ')
        print(json.dumps(json_data, indent=4))

