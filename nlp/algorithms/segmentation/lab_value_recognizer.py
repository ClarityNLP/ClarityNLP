#!/usr/bin/env python3
"""

Need finder for lab values including vitals

Need finder for prescriptions and dispensing info

"""

import re
import os
import sys
import json
import argparse

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

# word, possibly hyphenated, parenthesized, or abbreviated
_str_word = r'\(?[-a-z.]+\)?'

# numeric value, either floating point or integer, possibly suffixed with
# an 's' or an apostrophe-s (the 's' is for constructs such as 70s, 80s, etc.)
_str_num = r'(\d+\.\d+|\.\d+|\d+)\'?s?'

# Recognize one or more numeric values, possibly parenthesized or bracketed,
# with optional dashes/slashes. Assumes prior collapse of repeated whitespace.
_str_range = r'[\(\[{]?' + _str_sep + _str_num + r'\s?-\s?' +\
    _str_num + _str_sep + r'[\)\]}]?'
_str_slashnum = _str_num + _str_sep + r'(' +\
    r'[/\(]' + _str_sep + _str_num + _str_sep + r'[/\)]' + r')+'
_str_value = r'(' + _str_slashnum + r'|' + _str_range + r'|' + _str_num + r')'
_str_values = _str_value + _str_sep + r'(' + _str_value + _str_sep + r')*'

# temperature (ignores the exceedingly unlikely units of Kelvin or Rankine);
# also, the abbreviation 'K' for Kelvin could be confused with potassium
_str_temp_units = r'\(?(C|F|deg\.?(rees)?\s?(C|F)|degrees)\)?'
_str_temp_header = r'\b(Temperature|Tcurrent|Tmax|Tcur|Te?mp|Tm|T)\.?'

# heart rate
_str_hr_units  = r'\(?(bpm|beats/m(in\.?)?|beats per min\.?(ute)?)\)?'
_str_hr_header = r'\b(Pulse|P|HR|Heart\s?Rate)'

# respiration rate
_str_rr_units = r'\(?((insp\.?|breaths?)[\s/]*min)\.?\)?'
_str_rr_header = r'\b(respiration\s?rate|resp\.?|RR?)'

# height
_str_height_units = r'\(?(inches|inch|feet|meters|in|ft|m)\.?\)?'
_str_height_header = r'\b(Height|Hgt\.?|Ht\.?)'

# weight
_str_weight_units = r'\(?(grams|ounces|pounds|kilograms|gms?|' +\
    r'oz|lbs?|kg|g)\.?\)?'
_str_weight_header = r'\b(Weight|Wgt\.?|Wt\.?|w\.?)'

# length
_str_length_units = r'\(?(centimeters?|decimeters?|millimeters?|meters?|' +\
    r'inch(es)?|feet|foot|cm|dm|mm|in|ft|m)\.?\)?'
_str_length_header = r'\b(Length|Len|Lt|L\.?)'

# head circumference (infants)
_str_hc_units = _str_length_units
_str_hc_header = r'\b(HC)'

# body surface area
_str_bsa_units = r'\(?(meters\s?squared|meters\s?sq|msq|m2)\.?\)?'
_str_bsa_header = r'\bBSA'

# blood pressure
_str_bp_units = r'\(?(mm\s?hg)\)?'
_str_bp_header = r'\b(blood\s?pressure|b\.?\s?p)\.?'

# Oxygen saturation
_str_o2_units = r'\(?(percent|pct\.?|%)\)?'
# no leading r'\b', on purpose, for O2 l_to_r regexes below
_str_o2_header = r'(SpO2|SaO2|O2[-\s]sat\.?s?|O2Sats?|O2\s?flow|' +\
    r'Sat\.?s?|POx|PO|O2)'
_str_o2_device = r'\(?(bipap|non[-\s]?rebreather|nasal\s?cannula|'  +\
    r'cannula|NRB|RA|FM|NC)\)?'


_all_regex_lists = []


###############################################################################
def enable_debug():

    global _TRACE
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

    # global _regexes_r_to_l
    # global _regexes_l_to_r

    # _regexes_r_to_l = []
    # _regexes_l_to_r = []
    
    # _regexes_r_to_l.extend(_make_regexes(_str_temp_header,   _str_temp_units))
    # _regexes_r_to_l.extend(_make_regexes(_str_hr_header,     _str_hr_units))
    # _regexes_r_to_l.extend(_make_regexes(_str_height_header, _str_height_units))
    # _regexes_r_to_l.extend(_make_regexes(_str_weight_header, _str_weight_units))
    # _regexes_r_to_l.extend(_make_regexes(_str_length_header, _str_length_units))
    # _regexes_r_to_l.extend(_make_regexes(_str_hc_header,     _str_hc_units))
    # _regexes_r_to_l.extend(_make_regexes(_str_bsa_header,    _str_bsa_units))
    # _regexes_r_to_l.extend(_make_regexes(_str_bp_header,     _str_bp_units))
    # _regexes_r_to_l.extend(_make_regexes(_str_rr_header,     _str_rr_units))
    # # O2 regexes constructed specially below
    
    # # additional O2 saturation regexs
    # o2_header = r'(?P<header>\b' + _str_o2_header + _str_sep +\
    #     r'(' + _str_o2_units + _str_sep + r')?' + r')'

    # # capture constructs such as O2 sat: 98 2LNC
    # str_o2_1 = r'\b' + o2_header + _str_values + _str_sep +\
    #     r'\d+L\s?' + _str_o2_device + _str_sep
    # _regexes_r_to_l.append(re.compile(str_o2_1, re.IGNORECASE))
    
    # # capture one or two 'words' following an 'on', such as 'on NRB, on 6L NC'
    # str_o2_2 = r'\b' + o2_header + _str_values + _str_sep +\
    #     r'(' + _str_o2_units + _str_sep + r')?' +\
    #     r'(on\s)?(\d+L)?' + r'(' + _str_sep + _str_o2_device + _str_sep + r')?'
    # _regexes_r_to_l.append(re.compile(str_o2_2, re.IGNORECASE))

    # # capture constructs such as '98% RA, sats 91% on NRB, 96O2-sat on RA' [L to R]
    # str_o2_3 = r'(' + _str_o2_header + _str_sep + r')?'  +\
    #     r'(' + _str_o2_units  + _str_sep + r')?'         +\
    #     r'(?<!O)\d+' + _str_sep                          +\
    #     r'(' + _str_o2_units  + _str_sep + r')?'         +\
    #     r'(' + _str_o2_header + _str_sep + r')?'         +\
    #     r'(' + _str_o2_units  + _str_sep + r')?'         +\
    #     r'(' + r'on'          + _str_sep + r')?'         +\
    #     _str_o2_device + _str_sep
    # _regexes_l_to_r.append(re.compile(str_o2_3, re.IGNORECASE))

    global _all_regex_lists
    _all_regex_lists = []

    
    _all_regex_lists.append(_make_regexes(_str_temp_header,   _str_temp_units))
    _all_regex_lists.append(_make_regexes(_str_hr_header,     _str_hr_units))
    _all_regex_lists.append(_make_regexes(_str_height_header, _str_height_units))
    _all_regex_lists.append(_make_regexes(_str_weight_header, _str_weight_units))
    _all_regex_lists.append(_make_regexes(_str_length_header, _str_length_units))
    _all_regex_lists.append(_make_regexes(_str_hc_header,     _str_hc_units))
    _all_regex_lists.append(_make_regexes(_str_bsa_header,    _str_bsa_units))
    _all_regex_lists.append(_make_regexes(_str_bp_header,     _str_bp_units))
    _all_regex_lists.append(_make_regexes(_str_rr_header,     _str_rr_units))
    
    o2_regexes = []
    
    # additional O2 saturation regexs
    o2_header = r'(?P<header>\b' + _str_o2_header + _str_sep +\
        r'(' + _str_o2_units + _str_sep + r')?' + r')'

    # capture constructs such as O2 sat: 98 2LNC
    str_o2_1 = r'\b' + o2_header + _str_values + _str_sep +\
        r'\d+L\s?' + _str_o2_device + _str_sep
    o2_regexes.append(re.compile(str_o2_1, re.IGNORECASE))
    
    # capture one or two 'words' following an 'on', such as 'on NRB, on 6L NC'
    str_o2_2 = r'\b' + o2_header + _str_values + _str_sep +\
        r'(' + _str_o2_units + _str_sep + r')?' +\
        r'(on\s)?(\d+L)?' + r'(' + _str_sep + _str_o2_device + _str_sep + r')?'
    o2_regexes.append(re.compile(str_o2_2, re.IGNORECASE))

    # capture constructs such as '98% RA, sats 91% on NRB, 96O2-sat on RA' [L to R]
    str_o2_3 = r'(' + _str_o2_header + _str_sep + r')?'  +\
        r'(' + _str_o2_units  + _str_sep + r')?'         +\
        r'(?<!O)\d+' + _str_sep                          +\
        r'(' + _str_o2_units  + _str_sep + r')?'         +\
        r'(' + _str_o2_header + _str_sep + r')?'         +\
        r'(' + _str_o2_units  + _str_sep + r')?'         +\
        r'(' + r'on'          + _str_sep + r')?'         +\
        _str_o2_device + _str_sep
    o2_regexes.append(re.compile(str_o2_3, re.IGNORECASE))

    _all_regex_lists.append(o2_regexes)
    
    
###############################################################################
def _cleanup_sentence(sentence):

    # collapse multiple whitespace, to simplify regexes above
    sentence = re.sub(r'\s+', ' ', sentence)

    return sentence


###############################################################################
def _resolve_overlap(result_list):
    """
    Remove any remaining overlap among the items in the list. The items are
    of type finder_overlap.Candidate. Assumes the list items are sorted in
    order of occurrence in the sentence.
    """

    if 0 == len(result_list):
        return []

    if _TRACE:
        print('Called _resolve_overlap...')
        print('Candidates: ')
        for r in result_list:
            print('[{0:3}, {1:3}): {2}'.format(r.start, r.end, r.match_text))
        print()
    
    final_results = [ result_list[0] ]

    for i in range(1, len(result_list)):
        r = result_list[i]
        f = final_results[-1]
        # check for overlap with previous final result
        if not overlap.has_overlap(r.start, r.end, f.start, f.end):
            final_results.append(r)
            continue
        else:
            # has overlap with prevous result

            if _TRACE:
                print('\tOverlap: ')
                print('\t\tf:[{0:3},{1:3}): {2}'.
                      format(f.start, f.end, f.match_text))
                print('\t\tr:[{0:3},{1:3}): {2}'.
                      format(r.start, r.end, r.match_text))
                
            # check if duplicate
            if r.start == f.start and r.end == f.end:
                # ignore duplicate
                if _TRACE: print('\t\tduplicate')
                continue

            # partial overlap:
            #     |f.start---f.end|
            #              |r.start---r.end|
            #
            #     |f.start---f.end|
            #     |r.start--------------r.end|
            assert r.start <= f.end
            diff = f.end - r.start
            if _TRACE:
                print('\t\tdiff: {0}'.format(diff))
            assert diff >= 0
            if 0 == diff:
                continue

            # subtract 'diff' chars from the end of f
            # keep r intact
            new_f = overlap.Candidate(
                start      = f.start,
                end        = f.end-diff,
                match_text = f.match_text[:-diff],
                regex      = f.regex,
                other      = f.other)

            if new_f.start == new_f.end:
                if _TRACE:
                    print('\t\tzero span')
                continue
            
            # if identical to prior elt, ignore
            if len(final_results) >= 2:
                f2 = final_results[-2]
                if new_f.start == f2.start and \
                   new_f.end   == f2.end   and \
                   new_f.match_text == f2.match_text:
                    if _TRACE:
                        print('\t\tidentical to prior elt, ignoring...')
                    continue

            if _TRACE:
                print('\t\tOverwriting f with new_f: ')
                print('\t\tnew_f:[{0:3},{1:3}): {2}'.
                      format(new_f.start, new_f.end, new_f.match_text))
                
            final_results[-1] = new_f
            final_results.append(r)
    
    return final_results


###############################################################################
def run(sentence_in):
    """
    """

    results = []

    sentence = _cleanup_sentence(sentence_in)

    if _TRACE:
        print(' SENTENCE: "{0}"'.format(sentence))
    
    for regex_list_index, regex_list in enumerate(_all_regex_lists):
        candidates = []
        for regex_index, regex in enumerate(regex_list):
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

        if len(candidates) > 0:
            
            if _TRACE:
                print('\tCandidate matches: ')
                for index, c in enumerate(candidates):
                    print('\t[{0:2}]\t[{1},{2}): {3}'.
                          format(index, c.start, c.end, c.match_text, c.regex))
                print()

            pruned_candidates = overlap.remove_overlap(candidates, _TRACE)

            if _TRACE:
                print('\tcandidates count after overlap removal: {0}'.
                      format(len(pruned_candidates)))
                print('\tPruned candidates: ')
                for c in pruned_candidates:
                    print('\t\t[{0},{1}): {2}'.format(c.start, c.end, c.match_text))
                print()

            results.extend(pruned_candidates)

    # sort results by order of occurrence in sentence
    results = sorted(results, key=lambda x: x.start)

    # resolve any overlap in these final results
    results = _resolve_overlap(results)
    
    return results


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Find individual components in lists of vitals.')

    parser.add_argument('-v', '--version',
                        help='show version and exit',
                        action='store_true')
    parser.add_argument('-d', '--debug',
                        help='print debug information to stdout',
                        action='store_true')

    args = parser.parse_args()

    if 'version' in args and args.version:
        print(get_version())
        sys.exit(0)

    if 'debug' in args and args.debug:
        enable_debug()
    
    TEST_SENTENCES = [
        # # heart rate
        # 'Vitals: HR 70 (70 - 72) bpm, HR:    70(70   -72)  beats/min.',
        # 'Vitals: HR(bpm) 70 (70-72), HR (bpm): 70 (70-72), HR (bpm): 53',
        # 'Vitals: HR 70, HR:70, HR:70-72, HR:70 70/72',

        # # temperature
        # 'Vitals: T 95.6, T97.3, T: 99, Tmp. 95.5, T=98, T-100.6, Temp. 98.5F',
        # 'Tmax: 35.8 C (96.4 Tcurrent: 35.7 C (96.2',
        # 'Tmax: 35.8/96.4, Tcurrent: 35.7/96.2',
        # 'T: 35.8C/96.4F, Tmax35.7C / 96.2 F',

        # # height
        # 'Height: (in) 74, Height (in): 74, Height 74 (in.), Ht: 74 in.',

        # # weight
        # 'Weight: (lbs) 199, Weight (lb): 199, Wgt (current): 119.8 kg (admission): 121 kg',
        # 'Wt: 199 kg, Wt 198 lb., Weight: 197',

        # # body surface area
        # 'Vitals: BSA (m2): 2.17 m2, BSA: 2.20 msq.',

        # # blood pressure
        # 'Vitals: BP 75/30, BP120/60, BP (mm Hg): 140/91, BP:115/68',
        # 'Vitals: BP= 122/58, BP-93/46, BP115/65, BP: 84/43',
        # 'Vitals: BP: 93/67(73) {72/21(39) - 119/85(91)}',
        # 'Vitals: BP= 90-109/49-82',
        # 'Vitals: BP 119/53 (105/43 sleeping)',

        # # respiration rate
        # 'Vitals: RR 17, R:21, RR= 20, RR-16, R18, RR=24',
        # 'Vitals: RR 12 (10-23) insp/min',

        # # O2 saturation
        # 'Vitals: O2: 97, SpO2 98%/3L, O2 sat= 100% 2L/NC, Sats-98% 3L/NC',
        # 'Vitals: sats 96% on RA, O2SAts100%, SpO2% 99/bipap, O2 sat 95%RA',
        # 'Vitals: O2 Sat 85% 3L, POx=100%, POx=93% on 8L FM, SaO2 96% 6L NC',
        # 'Vitals: O2 sat 97%, SpO2 97% on NRB',
        # 'Vitals: O2 Flow: 100 (Non-Rebreather), SpO2 92%/RA',
        # 'Vitals: O2Sat98 2LNC',
        # 'Vitals: 98% RA, 91% on NRB, 96O2-sat on RA, 96O2-sat % RA',
        # 'Vitals: sats 96% on RA',

        # combined
        # 'VS: T 95.6 HR 45 BP 75/30 RR 17 98% RA.',
        # 'VS T97.3 P84 BP120/56 RR16 O2Sat98 2LNC',
        # 'Height: (in) 74 Weight (lb): 199 BSA (m2): 2.17 m2 ',
        # 'BP (mm Hg): 140/91 HR (bpm): 53',
        # 'Vitals: T: 99 BP: 115/68 P: 79 R:21 O2: 97',
        # 'Vitals - T 95.5 BP 132/65 HR 78 RR 20 SpO2 98%/3L',
        # 'VS: T=98 BP= 122/58  HR= 7 RR= 20  O2 sat= 100% 2L NC',
        # 'VS:  T-100.6, HR-105, BP-93/46, RR-16, Sats-98% 3L/NC',
        # 'VS - Temp. 98.5F, BP115/65 , HR103 , R16 , 96O2-sat % RA',
        # 'Vitals: Temp 100.2 HR 72 BP 184/56 RR 16 sats 96% on RA',
        # 'PHYSICAL EXAM: O: T: 98.8 BP: 123/60   HR:97    R 16  O2Sats100%',
        # 'VS before transfer were 85 BP 99/34 RR 20 SpO2% 99/bipap 10/5 50%.',
        # 'Initial vs were: T 98 P 91 BP 122/63 R 20 O2 sat 95%RA.',
        # 'Initial vitals were HR 106 BP 88/56 RR 20 O2 Sat 85% 3L.',
        # 'Initial vs were: T=99.3 P=120 BP=111/57 RR=24 POx=100%.',
        # 'At transfer vitals were HR=120 BP=109/44 RR=29 POx=93% on 8L FM.',
        # "Vitals as follows: BP 120/80 HR 60-80's RR  SaO2 96% 6L NC.",
        # 'Vital signs were T 97.5 HR 62 BP 168/60 RR 18 95% RA.',
        # 'T 99.4 P 160 R 56 BP 60/36 mean 44 O2 sat 97% Wt 3025 grams ' +\
        # 'Lt 18.5 inches HC 35 cm',
        # 'Vital signs were T 97.0 BP 85/44 HR 107 RR 28 and SpO2 91% on NRB.',
        # 'Vitals were BP 119/53 (105/43 sleeping) HR 103 RR 15 and ' +\
        # 'SpO2 97% on NRB.',
        # 'Vitals were Temperature 100.8 Pulse: 103 RR: 28 BP: 84/43 ' +\
        # 'O2Sat: 88 O2 Flow: 100 (Non-Rebreather).',
        'Vitals were T 97.1 HR 76 BP 148/80 RR 25 SpO2 92%/RA.',
    ]

    init()

    for sentence in TEST_SENTENCES:
        print('SENTENCE: "{0}"'.format(sentence))
        results = run(sentence)

        print('RESULTS: ')
        for r in results:
            print('\t\t[{0:3},{1:3}): {2}'.format(r.start, r.end, r.match_text))
        print()
        
