#!/usr/bin/env python3
"""



OVERVIEW:



The code in this module evaluates mathematical and logical expressions that
appear in NLPQL 'define' statements. The expression is the part of the
statement that follows the 'where' keyword.  For instance, in the statement

    define hasFever:
        where Temperature.value >= 100.4;

the expression is the string 'Temperature.value >= 100.4'.

NLPQL expressions evaluate to a Boolean result. Expressions can be combined
with logical operators and they can be parenthesized in the usual way to
enforce precedence or evaluation order. Some examples:

    Temperature.value >= 97.7 AND Temperature.value <= 99.5
    hasRigors AND (hasDyspnea OR hasTachycardia)
    LesionMeasurement.dimension_X > 10 AND Temperature.value > 98.6
    etc.

There are many more examples towards the end of this file in the _run_tests
function.

The expression is assumed to have already been validated by the NLPQL parser,
which means that parentheses are balanced, the operators and variables are
known, and that the statement obeys valid mathematical syntax.

This module converts the expression to a set of MongoDB aggregation commands
and executes the command against a MongoDB collection. The ObjectId (_id) of
each document satisfying the expression is returned to the caller.



USAGE:



Step 1:

The first thing to do when using this module is to parse the infix epression
string. Do this by making a call to the 'parse_expression' function:

    parse_result = parse_expression(infix_expression, name_list)

The 'name_list' is an optional list argument used to validate the tokens in
the infix expression. NLPQL 'define' statements create new labels and define
them using combinations of existing labels. In the 'hasFever' example above,
the 'hasFever' label is defined using the existing label 'Temperature'. The
name_list contains all such labels and is used to verify that all string tokens
are valid.

The 'parse_result' is a fully-parenthesized string with the operator symbols
replaced by string mnemonics and a space character inserted between the tokens.
The expression 'Temperature.value >= 100.4' would be returned from the
expression parser as

    '( Temperature.value GE 100.4 )'

If the expression is invalid or cannot be evaluated, then an empty string is
returned and relevant information is written to the runtime log.


Step 2:

The next step after a successful parse is to generate a list of
ExpressionObject namedtuples from the parse result. These namedtuples are
defined below and are self-contained descriptions of an evaluation run. Some
input expressions may be decomposed into multiple subexpressions, and in such
cases the list of ExpressionObjects contains all such subexpressions.

Generate this list by calling 'generate_expressions':

    expression_obj_list = generate_expressions(nlpql_feature, parse_result)

The 'nlpql_feature' is the name to assign to the result of the evaluation,
such as 'hasFever' in the example above. The 'parse_result' is the nonempty
string returned by 'parse_expression'.

The 'expression_obj_list' returned by the function is the list of
ExpressionObject namedtuples mentioned previously. Users do not need to access
or interpret the members of this namedtuple.


Step 3:

The final step is to evaluate each of the (sub)expressions in the
expression_obj_list. This can be done as follows:

    for expr_obj in expression_obj_list:

        result = evaluate_expression(expr_obj, 
                                     job_id,
                                     context_field,
                                     mongo_collection_obj)

The job_id is an integer assigned by the ClarityNLP runtime.

The context_field is a string that has a value of either 'document' for a
document context or 'subject' for a patient context.

The 'mongo_collection_obj' argument is a pymongo object representing the
desired collection. This object can be created externally to the module as
follows:

    mongo_client_obj     = pymongo.MongoClient(mongo_host, mongo_port)
    mongo_db_obj         = mongo_client_obj[db_name]
    mongo_collection_obj = mongo_db_obj[collection_name]

The collection object is created externally to avoid the penalty of recreation
for each expression evaluation.

This function returns an EvalResult namedtuple, which is defined below. This
namedtuple contains a list of the ObjectId (_id) values for all documents that
satisfy the expression.

Given a list of document IDs, the full documents can be retrieved from the
database with this query:

    cursor = collection.find({'_id' : {'$in' : doc_id_list}})

Each document can be accessed by iteration:

    for doc in cursor:
        # do something with doc



TESTING:


Test code has been moved to 'expr_tester.py'.



LIMITATIONS:


The 'not' operator is not supported. You will need to use positive logic.

Database operations involving syntax such as 'predicate IS NOT? NULL',
'predicate NOT? LIKE predicate (STRING)?' are not yet supported.

"""

import re
import os
import sys
import copy
import string
import optparse
from pymongo import MongoClient
from collections import namedtuple
from bson.objectid import ObjectId

try:
    from data_access.expr_lexer  import NlpqlExpressionLexer
    from data_access.expr_parser import NlpqlExpressionParser
    from data_access.expr_parser import NLPQL_EXPR_OPSTRINGS
    from data_access.expr_parser import NLPQL_EXPR_OPSTRINGS_LC # lowercase
    from data_access.expr_parser import NLPQL_EXPR_LOGIC_OPERATORS
except ImportError:
    from expr_lexer  import NlpqlExpressionLexer
    from expr_parser import NlpqlExpressionParser
    from expr_parser import NLPQL_EXPR_OPSTRINGS
    from expr_parser import NLPQL_EXPR_OPSTRINGS_LC # lowercase
    from expr_parser import NLPQL_EXPR_LOGIC_OPERATORS

# expression types
EXPR_TYPE_MATH    = 'math'
EXPR_TYPE_LOGIC   = 'logic'
EXPR_TYPE_MIXED   = 'mixed' # math+logic or math with different NLPQL features
EXPR_TYPE_UNKNOWN = 'unknown'

# unsupported operator strings (should match entries in NLPQL_EXPR_OPSTRINGS)
EXPR_UNSUPPORTED_OPSTRINGS = ['NOT']

# expression object, contains info on a primitive expression to be evaluated
EXPR_OBJ_FIELDS = [
    # one of the EXPR_TYPE_ constants
    'expr_type',

    # (string) the NLPQL feature assigned to this expression
    'nlpql_feature',

    # (string) the raw text of the infix expression to be evaluated
    'expr_text',

    # (integer) index of this expression in the phenotype
    'expr_index'
]

ExpressionObject = namedtuple('ExpressionObject', EXPR_OBJ_FIELDS)

# result from an individual expression evaluation
EXPR_RESULT_FIELDS = [

    # one of the EXPR_TYPE_ constants
    'expr_type',

    # a string such as 'Temperature', 'hasRigors', 'hasSepsis', etc.
    # could also be a temporary such as m0, m1
    'nlpql_feature',

    # string, the text of the expression that was evaluated
    'expr_text',

    # (integer) index of this expression in the phenotype
    'expr_index',

    # list of strings, the postfix representation of the expression
    'postfix_tokens',

    # list of _id values of all result documents that satisfy the expression
    'doc_ids',

    # list of lists; each inner list is a group of _id values
    # there is one group per value of the context variable, representing the
    # docs found for that group
    'group_list',
]

EvalResult = namedtuple('EvalResult', EXPR_RESULT_FIELDS)

# regex that identifies a temporary NLPQL feature
# 32 hex digits in the MD5 hash, needs to be exportable
regex_temp_nlpql_feature = re.compile(r'\A(math|logic)_\d+_\d+\Z')
    
# identifies a temp logic feature, not exported
_regex_temp_nlpql_logic_feature = re.compile(r'\Alogic_\d+_\d+\Z')

_VERSION_MAJOR = 0
_VERSION_MINOR = 3
_MODULE_NAME   = 'expr_eval.py'

# set to True to enable debug output
_TRACE = False

# quoted string literal
_str_string_literal = r'\A[\'\"][^\'\"]+[\'\"]\Z'
_regex_string_literal = re.compile(_str_string_literal, re.IGNORECASE)

# NLPQL numeric literal operand
_str_numeric_literal = r'\A[-+]?(\d+\.\d+|\.\d+|\d+)\Z'
_regex_numeric_literal = re.compile(_str_numeric_literal)

_str_identifier = r'(?!and)(?!or)(?!not)\b[a-zA-Z$_][a-zA-Z0-9$_]*'
_str_nlpql_feature = r'\A' + _str_identifier + r'\Z'
_regex_nlpql_feature = re.compile(_str_nlpql_feature, re.IGNORECASE)

_str_variable = r'(?P<nlpql_feature>' + _str_identifier + r')' +\
                r'\.' +\
                r'(?P<value>' + _str_identifier + r')'
_regex_variable = re.compile(_str_variable, re.IGNORECASE)

# recognize n-ary OR in a postfix string
_str_nary_or = _str_identifier + r'\s'            +\
            r'(' + _str_identifier + r'\sor\s)*'  +\
             _str_identifier + r'\sor\b'
_regex_nary_or = re.compile(_str_nary_or, re.IGNORECASE)

# recognize n-ary AND in a postfix string
_str_nary_and = _str_identifier + r'\s'            +\
            r'(' + _str_identifier + r'\sand\s)*'  +\
            _str_identifier + r'\sand\b'
_regex_nary_and = re.compile(_str_nary_and, re.IGNORECASE)

_regex_temp_feature = re.compile(r't\d+', re.IGNORECASE)

# logic op after postfix conversion, includes tokens such as or3, and5, etc.
_regex_logic_operator = re.compile(r'\A((and|or)(\d+)?|not)\Z')

_PYTHON_OPERATOR_MAP = {
    'PLUS':'+',
    'MINUS':'-',
    'MULT':'*',
    'DIV':'/',
    'MOD':'%',
    'EXP':'**',
    'GE':'>=',
    'GT':'>',
    'LE':'<=',
    'LT':'<',
    'EQ':'==',
    'NE':'!='
}

# convert from operator mnemonic to MongoDB aggregation operator
# (the unary operator 'not' is handled separately)
_MONGO_OPS = {
    'or':'$or',
    'and':'$and',
    'eq':'$eq',
    'ne':'$ne',
    'gt':'$gt',
    'lt':'$lt',
    'ge':'$gte',
    'le':'$lte',
    'plus':'$add',
    'minus':'$subtract',
    'mult':'$multiply',
    'div':'$divide',
    'mod':'$mod',
    'exp':'$pow',
}

# operator precedence, matches python's rules
_PRECEDENCE_MAP = {
    '(':0,
    ')':0,
    'or':1,
    'and':2,
    'not':3,
    'lt':4,
    'le':4,
    'gt':4,
    'ge':4,
    'ne':4,
    'eq':4,
    'plus':9,
    'minus':9,
    'mult':10,
    'div':10,
    'mod':10,
    'exp':12,
}

# unary operators
_UNITARY_OPS = ['not']

# operators with right-to-left associativity
_R_TO_L_OPS = ['^'] # exponentiation

_LEFT_PARENS  = '('
_RIGHT_PARENS = ')'
_CHAR_SPACE = ' '
_EMPTY_STRING = ''

_TMP_FEATURE_MATH  = 0
_TMP_FEATURE_LOGIC = 1

_EXPR_INDEX = 0


###############################################################################
def enable_debug():
    """
    Enable debug output.
    """

    global _TRACE
    _TRACE = True
    

###############################################################################
def _extract_variables(infix_expression):
    """
    Returns all unique variables (of the form nlpql_feature.field) from
    the given infix expression, along with separate lists of nlpql_features
    and the associated fields.
    """

    fields = set()
    variables = set()
    nlpql_features = set()
    
    infix_tokens = infix_expression.split()
    for token in infix_tokens:
        match = _regex_variable.match(token)
        if match:
            variable = match.group()
            variables.add(variable)
            nlpql_feature, field = variable.split('.')
            nlpql_features.add(nlpql_feature)
            fields.add(field)

    return (variables, nlpql_features, fields)


###############################################################################
def _is_math_expr(infix_tokens):
    """
    Pure math expressions consist entirely of terms of the form:

            nlpql_feature.value
            operator
            numeric_literal
            parentheses

    This function checks infix expression tokens and returns a Boolean
    indicating whether the expression is pure math or not.

    Only a single nlpql_feature is present in a pure math expression.
    Expressions with variables involving multiple nlpql_features are of
    mixed type.
    """

    nlpql_feature_set = set()
    value_set = set()

    for token in infix_tokens:
        if _LEFT_PARENS == token or _RIGHT_PARENS == token:
            continue
        match = _regex_variable.match(token)
        if match:
            nlpql_feature = match.group('nlpql_feature')
            nlpql_feature_set.add(nlpql_feature)
            value = match.group('value')
            value_set.add(value)
            continue
        if token in NLPQL_EXPR_OPSTRINGS:
            continue
        match = _regex_numeric_literal.match(token)
        if match:
            continue

        # if here, not a pure math expression
        return False

    return 1 == len(nlpql_feature_set)


###############################################################################
def _is_logic_expr(infix_tokens):
    """
    Pure logic expressions consist entirely of terms of the form:

        nlpql_feature
        logic operator ('and', 'or', 'not')
        parentheses

    This function checks infix expression tokens and returns a Boolean
    indicating whether the expression is pure logic or not.
    """

    for token in infix_tokens:
        if _LEFT_PARENS == token or _RIGHT_PARENS == token:
            continue
        if token in NLPQL_EXPR_LOGIC_OPERATORS:
            continue
        match = _regex_nlpql_feature.match(token)
        if match:
            continue

        # if here, not a pure logic expression
        return False

    return True


###############################################################################
def _is_mixed_expr(infix_tokens):
    """
    A 'mixed' expression has one of these forms:

        A math expression involving variables with two or more NLPQL features
        An expression combining both math and logic subexpressions
    """

    has_variable = False
    has_nlpql_feature = False

    for token in infix_tokens:
        if _LEFT_PARENS == token or _RIGHT_PARENS == token:
            continue
        match = _regex_variable.match(token)
        if match:
            continue
        if token in NLPQL_EXPR_OPSTRINGS:
            continue
        match = _regex_nlpql_feature.match(token)
        if match:
            continue
        match = _regex_numeric_literal.match(token)
        if match:
            continue
        match = _regex_nlpql_feature.match(token)
        if match:
            continue

        # if here, invalid
        return False

    return True


###############################################################################
def _expr_type(infix_expression_string):
    """
    Examine the tokens and return the expression type.
    """

    infix_tokens = infix_expression_string.split()
    
    if _is_math_expr(infix_tokens):
        return EXPR_TYPE_MATH
    elif _is_logic_expr(infix_tokens):
        return EXPR_TYPE_LOGIC
    elif _is_mixed_expr(infix_tokens):
        return EXPR_TYPE_MIXED
    else:
        return EXPR_TYPE_UNKNOWN

    
###############################################################################
def _is_operator(token):
    """
    Return True if token is a valid NLPQL operator, False if not.
    """

    return token in NLPQL_EXPR_OPSTRINGS or token in NLPQL_EXPR_OPSTRINGS_LC


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
def _is_variable(token):
    """
    Return True if token is a variable of the form nlpql_feature.field, 
    False if not.
    """

    matchobj = _regex_variable.match(token)
    return matchobj is not None


###############################################################################
def _is_nlpql_feature(token):
    """
    Return True if token is a valid NLPQL feature, False if not.
    """

    matchobj = _regex_nlpql_feature.search(token)
    return matchobj is not None


###############################################################################
def _precedence(operator_token):
    """
    Return the numeric precedence value of the given operator token.
    """

    assert operator_token in _PRECEDENCE_MAP
    return _PRECEDENCE_MAP[operator_token]

    
###############################################################################
def _infix_to_postfix(infix_tokens):
    """
    Convert an infix expression of the form A OP1 B OP2 C ... into the
    equivalent postfix form. Parentheses may also be present as separete tokens
    and are assumed to be balanced.

    The 'infix_tokens' argument is a list of strings.

    Returns the postfix equivalent of the infix tokens.

    Example:

        The infix expression
  
           'D > A + (B * C)'

        has this representation as a list of infix tokens:

           ['D', '>', 'A', '+', '(', 'B', '*', 'C', ')']

        This function converts the list to its postfix equivalent:

           ['D', 'A', 'B', 'C', '*', '+', '>']

        Note that the postfix version has no parentheses, since the conversion
        algorithm uses operator precedence and associativity rules to remove
        them.
    """

    postfix_expr = []
    operator_stack = []

    for token in infix_tokens:
        if _is_operand(token):
            # operands are accepted in order of occurrence
            postfix_expr.append(token)
        else:
            token = token.lower()
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
                        operator_stack.append(token)
                    elif p1 == p2:
                        # equal precedence, so check associativity
                        if token in _R_TO_L_OPS:
                            # right-to-left associativity, push new operand
                            operator_stack.append(token)
                        else:
                            # left-to-right associativity
                            # pop stack, append to postfix, push new operand
                            stacktop = operator_stack.pop()
                            postfix_expr.append(stacktop)
                            operator_stack.append(token)
                    else:
                        # lower precedence, so pop stack and try again
                        stacktop = operator_stack.pop()
                        postfix_expr.append(stacktop)
                        if len(operator_stack) > 0:
                            finished = False
                        else:
                            # shortcut for empty stack
                            operator_stack.append(token)

    # pop all remaining tokens and append to postfix expression
    while operator_stack:
        token = operator_stack.pop()
        if token == _LEFT_PARENS or token == _RIGHT_PARENS:
            continue
        else:
            postfix_expr.append(token)

    return postfix_expr


###############################################################################
def _count_spaces(text):
    """
    Scan the text string, count the space characters, and return the count.
    """

    count = 0
    for c in text:
        if _CHAR_SPACE == c:
            count += 1
    return count


###############################################################################
def _make_n_ary(postfix_tokens):
    """
    Find instances of n-ary AND and n-ary OR and replace with ORn and ANDn,
    where 'n' is an integer literal.

    For instance, the postfix string

         A B or C or D or

    will be replaced with

         A B C D or4

    All tokens are assumed to be lowercase.
    """

    if _TRACE: print('calling _make_n_ary')
    
    postfix_string = ' '.join(postfix_tokens)
    if _TRACE: print('\tStarting postfix: {0}'.format(postfix_tokens))

    matches = []
    iterator = _regex_nary_or.finditer(postfix_string)
    for match in iterator:
        matching_text = match.group()
        if _TRACE:
            print('\tNARY MATCH (or): ->{0}<-'.format(matching_text))
        matching_text = re.sub(r'\bor', '', matching_text)
        matching_text = re.sub(r'\s+', ' ', matching_text)
        matching_text += 'or'
        n_value = _count_spaces(matching_text)
        matching_text = matching_text + '{0}'.format(n_value)
        if _TRACE:
            print('\tAFTER SUB: ->{0}<-'.format(matching_text))
        matches.append( (match.start(), match.end(), matching_text))

    iterator = _regex_nary_and.finditer(postfix_string)
    for match in iterator:
        matching_text = match.group()
        if _TRACE:
            print('\tNARY MATCH (and): ->{0}<-'.format(matching_text))
        matching_text = re.sub(r'\band', '', matching_text)
        matching_text = re.sub(r'\s+', ' ', matching_text)
        matching_text += 'and'
        n_value = _count_spaces(matching_text)
        matching_text = matching_text + '{0}'.format(n_value)
        if _TRACE:
            print('\tAFTER SUB: ->{0}<-'.format(matching_text))
        matches.append( (match.start(), match.end(), matching_text))

    # sort in order of occurrence
    matches = sorted(matches, key=lambda x: x[0])

    # do the text replacements in the postfix string
    prev = 0
    new_text = ''
    for start,end,replacement_text in matches:
        new_text += postfix_string[prev:start]
        new_text += replacement_text
        prev = end
    new_text += postfix_string[prev:]

    new_tokens = new_text.split()
    return new_tokens

        
###############################################################################
def _remove_unnecessary_parens(infix_expression):
    """
    Find all matching pairs of parentheses in the infix expression, along with
    the nesting depth of each pair. Starting from the innermost pair of parens,
    remove it, convert the new expression to postfix, and compare with the
    postfix version from original baseline. If no change, that pair of parens
    was nonessential and can be removed.
    """

    if _TRACE: print('Called _remove_unnecessary_parens')
    
    # return if no parens
    pos = infix_expression.find(_LEFT_PARENS)
    if -1 == pos:
        return infix_expression

    if _TRACE: print('\t  Infix baseline: "{0}"'.format(infix_expression))
    
    infix_tokens = infix_expression.split()
    
    # get baseline postfix expression
    postfix_tokens = _infix_to_postfix(infix_tokens)
    postfix_baseline = ' '.join(postfix_tokens)
    if _TRACE: print('\tPostfix baseline: "{0}"'.format(postfix_baseline))

    # locate matching pairs of parens
    pairs = []
    stack = []
    for i in range(len(infix_tokens)):
        tok = infix_tokens[i]
        if _LEFT_PARENS == tok:
            stack.append(i)
        elif _RIGHT_PARENS == tok:
            depth = len(stack)
            left = stack.pop()
            # triplets are actually appended to the pairs list, but whatever...
            pairs.append( (left, i, depth))

    # sort by decreasing order of nesting depth
    pairs = sorted(pairs, key=lambda x: x[2], reverse=True)
    if _TRACE:
        print('\t    Parens pairs: {0}'.format(pairs))
            
    for i in range(len(pairs)):

        left, right, depth = pairs[i]
        infix_tokens_save = copy.deepcopy(infix_tokens)

        # remove this pair of parens, convert to postfix, and see if changed
        del infix_tokens[right]
        del infix_tokens[left]
        trial_infix_expr = ' '.join(infix_tokens)
        if _TRACE:
            print('\t Removing parens: left={0}, right={1}'.format(left, right))
            print('\tTrial infix expr: {0}'.format(trial_infix_expr))

        postfix = _infix_to_postfix(infix_tokens)
        postfix = ' '.join(postfix)
        if _TRACE:
            print('\t   Trial postfix: "{0}"'.format(postfix))

        if postfix != postfix_baseline:
            # removal changed postfix result, so restore these parens
            if _TRACE: print('\t   Postfix CHANGED, restoring parens.')
            infix_tokens = infix_tokens_save            
        else:
            # removed nonessential parens
            infix_expression = trial_infix_expr
            if _TRACE:
                print('\t   Postfix MATCHED, removing parens.')
                print('\t  NEW INFIX EXPR: {0}'.format(infix_expression))
            
            # update remaining pair indices to account for token removal
            for j in range(i+1, len(pairs)):
                # current pair at (l0, r0); updated to (l, r)
                l0,r0,depth = pairs[j]
                l = l0
                r = r0
                if left < l0:
                    l -= 1
                if left < r0:
                    r -= 1
                if right < l0:
                    l -= 1
                if right < r0:
                    r -= 1
                pairs[j] = (l, r, depth)

            if _TRACE:
                remaining_pairs = pairs[i+1:]
                if len(remaining_pairs) > 0:
                    print('\tRemaining parens pairs: {0}'.format(remaining_pairs))
            
    if _TRACE:
        print('\tDONE')
        print('\tEssential parens: "{0}"'.format(infix_expression))
    return infix_expression


###############################################################################
def _evaluate_literals(infix_expression):
    """
    Evaluate any literal subexpressions inside the given infix expression
    and replace with the result.
    """

    stack = []
    tokens = infix_expression.split()
    
    for t in tokens:
        if _RIGHT_PARENS != t:
            stack.append(t)
        else:
            # walk back in the stack to the nearest '('
            all_literal_operands = True
            for j in reversed(range(len(stack))):
                tok = stack[j]
                if _LEFT_PARENS == tok:
                    break
                if tok in NLPQL_EXPR_OPSTRINGS:
                    continue
                match = _regex_numeric_literal.match(tok)
                if not match:
                    all_literal_operands = False
                    break
            if all_literal_operands:
                expr_tokens = []
                s = stack.pop()
                while _LEFT_PARENS != s:
                    if s in NLPQL_EXPR_OPSTRINGS:
                        s = _PYTHON_OPERATOR_MAP[s]
                    expr_tokens.append(s)
                    s = stack.pop()
                expr_tokens.reverse()
                literal_expr = ' '.join(expr_tokens)

                # let any exceptions propagate
                eval_result = eval(literal_expr)
                stack.append('{0}'.format(eval_result))
            else:
                # no literal subexpression, so push ')'
                stack.append(_RIGHT_PARENS)

    result_expr = ' '.join(stack)
    return result_expr


###############################################################################
def _decode_operator(token):
    """
    Decode a logical operator of the form or3, and5, etc. and return
    the operator and the 'arity' value.
    """
    
    assert token.startswith('or') or token.startswith('and')
    if token.startswith('or'):
        operator = 'or'
        if len(token) > 2:
            n = int(token[2:])
        else:
            n = 2
    elif token.startswith('and'):
        operator = 'and'
        if len(token) > 3:
            n = int(token[3:])
        else:
            n = 2
            
    if _TRACE:
        print('\tFound operator "{0}", n == {1}'.format(operator, n))

    return (operator, n)
        

###############################################################################
def _is_temp_feature(label):
    """
    Returns a Boolean indicating whether the string label is that of a
    temporary NLPQL feature. Temp labels are created in _make_temp_feature,
    so the code in both of these functions needs to be consistent.
    """

    matchobj = regex_temp_nlpql_feature.match(label)
    return matchobj is not None and _is_nlpql_feature(label)
    

###############################################################################
def _make_temp_feature(counter, token_list, expr_index, math_or_logic=_TMP_FEATURE_MATH):
    """
    Create a unique NLPQL feature name for a mathematical subexpression.
    This new name becomes the 'nlpql_feature' label that gets substituted
    in place of the math subexpression.

    If this code is changed, the code in _is_temp_feature needs to be changed
    to match.

    The new label consists of a prefix followed by the MD5 hash of the tokens
    joined with an underscore. The prefix includes a counter, and the hash is
    converted to hex for the final result.

    The benefit of using a hash is that we avoid exceeding the MongoDB limit
    on string length. Simply using a fixed-length slice of the joined strings
    is not adequate, since lengthy expressions may use the same variables and
    not differ until beyond the slice point.
    """
    
    if _TRACE:
        print('Called _make_temp_feature')
        print('\t    tokens: {0}'.format(token_list))
        print('\texpr_index: {0}, counter: {1}'.format(expr_index, counter))

    if _TMP_FEATURE_MATH == math_or_logic:
        label = 'math_{0}_{1}'.format(expr_index, counter)
    else:
        label = 'logic_{0}_{1}'.format(expr_index, counter)
    
    if _TRACE:
        print('\t New label: {0}'.format(label))

    assert _is_nlpql_feature(label)
    assert _is_temp_feature(label)
    return label


###############################################################################
def _merge_math_tokens(tokens, math_expressions, expr_index, counter):
    """
    Replace two distinct pure math expressions (represented by tokens such as
    m0 or m1) with a compound pure math expression represented by a single
    token. In other words, combine simple pure math expressions into compound
    pure math expressions.

    Two pure math expressions can be merged if their variables all refer to
    the same NLPQL feature. For instance, the pure math expressions

            (m0)      and    (m1)
        (Meas.x > 10) and (Meas.x < 30)

    can be merged into this compound expression, since the source expressions
    both use the same NLPQL feature 'Meas':

                     (m2)
        (Meas.X > 10 and Meas.x < 30)

    These two expressions cannot be merged, since the variables refer to
    different NLPQL features:

                 (m0)         and     (m1)
         (Temp.value > 100.4) and (Meas.x < 10)

    """
    stack = []
    for t in tokens:
        if _RIGHT_PARENS != t:
            stack.append(t)
        else:
            # pop all tokens back to the nearest left parens
            expr_tokens = []
            all_math_tokens = True
            s = stack.pop()
            while _LEFT_PARENS != s:
                if not _is_temp_feature(s) and not s in NLPQL_EXPR_LOGIC_OPERATORS:
                    all_math_tokens = False
                expr_tokens.append(s)
                s = stack.pop()

            expr_tokens.reverse()
            if all_math_tokens:
                
                # can merge into single expression if single nlpql_feature
                # and multiple tokens
                feature_set = set() 
                for m in expr_tokens:
                    if m in math_expressions:
                        expr, feature = math_expressions[m]
                        feature_set.add(feature)
                        
                if 1 == len(feature_set) and len(expr_tokens) > 1:
                    # merge these expressions, since all use same NLPQL feature
                    feature = feature_set.pop()
                    saved_tokens = copy.deepcopy(expr_tokens)
                    for j in range(len(expr_tokens)):
                        m = expr_tokens[j]
                        if m in math_expressions:
                            expr, feature = math_expressions[m]
                            expr_tokens[j] = expr
                            del math_expressions[m]
                    nlpql_expression = ' '.join(expr_tokens)
                    nlpql_feature = _make_temp_feature(counter,
                                                       saved_tokens,
                                                       expr_index)
                    math_expressions[nlpql_feature] = (nlpql_expression, feature)
                    counter += 1

                    # push back on stack with parens if more than a single token
                    if len(expr_tokens) > 1:
                        stack.append(_LEFT_PARENS)
                        stack.append(nlpql_feature)
                        stack.append(_RIGHT_PARENS)
                    else:
                        stack.append(nlpql_feature)
                else:
                    # push back with parens
                    stack.append(_LEFT_PARENS)
                    for et in expr_tokens:
                        stack.append(et)
                    stack.append(_RIGHT_PARENS)
                    
            else:
                # push back with parens
                stack.append(_LEFT_PARENS)
                for et in expr_tokens:
                    stack.append(et)
                stack.append(_RIGHT_PARENS)
                
    new_infix_expr = ' '.join(stack)
    if _TRACE: print('  COMBINED M EXPR: {0}'.format(new_infix_expr))
    
    return new_infix_expr, counter
    

###############################################################################
def _resolve_mixed(infix_expression, expr_index):
    """
    'Resolve' the mixed-type expression by performing substitutions for the
    math expressions, then combining the math expressions where possible.

    The argument is assumed to be a fully-parenthesized, syntactically-valid
    NLPQL expression that has made it through the front end parser.

    All tokens (including parens) are assumed to be separated by whitespace.

    Returns a list of (nlpql_feature, nlpql_expression) tuples along with the
    original expression containing the subexpression substitutions. The
    substitute nlpql_feature values begin with 'm0', 'm1', 'm2', etc. All of 
    these subexpressions have type EXPR_TYPE_MATH, so that the overall result
    is a pure logic expression involving the substituted symbols.
    """

    if _TRACE: print('Called _resolve_mixed')

    tokens = infix_expression.split()

    stack = []
    counter = 0
    math_expressions = {}

    for t in tokens:
        if _RIGHT_PARENS != t:
            stack.append(t)
        else:
            # pop all tokens back to the nearest left parens
            expr_tokens = []
            s = stack.pop()
            while _LEFT_PARENS != s:
                expr_tokens.append(s)
                s = stack.pop()

            expr_tokens.reverse()
            nlpql_expression = ' '.join(expr_tokens)
            expr_type = _expr_type(nlpql_expression)
            variable_set, feature_set, field_set = _extract_variables(nlpql_expression)
            if EXPR_TYPE_MATH == expr_type:
                # if single parenthesized token, push with no parens
                if 1 == len(expr_tokens):
                    stack.append(expr_tokens.pop())
                else:
                    # push replacement token with no parens
                    feature = feature_set.pop()
                    nlpql_feature = _make_temp_feature(counter,
                                                       expr_tokens,
                                                       expr_index)
                    stack.append(nlpql_feature)
                    math_expressions[nlpql_feature] = (nlpql_expression, feature)
                    counter += 1
                    if _TRACE:
                        print('\tReplacing "{0}" with feature "{1}"'.
                              format(nlpql_expression, nlpql_feature))
            else:
                # push logic operands with parens
                stack.append(_LEFT_PARENS)
                for et in expr_tokens:
                    stack.append(et)
                stack.append(_RIGHT_PARENS)
                
    new_infix_expr = ' '.join(stack)
    if _TRACE: print('\t   M EXPR: {0}'.format(new_infix_expr))

    # combine math expressions where possible
    prev = new_infix_expr
    
    # do a max of 10 iterations to combine subexpressions
    for k in range(10):
        tokens = new_infix_expr.split()
        new_infix_expr, counter = _merge_math_tokens(tokens,
                                                     math_expressions,
                                                     expr_index,
                                                     counter)
        if prev == new_infix_expr:
            break
        else:
            prev = new_infix_expr
    
    temp_expressions = []
    for k in math_expressions.keys():
        expr, feature = math_expressions[k]
        temp_expressions.append( (k, expr) )
    temp_expressions = sorted(temp_expressions, key=lambda x: x[0])

    # # renumber the temp expressions starting with 0
    # counter = 0
    # for k in range(len(temp_expressions)):
    #     mval, expr = temp_expressions[k]
    #     new_mval = 'm{0}'.format(counter)
    #     temp_expressions[k] = (new_mval, expr)
    #     counter += 1
    # also make replacements in the new_infix_expr string - TBD
    
    return (temp_expressions, new_infix_expr)


###############################################################################
def _print_math_results(doc_ids, mongo_collection_obj, nlpql_feature):
    """
    Write results from evaluation of a math pipeline to stdout.
    """

    # query for the desired documents
    cursor = mongo_collection_obj.find({'_id': {'$in': doc_ids}})

    print('RESULTS for NLPQL feature "{0}": '.format(nlpql_feature))
    count = 0
    for doc in cursor:
        print('{0:5}\t_id: {1}, value: {2}'.
              format(count, doc['_id'], doc['value']))

        count += 1

        
###############################################################################
def _print_logic_results(group_list,
                         doc_ids,
                         mongo_collection_obj,
                         nlpql_feature):
    """
    Write results from evaluation of a logic pipeline to stdout.
    """

    # query for these documents
    cursor = mongo_collection_obj.find({'_id': {'$in': doc_ids}})

    # load docs into a map
    doc_map = {}
    for doc in cursor:
        id_val = doc['_id']
        doc_map[id_val] = doc

    # generate doc groups
    all_doc_groups = []
    for group in group_list:
        doc_group = []
        for id_val in group:
            doc_group.append(doc_map[id_val])
        all_doc_groups.append(doc_group)

    # print info for the groups
    print('RESULTS for NLPQL feature "{0}": '.format(nlpql_feature))
    count = 0
    for group in all_doc_groups:
        for doc in group:
            print('\t{0}: {1:16}\tsubject: {2}\treport_id: {3}'.
                  format(doc['_id'],
                         doc['nlpql_feature'],
                         doc['subject'],
                         doc['report_id']))
            count += 1
        print()
    

###############################################################################
def _run_math_pipeline(pipeline, mongo_collection_obj):
    """
    Run an aggregation pipeline for a pure math expression and return a list
    of _id values for all documents that satisfy the math expression.
    """

    # run the aggregation pipeline
    cursor = mongo_collection_obj.aggregate(pipeline, allowDiskUse=True)

    # keep all doc ids for which the aggregation result is True
    doc_ids = [doc['_id'] for doc in cursor if doc['value']]

    return doc_ids


###############################################################################
def _run_logic_pipeline(pipeline, mongo_collection_obj):

    # run the aggregation pipeline
    cursor = mongo_collection_obj.aggregate(pipeline, allowDiskUse=True)

    # get ntuple array from each cursor result, which contains the groups for
    # each value of the context variable

    all_groups = []
    for agg_result in cursor:
        ntuple = agg_result['ntuple']
        group_ids = []
        for t in ntuple:
            group_ids.append(t['_id'])
        all_groups.append(group_ids)

    # collect all _ids into a list for a bach query
    doc_ids = []
    for group in all_groups:
        for id_val in group:
            doc_ids.append(id_val)

    return (all_groups, doc_ids)

        
###############################################################################
def _convert_variables(infix_expr):
    """
    Convert the variables in a mathematical expression to a form that can be
    evaluated via MongoDB aggregation.
    """

    if _TRACE: print('Called _convert_variables')
    
    variables, nlpql_feature_set, field_set = _extract_variables(infix_expr)
    if _TRACE: print('\tVARIABLES: {0}'.format(variables))

    # pure math expressions only have a single nlpql feature
    assert 1 == len(nlpql_feature_set)
    nlpql_feature = nlpql_feature_set.pop()

    infix_tokens = infix_expr.split()

    new_infix_tokens = []
    new_infix_tokens.append('(')
    new_infix_tokens.append('nlpql_feature')
    new_infix_tokens.append('EQ')
    new_infix_tokens.append('"{0}"'.format(nlpql_feature))
    new_infix_tokens.append(')')
    new_infix_tokens.append('and')
    new_infix_tokens.append('(')
    for token in infix_tokens:
        match = _regex_variable.match(token)
        if match:
            value = match.group('value')
            new_infix_tokens.append(value)
        else:
            new_infix_tokens.append(token)
    new_infix_tokens.append(')')

    new_expr = ' '.join(new_infix_tokens)
    if _TRACE: print('\tConverted expression: "{0}"'.format(new_expr))
    
    return (new_expr, nlpql_feature, list(field_set))

         
###############################################################################
def _format_math_operand(operand):
    """
    Construct the appropriate MongoDB syntax for an operand in an aggregation
    clause. Compound operators need to be surrounded by curly brackets, 
    numeric literals are unchanged, and variables need a '$' prepended.
    """

    if isinstance(operand, dict):
        return operand
    elif _is_numeric_literal(operand):
        operand = float(operand)
    elif _is_string_literal(operand):
        # strip quotes
        operand = operand.strip('"')
    elif isinstance(operand, str):
        # field name, prepend '$'
        operand = '${0}'.format(operand)
        
    return operand


###############################################################################
def _mongo_math_format(operator, op1, op2=None):
    """
    Format a MongoDB aggregation expression for an operator and two operands.
    """

    if _TRACE:
        print('Called _mongo_math_format with operator ' +\
              '"{0}", op1: "{1}", op2: "{2}"'.format(operator, op1, op2))
    
    if 'not' == operator:
        result = {'$not': [_format_math_operand]}
    else:
        opstring = '{0}'.format(_MONGO_OPS[operator])
        operand1 = _format_math_operand(op1)
        operand2 = _format_math_operand(op2)
        result = {opstring: [operand1, operand2]}
    
    return result

        
###############################################################################
def _eval_math_expr(job_id,
                    expr_obj,
                    mongo_collection_obj):
    """
    Generate a MongoDB aggregation pipeline to evaluate the given math
    expression, supplied in infix form.

    The job_id param is an integer representing a job_id in MongoDB.
    The infix_expr param is the expression to be evaluated.
    """

    if _TRACE:
        print('Called _eval_math_expr')
        print('\tExpression: "{0}"'.format(expr_obj.expr_text))

    final_nlpql_feature = expr_obj.nlpql_feature
    infix_expr = expr_obj.expr_text
        
    # get rid of extraneous parentheses
    infix_expr = _remove_unnecessary_parens(infix_expr)

    # rewrite expression and extract NLPQL feature and field names
    new_expr, nlpql_feature, field_list = _convert_variables(infix_expr)

    # convert to postfix
    infix_tokens = new_expr.split()
    postfix_tokens = _infix_to_postfix(infix_tokens)
    if _TRACE: print('\tpostfix: {0}'.format(postfix_tokens))

    # 'evaluate' to generate MongoDB aggregation commands
    stack = []
    for token in postfix_tokens:
        if not _is_operator(token):
            stack.append(token)
            if _TRACE: print('\tPushed postfix token "{0}"'.format(token))
        else:
            if token in _UNITARY_OPS:
                operand = stack.pop()
                result = _mongo_math_format(token, operand)
            else:
                operand2 = stack.pop()
                operand1 = stack.pop()
                result = _mongo_math_format(token, operand1, operand2)
                
            stack.append(result)

    # should only have a single element left on the stack, the result
    assert 1 == len(stack)

    # Create a result document containing a Boolean 'value' field, which will
    # be set to True for all documents satisfying the mathematical expression.
    op_stage = {
        "$project": {
            "value": stack[0]
        }
    }

    if _TRACE:
        print('MATH_OP PIPELINE STAGE: ')
        print(op_stage)
        print()

    # initial filter, match on job_id and check nlpql_feature field
    initial_filter = {
        "$match": {
            "job_id":job_id,
            "nlpql_feature": {"$exists":True, "$ne":None},
        }
    }

    # insert field checks into initial filter
    for f in field_list:
        initial_filter['$match'][f] = {"$exists":True, "$ne":None}

    pipeline = [
        initial_filter,
        op_stage,
    ]

    if _TRACE:
        print('FULL AGGREGATION PIPELINE: ')
        print(pipeline)
        print()

    doc_ids = _run_math_pipeline(pipeline, mongo_collection_obj)

    if _TRACE:
        _print_math_results(doc_ids, mongo_collection_obj, final_nlpql_feature)

    result = EvalResult(
        expr_type      = EXPR_TYPE_MATH,
        nlpql_feature  = final_nlpql_feature,
        expr_text      = infix_expr,
        expr_index     = expr_obj.expr_index,
        postfix_tokens = copy.deepcopy(postfix_tokens),
        doc_ids        = copy.deepcopy(doc_ids),
        group_list     = [] # no groups for math expressions
    )
    
    return result
    
        
###############################################################################
def _format_logic_operand(operand):
    """
    Construct the appropriate MongoDB syntax for an operand in an aggregation
    clause.
    """

    if isinstance(operand, str):
        operand = {"$in": [operand, "$feature_set"]}

    # otherwise operand is a dict, just return it
    return operand


###############################################################################
def _mongo_logic_format(operator, operands):
    """
    Format a MongoDB aggregation expression for an operator and its operands.
    """

    opstring = '{0}'.format(_MONGO_OPS[operator])
    
    formatted_operands = []
    for op in operands:
        formatted_operands.append( _format_logic_operand(op) )

    result = {opstring: formatted_operands}
    return result


###############################################################################
def _eval_logic_expr(job_id,
                     context_field,
                     expr_obj,
                     mongo_collection_obj):
    """
    Generate a MongoDB aggregation pipeline to evaluate the given logical
    expression, supplied in infix form.

    The job_id param is an integer, a ClarityNLP job ID.
    The context_field param is a string, either 'subject' or 'document'.
    The final_nlpql_feature param is the name of the feature to which
    this expression applies.
    The infix_expr param is the expression to be evaluated.
    """

    if _TRACE:
        print('Called _eval_logic_expr')
        print('\tExpression: "{0}"'.format(expr_obj.expr_text))

    final_nlpql_feature = expr_obj.nlpql_feature
    infix_expr = expr_obj.expr_text

    assert 'subject' == context_field or 'report_id' == context_field

    if 'subject' == context_field:
        other_context_field = 'report_id'
        sort_field = 'ntuple.report_id'
    else:
        other_context_field = 'subject'
        sort_field = 'ntuple.subject'

    infix_expr = _remove_unnecessary_parens(infix_expr)
        
    infix_tokens = infix_expr.split()
    postfix_tokens = _infix_to_postfix(infix_tokens)

    # convert to n-ary and, or, if possible
    postfix_tokens = _make_n_ary(postfix_tokens)
    
    if _TRACE: print('\tpostfix: {0}'.format(postfix_tokens))

    # single-word expression, an nlpql_feature
    if 1 == len(postfix_tokens):
        nlpql_features = [postfix_tokens[0]]
        feature = '{0}'.format(postfix_tokens[0])
        stack = [{"$in": [feature, "$feature_set"]}]
    else:
        # generate aggregation commands for logic involving NLPQL features
        stack = []
        nlpql_features = []
        for token in postfix_tokens:
            match = _regex_logic_operator.match(token)
            if not match:
                stack.append(token)
                nlpql_features.append(token)
                if _TRACE: print('\tPushed postfix token "{0}"'.format(token))
            else:
                if 'not' == token:
                    operand = stack.pop()
                    result = _mongo_logic_format(token, operand)
                else:
                    operator, n = _decode_operator(token)

                    # pop n operands from the stack
                    operands = []
                    for i in range(n):
                        operands.append(stack.pop())
                    operands.reverse()
                    result = _mongo_logic_format(operator, operands)

                stack.append(result)

    # should only have a single element left on the stack, the result
    assert 1 == len(stack)
    
    # add preamble/postamble to this stage
    op_stage = {"$match": {"$expr": stack[0]}}

    if _TRACE:
        print('LOGIC_OP PIPELINE STAGE: ')
        print(op_stage)
        print()
    
    pipeline = [
        
        # initial filter, match on job_id and check nlpql_feature field
        {
            "$match": {
                "job_id":job_id,
                "nlpql_feature": {"$exists":True, "$ne":None}
            }
        },

        # keep only those docs having the NLPQL feature(s) in question
        {
            "$match": {
                "nlpql_feature": {"$in": nlpql_features}
            }
        },
        
        # group documents by value of the context field, which is either
        # the patient id or doc id
        # also compute the *set* of all nlpql features for each patient or doc
        {
            "$group": {
                "_id": "${0}".format(context_field),
                #"ntuple": {"$push": "$$ROOT"},

                # save only these four fields from each doc; more efficient
                # than saving entire doc, uses less memory
                "ntuple": {
                    "$push": {
                        "_id": "$_id",
                        "nlpql_feature": "$nlpql_feature",
                        "subject": "$subject",
                        "report_id": "$report_id"
                    }
                },
                "feature_set": {"$addToSet": "$nlpql_feature"}
            }
        },

        # do logic ops on the nlpql feature set for this patient or doc
        op_stage,

        # *** sorting on the other field is unnecessary ***
        
        # # sort on 'other' context variable (compared as strings)
        # {"$unwind": "$ntuple"},
        # {"$sort": {sort_field: 1}},

        # # Regroup using the _ids from the previous grouping, which will
        # # reconstruct the original grouping by value of the context variable.
        # # Also recover the ntuple and feature_set arrays from the
        # # original grouping.
        # {
        #     "$group": {
        #         "_id": "$_id",
        #         "ntuple": {"$push": "$ntuple"},
        #         "feature_set": {"$addToSet": "$ntuple.nlpql_feature"}
        #     }
        # },
    ]

    if _TRACE:
        print('FULL AGGREGATION PIPELINE: ')
        print(pipeline)
        print()

    group_list, doc_ids = _run_logic_pipeline(pipeline, mongo_collection_obj)

    #if _TRACE:
    #    _print_logic_results(group_list, doc_ids, mongo_collection_obj, final_nlpql_feature)

    result = EvalResult(
        expr_type      = EXPR_TYPE_LOGIC,
        nlpql_feature  = final_nlpql_feature,
        expr_text      = infix_expr,
        expr_index     = expr_obj.expr_index,
        postfix_tokens = copy.deepcopy(postfix_tokens), 
        doc_ids        = copy.deepcopy(doc_ids),
        group_list     = copy.deepcopy(group_list)
    )
    
    return result


###############################################################################
def build_feature_map(oid_list, doc_map):
    """
    Given a list of Mongo _id values, find all of the NLPQL features that
    the associated docs have, count them, and sort in decreasing order of
    occurrence count. Return the list of (nlpql_feature, count) tuples as
    the 'feature_list'.

    Also build a 'feature_map' dict that maps each nlpql_feature to a triplet
    containing (number_of_docs_with_this_feature, current_index, index_list).

    The 'current_index' field will be used by the output generation code.
    The index_list is the list of docs in the oid_list that have the
    given nlpql feature.

    Returns (feature_list, feature_map).
    """

    # count the number of NLPQL features in this oid_list
    feature_counts = {}
    for oid in oid_list:
        assert oid in doc_map
        doc = doc_map[oid]
        feature = doc['nlpql_feature']
        if not feature in feature_counts:
            feature_counts[feature] = 1
        else:
            feature_counts[feature] += 1

    # convert to list of (feature, count) tuples, sort by decreasing count
    features = feature_counts.keys()
    counts   = feature_counts.values()
    feature_list = list(zip(features, counts))
    feature_list = sorted(feature_list, key=lambda x: x[1], reverse=True)

    feature_map = {}        
    for i in range(len(oid_list)):
        oid = oid_list[i]
        doc = doc_map[oid]
        feature = doc['nlpql_feature']
        if not feature in feature_map:
            # (number of docs with this feature, current_index, index_list)
            feature_map[feature] = (1, 0, [i])
        else:
            doc_count, current_index, index_list = feature_map[feature]
            index_list.append(i)
            doc_count += 1
            feature_map[feature] = (doc_count, current_index, index_list)
            
    return (feature_list, feature_map)
                

###############################################################################
def _get_docs_with_feature(feature, feature_map, group):
    """
    Return _id values of all group entries having the given feature.
    """

    oid_list = []

    assert feature in feature_map
    doc_count, current_index, index_list = feature_map[feature]
    for index in range(len(group)):
        if index in index_list:
            oid_list.append(group[index])
            
    return oid_list


###############################################################################
def _generate_logical_result(eval_result, group, doc_map, feature_map):
    """
    Generate the groups of output documents that result from the evaluation of
    a logical expression.

    The parameters are:

        eval_result: namedtuple containing the evaluation results
        group: list of _id values for all docs in the result group
        doc_map: dict mapping document _id values to the actual document data
        feature_map: dict mapping nlpql_feature -> triplet consisting of
                     (doc_count, current_index, index_list)

    A list of lists is returned as the result. Each inner list contains
    MongoDB _id values and represents a single result group in the overall
    result.

    The individual result groups are composed by 'evaluating' the postfix
    form of the logic expression.

    This code does NOT compute the full Cartesian product for the result set.
    It instead computes the minimal set of documents that includes all
    result data.

    """

    if _TRACE: print('Called generate_logical_result')
    
    postfix_tokens = eval_result.postfix_tokens
    assert len(postfix_tokens) > 1

    # only strings get pushed onto the evaluation stack
    stack = []

    # list of lists of _id values; each sublist is a group of result docs
    oid_list = []

    counter = 0
    for token in postfix_tokens:
        match = _regex_logic_operator.match(token)
        if not match:
            stack.append(token)
            if _TRACE: print('\tPushed postfix token "{0}"'.format(token))
        else:
            if 'not' == token:
                operand = stack.pop()
                assert False # support for logicval 'not' is TBD
                #result = _mongo_logic_format(token, operand)
            else:
                operator, n = _decode_operator(token)

                # pop n operands from the stack
                operands = []
                new_feature_name = ''
                for i in range(n):
                    operand = stack.pop()
                    operands.append(operand)
                operands.reverse()
                if _TRACE: print('\tOperands: {0}'.format(operands))

                # construct a new feature name for this operation
                new_feature_name = _make_temp_feature(counter,
                                                      operands,
                                                      eval_result.expr_index,
                                                      _TMP_FEATURE_LOGIC)
                if _TRACE: print('\tNew feature name: {0}'.format(new_feature_name))
                counter += 1

                # An 'ntuple' is a group of result documents; it is one of the
                # inner lists in the result list-of-lists that this function
                # returns. An evaluation of an OR or an AND usually generates
                # multiple ntuples.
                ntuples = []
                if 'or' == operator:
                    for feature in operands:
                        match = _regex_temp_nlpql_logic_feature.match(feature)
                        if not match:
                            # simple feature
                            if feature in feature_map:
                                oids = _get_docs_with_feature(feature,
                                                              feature_map,
                                                              group)
                                for oid in oids:
                                    # each OR'd feature is an ntuple in itself
                                    ntuples.append([oid])
                        else:
                            # result from prior logical operation; accept as is
                            ntuples.extend(oid_list)
                else: # 'and' == operator

                    # a logical AND requires all features to exist
                    max_count = 0
                    all_exist = True
                    for feature in operands:
                        if isinstance(feature, str) and not feature in feature_map:
                            all_exist = False
                            break
                        else:
                            feature_count,index,index_list = feature_map[feature]
                            if feature_count > max_count:
                                max_count = feature_count
                    if not all_exist:
                        stack.append('None')
                        continue

                    # Generate 'max_count' ntuples; each ntuple has len(operands)
                    # features. For those features appearing fewer than max_count
                    # times, repeat until max_count has been reached.
                    while len(ntuples) < max_count:
                        ntuple = []
                        for feature in operands:
                            v = feature_map[feature]
                            feature_count = v[0]
                            current_index = v[1]
                            index_list    = v[2]
                            ntuple.append(group[index_list[current_index]])
                            current_index += 1
                            if current_index >= feature_count:
                                current_index = 0
                            feature_map[feature] = (feature_count, current_index, index_list)
                        ntuples.append(ntuple)

                # the newly-generated ntuples replace the previous state
                oid_list = []
                oid_list = copy.deepcopy(ntuples)

                if _TRACE:
                    print('OID LIST (end): ')
                    print(oid_list)
                    print()

                # replace the old features in the feature_map with the new
                new_oid_count = 0
                new_indices = []
                for feature in operands:
                    if feature in feature_map:
                        feature_count, current_index, index_list = feature_map[feature]

                        # remove ole feature entry
                        del feature_map[feature]

                        # accumulate count and indices for the old features,
                        # which now have the label 'new_feature_name'
                        new_oid_count += feature_count
                        new_indices.extend(index_list)

                # add a new entry for the new features
                feature_map[new_feature_name] = (new_oid_count, 0, copy.deepcopy(new_indices))

            # the new feature name now replaces what was popped
            stack.append(new_feature_name)

    # should only have a single element left on the stack, the result
    assert 1 == len(stack)
    return oid_list
    

###############################################################################
def flatten_logical_result(eval_result, mongo_collection_obj):
    """
    Generate the groups of MongoDB _id values representing the result set.
    Most of the work is done by _generate_logical_result(), which has more
    explanation in its docstring and in its code.
    """

    if _TRACE: print('Called flatten_logical_result')
    
    assert EXPR_TYPE_LOGIC == eval_result.expr_type

    doc_ids = eval_result.doc_ids
    group_list  = eval_result.group_list
    
    if _TRACE:
        print('\tFinal NLPQL feature: {0}'.format(eval_result.nlpql_feature))
        print('\tExpression text: {0}'.format(eval_result.expr_text))
        print('\tPostfix tokens: {0}'.format(eval_result.postfix_tokens))
        print('\tDocument count: {0}'.format(len(doc_ids)))
        print('\tGroup count:    {0}'.format(len(group_list)))

    # query for these documents
    cursor = mongo_collection_obj.find({'_id': {'$in': doc_ids}})

    # load all docs into a map for quick access to data
    doc_map = {}
    for doc in cursor:
        # ObjectId is the key
        oid = doc['_id']
        doc_map[oid] = doc

    # list of ObjectID lists, one list for each group
    oid_lists = []
        
    # each group is a list of ObjectId values
    group_index = 0
    for group in group_list:

        # feature_list: (feature, count) tuples, sorted by decreasing count
        # feature_map: (feature_count, cur_index, [feature_indices_in_group]

        # assign indices to each feature
        feature_list, feature_map = build_feature_map(group, doc_map)

        if _TRACE:
            print('\n\n<<Group index: {0}>>'.format(group_index))
            print('Expression: "{0}"'.format(eval_result.expr_text))
            print('   Postfix: {0}'.format(eval_result.postfix_tokens))
            for oid in group:
                doc = doc_map[oid]
                feature = doc['nlpql_feature']
                subj = doc['subject']
                rid = doc['report_id']
                print('\t{0}: {1:16}\tsubject: {2}\treport_id: {3}'.
                      format(oid, feature, subj, rid))
            for feature, feature_count in feature_list:
                doc_count, current_index, index_list = feature_map[feature]
                assert doc_count == len(index_list)
                print("\tIndices of feature '{0}': {1}".format(feature, index_list))
            print()

        # 'evaluate' the postfix expression and generate the result set

        if 1 == len(eval_result.postfix_tokens):
            # take all the docs in the group with this feature
            feature = eval_result.postfix_tokens[0]
            if _TRACE: print('SINGLE FEATURE: {0}'.format(feature))
            oid_list = _get_docs_with_feature(feature, feature_map, group)
            if _TRACE: print('OID LIST: {0}'.format(oid_list))
            # a single NLPQL feature means single-document groups
            oid_list = [[oid] for oid in oid_list]
        else:
            oid_list = _generate_logical_result(eval_result, group, doc_map, feature_map)
            
        oid_lists.append(oid_list)
        
        if _TRACE:
            print('RESULTS: ')
            for l in oid_list:
                assert isinstance(l, list)
                suffixes = []
                features = []
                for oid in l:
                    doc = doc_map[oid]
                    oid_suffix = str(oid)[-4:]
                    doc_feature = doc['nlpql_feature']
                    suffixes.append(oid_suffix)
                    features.append(doc_feature)
                zipped = list(zip(suffixes, features))
                print('\t{0}'.format(zipped))
        
        group_index += 1
                
    return doc_map, oid_lists
    

###############################################################################
def _occurrence_count(pattern, text):
    """
    Return the number of occurrences of pattern in text.
    """

    count = 0
    
    pos = text.find(pattern)
    while -1 != pos:
        count += 1
        pos = text.find(pattern, pos + len(pattern))

    return count


###############################################################################
def is_valid(parse_result, name_list=None):
    """
    Check the expression and determine whether it can be evaluated with
    this module. All tokens must be recognized entities. If a token is
    unrecognized, try to separate it into a list of known names separated by
    logic operators. If that fails, the expression cannot be evaluated.

    Assumption: the expression parser has already parsed the expression,
    and that the infix parse result is used in this function.

    This function returns an empty string if it finds an unrecognized token.
    Otherwise it returns an infix string for further processing.
    """

    if _TRACE: print('Called is_valid')
    
    infix_tokens = parse_result.split()

    # check each token and ensure that it can be recognized as an expected form
    new_tokens = []
    for token in infix_tokens:
        if _LEFT_PARENS == token or _RIGHT_PARENS == token:
            new_tokens.append(token)
            continue
        match = _regex_variable.match(token)
        if match:
            new_tokens.append(token)
            continue
        if token in NLPQL_EXPR_OPSTRINGS:
            if token in EXPR_UNSUPPORTED_OPSTRINGS:
                print('\n*** Unsupported operator: "{0}" ***\n'.format(token))
                return _EMPTY_STRING
            new_tokens.append(token)
            continue
        match = _regex_numeric_literal.match(token)
        if match:
            new_tokens.append(token)
            continue
        match = _regex_nlpql_feature.match(token)
        if not match:
            print('\tTOKEN OF UNKNOWN TYPE: {0}'.format(token))
            return _EMPTY_STRING

        # if here, the token matched the format for an NLPQL feature

        # validate the token against the list of known names, if possible
        if name_list is not None and token in name_list:
            new_tokens.append(token)
            continue
        elif name_list is None:
            # accept all tokens if no list to validate against
            new_tokens.append(token)
            continue
        else:
            # the token was not found in the list of known names
            # try to resolve into known_name + logic_op + remainder
            print('\tUnrecognized token: "{0}", resolving...'.format(token))
            # parenthesize its replacement, if any
            new_tokens.append(_LEFT_PARENS)
            while True:
                found_it = False
                start_token = token
                for name in name_list:
                    print('\tSearching for {0} in {1}'.format(name, token))
                    if token.startswith(name):
                        print('\t\tFound: {0}'.format(name))
                        new_tokens.append(name)
                        token = token[len(name):]
                        print('\t\tRemaining token: ->{0}<-'.format(token))
                        if len(token) > 0:
                            # need logic op
                            for lop in NLPQL_EXPR_LOGIC_OPERATORS:
                                if token.startswith(lop):
                                    print('\t\tFound logic op: {0}'.format(lop))
                                    new_tokens.append(lop)
                                    token = token[len(lop):]
                                    print('\t\tRemaining token: ->{0}<-'.format(token))
                                    found_it = True
                        else:
                            # no more text to match
                            found_it = True        

                        break
                    
                if not found_it or start_token == token:
                    print('\tResolution failed for token "{0}"'.format(token))
                    return _EMPTY_STRING

                if 0 == len(token):
                    # fix is complete
                    new_tokens.append(_RIGHT_PARENS)
                    break

    # if here, resolved all the tokens
    new_infix_expression = ' '.join(new_tokens)
    if _TRACE: print('\tNEW INFIX EXPRESSION: {0}'.format(new_infix_expression))
    return new_infix_expression


###############################################################################
def parse_expression(nlpql_infix_expression, name_list=None):
    """
    Parse the NLPQL expression and evaluate any literal subexpressions.
    Check the result for validity. Return a fully-parenthesized expression
    if the expression is valid and can be evaluated, or an empty string
    if not.
    """

    if _TRACE: print('Called parse_expression')

    lexer = NlpqlExpressionLexer()
    parser = NlpqlExpressionParser()    
    
    # parse the infix expression and get a fully-parenthesized infix result
    try:
        infix_result = parser.parse(lexer.tokenize(nlpql_infix_expression))
    except SyntaxError as e:
        print('\tSyntaxError exception in parse')
        print('\tmsg: {0}'.format(e.msg))
        return _EMPTY_STRING
        
    if _TRACE: print('\tParse result: "{0}"'.format(infix_result))

    # evaluate any subexpressions consisting only of numeric literals
    infix_result = _evaluate_literals(infix_result)
    if _TRACE: print('  Evaluated literals: "{0}"'.format(infix_result))

    # check for validity and try to correct if invalid
    infix_result = is_valid(infix_result, name_list)
    if 0 == len(infix_result):
        return _EMPTY_STRING

    return infix_result
    

###############################################################################
def generate_expressions(final_nlpql_feature, parse_result):
    """
    Parse the NLPQL expression, evaluate any literal subexpressions, and
    resolve whateve remains into a set of subexpressions of either
    math or logic type. The primitive subexpressions are returned in a list
    of ExpressionObject namedtuples.
    """

    global _EXPR_INDEX
    
    if _TRACE:
        print('Called generate_expressions')
        print('\tExpression index: {0}'.format(_EXPR_INDEX))    

    # determine the expression type, need math, logic, or mixed
    expr_type = _expr_type(parse_result)
    
    if EXPR_TYPE_UNKNOWN == expr_type:
        print('\tExpression has unknown type: "{0}"'.
              format(nlpql_infix_expression))
        return []

    # the objects to be evaluated
    expression_object_list = []
    
    if EXPR_TYPE_MATH == expr_type:
        expr_obj = ExpressionObject(
            expr_type     = EXPR_TYPE_MATH,
            nlpql_feature = final_nlpql_feature,
            expr_text     = parse_result,
            expr_index    = _EXPR_INDEX
        )
        expression_object_list.append(expr_obj)

    elif EXPR_TYPE_LOGIC == expr_type:
        expr_obj = ExpressionObject(
            expr_type     = EXPR_TYPE_LOGIC,
            nlpql_feature = final_nlpql_feature,
            expr_text     = parse_result,
            expr_index    = _EXPR_INDEX
        )
        expression_object_list.append(expr_obj)
    
    elif EXPR_TYPE_MIXED == expr_type:

        # resolve mixed expressions into pure subexpressions
        subexpressions, final_infix_expr = _resolve_mixed(parse_result, _EXPR_INDEX)

        # the new infix expression includes the subexpression temporaries
        final_infix_expr = _remove_unnecessary_parens(final_infix_expr)        

        # ensure the final expression is of logic type
        final_expr_type = _expr_type(final_infix_expr)
        assert EXPR_TYPE_LOGIC == final_expr_type

        # check types of all subexpressions
        for sub_feature, sub_expr in subexpressions:
            subexpr_type = _expr_type(sub_expr)
            if EXPR_TYPE_MATH == subexpr_type or EXPR_TYPE_LOGIC == subexpr_type:
                expr_obj = ExpressionObject(
                    expr_type     = subexpr_type,
                    nlpql_feature = sub_feature,
                    expr_text     = sub_expr,
                    expr_index    = _EXPR_INDEX
                )
                expression_object_list.append(expr_obj)
            else:
                # subexpression did not resolve to primitive type
                print('Subexpression resolution failure: '.format(sub_expr))
                print('\t"{0}"'.format(sub_expr))
                return []

        # append the final logic expression
        expr_obj = ExpressionObject(
            expr_type     = EXPR_TYPE_LOGIC,
            nlpql_feature = final_nlpql_feature,
            expr_text     = final_infix_expr,
            expr_index    = _EXPR_INDEX
        )
        expression_object_list.append(expr_obj)
        
        if _TRACE:
            print('SUBEXPRESSION TABLE: ')
            for expr_obj in expression_object_list:
                print("\t\tnlpql_feature: {0}, expr_type: {1}, expr_index: {2}, expression: '{3}'".
                      format(expr_obj.nlpql_feature,
                             expr_obj.expr_type,
                             expr_obj.expr_index,
                             expr_obj.expr_text))

    _EXPR_INDEX += 1
    
    return expression_object_list


###############################################################################
def evaluate_expression(expr_obj,
                        job_id,
                        context_field,
                        mongo_collection_obj):
    """
    Evaluate a single ExpressionObject namedtuple.
    """

    if _TRACE: print('Called evaluate_expression')

    assert EXPR_TYPE_MATH == expr_obj.expr_type or \
        EXPR_TYPE_LOGIC == expr_obj.expr_type

    if EXPR_TYPE_MATH == expr_obj.expr_type:
        result = _eval_math_expr(job_id,
                                 expr_obj,
                                 mongo_collection_obj)

    else:
        result = _eval_logic_expr(job_id,
                                  context_field,
                                  expr_obj,
                                  mongo_collection_obj)

    return result
