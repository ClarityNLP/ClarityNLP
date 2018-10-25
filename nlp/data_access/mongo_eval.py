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
import subprocess
from pymongo import MongoClient
from collections import OrderedDict, namedtuple

if __name__ == '__main__':
    import mongo_logic_ops
else:
    from data_access import mongo_logic_ops

# results are returned as instances of this namedtuple type
MONGO_EVAL_FIELDS = [
    'operation',  # which operation was performed, see below
    'n',          # value of n for n-ary logic ops
    'doc_ids',    # list of all returned doc _id values
    'doc_groups'  # list of lists for joined docs
]
MongoEvalResult = namedtuple('MongoEvalResult', MONGO_EVAL_FIELDS)

# values for the 'mongo_op' field
MONGO_OP_MATH    = 'MATH'
MONGO_OP_AND     = 'AND'
MONGO_OP_OR      = 'OR'
MONGO_OP_SETDIFF = 'SETDIFF'
MONGO_OP_NOT     = 'NOT'
MONGO_OP_ERROR   = 'ERROR'

MONGO_EVAL_ERROR = MongoEvalResult(MONGO_OP_ERROR, 0, [], [])


# non-exported variables

_VERSION_MAJOR = 0
_VERSION_MINOR = 2

_MODULE_NAME = 'mongo_eval.py'

# set to True to enable debug output
_TRACE = False

# operators in an NLPQL 'where' expression
_str_op = r'\A(==|!=|<=|>=|and|or|not|[-+/*%\^<>=])\Z'
_regex_operator = re.compile(_str_op, re.IGNORECASE)

_str_embedded_op = r'(==|!=|<=|>=|[-+/*%\^<>=])'
_regex_embedded_op = re.compile(_str_embedded_op)

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
    '=':4,
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
    '=':'$eq',
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
_SINGLE_ROW_OP   = 'SINGLE_ROW_OP'
_MULTI_ROW_OP    = 'MULTI_ROW_OP'
_OPERATOR_AND    = 'and'
_OPERATOR_OR     = 'or'
_OPERATOR_NOT    = 'not'


###############################################################################
def _to_mongo_op(logic_operator, nlpql_feature_count):
    """
    Convert the logic operator to one of the predefined constants.
    """

    operator = logic_operator.lower()

    if _OPERATOR_AND == operator:
        op_id = MONGO_OP_AND
    elif _OPERATOR_OR == operator:
        op_id = MONGO_OP_OR
    elif _OPERATOR_NOT == operator:
        if 2 == nlpql_feature_count:
            op_id = MONGO_OP_SETDIFF
        else:
            op_id = MONGO_OP_NOT
    else:
        op_id = MONGO_OP_ERROR

    return op_id
        

###############################################################################
def _is_single_row_op(infix_tokens):
    """
    Return a Boolean result indicating whether the given infix expression
    can be evaluated as a "single-row" operation.

    Pure single-row operations consist entirely of terms of the form:

            nlpql_feature.value
            operator
            numeric_literal

    These expressions involve a single nlpql_feature, so that all variables
    can be found in the same 'row' (mongo document) of the intermediate
    results. The condition of being all in the same row means that no joins
    are needed to evaluate the expression.

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

        # if here, not a single-row operation
        return _EMPTY_LIST

    if 1 == len(nlpql_feature_set):
        # return new tokens with the nlpql_feature prepended and stripped
        # from the individual tokens
        new_infix_tokens = []
        new_infix_tokens.append('(')
        new_infix_tokens.append('nlpql_feature')
        new_infix_tokens.append('==')
        new_infix_tokens.append('"{0}"'.format(nlpql_feature_set.pop()))
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
def _is_multi_row_op(infix_tokens):
    """
    Return a Boolean result indicating whether the given infix expression
    is a "multi-row" operation.

    Multi-row operations consist entirely of terms of the form:

        identifier
        n-way 'and'
        n-way 'or'
        A not B
        not A

    These expressions do NOT involve numeric literals or terms of the form
    nlpql_feature.value.

    These expressions involve multiple nlpql_features, so that they span
    multiple 'rows' of the intermediate result file.

    """

    if _TRACE:
        print('_is_multi_row_op: testing {0}'.format(infix_tokens))

    operator_set = set()
    identifier_set = set()
    
    for token in infix_tokens:
        if _LEFT_PARENS == token or _RIGHT_PARENS == token:
            continue
        match = _regex_operator.match(token)
        if match:
            op_text = match.group().lower()
            if _OPERATOR_AND == op_text or _OPERATOR_OR == op_text or _OPERATOR_NOT == op_text:
                operator_set.add(op_text)
                continue
        match = _regex_identifier.match(token)
        if match:
            identifier_set.add(match.group())
            continue

        # if here, not a multi-row operation
        return _EMPTY_LIST

    if 1 == len(operator_set):
        operator = operator_set.pop()

        # n-way 'and', n-way 'or'
        if _OPERATOR_AND == operator or _OPERATOR_OR == operator:
            new_infix_tokens = [operator]
            new_infix_tokens.append(list(identifier_set))
            if _TRACE: print('\tfound n-way {0} expression'.format(operator))
            return new_infix_tokens

        # 'A not B'
        elif _OPERATOR_NOT == operator and 2 == len(identifier_set):
            new_infix_tokens = [operator]
            new_infix_tokens.append(list(identifier_set))
            if _TRACE: print('\tfound "A not B" expression')
            return new_infix_tokens

        # not A
        elif _OPERATOR_NOT == operator and 1 == len(identifier_set):
            new_infix_tokens = [operator]
            new_infix_tokens.append(list(identifier_set))
            if _TRACE: print('\tfound "not A" expression')
            return new_infix_tokens
        else:
            return _EMPTY_LIST
    else:
        return _EMPTY_LIST


###############################################################################
def _insert_whitespace(infix_expr):
    """
    Insert whitespace between all operands and operators. The infix expression
    already has whitespace surrounding the operators between data entities.
    """

    tokens = []

    data_entities = infix_expr.split()
    for de in data_entities:
        match = _regex_embedded_op.search(de)
        if match:
            start = match.start()
            end   = match.end()
            tokens.append( de[:start] )
            tokens.append( match.group() )
            tokens.append( de[end:] )
        else:
            tokens.append(de)

    return ' '.join(tokens)


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
def _filters_to_pipeline(pipeline, match_filters: dict):
    """
    """

    MATCH_PREAMBLE  = '{ "$match" : {'
    MATCH_POSTAMBLE = '}}'

    if match_filters:
        match_string = ''
        for k in match_filters.keys():
            if len(match_string) > 0:
                match_string = match_string + ", "
            val = str(match_filters[k])
            if type(match_filters[k]) == str:
                val = '"' + val + '"'
            match_string = match_string + '"' + k + '":' + val
        pipeline.append(MATCH_PREAMBLE + match_string + MATCH_POSTAMBLE)

    return pipeline


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
def _to_mongo_pipeline(postfix_tokens,
                       match_filters: dict,
                       expr_type,
                       join_field):
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

    stack = list()
    mongo_commands = list()

    # insert the filters into the aggregation pipeline
    mongo_commands = _filters_to_pipeline(mongo_commands, match_filters)

    if _SINGLE_ROW_OP == expr_type:
        # joins are not needed, can ignore join_field
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

    elif _MULTI_ROW_OP == expr_type:
        # either an n-way 'AND' or n-way 'OR' expression
        operator = postfix_tokens[-1]
        print('here is operator: {0}'.format(operator))
            
    return mongo_commands


###############################################################################
def _mongo_evaluate_single_row(json_commands, mongo_collection_obj):
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

    if _TRACE:
        print('called _is_mongo_computable: ')

    infix_expr = _insert_whitespace(infix_expr)
    infix_tokens = _tokenize(infix_expr)

    new_infix_tokens = _is_single_row_op(infix_tokens)
    if len(new_infix_tokens) > 0:
        new_infix_tokens.append(_SINGLE_ROW_OP)
        if _TRACE:
            print('\tREWRITTEN SINGLE-ROW OP: {0}'.format(new_infix_tokens))
        return new_infix_tokens

    new_infix_tokens = _is_multi_row_op(infix_tokens)
    if len(new_infix_tokens) > 0:
        new_infix_tokens.append(_MULTI_ROW_OP)
        if _TRACE:
            print('\tREWRITTEN MULTI_ROW_OP: {0}'.format(new_infix_tokens))
        return new_infix_tokens
    
    return _EMPTY_LIST


###############################################################################
def run(mongo_collection_obj,
        infix_str_or_tokens,       # string or token list to evaluate
        join_field = None,         # which field to join on for logic expr
        match_filters: dict=None): # initial filters for aggregation pipeline

    """
    Evaluate the given infix expression, generate a MongoDB aggregation
    command from it, execute the command against the specified collection,
    and return a MongoEvalResult namedtuple with the results.

    The infix_expr is a string that is assumed to have survived the NLPQL
    parsing process, so the syntax is assumed to be correct.

    Also assumed is that whitespace separates operators from operands.
    No assumption is made about whitespace and parentheses.

    Create the mongo_collection_obj external to this function as follows:

        mongo_client_obj     = MongoClient(mongo_host, mongo_port)
        mongo_db_obj         = mongo_client_obj[db_name]
        mongo_collection_obj = mongo_db_obj[collection_name]

    Results:

    For logical AND, there is an ntuple for each value of the join variable.
    The ntuple contains the documents that were joined on that particular value.
    The number of entries in each ntuple is n for an n-ary join.

    For logical OR, there is a variable number of ntuples depending on how many
    items were joined. Each ntuple can contain from 1 to n entries.

    For logical A NOT B, there is an ntuple containing a single doc for each
    value of the join variable in A but not in B.

    For logical NOT, there is a single ntuple containing all result documents.

    """

    if _TRACE:
        print('Called mongo_eval::run: ')
        print('\tinfix_str_or_tokens: {0}'.format(infix_str_or_tokens))
        print('\tmatch_filters: {0}'.format(match_filters))

    if match_filters is None:
        # --selftest path
        match_filters = dict()

    # tokenize the input expression string and add nlpql_feature filters
    if str == type(infix_str_or_tokens):
        tokens = is_mongo_computable(infix_str_or_tokens)
        if 0 == len(tokens):
            return MONGO_EVAL_ERROR
    else:
        assert list == type(infix_str_or_tokens)
        tokens = infix_str_or_tokens

    assert len(tokens) > 0
    assert _SINGLE_ROW_OP == tokens[-1] or _MULTI_ROW_OP == tokens[-1]

    # strip the expression type token
    expr_type = tokens[-1]
    tokens = tokens[:-1]

    if _TRACE:
        print('tokens before postfix in run: {0}'.format(tokens))

    if _SINGLE_ROW_OP == expr_type:
        postfix_tokens = _infix_to_postfix(tokens)
        mongo_pipeline = _to_mongo_pipeline(postfix_tokens,
                                            match_filters,
                                            expr_type,
                                            join_field)

        if _TRACE: print('mongo pipeline: {0}'.format(mongo_pipeline))
        doc_ids = _mongo_evaluate_single_row(mongo_pipeline, mongo_collection_obj)

        mongo_eval_result = MongoEvalResult(operation  = MONGO_OP_MATH,
                                            n          = 1,
                                            doc_ids    = doc_ids,
                                            doc_groups = [])

    else:
        # the operator and nlpql features are stored in the 'tokens' list
        operator           = tokens[0]
        nlpql_feature_list = tokens[1]
        feature_count      = len(nlpql_feature_list)

        mongo_pipeline = [
            {
                "$match" : {
                    "job_id" : match_filters['job_id']
                }
            }
        ]

        if _OPERATOR_AND == operator or \
           _OPERATOR_OR == operator  or \
           (_OPERATOR_NOT == operator and 2 == feature_count): 
            mongo_pipeline = mongo_logic_ops.logic_expr_a_b(mongo_pipeline,
                                                            operator,
                                                            join_field,
                                                            nlpql_feature_list)
        else:
            assert 1 == feature_count
            mongo_pipeline = mongo_logic_ops.logic_expr_not_a(mongo_pipeline,
                                                              nlpql_feature_list[0])

        if _TRACE: print('mongo pipeline: {0}'.format(mongo_pipeline))
        cursor = mongo_collection_obj.aggregate(mongo_pipeline)

        ids = []
        groups = []
        for agg_result in cursor:
            ntuple = agg_result['ntuple']
            groups.append(ntuple)
            for t in ntuple:
                ids.append(t['_id'])

        # convert operator to predefined constant
        mongo_op = _to_mongo_op(operator, len(nlpql_feature_list))
        mongo_eval_result = MongoEvalResult(operation  = mongo_op,
                                            n          = feature_count,
                                            doc_ids    = ids,
                                            doc_groups = groups)

        # print('mongo_eval: mongo_eval_result: ')
        # print(mongo_eval_result)
        # print()
                                            
    return mongo_eval_result


###############################################################################
def _run_test_pipeline(mongo_collection_obj, pipeline):
    """
    Run an aggregation pipeline for self-testing. Each aggregation result
    contains a single field called 'ntuple', which is an array of intermediate
    phenotype result documents.
    """

    ids = []
    groups = []

    cursor = mongo_collection_obj.aggregate(pipeline)

    for agg_result in cursor:
        #print('agg_result: {0}'.format(agg_result))
        ntuple = agg_result['ntuple']
        groups.append(ntuple)
        for t in ntuple:
            ids.append(t['_id'])

    # for g in groups:
    #     print('\tgroup size: {0}'.format(len(g)))
    #     for t in g:
    #         print('\t\t{0}'.format(t))
    # print()
            
    return (sorted(ids), groups)


###############################################################################
def _run_tests():

    # mongo needs to be running locally for this test, so check for it...
    ps_process = subprocess.run(['ps', '-ax'],
                                stdout=subprocess.PIPE,
                                universal_newlines=True)
    grep_process = subprocess.run(['grep', 'mongod'],
                                  input=ps_process.stdout,
                                  stdout=subprocess.PIPE,
                                  universal_newlines=True)
    if 0 == len(grep_process.stdout):
        print('mongo_eval: please start a local mongo server for this test...')
        return

    # a name that should be unique...
    COLLECTION_NAME = 'clarity_nlp_mongo_eval_test_!~!_001;;;'

    variables = ['nlpql_feature', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    data = []
    for i in range(0,21):
        values = [(i+j) for j in range(0, len(variables))]
        values[0] = 'T' # the nlpql_feature
        data.append({item[0]:item[1] for item in list(zip(variables, values))})

    # add a row where some data is missing
    data.append({item[0]:item[1] for item in [
        ('nlpql_feature', 'T'), ('A', None), ('B', 1), ('C', 2), ('D', 3),
        ('E', None), ('F', 1), ('G', 2), ('H', 5)
    ]})

    if _TRACE:
        print('DATA: ')
        for elem in data:
            print(elem)

    # data for testing single-row operations
    # operators and operands MUST be separated by whitespace
    TEST_EXPRESSIONS = [
        'not (T.A >= 8)',
        'T.B + T.D * T.F < 400',
        'not ( 0 == T.C % 5 ) and not ( 0 == T.D % 3)',
        '(T.A >= 5 and T.D <= 20) or (T.F >= 23 and T.H <= 27 and T.G == 25)',
        '5 * T.H >= T.A ^ 2',
        'T.E % 15 < 10',

        # spans two lines
        'T.A == 19 and T.B == 20 and T.C == 21 or '              \
        '(T.E < 15 and T.H > 10 and (T.G >= 11 and T.G <= 14))',

        'T.B != 10 and T.C != 12 and T.D != 13',
        'T.A > 4 and T.B < 16 and T.C > 7 and T.D < 16',
        '2 * T.H - 3 == T.F + T.G',
        'T.A ^ (T.D % T.B) < 2 * (T.H + T.D)',

        # spans two lines
        'not (T.A < 5 or T.B > 10 and T.C < 15 or T.D > 20) or ' \
        'T.G == 22 or T.F == 25 and not T.H == 8',

        '(((T.A * T.B) - (2 * T.C)) > (1 * T.H) )',
        '(T.A / 2) ^ 3 ^ 2  < T.D * T.E * T.F * T.G * T.H',
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

        # run the single-row operation using MongoDB aggregation
        mongo_eval_result = run(mongo_collection_obj, expr, 'report_id')
        
        if _TRACE: print('results: ')

        # now run the same expression using the Python evaluator
        expr_save = expr
        for doc in cursor:
            if _TRACE: print('\t{0}'.format(doc))

            # restore the original expression
            expr = expr_save

            # remove the 'T.' from each variable
            expr = re.sub(r'T\.', '', expr)

            # substitute values of each variable occurring in expr
            for var in variables:
                if var in expr:
                    val = doc[var]
                    expr = expr.replace(var, str(val))

            # convert '^' to python '**' operator
            if '^' in expr:
                expr = expr.replace('^', '**')

            success = True
            try:
                if _TRACE: print('\tevaluation: {0}'.format(expr))
                boolean_result = eval(expr)
            except TypeError:
                # will be thrown if any values are 'None'
                success = False
                if _TRACE: print('\t\tCOULD NOT EVALUATE')

            # compare MongoDB result and python result
            if success:
                if doc['_id'] in mongo_eval_result.doc_ids:
                    if _TRACE: print('\t\tTRUE')
                    assert boolean_result
                else:
                    if _TRACE: print('\t\tFALSE')
                    assert not boolean_result

        cursor.rewind()

    mongo_db_obj.drop_collection(COLLECTION_NAME)

    # data for testing multi-row operations
    data = [
        {'_id':1,  'nlpql_feature':'A', 'report_id':1, 'subject':1, 'sentence':'Hello1', 'start':1},
        {'_id':2,  'nlpql_feature':'A', 'report_id':2, 'subject':2, 'sentence':'Hello2', 'start':2},
        {'_id':3,  'nlpql_feature':'A', 'report_id':3, 'subject':3, 'sentence':'Hello3', 'start':3},
        {'_id':4,  'nlpql_feature':'A', 'report_id':4, 'subject':4, 'sentence':'Hello4', 'start':4},
        {'_id':5,  'nlpql_feature':'A', 'report_id':5, 'subject':5, 'sentence':'Hello5', 'start':5},

        {'_id':6,  'nlpql_feature':'B', 'report_id':6, 'subject':1, 'sentence':'Hello6', 'start':1},
        {'_id':7,  'nlpql_feature':'B', 'report_id':7, 'subject':2, 'sentence':'Hello7', 'start':2},
        {'_id':8,  'nlpql_feature':'B', 'report_id':8, 'subject':3, 'sentence':'Hello8', 'start':3},
        {'_id':9,  'nlpql_feature':'B', 'report_id':4, 'subject':4, 'sentence':'Hello4', 'start':4},
        {'_id':10, 'nlpql_feature':'B', 'report_id':5, 'subject':5, 'sentence':'Hello5', 'start':5},

        {'_id':11, 'nlpql_feature':'C', 'report_id':6, 'subject':1, 'sentence':'Hello6', 'start':1},
        {'_id':12, 'nlpql_feature':'C', 'report_id':7, 'subject':2, 'sentence':'Hello7', 'start':2},
        {'_id':13, 'nlpql_feature':'C', 'report_id':8, 'subject':3, 'sentence':'Hello8', 'start':3},

        {'_id':14, 'nlpql_feature':'D', 'report_id':6, 'subject':1, 'sentence':'Hello6', 'start':1},
        {'_id':15, 'nlpql_feature':'D', 'report_id':9, 'subject':2, 'sentence':'Hello9', 'start':2},
    ]

    mongo_collection_obj = mongo_db_obj[COLLECTION_NAME]
    mongo_db_obj.drop_collection(COLLECTION_NAME)
    result = mongo_collection_obj.insert_many(data)

    # logical AND between features A and B, document context
    pipeline = []
    pipeline = mongo_logic_ops.logic_expr_a_b(pipeline, 'and', 'report_id',
                                          ['A', 'B'])
    doc_ids, groups = _run_test_pipeline(mongo_collection_obj, pipeline)
    assert doc_ids == [4,5,9,10]

    # logical AND between features A and B, patient context
    pipeline = []
    pipeline = mongo_logic_ops.logic_expr_a_b(pipeline, 'and', 'subject',
                                          ['A', 'B'])
    doc_ids, groups = _run_test_pipeline(mongo_collection_obj, pipeline)
    #assert doc_ids == [1,2,3,4,5,6,7,8,9,10]
    assert doc_ids == [4,5,9,10]

    # logical AND between features C and D, document context
    pipeline = []
    pipeline = mongo_logic_ops.logic_expr_a_b(pipeline, 'and', 'report_id',
                                          ['C', 'D'])
    doc_ids, groups = _run_test_pipeline(mongo_collection_obj, pipeline)
    assert doc_ids == [11,14]

    # logical AND between features B, C and D, patient context
    pipeline = []
    pipeline = mongo_logic_ops.logic_expr_a_b(pipeline, 'and', 'subject',
                                          ['B', 'C', 'D'])
    doc_ids, groups = _run_test_pipeline(mongo_collection_obj, pipeline)
    #assert doc_ids == [6,7,11,12,14,15]
    assert doc_ids == [6,11,14]

    # logical AND between features A, B, C and D, patient context
    pipeline = []
    pipeline = mongo_logic_ops.logic_expr_a_b(pipeline, 'and', 'subject',
                                          ['A', 'B', 'C', 'D'])
    doc_ids, groups = _run_test_pipeline(mongo_collection_obj, pipeline)
    #assert doc_ids == [1,2,6,7,11,12,14,15]
    assert doc_ids == []

    # logical OR between features C and D, document context
    pipeline = []
    pipeline = mongo_logic_ops.logic_expr_a_b(pipeline, 'or', 'report_id',
                                          ['C', 'D'])
    doc_ids, groups = _run_test_pipeline(mongo_collection_obj, pipeline)
    assert doc_ids == [11,12,13,14,15]

    # logical OR between features C and D, patient context
    pipeline = []
    pipeline = mongo_logic_ops.logic_expr_a_b(pipeline, 'or', 'subject',
                                          ['C', 'D'])
    doc_ids, groups = _run_test_pipeline(mongo_collection_obj, pipeline)
    assert doc_ids == [11,12,13,14,15]
    
    # logical OR between features A, C, and D
    pipeline = []
    pipeline = mongo_logic_ops.logic_expr_a_b(pipeline, 'or', None,
                                          ['A', 'C', 'D'])
    doc_ids, groups = _run_test_pipeline(mongo_collection_obj, pipeline)
    assert doc_ids == [1,2,3,4,5,11,12,13,14,15]

    # A not B, document context
    pipeline = []
    pipeline = mongo_logic_ops.logic_expr_a_b(pipeline, 'not', 'report_id',
                                          ['A', 'B'])
    doc_ids, groups = _run_test_pipeline(mongo_collection_obj, pipeline)
    assert doc_ids == [1,2,3]

    # A not B, patient context
    pipeline = []
    pipeline = mongo_logic_ops.logic_expr_a_b(pipeline, 'not', 'subject',
                                          ['A', 'B'])
    doc_ids, groups = _run_test_pipeline(mongo_collection_obj, pipeline)
    assert doc_ids == []

    # D not C, document context
    pipeline = []
    pipeline = mongo_logic_ops.logic_expr_a_b(pipeline, 'not', 'report_id',
                                          ['D', 'C'])
    doc_ids, groups = _run_test_pipeline(mongo_collection_obj, pipeline)
    assert doc_ids == [15]

    # B not C, patient context
    pipeline = []
    pipeline = mongo_logic_ops.logic_expr_a_b(pipeline, 'not', 'subject',
                                          ['B', 'C'])
    doc_ids, groups = _run_test_pipeline(mongo_collection_obj, pipeline)
    assert doc_ids == [9,10]

    # not B
    pipeline = []
    pipeline = mongo_logic_ops.logic_expr_not_a(pipeline, 'B')
    doc_ids, groups = _run_test_pipeline(mongo_collection_obj, pipeline)
    assert doc_ids == [1,2,3,4,5,11,12,13,14,15]

    # not D
    pipeline = []
    pipeline = mongo_logic_ops.logic_expr_not_a(pipeline, 'D')
    doc_ids, groups = _run_test_pipeline(mongo_collection_obj, pipeline)
    assert doc_ids == [1,2,3,4,5,6,7,8,9,10,11,12,13]


    mongo_db_obj.drop_collection(COLLECTION_NAME)
    

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
    json_result = _to_mongo_pipeline(postfix_expr, {})
    if _EMPTY_JSON != json_result:
        json_data = json.loads(json_result)
        print('   Command: ')
        print(json.dumps(json_data, indent=4))

