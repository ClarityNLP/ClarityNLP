#!/usr/bin/python3
"""
    Test program for the 'lab_value_matcher' module.
"""

import re
import os
import sys
import json
import argparse
from collections import namedtuple

if __name__ == '__main__':
    # interactive testing; add nlp dir to path to find logging class
    match = re.search(r'nlp/', sys.path[0])
    if match:
        nlp_dir = sys.path[0][:match.end()]
        sys.path.append(nlp_dir)
    else:
        print('\n*** test_lab_value_matcher.py: nlp dir not found ***\n')
        sys.exit(0)

#from claritynlp_logging import log, ERROR, DEBUG

try:
    import lab_value_matcher as lvm
except:
    from algorithms.finder import lab_value_matcher as lvm

    
_VERSION_MAJOR = 0
_VERSION_MINOR = 4
_MODULE_NAME = 'test_lab_value_matcher.py'

_RESULT_FIELDS = ['match_text']
_Result = namedtuple('_Result', _RESULT_FIELDS)
_Result.__new__.__defaults__ = (None,) * len(_Result._fields)


###############################################################################
def _compare_results(
        computed_values,
        expected_values,
        sentence,
        field_list):

    # check that len(computed) == len(expected)
    if len(computed_values) != len(expected_values):
        print('\tMismatch in computed vs. expected results: ')
        print('\tSentence: {0}'.format(sentence))
        print('\tComputed: ')
        for v in computed_values:
            print('\t\t{0}'.format(v))
        print('\tExpected: ')
        for v in expected_values:
            print('\t\t{0}'.format(v))

        print('NAMEDTUPLE: ')
        for k,v in v._asdict().items():
            print('\t{0} => {1}'.format(k,v))

        return False

    # check fields for each result
    failures = []
    for i, t in enumerate(computed_values):
        # iterate over fields of current result
        for field, value in t._asdict().items():
            # remove trailing whitespace, if any, from computed value
            if str == type(value):
                value = value.strip()
            expected = expected_values[i]._asdict()
            # compare only those fields in _RESULT_FIELDS
            if field in field_list:
                if value != expected[field]:
                    # append as namedtuples
                    failures.append( (t, expected_values[i]) )

    if len(failures) > 0:
        print(sentence)
        for f in failures:
            # extract fields with values not equal to None
            c = [ (k,v) for k,v in f[0]._asdict().items()
                  if v is not None and k in field_list]
            e = [ (k,v) for k,v in f[1]._asdict().items() if v is not None]
            print('\tComputed: {0}'.format(c))
            print('\tExpected: {0}'.format(e))
            
        return False

    return True
    

###############################################################################
def _run_tests(test_data):

    for sentence, expected_values in test_data.items():

        # computed values are finder_overlap.Candidate namedtuples
        # relevant field is 'match_text'
        computed_values = lvm.run(sentence)
        
        ok = _compare_results(
            computed_values,
            expected_values,
            sentence,
            _RESULT_FIELDS)

        if not ok:
            return False
        
    return True


###############################################################################
def run():

    lvm.init()
    
    test_data = {
        'Vitals were SBP 116, HR 75 R=18 L. 80 in.':[
            _Result(match_text='SBP 116'),
            _Result(match_text='HR 75'),
            _Result(match_text='R=18'),
            _Result(match_text='L. 80 in.')
        ],
        'Vitals were HR=120, BP=109/44, RR=29, POx=93% on 8L FM':[
            _Result(match_text='HR=120'),
            _Result(match_text='BP=109/44'),
            _Result(match_text='RR=29'),
            _Result(match_text='POx=93% on 8L FM')
        ],
        'Vitals: T: 96.0  BP: 90/54 P: 88 R: 16 18 O2:88/NRB':[
            _Result(match_text='T: 96.0'),
            _Result(match_text='BP: 90/54'),
            _Result(match_text='P: 88'),
            _Result(match_text='R: 16 18'),
            _Result(match_text='O2:88/NRB')
        ],
        'Vitals: T 98.9 F BP 138/56 P 89 RR 28 SaO2 100% on NRB':[
            _Result(match_text='T 98.9 F'),
            _Result(match_text='BP 138/56'),
            _Result(match_text='P 89'),
            _Result(match_text='RR 28'),
            _Result(match_text='SaO2 100% on NRB')
        ],
        'Vitals were T 98 BP 163/64 HR 73 O2 95% on 55% venti mask':[
            _Result(match_text='T 98'),
            _Result(match_text='BP 163/64'),
            _Result(match_text='HR 73'),
            _Result(match_text='O2 95% on 55% venti mask')
        ],
        'VS: T 95.6 HR 45 BP 75/30 RR 17 98% RA.':[
            _Result(match_text='T 95.6'),
            _Result(match_text='HR 45'),
            _Result(match_text='BP 75/30'),
            _Result(match_text='RR 17'),
            _Result(match_text='98% RA')
        ],
        'VS T97.3 P84 BP120/56 RR16 O2Sat98 2LNC':[
            _Result(match_text='T97.3'),
            _Result(match_text='P84'),
            _Result(match_text='BP120/56'),
            _Result(match_text='RR16'),
            _Result(match_text='O2Sat98 2LNC')
        ],
        'Ht: (in) 74 Wt. (lb): 199 BSA (m2): 2.17 m2 ' +\
        'BP (mm Hg): 140/91 HR (bpm): 53':[
            _Result(match_text='Ht: (in) 74'),
            _Result(match_text='Wt. (lb): 199'),
            _Result(match_text='BSA (m2): 2.17 m2'),
            _Result(match_text='BP (mm Hg): 140/91'),
            _Result(match_text='HR (bpm): 53')
        ],
        'Vitals: T: 99 BP: 115/68 P: 79 R:21 O2: 97':[
            _Result(match_text='T: 99'),
            _Result(match_text='BP: 115/68'),
            _Result(match_text='P: 79'),
            _Result(match_text='R:21'),
            _Result(match_text='O2: 97')
        ],
        'Vitals - T 95.5 BP 132/65 HR 78 RR 20 SpO2 98%/3L':[
            _Result(match_text='T 95.5'),
            _Result(match_text='BP 132/65'),
            _Result(match_text='HR 78'),
            _Result(match_text='RR 20'),
            _Result(match_text='SpO2 98%/3L')
        ],
        'VS: T=98 BP= 122/58  HR= 7 RR= 20  O2 sat= 100% 2L NC':[
            _Result(match_text='T=98'),
            _Result(match_text='BP= 122/58'),
            _Result(match_text='HR= 7'),
            _Result(match_text='RR= 20'),
            _Result(match_text='O2 sat= 100% 2L NC')
        ],
        'Vitals: T: 97.7 P:100 R:16 BP:126/95 SaO2:100 Ra':[
            _Result(match_text='T: 97.7'),
            _Result(match_text='P:100'),
            _Result(match_text='R:16'),
            _Result(match_text='BP:126/95'),
            _Result(match_text='SaO2:100 Ra')
        ],
        'VS:  T-100.6, HR-105, BP-93/46, RR-16, Sats-98% 3L/NC':[
            _Result(match_text='T-100.6'),
            _Result(match_text='HR-105'),
            _Result(match_text='BP-93/46'),
            _Result(match_text='RR-16'),
            _Result(match_text='Sats-98% 3L/NC')
        ],
        'VS - Temp. 98.5F, BP115/65 , HR103 , R16 , 96O2-sat % RA':[
            _Result(match_text='Temp. 98.5F'),
            _Result(match_text='BP115/65'),
            _Result(match_text='HR103'),
            _Result(match_text='R16'),
            _Result(match_text='96O2-sat % RA')
        ],
        'Vitals: Temp 100.2 HR 72 BP 184/56 RR 16 sats 96% on RA':[
            _Result(match_text='Temp 100.2'),
            _Result(match_text='HR 72'),
            _Result(match_text='BP 184/56'),
            _Result(match_text='RR 16'),
            _Result(match_text='sats 96% on RA')
        ],
        'PHYSICAL EXAM: O: T: 98.8 BP: 123/60   HR:97    R 16  O2Sats100%':[
            _Result(match_text='T: 98.8'),
            _Result(match_text='BP: 123/60'),
            _Result(match_text='HR:97'),
            _Result(match_text='R 16'),
            _Result(match_text='O2Sats100%')
        ],
        'VS before transfer were 85 BP 99/34 RR 20 SpO2% 99/bipap 10/5 50%.':[
            _Result(match_text='BP 99/34'),
            _Result(match_text='RR 20'),
            _Result(match_text='SpO2% 99/bipap')
        ],
        'Initial vs were: T 98 P 91 BP 122/63 R 20 O2 sat 95%RA.':[
            _Result(match_text='T 98'),
            _Result(match_text='P 91'),
            _Result(match_text='BP 122/63'),
            _Result(match_text='R 20'),
            _Result(match_text='O2 sat 95%RA')
        ],
        'Initial vitals were HR 106 BP 88/56 RR 20 O2 Sat 85% 3L.':[
            _Result(match_text='HR 106'),
            _Result(match_text='BP 88/56'),
            _Result(match_text='RR 20'),
            _Result(match_text='O2 Sat 85% 3L')
        ],
        'Initial vs were: T=99.3 P=120 BP=111/57 RR=24 POx=100%.':[
            _Result(match_text='T=99.3'),
            _Result(match_text='P=120'),
            _Result(match_text='BP=111/57'),
            _Result(match_text='RR=24'),
            _Result(match_text='POx=100%')
        ],
        'At transfer vitals were HR=120 BP=109/44 RR=29 POx=93% on 8L FM.':[
            _Result(match_text='HR=120'),
            _Result(match_text='BP=109/44'),
            _Result(match_text='RR=29'),
            _Result(match_text='POx=93% on 8L FM')
        ],
        "Vitals as follows: BP 120/80 HR 60-80's RR  SaO2 96% 6L NC.":[
            _Result(match_text='BP 120/80'),
            _Result(match_text="HR 60-80's"),
            _Result(match_text='SaO2 96% 6L NC')
        ],
        'Vital signs were T 97.5 HR 62 BP 168/60 RR 18 95% RA.':[
            _Result(match_text='T 97.5'),
            _Result(match_text='HR 62'),
            _Result(match_text='BP 168/60'),
            _Result(match_text='RR 18'),
            _Result(match_text='95% RA')
        ],
        'T 99.4 P 160 R 56 BP 60/36 mean 44 O2 sat 97% Wt 3025 grams ' +\
        'Lt 18.5 inches HC 35 cm':[
            _Result(match_text='T 99.4'),
            _Result(match_text='P 160'),
            _Result(match_text='R 56'),
            _Result(match_text='BP 60/36'),
            _Result(match_text='O2 sat 97%'),
            _Result(match_text='Wt 3025 grams'),
            _Result(match_text='Lt 18.5 inches'),
            _Result(match_text='HC 35 cm')
        ],
        'Vital signs were T 97.0 BP 85/44 HR 107 RR 28 and SpO2 91% on NRB.':[
            _Result(match_text='T 97.0'),
            _Result(match_text='BP 85/44'),
            _Result(match_text='HR 107'),
            _Result(match_text='RR 28'),
            _Result(match_text='SpO2 91% on NRB'),
        ],
        'Vitals were T 95.6 HR 67 BP 143/79 RR 16 and ' +\
        'O2 sat 92% on room air and 100% on 3 L/min nc':[
            _Result(match_text='T 95.6'),
            _Result(match_text='HR 67'),
            _Result(match_text='BP 143/79'),
            _Result(match_text='RR 16'),
            _Result(match_text='O2 sat 92% on room air')
        ],
        'Vitals were BP 119/53 (105/43 sleeping) HR 103 RR 15 and ' +\
        'SpO2 97% on NRB.':[
            _Result(match_text='BP 119/53 (105/43'),
            _Result(match_text='HR 103'),
            _Result(match_text='RR 15'),
            _Result(match_text='SpO2 97% on NRB'),
        ],
        'Vitals were Temp. 100.8 Pulse: 103 RR: 28 BP: 84/43 ' +\
        'O2Sat: 88 O2 Flow: 100 (Non-Rebreather).':[
            _Result(match_text='Temp. 100.8'),
            _Result(match_text='Pulse: 103'),
            _Result(match_text='RR: 28'),
            _Result(match_text='BP: 84/43'),
            _Result(match_text='O2Sat: 88'),
            _Result(match_text='O2 Flow: 100 (Non-Rebreather)')
        ],
        'Vitals were T 97.1 HR 76 BP 148/80 RR 25 SpO2 92%/RA.':[
            _Result(match_text='T 97.1'),
            _Result(match_text='HR 76'),
            _Result(match_text='BP 148/80'),
            _Result(match_text='RR 25'),
            _Result(match_text='SpO2 92%/RA'),
        ],
        'Tm 96.4, BP= 90-109/49-82, HR= paced at 70, RR= 24, ' +\
        'O2 sat= 96% on 4L':[
            _Result(match_text='Tm 96.4'),
            _Result(match_text='BP= 90-109/49-82'),
            _Result(match_text='HR= paced at 70'),
            _Result(match_text='RR= 24'),
            _Result(match_text='O2 sat= 96% on 4L'),
        ],
        'Vitals were T 97.1 BP 80/70 AR 80 RR 24 O2 sat 70% on 50% flowmask':[
            _Result(match_text='T 97.1'),
            _Result(match_text='BP 80/70'),
            _Result(match_text='RR 24'),
            _Result(match_text='O2 sat 70% on 50% flowmask'),
        ],
        'Vitals: T: 98.9 degrees Farenheit BP: 120/49 mmHg supine ' +\
        'HR 84 bpm RR 13 bpm O2: 100% PS 18/10 FiO2 40%':[
            _Result(match_text='T: 98.9 degrees Farenheit'),
            _Result(match_text='BP: 120/49 mmHg'),
            _Result(match_text='HR 84 bpm'),
            _Result(match_text='RR 13 bpm'),
            _Result(match_text='O2: 100%'),
            _Result(match_text='PS 18/10'),
            _Result(match_text='FiO2 40%')
        ],
        'Vitals T 99.2 (baseline ~96-97), BP 91/50, HR 63, RR 12, ' +\
        'satting 95% on trach mask':[
            _Result(match_text='T 99.2'),
            _Result(match_text='BP 91/50'),
            _Result(match_text='HR 63'),
            _Result(match_text='RR 12'),
            _Result(match_text='satting 95% on trach mask')
        ],
        'Vitals: T 99.2F BP 220/109 HR 69 SR sO2 100% on 100% O2 on vent':[
            _Result(match_text='T 99.2F'),
            _Result(match_text='BP 220/109'),
            _Result(match_text='HR 69'),
            _Result(match_text='sO2 100% on 100% O2 on vent')
        ],
        'Vital signs: Tmax: 38 C (100.4   Tcurrent: 37 C (98.6   '   +\
        'HR: 82 (78 - 103) bpm '                                     +\
        'BP: 121/68(76) {113/57(72) - 137/88(94)} mmHg   RR: 24 '    +\
        '(19 - 29) insp/min   SpO2: 92%   Heart rhythm: SR '         +\
        '(Sinus Rhythm)   Wgt (current): 107 kg (admission): 98 kg ' +\
        'Height: 68 Inch    CVP: 16 (6 - 17)mmHg':[
            _Result(match_text='Tmax: 38 C'),
            _Result(match_text='Tcurrent: 37 C'),
            _Result(match_text='HR: 82 (78 - 103) bpm'),
            _Result(match_text='BP: 121/68(76) {113/57(72) - 137/88(94)} mmHg'),
            _Result(match_text='RR: 24 (19 - 29) insp/min'),
            _Result(match_text='SpO2: 92%'),
            _Result(match_text='Wgt (current): 107 kg (admission): 98 kg'),
            _Result(match_text='Height: 68 Inch'),
            _Result(match_text='CVP: 16 (6 - 17)mmHg')
        ],
        'Vital signs: Tcurrent: 36.8 C (98.2   HR: 75 (75 - 107) bpm ' +\
        'BP: 122/78(89) {122/78(29) - 149/86(100)} mmHg '              +\
        'RR: 21 (20 - 38) insp/min   SpO2: 96% '                       +\
        'Heart rhythm: ST (Sinus Tachycardia)   Height: 72 Inch':[
            _Result(match_text='Tcurrent: 36.8 C'),
            _Result(match_text='HR: 75 (75 - 107) bpm'),
            _Result(match_text='BP: 122/78(89) {122/78(29) - 149/86(100)} mmHg'),
            _Result(match_text='RR: 21 (20 - 38) insp/min'),
            _Result(match_text='SpO2: 96%'),
            _Result(match_text='Height: 72 Inch'),
        ],
        'Ventilator mode: CMV/ASSIST/AutoFlow   Vt (Set): 550 (550 - 550) mL ' +\
        'Vt (Spontaneous): 234 (234 - 234) mL   RR (Set): 16 ' +\
        'RR (Spontaneous): 0   PEEP: 5 cmH2O   FiO2: 70%   RSBI: 140 ' +\
        'PIP: 25 cmH2O   SpO2: 98%   Ve: 14.6 L/min':[
            _Result(match_text='Vt (Set): 550 (550 - 550) mL'),
            _Result(match_text='Vt (Spontaneous): 234 (234 - 234) mL'),
            _Result(match_text='RR (Set): 16'),
            _Result(match_text='RR (Spontaneous): 0'),
            _Result(match_text='PEEP: 5 cmH2O'),
            _Result(match_text='FiO2: 70%'),
            _Result(match_text='RSBI: 140'),
            _Result(match_text='PIP: 25 cmH2O'),
            _Result(match_text='SpO2: 98%'),
            _Result(match_text='Ve: 14.6 L/min')
        ],
        'Vt (Spontaneous): 608 (565 - 793) mL   PS : 15 cmH2O   ' +\
        'RR (Spontaneous): 27   PEEP: 10 cmH2O   FiO2: 50%   ' +\
        'RSBI Deferred: PEEP > 10   PIP: 26 cmH2O   SpO2: 99%   ' +\
        'ABG: 7.41/39/81/21/0   Ve: 17.4 L/min   PaO2 / FiO2: 164':[
            _Result(match_text='Vt (Spontaneous): 608 (565 - 793) mL'),
            _Result(match_text='PS : 15 cmH2O'),
            _Result(match_text='RR (Spontaneous): 27'),
            _Result(match_text='PEEP: 10 cmH2O'),
            _Result(match_text='FiO2: 50%'),
            _Result(match_text='PIP: 26 cmH2O'),
            _Result(match_text='SpO2: 99%'),
            _Result(match_text='ABG: 7.41/39/81/21/0'),
            _Result(match_text='Ve: 17.4 L/min'),
            _Result(match_text='PaO2 / FiO2: 164')
        ],
        'Respiratory: Vt (Set): 600 (600 - 600) mL   Vt (Spontaneous): 743 ' +\
        '(464 - 816) mL  PS : 5 cmH2O   RR (Set): 14   RR (Spontaneous): 19' +\
        ' PEEP: 5 cmH2O   FiO2: 50%   RSBI: 49   PIP: 11 cmH2O   '           +\
        'Plateau: 20 cmH2O   SPO2: 99%   ABG: 7.34/51/109/25/0   '           +\
        'Ve: 10.3 L/min   PaO2 / FiO2: 218':[
            _Result(match_text='Vt (Set): 600 (600 - 600) mL'),
            _Result(match_text='Vt (Spontaneous): 743 (464 - 816) mL'),
            _Result(match_text='PS : 5 cmH2O'),
            _Result(match_text='RR (Set): 14'),
            _Result(match_text='RR (Spontaneous): 19'),
            _Result(match_text='PEEP: 5 cmH2O'),
            _Result(match_text='FiO2: 50%'),
            _Result(match_text='RSBI: 49'),
            _Result(match_text='PIP: 11 cmH2O'),
            _Result(match_text='Plateau: 20 cmH2O'),
            _Result(match_text='SPO2: 99%'),
            _Result(match_text='ABG: 7.34/51/109/25/0'),
            _Result(match_text='Ve: 10.3 L/min'),
            _Result(match_text='PaO2 / FiO2: 218')            
        ],

        # all-text regexes were removed, not a problem for Spacy sentence seg.
        
        # 'Vital signs were a temperature of 97.5, a heart rate of 70, ' +\
        # 'a blood pressure of 193/100, a respiratory rate of 20, and '  +\
        # 'an oxygen saturation of 96% on 2 liters':[
        #     _Result(match_text='temperature of 97.5'),
        #     _Result(match_text='heart rate of 70'),
        #     _Result(match_text='blood pressure of 193/100'),
        #     _Result(match_text='respiratory rate of 20'),
        #     _Result(match_text='oxygen saturation of 96% on 2 liters')
        # ],
        # 'His vitals were a temperature of 98.1.  Heart rate of 76.  Blood ' +\
        # 'pressure 160/80 with intermittent rise to systolic blood pressure ' +\
        # 'of 230 and a respiratory rate of 14. His initial weight was ' +\
        # 'approximately 73 kg':[
        #     _Result(match_text='temperature of 98.1'),
        #     _Result(match_text='Heart rate of 76'),
        #     _Result(match_text='Blood pressure 160/80'),
        #     _Result(match_text='systolic blood pressure of 230'),
        #     _Result(match_text='respiratory rate of 14'),
        #     _Result(match_text='weight was approximately 73 kg')
        # ],
        # 'Physical examination on admission revealed temperature was 96.3, ' +\
        # 'heart rate was 76, blood pressure was 190/80, the respiratory '    +\
        # 'rate was 21,\nand the oxygen saturation was 80% to 92% on a 100% ' +\
        # 'nonrebreather mask':[
        #     _Result(match_text='temperature was 96.3'),
        #     _Result(match_text='heart rate was 76'),
        #     _Result(match_text='blood pressure was 190/80'),
        #     _Result(match_text='respiratory rate was 21'),
        #     _Result(match_text='oxygen saturation was 80% to 92% on a ' \
        #             '100% nonrebreather mask')
        # ],
        # 'Vital signs are heart rate of 107, blood pressure 104/58; '   +\
        # 'breathing at 16; temperature 100 F., orally.  O2 saturation ' +\
        # '98% on room air; weight 115 pounds':[
        #     _Result(match_text='heart rate of 107'),
        #     _Result(match_text='blood pressure 104/58'),
        #     _Result(match_text='breathing at 16'),
        #     _Result(match_text='temperature 100 F'),
        #     _Result(match_text='O2 saturation 98% on room air'),
        #     _Result(match_text='weight 115 pounds')
        # ],
        # lists of numbers, each with units
        'Radiology 117 K/uL 12.6 g/dL 151 mg/dL 3.9 mg/dL 24 mEq/L':[
            _Result(match_text='117 K/uL 12.6 g/dL 151 mg/dL ' +\
                    '3.9 mg/dL 24 mEq/L'),
        ],
        'Radiology 4.4 mEq/L 103 mg/dL 97 mEq/L 133 mEq/L 39.3 % 11.7 K/uL':[
            _Result(match_text='4.4 mEq/L 103 mg/dL 97 mEq/L ' +\
                    '133 mEq/L 39.3 % 11.7 K/uL')
        ],
        # more lab values, ion concentrations
        'Albumin:4.2 g/dL, LDH: 332 IU/L, Ca++:8.0 mg/dL, Mg++:2.1 mg/dL':[
            _Result(match_text='Albumin:4.2 g/dL'),
            _Result(match_text='LDH: 332 IU/L'),
            _Result(match_text='Ca++:8.0 mg/dL'),
            _Result(match_text='Mg++:2.1 mg/dL')
        ],
        # values with embedded commas
        'Total out: 1,621 mL 2,715 mL':[
            _Result(match_text='1,621 mL 2,715 mL')
        ],
        'In: 2,405 mL 2,588 mL PO: 840 mL 100 mL TF: IVF: 1,565 mL 2,488 mL':[
            _Result(match_text='2,405 mL 2,588 mL'),
            _Result(match_text='840 mL 100 mL'),
            _Result(match_text='1,565 mL 2,488 mL')
        ],
        'Balance: -911 mL -76 mL -32 mL':[
            _Result(match_text='-911 mL -76 mL -32 mL')
        ],
        'Performed at WEST STAT LAB Phosphate 3.7 2.7 - 4.5 mg/dL PERFORMED ' \
        'AT WEST STAT LAB Lab Magnesium 1.8 1.6 - 2.6':[
            _Result(match_text='Phosphate 3.7 2.7 - 4.5 mg/dL'),
            _Result(match_text='Magnesium 1.8 1.6 - 2.6')
        ],
        'White Blood Cells 8.2 4.0 - 11.0 K/uL Red Blood Cells 3.95* 4.2 - '  +\
        '5.4 m/uL PERFORMED AT WEST STAT LAB Hemoglobin 12.1 12.0 - 16.0 '    +\
        'g/dL    PERFORMED AT WEST STAT LAB Hematocrit 38.0 36 - 48 %  '      +\
        'PERFORMED AT WEST STAT LAB MCV 96 82 - 98 fL  PERFORMED AT WEST '    +\
        'STAT LAB MCH 30.7 27 - 32 pg':[
            _Result(match_text='Cells 8.2 4.0 - 11.0 K/uL'),
            _Result(match_text='Cells 3.95* 4.2 - 5.4 m/uL'),
            _Result(match_text='Hemoglobin 12.1 12.0 - 16.0 g/dL'),
            _Result(match_text='Hematocrit 38.0 36 - 48 %'),
            _Result(match_text='MCV 96 82 - 98 fL'),
            _Result(match_text='MCH 30.7 27 - 32 pg')
        ],
        'Cr 0.4 0.4 0.4 0.4 0.4 0.4 0.4 0.4 TCO2 43 47 Glucose ':[
            _Result(match_text='0.4 0.4 0.4 0.4 0.4 0.4 0.4 0.4')
        ],
        'CO(LVOT): 3.3 l/min SV(LVOT): 55.2 ml SV(MOD-sp4): 43.0 ml':[
            _Result(match_text='CO(LVOT): 3.3 l/min'),
            _Result(match_text='SV(LVOT): 55.2 ml'),
            _Result(match_text='SV(MOD-sp4): 43.0 ml'),
        ],
        "E/E': 20.2, E/E' lat: 27.4 E/E' med: 12.9 and ...":[
            _Result(match_text="E/E': 20.2"),
            _Result(match_text="E/E' lat: 27.4"),
            _Result(match_text="E/E' med: 12.9"),
        ],
    }

    if not _run_tests(test_data):
        return False

    return True


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Run validation tests on the recognizer modules.'
    )
    
    parser.add_argument('-v', '--version',
                        help='show version and exit',
                        action='store_true')
    parser.add_argument('-d', '--debug',
                        help='log debug information to stdout',
                        action='store_true')

    args = parser.parse_args()

    if 'version' in args and args.version:
        print(_get_version())
        sys.exit(0)

    if 'debug' in args and args.debug:
        lvm.enable_debug()

    assert run()

