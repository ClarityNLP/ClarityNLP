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

There are many more examples in the expression evaluator test program,
'expr_tester.py'.

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

Examples of how to use the expression evaluator can be found in the test
program 'expr_tester.py'.


TESTING:


Test code has been moved to 'expr_tester.py'.



LIMITATIONS:


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
from claritynlp_logging import log, ERROR, DEBUG

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
EXPR_UNSUPPORTED_OPSTRINGS = []#['NOT']

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

# regex that identifies a temporary NLPQL feature, exportable
regex_temp_nlpql_feature = re.compile(r'\A(math|logic)_\d+_\d+\Z')


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 8
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

# logic op after postfix conversion, includes tokens such as or3, and5, etc.
_regex_logic_operator = re.compile(r'\A((and|or)(\d+)?|not)\Z')

# identifies a temp logic feature, not exported
_regex_temp_nlpql_logic_feature = re.compile(r'\Alogic_\d+_\d+\Z')

# identifies a temp math feature, not exported
_regex_temp_math_feature = re.compile(r'\Amath_\d+_\d+\Z')


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
_MONGO_OPS = {
    'not':'$not',
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
_UNARY_OPS = ['not']

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

    if _TRACE:
        log('Called _is_math_expr...')
        log('\tinfix_tokens: {0}'.format(infix_tokens))

    tmp_feature_count = 0
    nlpql_feature_set = set()
    value_set = set()

    for token in infix_tokens:
        #log('\t[_is_math_expr] token "{0}"'.format(token))
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
        if _TRACE: log('\tNot a math expression')
        return False

    nlpql_feature_count = len(nlpql_feature_set)

    is_math_expr = False
    if 1 == nlpql_feature_count:
        is_math_expr = True
    
    if _TRACE:
        log('\tIs a math expression: {0}'.format(is_math_expr))
    return is_math_expr


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
    equivalent postfix form. Parentheses may also be present as separate tokens
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
def _make_nary(postfix_tokens):
    """
    Find instances of n-ary AND and n-ary OR and replace with ORn and ANDn,
    where 'n' is an integer literal.

    For instance, the postfix string

         A B or C or D or

    will be replaced with

         A B C D or4

    All tokens are assumed to be lowercase.
    """

    if _TRACE: log('calling _make_nary')
    
    postfix_string = ' '.join(postfix_tokens)
    if _TRACE: log('\tStarting postfix: {0}'.format(postfix_tokens))

    matches = []
    iterator = _regex_nary_or.finditer(postfix_string)
    for match in iterator:
        matching_text = match.group()
        if _TRACE:
            log('\tNARY MATCH (or): ->{0}<-'.format(matching_text))
        matching_text = re.sub(r'\bor', '', matching_text)
        matching_text = re.sub(r'\s+', ' ', matching_text)
        matching_text += 'or'
        n_value = _count_spaces(matching_text)
        matching_text = matching_text + '{0}'.format(n_value)
        if _TRACE:
            log('\tAFTER SUB: ->{0}<-'.format(matching_text))
        matches.append( (match.start(), match.end(), matching_text))

    iterator = _regex_nary_and.finditer(postfix_string)
    for match in iterator:
        matching_text = match.group()
        if _TRACE:
            log('\tNARY MATCH (and): ->{0}<-'.format(matching_text))
        matching_text = re.sub(r'\band', '', matching_text)
        matching_text = re.sub(r'\s+', ' ', matching_text)
        matching_text += 'and'
        n_value = _count_spaces(matching_text)
        matching_text = matching_text + '{0}'.format(n_value)
        if _TRACE:
            log('\tAFTER SUB: ->{0}<-'.format(matching_text))
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

    if _TRACE: log('Called _remove_unnecessary_parens')
    
    # return if no parens
    pos = infix_expression.find(_LEFT_PARENS)
    if -1 == pos:
        return infix_expression

    if _TRACE: log('\t  Infix baseline: "{0}"'.format(infix_expression))
    
    infix_tokens = infix_expression.split()
    
    # get baseline postfix expression
    postfix_tokens = _infix_to_postfix(infix_tokens)
    postfix_baseline = ' '.join(postfix_tokens)
    if _TRACE: log('\tPostfix baseline: "{0}"'.format(postfix_baseline))

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
        log('\t    Parens pairs: {0}'.format(pairs))
            
    for i in range(len(pairs)):

        left, right, depth = pairs[i]
        infix_tokens_save = copy.deepcopy(infix_tokens)

        # remove this pair of parens, convert to postfix, and see if changed
        del infix_tokens[right]
        del infix_tokens[left]
        trial_infix_expr = ' '.join(infix_tokens)
        if _TRACE:
            log('\t Removing parens: left={0}, right={1}'.format(left, right))
            log('\tTrial infix expr: {0}'.format(trial_infix_expr))

        postfix = _infix_to_postfix(infix_tokens)
        postfix = ' '.join(postfix)
        if _TRACE:
            log('\t   Trial postfix: "{0}"'.format(postfix))

        if postfix != postfix_baseline:
            # removal changed postfix result, so restore these parens
            if _TRACE: log('\t   Postfix CHANGED, restoring parens.')
            infix_tokens = infix_tokens_save            
        else:
            # removed nonessential parens
            infix_expression = trial_infix_expr
            if _TRACE:
                log('\t   Postfix MATCHED, removing parens.')
                log('\t  NEW INFIX EXPR: {0}'.format(infix_expression))
            
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
                    log('\tRemaining parens pairs: {0}'.format(remaining_pairs))
            
    if _TRACE:
        log('\tDONE')
        log('\tEssential parens: "{0}"'.format(infix_expression))
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
        log('\t[_decode_operator] Found operator "{0}", n == {1}'.
              format(operator, n))

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
def _make_temp_feature(counter,
                       expr_index,
                       math_or_logic=_TMP_FEATURE_MATH):
    """
    Create a unique NLPQL feature name for a subexpression.
    This new name becomes the 'nlpql_feature' label attached to the
    subexpression.

    If this code is changed, the code in _is_temp_feature needs to be changed
    to match.
    """
    
    if _TRACE:
        log('Called _make_temp_feature')
        #log('\t    tokens: {0}'.format(token_list))
        log('\texpr_index: {0}, counter: {1}'.format(expr_index, counter))

    if _TMP_FEATURE_MATH == math_or_logic:
        label = 'math_{0}_{1}'.format(expr_index, counter)
    else:
        label = 'logic_{0}_{1}'.format(expr_index, counter)
    
    if _TRACE:
        log('\t New label: {0}'.format(label))

    assert _is_nlpql_feature(label)
    assert _is_temp_feature(label)
    return label


###############################################################################
def _merge_math_tokens(
        tokens,            # list of infix tokens
        math_expressions,  # dict: math_tmp_feature => (expression_str, feature)
        expr_index,        # index of expr in the NLPQL file
        counter):          # int, used for tmp feature creation
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

    if _TRACE:
        log('Called _merge_math_tokens...')
        log('\tTokens: {0}'.format(tokens))
        log('\tMath_expressions: ')
        for k,v in math_expressions.items():
            log('\t\t{0} => {1}'.format(k,v))

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

            if _TRACE:
                log('\tCandidate tokens: {0}'.format(expr_tokens))
                log('\t\tAll math: {0}'.format(all_math_tokens))
            
            if all_math_tokens:                
                # can merge into single expression if single nlpql_feature
                # and multiple tokens
                if _TRACE:
                    log('\tMerging these tokens: {0}'.format(expr_tokens))
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

                    # check if preceded by NOT; if so, include in the expr
                    if len(stack) > 0 and 'NOT' == stack[-1]:
                        if _TRACE: log('\tExpr is preceded by NOT')
                        nlpql_expression = 'NOT ( ' + nlpql_expression + ' )'
                        # pop the NOT operator from the stack
                        stack.pop()
                    
                    nlpql_feature = _make_temp_feature(counter, expr_index)
                    math_expressions[nlpql_feature] = (nlpql_expression, feature)
                    counter += 1

                    # push back on stack with no parens
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

            if _TRACE:
                log('\tCurent stack: ')
                log('\t\t{0}'.format(stack))
                
    new_infix_expr = ' '.join(stack)
    
    if _TRACE:
        log('\tMerge result: {0}'.format(new_infix_expr))
        log('\tMath_expressions: ')
        for k,v in math_expressions.items():
            log('\t\t{0} => {1}'.format(k,v))

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
    original expression containing the subexpression substitutions. All of 
    these subexpressions have type EXPR_TYPE_MATH, so that the overall result
    is a pure logic expression involving the substituted symbols.
    """

    if _TRACE:
        log('Called _resolve_mixed')
        log('\tinfix expression: {0}'.format(infix_expression))

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

                # found a math expression; check to see if preceded by 'not'
                if len(stack) > 0 and 'NOT' == stack[-1]:
                    # prefix the NOT token and surround expr with parens
                    nlpql_expression = 'NOT ( ' + nlpql_expression + ' )'
                    expr_tokens = nlpql_expression.split()
                    is_math = _is_math_expr(expr_tokens)
                    # pop the not operator from the stack
                    stack.pop()

                    if _TRACE:
                        log('\tFound math expr preceded by NOT')                        
                        log('\t\tis_math: {0}'.format(is_math))
                        log('\t\tNew expression: "{0}"'.format(nlpql_expression))
                        log('\t\tNew expr_tokens: {0}'.format(expr_tokens))
                    
                # if single parenthesized token, push with no parens
                if 1 == len(expr_tokens):
                    stack.append(expr_tokens.pop())
                else:
                    # push replacement token with no parens
                    feature = feature_set.pop()
                    nlpql_feature = _make_temp_feature(counter, expr_index)
                    stack.append(nlpql_feature)
                    math_expressions[nlpql_feature] = (nlpql_expression, feature)
                    counter += 1
                    if _TRACE:
                        log('\tReplacing "{0}" with feature "{1}"'.
                              format(nlpql_expression, nlpql_feature))
            else:
                # push logic operands with parens
                stack.append(_LEFT_PARENS)
                for et in expr_tokens:
                    stack.append(et)
                stack.append(_RIGHT_PARENS)
                
    new_infix_expr = ' '.join(stack)
    if _TRACE: log('\tEXPR AFTER RESOLUTION: {0}'.format(new_infix_expr))

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

    log('RESULTS for NLPQL feature "{0}": '.format(nlpql_feature))
    count = 0
    for doc in cursor:
        log('\t{0}: value: {1}\tsubject: {2}\treport_id: {3}'.
              format(doc['_id'],
                     doc['value'],
                     doc['subject'],
                     doc['report_id']))

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
    log('RESULTS for NLPQL feature "{0}": '.format(nlpql_feature))
    count = 0
    for group in all_doc_groups:
        for doc in group:
            log('\t{0}: {1:16}\tsubject: {2}\treport_id: {3}'.
                  format(doc['_id'],
                         doc['nlpql_feature'],
                         doc['subject'],
                         doc['report_id']))
            count += 1
        log()
    

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

    if _TRACE: log('Called _convert_variables')
    
    variables, nlpql_feature_set, field_set = _extract_variables(infix_expr)
    if _TRACE: log('\tVARIABLES: {0}'.format(variables))

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
    if _TRACE: log('\tConverted expression: "{0}"'.format(new_expr))

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
        log('Called _mongo_math_format with operator ' +\
              '"{0}", op1: "{1}", op2: "{2}"'.format(operator, op1, op2))
    
    if 'not' == operator:
        result = {'$not': [_format_math_operand(op1)]}
    else:
        opstring = '{0}'.format(_MONGO_OPS[operator])
        operand1 = _format_math_operand(op1)
        operand2 = _format_math_operand(op2)

        # The operators $gt, $gte, $lt, $lte are affected by the presence of
        # non-existent fields. Explicit checks for None (null in Mongo-speak)
        # need to be inserted and the comparisons rigged to return False.
        # Mongo handles $not and $ne correctly.

        if 'lt' == operator or 'lte' == operator:
            # null fields: check to see if operand2 is < max_float, False
            result = {opstring: [{'$ifNull': [operand1, sys.float_info.max]}, operand2]}
        elif 'gt' == operator or 'gte' == operator:
            # null fields: check to see if operand2 is > min_float, False
            result = {opstring: [{'$ifNull': [operand1, sys.float_info.min]}, operand2]}
        else:
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
        log('Called _eval_math_expr')
        log('\tExpression: "{0}"'.format(expr_obj.expr_text))

    final_nlpql_feature = expr_obj.nlpql_feature
    infix_expr = expr_obj.expr_text
        
    # get rid of extraneous parentheses
    infix_expr = _remove_unnecessary_parens(infix_expr)

    # rewrite expression and extract NLPQL feature and field names
    new_expr, nlpql_feature, field_list = _convert_variables(infix_expr)

    # convert to postfix
    infix_tokens = new_expr.split()
    postfix_tokens = _infix_to_postfix(infix_tokens)
    if _TRACE: log('\tpostfix: {0}'.format(postfix_tokens))

    # 'evaluate' to generate MongoDB aggregation commands
    stack = []
    for token in postfix_tokens:
        if not _is_operator(token):
            stack.append(token)
            if _TRACE: log('\t(M) Pushed postfix token "{0}"'.format(token))
        else:
            if token in _UNARY_OPS:
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
        log('MATH_OP PIPELINE STAGE: ')
        log(op_stage)
        log()

    # initial filter, match on job_id and check nlpql_feature field
    initial_filter = {
        "$match": {
            "job_id":job_id,
            "nlpql_feature": {"$exists":True, "$ne":None},
        }
    }

    # if only a single field is used, remove any expressions in which this
    # field does not exist
    if 1 == len(field_list):
        f = field_list[0]
        initial_filter['$match'][f] = {"$exists":True, "$ne":None}
    else:
        # this case handled explicitly by the '$isNull' checks for $lt, $lte,
        # $gt, $gte in _mongo_math_format
        pass

    pipeline = [
        initial_filter,
        op_stage,
    ]

    if _TRACE:
        log('FULL AGGREGATION PIPELINE: ')
        log(pipeline)
        log()

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
        log('Called _eval_logic_expr')
        log('\tExpression: "{0}"'.format(expr_obj.expr_text))

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
    postfix_tokens = _make_nary(postfix_tokens)
    
    if _TRACE: log('\tpostfix: {0}'.format(postfix_tokens))

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
                if _TRACE: log('\t(L) Pushed postfix token "{0}"'.format(token))
            else:
                # only binary not is supported by the parser
                # the parser converted "A NOT B" to "A AND NOT B"
                # with this trick the _mongo_logic_format code still works
                if 'not' == token:
                    operand = stack.pop()
                    result = _mongo_logic_format(token, [operand])
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
        log('LOGIC_OP PIPELINE STAGE: ')
        log(op_stage)
        log()

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
        log('FULL AGGREGATION PIPELINE: ')
        log(pipeline)
        log()

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
def _remove_negated_subexpressions(postfix_tokens):
    """
    Remove negated subexpressions from the input postfix tokens.
    For instance, the string '(hasTachycardia AND hasDyspnea) NOT hasRigors'
    looks like this in postfix:
    
        hasTachycardia hasDyspnea AND hasRigors NOT

    Removing the negated expression gives this result:

        hasTachycardia hasDyspnea AND
    """
    TOKEN_NOTAND = 'notand'

    if _TRACE:
        log('Calling _remove_negated_subexpressions...')
        log('\tinitial postfix tokens: {0}'.format(postfix_tokens))
    
    new_tokens = []

    # The expression parser substitutes 'AND NOT' for each occurrence of 'NOT',
    # to simplify subsequent processing. In postfix this becomes 'NOT AND'.
    # Replace all occurrences of 'NOT AND' with 'NOTAND' to simplify the
    # removal process.
    token_index = 0
    while token_index < len(postfix_tokens):
        token = postfix_tokens[token_index]
        if 'not' == token:
            token = TOKEN_NOTAND
            token_index += 1
            assert 'and' == postfix_tokens[token_index]
        new_tokens.append(token)
        token_index += 1

    # Now 'evaluate' the token stream and remove arguments of the 'NOTAND'
    # operator.
    stack = []
    for token in new_tokens:
        if TOKEN_NOTAND == token:
            # pop the top of the stack and discard
            assert len(stack) > 0
            stack.pop()
            continue
        match = _regex_logic_operator.match(token)
        if match:
            # pop n operands, join in proper order with commas,
            # append operator token, and push on stack
            operator, n = _decode_operator(token)
            operands = []
            for i in range(n):
                operand = stack.pop()
                operands.append(operand)
            operands.reverse()
            operands.append(token)
            eval_string = ','.join(operands)
            stack.append(eval_string)
        else:
            stack.append(token)

    assert 1 == len(stack)
    new_tokens = stack[0].split(',')

    if _TRACE:
        log('\t  final postfix tokens: {0}'.format(new_tokens))

    return new_tokens


###############################################################################
def _generate_logical_result(
        postfix_tokens,  # expression in postfix form, negations removed
        expr_index,      # index of the current expression in the NLPQL file
        group,           # result of MongoDB $group operation on context var
                         # all members of the group share the same value of
                         # the context variable
        doc_map,         # dict: _id => document data
        feature_map):    # dict: nlpql_feature => triplet consisting of
                         #    (doc_count, current_index, index_list)
    """
    Generate the groups of output documents that comprise the output from
    the evaluation of a logical expression. This process is explained more
    fully in the documentation for the expression evaluator.

    A list of lists is returned as the result. Each inner list contains
    MongoDB _id values, and it represents the output data for a single
    input group, i.e. for a single patient or document, depending on the
    context variable.

    This code does NOT compute the full Cartesian product for the result set.
    It instead computes the minimal set of documents that includes all
    result data. See the documentation for more on this.
    """

    if _TRACE:
        log('Called generate_logical_result')
        log('\tPostfix tokens: {0}'.format(postfix_tokens))
        log('\tFeature map: ')
        for k,v in feature_map.items():
            log('\t\t{0} => {1}'.format(k,v))

    # scan the postfix tokens and verify that 'not' has been removed
    for token in postfix_tokens:
        assert 'not' != token.lower()

    assert len(postfix_tokens) > 1

    # The code below will push and pop lists of lists of MongoDB _id values
    # on this stack. These _id values are also known as oid values, hence
    # the terminology below.
    stack = []
    
    for token in postfix_tokens:
        match = _regex_logic_operator.match(token)
        if not match:
            # this is an nlpql_feature, an operand of an AND or OR logic op
            if token in feature_map:
                oid_list = _get_docs_with_feature(token, feature_map, group)
            else:
                oid_list = []
            # each oid becomes a single-item list to push back
            new_lists = [ [oid] for oid in oid_list]
            stack.append(new_lists)
        else:
            operator, n = _decode_operator(token)

            # pop n operands, which are lists of OID lists
            operands = []
            for i in range(n):
                operand = stack.pop()
                operands.append(operand)

            # reverse the operand order to match the expression
            operands.reverse()
            
            if 'or' == operator:
                # new lists == all operands appended together
                new_lists = []
                for op in operands:
                    new_lists.extend(op)
                stack.append(new_lists)
            else:
                assert 'and' == operator

                # all operands must be nonempty for logical AND
                all_nonempty = True
                for op in operands:
                    if 0 == len(op):
                        all_nonempty = False
                        break
                if not all_nonempty:
                    stack.append([])
                    continue

                # Construct the AND result, which is a list of lists of oid
                # values.
                #
                # length of outer list == length of longest operand
                # length of inner lists = operand count == len(operands)
                #
                # This code 'tiles' the individual operands to generate the
                # result, producing a miminal representation of the data. See
                # the documentation for more. This is emphatically NOT the
                # Cartesian product, which would explode the result data and
                # generate lots of needless redundancy.
                #
                # In short, this output generation code produces the MINIMAL
                # amount of redundancy for a given context variable group.
                
                meta = [ (len(op), op) for op in operands]
                meta = sorted(meta, key=lambda x: x[0], reverse=True)

                # if _TRACE:
                #     log('\tMETA: ')
                #     for m in meta:
                #         log('\t{0}'.format(m))
                
                new_lists = []
                inner_length = len(operands)
                outer_length = meta[0][0]
                for i in range(outer_length):
                    new_lists.append([])

                for num, operand in meta:
                    index = 0
                    for i in range(outer_length):
                        new_lists[i].extend(operand[index])
                        index += 1
                        if index >= num:
                            index = 0
                            
                stack.append(new_lists)

    # if _TRACE:
    #     log('STACK TOP (end): ')
    #     for i, l in enumerate(stack[-1]):
    #         log('\t[{0}]:\t{1}'.format(i, l))
    #     log()

    assert 1 == len(stack)
    return stack[-1]


###############################################################################
def flatten_logical_result(eval_result, mongo_collection_obj):
    """
    Generate the groups of MongoDB _id values representing the result set.
    Most of the work is done by _generate_logical_result(), which has more
    explanation in its docstring and in its code.
    """

    if _TRACE: log('Called flatten_logical_result')
    
    assert EXPR_TYPE_LOGIC == eval_result.expr_type

    doc_ids = eval_result.doc_ids
    group_list  = eval_result.group_list

    if _TRACE:
        log('\tFinal NLPQL feature: {0}'.format(eval_result.nlpql_feature))
        log('\tExpression text: {0}'.format(eval_result.expr_text))
        log('\tPostfix tokens: {0}'.format(eval_result.postfix_tokens))
        log('\tDocument count: {0}'.format(len(doc_ids)))
        log('\tGroup count:    {0}'.format(len(group_list)))

    # query for these documents
    cursor = mongo_collection_obj.find({'_id': {'$in': doc_ids}})

    # load all docs into a map for quick access to data
    features = set()
    doc_map = {}
    for doc in cursor:
        # ObjectId is the key
        oid = doc['_id']
        doc_map[oid] = doc

        if _TRACE:
            # count distinct features
            feature = doc['nlpql_feature']
            features.add(feature)

    if _TRACE:
        log('\tFEATURE SET: {0}'.format(features))

    # Remove negated subexpressions to simplify output generation, which needs
    # the postfix version of the expression. The MongoDB aggregation stage has
    # already removed the data.
    postfix_tokens = _remove_negated_subexpressions(eval_result.postfix_tokens)
        
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
            log('\n\n<<Group index: {0}>>'.format(group_index))
            log('Expression: "{0}"'.format(eval_result.expr_text))
            log('   Postfix: {0}'.format(eval_result.postfix_tokens))
            for oid in group:
                doc = doc_map[oid]
                feature = doc['nlpql_feature']
                subj = doc['subject']
                rid = doc['report_id']
                log('\t{0}: {1:16}\tsubject: {2}\treport_id: {3}'.
                      format(oid, feature, subj, rid))
            for feature, feature_count in feature_list:
                doc_count, current_index, index_list = feature_map[feature]
                assert doc_count == len(index_list)
                log("\tIndices of feature '{0}': {1}".format(feature, index_list))
            log()

        # 'evaluate' the postfix expression and generate the result set

        if 1 == len(postfix_tokens):
            # take all the docs in the group with this feature
            feature = postfix_tokens[0]
            if _TRACE: log('SINGLE FEATURE: {0}'.format(feature))
            oid_list = _get_docs_with_feature(feature, feature_map, group)
            if _TRACE: log('OID LIST: {0}'.format(oid_list))
            # a single NLPQL feature means single-document groups
            oid_list = [[oid] for oid in oid_list]
        else:
            oid_list = _generate_logical_result(
                postfix_tokens,
                eval_result.expr_index,
                group,
                doc_map,
                feature_map)
            
        oid_lists.append(oid_list)
        
        if _TRACE:
            log('RESULTS: ')
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
                log('\t{0}'.format(zipped))
        
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

    if _TRACE: log('Called is_valid')
    
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
                log('\n*** Unsupported operator: "{0}" ***\n'.format(token))
                return _EMPTY_STRING
            new_tokens.append(token)
            continue
        match = _regex_numeric_literal.match(token)
        if match:
            new_tokens.append(token)
            continue
        match = _regex_nlpql_feature.match(token)
        if not match:
            log('\tTOKEN OF UNKNOWN TYPE: {0}'.format(token))
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
            if _TRACE:
                log('\tUnrecognized token: "{0}", resolving...'.format(token))
            # parenthesize its replacement, if any
            new_tokens.append(_LEFT_PARENS)
            while True:
                found_it = False
                start_token = token
                for name in name_list:
                    if _TRACE: log('\tSearching for {0} in {1}'.format(name, token))
                    if token.startswith(name):
                        if _TRACE: log('\t\tFound: {0}'.format(name))
                        new_tokens.append(name)
                        token = token[len(name):]
                        if _TRACE: log('\t\tRemaining token: ->{0}<-'.format(token))
                        if len(token) > 0:
                            # need logic op
                            for lop in NLPQL_EXPR_LOGIC_OPERATORS:
                                if token.startswith(lop):
                                    if _TRACE: log('\t\tFound logic op: {0}'.format(lop))
                                    new_tokens.append(lop)
                                    token = token[len(lop):]
                                    if _TRACE: log('\t\tRemaining token: ->{0}<-'.format(token))
                                    found_it = True
                        else:
                            # no more text to match
                            found_it = True        

                        break
                    
                if not found_it or start_token == token:
                    log('\tResolution failed for token "{0}"'.format(token))
                    return _EMPTY_STRING

                if 0 == len(token):
                    # fix is complete
                    new_tokens.append(_RIGHT_PARENS)
                    break

    # if here, resolved all the tokens
    new_infix_expression = ' '.join(new_tokens)
    if _TRACE: log('\tNEW INFIX EXPRESSION: {0}'.format(new_infix_expression))
    return new_infix_expression


###############################################################################
def parse_expression(nlpql_infix_expression, name_list=None):
    """
    Parse the NLPQL expression and evaluate any literal subexpressions.
    Check the result for validity. Return a fully-parenthesized expression
    if the expression is valid and can be evaluated, or an empty string
    if not.
    """

    if _TRACE: log('Called parse_expression')

    lexer = NlpqlExpressionLexer()
    parser = NlpqlExpressionParser()    
    
    # parse the infix expression and get a fully-parenthesized infix result
    try:
        infix_result = parser.parse(lexer.tokenize(nlpql_infix_expression))
    except SyntaxError as e:
        log('\tSyntaxError exception in parse')
        log('\tmsg: {0}'.format(e.msg))
        return _EMPTY_STRING
        
    if _TRACE: log('\tParse result: "{0}"'.format(infix_result))

    # evaluate any subexpressions consisting only of numeric literals
    infix_result = _evaluate_literals(infix_result)
    if _TRACE: log('  Evaluated literals: "{0}"'.format(infix_result))

    # check for validity and try to correct if invalid
    infix_result = is_valid(infix_result, name_list)
    if 0 == len(infix_result):
        return _EMPTY_STRING

    return infix_result
    

###############################################################################
def generate_expressions(final_nlpql_feature, parse_result):
    """
    Parse the NLPQL expression, evaluate any literal subexpressions, and
    resolve whatever remains into a set of subexpressions of either
    math or logic type. The primitive subexpressions are returned in a list
    of ExpressionObject namedtuples.
    """

    global _EXPR_INDEX
    
    if _TRACE:
        log('Called generate_expressions')
        log('\tExpression index: {0}'.format(_EXPR_INDEX))    

    # determine the expression type, need math, logic, or mixed
    expr_type = _expr_type(parse_result)
    
    if EXPR_TYPE_UNKNOWN == expr_type:
        log('\tExpression has unknown type: "{0}"'.
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
                log('Subexpression resolution failure: '.format(sub_expr))
                log('\t"{0}"'.format(sub_expr))
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
            log('SUBEXPRESSION TABLE: ')
            for expr_obj in expression_object_list:
                log("\t\tnlpql_feature: {0}, expr_type: {1}, expr_index: {2}, expression: '{3}'".
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

    if _TRACE: log('Called evaluate_expression')

    assert EXPR_TYPE_MATH == expr_obj.expr_type or \
        EXPR_TYPE_LOGIC == expr_obj.expr_type

    # the job_id needs to be an integer
    job_id = int(job_id)
    
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
