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
            minValue         minimum value of x and y, if neither is EMPTY_FIELD
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

# imports from clarity core
from nlp.finder.date_finder import run as run_date_finder, DateValue, EMPTY_FIELD as EMPTY_DATE_FIELD
from nlp.finder.size_measurement_finder import run as run_size_measurement, SizeMeasurement, EMPTY_FIELD as EMPTY_SMF_FIELD


VERSION_MAJOR = 0
VERSION_MINOR = 5

# set to True to enable debug output
TRACE = False

# serializable result object; measurementList is an array of Value namedtuples

EMPTY_FIELD = -1  # ignore any field with this value
VALUE_RESULT_FIELDS = ['sentence', 'measurementCount', 'terms', 'querySuccess', 'measurementList']
ValueResult = namedtuple('ValueResult', VALUE_RESULT_FIELDS)

VALUE_FIELDS = ['text', 'start', 'end', 'condition', 'matchingTerm', 'x', 'y', 'minValue', 'maxValue']
Value = namedtuple('Value', VALUE_FIELDS)


# match (), {}, and []
str_brackets   = r'[(){}\[\]]' 
regex_brackets = re.compile(str_brackets)

# hyphenated words, abbreviations
str_text_word = r'[-a-zA-Z.]+'

# this is a catchall that finds words, titer expressions (1:200),
# '+' and '-' symbols, +/-, etc.
str_enumlist_value = r'[-a-zA-Z:\d/\+()]+'

# matcher for 'words', including hyphenated words and abbreviations
str_words     = r'([-a-zA-Z.]+\s+){0,8}?' # nongreedy

str_digits    = r'\d+'
str_op        = r'((is|of|was|approx\.?|approximately|~=|>=|<=|[<>=~\?])\s*)?'
str_approx    = r'(~=|~|\b(approx\.?|approximately))'
str_equal     = r'\b(equal|eq\.?)'
str_less_than = r'\b(less\s+than|lt\.?)'
str_gt_than   = r'\b(greater\s+than|gt\.?)'
str_lt        = r'(<|' + str_less_than + r')'
str_lte       = r'(<=|' + str_less_than + r'\s+or\s+' + str_equal + r')'
str_gt        = r'(>|' + str_gt_than + r')'
str_gte       = r'(>=|' + str_gt_than + r'\s+or\s+' + str_equal + r')'
str_separator = r'([-:=\s]\s*)?'
str_num       = r'(\d+(\.\d+)?|\.\d+)'
str_cond      = r'(?P<cond>' + str_op + r')'
str_val       = r'(?P<val>' + str_num + r')(\'?s)?'
str_range_sep = r'\s*(-|to(\s+the)?)\s*'
str_range     = r'(?P<num1>' + str_num + r')(\'?s)?' + str_range_sep + \
                r'(?P<num2>' + str_num + r')(\'?s)?'

# 'between' and 'from' often denote ranges, such as 'between 10 and 20'
str_bf     = r'\b(between|from)\s*'
str_bf_sep = r'\s*(-|to|and)\s*'

str_bf_range = str_bf + \
               r'(?P<num1>' + str_num + r')(\'?s)?' + str_bf_sep + \
               r'(?P<num2>' + str_num + r')(\'?s)?'

# two integers separated by '/'
str_fraction  = r'\d+\s*/\s*\d+'
str_fraction_range  = r'(?P<frac1>' + str_fraction + r')(\'?s)?' + str_range_sep + \
                      r'(?P<frac2>' + str_fraction + r')(\'?s)?'

# between 110/70 and 120/80, from 100/60 to 120/70, etc.
str_bf_fraction_range = str_bf + \
                        r'(?P<frac1>' + str_fraction + r')(\'?s)?' + str_bf_sep + \
                        r'(?P<frac2>' + str_fraction + r')(\'?s)?'

regex_num      = re.compile(str_num)
regex_fraction = re.compile(str_fraction)
regex_number = re.compile(str_num)
regex_digits = re.compile(str_digits)
regex_range  = re.compile(str_range)
regex_approx = re.compile(str_approx)
regex_lt     = re.compile(str_lt)
regex_lte    = re.compile(str_lte)
regex_gt     = re.compile(str_gt)
regex_gte    = re.compile(str_gte)

# condition field values
STR_APPROX         = 'APPROX'
STR_LT             = 'LESS_THAN'
STR_LTE            = 'LESS_THAN_OR_EQUAL'
STR_GT             = 'GREATER_THAN'
STR_GTE            = 'GREATER_THAN_OR_EQUAL'
STR_EQUAL          = 'EQUAL'
STR_RANGE          = 'RANGE'
STR_FRACTION_RANGE = 'FRACTION_RANGE'

ValueMeasurement = namedtuple('ValueMeasurement', 'text start end num1 num2 cond matching_term')

# indentation levels for JSON output
I1 = ' '*4
I2 = ' '*8
I3 = ' '*12
I4 = ' '*16
I5 = ' '*20
I6 = ' '*24

# used to restore original terms
term_dict = {}

###############################################################################
def to_json(original_terms, original_sentence, results, is_text):
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
        m_dict['matchingTerm'] = term_dict[m.matching_term]
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
def cond_to_string(words, cond):
    """
    Determine the relationship between the query term and the value.
    """
    
    # need to check two strings, so concat and run regex on result
    s = words + ' ' + cond

    if regex_approx.search(s):
        result = STR_APPROX
    elif regex_lte.search(s):
        result = STR_LTE
    elif regex_gte.search(s):
        result = STR_GTE
    elif regex_lt.search(s):
        result = STR_LT
    elif regex_gt.search(s):
        result = STR_GT
    else:
        result = STR_EQUAL
    
    return result

###############################################################################
def get_num_and_denom(str_fraction):
    """
    Convert a fraction (such as 110/70) to an integer 2-tuple.
    """

    values = str_fraction.strip().split('/')
    assert 2 == len(values)
    return (int(values[0]), int(values[1]))

###############################################################################
def update_match_results(match, spans, results, num1, num2, cond, matching_term):
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
            break

    if keep_it:
        meas = ValueMeasurement(match_text, start, end, num1, num2, cond, matching_term)
        results.append(meas)
        spans.append( (start, end))

###############################################################################
def get_query_start(query_term):
    """
    Construct the starting string for a value extraction query.
    """

    # Form a query string from either a standalone query term or a
    # query term followed by optional words plus a separator symbol.
    if len(query_term) > 1:
        str_query = r'\b(' + query_term + r'\s*' + r'|' + \
                    query_term + r'\s+([a-zA-Z]+\s*)' + r')' + str_separator
        str_start = str_query + r'(?P<words>' + str_words + r')'
    else:
        # If the query term is a single letter, it cannot be followed by
        # another letter, since likely starting a new word. Must be followed
        # either by a non-letter character, such as a digit or whitespace.
        str_query = r'\b(' + query_term + r'(?![a-zA-Z])\s*' + r'|' + \
                    query_term + r'\s+([a-zA-Z]+\s*)' + r')' + str_separator
        str_start = str_query + r'(?P<words>' + str_words + r')'

    return str_start

###############################################################################
def extract_enumlist_value(query_term, sentence, filter_words):
    """
    Extract a word to match the query term, and accept if that word
    appears in the result filter.
    """

    results = []
    
    str_start = get_query_start(query_term)
    str_word_query = str_start + r'(?P<word>' + str_enumlist_value + r')'

    found_it = False
    iterator = re.finditer(str_word_query, sentence)
    for match in iterator:
        word = match.group('word')

        # check word against all filter words, keep if found
        for fw in filter_words:
            if word == fw:
                found_it = True
                break

    if found_it:
        meas = ValueMeasurement(word, match.start(), match.end(),
                                word, EMPTY_FIELD, STR_EQUAL, query_term)
        results.append(meas)

    return results

        
###############################################################################
def extract_value(query_term, sentence, minval, maxval, denom_only):
    """
    Search the sentence for the query term, find associated values that fit
    one of the regex patterns, extract the values, check the value against
    [minval, maxval], determine relationship between query term and value
    (i.e. less than, greater than, etc.), and return results.
    """
    
    # no values to extract if the sentence contains no digits
    match = regex_digits.search(sentence)
    if not match:
        return []

    str_start = get_query_start(query_term)
    
    # find two ints separated by '/', such as blood pressure values
    str_fraction_query = str_start + str_cond + r'(?P<frac>' + str_fraction + r')'
    
    # two fractions with a range separator inbetween
    str_fraction_range_query = str_start + str_cond + str_fraction_range
    str_bf_fraction_range_query = str_start + str_cond + str_bf_fraction_range
    
    # <query> <operator> <value>
    str_op_val_query = str_start + str_cond + str_val
    
    # two numbers with a range separator inbetween
    str_range_query = str_start + str_cond + str_range
    str_bf_range_query = str_start + str_cond + str_bf_range

    # <query> <words> <value>
    str_wds_val_query = str_start + str_val

    spans   = []  # [start, end) character offsets of each match
    results = []  # ValueMeasurement namedtuple results

    # check for bf fraction ranges first
    iterator = re.finditer(str_bf_fraction_range_query, sentence)
    for match in iterator:
        (n1, d1) = get_num_and_denom(match.group('frac1'))
        (n2, d2) = get_num_and_denom(match.group('frac2'))

        # keep either numerator or denom, according to user preference
        x1 = n1
        x2 = n2
        if denom_only:
            x1 = d1
            x2 = d2
        
        # accept a fraction range if both values are contained in [minval, maxval]
        if x1 >= minval and x1 <= maxval and x2 >= minval and x2 <= maxval:
            cond = 'FRACTION_RANGE'
            match_text = match.group().strip()
            start = match.start()
            end = start + len(match_text)
            meas = ValueMeasurement(match_text, start, end, x1, x2, cond, query_term)
            results.append(meas)
            spans.append( (start, end))

    # check for other fraction ranges
    iterator = re.finditer(str_fraction_range_query, sentence)
    for match in iterator:
        (n1, d1) = get_num_and_denom(match.group('frac1'))
        (n2, d2) = get_num_and_denom(match.group('frac2'))

        # keep either numerator or denom, according to user preference
        x1 = n1
        x2 = n2
        if denom_only:
            x1 = d1
            x2 = d1
            
        # accept a fraction range if both values are contained in [minval, maxval]
        if x1 >= minval and x1 <= maxval and x2 >= minval and x2 <= maxval:
            cond = STR_FRACTION_RANGE
            update_match_results(match, spans, results, x1, x2, cond, query_term)

    # check for fractions
    iterator = re.finditer(str_fraction_query, sentence)
    for match in iterator:
        (n, d) = get_num_and_denom(match.group('frac'))

        # keep either numerator or denom, according to user preference
        x = n
        if denom_only:
            x = d
        
        # accept a fraction if value is contained in [minval, maxval]
        if x >= minval and x <= maxval:
            words = match.group('words')
            cond_words = match.group('cond').strip()
            cond = cond_to_string(words, cond_words)
            update_match_results(match, spans, results, x, EMPTY_FIELD, cond, query_term)

    # check for bf numeric ranges
    iterator = re.finditer(str_bf_range_query, sentence)
    for match in iterator:
        num1 = float(match.group('num1'))
        num2 = float(match.group('num2'))
        # accept a numeric range if both numbers are contained in [minval, maxval]
        if num1 >= minval and num1 <= maxval and num2 >= minval and num2 <= maxval:
            cond = STR_RANGE
            update_match_results(match, spans, results, num1, num2, cond, query_term)        
            
    # check for numeric ranges
    iterator = re.finditer(str_range_query, sentence)
    for match in iterator:
        num1 = float(match.group('num1'))
        num2 = float(match.group('num2'))
        # accept a numeric range if both numbers are contained in [minval, maxval]
        if num1 >= minval and num1 <= maxval and num2 >= minval and num2 <= maxval:
            cond = STR_RANGE
            update_match_results(match, spans, results, num1, num2, cond, query_term)

    # check for op-value matches
    iterator = re.finditer(str_op_val_query, sentence)
    for match in iterator:
        val = float(match.group('val'))
        if val >= minval and val <= maxval:
            words = match.group('words')
            cond_words = match.group('cond').strip()
            cond = cond_to_string(words, cond_words)
            update_match_results(match, spans, results, val, EMPTY_FIELD, cond, query_term)
            
    # check for wds-value matches
    iterator = re.finditer(str_wds_val_query, sentence)
    for match in iterator:
        val = float(match.group('val'))
        if val >= minval and val <= maxval:
            update_match_results(match, spans, results, val, EMPTY_FIELD, EMPTY_FIELD, query_term)

    return results

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
def clean_sentence(sentence, is_case_sensitive):
    """
    Do some preliminary processing on the sentence prior to value extraction.
    """
    
    # erase [], {}, or () from the sentence
    sentence = regex_brackets.sub(' ', sentence)

    # convert to lowercase unless case sensitive match enabled
    if not is_case_sensitive:
        sentence = sentence.lower()

    # find date expressions in the sentence
    json_string = run_date_finder(sentence)
    json_data = json.loads(json_string)

    # unpack JSON result into a list of DateMeasurement namedtuples
    dates = [DateValue(**record) for record in json_data]

    # erase each date from the sentence
    for date in dates:
        start = int(date.start)
        end   = int(date.end)
        sentence = erase(sentence, start, end)

    # find size measurements in the sentence
    json_string = run_size_measurement(sentence)
    json_data = json.loads(json_string)

    # unpack JSON result into a list of SizeMeasurement namedtuples
    measurements = [SizeMeasurement(**m) for m in json_data]

    # erase each measurement from the sentence
    for m in measurements:
        start = int(m.start)
        end   = int(m.end)
        sentence = erase(sentence, start, end)
        
    return sentence

###############################################################################
def get_version():
    return 'value_extractor {0}.{1}'.format(VERSION_MAJOR, VERSION_MINOR)
        
###############################################################################
def show_help():
    print(get_version())
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
def run(term_string, sentence, str_minval=None, str_maxval=None,
        enumlist=None, is_case_sensitive=False, is_denom_only=False):
    """
    Run the value extractor for all query terms and return a list of
    ValueMeasurement namedtuples.
    """

    # use default minval and maxval if not provided
    if enumlist is None and str_minval is None:
        str_minval = '-' + str(sys.float_info.max)
    if enumlist is None and str_maxval is None:
        str_maxval = str(sys.float_info.max)
    
    # save a copy of the original sentence (needed for results)
    original_sentence = sentence

    terms = term_string.split(',') # produces a list
    terms = [term.strip() for term in terms]

    if enumlist:
        filter_terms = enumlist.split(',')
        filter_terms = [term.strip() for term in filter_terms]

    # save a copy of the original terms
    original_terms = terms.copy()

    # convert terms to lowercase unless doing a case-sensitive match
    if not is_case_sensitive:
        terms = [term.lower() for term in terms]

        if enumlist:
            filter_terms = [ft.lower() for ft in filter_terms]

    # map the new terms to the original, so can restore in output
    for i in range(len(terms)):
        new_term = terms[i]
        original_term = original_terms[i]
        term_dict[new_term] = original_term

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

    sentence = clean_sentence(sentence, is_case_sensitive)

    results = []
    for term in terms:
        if enumlist:
            # extract a single enumlist value
            values = extract_enumlist_value(term, sentence, filter_terms)
        else:
            # extract a single numeric value
            values = extract_value(term, sentence, minval, maxval, is_denom_only)
        results.extend(values)

    # order results by their starting character offset
    results = sorted(results, key=lambda x: x.start)
    
    return to_json(original_terms, original_sentence, results, enumlist)

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
        'VS before transfer were 85 BP 99/34 RR 20 SpO2% 99/bipap 10/5 50%.',
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
        'Sputum cultures positive for gram positive cocci in pairs as well as gram negative diplococci.',
        'She completed a 7 day course of Vancomycin and Zosyn for the BAL '     +\
        'which grew gram positive and negative rods.',
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
        show_help()
        sys.exit(0)

    opts, other = optparser.parse_args(sys.argv)

    if opts.show_help:
        show_help()
        sys.exit(0)

    if opts.get_version:
        print(get_version())
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
        
    # if TRACE:
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

