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

# namedtuple for expected results
_RESULT_FIELDS = ['term', 'x', 'y', 'condition']
_Result = namedtuple('_Result', _RESULT_FIELDS)


###############################################################################
def _compare_fields(field_name, computed, expected, failure_list):
    
    if computed != expected:
        failure_list.append('\texpected {0}: "{1}", got: "{2}"'.
                            format(field_name, expected, computed))

    return failure_list


###############################################################################
def _compare_results(
        term_string,
        test_data,
        minval,
        maxval,
        enumlist=None,
        denom_only=False):
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
            enumlist=enumlist,
            is_denom_only=denom_only
        )

        num_expected = len(expected_list)

        is_mismatched = False
        if 0 == num_expected and ve.EMPTY_RESULT == json_result:
            # expected not to find anything and actually did not
            continue
        elif num_expected > 0 and ve.EMPTY_RESULT == json_result:
            is_mismatched = True

        if not is_mismatched:
            # load the json result and decode as a ValueResult namedtuple
            result_data = json.loads(json_result)
            value_result = ve.ValueResult(**result_data)

        # check that len(computed) == len(expected)
        if is_mismatched or (value_result.measurementCount != num_expected):
            print('\tMismatch in computed vs. expected results: ')
            print('\tSentence: {0}'.format(sentence))
            print('\tComputed: ')
            for m in value_result.measurementList:
                print('\t\t{0}'.format(m))
            print('\tExpected: ')
            for e in expected_list:
                print('\t\t{0}'.format(e))
            #return
            sys.exit(0)
        
        # check fields
        failures = []
        for i, value in enumerate(value_result.measurementList):

            computed = value['matchingTerm']
            expected = expected_list[i].term
            failures = _compare_fields('matching term', computed, expected, failures)

            computed = value['x']
            expected = expected_list[i].x
            failures = _compare_fields('x', computed, expected, failures)

            computed = value['y']
            expected = expected_list[i].y
            failures = _compare_fields('y', computed, expected, failures)

            computed = value['condition']
            expected = expected_list[i].condition
            failures = _compare_fields('condition', computed, expected, failures)
                
        if len(failures) > 0:
            print(sentence)
            for f in failures:
                print(f)


###############################################################################
if __name__ == '__main__':

    minval = 0
    maxval = 1000000

    # find values using "LVEF" as the search term
    term_string = "lvef"
    test_data = {
        'The LVEF is 40%.':[
            _Result('lvef', 40, None, ve.STR_EQUAL)
        ],
        'Hyperdynamic LVEF >75%':[
            _Result('lvef', 75, None, ve.STR_GT)
        ],
        'Overall normal LVEF (>55%).':[
            _Result('lvef', 55, None, ve.STR_GT)
        ],
        'Overall left ventricular systolic function is normal (LVEF 60%).':[
            _Result('lvef', 60, None, ve.STR_EQUAL)
        ],
        'Overall left ventricular systolic function is normal (LVEF>55%).':[
            _Result('lvef', 55, None, ve.STR_GT)
        ],
        'Overall left ventricular systolic function is low normal (LVEF 50-55%).':[
            _Result('lvef', 50, 55, ve.STR_RANGE)
        ],
        'LVEF was estimated at 55% and ascending aorta measured 5.1 centimeters.':[
            _Result('lvef', 55, None, ve.STR_EQUAL)
        ],
        'Overall left ventricular systolic function is severely '              \
        'depressed (LVEF= 20 %).':[
            _Result('lvef', 20, None, ve.STR_EQUAL)
        ],
        'Overall left ventricular systolic function is severely depressed '    \
        '(LVEF= < 30 %).':[
            _Result('lvef', 30, None, ve.STR_LT)
        ],
        'Overall left ventricular systolic function is severely depressed '    \
        '(LVEF= 15-20 %).':[
            _Result('lvef', 15, 20, ve.STR_RANGE)
        ],
        'Conclusions: There is moderate global left ventricular hypokinesis '  \
        '(LVEF 35-40%).':[
            _Result('lvef', 35, 40, ve.STR_RANGE)
        ],
        'Overall left ventricular systolic function is moderately depressed '  \
        '(LVEF~25-30 %).':[
            _Result('lvef', 25, 30, ve.STR_RANGE)
        ],
        'Normal LV wall thickness, cavity size and regional/global systolic '  \
        'function (LVEF >55%).':[
            _Result('lvef', 55, None, ve.STR_GT)
        ],
        'Overall left ventricular systolic function is mildly depressed '      \
        '(LVEF= 40-45 %) with inferior akinesis.':[
            _Result('lvef', 40, 45, ve.STR_RANGE)
        ],
        'Left ventricular wall thickness, cavity size and regional/global '    \
        'systolic function are normal (LVEF >55%).':[
            _Result('lvef', 55, None, ve.STR_GT)
        ],
        'There is mild symmetric left ventricular hypertrophy with normal '    \
        'cavity size and regional/global systolic function '                   \
        '(LVEF>55%).':[
            _Result('lvef', 55, None, ve.STR_GT)
        ],
        'LEFT VENTRICLE: Overall normal LVEF (>55%). Beat-to-beat '            \
        'variability on LVEF due to irregular rhythm/premature '               \
        'beats.':[
            _Result('lvef', 55, None, ve.STR_GT)
        ],
        'Overall left ventricular systolic function is moderately '            \
        'depressed (LVEF= 30 % with relative preservation of the '             \
        'lateral, inferolateral and inferior walls).':[
            _Result('lvef', 30, None, ve.STR_EQUAL)
        ]
    }

    _compare_results(term_string, test_data, minval, maxval)
    
    # find values using "ejection fraction" as the search term
    term_string = "ejection fraction"
    test_data = {
        'Left Ventricle - Ejection Fraction:  60%  >= 55%':[
            _Result('ejection fraction', 60, None, ve.STR_EQUAL)
        ],
        'Left Ventricle - Ejection Fraction:  55% (nl >=55%)':[
            _Result('ejection fraction', 55, None, ve.STR_EQUAL)
        ],
        'Left Ventricle - Ejection Fraction:  50% to 55%  >= 55%':[
            _Result('ejection fraction', 50, 55, ve.STR_RANGE)
        ],
        '53-year-old male with crack lung, CHF and ejection fraction '         \
        'of 20%, with abdominal pain and fever, who has failed antibiotic '    \
        'monotherapy.':[
            _Result('ejection fraction', 20, None, ve.STR_EQUAL)
        ],
        'His most recent echocardiogram was in [**2648-8-10**], which showed ' \
        'an ejection fraction of approximately 60 to 70% and a mildly '        \
        'dilated left atrium.':[
            _Result('ejection fraction', 60, 70, ve.STR_RANGE)
        ],
        'He underwent cardiac catheterization on [**7-30**], which revealed '  \
        'severe aortic stenosis with an aortic valve area of 0.8 '             \
        'centimeters squared, an ejection fraction '                           \
        'of 46%.':[
            _Result('ejection fraction', 46, None, ve.STR_EQUAL)
        ],
        'The echocardiogram was done on [**2-15**], and per telemetry, '       \
        'showed inferior hypokinesis with an ejection fraction of 50%, and '   \
        'an aortic valve area of 0.7 cm2 with trace mitral '                   \
        'regurgitation.':[
            _Result('ejection fraction', 50, None, ve.STR_EQUAL)
        ],
        'Echocardiogram in [**3103-2-6**] showed a large left atrium, '        \
        'ejection fraction 60 to 65% with mild symmetric left ventricular '    \
        'hypertrophy, trace aortic regurgitation, mild '                       \
        'mitral regurgitation.':[
            _Result('ejection fraction', 60, 65, ve.STR_RANGE)
        ],
        "Myocardium:  The patient's ejection fraction at the outside "         \
        'hospital showed a 60% preserved ejection fraction and his ACE '       \
        'inhibitors were titrated up throughout this hospital stay as '        \
        'tolerated.':[
            _Result('ejection fraction', 60, None, ve.STR_EQUAL)
        ],
        'Overall left ventricular systolic function is probably borderline '   \
        'depressed (not fully assessed; estimated ejection fraction ?50%); '   \
        'intrinsic function may be more depressed given the severity of '      \
        'the regurgitation.':[
            _Result('ejection fraction', 50, None, ve.STR_EQUAL)
        ]
    }

    _compare_results(term_string, test_data, minval, maxval)
    
    # vital signs
    term_string = "t, temp, temperature, p, pulse, hr, bp, r, rr, o2, o2sat, " \
        "spo2, o2 sat, sats, o2sats, pox, sao2"
    test_data = {
        'VS: T 95.6 HR 45 BP 75/30 RR 17 98% RA.':[
            _Result('t',  95.6, None, ve.STR_EQUAL),
            _Result('hr', 45,   None, ve.STR_EQUAL),
            _Result('bp', 75,   None, ve.STR_EQUAL),
            _Result('rr', 17,   None, ve.STR_EQUAL),
        ],
        'VS T97.3 P84 BP120/56 RR16 O2Sat98 2LNC':[
            _Result('t',  97.3, None, ve.STR_EQUAL),
            _Result('p',  84,   None, ve.STR_EQUAL),
            _Result('bp', 120,  None, ve.STR_EQUAL),
            _Result('rr', 16,   None, ve.STR_EQUAL),
            _Result('o2sat', 98, None, ve.STR_EQUAL),
        ],
        'Vitals - T 95.5 BP 132/65 HR 78 RR 20 SpO2 98%/3L':[
            _Result('t',    95.5, None, ve.STR_EQUAL),
            _Result('bp',   132,  None, ve.STR_EQUAL),
            _Result('hr',   78,   None, ve.STR_EQUAL),
            _Result('rr',   20,   None, ve.STR_EQUAL),
            _Result('spo2', 98,   None, ve.STR_EQUAL),
        ],
        'VS: T=98 BP= 122/58  HR= 7 RR= 20  O2 sat= 100% 2L NC':[
            # note: 'O2' and 'O2 sat' both match value 100
            #        longest matching term 'o2 sat' wins
            _Result('t',      98,   None, ve.STR_EQUAL),
            _Result('bp',     122,  None, ve.STR_EQUAL),
            _Result('hr',     7,    None, ve.STR_EQUAL),
            _Result('rr',     20,   None, ve.STR_EQUAL),
            _Result('o2 sat', 100,  None, ve.STR_EQUAL),
        ],
        'VS:  T-100.6, HR-105, BP-93/46, RR-16, Sats-98% 3L/NC':[
            _Result('t',    100.6,  None, ve.STR_EQUAL),
            _Result('hr',   105,    None, ve.STR_EQUAL),
            _Result('bp',   93,     None, ve.STR_EQUAL),
            _Result('rr',   16,     None, ve.STR_EQUAL),
            _Result('sats', 98,     None, ve.STR_EQUAL),
        ],
        'VS: T: 95.9 BP: 154/56 HR: 69 RR: 16 O2sats: 94% 2L NC':[
            _Result('t',      95.9,   None, ve.STR_EQUAL),
            _Result('bp',     154,    None, ve.STR_EQUAL),
            _Result('hr',     69,     None, ve.STR_EQUAL),
            _Result('rr',     16,     None, ve.STR_EQUAL),
            _Result('o2sats', 94,     None, ve.STR_EQUAL),
        ],
        'VS - Temp. 98.5F, BP115/65 , HR103 , R16 , 96O2-sat % RA':[
            _Result('temp',   98.5,   None, ve.STR_EQUAL),
            _Result('bp',     115,    None, ve.STR_EQUAL),
            _Result('hr',     103,    None, ve.STR_EQUAL),
            _Result('r',      16,     None, ve.STR_EQUAL),
        ],
        'PHYSICAL EXAM: O: T: 98.8 BP: 123/60   HR:97    R 16  O2Sats100%':[
            _Result('t',      98.8,   None, ve.STR_EQUAL),
            _Result('bp',     123,    None, ve.STR_EQUAL),
            _Result('hr',     97,     None, ve.STR_EQUAL),
            _Result('r',      16,     None, ve.STR_EQUAL),
            _Result('o2sats', 100,    None, ve.STR_EQUAL),
        ],
        'In the ED, initial vs were: T=99.3, P=120, BP=111/57, RR=24, '       \
        'POx=100%.':[
            _Result('t',      99.3,   None, ve.STR_EQUAL),
            _Result('p',      120,    None, ve.STR_EQUAL),
            _Result('bp',     111,    None, ve.STR_EQUAL),
            _Result('rr',     24,     None, ve.STR_EQUAL),
            _Result('pox',    100,    None, ve.STR_EQUAL),
        ],
        'Vitals in PACU post-op as follows: BP 120/80 HR 60-80s RR  SaO2 '    \
        '96% 6L NC.':[
            # note: RR value is missing
            # overlap resolution ensures no match to the '2' in 'SaO2'
            _Result('bp',     120,    None, ve.STR_EQUAL),
            _Result('hr',     60,     80,   ve.STR_RANGE),
            _Result('sao2',   96,     None, ve.STR_EQUAL),
        ],
        'T 99.4 P 160 R 56 BP 60/36 mean 44 O2 sat 97% Wt 3025 grams Lt '     \
        '18.5 inches HC 35 cm':[
            _Result('t',      99.4,   None, ve.STR_EQUAL),
            _Result('p',      160,    None, ve.STR_EQUAL),
            _Result('r',      56,     None, ve.STR_EQUAL),
            _Result('bp',     60,     None, ve.STR_EQUAL),
            _Result('o2 sat', 97,     None, ve.STR_EQUAL),
        ],
        'Prior to transfer, his vitals were BP 119/53 (105/43 sleeping), '    \
        'HR 103, RR 15, and SpO2 97% on NRB.':[
            _Result('bp',     119,    None, ve.STR_EQUAL),
            _Result('hr',     103,    None, ve.STR_EQUAL),
            _Result('rr',     15,     None, ve.STR_EQUAL),
            _Result('spo2',   97,     None, ve.STR_EQUAL),
        ],
        'VS: T 98.5 BP 120/50 (110-128/50-56) HR 88 (88-107) ....RR 24 '      \
        '(22-26), SpO2 94% on 4L NC(89-90% on 3L, 92-97% on 4L)':[
            _Result('t',      98.5,   None,  ve.STR_EQUAL),
            _Result('bp',     120,    None,  ve.STR_EQUAL),
            _Result('hr',     88,     None,  ve.STR_EQUAL),
            _Result('rr',     24,     None,  ve.STR_EQUAL),
            _Result('spo2',   94,     None,  ve.STR_EQUAL),
        ],
        'In the ED inital vitals were, Temperature 100.8, Pulse: 103, '       \
        'RR: 28, BP: 84/43, O2Sat: 88, O2 Flow: 100 (Non-Rebreather).':[
            # note that 100 matches 'o2'
            _Result('temperature', 100.8, None, ve.STR_EQUAL),
            _Result('pulse',       103,   None, ve.STR_EQUAL),
            _Result('rr',          28,    None, ve.STR_EQUAL),
            _Result('bp',          84,    None, ve.STR_EQUAL),
            _Result('o2sat',       88,    None, ve.STR_EQUAL),
            _Result('o2',          100,   None, ve.STR_EQUAL),
        ]
    }

    _compare_results(term_string, test_data, minval, maxval)

    # blood components
    term_string = "wbc, rbc, hgb, hct, mcv, mch, mchc, rdw, plt, plt ct, "    \
        "rates, temp, tidal v, peep, fio2, po2, pco2, ph, caltco2, "          \
        "base xs, lactate, neuts, lymphs, monos, eos, baso, pt, ptt, "        \
        "inr(pt), glucose, urean, creat, na, k, cl, hco3, angap, totprot, "   \
        "uricacd, igg, iga, igm, c3, c4, blood c4"
    test_data = {
        'CTAB Pertinent Results: BLOOD WBC-7.0# RBC-4.02* Hgb-13.4* '         \
        'Hct-38.4* MCV-96 MCH-33.2* MCHC-34.7 RDW-12.9 Plt Ct-172 '           \
        '02:24AM BLOOD WBC-4.4 RBC-4.21*':[
            _Result('wbc',    7.0,   None,  ve.STR_EQUAL),
            _Result('rbc',    4.02,  None,  ve.STR_EQUAL),
            _Result('hgb',    13.4,  None,  ve.STR_EQUAL),
            _Result('hct',    38.4,  None,  ve.STR_EQUAL),
            _Result('mcv',    96,    None,  ve.STR_EQUAL),
            _Result('mch',    33.2,  None,  ve.STR_EQUAL),
            _Result('mchc',   34.7,  None,  ve.STR_EQUAL),
            _Result('rdw',    12.9,  None,  ve.STR_EQUAL),
            _Result('plt ct', 172,   None,  ve.STR_EQUAL),
            _Result('wbc',    4.4,   None,  ve.STR_EQUAL),
            _Result('rbc',    4.21,  None,  ve.STR_EQUAL),
        ],
        'Hgb-13.9* Hct-39.7* MCV-94 MCH-33.0* MCHC-35.0 RDW-12.6 Plt Ct-184 ' \
        'BLOOD WBC-5.6 RBC-4.90 Hgb-16.1 Hct-46.2 MCV-94 MCH-33.0* '          \
        'MCHC-34.9 RDW-12.8 Plt Ct-234':[
            _Result('hgb',    13.9,  None,  ve.STR_EQUAL),
            _Result('hct',    39.7,  None,  ve.STR_EQUAL),
            _Result('mcv',    94,    None,  ve.STR_EQUAL),
            _Result('mch',    33.0,  None,  ve.STR_EQUAL),
            _Result('mchc',   35.0,  None,  ve.STR_EQUAL),
            _Result('rdw',    12.6,  None,  ve.STR_EQUAL),
            _Result('plt ct', 184,   None,  ve.STR_EQUAL),
            _Result('wbc',    5.6,   None,  ve.STR_EQUAL),
            _Result('rbc',    4.90,  None,  ve.STR_EQUAL),
            _Result('hgb',    16.1,  None,  ve.STR_EQUAL),
            _Result('hct',    46.2,  None,  ve.STR_EQUAL),
            _Result('mcv',    94,    None,  ve.STR_EQUAL),
            _Result('mch',    33.0,  None,  ve.STR_EQUAL),
            _Result('mchc',   34.9,  None,  ve.STR_EQUAL),
            _Result('rdw',    12.8,  None,  ve.STR_EQUAL),
            _Result('plt ct', 234,   None,  ve.STR_EQUAL),
        ],
        'BLOOD Type-ART Temp-36.6 Rates-16/ Tidal V-600 PEEP-5 FiO2-60 '      \
        'pO2-178* pCO2-35 pH-7.42 calTCO2-23 Base XS-0 Intubat-INTUBATED '    \
        'Vent-CONTROLLED BLOOD Lactate-1.0 BLOOD Lactate-1.6':[
            # note: the 16/ is not confused with a fraction
            _Result('temp',    36.6,  None,  ve.STR_EQUAL),
            _Result('rates',   16,    None,  ve.STR_EQUAL),
            _Result('tidal v', 600,   None,  ve.STR_EQUAL),
            _Result('peep',    5,     None,  ve.STR_EQUAL),
            _Result('fio2',    60,    None,  ve.STR_EQUAL),
            _Result('po2',     178,   None,  ve.STR_EQUAL),
            _Result('pco2',    35,    None,  ve.STR_EQUAL),
            _Result('ph',      7.42,  None,  ve.STR_EQUAL),
            _Result('caltco2', 23,    None,  ve.STR_EQUAL),
            _Result('base xs', 0,     None,  ve.STR_EQUAL),
            _Result('lactate', 1.0,   None,  ve.STR_EQUAL),
            _Result('lactate', 1.6,   None,  ve.STR_EQUAL),
        ],
        'BLOOD Neuts-59.7 Lymphs-33.5 Monos-4.9 Eos-1.3 Baso-0.6 BLOOD '      \
        'PT-10.8 PTT-32.6 INR(PT)-1.0 BLOOD Plt Ct-234 BLOOD Glucose-182* '   \
        'UreaN-14 Creat-0.8 Na-134 K-4.0 Cl-101 HCO3-25 AnGap-12':[
            # overlap resolution prevents 'pt)-1.0' from matching term 'pt'
            _Result('neuts',   59.7,  None,  ve.STR_EQUAL),
            _Result('lymphs',  33.5,  None,  ve.STR_EQUAL),
            _Result('monos',   4.9,   None,  ve.STR_EQUAL),
            _Result('eos',     1.3,   None,  ve.STR_EQUAL),
            _Result('baso',    0.6,   None,  ve.STR_EQUAL),
            _Result('pt',      10.8,  None,  ve.STR_EQUAL),
            _Result('ptt',     32.6,  None,  ve.STR_EQUAL),
            _Result('inr(pt)', 1.0,   None,  ve.STR_EQUAL),
            _Result('plt ct',  234,   None,  ve.STR_EQUAL),
            _Result('glucose', 182,   None,  ve.STR_EQUAL),
            _Result('urean',   14,    None,  ve.STR_EQUAL),
            _Result('creat',   0.8,   None,  ve.STR_EQUAL),
            _Result('na',      134,   None,  ve.STR_EQUAL),
            _Result('k',       4.0,   None,  ve.STR_EQUAL),
            _Result('cl',      101,   None,  ve.STR_EQUAL),
            _Result('hco3',    25,    None,  ve.STR_EQUAL),
            _Result('angap',   12,    None,  ve.STR_EQUAL),
        ],
        'BLOOD Glucose-119* UreaN-21* Creat-0.9 Na-138 K-3.8 Cl-100 HCO3-25 ' \
        'AnGap-17 BLOOD TotProt-6.2* UricAcd-2.8* BLOOD PEP-AWAITING '        \
        'F IgG-1040 IgA-347 IgM-87 IFE-PND BLOOD C3-144 C4-37 BLOOD C4-45*':[
            _Result('glucose',  119,   None,  ve.STR_EQUAL),
            _Result('urean',    21,    None,  ve.STR_EQUAL),
            _Result('creat',    0.9,   None,  ve.STR_EQUAL),
            _Result('na',       138,   None,  ve.STR_EQUAL),
            _Result('k',        3.8,   None,  ve.STR_EQUAL),
            _Result('cl',       100,   None,  ve.STR_EQUAL),
            _Result('hco3',     25,    None,  ve.STR_EQUAL),
            _Result('angap',    17,    None,  ve.STR_EQUAL),
            _Result('totprot',  6.2,   None,  ve.STR_EQUAL),
            _Result('uricacd',  2.8,   None,  ve.STR_EQUAL),
            _Result('igg',      1040,  None,  ve.STR_EQUAL),
            _Result('iga',      347,   None,  ve.STR_EQUAL),
            _Result('igm',      87,    None,  ve.STR_EQUAL),
            _Result('c3',       144,   None,  ve.STR_EQUAL),
            _Result('c4',       37,    None,  ve.STR_EQUAL),
            _Result('blood c4', 45,    None,  ve.STR_EQUAL),
        ]
    }

    _compare_results(term_string, test_data, minval, maxval)

    # approximations
    term_string = "rr"
    the_result = _Result('rr', 22, None, ve.STR_APPROX)
    test_data = {
        'RR approx 22'          :[the_result],
        'RR approx. 22'         :[the_result],
        'RR approximately 22'   :[the_result],
        'RR is approx. 22'      :[the_result],
        'RR is approximately 22':[the_result],
        'RR near 22'            :[the_result],
        'RR is about 22'        :[the_result],
        'RR ~ 22'               :[the_result],
        'RR~=22'                :[the_result]
    }

    _compare_results(term_string, test_data, minval, maxval)

    # >=, <=
    term_string = "rr"
    test_data = {
        'RR >= 24':[_Result('rr', 24, None, ve.STR_GTE)],
        'RR <= 42':[_Result('rr', 42, None, ve.STR_LTE)],
        'her RR was greater than 24':[_Result('rr', 24, None, ve.STR_GT)],
        'his RR was less than 42':[_Result('rr', 42, None, ve.STR_LT)],
        'his RR was up to 50':[_Result('rr', 50, None, ve.STR_LT)],
        'RR above 45':[_Result('rr', 45, None, ve.STR_GT)],
    }

    _compare_results(term_string, test_data, minval, maxval)

    # ranges
    term_string = "rr, fvc"
    the_result = _Result('rr', 22, 42, ve.STR_RANGE)
    test_data = {
        'RR 22-42':[the_result],
        'RR22-42':[the_result],
        'RR 22 - 42':[the_result],
        'RR(22-42)':[the_result],
        'RR (22 to 42)':[the_result],
        'RR (22 - 42)':[the_result],
        'RR22to42':[the_result],
        'RR 22to42':[the_result],
        'RR 22 to 42':[the_result],
        'RR from 22 to 42':[the_result],
        'RR range: 22-42':[the_result],
        'RR= 22-42':[the_result],
        'RR=22-42':[the_result],
        'RR= 22 -42':[the_result],
        'RR = 22 - 42':[the_result],
        'RR = 22 to 42':[the_result],
        'RR=22to42':[the_result],
        'RR is 22-42':[the_result],
        'RR ~ 22-42':[the_result],
        'RR approx. 22-42':[the_result],
        'RR is approximately 22 - 42':[the_result],
        'RR is ~22-42':[the_result],
        'RR varies from 22-42':[the_result],
        'RR varied from 22 to 42':[the_result],
        'RR includes all values in the range 22 to 42':[the_result],
        'RR values were 22-42':[the_result],
        'RR: 22-42':[the_result],
        'RR 22-42':[the_result],
        'RR=22-42':[the_result],
        'RR ~= 22-42':[the_result],
        'RR ~= 22 to 42':[the_result],
        'RR is approx. = 22-42':[the_result],
        'RR- 22-42':[the_result],
        'RR= 22    -42':[the_result],
        'RR between 22 and 42':[the_result],
        'RR ranging from 22 to 42':[the_result],
        'FVC value for this patient is 500ml to 600ml.':[
            _Result('fvc', 500, 600, ve.STR_RANGE),
        ]
    }
    
    _compare_results(term_string, test_data, minval, maxval)
    
    # blood pressure - check numerators (the default)
    term_string = "bp"
    test_data = {
        'BP < 120/80':[_Result('bp', 120, None, ve.STR_LT)],
        'BP = 110/70':[_Result('bp', 110, None, ve.STR_EQUAL)],
        'BP >= 100/70':[_Result('bp', 100, None, ve.STR_GTE)],
        'BP <= 110/70':[_Result('bp', 110, None, ve.STR_LTE)],
        'BP lt. or eq 112/70':[_Result('bp', 112, None, ve.STR_LTE)],
        'her BP was less than 120/80':[_Result('bp', 120, None, ve.STR_LT)],
        'his BP was gt 110 /70':[_Result('bp', 110, None, ve.STR_GT)],
        'BP lt. 110/70':[_Result('bp', 110, None, ve.STR_LT)],
        'BP 110/70 to 120/80':[_Result('bp', 110, 120, ve.STR_FRACTION_RANGE)],
        'BP was between 100/60 and 120/80':[_Result('bp', 100, 120, ve.STR_FRACTION_RANGE)],
        'BP range: 105/75 - 120/70':[_Result('bp', 105, 120, ve.STR_FRACTION_RANGE)],
        # embedded dates and measurements
        'Her BP on 3/27 measured 110/70.':[
            _Result('bp', 110, None, ve.STR_EQUAL)
        ],
        'Her BP at 8 AM on 3/27 measured 110/70':[
            _Result('bp', 110, None, ve.STR_EQUAL)
        ],
        'Her BP at 3:47P.M on March 27 measured 110/70':[
            _Result('bp', 110, None, ve.STR_EQUAL)
        ],
        'Her BP at 05:14:28 AM on March 27, 2005 measured 110/70':[
            _Result('bp', 110, None, ve.STR_EQUAL)
        ],
        'Her BP on 3/27 measured 110/70 and her BP on 4/01 measured 115/80.':[
            _Result('bp', 110, None, ve.STR_EQUAL),
            _Result('bp', 115, None, ve.STR_EQUAL)
        ],
        'Her BP on 3/27 from her 12 cm. x 9 cm x 6 cm heart was 110/70.':[
            _Result('bp', 110, None, ve.STR_EQUAL)
        ],
        "her BP was near the 120/80's":[
            _Result('bp', 120, None, ve.STR_APPROX)
        ]
    }

    _compare_results(term_string, test_data, minval, maxval)

    # blood pressure - check denominators
    term_string = "bp"
    test_data = {
        'BP < 120/80':[_Result('bp', 80, None, ve.STR_LT)],
        'BP = 110/70':[_Result('bp', 70, None, ve.STR_EQUAL)],
        'BP >= 100/70':[_Result('bp', 70, None, ve.STR_GTE)],
        'BP <= 110/70':[_Result('bp', 70, None, ve.STR_LTE)],
        'BP lt. or eq 112/70':[_Result('bp', 70, None, ve.STR_LTE)],
        'her BP was less than 120/80':[_Result('bp', 80, None, ve.STR_LT)],
        'his BP was gt 110 /70':[_Result('bp', 70, None, ve.STR_GT)],
        'BP lt. 110/70':[_Result('bp', 70, None, ve.STR_LT)],
        'BP 110/70 to 120/80':[_Result('bp', 70, 80, ve.STR_FRACTION_RANGE)],
        'BP was between 100/60 and 120/80':[_Result('bp', 60, 80, ve.STR_FRACTION_RANGE)],
        'BP range: 105/75 - 120/70':[_Result('bp', 75, 70, ve.STR_FRACTION_RANGE)],
        # embedded dates and measurements
        'Her BP on 3/27 measured 110/70.':[_Result('bp', 70, None, ve.STR_EQUAL)],
        'Her BP on 3/27 measured 110/70 and her BP on 4/01 measured 115/80.':[
            _Result('bp', 70, None, ve.STR_EQUAL),
            _Result('bp', 80, None, ve.STR_EQUAL)
        ],
        'Her BP at 8 AM on 3/27 measured 110/70':[
            _Result('bp', 70, None, ve.STR_EQUAL)
        ],
        'Her BP at 3:47P.M on March 27 measured 110/70':[
            _Result('bp', 70, None, ve.STR_EQUAL)
        ],
        'Her BP at 05:14:28 AM on March 27, 2005 measured 110/70':[
            _Result('bp', 70, None, ve.STR_EQUAL)
        ],
        'Her BP on 3/27 from her 12cm x 9cm. x 6   cm heart was 110/70.':[
            _Result('bp', 70, None, ve.STR_EQUAL)
        ],
        "her BP was near the 120/80's":[
            _Result('bp', 80, None, ve.STR_APPROX)
        ]
    }

    _compare_results(term_string, test_data, minval, maxval, denom_only=True)
    
    # numbers with suffixes and commas
    term_string = "hr, platelets"
    test_data = {
        "her HR varied from the 80s to the 90's":[
            _Result('hr', 80, 90, ve.STR_RANGE)
        ],
        'her HR was in the 90s':[_Result('hr', 90, None, ve.STR_EQUAL)],
        'platelets were 20k':[_Result('platelets', 20000, None, ve.STR_EQUAL)],
        'platelets in the range 20k-40k':[
            _Result('platelets', 20000, 40000, ve.STR_RANGE)
        ],
        'platelets from 25k - 38k':[
            _Result('platelets', 25000, 38000, ve.STR_RANGE)
        ],
        'platelets between 25k and 38k':[
            _Result('platelets', 25000, 38000, ve.STR_RANGE)
        ],
        'platelets between 25,000 and 38,000':[
            _Result('platelets', 25000, 38000, ve.STR_RANGE)
        ],
    }

    _compare_results(term_string, test_data, minval, maxval)

    # times, durations, multiple overlap
    term_string = "platelets, platelet, platelet count"
    test_data = {
        'platelets 2 hrs after transfusion 156':[
            _Result('platelets', 156, None, ve.STR_EQUAL)
        ],
        'platelets q. 2- 3 hrs measured 200':[
            _Result('platelets', 200, None, ve.STR_EQUAL)
        ],
        'platelets for the previous 3-4 months were 220':[
            _Result('platelets', 220, None, ve.STR_EQUAL)
        ],
        'platelets within the prev. 1 hour measured 223':[
            _Result('platelets', 223, None, ve.STR_EQUAL)
        ],
        'platelets for the past 2 months were 235,000':[
            _Result('platelets', 235000, None, ve.STR_EQUAL)
        ],
        'platelet values for two weeks have been above 215K':[
            _Result('platelet', 215000, None, ve.STR_GT)
        ],
        'received one bag of platelets due to platelet count of 71k':[
            _Result('platelet count', 71000, None, ve.STR_EQUAL)
        ],
        'Pt also has profound thrombocytopenia, with platelet ' \
        'count at 1600 of 5000 -> ?':[
            _Result('platelet count', 5000, None, ve.STR_EQUAL)
        ],
        'Received platelets yesterday for platelet count of 28; ' \
        'platelets 2 hrs after transfusion 156, '                 \
        '12 hrs after transfusion 132.':[
            _Result('platelet count', 28, None, ve.STR_EQUAL),
            _Result('platelets', 156, None, ve.STR_EQUAL)
        ],
        'One bag of platelets hung at 0610 and she will need a repeat '
        'platelet count in one hour after transfusion completed.':[],
        'post transfusion platelet count due around 0730.':[],
        'Will follow platelets soon after transfusion and again 6-12 ' \
        'hours later peding initial post-transfusion result.':[],

        'Platelet count four hours after transfusion was 139,000 and '   \
        'approximately ten hours after transfusion, the platelet count ' \
        'remained stable at 138, Maternal platelet count as reported '   \
        'earlier was normal.':[
            _Result('platelet count', 139000, None, ve.STR_EQUAL),
            _Result('platelet count', 138,    None, ve.STR_EQUAL)
        ]
    }

    _compare_results(term_string, test_data, minval, maxval)

    # others
    term_string = 'platelet count, platelets'
    test_data = {
        # range with no units on first number
        'Will consider transfusion for platelet count < 30-50k.':[
            _Result('platelet count', 30000, 50000, ve.STR_RANGE)
        ],
        # range with no units on first number
        'Will consider IVIg for platelet count 30-80k.':[
            _Result('platelet count', 30000, 80000, ve.STR_RANGE)
        ],
        # from a to b with missing b
        'platelet count up from 5 to Pt hemodynamicaly stable Plan':[],

        # do not confuse frequency with value
        'Given platelets x2.':[],

        # do not confuse 2nd with value
        'Platelet count after 2nd unit up to Neurosurg resident ':[],
    }

    _compare_results(term_string, test_data, minval, maxval)
    
    # enumlist: search for keywords and keep results containing enumlist terms
    term_string = 'positive, +, hbsab'
    enumlist = 'titer, titers'
    test_data = {
        'POSITIVE Titer-1:80':[
            _Result('positive', 'titer', None, ve.STR_EQUAL)
        ],
        '+Titer-1:80':[
            _Result('+', 'titer', None, ve.STR_EQUAL)
        ],
        'HBSAb titers remained greater than 450.':[
            _Result('hbsab', 'titers', None, ve.STR_EQUAL)
        ],
    }

    _compare_results(term_string, test_data, minval, maxval, enumlist)

    term_string = 'HCV, HBV, IgG'
    enumlist = 'negative, positive, -, +'
    test_data = {
        'She was HCV negative, HBV negative, IgM Titer-1:80, IgG +':[
            _Result('hcv', 'negative', None, ve.STR_EQUAL),
            _Result('hbv', 'negative', None, ve.STR_EQUAL),
            _Result('igg', '+',        None, ve.STR_EQUAL)
        ]
    }

    # term_string = 'gram, gram positive, gram negative, positive, negative'
    # enumlist = 'cocci, rod(s), rods, bacteremia'
    # test_data = {
    #     'GRAM POSITIVE COCCI': [
    #         _Result('gram positive', 'cocci', None, ve.STR_EQUAL)
    #     ],
    #     'GRAM NEGATIVE ROD(S).':[
    #         _Result('gram negative', 'rod(s)', None, ve.STR_EQUAL)
    #     ],
    #     'NO ENTERIC GRAM NEGATIVE RODS FOUND.':[
    #         _Result('gram negative', 'rods', None, ve.STR_EQUAL)
    #     ],
    #     'Patient presents with sudden onset of fever, chills, and '
    #     'hypotension with 3/4 bottles positive gram negative bacteremia.':[
    #         _Result('gram negative', 'bacteremia', None, ve.STR_EQUAL)
    #     ],
    #     'She completed a 7 day course of Vancomycin and Zosyn for the BAL ' \
    #     'which grew gram positive and negative rods.':[
    #         _Result('gram positive', 'rods', None, ve.STR_EQUAL),
    #         _Result('negative', 'rods', None, ve.STR_EQUAL)
    #     ]
    # }

    # _compare_results(term_string, test_data, minval, maxval, enumlist)
    
    # # search for keywords and return text 'values' from enumlist
    # term_string = 'positive, +, negative'
    # enumlist = 'titer, hav, igm, igg'
    # test_data = {
    #     'POSITIVE Titer-1:80':[
    #         _Result('positive', 'titer', None, ve.STR_EQUAL)],
    #     '+Titer-1:80':[_Result('+', 'titer', None, ve.STR_EQUAL)],
    #     #'She was HCV negative, HBV negative, had + HAV IgG, negative IgM.':[
    #     #    _Result('+', 'hav igg', None, ve.STR_EQUAL),
    #     #    _Result('negative', 'igm', None, ve.STR_EQUAL)
    #     #],
    # }

    # _compare_results(term_string, test_data, minval, maxval, enumlist)

    # # hypotheticals
    # term_string = 'temp'
    # test_data = {
    #     'If the FVC is 1500 ml, you should set the temp to 100.':[],
    #     'you should set the temp to 100':[],
    #     #'do you know if the temp is 100?':[],
    # }

    # _compare_results(term_string, test_data, minval, maxval)

    
    # TODO: accept s endings only if NOT a separate search term!!
