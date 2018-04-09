#!/usr/bin/env python3
"""
Search a sentence for one or more query terms and return any values associated
with those terms. The term list and the sentence are specified on the command
line. Returns results only for values in the range [--min, --max].

Values are assumed to occur AFTER the query term.

The default behavior is to do case-insensitive matching. Case-sensitive
matching can be enabled with a command line option.

Set the variable 'USE_TEST_SENTENCES' below to True to use the test sentences
contained within this file. Use of the test sentences causes the command line
'-s' and '--sentence' options to be ignored.
"""

import re
import os
import sys
import optparse
from collections import namedtuple
from nlp.segmentation import *

try:
    from .measurement_finder import Measurement
except Exception as e:
    print(e)
    from measurement_finder import Measurement

print('Initializing models for value extractor...')
segmentor = Segmentation()
print('Done initializing models for value extractor...')

VERSION_MAJOR = 0
VERSION_MINOR = 3

# set to True to enable debug output
TRACE = False

# set to True to use test sentences and ingore the '-s' and '--sentence' opts
USE_TEST_SENTENCES = False

# match (), {}, and []
str_brackets = r'[(){}\[\]]'
regex_brackets = re.compile(str_brackets)

# matcher for words, including hyphenated words and abbreviations
str_words = r'([-a-zA-Z.]+\s+){0,8}?'  # nongreedy

str_digits = r'\d+'
str_op = r'((is|of|was|approx\.?|approximately|~=|>=|<=|[<>=~\?])\s*)?'
str_approx = r'(~=|~|\b(approx\.?|approximately))'
str_equal = r'\b(equal|eq\.?)'
str_less_than = r'\b(less\s+than|lt\.?)'
str_gt_than = r'\b(greater\s+than|gt\.?)'
str_lt = r'(<|' + str_less_than + r')'
str_lte = r'(<=|' + str_less_than + r'\s+or\s+' + str_equal + r')'
str_gt = r'(>|' + str_gt_than + r')'
str_gte = r'(>=|' + str_gt_than + r'\s+or\s+' + str_equal + r')'
str_separator = r'([-:=\s]\s*)?'
str_num = r'(\d+(\.\d+)?|\.\d+)'
str_cond = r'(?P<cond>' + str_op + r')'
str_val = r'(?P<val>' + str_num + r')'
str_range_sep = r'\s*(-|to)\s*'
str_range = r'(?P<num1>' + str_num + r')' + str_range_sep + \
            r'(?P<num2>' + str_num + r')'

# 'between' and 'from' often denote ranges, such as 'between 10 and 20'
str_bf = r'\b(between|from)\s*'
str_bf_sep = r'\s*(-|to|and)\s*'

str_bf_range = str_bf + \
               r'(?P<num1>' + str_num + r')' + str_bf_sep + \
               r'(?P<num2>' + str_num + r')'

# two integers separated by '/'
str_fraction = r'\d+\s*/\s*\d+'
str_fraction_range = r'(?P<frac1>' + str_fraction + r')' + str_range_sep + \
                     r'(?P<frac2>' + str_fraction + r')'

# between 110/70 and 120/80, from 100/60 to 120/70, etc.
str_bf_fraction_range = str_bf + \
                        r'(?P<frac1>' + str_fraction + r')' + str_bf_sep + \
                        r'(?P<frac2>' + str_fraction + r')'

regex_number = re.compile(str_num)
regex_digits = re.compile(str_digits)
regex_range = re.compile(str_range)
regex_approx = re.compile(str_approx)
regex_lt = re.compile(str_lt)
regex_lte = re.compile(str_lte)
regex_gt = re.compile(str_gt)
regex_gte = re.compile(str_gte)

# condition field values
STR_APPROX = 'APPROX'
STR_LT = 'LESS_THAN'
STR_LTE = 'LESS_THAN_OR_EQUAL'
STR_GT = 'GREATER_THAN'
STR_GTE = 'GREATER_THAN_OR_EQUAL'
STR_EQUAL = 'EQUAL'
STR_RANGE = 'RANGE'
STR_FRACTION_RANGE = 'FRACTION_RANGE'

ValueMeasurement = namedtuple('ValueMeasurement', 'text start end num1 num2 cond')

# indentation levels for JSON output
I1 = ' ' * 4
I2 = ' ' * 8
I3 = ' ' * 12
I4 = ' ' * 16
I5 = ' ' * 20
I6 = ' ' * 24


###############################################################################
def num_to_json(num):
    """
    Format num appropriately for JSON; num could be an int or a 2-tuple.
    """

    if isinstance(num, tuple):
        return '[{0}, {1}]'.format(num[0], num[1])
    else:
        return '"{0}"'.format(num)


###############################################################################
def write_json_result(terms, sentence, results):
    """
    Prettyprint the result as JSON.
    """

    # header
    print('{')
    print(I1 + '"results":[')

    total = len(results)

    print(I2 + '{')
    print(I3 + '"sentence":"{0}",'.format(sentence))
    print(I3 + '"measurementCount":"{0}",'.format(len(results)))
    print(I3 + '"measurements":[')

    num_written = 0
    for vm in results:
        print(I4 + '{')
        print(I5 + '"text":"{0}",'.format(sentence[vm.start:vm.end]))
        print(I5 + '"start":"{0}",'.format(vm.start))
        print(I5 + '"end":"{0}",'.format(vm.end))
        print(I5 + '"condition":"{0}",'.format(vm.cond))
        print(I5 + '"X":{0}'.format(num_to_json(vm.num1)), end='')
        if -1 != vm.num2:
            print(',')
            print(I5 + '"Y":{0}'.format(num_to_json(vm.num2)))
        else:
            print('')
        print(I4 + '}', end='')

        num_written = num_written + 1
        if num_written < total:
            print(',')
        else:
            print('')

    print(I3 + '],')

    # join the query terms into a comma-separated list
    words = ','.join(terms)

    print(I3 + '"terms":"{0}",'.format(words))
    if total > 0:
        print(I3 + '"querySuccess":"TRUE"')
    else:
        print(I3 + '"querySuccess":"FALSE"')

    print(I2 + '}')

    # footer
    print(I1 + ']')
    print('}')


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
def update_match_results(match, spans, results, num1, num2, cond):
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
        meas = ValueMeasurement(match_text, start, end, num1, num2, cond)
        results.append(meas)
        spans.append((start, end))


###############################################################################
def extract_value(query_term, sentence, minval, maxval):
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

    # form a query string from either a standalone query term or a
    # query term followed by optional words plus a separator symbol
    str_query = r'\b(' + query_term + r'\s*' + r'|' + \
                query_term + r'\s+([a-zA-Z]+\s*)' + r')' + str_separator
    str_start = str_query + r'(?P<words>' + str_words + r')'

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

    spans = []  # [start, end) character offsets of each match
    results = []  # ValueMeasurement namedtuple results

    # check for bf fraction ranges first
    iterator = re.finditer(str_bf_fraction_range_query, sentence)
    for match in iterator:
        (n1, d1) = get_num_and_denom(match.group('frac1'))
        (n2, d2) = get_num_and_denom(match.group('frac2'))
        # accept a fraction range if both numerators are contained in [minval, maxval]
        if n1 >= minval and n1 <= maxval and n2 >= minval and n2 <= maxval:
            cond = 'FRACTION_RANGE'
            match_text = match.group().strip()
            start = match.start()
            end = start + len(match_text)
            meas = ValueMeasurement(match_text, start, end, (n1, d1), (n2, d2), cond)
            results.append(meas)
            spans.append((start, end))

    # check for other fraction ranges
    iterator = re.finditer(str_fraction_range_query, sentence)
    for match in iterator:
        (n1, d1) = get_num_and_denom(match.group('frac1'))
        (n2, d2) = get_num_and_denom(match.group('frac2'))
        # accept a fraction range if both numerators are contained in [minval, maxval]
        if n1 >= minval and n1 <= maxval and n2 >= minval and n2 <= maxval:
            cond = STR_FRACTION_RANGE
            update_match_results(match, spans, results, (n1, d1), (n2, d2), cond)

    # check for fractions
    iterator = re.finditer(str_fraction_query, sentence)
    for match in iterator:
        (n, d) = get_num_and_denom(match.group('frac'))
        # accept a fraction if numerator is contained in [minval, maxval]
        if n >= minval and n <= maxval:
            words = match.group('words')
            cond_words = match.group('cond').strip()
            cond = cond_to_string(words, cond_words)
            update_match_results(match, spans, results, (n, d), -1, cond)

    # check for bf numeric ranges
    iterator = re.finditer(str_bf_range_query, sentence)
    for match in iterator:
        num1 = float(match.group('num1'))
        num2 = float(match.group('num2'))
        # accept a numeric range if both numbers are contained in [minval, maxval]
        if num1 >= minval and num1 <= maxval and num2 >= minval and num2 <= maxval:
            cond = STR_RANGE
            update_match_results(match, spans, results, num1, num2, cond)

            # check for numeric ranges
    iterator = re.finditer(str_range_query, sentence)
    for match in iterator:
        num1 = float(match.group('num1'))
        num2 = float(match.group('num2'))
        # accept a numeric range if both numbers are contained in [minval, maxval]
        if num1 >= minval and num1 <= maxval and num2 >= minval and num2 <= maxval:
            cond = STR_RANGE
            update_match_results(match, spans, results, num1, num2, cond)

    # check for op-value matches
    iterator = re.finditer(str_op_val_query, sentence)
    for match in iterator:
        val = float(match.group('val'))
        if val >= minval and val <= maxval:
            words = match.group('words')
            cond_words = match.group('cond').strip()
            cond = cond_to_string(words, cond_words)
            update_match_results(match, spans, results, val, -1, cond)

    # check for wds-value matches
    iterator = re.finditer(str_wds_val_query, sentence)
    for match in iterator:
        val = float(match.group('val'))
        if val >= minval and val <= maxval:
            update_match_results(match, spans, results, val, -1, -1)

    return results


###############################################################################
def erase(sentence, start, end):
    """
    Overwrite characters [start, end) with whitespace.
    """
    piece1 = sentence[:start]
    piece2 = ' ' * (end - start)
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

    return sentence


###############################################################################
def get_version():
    return 'value_extractor {0}.{1}'.format(VERSION_MAJOR, VERSION_MINOR)


###############################################################################
def show_help():
    print(get_version())
    print("""
    USAGE: python3 ./value_extractor.py -t <terms> -s <sentence> --min <minval> --max <maxval> [-i]

    OPTIONS:
        -h, --help                      Print this information and exit.
        -v, --version                   Print version information and exit.
        -c, --case                      Preserve case when matching terms.
        -t, --terms    <quoted string>  List of comma-separated search terms.
        -s, --sentence <quoted string>  Sentence to be processed.
        -m, --min      <float or int>   Minimum acceptable value.
        -n, --max      <float or int>   Maximum acceptable value.

    """)


###############################################################################

def process_sentence(term_list, sentence_value, minimum_value, maximum_value):
    process_results = []
    for term in term_list:
        values = extract_value(term, sentence_value, minimum_value, maximum_value)
        process_results.extend(values)
    return process_results


def process_sentence_full(term_list, text, minimum_value, maximum_value, is_case_sensitive_text=True):
    sentence_list = segmentor.parse_sentences(text)
    process_results = []
    for s in sentence_list:
        s = clean_sentence(s, is_case_sensitive_text)
        value_results = process_sentence(term_list, s, minimum_value, maximum_value)
        if len(value_results) > 0:
            for x in value_results:
                process_results.append(Measurement(sentence=s, text=s[x.start:x.end], start=x.start, end=x.end,
                                                   condition=x.cond, X=x.num1, Y=x.num2))

    return process_results


###############################################################################
if __name__ == '__main__':

    test_sentences = [

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
        'BP 110/70 to 120/80, BP was between 100/60 and 120/80, BP range: 105/75 - 120/70'
    ]

    optparser = optparse.OptionParser(add_help_option=False)
    optparser.add_option('-t', '--terms', action='store', dest='terms')
    optparser.add_option('-s', '--sentence', action='store', dest='sentence')
    optparser.add_option('-m', '--min', action='store', dest='minval')
    optparser.add_option('-n', '--max', action='store', dest='maxval')
    optparser.add_option('-c', '--case', action='store_true', dest='case_sensitive', default=False)
    optparser.add_option('-v', '--version', action='store_true', dest='get_version')
    optparser.add_option('-h', '--help', action='store_true', dest='show_help', default=False)

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

    terms = opts.terms.split(',')  # produces a list
    terms = [term.strip() for term in terms]

    str_minval = opts.minval
    str_maxval = opts.maxval
    sentence = opts.sentence
    is_case_sensitive = opts.case_sensitive

    if not sentence and not USE_TEST_SENTENCES:
        print('A sentence must be specified on the command line.')
        sys.exit(-1)

    if not str_minval or not str_maxval:
        print('Both the --min and --max arguments must be specified.')
        sys.exit(-1)

    if TRACE:
        print('\n Command line arguments: \n')
        print('\t              min value: {0}'.format(str_minval))
        print('\t              max value: {0}'.format(str_maxval))
        print('\t         case-sensitive: {0}'.format(is_case_sensitive))
        print('\t                  terms: {0}'.format(terms))
        print('\t               sentence: {0}'.format(sentence))
        print('\n')

    # save a copy of the original terms
    original_terms = terms.copy()

    # convert terms to lowercase unless doing a case-sensitive match
    if not is_case_sensitive:
        terms = [term.lower() for term in terms]

    # do range check on numerator values for fractions
    if -1 != str_minval.find('/'):
        str_minval = str_minval.split('/')[0]
    if -1 != str_maxval.find('/'):
        str_maxval = str_maxval.split('/')[0]

    min_value = float(str_minval)
    max_value = float(str_maxval)

    sentences = []
    if USE_TEST_SENTENCES:
        sentences = test_sentences
    else:
        sentences.append(sentence)

    for sentence in sentences:
        original_sentence = sentence
        sentence = clean_sentence(sentence, is_case_sensitive)
        results = process_sentence(terms, sentence, min_value, max_value)

        # order results by their starting character offset
        results = sorted(results, key=lambda x: x.start)

        # write JSON result to stdout
        write_json_result(original_terms, original_sentence, results)
