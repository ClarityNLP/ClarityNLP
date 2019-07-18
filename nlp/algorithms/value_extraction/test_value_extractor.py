#!/usr/bin/python3
"""
Test program for the value extractor.

Run from the same folder as value_extractor.py.

"""

import re
import os
import sys
import json
import argparse
from collections import namedtuple

import value_extractor as ve

_MODULE_NAME = 'test_value_extractor.py'

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# set to True to enable debug output
_TRACE = False

TEST_RESULT_FIELDS = ['meas_count', 'term', 'x', 'y', 'condition']
TestResult = namedtuple('TestResult', TEST_RESULT_FIELDS)


###############################################################################
def compare_results(term_string, test_data, minval, maxval):
    """
    Run the value extractor on the test data using the supplied term string
    and check the results.
    """

    for sentence,expected in test_data.items():

        # run value extractor on the next test sentence
        json_result = ve.run(term_string, sentence, minval, maxval)

        # load the json result and decode into a ValueResult namedtuple
        result_data = json.loads(json_result)
        value_result = ve.ValueResult(**result_data)

        # check relevant fields
        assert value_result.measurementCount == expected.meas_count

        failures = []
        for value in value_result.measurementList:
            if value['matchingTerm'] != expected.term:
                failures.append('\texpected matching term: {0}, got: {1}'.
                                format(expected.term, value['matchingTerm']))
            if value['x'] != expected.x:
                failures.append('\texpected x: {0}, got: {1}'.
                                format(expected.x, value['x']))
            if value['y'] != expected.y:
                failures.append('\texpected y: {0}, got: {1}'.
                                format(expected.y, value['y']))
            if value['condition'] != expected.condition:
                failures.append('\texpected condition: {0}, got: {1}'.
                                format(expected.condition, value['condition']))
            if len(failures) > 0:
                print(sentence)
                for f in failures:
                    print(f)
    
    

###############################################################################
if __name__ == '__main__':

    minval = 0
    maxval = 1000

    # find values using "LVEF" as the search term
    term_string = "lvef"
    test_data = {
        'The LVEF is 40%.':TestResult(1, 'lvef', 40, None, ve.STR_EQUAL),
        'Hyperdynamic LVEF >75%':TestResult(1, 'lvef', 75, None, ve.STR_GT),
        'Overall normal LVEF (>55%).':TestResult(1, 'lvef', 55, None, ve.STR_GT),
        'Overall left ventricular systolic function is normal '                \
        '(LVEF 60%).':TestResult(1, 'lvef', 60, None, ve.STR_EQUAL),
        'Overall left ventricular systolic function is normal '                \
        '(LVEF>55%).':TestResult(1, 'lvef', 55, None, ve.STR_GT),
        'Overall left ventricular systolic function is low normal '            \
        '(LVEF 50-55%).':TestResult(1, 'lvef', 50, 55, ve.STR_RANGE),
        'LVEF was estimated at 55% and ascending aorta measured '              \
        '5.1 centimeters.':TestResult(1, 'lvef', 55, None, ve.STR_EQUAL),
        'Overall left ventricular systolic function is severely depressed '    \
        '(LVEF= 20 %).':TestResult(1, 'lvef', 20, None, ve.STR_EQUAL),
        'Overall left ventricular systolic function is severely depressed '    \
        '(LVEF= < 30 %).':TestResult(1, 'lvef', 30, None, ve.STR_LT),
        'Overall left ventricular systolic function is severely depressed '    \
        '(LVEF= 15-20 %).':TestResult(1, 'lvef', 15, 20, ve.STR_RANGE),
        'Conclusions: There is moderate global left ventricular hypokinesis '  \
        '(LVEF 35-40%).':TestResult(1, 'lvef', 35, 40, ve.STR_RANGE),
        'Overall left ventricular systolic function is moderately depressed '  \
        '(LVEF~25-30 %).':TestResult(1, 'lvef', 25, 30, ve.STR_RANGE),
        'Normal LV wall thickness, cavity size and regional/global systolic '  \
        'function (LVEF >55%).':TestResult(1, 'lvef', 55, None, ve.STR_GT),
        'Overall left ventricular systolic function is mildly depressed '      \
        '(LVEF= 40-45 %) with inferior akinesis.':TestResult(1, 'lvef', 40, 45, ve.STR_RANGE),
        'Left ventricular wall thickness, cavity size and regional/global '    \
        'systolic function are normal (LVEF >55%).':TestResult(1, 'lvef', 55, None, ve.STR_GT),
        'There is mild symmetric left ventricular hypertrophy with normal '    \
        'cavity size and regional/global systolic function '                   \
        '(LVEF>55%).':TestResult(1, 'lvef', 55, None, ve.STR_GT),
        'LEFT VENTRICLE: Overall normal LVEF (>55%). Beat-to-beat '            \
        'variability on LVEF due to irregular rhythm/premature '               \
        'beats.':TestResult(1, 'lvef', 55, None, ve.STR_GT),
        'Overall left ventricular systolic function is moderately '            \
        'depressed (LVEF= 30 % with relative preservation of the '             \
        'lateral, inferolateral and inferior walls).':TestResult(1, 'lvef', 30, None, ve.STR_EQUAL)
    }

    compare_results(term_string, test_data, minval, maxval)
    
    # find values using "ejection fraction" as the search term
    term_string = "ejection fraction"
    test_data = {
        'Left Ventricle - Ejection Fraction:  '                                \
        '60%  >= 55%':TestResult(1, 'ejection fraction', 60, None, ve.STR_EQUAL),
        'Left Ventricle - Ejection Fraction:  '                                \
        '55% (nl >=55%)':TestResult(1, 'ejection fraction', 55, None, ve.STR_EQUAL),
        'Left Ventricle - Ejection Fraction:  '                                \
        '50% to 55%  >= 55%':TestResult(1, 'ejection fraction', 50, 55, ve.STR_RANGE),
        '53-year-old male with crack lung, CHF and ejection fraction '         \
        'of 20%, with abdominal pain and fever, who has failed antibiotic '    \
        'monotherapy.':TestResult(1, 'ejection fraction', 20, None, ve.STR_EQUAL),                                
        'His most recent echocardiogram was in [**2648-8-10**], which showed ' \
        'an ejection fraction of approximately 60 to 70% and a mildly '        \
        'dilated left atrium.':TestResult(1, 'ejection fraction', 60, 70, ve.STR_RANGE),
        'He underwent cardiac catheterization on [**7-30**], which revealed '  \
        'severe aortic stenosis with an aortic valve area of 0.8 '             \
        'centimeters squared, an ejection fraction '                           \
        'of 46%.':TestResult(1, 'ejection fraction', 46, None, ve.STR_EQUAL),
        'The echocardiogram was done on [**2-15**], and per telemetry, '       \
        'showed inferior hypokinesis with an ejection fraction of 50%, and '   \
        'an aortic valve area of 0.7 cm2 with trace mitral '                   \
        'regurgitation.':TestResult(1, 'ejection fraction', 50, None, ve.STR_EQUAL),
        'Echocardiogram in [**3103-2-6**] showed a large left atrium, '        \
        'ejection fraction 60 to 65% with mild symmetric left ventricular '    \
        'hypertrophy, trace aortic regurgitation, mild '                       \
        'mitral regurgitation.':TestResult(1, 'ejection fraction', 60, 65, ve.STR_RANGE),
        "Myocardium:  The patient's ejection fraction at the outside "         \
        'hospital showed a 60% preserved ejection fraction and his ACE '       \
        'inhibitors were titrated up throughout this hospital stay as '        \
        'tolerated.':TestResult(1, 'ejection fraction', 60, None, ve.STR_EQUAL),
        'Overall left ventricular systolic function is probably borderline '   \
        'depressed (not fully assessed; estimated ejection fraction ?50%); '   \
        'intrinsic function may be more depressed given the severity of '      \
        'the regurgitation.':TestResult(1, 'ejection fraction', 50, None, ve.STR_EQUAL)
    }

    compare_results(term_string, test_data, minval, maxval)
    
