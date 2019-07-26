#!/usr/bin/env python3
"""


OVERVIEW:


The code in this module searches a sentence for one or more query terms and
returns a JSON result containing any values associated with those terms. The
term list and the sentence are specified on the command line. Results are
returned only for values in the range [--min, --max].

Values are assumed to occur AFTER the query term. In general, the first
acceptable value occurring after the query term will be the one returned.

The default behavior is to do case-insensitive matching. Case-sensitive 
matching can be enabled with a command line option.


OUTPUT:


The set of JSON fields in the output includes:

        sentence             the sentence from which values were extracted
        terms                comma-separated list of query terms
        querySuccess         whether any query terms were found in the sentence
        measurementCount     number of values found
        measurements         array of results

            text             matching text of this value
            start            value starting char offset
            end              value ending char offset + 1
            condition        relation of query term to value; values are:
                             'APPROX', 'LESS_THAN', 'LESS_THAN_OR_EQUAL',
                             'GREATER_THAN', 'GREATER_THAN_OR_EQUAL',
                             'EQUAL', 'RANGE', FRACTION_RANGE'
            matchingTerm     the query term associated with this value
            x                matching value
            y                matching value
            minValue         mininum value of x and y, if neither is EMPTY_FIELD
            maxValue         maximum value of x and y, if neither is EMPTY_FIELD



All JSON results will have an identical number of fields. Any fields with a 
value of EMPTY_FIELD should be ignored. This will be the case for the y-field
for non-range results.

USAGE:

To use this code as an imported module, add the following lines to the
import list in the importing module:

        import json
        import value_extractor as ve

To find values in a sentence and capture the JSON result:

        json_string = ve.run(search_term_string, sentence, minval, maxval)

To unpack the JSON data:

        json_data = json.loads(json_string)
        result = ve.ValueResult(**json_data)

        The entries result.sentence, result.terms, result.querySuccess, and
        result.measurementCount and result.measurementList are now accessible.

To unpack the array of values:

        measurements = result.measurementList
        values = [ve.Value(**m) for m in measurements]

        for v in values:
            print(v.text)
            print(v.start)
            print(v.end)
            etc.

The 'run' function has the following signature:

        def run(term_string, sentence, str_minval=None, str_maxval=None,
            str_enumlist=None, is_case_sensitive=False, is_denom_only=False):

        Parmeters:

            term_string:       [string]  comma-separated search terms
            sentence:          [string]  the sentence to be processed
            str_minval:        [string]  minimum acceptable value for numeric queries
            str_maxval:        [string]  maximum acceptable value for numeric queries
            enumlist:          [string]  comma-separated desired result terms
            is_case_sensitive: [Boolean] if True perform case-sensitive comparisons
            is_denom_only:     [Boolean] if True, return denominators for fractions

"""

import re
import os
import sys
import json
import optparse
from collections import namedtuple

# imports from ClarityNLP core
try:
    # for normal operation via NLP pipeline
    from algorithms.finder.date_finder import run as \
        run_date_finder, DateValue, EMPTY_FIELD as EMPTY_DATE_FIELD
    from algorithms.finder.time_finder import run as \
        run_time_finder, TimeValue, EMPTY_FIELD as EMPTY_DATE_FIELD
    from algorithms.finder.size_measurement_finder import run as \
        run_size_measurement, SizeMeasurement, EMPTY_FIELD as EMPTY_SMF_FIELD
except Exception as e:
    # If here, this module was executed directly from the value_extraction
    # folder for testing. Construct path to nlp/algorithms/finder and perform
    # the imports above. This is a hack to allow an import from a higher-
    # level package.
    this_module_dir = sys.path[0]
    pos = this_module_dir.find('/nlp')
    if -1 != pos:
        nlp_dir = this_module_dir[:pos+4]
        finder_dir = os.path.join(nlp_dir, 'algorithms', 'finder')
        sys.path.append(finder_dir)
        from date_finder import run as run_date_finder, \
            DateValue, EMPTY_FIELD as EMPTY_DATE_FIELD
        from time_finder import run as run_time_finder, \
            TimeValue, EMPTY_FIELD as EMPTY_TIME_FIELD
        from size_measurement_finder import run as \
            run_size_measurement, SizeMeasurement, EMPTY_FIELD as \
            EMPTY_SMF_FIELD


# ignore any result field with this value
EMPTY_FIELD = None  # ignore any field with this value

# serializable result object; measurementList is an array of Value namedtuples
VALUE_RESULT_FIELDS = [
    'sentence', 'measurementCount', 'terms', 'querySuccess', 'measurementList'
]
ValueResult = namedtuple('ValueResult', VALUE_RESULT_FIELDS)

VALUE_FIELDS = [
    'text', 'start', 'end', 'condition', 'matchingTerm',
    'x', 'y', 'minValue', 'maxValue'
]
Value = namedtuple('Value', VALUE_FIELDS)

# condition field values
STR_APPROX         = 'APPROX'
STR_LT             = 'LESS_THAN'
STR_LTE            = 'LESS_THAN_OR_EQUAL'
STR_GT             = 'GREATER_THAN'
STR_GTE            = 'GREATER_THAN_OR_EQUAL'
STR_EQUAL          = 'EQUAL'
STR_RANGE          = 'RANGE'
STR_FRACTION_RANGE = 'FRACTION_RANGE'

ValueMeasurement = namedtuple('ValueMeasurement',
                              'text start end num1 num2 cond matching_term')

###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 14
_MODULE_NAME = 'value_extractor.py'

# set to True to enable debug output
_TRACE = False

# chars to be replaced with whitespace to simplify things
_regex_whitespace_replace = re.compile(r'[%(){}\[\]]')

# hyphenated words, abbreviations
_str_text_word = r'[-a-zA-Z.]+'

# this is a catchall that finds words, titer expressions (1:200),
# '+' and '-' symbols, +/-, etc.
_str_enumlist_value = r'[-a-zA-Z:\d/\+()]+'

# matcher for 'words', including hyphenated words and abbreviations
_str_words     = r'([-a-zA-Z.]+\s+){0,8}?' # nongreedy

_str_digits    = r'\d+'
_str_op        = r'((is|of|was|approx\.?|approximately|~=|>=|<=|[<>=~\?])\s*)?'
_str_approx    = r'(~=|~|\b(approx\.?|approximately))'
_str_equal     = r'\b(equal|eq\.?)'
_str_less_than = r'\b(less\s+than|lt\.?|up\s+to|under)'
_str_gt_than   = r'\b(greater\s+than|gt\.?|exceed(ing|s)|above|over)'
_str_lt        = r'(<|' + _str_less_than + r')'
_str_lte       = r'(<=|' + _str_less_than + r'\s+or\s+' + _str_equal + r')'
_str_gt        = r'(>|' + _str_gt_than + r')'
_str_gte       = r'(>=|' + _str_gt_than + r'\s+or\s+' + _str_equal + r')'
_str_separator = r'([-:=\s]\s*)?'

# numbers with commas
_str_comma_num = r'\d{1,3}(,\d{3})+'

# integers or floating point numbers
_str_int_float = r'(\d+(\.\d+)?|\.\d+)'

# any number
_str_num       = _str_comma_num + r'|' + _str_int_float

_str_cond      = r'(?P<cond>' + _str_op + r')'
_str_suffix    = r'(k|K|s|\'s)?'
_str_suffix1   = r'(?P<suffix1>' + _str_suffix + r')'
_str_suffix2   = r'(?P<suffix2>' + _str_suffix + r')'
_str_val       = r'(?P<val>' + _str_num + r')(?P<suffix>' + _str_suffix + r')'
_str_range_sep = r'\s*(-|to(\s+the)?)\s*'
_str_range     = r'(?P<num1>' + _str_num + r')' + _str_suffix1                +\
    _str_range_sep                                                            +\
    r'(?P<num2>' + _str_num + r')' + _str_suffix2

# # from http://ebmcalc.com/Basic.htm, an online medical unit conversion tool
# str_units = r'(#|$|%O2|%|10^12/L|10^3/microL|10^9/L|atm|bar|beats/min|bpm|'  +\
#             r'breaths/min|centimeters|cm|cents|cmH20|cmHg|cm^2|cm2|days|'    +\
#             r'degC|degF|dyn-sec-cm-5|eq|feet|fL|fractionO2|fraction|ftH20|'  +\
#             r'ft|g/dL|g/L/|gallon|gm/day|gm/dL|gm/kg/day|gm/kg|gm/L|gm/cm2|' +\
#             r'gm/sqcm|gm|hrs|hr|inches|index|inH2O|inHg|in|IU/L|kcal/day|'   +\
#             r'kg/m2|kg/m^2|kg/sqm|kg|kilograms|km/hr|km/sec|km/s|knots|kPa|' +\
#             r'L/24H|L/day|L/min|L/sec|lb|Liter|litresO2|logit|L|m/sec|mbar|' +\
#             r'mcg/dL|mcg/kg|mcg/mL|mcgm/mL|mEq/L/hr|meq/L|mEq/L|mEq|meters|' +\
#             r'METs|mg%|mg/day|mg/dL|mg/g|mg/kg|mg/mL|mg|micm|miles/hr|'      +\
#             r'miles/sec|miles/s|mph|mins|min|mIU/mL|mL/24H|mL/day|mL/dL|'    +\
#             r'mL/hr|mL/L|mL/min|mL/sec|mL/sqm|mL|mm/Hr|mmHg|mmol/L|mm|'      +\
#             r'months|mOsm/dl|mOsm/kg|mosm/kg|mo|m|ng/kg/min|ng/mL|nm|'       +\
#             r'number|Pascal|percent|pg|ph|points|pounds|psi|rate|ratio|'     +\
#             r'score|secs|sec|seq|sqcm/sqm|sqcm|sqm|sqrcm|sqrm|torr|u/L|U/L|' +\
#             r'Vol%|weeks|yd|years|yr)'

# 'between' and 'from' often denote ranges, such as 'between 10 and 20'
_str_bf     = r'\b(between|from)\s*'
_str_bf_sep = r'\s*(-|to|and)\s*'

# ranges with optional suffixes, to capture "90's to 100's", 20k-40k, etc.
_str_bf_range = _str_bf + \
    r'(?P<num1>' + _str_num + r')' + _str_suffix1 + _str_bf_sep              +\
    r'(?P<num2>' + _str_num + r')' + _str_suffix2

_str_units_range = r'(' + _str_bf + r')?'                                    +\
    r'(?P<num1>' + _str_num + r')' + r'\s*'                                  +\
    r'(?P<units1>' + _str_text_word + r')'                                   +\
    _str_bf_sep                                                              +\
    r'(?P<num2>' + _str_num + r')' +r'\s*'                                   +\
    r'(?P<units2>' + _str_text_word + r')'

# two integers separated by '/'
_str_fraction  = r'\d+\s*/\s*\d+'
_str_fraction_range  = r'(?P<frac1>' + _str_fraction + r')(\'?s)?'           +\
    _str_range_sep                                                           +\
    r'(?P<frac2>' + _str_fraction + r')(\'?s)?'

# between 110/70 and 120/80, from 100/60 to 120/70, etc.
_str_bf_fraction_range = _str_bf                                             +\
    r'(?P<frac1>' + _str_fraction + r')(\'?s)?'                              +\
    _str_bf_sep                                                              +\
    r'(?P<frac2>' + _str_fraction + r')(\'?s)?'

# common punctuation
_str_punct = r'[.;,?\'\"!$%~]'
_regex_punct = re.compile(_str_punct)

_regex_num      = re.compile(_str_num)
_regex_fraction = re.compile(_str_fraction)
_regex_number   = re.compile(_str_num)
_regex_digits   = re.compile(_str_digits)
_regex_range    = re.compile(_str_range)
_regex_approx   = re.compile(_str_approx)
_regex_lt       = re.compile(_str_lt)
_regex_lte      = re.compile(_str_lte)
_regex_gt       = re.compile(_str_gt)
_regex_gte      = re.compile(_str_gte)

# vitals
_str_vitals = r'\b(temperature|temp|t|hr|bp|pulse|p|rr?|o2sats?|o2 sats?|spo2|o2|fio2|wt|ht)'
_regex_vitals = re.compile(_str_vitals)

# durations (for 2 hrs, q. 6-8 hrs, etc.)
#_str_duration_wd = r'\b(for|over|last|lasting|lasted|within|q\.?|each|every|once)'

# NOTE: could match heart rate 'hr'; need to resolve any 'hr' matches
_str_duration_amt = r'(hours?|hrs|hr\.?|minutes?|mins|min\.?|seconds?|secs|sec\.?)'
#_str_duration_range = _str_duration_wd + r'\s*' + _str_range + r'\s*' +\
#    _str_duration_amt
#_str_duration_num = _str_duration_wd + r'\s*' + _str_num + r'\s*'
#_str_duration1 = _str_duration_range + r'|' + _str_duration_num
_str_duration2 = r'(?P<dur_num2>' + _str_num + r')'               +\
                 r'\s*'                                           +\
                 r'(?P<dur_amt2>' +_str_duration_amt + r')'
#_str_duration = _str_duration1 + r'|' + _str_duration2
_regex_duration = re.compile(_str_duration2)

# used to restore original terms
_term_dict = {}

# returned if no results found
_EMPTY_JSON = '{}'


###############################################################################
def _to_json(original_terms, original_sentence, results, is_text):
    """
    Convert results to a JSON string.
    """

    total = len(results)
    
    result_dict = {}
    result_dict['sentence'] = original_sentence
    result_dict['measurementCount'] = len(results)
    result_dict['terms'] = original_terms
    result_dict['querySuccess'] = len(results) > 0

    # build a list of dictionaries for the value measurements
    dict_list = []
    for m in results:
        m_dict = {}

        # restore original text
        m_dict['text'] = original_sentence[int(m.start):int(m.end)]
        m_dict['start'] = m.start
        m_dict['end'] = m.end
        m_dict['condition'] = m.cond
        m_dict['matchingTerm'] = _term_dict[m.matching_term]
        m_dict['x'] = m.num1

        if EMPTY_FIELD == m.num2:
            m_dict['y'] = EMPTY_FIELD
        else:
            m_dict['y'] = m.num2

        # set min and max fields for numeric results
        if is_text:
            minval = EMPTY_FIELD
            maxval = EMPTY_FIELD
        else:
            minval = m.num1
            maxval = m.num1
            if EMPTY_FIELD != m.num2:
                minval = min([m.num1, m.num2])
                maxval = max([m.num1, m.num2])

        m_dict['minValue'] = minval
        m_dict['maxValue'] = maxval
            
        dict_list.append(m_dict)

    result_dict['measurementList'] = dict_list
    return json.dumps(result_dict, indent=4)

    
###############################################################################
def _cond_to_string(words, cond):
    """
    Determine the relationship between the query term and the value.
    """
    
    # need to check two strings, so concat and run regex on result
    s = words + ' ' + cond

    if _regex_approx.search(s):
        result = STR_APPROX
    elif _regex_lte.search(s):
        result = STR_LTE
    elif _regex_gte.search(s):
        result = STR_GTE
    elif _regex_lt.search(s):
        result = STR_LT
    elif _regex_gt.search(s):
        result = STR_GT
    else:
        result = STR_EQUAL
    
    return result


###############################################################################
def _get_num_and_denom(str_fraction):
    """
    Convert a fraction (such as 110/70) to an integer 2-tuple.
    """

    values = str_fraction.strip().split('/')
    assert 2 == len(values)
    return (int(values[0]), int(values[1]))


###############################################################################
def _get_suffixed_num(match_obj, num_grp, suffix_grp):
    """
    Convert a string representing a numeric value with an optional suffix
    to a floating point value.

    The two strings identify the regex match groups for the number and
    suffix.
    """

    # strip commas from number before conversion to float
    num_str = match_obj.group(num_grp)
    num_str_no_commas = re.sub(r',', '', num_str)
    num = float(num_str_no_commas)

    suffix = match_obj.group(suffix_grp)
    if suffix is not None and len(suffix) > 0 and 'k' == suffix.lower():
        num *= 1000.0
    return num


###############################################################################
def _update_match_results(
        match, spans, results, num1, num2, cond, matching_term):
    """
    Given a match object, check its [start, end) span against all matching
    spans thus far, and add to span list only if no overlap. This prevents
    multiple inclusions of already-matched values in the result list.
    """

    match_text = match.group().strip()
    start = match.start()
    end = start + len(match_text)
    keep_it = True
    for start_i, end_i in spans:
        if start >= start_i and end <= end_i:
            keep_it = False
            if _TRACE:
                print('\tupdate_match_results: discarding "{0}"'.
                      format(match))
            break

    if keep_it:
        meas = ValueMeasurement(
            match_text, start, end, num1, num2, cond, matching_term
        )
        results.append(meas)
        spans.append( (start, end))


###############################################################################
def _get_query_start(query_term):
    """
    Construct the starting string for a value extraction query.
    """

    # Form a query string from either a standalone query term or a
    # query term followed by optional words plus a separator symbol.
    if len(query_term) > 1:
        str_query = r'\b(' + query_term + r'\s*' + r'|'                      +\
            query_term + r'\s+([a-zA-Z]+\s*)' + r')' + _str_separator
        str_start = str_query + r'(?P<words>' + _str_words + r')'
    else:
        # If the query term is a single letter, it cannot be followed by
        # another letter, since likely starting a new word. Must be followed
        # either by a non-letter character, such as a digit or whitespace.
        str_query = r'\b(' + query_term + r'(?![a-zA-Z])\s*' + r'|' + \
                    query_term + r'\s+([a-zA-Z]+\s*)' + r')' + _str_separator
        str_start = str_query + r'(?P<words>' + _str_words + r')'

    return str_start


###############################################################################
def _extract_enumlist_values(query_terms, sentence, filter_words):
    """
    Extract a word to match the query term, and accept if that word
    appears in the result filter.
    """

    if _TRACE:
        print('calling extract_enumlist_values...')
        print('\t query_terms: {0}'.format(query_terms))
        print('\t    sentence: {0}'.format(sentence))
        print('\tfilter_words: {0}'.format(filter_words))

    # find each query term in the sentence and record their positions
    boundaries = []
    for query_term in query_terms:
        # escape any chars that have special meaning for regex
        str_word_query = re.escape(query_term)
        iterator = re.finditer(str_word_query, sentence)
        for match in iterator:
            boundaries.append(match.start())
        
    # return if no query terms were found
    if 0 == len(boundaries):
        return []

    # sort by increasing char position
    boundaries = sorted(boundaries)
    num_boundaries = len(boundaries)

    if _TRACE:
        print('\tboundaries: {0}'.format(boundaries))

    results = []
    for query_term in query_terms:
        if _TRACE: print('\tsearching for query term "{0}"'.format(query_term))
        str_word_query = re.escape(query_term)
        str_enum_query = str_word_query                                      +\
            r'(?P<words>'                                                    +\
            r'\s*(' + _str_enumlist_value + r'\s*){0,8}'                     +\
            r')'

        found_it = False
        iterator = re.finditer(str_enum_query, sentence)
        for match in iterator:
            if _TRACE:
                print("\t\tmatch '{0}' start: {1}".
                      format(match.group(), match.start()))
            start = match.start()

            # this start offset must occur in the boundaries list
            try:
                index = boundaries.index(start)
            except ValueError:
                # skip this term for now - need to log this - TBD
                if _TRACE:
                    print('\t\t***ERROR***: start offset not found ' +\
                          'in boundaries list.')
                continue

            # don't cross into the next query term match region
            end = match.end()
            if index < num_boundaries-1:
                if match.end() > boundaries[index+1]:
                    end = boundaries[index+1]

            words = match.group('words')
            words_start = match.start('words')
            word = ''

            #need to find candidates, do overlap resolution, take longest match - TBD
            
            for fw in filter_words:
                pos = words.find(fw)
                if -1 != pos and words_start + pos < end:
                    found_it = True
                    if len(fw) > len(word):
                        word = fw

            if found_it:
                meas = ValueMeasurement(word, start, end,
                                        word, EMPTY_FIELD, STR_EQUAL,
                                        query_term)
                results.append(meas)
                if _TRACE:
                    print('\t\tnew result: "{0}"'.format(meas))

    return results

        
###############################################################################
def _extract_value(query_term, sentence, minval, maxval, denom_only):
    """
    Search the sentence for the query term, find associated values that fit
    one of the regex patterns, extract the values, check the value against
    [minval, maxval], determine relationship between query term and value
    (i.e. less than, greater than, etc.), and return results.
    """

    if _TRACE:
        print('calling extract_value with term "{0}"'.format(query_term))
    
    # no values to extract if the sentence contains no digits
    match = _regex_digits.search(sentence)
    if not match:
        if _TRACE:
            print('\tno digits found in sentence: {0}'.format(sentence))
        return []

    str_start = _get_query_start(query_term)
    
    # find two ints separated by '/', such as blood pressure values
    str_fraction_query = str_start + _str_cond                               +\
        r'(?P<frac>' + _str_fraction + r')'
    
    # two fractions with a range separator inbetween
    str_fraction_range_query = str_start + _str_cond + _str_fraction_range
    str_bf_fraction_range_query = str_start + _str_cond + _str_bf_fraction_range
    
    # <query> <operator> <value>
    str_op_val_query = str_start + _str_cond + _str_val
    
    # two numbers with a range separator inbetween
    str_range_query = str_start + _str_cond + _str_range
    str_bf_range_query = str_start + _str_cond + _str_bf_range
    str_units_range_query = str_start + _str_cond + _str_units_range

    # <query> <words> <value>
    str_wds_val_query = str_start + _str_val

    spans   = []  # [start, end) character offsets of each match
    results = []  # ValueMeasurement namedtuple results

    # check for bf fraction ranges first
    iterator = re.finditer(str_bf_fraction_range_query, sentence)
    for match in iterator:
        if _TRACE:
            print('\tmatched bf_fraction_range_query: {0}'.format(match.group()))
        (n1, d1) = _get_num_and_denom(match.group('frac1'))
        (n2, d2) = _get_num_and_denom(match.group('frac2'))

        # keep either numerator or denom, according to user preference
        x1 = n1
        x2 = n2
        if denom_only:
            x1 = d1
            x2 = d2
        
        # accept a fraction range if both values are in [minval, maxval]
        if x1 >= minval and x1 <= maxval and x2 >= minval and x2 <= maxval:
            cond = 'FRACTION_RANGE'
            match_text = match.group().strip()
            start = match.start()
            end = start + len(match_text)
            meas = ValueMeasurement(match_text, start, end, x1, x2,
                                    cond, query_term)
            results.append(meas)
            spans.append( (start, end))

    # check for other fraction ranges
    iterator = re.finditer(str_fraction_range_query, sentence)
    for match in iterator:
        if _TRACE:
            print('\tmatched fraction_range_query: {0}'.format(match.group()))
        (n1, d1) = _get_num_and_denom(match.group('frac1'))
        (n2, d2) = _get_num_and_denom(match.group('frac2'))

        # keep either numerator or denom, according to user preference
        x1 = n1
        x2 = n2
        if denom_only:
            x1 = d1
            x2 = d2
            
        # accept a fraction range if both values are in [minval, maxval]
        if x1 >= minval and x1 <= maxval and x2 >= minval and x2 <= maxval:
            cond = STR_FRACTION_RANGE
            _update_match_results(match, spans, results, x1, x2,
                                  cond, query_term)

    # check for fractions
    iterator = re.finditer(str_fraction_query, sentence)
    for match in iterator:
        if _TRACE:
            print('\tmatched fraction_query: {0}'.format(match.group()))
        (n, d) = _get_num_and_denom(match.group('frac'))

        # keep either numerator or denom, according to user preference
        x = n
        if denom_only:
            x = d
        
        # accept a fraction if value is contained in [minval, maxval]
        if x >= minval and x <= maxval:
            words = match.group('words')
            cond_words = match.group('cond').strip()
            cond = _cond_to_string(words, cond_words)
            _update_match_results(match, spans, results, x, EMPTY_FIELD,
                                  cond, query_term)

    # check for units range query
    iterator = re.finditer(str_units_range_query, sentence)
    for match in iterator:
        if _TRACE:
            print('\tmatched units_range_query: {0}'.format(match.group()))
        units1 = match.group('units1').strip().lower()
        units2 = match.group('units2').strip().lower()
        # strip punctuation
        units1 = _regex_punct.sub('', units1)
        units2 = _regex_punct.sub('', units2)
        if units1 == units2:
            num1 = float(match.group('num1'))
            num2 = float(match.group('num2'))
            if 'k' == units1.lower():
                num1 *= 1000.0
                num2 *= 1000.0
            # accept a numeric range if both numbers are in [minval, maxval]
            if num1 >= minval and num1 <= maxval and \
               num2 >= minval and num2 <= maxval:
                cond = STR_RANGE
                _update_match_results(match, spans, results, num1, num2,
                                      cond, query_term)

    # check for bf numeric ranges
    iterator = re.finditer(str_bf_range_query, sentence)
    for match in iterator:
        if _TRACE:
            print('\tmatched bf_range_query: {0}'.format(match.group()))
        num1 = _get_suffixed_num(match, 'num1', 'suffix1')
        num2 = _get_suffixed_num(match, 'num2', 'suffix2')
        # accept a numeric range if both numbers are in [minval, maxval]
        if num1 >= minval and num1 <= maxval and \
           num2 >= minval and num2 <= maxval:
            cond = STR_RANGE
            _update_match_results(match, spans, results, num1, num2,
                                  cond, query_term)
            
    # check for numeric ranges
    iterator = re.finditer(str_range_query, sentence)
    for match in iterator:
        if _TRACE:
            print('\tmatched range query: {0}'.format(match.group()))
        num1 = _get_suffixed_num(match, 'num1', 'suffix1')
        num2 = _get_suffixed_num(match, 'num2', 'suffix2')
        # accept a numeric range if both numbers are in [minval, maxval]
        if num1 >= minval and num1 <= maxval and \
           num2 >= minval and num2 <= maxval:
            cond = STR_RANGE
            _update_match_results(match, spans, results, num1, num2,
                                  cond, query_term)

    # check for op-value matches
    iterator = re.finditer(str_op_val_query, sentence)
    for match in iterator:
        if _TRACE:
            print('\tmatched op_val_query: {0}'.format(match.group()))
        val = _get_suffixed_num(match, 'val', 'suffix')
        if val >= minval and val <= maxval:
            words = match.group('words')
            cond_words = match.group('cond').strip()
            cond = _cond_to_string(words, cond_words)
            _update_match_results(match, spans, results, val, EMPTY_FIELD,
                                  cond, query_term)
            
    # check for wds-value matches
    iterator = re.finditer(str_wds_val_query, sentence)
    for match in iterator:
        if _TRACE:
            print('\tmatched wds_val_query: {0}'.format(match.group()))
        val = _get_suffixed_num(match, 'val', 'suffix')
        if val >= minval and val <= maxval:
            _update_match_results(match, spans, results, val,
                                  EMPTY_FIELD, EMPTY_FIELD, query_term)

    results = remove_hypotheticals(sentence, results)
    return results


###############################################################################
def _resolve_overlap(terms, results):
    """
    Check results for overlap and prune according to these rules:
    
    1.  If two results overlap exactly, return the result with the longest
        matching term.
    
        Example:
    
            sentence: 'T=98 BP= 122/58  HR= 7 RR= 20  O2 sat= 100% 2L NC'
            term_str: 'o2, o2 sat'

            Both 'o2' and 'o2 sat' match the value 100, and both matches have
            identical start/end values. Return 'o2 sat' as the result.

    2.  If two results partially overlap, discard the first match if the 
        matched value is part of the search term for the second.

        Example:

            sentence: 'BP 120/80 HR 60-80s RR  SaO2 96% 6L NC.'
            term_str: 'rr, sao2'

            The rr search term has no associated value, so the value extractor
            looks and finds the '2' in 'SaO2'. The '2' is part of the search
            term 'sao2', so prevent this from being returned as a match.

    3.  If two results partially overlap, discard any match that is completely
        contained inside the span of the other.

        Example:

            sentence: 'BLOOD PT-10.8 PTT-32.6 INR(PT)-1.0'
            term_str: 'pt, ptt, inr(pt)'

            The value extractor will find these matches:
                'PT-10.8' for match term 'pt'
                'PT)-1.0' for match term 'pt'
                'PTT-32.6' for match term 'ptt'
                'INR(PT)-1.0' for match term 'INR(PT)'
                 
            The second match is contained entirely within the span of the
            fourth, so it should be discarded.

    """

    if results is None:
        return results
    
    n = len(results)
    if 0 == n:
        return

    discard_set = set()
    for i in range(n):
        s1 = results[i].start
        e1 = results[i].end
        for j in range(i+1, n):
            s2 = results[j].start
            e2 = results[j].end

            # results have been sorted by position in sentence
            assert s1 <= s2
            
            if e1 > s2:
                if _TRACE:
                    print('overlap1: {0}'.format(results[i]))
                    print('overlap2: {0}'.format(results[j]))

                to_discard = None
                if s1 == s2 and e1 == e2:
                    # identical overlap, keep match longest matching_term
                    term1 = results[i].matching_term
                    term2 = results[j].matching_term
                    if len(term1) > len(term2):
                        to_discard = results[j]
                    else:
                        to_discard = results[i]
                else:
                    # partial overlap, discard if value part of another term
                    if results[i].text.endswith(results[j].matching_term):
                        to_discard = results[i]
                    elif e2 <= e1:
                        to_discard = results[j]

                if to_discard is not None:
                    discard_set.add(to_discard)
                    if _TRACE:
                        print('\tdiscarding {0}'.format(to_discard))

    if 0 == len(discard_set):
        return results

    # prune discarded items
    new_results = []
    for r in results:
        if r not in discard_set:
            new_results.append(r)

    return new_results


###############################################################################
def remove_hypotheticals(sentence, results):
    """
    Use a simplified version of the ConText algorithm of Harkema et. al. to 
    identify and remove values used in hypothetical phrases.
    """

    # number of words influenced by a hypothetical start term
    WINDOW = 6

    if _TRACE:
        print('calling remove_hypotheticals...')

    sentence_lc = sentence.lower()

    str_split = r'[,;\s]+'
    words = re.split(str_split, sentence_lc)

    word_count = len(words)

    # find matching text of each result in the words list
    result_spans = []
    for r in results:
        r_words = re.split(str_split, r.text.lower())
        r_word_count = len(r_words)

        for i in range(word_count - (r_word_count - 1)):
            j = 0
            while j < r_word_count:
                if words[i+j].startswith(r_words[j]):
                    j += 1
                else:
                    break
            if j == len(r_words):
                # found the 'r_words' string in 'words'
                result_spans.append( (i, i+r_word_count, r))
                break

    if _TRACE:
        print('\tresult word spans: ')
        for span in result_spans:
            print('\t\twords [{0},{1})'.format(span[0], span[1]))

    # scan the word list looking for these hypothetical trigger words:
    #     'call for'
    #     'if': only if not preceded by 'know' and not followed by 'negative'
    #     'in case'
    #     'should'
    triggers = []
    for i in range(word_count):
        trigger = None
        word_offset = 0
        if 'call' == words[i] and i < word_count-1 and 'for' == words[i+1]:
            trigger = 'call for'
            word_offset = 1
        elif 'if' == words[i]:
            if i > 0 and 'know' == words[i-1]:
                continue
            elif i < word_count-1 and 'negative' == words[i+1]:
                continue
            else:
                trigger = 'if'
        elif 'in' == words[i] and i < word_count-2 and 'case' == words[i+1]:
            trigger = 'in case'
            word_offset = 1
        elif 'should' == words[i]:
            trigger = 'should'
        else:
            continue

        assert trigger is not None

        # hypothetical window starts at the end of the trigger phrase,
        # which is set by the word offset
        triggers.append( (i+word_offset, trigger))

    if _TRACE:
        print('\ttriggers: ')
        print('\t\t{0}'.format(triggers))

    omit_results = set()
        
    # for each trigger, find next value result starting within WINDOW words\
    for hw in triggers:
        h_start = hw[0]
        for rs in result_spans:
            rs_start = rs[0]
            if rs_start < h_start:
                continue
            if rs_start - h_start < WINDOW:
                if _TRACE:
                    print('Trigger {0} influences {1}'.
                          format(hw[1], words[rs_start]))
                omit_results.add(rs[2])
                continue
    
    new_results = []
    for r in results:
        if not r in omit_results:
            new_results.append(r)

    return new_results


###############################################################################
def erase(sentence, start, end):
    """
    Overwrite characters [start, end) with whitespace.
    """
    piece1 = sentence[:start]
    piece2 = ' '*(end-start)
    piece3 = sentence[end:]
    return piece1 + piece2 + piece3


###############################################################################
def _erase_durations(sentence):
    """
    Erase time duration expressions from the sentence.
    Example:

        before: 'platelets 2 hrs after transfusion 156'
         after: 'platelets       after transfusion 156'
    """
    
    # find time durations in the sentence
    iterator = _regex_duration.finditer(sentence)
    for match in iterator:
        if _TRACE:
            print('\tDURATION: {0}'.format(match.group()))

        try:
            if match.group('dur_amt1') is not None:
                duration = match.group('dur_amt1')
        except IndexError:
            pass

        try:
            if match.group('dur_amt2') is not None:
                duration = match.group('dur_amt2')
        except IndexError:
            pass

        if _TRACE:
            print('\t     amt: {0}'.format(duration))

        erase_it = True
        if 'hr' == duration:
            # check sentence for other vitals (excluding hr)
            vitals_count = 0
            iterator = _regex_vitals.finditer(sentence)
            for match2 in iterator:
                match_text = match2.group()
                if 'hr' == match_text:
                    continue
                vitals_count += 1

            if _TRACE:
                print('\tvitals_count: {0}'.format(vitals_count))
                
            if vitals_count > 0:
                # this 'hr' appears with other vitals and is prob heart rate
                erase_it = False

        if erase_it:
            sentence = erase(sentence, match.start(), match.end())
            if _TRACE:
                print('\terased time duration expression: "{0}"'.
                      format(match.group()))
        
    return sentence


###############################################################################
def _common_clean(string_list, is_case_sensitive):
    """
    Do cleaning operations common to both sentences and query terms.
    """

    for i, text in enumerate(string_list):

        # replace certain chars with whitespace
        text = _regex_whitespace_replace.sub(' ', text)
    
        # convert to lowercase unless case sensitive match enabled
        if not is_case_sensitive:
            text = text.lower()

        string_list[i] = text
        
            
###############################################################################
def _clean_sentence(sentence, is_case_sensitive):
    """
    Do some preliminary processing on the sentence prior to value extraction.
    """

    if _TRACE:
        print('calling clean_sentence...')

    string_list = [sentence]
    _common_clean(string_list, is_case_sensitive)
    sentence = string_list[0]
    
    # find date expressions in the sentence
    json_string = run_date_finder(sentence)
    json_data = json.loads(json_string)

    # unpack JSON result into a list of DateMeasurement namedtuples
    dates = [DateValue(**record) for record in json_data]

    # erase each date expression from the sentence
    for date in dates:
        start = int(date.start)
        end   = int(date.end)

        if _TRACE:
            print('\tfound date expression: "{0}"'.format(date))

        # erase date if not all digits, such as 1500, which
        # could be a measurement (i.e. 1500 ml)
        if not re.match(r'\A\d+\Z', date.text):
            if _TRACE:
                print('\terasing date "{0}"'.format(date.text))
            sentence = erase(sentence, start, end)

    # find size measurements in the sentence
    json_string = run_size_measurement(sentence)
    json_data = json.loads(json_string)

    # unpack JSON result into a list of SizeMeasurement namedtuples
    measurements = [SizeMeasurement(**m) for m in json_data]

    # erase each size measurement from the sentence except for those in
    # units of cc's and inches
    for m in measurements:

        if _TRACE:
            print('\tfound size measurement: "{0}"'.format(m.text))
        
        if 'CUBIC_MILLIMETERS' == m.units:
            if -1 != m.text.find('cc'):
                continue
        if 'MILLIMETERS' == m.units:
            if -1 != m.text.find('in'):
                continue
        start = int(m.start)
        end   = int(m.end)
        if _TRACE:
            print('\terasing size measurement "{0}"'.format(m.text))
        sentence = erase(sentence, start, end)

    # find time expressions in the sentence
    json_string = run_time_finder(sentence)
    json_data = json.loads(json_string)

    # unpack JSON result into a list of TimeValue namedtuples
    times = [TimeValue(**record) for record in json_data]

    # erase each time expression from the sentence
    for t in times:
        start = int(t.start)
        end   = int(t.end)

        # erase time expression if not one of these formats:
        #     hh, hhmm, hhmmss, or one of these on each side of +-
        #     only digits and '.' (confused with floating pt values)
        erase_it = False
        match_a = re.match(r'\A\d+\Z', t.text)
        match_b = re.match(r'\A\d+[\-\+]\d+\Z', t.text)
        match_c = re.match(r'\A[\d\.]+\Z', t.text)
        if not match_a and not match_b and not match_c:
            erase_it = True
        if erase_it:
            if _TRACE:
                print('\tERASING TIME EXPRESSION: "{0}"'.format(t.text))
            sentence = erase(sentence, start, end)

    sentence = _erase_durations(sentence)
            
    if _TRACE:
        print('\tcleaned sentence: {0}'.format(sentence))
        
    return sentence


###############################################################################
def run(term_string,               # comma-separated string of query terms
        sentence,
        str_minval=None,
        str_maxval=None,
        enumlist=None,
        is_case_sensitive=False,
        is_denom_only=False):
    """
    Run the value extractor for all query terms and return a list of
    ValueMeasurement namedtuples.
    """

    if _TRACE:
        print('called value_extractor run...')
        print('\tARGUMENTS: ')
        print('\t      term_string: {0}'.format(term_string))
        print('\t         sentence: {0}'.format(sentence))
        print('\t       str_minval: {0}'.format(str_minval))
        print('\t       str_maxval: {0}'.format(str_maxval))
        print('\t         enumlist: {0}'.format(enumlist))
        print('\tis_case_sensitive: {0}'.format(is_case_sensitive))
        print('\t    is_denom_only: {0}'.format(is_denom_only))

    assert term_string is not None
    
    # use default minval and maxval if not provided
    if enumlist is None and str_minval is None:
        str_minval = '-' + str(sys.float_info.max)
    if enumlist is None and str_maxval is None:
        str_maxval = str(sys.float_info.max)
    
    # save a copy of the original sentence (needed for results)
    original_sentence = sentence

    terms = term_string.split(',') # produces a list
    terms = [term.strip() for term in terms]
    
    # sort terms from longest to shortest
    terms = sorted(terms, key=lambda x: len(x), reverse=True)

    # save a copy of the original terms
    original_terms = terms.copy()

    _common_clean(terms, is_case_sensitive)
    
    if enumlist:
        if isinstance(enumlist, str):
            filter_terms = enumlist.split(',')
        else:
            filter_terms = enumlist
        filter_terms = [term.strip() for term in filter_terms]
        
    # save a copy of the original terms
    #original_terms = terms.copy()
    
    # convert terms to lowercase unless doing a case-sensitive match
    if not is_case_sensitive:
        terms = [term.lower() for term in terms]
        
        if enumlist:
            filter_terms = [ft.lower() for ft in filter_terms]

    if _TRACE:
        print('\n\tterms: {0}'.format(terms))
    if _TRACE and enumlist:
        print('\tfilter_terms: {0}'.format(filter_terms))
                
    # map the new terms to the original, so can restore in output
    for i in range(len(terms)):
        new_term = terms[i]
        original_term = original_terms[i]
        _term_dict[new_term] = original_term
        if _TRACE:
            print('\tterm_dict[{0}] => {1}'.format(new_term, original_term))

    if not enumlist:
        # do range check on numerator values for fractions
        if isinstance(str_minval, str):
            if -1 != str_minval.find('/'):
                str_minval = str_minval.split('/')[0]

        if isinstance(str_maxval, str):
            if -1 != str_maxval.find('/'):
                str_maxval = str_maxval.split('/')[0]

        minval = float(str_minval)
        maxval = float(str_maxval)

    # end of setup

    sentence = _clean_sentence(sentence, is_case_sensitive)

    results = []
    if enumlist:
        results = _extract_enumlist_values(terms, sentence, filter_terms)
    else:
        for term in terms:
            # extract a single numeric value
            values = _extract_value(term, sentence, minval, maxval,
                                    is_denom_only)
            results.extend(values)

    if 0 == len(results):
        if _TRACE:
            print('\t*** no results found ***')
        return _EMPTY_JSON
            
    # order results by their starting character offset
    results = sorted(results, key=lambda x: x.start)

    # prune if appropriate for overlapping results
    results = _resolve_overlap(terms, results)

    return _to_json(original_terms, original_sentence, results, enumlist)


###############################################################################
def _get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
def _show_help():
    print(_get_version())
    print("""
    USAGE: 

    To extract numeric values:

        python3 ./value_extractor.py -t <term list> -s <sentence> --min <minval> --max <maxval> [-hvcyz]

    To extract text and keep only those words that appear in an enumerated list:

        python3 ./value_extractor.py -t <term list> -s <sentence> --enumlist <enumerated list> [-hvcz]
           

    OPTIONS:

        -t, --terms    <quoted string>  List of comma-separated search terms.
        -s, --sentence <quoted string>  Sentence to be processed.
        -m, --min      <float or int>   Minimum acceptable value.
        -n, --max      <float or int>   Maximum acceptable value.
        -e, --enumlist <quoted string>  List of comma-separated terms for filtering results.
                                        The presence of this option causes textual values to be extracted.
                                        Only those terms appearing in the enumerated list are returned.

    FLAGS:

        -h, --help                      Print this information and exit.
        -v, --version                   Print version information and exit.
        -c, --case                      Preserve case when matching terms.
        -y, --denom                     Return the denominator of fractional values instead of the numerator.
                                        Default is to return the numerator.
        -z, --test                      Disable -s option and use internal test sentences.

    """)


###############################################################################
if __name__ == '__main__':

    TEST_SENTENCES = [

        # LVEF
        'The LVEF is 40%.',
        'Hyperdynamic LVEF >75%.',
        'Overall normal LVEF (>55%).',
        'Overall left ventricular systolic function is normal (LVEF 60%).',
        'Overall left ventricular systolic function is normal (LVEF>55%).',
        'Overall left ventricular systolic function is low normal (LVEF 50-55%).',
        'LVEF was estimated at 55% and ascending aorta measured 5.1 centimeters.',
        'Overall left ventricular systolic function is severely depressed (LVEF= 20 %).',
        'Overall left ventricular systolic function is severely depressed (LVEF= < 30 %).',
        'Overall left ventricular systolic function is severely depressed (LVEF= 15-20 %).',
        'Conclusions: There is moderate global left ventricular hypokinesis (LVEF 35-40%).',
        'Overall left ventricular systolic function is moderately depressed (LVEF~25-30 %).',
        'Normal LV wall thickness, cavity size and regional/global systolic function (LVEF >55%).',
        'Overall left ventricular systolic function is mildly depressed (LVEF= 40-45 %) with inferior akinesis.',
        'Left ventricular wall thickness, cavity size and regional/global systolic function are normal (LVEF >55%).',
        'There is mild symmetric left ventricular hypertrophy with normal cavity size and regional/global systolic function (LVEF>55%).',
        'LEFT VENTRICLE: Overall normal LVEF (>55%). Beat-to-beat variability on LVEF due to irregular rhythm/premature beats.',
        'Overall left ventricular systolic function is moderately depressed (LVEF= 30 % with relative preservation of the lateral, inferolateral and inferior walls).',
        
        # EF
        'An echo showed an EF of 40%.',
        'EF was 50%, with 4+ TR and AVR gradient 30mmHG.',
        'Echo showed preseved systolic function with EF >55.',
        'Congestive heart failure (EF 30% as of [**9-/3389**])',
        'Left ventricular systolic function is hyperdynamic (EF>75%).',
        'Congestive Heart Failure, chronic: TTE in the ICU showed an EF 30%.',
        'Last EF slightly improved to 45% with inferior akinesis, mild AR and severe AS.',
        'UNDERLYING MEDICAL CONDITION: 60 year old man with hx of CHF, intubated, EF 20%, fevers and rash and elevated LFTs',
        'Dilated cardiomyopathy with EF of 10% secondary to chemotherapy(Hodgkins) in [**3003**], last ECHO [**8-/3023**], EF 10-15% .',
        'UNDERLYING MEDICAL CONDITION: 73 year old woman with recent MI s/p revasc, intubated with VAP and EF 40% s/p trach    now in respiratory distress',
        'UNDERLYING MEDICAL CONDITION: 53 year old man with crack lung, CHF (EF=20%), ate raw chicken p/w abdominal pain, fever, failed antibiotic monotherapy.',
        '84M Russian-speaking with h/o severe 3-vessel CAD unamenable to PCI s/p CABG x4 ([**2746**]) and MI x3, chronic angina, DM, CHF (EF 30-35%) presented from clinic with progressive dyspnea x 2 days.',
        
        # narrative forms for LVEF
        'Left Ventricle - Ejection Fraction:  60%  >= 55%',
        'Left Ventricle - Ejection Fraction: 55% (nl >=55%)',
        'Left Ventricle - Ejection Fraction:  50% to 55%  >= 55%',
        '53-year-old male with crack lung, CHF and ejection fraction of 20%, with abdominal pain and fever, who has failed antibiotic monotherapy.',
        'His most recent echocardiogram was in [**2648-8-10**], which showed an ejection fraction of approximately 60 to 70% and a mildly dilated left atrium.',
        'He underwent cardiac catheterization on [**7-30**], which revealed severe aortic stenosis with an aortic valve area of 0.8 centimeters squared, an ejection fraction of 46%.',
        'The echocardiogram was done on [**2-15**], and per telemetry, showed inferior hypokinesis with an ejection fraction of 50%, and an aortic valve area of 0.7 cm2 with trace mitral regurgitation.',
        'Echocardiogram in [**3103-2-6**] showed a large left atrium, ejection fraction 60 to 65% with mild symmetric left ventricular hypertrophy, trace aortic regurgitation, mild mitral regurgitation.',
        "Myocardium:  The patient's ejection fraction at the outside hospital showed a 60% preserved ejection fraction and his ACE inhibitors were titrated up throughout this hospital stay as tolerated.",
        'Overall left ventricular systolic function is probably borderline depressed (not fully assessed; estimated ejection fraction ?50%); intrinsic function may be more depressed given the severity of the regurgitation.',

        # vital signs
        'VS: T 95.6 HR 45 BP 75/30 RR 17 98% RA.',
        'VS T97.3 P84 BP120/56 RR16 O2Sat98 2LNC',
        'VS: T 97.7, BP 134/73, HR 74, 22, 98% 3L',
        'Vitals: T: 99 BP: 115/68 P: 79 R:21 O2: 97',
        'Vitals - T 95.5 BP 132/65 HR 78 RR 20 SpO2 98%/3L',
        'In the ED, initial VS: 98.90 97 152/81 100% on RA.',
        'VS: T=98 BP= 122/58  HR= 7 RR= 20  O2 sat= 100% 2L NC',
        'VS:  T-100.6, HR-105, BP-93/46, RR-16, Sats-98% 3L/NC',
        'VS: T: 95.9 BP: 154/56 HR: 69 RR: 16 O2sats: 94% 2L NC',
        'VS - Temp. 98.5F, BP115/65 , HR103 , R16 , 96O2-sat % RA',
        'Vitals: Temp 100.2 HR 72 BP 184/56 RR 16 sats 96% on RA',
        'PHYSICAL EXAM: O: T: 98.8 BP: 123/60   HR:97    R 16  O2Sats100%',
        'VS before transfer were 85 BP 99/34 RR 20 SpO2% 99/bipap 10/5 50%.', # left side
        'In the ED, initial vs were: T 98 P 91 BP 122/63 R 20 O2 sat 95%RA.',
        'In the ED initial vitals were HR 106, BP 88/56, RR 20, O2 Sat 85% 3L.',
        'In the ED, initial vs were: T=99.3, P=120, BP=111/57, RR=24, POx=100%.',
        'Upon transfer her vitals were HR=120, BP=109/44, RR=29, POx=93% on 8L FM.',
        'Vitals in PACU post-op as follows: BP 120/80 HR 60-80s RR  SaO2 96% 6L NC.',
        'In the ED, initial vital signs were T 97.5, HR 62, BP 168/60, RR 18, 95% RA.',
        'T 99.4 P 160 R 56 BP 60/36 mean 44 O2 sat 97% Wt 3025 grams Lt 18.5 inches HC 35 cm',
        'In the ED, initial vital signs were T 97.0, BP 85/44, HR 107, RR 28, and SpO2 91% on NRB.',
        'Prior to transfer, his vitals were BP 119/53 (105/43 sleeping), HR 103, RR 15, and SpO2 97% on NRB.',
        'T 99.4 P 140 R 84 BP 57/30 mean 40 O2 sat 92% in RA, dropped to 89-90% Wt 2800 grams Lt 18.5 inches HC 34 cm',
        'VS: T 98.5 BP 120/50 (110-128/50-56) HR 88 (88-107) ....RR 24 (22-26), SpO2 94% on 4L NC(89-90% on 3L, 92-97% on 4L)',
        'In the ED inital vitals were, Temperature 100.8, Pulse: 103, RR: 28, BP: 84/43, O2Sat: 88, O2 Flow: 100 (Non-Rebreather).',
        'At clinic, he was noted to have increased peripheral edema and was sent to the ED where his vitals were T 97.1 HR 76 BP 148/80 RR 25 SpO2 92%/RA.',

        # blood components
        'CTAB Pertinent Results: BLOOD WBC-7.0# RBC-4.02* Hgb-13.4* Hct-38.4* MCV-96 MCH-33.2* MCHC-34.7 RDW-12.9 Plt Ct-172 02:24AM BLOOD WBC-4.4 RBC-4.21*',
        'Hgb-13.9* Hct-39.7* MCV-94 MCH-33.0* MCHC-35.0 RDW-12.6 Plt Ct-184 BLOOD WBC-5.6 RBC-4.90 Hgb-16.1 Hct-46.2 MCV-94 MCH-33.0* MCHC-34.9 RDW-12.8 Plt Ct-234',
        'BLOOD Type-ART Temp-36.6 Rates-16/ Tidal V-600 PEEP-5 FiO2-60 pO2-178* pCO2-35 pH-7.42 calTCO2-23 Base XS-0 Intubat-INTUBATED Vent-CONTROLLED BLOOD Lactate-1.0 BLOOD Lactate-1.6'
        'BLOOD Neuts-59.7 Lymphs-33.5 Monos-4.9 Eos-1.3 Baso-0.6 BLOOD PT-10.8 PTT-32.6 INR(PT)-1.0 BLOOD Plt Ct-234 BLOOD Glucose-182* UreaN-14 Creat-0.8 Na-134 K-4.0 Cl-101 HCO3-25 AnGap-12',
        'BLOOD Glucose-119* UreaN-21* Creat-0.9 Na-138 K-3.8 Cl-100 HCO3-25 AnGap-17 BLOOD TotProt-6.2* UricAcd-2.8* BLOOD PEP-AWAITING F IgG-1040 IgA-347 IgM-87 IFE-PND BLOOD C3-144 C4-37 BLOOD C4-45*',

        # approximations
        'RR approx 22, RR approx. 22, RR approximately 22, RR is approx. 22, RR is approximately 22',

        # >=, <=
        'RR >= 24, RR <= 42, her RR was greater than 24, his RR was less than 42',
        
        # ranges
        'RR 22-42, RR22-42, RR 22 - 42, RR(22-42), RR (22 to 42), RR (22 - 42)',
        'RR22to42, RR 22to42, RR 22 to 42, RR from 22 to 42, RR range: 22-42',
        'RR= 22-42, RR=22-42, RR= 22 -42, RR = 22 - 42, RR = 22 to 42, RR=22to42, RR is 22-42',
        'RR ~ 22-42, RR approx. 22-42, RR is approximately 22 - 42, RR is ~22-42, RR varies from 22-42',
        'RR varied from 22 to 42, RR includes all values in the range 22 to 42, RR values were 22-42',
        'RR: 22-42, RR 22-42, RR=22-42, RR ~= 22-42, RR ~= 22 to 42, RR is approx. = 22-42, RR- 22-42',
        'RR= 22    -42, RR between 22 and 42, RR ranging from 22 to 42',
        'FVC value for this patient is 500ml to 600ml.',

        # more BP
        'BP < 120/80, BP = 110/70, BP >= 100/70, BP <= 110/70, BP lt. or eq 110/70',
        'her BP was less than 120/80, his BP was gt 110 /70, BP lt. 110/70',
        
        # some blood pressure ranges
        'BP 110/70 to 120/80, BP was between 100/60 and 120/80, BP range: 105/75 - 120/70',

        # sentences containing date expressions
        'Her BP on 3/27 measured 110/70.',
        'Her BP on 3/27 measured 110/70 and her BP on 4/01 measured 115/80.',

        # numbers followed by s, e.g. 90s
        "her HR varied from the 80s to the 90's",
        'her HR was in the 90s',
        "her BP was near the 120/80's",

        # single letter queries
        'T was 98.6 and it went to 98',
        'T98.6 degrees F, p100, pulse 70, derp 80',

        # sentences containing dates and size measurements
        "Her BP on 3/27 from her 12 cm x 9 cm x 6 cm heart was 110/70.",

        # titers and other
        'She was HCV negative, HBV negative, had + HAV IgG, negative IgM.',
        'POSITIVE Titer-1:80',
        'HBSAb titers remained greater than 450.',
        'RPR done at that visit came back positive at a titer of 1:256 and ' +\
        'patient was started on Doxycycline 100mg [**Hospital1 **] pending ' +\
        'LP which was done on [**2699-10-27**].',
        'Hepatitis titers negative (vaccinated for HBV), and anti-smooth '   +\
        'muscle Ab negative.',
        'CMV serologies negative in serum, EBV IgG positive, IgM negative.',
        'She was HCV negative, HBV negative, IgM Titer-1:80, IgG +',

        # gram pos/neg
        'Subsequently the patient was found to have sputum gram stain with ' +\
        '4+ gram positive cocci in pairs, clusters and chains and 1+ gram positive rods.',
        'On [**9-24**] a sputum culture was positive for gram negative rods '+\
        'and he was started on Cipro 500mg po daily for 14 days.',
        'GRAM POSITIVE COCCI.',
        'GRAM POSITIVE COCCI IN PAIRS.',
        'GRAM NEGATIVE ROD(S).',
        'GRAM POSITIVE COCCUS(COCCI).',
        'GRAM POSITIVE COCCI IN CLUSTERS.',
        'NO ENTERIC GRAM NEGATIVE RODS FOUND.',
        'Patient presents with sudden onset of fever, chills, and hypotension ' +\
        'with 3/4 bottles positive gram negative bacteremia.',
        'Cultures came back\npositive with Gram negative rods in her blood on ' +\
        'the 24th and Gram negative rods Pseudomonas in her sputum and E. '     +\
        'coli from\nthe 22nd.',
        'The patient was admitted directly to the ICU with hypotension '        +\
        'secondary to septic shock with a gram negative rod septicemia.',
        'Sputum cultures positive for gram positive cocci in pairs as well as ' +\
        'gram negative diplococci.',
        'She completed a 7 day course of Vancomycin and Zosyn for the BAL '     +\
        'which grew gram positive and negative rods.',

        'She was HCV negative HBV was positive, IgM Titer-1:80, IgG +'
        #--enum "negative, positive, +, 1:80"

        # hypotheticals
        'If the FVC is 1500 ml, you should set the temp to 100.',
        'The FVC is 1500 ml, so you should set the temp to 100.',
        'The FVC is 1500 ml, so set the temp to 100.',
        'Call for instructions when temp > 101.',
        'Call in case temp > 101.'

        # reported problems

        # problem with list recognition in size_measurement_finder.py: recognizes '2 and 5cm' as end-of-list
        'Saturations remain 100% on 40% fio2 and 5cm PEEP',
        'FVC is 1500ml',
        'FVC is 1500 ml',

        # was treating '56 in' as a size measurement
        'obstructive lung disease (FEV1/FVC 56 in [**10-21**]), and s/p' +\
        'recent right TKR on [**3165-1-26**] who',
        'with history of treated MAC, obstructive lung disease' +\
        '(FEV1/FVC 56 in [**10-21**]), and',
    ]

    optparser = optparse.OptionParser(add_help_option=False)
    optparser.add_option('-t', '--terms',    action='store',      dest='terms')
    optparser.add_option('-s', '--sentence', action='store',      dest='sentence')                        
    optparser.add_option('-m', '--min',      action='store',      dest='minval')
    optparser.add_option('-n', '--max',      action='store',      dest='maxval')
    optparser.add_option('-e', '--enumlist', action='store',      dest='enumlist')
    optparser.add_option('-c', '--case',     action='store_true', dest='case_sensitive', default=False)
    optparser.add_option('-v', '--version',  action='store_true', dest='get_version')
    optparser.add_option('-h', '--help',     action='store_true', dest='show_help', default=False)
    optparser.add_option('-y', '--denom',    action='store_true', dest='frac_denom_only', default=False)
    optparser.add_option('-z', '--test',     action='store_true', dest='use_test_sentences', default=False)

    if 1 == len(sys.argv):
        _show_help()
        sys.exit(0)

    opts, other = optparser.parse_args(sys.argv)

    if opts.show_help:
        _show_help()
        sys.exit(0)

    if opts.get_version:
        print(_get_version())
        sys.exit(0)

    terms = opts.terms
    str_minval = opts.minval
    str_maxval = opts.maxval
    sentence = opts.sentence
    is_case_sensitive = opts.case_sensitive
    use_test_sentences = opts.use_test_sentences
    enumlist = opts.enumlist
    frac_denom_only = opts.frac_denom_only

    if not sentence and not use_test_sentences:
        print('A sentence must be provided on the command line.')
        sys.exit(-1)

    # don't need min and max for text extraction
    if not enumlist and (not str_minval or not str_maxval):
        print('Both the --min and --max arguments must be specified.')
        sys.exit(-1)

    if not terms:
        print('One or more search terms must be provided on the command line.')
        sys.exit(-1)

    if not enumlist:
        enumlist = []
        
    # if _TRACE:
    #     print('\n Command line arguments: \n')
    #     print('\t              min value: {0}'.format(str_minval))
    #     print('\t              max value: {0}'.format(str_maxval))
    #     print('\t         case-sensitive: {0}'.format(is_case_sensitive))
    #     print('\t                  terms: {0}'.format(terms))
    #     print('\t               sentence: {0}'.format(sentence))
    #     print('\n')

    sentences = []
    if use_test_sentences:
        sentences = TEST_SENTENCES
    else:
        sentences.append(sentence)

    # end of setup
        
    for sentence in sentences:

        if use_test_sentences:
            print(sentence)

        json_string = run(terms, sentence, str_minval, str_maxval, enumlist,
                          is_case_sensitive, frac_denom_only)
        print(json_string)

