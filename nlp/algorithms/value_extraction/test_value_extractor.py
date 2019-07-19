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

TEST_RESULT_FIELDS = ['term', 'x', 'y', 'condition']
TestResult = namedtuple('TestResult', TEST_RESULT_FIELDS)


###############################################################################
def compare_fields(field_name, computed, expected, failure_list):
    
    if computed != expected:
        failure_list.append('\texpected {0}: {1}, got: {2}'.
                            format(field_name, expected, computed))

    return failure_list


###############################################################################
def compare_results(term_string, test_data, minval, maxval, denom_only=False):
    """
    Run the value extractor on the test data using the supplied term string
    and check the results.
    """

    for sentence,expected_list in test_data.items():

        # run value extractor on the next test sentence
        json_result = ve.run(
            term_string,
            sentence,
            minval,
            maxval,
            is_denom_only=denom_only
        )
        
        # load the json result and decode into a ValueResult namedtuple
        result_data = json.loads(json_result)
        value_result = ve.ValueResult(**result_data)

        if value_result.measurementCount != len(expected_list):
            print('\tMismatch in computed vs. expected results: ')
            print('\tSentence: {0}'.format(sentence))
            print('\tComputed: ')
            for m in value_result.measurementList:
                print('\t\t{0}'.format(m))
            print('\tExpected: ')
            for e in expected_list:
                print('\t\t{0}'.format(e))
            return
        
        # check fields
        failures = []
        for i, value in enumerate(value_result.measurementList):

            computed = value['matchingTerm']
            expected = expected_list[i].term
            failures = compare_fields('matching term', computed, expected, failures)

            computed = value['x']
            expected = expected_list[i].x
            failures = compare_fields('x', computed, expected, failures)

            computed = value['y']
            expected = expected_list[i].y
            failures = compare_fields('y', computed, expected, failures)

            computed = value['condition']
            expected = expected_list[i].condition
            failures = compare_fields('condition', computed, expected, failures)
                
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
        'The LVEF is 40%.':[
            TestResult('lvef', 40, None, ve.STR_EQUAL)
        ],
        'Hyperdynamic LVEF >75%':[
            TestResult('lvef', 75, None, ve.STR_GT)
        ],
        'Overall normal LVEF (>55%).':[
            TestResult('lvef', 55, None, ve.STR_GT)
        ],
        'Overall left ventricular systolic function is normal (LVEF 60%).':[
            TestResult('lvef', 60, None, ve.STR_EQUAL)
        ],
        'Overall left ventricular systolic function is normal (LVEF>55%).':[
            TestResult('lvef', 55, None, ve.STR_GT)
        ],
        'Overall left ventricular systolic function is low normal (LVEF 50-55%).':[
            TestResult('lvef', 50, 55, ve.STR_RANGE)
        ],
        'LVEF was estimated at 55% and ascending aorta measured 5.1 centimeters.':[
            TestResult('lvef', 55, None, ve.STR_EQUAL)
        ],
        'Overall left ventricular systolic function is severely '              \
        'depressed (LVEF= 20 %).':[
            TestResult('lvef', 20, None, ve.STR_EQUAL)
        ],
        'Overall left ventricular systolic function is severely depressed '    \
        '(LVEF= < 30 %).':[
            TestResult('lvef', 30, None, ve.STR_LT)
        ],
        'Overall left ventricular systolic function is severely depressed '    \
        '(LVEF= 15-20 %).':[
            TestResult('lvef', 15, 20, ve.STR_RANGE)
        ],
        'Conclusions: There is moderate global left ventricular hypokinesis '  \
        '(LVEF 35-40%).':[
            TestResult('lvef', 35, 40, ve.STR_RANGE)
        ],
        'Overall left ventricular systolic function is moderately depressed '  \
        '(LVEF~25-30 %).':[
            TestResult('lvef', 25, 30, ve.STR_RANGE)
        ],
        'Normal LV wall thickness, cavity size and regional/global systolic '  \
        'function (LVEF >55%).':[
            TestResult('lvef', 55, None, ve.STR_GT)
        ],
        'Overall left ventricular systolic function is mildly depressed '      \
        '(LVEF= 40-45 %) with inferior akinesis.':[
            TestResult('lvef', 40, 45, ve.STR_RANGE)
        ],
        'Left ventricular wall thickness, cavity size and regional/global '    \
        'systolic function are normal (LVEF >55%).':[
            TestResult('lvef', 55, None, ve.STR_GT)
        ],
        'There is mild symmetric left ventricular hypertrophy with normal '    \
        'cavity size and regional/global systolic function '                   \
        '(LVEF>55%).':[
            TestResult('lvef', 55, None, ve.STR_GT)
        ],
        'LEFT VENTRICLE: Overall normal LVEF (>55%). Beat-to-beat '            \
        'variability on LVEF due to irregular rhythm/premature '               \
        'beats.':[
            TestResult('lvef', 55, None, ve.STR_GT)
        ],
        'Overall left ventricular systolic function is moderately '            \
        'depressed (LVEF= 30 % with relative preservation of the '             \
        'lateral, inferolateral and inferior walls).':[
            TestResult('lvef', 30, None, ve.STR_EQUAL)
        ]
    }

    compare_results(term_string, test_data, minval, maxval)
    
    # find values using "ejection fraction" as the search term
    term_string = "ejection fraction"
    test_data = {
        'Left Ventricle - Ejection Fraction:  60%  >= 55%':[
            TestResult('ejection fraction', 60, None, ve.STR_EQUAL)
        ],
        'Left Ventricle - Ejection Fraction:  55% (nl >=55%)':[
            TestResult('ejection fraction', 55, None, ve.STR_EQUAL)
        ],
        'Left Ventricle - Ejection Fraction:  50% to 55%  >= 55%':[
            TestResult('ejection fraction', 50, 55, ve.STR_RANGE)
        ],
        '53-year-old male with crack lung, CHF and ejection fraction '         \
        'of 20%, with abdominal pain and fever, who has failed antibiotic '    \
        'monotherapy.':[
            TestResult('ejection fraction', 20, None, ve.STR_EQUAL)
        ],
        'His most recent echocardiogram was in [**2648-8-10**], which showed ' \
        'an ejection fraction of approximately 60 to 70% and a mildly '        \
        'dilated left atrium.':[
            TestResult('ejection fraction', 60, 70, ve.STR_RANGE)
        ],
        'He underwent cardiac catheterization on [**7-30**], which revealed '  \
        'severe aortic stenosis with an aortic valve area of 0.8 '             \
        'centimeters squared, an ejection fraction '                           \
        'of 46%.':[
            TestResult('ejection fraction', 46, None, ve.STR_EQUAL)
        ],
        'The echocardiogram was done on [**2-15**], and per telemetry, '       \
        'showed inferior hypokinesis with an ejection fraction of 50%, and '   \
        'an aortic valve area of 0.7 cm2 with trace mitral '                   \
        'regurgitation.':[
            TestResult('ejection fraction', 50, None, ve.STR_EQUAL)
        ],
        'Echocardiogram in [**3103-2-6**] showed a large left atrium, '        \
        'ejection fraction 60 to 65% with mild symmetric left ventricular '    \
        'hypertrophy, trace aortic regurgitation, mild '                       \
        'mitral regurgitation.':[
            TestResult('ejection fraction', 60, 65, ve.STR_RANGE)
        ],
        "Myocardium:  The patient's ejection fraction at the outside "         \
        'hospital showed a 60% preserved ejection fraction and his ACE '       \
        'inhibitors were titrated up throughout this hospital stay as '        \
        'tolerated.':[
            TestResult('ejection fraction', 60, None, ve.STR_EQUAL)
        ],
        'Overall left ventricular systolic function is probably borderline '   \
        'depressed (not fully assessed; estimated ejection fraction ?50%); '   \
        'intrinsic function may be more depressed given the severity of '      \
        'the regurgitation.':[
            TestResult('ejection fraction', 50, None, ve.STR_EQUAL)
        ]
    }

    compare_results(term_string, test_data, minval, maxval)
    
    # vital signs
    term_string = "t, temp, temperature, p, pulse, hr, bp, r, rr, o2, o2sat, " \
        "spo2, o2 sat, sats, o2sats, pox, sao2"
    test_data = {
        'VS: T 95.6 HR 45 BP 75/30 RR 17 98% RA.':[
            TestResult('t',  95.6, None, ve.STR_EQUAL),
            TestResult('hr', 45,   None, ve.STR_EQUAL),
            TestResult('bp', 75,   None, ve.STR_EQUAL),
            TestResult('rr', 17,   None, ve.STR_EQUAL),
        ],
        'VS T97.3 P84 BP120/56 RR16 O2Sat98 2LNC':[
            TestResult('t',  97.3, None, ve.STR_EQUAL),
            TestResult('p',  84,   None, ve.STR_EQUAL),
            TestResult('bp', 120,  None, ve.STR_EQUAL),
            TestResult('rr', 16,   None, ve.STR_EQUAL),
            TestResult('o2sat', 98, None, ve.STR_EQUAL),
        ],
        'Vitals - T 95.5 BP 132/65 HR 78 RR 20 SpO2 98%/3L':[
            TestResult('t',    95.5, None, ve.STR_EQUAL),
            TestResult('bp',   132,  None, ve.STR_EQUAL),
            TestResult('hr',   78,   None, ve.STR_EQUAL),
            TestResult('rr',   20,   None, ve.STR_EQUAL),
            TestResult('spo2', 98,   None, ve.STR_EQUAL),
        ],
        'VS: T=98 BP= 122/58  HR= 7 RR= 20  O2 sat= 100% 2L NC':[
            # note: 'O2' and 'O2 sat' both match value 100
            #        longest matching term 'o2 sat' wins
            TestResult('t',      98,   None, ve.STR_EQUAL),
            TestResult('bp',     122,  None, ve.STR_EQUAL),
            TestResult('hr',     7,    None, ve.STR_EQUAL),
            TestResult('rr',     20,   None, ve.STR_EQUAL),
            TestResult('o2 sat', 100,  None, ve.STR_EQUAL),
        ],
        'VS:  T-100.6, HR-105, BP-93/46, RR-16, Sats-98% 3L/NC':[
            TestResult('t',    100.6,  None, ve.STR_EQUAL),
            TestResult('hr',   105,    None, ve.STR_EQUAL),
            TestResult('bp',   93,     None, ve.STR_EQUAL),
            TestResult('rr',   16,     None, ve.STR_EQUAL),
            TestResult('sats', 98,     None, ve.STR_EQUAL),
        ],
        'VS: T: 95.9 BP: 154/56 HR: 69 RR: 16 O2sats: 94% 2L NC':[
            TestResult('t',      95.9,   None, ve.STR_EQUAL),
            TestResult('bp',     154,    None, ve.STR_EQUAL),
            TestResult('hr',     69,     None, ve.STR_EQUAL),
            TestResult('rr',     16,     None, ve.STR_EQUAL),
            TestResult('o2sats', 94,     None, ve.STR_EQUAL),
        ],
        'VS - Temp. 98.5F, BP115/65 , HR103 , R16 , 96O2-sat % RA':[
            TestResult('temp',   98.5,   None, ve.STR_EQUAL),
            TestResult('bp',     115,    None, ve.STR_EQUAL),
            TestResult('hr',     103,    None, ve.STR_EQUAL),
            TestResult('r',      16,     None, ve.STR_EQUAL),
        ],
        'PHYSICAL EXAM: O: T: 98.8 BP: 123/60   HR:97    R 16  O2Sats100%':[
            TestResult('t',      98.8,   None, ve.STR_EQUAL),
            TestResult('bp',     123,    None, ve.STR_EQUAL),
            TestResult('hr',     97,     None, ve.STR_EQUAL),
            TestResult('r',      16,     None, ve.STR_EQUAL),
            TestResult('o2sats', 100,    None, ve.STR_EQUAL),
        ],
        'In the ED, initial vs were: T=99.3, P=120, BP=111/57, RR=24, '       \
        'POx=100%.':[
            TestResult('t',      99.3,   None, ve.STR_EQUAL),
            TestResult('p',      120,    None, ve.STR_EQUAL),
            TestResult('bp',     111,    None, ve.STR_EQUAL),
            TestResult('rr',     24,     None, ve.STR_EQUAL),
            TestResult('pox',    100,    None, ve.STR_EQUAL),
        ],
        'Vitals in PACU post-op as follows: BP 120/80 HR 60-80s RR  SaO2 '    \
        '96% 6L NC.':[
            # note: RR value is missing
            # overlap resolution ensures no match to the '2' in 'SaO2'
            TestResult('bp',     120,    None, ve.STR_EQUAL),
            TestResult('hr',     60,     80,   ve.STR_RANGE),
            TestResult('sao2',   96,     None, ve.STR_EQUAL),
        ],
        'T 99.4 P 160 R 56 BP 60/36 mean 44 O2 sat 97% Wt 3025 grams Lt '     \
        '18.5 inches HC 35 cm':[
            TestResult('t',      99.4,   None, ve.STR_EQUAL),
            TestResult('p',      160,    None, ve.STR_EQUAL),
            TestResult('r',      56,     None, ve.STR_EQUAL),
            TestResult('bp',     60,     None, ve.STR_EQUAL),
            TestResult('o2 sat', 97,     None, ve.STR_EQUAL),
        ],
        'Prior to transfer, his vitals were BP 119/53 (105/43 sleeping), '    \
        'HR 103, RR 15, and SpO2 97% on NRB.':[
            TestResult('bp',     119,    None, ve.STR_EQUAL),
            TestResult('hr',     103,    None, ve.STR_EQUAL),
            TestResult('rr',     15,     None, ve.STR_EQUAL),
            TestResult('spo2',   97,     None, ve.STR_EQUAL),
        ],
        'VS: T 98.5 BP 120/50 (110-128/50-56) HR 88 (88-107) ....RR 24 '      \
        '(22-26), SpO2 94% on 4L NC(89-90% on 3L, 92-97% on 4L)':[
            TestResult('t',      98.5,   None,  ve.STR_EQUAL),
            TestResult('bp',     120,    None,  ve.STR_EQUAL),
            TestResult('hr',     88,     None,  ve.STR_EQUAL),
            TestResult('rr',     24,     None,  ve.STR_EQUAL),
            TestResult('spo2',   94,     None,  ve.STR_EQUAL),
        ],
        'In the ED inital vitals were, Temperature 100.8, Pulse: 103, '       \
        'RR: 28, BP: 84/43, O2Sat: 88, O2 Flow: 100 (Non-Rebreather).':[
            # note that 100 matches 'o2'
            TestResult('temperature', 100.8, None, ve.STR_EQUAL),
            TestResult('pulse',       103,   None, ve.STR_EQUAL),
            TestResult('rr',          28,    None, ve.STR_EQUAL),
            TestResult('bp',          84,    None, ve.STR_EQUAL),
            TestResult('o2sat',       88,    None, ve.STR_EQUAL),
            TestResult('o2',          100,   None, ve.STR_EQUAL),
        ]
    }

    compare_results(term_string, test_data, minval, maxval)

    # blood components
    term_string = "wbc, rbc, hgb, hct, mcv, mch, mchc, rdw, plt, plt ct"
    test_data = {
        'CTAB Pertinent Results: BLOOD WBC-7.0# RBC-4.02* Hgb-13.4* '         \
        'Hct-38.4* MCV-96 MCH-33.2* MCHC-34.7 RDW-12.9 Plt Ct-172 '           \
        '02:24AM BLOOD WBC-4.4 RBC-4.21*':[
            TestResult('wbc',    7.0,   None,  ve.STR_EQUAL),
            TestResult('rbc',    4.02,  None,  ve.STR_EQUAL),
            TestResult('hgb',    13.4,  None,  ve.STR_EQUAL),
            TestResult('hct',    38.4,  None,  ve.STR_EQUAL),
            TestResult('mcv',    96,    None,  ve.STR_EQUAL),
            TestResult('mch',    33.2,  None,  ve.STR_EQUAL),
            TestResult('mchc',   34.7,  None,  ve.STR_EQUAL),
            TestResult('rdw',    12.9,  None,  ve.STR_EQUAL),
            TestResult('plt ct', 172,   None,  ve.STR_EQUAL),
            TestResult('wbc',    4.4,   None,  ve.STR_EQUAL),
            TestResult('rbc',    4.21,  None,  ve.STR_EQUAL),
        ],
        'Hgb-13.9* Hct-39.7* MCV-94 MCH-33.0* MCHC-35.0 RDW-12.6 Plt Ct-184 ' \
        'BLOOD WBC-5.6 RBC-4.90 Hgb-16.1 Hct-46.2 MCV-94 MCH-33.0* '          \
        'MCHC-34.9 RDW-12.8 Plt Ct-234':[
            TestResult('hgb',    13.9,  None,  ve.STR_EQUAL),
            TestResult('hct',    39.7,  None,  ve.STR_EQUAL),
            TestResult('mcv',    94,    None,  ve.STR_EQUAL),
            TestResult('mch',    33.0,  None,  ve.STR_EQUAL),
            TestResult('mchc',   35.0,  None,  ve.STR_EQUAL),
            TestResult('rdw',    12.6,  None,  ve.STR_EQUAL),
            TestResult('plt ct', 184,   None,  ve.STR_EQUAL),
            TestResult('wbc',    5.6,   None,  ve.STR_EQUAL),
            TestResult('rbc',    4.90,  None,  ve.STR_EQUAL),
            TestResult('hgb',    16.1,  None,  ve.STR_EQUAL),
            TestResult('hct',    46.2,  None,  ve.STR_EQUAL),
            TestResult('mcv',    94,    None,  ve.STR_EQUAL),
            TestResult('mch',    33.0,  None,  ve.STR_EQUAL),
            TestResult('mchc',   34.9,  None,  ve.STR_EQUAL),
            TestResult('rdw',    12.8,  None,  ve.STR_EQUAL),
            TestResult('plt ct', 234,   None,  ve.STR_EQUAL),
        ]
    }

    compare_results(term_string, test_data, minval, maxval)
