#!/usr/bin/env python3
"""

This is an import-only module for improving sentence segmentation results. It
tries to find expressions that could be improperly split by sentence tokenizers
trained on standard written English. The idea is to replace the expressions
that this module finds by a single token that the sentence tokenizers will NOT
split. See segmentation/segmentation_helper for more.

For examples of "lab values" and how this module is to be used, see the
associated test file "test_lab_value_matcher.py".

"""

import re
import os
import sys
import json

try:
    import finder_overlap as overlap
except:
    from algorithms.finder import finder_overlap as overlap


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 1
_MODULE_NAME = 'lab_value_matcher.py'

# set to True to see debug output
_TRACE = False

# Most of these are from http://ebmcalc.com/Basic.htm, an online medical unit
# conversion tool. Additional unit strings have been added.
_str_units = r'(#|$|%O2|%|10^12/L|10^3/microL|10^9/L|atm|bar|beats/min|bpm|'  +\
             r'breaths/min|centimeters|cmH2O|cmHg|cm^2|cm2|cm|cents|days|'    +\
             r'degC|degF|dyn-sec-cm-5|eq|feet|fL|fractionO2|fraction|ftH20|'  +\
             r'ft|g/dL|g/L/|gallon|gm/day|gm/dL|gm/kg/day|gm/kg|gm/L|gm/cm2|' +\
             r'gm/sqcm|gm|inches|inch|index|inH2O|inHg|in|IU/L|'              +\
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
             r'insp/min)(?=([^a-z]|\Z))'

# English stopword set from nltk, with modifications
_stopwords = {
    "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren", "aren't", "as", "at", "be", "because", "been",
    "before", "being", "below", "between", "both", "but", "by", "can",
    "couldn't", "did", "didn't", "do", "does", "doesn", "doesn't", "doing",
    "don't", "down", "during", "each", "few", "for", "from", "further", "had",
    "hadn't", "has", "hasn", "hasn't", "have", "haven", "haven't", "having",
    "he", "her", "here", "hers", "herself", "him", "himself", "his", "how",
    "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "just",
    "me", "mightn", "mightn't", "more", "most", "mustn't", "my", "myself",
    "needn't", "no", "nor", "not", "now", "of", "off", "on", "once", "only",
    "or", "other", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she's", "should", "should've", "shouldn", "shouldn't",
    "so", "some", "such", "than", "that", "that'll", "the", "their", "theirs",
    "them", "themselves", "then", "there", "these", "they", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
    "we", "were", "weren't", "what", "when", "where", "which", "while", "who",
    "whom", "why", "will", "with", "won", "won't", "wouldn", "wouldn't",
    "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves"
}

# separator between header and value
_str_sep = r'[-:=\s/{}]*'

# word, possibly hyphenated or parenthesized
_str_word = r'(\(\s?[-a-z]+\s?\)|[-a-z]+)(?=[^a-z])'

# numeric value, either floating point or integer, possibly suffixed with
# an 's' or an apostrophe-s (the 's' is for constructs such as 70s, 80s, etc.)
_str_float_or_int = r'(\d+\.\d+|\.\d+|\d+)\'?s?'
# integers with embedded commas
_str_comma_int = r'(\d\d\d|\d\d|\d)(,\d\d\d)+'
_str_num = r'\-?(' + _str_comma_int + r'|' + _str_float_or_int + r')'
_regex_num = re.compile(_str_num)

# list of numbers with units
_str_num_and_unit_list = r'(' + _str_num + r'\s?' + _str_units +\
    r'\s?' + r'){2,}'
_regex_num_and_unit_list = re.compile(_str_num_and_unit_list, re.IGNORECASE)

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
_str_temp_units = r'\(?(C|F|deg\.?(rees)?\s?(C(elsius)?|F(arenheit)?)|' +\
    r'deg\.?(rees)?)\)?'
_str_temp_header = r'\b(Temperature|Tcurrent|Tmax|Tcur|Te?mp|Tm|T)\.?'

# heart rate
_str_hr_units  = r'\(?(bpm|beats/m(in\.?)?|beats per min\.?(ute)?)\)?'
_str_hr_header = r'\b(Pulse|P|HR|Heart\s?Rate)'

# respiration rate (and other respiratory quantities)
_str_rr_units = r'\(?((insp\.?|breaths?)[\s/]*min|bpm|mL|L/min)\.?\)?'
_str_rr_header = r'\b(respiration\s?rate|respiratory\s?rate|' +\
    r'breathing|resp\.?|RR?|RSBI|ABG|Vt|Ve)'

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
_str_bp_header = r'\b(systolic blood pressure|diastolic blood pressure|' +\
    'blood\s?pressure|b\.?\s?p|CVP|RAP|SBP|DBP)\.?'

# Oxygen saturation
_str_o2_units = r'\(?(percent|pct\.?|%|cmH2O|mmHg)\)?'
# no leading r'\b', on purpose
_str_o2_header = r'(SpO2|SaO2|sO2|O2[-\s]?saturation|O2[-\s]sat\.?s?|'       +\
    r'oxygen\s?saturation|satting|O2Sats?|O2\s?flow|Sat\.?s?|plateau|'       +\
    r'PaO2\s?/\s?FiO2|PaO2|FiO2|POx|PaCO2|PEEP|PIP|CPAP|PAW|PSV|PO|PS|O2)'
_str_o2_device = r'\(?(bipap|non[-\s]?rebreather(\smask)?|nasal\s?cannula|'  +\
    r'room air|([a-z]+)?\s?mask|cannula|PSV|NRB|RA|FM|NC|air|'               +\
    r'on\svent(ilator)?)\)?'

# need '-' and '+' to capture ion concentrations such as 'Ca++ : 8.0 mg/dL'
_str_simple_header = r'\b(?<!/)[-+a-z]+'

# header-value pair
_str_simple_pair = _str_simple_header + r':\s?' + _str_num + r'\s?' +\
    _str_units + r'\s?'
_regex_simple_pair = re.compile(_str_simple_pair, re.IGNORECASE)

# too slow; not needed if only capturing lists of number-unit pairs
# # header followed by list of numbers, each with units
# _str_header_value_units = _str_simple_header + _str_sep +\
#     r'((?<=[^a-z])' + _str_values + _str_sep + _str_units + _str_sep + r')+'
# _regex_header_value_units = re.compile(_str_header_value_units,
#                                        re.IGNORECASE)

# # header followed by list of numbers with no units
# _str_header_values = _str_simple_header + _str_sep +\
#     r'((?<=[^a-z])' + _str_values + _str_sep + r')+'
# _regex_header_values = re.compile(_str_header_values, re.IGNORECASE)

_str_avg = r'\b(average|mean|avg\.?|median|mode)\b'
_regex_avg = re.compile(_str_avg, re.IGNORECASE)

_all_regex_lists = []


###############################################################################
def enable_debug():

    global _TRACE
    _TRACE = True


###############################################################################
def _make_regexes(header_in, units_in):
    """
    Generate desired regex forms from the header and unit strings passed
    as arguments. Returns a list of the generated regexes.
    """
    
    regex_list = []
    
    # # header string with optional units
    header = r'(?<!/)(?P<header>' + header_in + _str_sep +\
        r'(' + units_in + _str_sep + r')?' + r'(?=[^a-z]))'

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

    # header + optional words + single value + optional units
    str_regex = header + r'(\s?' + _str_word + _str_sep + r')*' +\
        _str_values + _str_sep + r'(' + units_in + _str_sep + r')?'
    regex_list.append(re.compile(str_regex, re.IGNORECASE))
    
    return regex_list


###############################################################################
def init():
    """
    Construct all required regexes from predefined header and unit strings.
    """

    _all_regex_lists.clear()

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
 
    o2_header = r'(?<!/)(?P<header>\b' + _str_o2_header + _str_sep          +\
        r'(' + _str_o2_units + _str_sep + r')?' + r'(of\s)?' + r')'

    # capture constructs such as O2 sat: 98 2LNC
    str_o2_1 = r'\b' + o2_header + _str_values + _str_sep +\
        r'\d+L\s?' + _str_o2_device + _str_sep
    o2_regexes.append(re.compile(str_o2_1, re.IGNORECASE))
    
    # capture one or two 'words' following an 'on', such as 'on NRB, on 6L NC'
    str_o2_2 = r'\b' + o2_header + _str_values + _str_sep              +\
        r'(' + _str_o2_units + _str_sep + r')?'                        +\
        r'(on\s)?(\d+\s?(liters|L))?'                                  +\
        r'((\d+%)?' + _str_sep + _str_o2_device + _str_sep + r')?'
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

    str_o2_4 = r'\b' + o2_header + r'\d+% on \d+% O2' + _str_sep +\
        _str_o2_device + _str_sep
    o2_regexes.append(re.compile(str_o2_4, re.IGNORECASE))

    # range of O2 saturation
    str_o2_5 = r'\b' + o2_header +\
        r'(' + _str_word + _str_sep + r')*' +\
        r'\d+% to \d+%' + _str_sep +\
        r'(' + _str_word + _str_sep + r')+' +\
        r'\d+%' + _str_sep + _str_o2_device + _str_sep
    o2_regexes.append(re.compile(str_o2_5, re.IGNORECASE))
    
    _all_regex_lists.append(o2_regexes)

    _all_regex_lists.append( [_regex_num_and_unit_list] )
    _all_regex_lists.append( [_regex_simple_pair] )
    
    
###############################################################################
def _cleanup_text(text):

    # collapse multiple whitespace, to simplify regexes above
    text = re.sub(r'\s+', ' ', text)

    # collapse multiple '/' into a single '/'
    text = re.sub(r'/+', '/', text)

    return text


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

            # if r begins with 'mean', 'avg', etc., append to f
            match2 = _regex_avg.match(r.match_text)
            if match2:
                match_text = f.match_text + r.match_text
                new_f = overlap.Candidate(
                    start = f.start,
                    end = f.start + len(match_text),
                    match_text = match_text,
                    regex = f.regex,
                    other = f.other)
                final_results[-1] = new_f
                if _TRACE:
                    print('\tAppending r to f: ')
                    print('\t\tf:[{0:3},{1:3}): {2}'.
                          format(f.start, f.end, f.match_text))
                    print('\t\tr:[{0:3},{1:3}): {2}'.
                          format(r.start, r.end, r.match_text))
                continue

            match2 = re.match(r'\A[\d.%]+\s?\Z', r.match_text)
            if match2:
                # discard, value only
                if _TRACE:
                    print('\t\tvalue only, discarding "{0}"'.
                          format(r.match_text))
                continue
            
            if _TRACE: print('\tkeeping result {0}'.format(r.match_text))
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

            # if r is a subset of f, ignore r
            if -1 != f.match_text.find(r.match_text):
                if _TRACE: print('\t\tr is a subset of f, ignoring r...')
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
            match_text = f.match_text[:-diff]
            match = _regex_num.search(match_text)
            if not match:
                # remove final_result[-1] (only text, no numeric value remains)
                # replace with r
                if _TRACE:
                    print('\t\tignoring f, text only: "{0}"'.format(match_text))
                    
                final_results[-1] = r
                continue

            if match_text.endswith('/'):
                # discard r, f would be left as a fragment
                if _TRACE:
                    print('\t\tavoiding fragment, discarding "{0}"'.
                          format(r.match_text))
                continue

            match = re.match(r'[\d.%]+\s?', match_text)
            if match:
                # discard, value only
                if _TRACE:
                    print('\t\tvalue only, discarding "{0}"'.
                          format(match_text))
                continue
            
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
def run(text_in):
    """
    Find lab values in the input text and return a list of
    finder_overlap.Candidate results.
    """

    results = []

    text = _cleanup_text(text_in)

    if _TRACE:
        print('\n*****\n TEXT: "{0}"\n*****\n'.format(text))
    
    for regex_list_index, regex_list in enumerate(_all_regex_lists):
        candidates = []
        for regex_index, regex in enumerate(regex_list):
            iterator = regex.finditer(text)
            for match in iterator:
                start = match.start()
                end   = match.end()
                match_text = match.group()
                if 0 == len(match_text):
                    continue

                # valid matches must begin with an alphanumeric char or a dash
                first_char = match_text[0]
                if '-' != first_char and not first_char.isalnum():
                    if _TRACE:
                        print('\tDiscarding (not isalnum): "{0}"'.
                              format(match_text))
                    continue
                
                # discard if match_text begins with a stopword
                pos = match_text.find(' ')
                if -1 != pos and match_text[:pos] in _stopwords:
                    if _TRACE:
                        print('\tDiscarding (stopword) "{0}"'.
                              format(match_text))
                    continue

                if _TRACE:
                    print('\tMATCH: "{0}"'.format(match_text))
                    if 'header' in match.groupdict().keys():
                        header = match.group('header')
                        if header is not None:
                            print('\t\tHEADER: "{0}"'.format(header))

                c = overlap.Candidate(start, end, match_text, None)
                candidates.append(c)

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
                print('\tCandidate count after overlap removal: {0}'.
                      format(len(pruned_candidates)))
                print('\tPruned candidates: ')
                for c in pruned_candidates:
                    print('\t\t[{0},{1}): {2}'.format(c.start, c.end, c.match_text))
                print()

            results.extend(pruned_candidates)

    # sort results by order of occurrence in text
    results = sorted(results, key=lambda x: x.start)

    # resolve any overlap in these final results
    results = _resolve_overlap(results)
    
    return results


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)

