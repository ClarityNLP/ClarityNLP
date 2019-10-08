#!/usr/bin/env python3
"""

Need finder for lab values including vitals

Need finder for prescriptions and dispensing info

"""

import re
import os
import sys
import json

if __name__ == '__main__':
    # put the algorithms/finder folder on the path
    algorithms_path, other = os.path.split(sys.path[0])
    finder_path = os.path.join(algorithms_path, 'finder')
    sys.path.append(finder_path)

try:
    import finder_overlap as overlap
except:
    from algorithms.finder import finder_overlap as overlap


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 1
_MODULE_NAME = 'lab_value_recognizer.py'

# set to True to see debug output
_TRACE = False

# Most of these are from http://ebmcalc.com/Basic.htm, an online medical unit
# conversion tool. Additional unit strings have been added.
_str_units = r'(#|$|%O2|%|10^12/L|10^3/microL|10^9/L|atm|bar|beats/min|bpm|'  +\
             r'breaths/min|centimeters|cm|cents|cmH20|cmHg|cm^2|cm2|days|'    +\
             r'degC|degF|dyn-sec-cm-5|eq|feet|fL|fractionO2|fraction|ftH20|'  +\
             r'ft|g/dL|g/L/|gallon|gm/day|gm/dL|gm/kg/day|gm/kg|gm/L|gm/cm2|' +\
             r'gm/sqcm|gm|hrs|hr|inches|inch|index|inH2O|inHg|in|IU/L|'       +\
             r'kcal/day|K/uL|'                                                +\
             r'kg/m2|kg/m^2|kg/sqm|kg|kilograms|km/hr|km/sec|km/s|knots|kPa|' +\
             r'L/24H|L/day|L/min|L/sec|lb|Liter|litresO2|logit|L|m/sec|mbar|' +\
             r'mcg/dL|mcg/Kg/min/mcg/kg|mcg/mL|mcgm/mL|mEq/L/hr|meq/L|mEq/L|' +\
             r'mEq|meters|'                                                   +\
             r'METs|mg%|mg/day|mg/dL|mg/g|mg/kg|mg/mL|mg|micm|miles/hr|'      +\
             r'miles/sec|miles/s|mph|mins|min|mIU/mL|mL/24H|mL/day|mL/dL|'    +\
             r'mL/hr|mL/L|mL/min|mL/sec|mL/sqm|mL|mm/Hr|mmHg|mmol/L|mm|'      +\
             r'months|mOsm/dl|mOsm/kg|mosm/kg|mo|m|ng/kg/min|ng/mL|nm|'       +\
             r'number|Pascal|percent|pg|ph|points|pounds|psi|rate|ratio|'     +\
             r'score|secs|sec|seq|sqcm/sqm|sqcm|sqm|sqrcm|sqrm|torr|u/L|U/L|' +\
             r'Vol%|weeks|yd|years|yr|'                                       +\
             r'grams/day|grams/hour|grams/dL|grams/kg/day|grams/kg|grams/L'   +\
             r'grams/cm2|grams/sqcm|grams|'                                   +\
             r'insp/min)'

# Heart rhythm: AV Paced
#     premature ventricular contractions (PVCs)
#     paroxysmal supraventricular tachycardia (PSVT)
#     ventricular tachycardia (V-tach)
#     others

"""
grams/hour
mcg/Kg/min
insp/min
inch
K/uL
"""

# separator between header and value
_str_sep = r'[-:=\s/{}]*'

# numeric value, either floating point or integer
_str_num = r'(\d+\.\d+|\.\d+|\d+)'

# Recognize ne or more numeric values, possibly parenthesized or bracketed,
# with optional dashes/slashes. Assumes prior collapse of repeated whitespace.
# ex. 70 (70-72), 42, 33.44 - 22.9, etc
_str_range = r'[\(\[{]?' + _str_sep + _str_num + r'\s?-\s?' +\
    _str_num + _str_sep + r'[\)\]}]?'
_str_slashnum = _str_num + r'(' + _str_sep +\
    r'[/\(]' + _str_sep + _str_num + _str_sep + r'[/\)]' + r')+'
_str_value = r'(' + _str_slashnum + r'|' + _str_range + r'|' + _str_num + r')'
_str_values = _str_value + _str_sep + r'(' + _str_value + _str_sep + r')*'

# word, possibly hyphenated, possibly parenthesized
_str_word = r'\(?[-a-z]+\)?'

# temperature (ignores the exceedingly unlikely units of Kelvin or Rankine);
# also, the abbreviation 'K' for Kelvin could be confused with potassium
_str_temp_units = r'\(?(C|F|deg\.?(rees)?\s?(C|F)|degrees)\)?'
_str_temp_header = r'\b(Temperature|Tcurrent|Tmax|Tcur|Te?mp|Tm|T)\.?'

# heart rate
_str_hr_units  = r'\(?(bpm|beats/m|beats per min\.?(ute)?)\)?'
_str_hr_header = r'\b(Pulse|P|HR|Heart\s?Rate)'

# respiration rate
_str_rr_units = r'\(?((insp\.?|breaths?)\s?min)\)?'
_str_rr_header = r'\b(respiration\s?rate|resp\.?|RR?)'

# height
_str_height_units = r'\(?(inches|inch|feet|meters|in|ft|m)\.?\)?'
_str_height_header = r'\b(Height|Hgt\.?|Ht\.?)'

# weight
_str_weight_units = r'\(?(grams|ounces|pounds|kilograms|gms?|' +\
    r'oz|lbs?|kg|g)\.?\)?'
_str_weight_header = r'\b(Weight|Wgt\.?|Wt\.?)'

# body surface area
_str_bsa_units = r'\(?(meters\s?squared|meters\s?sq|msq|m2)\.?\)?'
_str_bsa_header = r'\bBSA'

# blood pressure
_str_bp_units = r'\(?(mm\s?hg)\)?'
_str_bp_header = r'\b(blood\s?pressure|b\.?\s?p)\.?'

# Oxygen saturation
_str_o2_units = r'\(?(percent|pct\.?|%)\)?'
_str_o2_header = r'\b(SpO2|SaO2|O2Sats|O2\s?sat|O2\s?flow|Sats?|POx|PO|O2)'
_str_o2_device = r'\(?(bipap|non[-\s]?rebreather|nasal\s?cannula|' +\
    r'cannula|NRB|RA|FM|NC)\)?'

# regexes are constructed at init()
_regexes = []


###############################################################################
def enable_debug():

    global TRACE
    _TRACE = True


###############################################################################
def _make_regexes(header_in, units_in):
    """
    """

    regex_list = []
    
    # # header string with optional units
    header = r'(?P<header>' + header_in + _str_sep +\
        r'(' + units_in + _str_sep + r')?' + r')'

    # one or more values with optional units
    elt = _str_values + r'(' + _str_sep + units_in + _str_sep + r')?'
    value_list = elt + r'(' + elt + r')*'
    str_regex = header + value_list
    regex_list.append(re.compile(str_regex, re.IGNORECASE))

    # lists such as "Wgt (current): 119.8 kg (admission): 121 kg"
    elt = _str_word + _str_sep + _str_values + _str_sep + units_in + _str_sep
    value_list = elt + r'(' + elt + r')*'
    str_regex = header + value_list
    regex_list.append(re.compile(str_regex, re.IGNORECASE))

    return regex_list


###############################################################################
def init():

    global _regexes

    regexes = []
    
    _regexes.extend(_make_regexes(_str_temp_header,   _str_temp_units))
    _regexes.extend(_make_regexes(_str_hr_header,     _str_hr_units))
    _regexes.extend(_make_regexes(_str_height_header, _str_height_units))
    _regexes.extend(_make_regexes(_str_weight_header, _str_weight_units))
    _regexes.extend(_make_regexes(_str_bsa_header,    _str_bsa_units))
    _regexes.extend(_make_regexes(_str_bp_header,     _str_bp_units))
    _regexes.extend(_make_regexes(_str_rr_header,     _str_rr_units))
    #_regexes.extend(_make_regexes(_str_o2_header,     _str_o2_units))

    # additional O2 saturation regexs
    o2_header = r'(?P<header>' + _str_o2_header + _str_sep +\
        r'(' + _str_o2_units + _str_sep + r')?' + r')'

    # capture constructs such as O2 sat: 98 2LNC
    str_o2_1 = o2_header + _str_values + _str_sep +\
        r'\d+L\s?' + _str_o2_device + _str_sep
    _regexes.append(re.compile(str_o2_1, re.IGNORECASE))
    
    # capture one or two 'words' following an 'on', such as 'on NRB, on 6L NC'
    str_o2_2 = o2_header + _str_values + _str_sep +\
        r'(' + _str_o2_units + _str_sep + r')?' +\
        r'(on\s)?(\d+L)?' + r'(' + _str_sep + _str_o2_device + _str_sep + r')?'
    _regexes.append(re.compile(str_o2_2, re.IGNORECASE))


###############################################################################
def _cleanup_sentence(sentence):

    # collapse multiple whitespace, to simplify regexes above
    sentence = re.sub(r'\s+', ' ', sentence)

    return sentence


###############################################################################
def run(sentence):
    """
    """

    candidates = []
    for regex_index, regex in enumerate(_regexes):
        iterator = regex.finditer(sentence)
        for match in iterator:
            start = match.start()
            end   = match.end()
            match_text = match.group()

            if _TRACE:
                if 'header' in match.groupdict().keys():
                    header = match.group('header')
                    if header is not None:
                        print('\tMATCH: "{0}"'.format(match_text))
                        print('\t\tHEADER: "{0}"'.format(header))

            candidates.append(overlap.Candidate(start, end, match_text, regex))

    candidates = sorted(candidates, key=lambda x: x.end-x.start, reverse=True)
    pruned_candidates = overlap.remove_overlap(candidates, False)

    # sort by order of occurrence in sentence
    pruned_candidates = sorted(pruned_candidates, key=lambda x: x.start)
    for c in pruned_candidates:
        print('\t\t[{0},{1}): {2}'.format(c.start, c.end, c.match_text))
    print()


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':

    TEST_SENTENCES = [
        # heart rate
        'Vitals: HR 70 (70 - 72) bpm, HR:    70(70   -72)  bpm',
        'Vitals: HR(bpm) 70 (70-72), HR (bpm): 70 (70-72), HR (bpm): 53',
        'Vitals: HR 70, HR:70, HR:70-72, HR:70 70/72',

        # temperature
        'Vitals: T 95.6, T97.3, T: 99, Tmp. 95.5, T=98, T-100.6, Temp. 98.5F',
        'Tmax: 35.8 C (96.4 Tcurrent: 35.7 C (96.2',
        'Tmax: 35.8/96.4, Tcurrent: 35.7/96.2',
        'T: 35.8C/96.4F, Tmax35.7C / 96.2 F',

        # height
        'Height: (in) 74, Height (in): 74, Height 74 (in.), Ht: 74 in.',

        # weight
        'Weight: (lbs) 199, Weight (lb): 199, Wgt (current): 119.8 kg (admission): 121 kg',
        'Wt: 199 kg, Wt 198 lb., Weight: 197',

        # body surface area
        'Vitals: BSA (m2): 2.17 m2, BSA: 2.20 msq.',

        # blood pressure
        'Vitals: BP 75/30, BP120/60, BP (mm Hg): 140/91, BP:115/68',
        'Vitals: BP= 122/58, BP-93/46, BP115/65, BP: 84/43',
        'Vitals: BP: 93/67(73) {72/21(39) - 119/85(91)}',
        'Vitals: BP= 90-109/49-82',

        # respiration rate
        'Vitals: RR 17, R:21, RR= 20, RR-16, R18, RR=24',
        'Vitals: RR 12 (10-23)',

        # O2 saturation
        'Vitals: O2: 97, SpO2 98%/3L, O2 sat= 100% 2L/NC, Sats-98% 3L/NC',
        'Vitals: sats 96% on RA, O2SAts100%, SpO2% 99/bipap, O2 sat 95%RA',
        'Vitals: O2 Sat 85% 3L, POx=100%, POx=93% on 8L FM, SaO2 96% 6L NC',
        'Vitals: O2 sat 97%, SpO2 97% on NRB',
        'Vitals: O2 Flow: 100 (Non-Rebreather), SpO2 92%/RA',
        'Vitals: O2Sat98 2LNC',
    ]

    init()

    for sentence in TEST_SENTENCES:
        sentence = _cleanup_sentence(sentence)
        print('SENTENCE: {0}'.format(sentence))
        run(sentence)
