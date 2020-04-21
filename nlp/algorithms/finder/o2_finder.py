#!/usr/bin/env python3
"""

This is a custom task for finding a patient's P/F ratio, which is relevant
to assessing the amount of oxygen in the blood. The P/F ratio is defined as:

    (partial pressure of O2 in arterial blood) / (fraction of inspired oxygen)

Using common symbols, this can be written as:

    P/F = PaO2 / FiO2

Generally a P/F ratio less than 300 means the patient has hypoxemia.

The P/F ratio can be estimated from pulse ox measurements and O2 flow rates.

Conversion of pulse ox value (SpO2 %) to O2 partial pressure (mmHg):

    SpO2 (%)    PaO2 (mmHg)
    --------    -----------
      80            44
      81            45
      82            46
      83            47
      84            49
      85            50
      86            52
      87            53
      88            55
      89            57
      90            60
      91            62
      92            65
      93            69
      94            73
      95            79
      96            86
      97            96
      98           112
      99           145

The FiO2 percentage can be estimated from O2 flow rates of different breathing
devices. Normal breathing in room air produces an FiO2 value of 20%.

For a nasal cannula, each L/min of O2 adds 4% to the FiO2 value:
FiO2 = 0.2 + (0.04) * (flow_rate_l_per_min-1), 1 <= flow_rate <= 10


       flow rate (L/min)    FiO2 (%)
       ----------------     --------
           1                  24
           2                  28
           3                  32
           4                  36
           5                  40
           6                  44
           7                  48
           8                  52
           9                  56
          10                  60

For a nasopharyngeal catheter:
FiO2 = (0.4) * (0.1)*(flow_rate_l_per_min-4), 4 <= flow_rate <= 6

       flow rate (L/min)    FiO2 (%)
       ----------------     --------
           4                  40
           5                  50
           6                  60

For a face mask with no reservoir (rebreather mask):
FiO2 = 0.35 + (0.04) * (flow_rate_l_per_min - 5), 5 <= flow_rate <= 10

       flow rate (L/min)    FiO2 (%)
       ----------------     --------
           5                  35
           6                  39
           7                  43
           8                  47
           9                  51
          10                  55

For a face mask with reservoir (non-rebreather):
FiO2 = 0.6 + (0.10) * (flow_rate_l_per_min - 6), 6 <= flow_rate <= 9
FiO2 = 0.9 + (0.05) * (flow_rate_l_per_min - 9), 9 <= flow_rate <= 10

       flow rate (L/min)    FiO2 (%)
       ----------------     --------
           6                  60
           7                  70
           8                  80
           9                  90
          10                  95

Venturi Mask:

FiO2 = 0.24 + (0.020)(flow_rate_l_per_m -  2),  2 <= flow_rate <= 4
       0.28 + (0.015)(flow_rate_l_per_m -  4),  4 <= flow_rate <= 6
       0.31 + (0.020)(flow_rate_l_per_m -  6),  6 <= flow_rate <= 8
       0.35 + (0.025)(flow_rate_l_per_m -  8),  8 <= flow_rate <= 10
       0.40 + (0.040)(flow_rate_l_per_m - 10), 10 <= flow_rate <= 15

       flow rate (L/min)    FiO2 (%)
       ----------------     --------
           2                  24
           4                  28
           6                  31
           8                  35
          10                  40
          15                  60

"""

import os
import re
import sys
import json
import argparse
from collections import namedtuple

if __name__ == '__main__':
    # interactive testing
    match = re.search(r'nlp/', sys.path[0])
    if match:
        nlp_dir = sys.path[0][:match.end()]
        sys.path.append(nlp_dir)
    else:
        print('\n*** o2_finder.py: nlp dir not found ***\n')
        sys.exit(0)

try:
    import finder_overlap as overlap
except:
    from algorithms.finder import finder_overlap as overlap

# default value for all fields
EMPTY_FIELD = None

O2_TUPLE_FIELDS = [
    'text',
    'start',
    'end',
    'o2_sat',           # [%]
    'pao2',             # [mmHg]
    'pao2_est',         # estimated from o2_sat
    'fio2',             # [%]
    'fio2_est',         # estimated from flow_rate
    'p_to_f_ratio',
    'p_to_f_ratio_est', # estimated
    'flow_rate',        # [L/min]
    'device',
    'value',
    'value2',

    # computed fields - TBD
]
O2Tuple = namedtuple('O2Tuple', O2_TUPLE_FIELDS)


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 1
_MODULE_NAME   = 'o2_finder.py'

# set to True to enable debug output
_TRACE = False


#_str_connector = r'\s?([-/:=\s]|of|on)\s?'
#_str_connector = r'([-/:=\s]|now|of|on a|on|with|was|were|is|to)+'
_str_connector = r'[-/:=~\sa-z]+'

# O2 saturation header
_str_o2_sat_hdr = r'\b(spo2|sao2|pox|so2|(o2|oxygen)[-\s]?saturation|'       +\
    r'o2[-\s]sat\.?s?|satting|o2sats?|sat\.?s?|pulse ox|o2(?!\s?flow)|'      +\
    r'desatt?ing|desat\.?)%?'

_str_units = r'\(?(percent|pct\.?|%|mmHg)\)?'

# o2 saturation value
_str_o2_val_range = r'\b(was|from)?\s?(?P<val1>\d\d?)(\s?' + _str_units + r')?' +\
    r'(\s?(\-|to)\s?)(?P<val2>(100|\d\d?))(\s?' + _str_units + r')?'
_regex_o2_val_range = re.compile(_str_o2_val_range, re.IGNORECASE)

_str_o2_value = r'(?<!o)(?P<val>(100|\d\d?)(?!L))(\s?' + _str_units + r')?'
_str_o2_val = r'(' + _str_o2_val_range + r'|' + _str_o2_value + r')'

# O2 flow rate in L/min
_str_flow_rate = r'(?P<flow_rate>\d+)\s?(Liters|L)(/min\.?)?'

# devices and related acronyms
#         RA : right atrial, usually via fiberoptic oximetry
#         FM : face mask
#        BVM : bag valve mask
#        RBM : rebreather mask
#  venti mask: Venturi mask
#       bipap: bilevel positive airway pressure

# sometimes see NC called "O2 NC"
_str_device_nc  = r'(?P<nc>(O2\s)?(nc|nasal[-\s]?cannula|cannula))'
_str_device_nrb = r'(?P<nrb>(nrb|(\d+%\s)?non[-\s]?rebreather(\smask)?))'
_str_device_ra  = r'(?P<ra>(ra|radial[-\s]?artery))'
_str_device_venturi = r'(?P<venturi>((venturi|venti)[-\s]?mask)|' +\
    r'\d+\s?%\s?(venturi|venti)[-\s]?mask)'
_str_device_bvm = r'(?P<bvm>(bvm|bag[-\s]valve\smask))'
_str_device_bipap = r'(?P<bipap>(bipap\s\d+/\d+\s?(with\s\d+L|\d+%)|bipap(\s\d+/\d+)?))'
_str_device_mask = r'(?P<mask>(fm|rbm|[a-z\s]+[-\s]?mask|' +\
    r'vent(ilator)?|\d+%\s?[a-z]+[-\s]?mask|\d+%\s?[a-z]+[-\s]?tent|mask))'
#_str_device_mask = r'(?P<mask>(fm))'
_str_device_air = r'(?P<air>(ra|room[-\s]air|air))'
_str_device_nasocath = r'(?P<nasocath>(naso\.?(pharyngeal)?[-\s]?cath\.?(eter)?|' +\
    r'cath\.?(eter)?))'

##### Functions to convert an O2 flow rate into an estimated FiO2 value. #####

def _to_fio2_nc(flow_rate_l_min):
    """
    Convert an O2 flow rate to an estimated FiO2 value for a nasal cannula.
    Return FiO2 as a percentage.
    """

    fio2_est = EMPTY_FIELD
    if flow_rate_l_min >= 1 and flow_rate_l_min <= 10:
        fio2_est = 24 + 4*(flow_rate_l_min - 1)
    return fio2_est

def _to_fio2_nrb(flow_rate_l_min):
    """
    Convert an O2 flow rate to an estimated FiO2 value for a non-rebreather mask.
    Return FiO2 as a percentage.
    """

    fio2_est = EMPTY_FIELD
    if flow_rate_l_min >= 6 and flow_rate_l_min < 9:
        fio2_est = 60 + 10 * (flow_rate_l_min - 6)
    elif flow_rate_l_min >= 9 and flow_rate_l_min <= 10:
        fio2_est = 90 + 5 * (flow_rate_l_min - 9)
    return fio2_est

def _to_fio2_venturi(flow_rate_l_min):
    """
    Convert an O2 flow rate to an estimated FiO2 value for a venturi mask.
    Return FiO2 as a percentage.
    """

    fio2_est = EMPTY_FIELD
    if flow_rate_l_min >=2 and flow_rate_l_min < 4:
        fio2_est = 24 + 2*(flow_rate_l_min - 2)
    elif flow_rate_l_min >= 4 and flow_rate_l_min < 6:
        fio2_est = 28 + 1.5*(flow_rate_l_min - 4)
    elif flow_rate_l_min >= 6 and flow_rate_l_min < 8:
        fio2_est = 31 + 2 * (flow_rate_l_min - 6)
    elif flow_rate_l_min >= 8 and flow_rate_l_min < 10:
        fio2_est = 35 + 2.5 * (flow_rate_l_min - 8)
    elif flow_rate_l_min >= 10 and flow_rate_l_min <= 15:
        fio2_est = 40 + 4 * (flow_rate_l_min - 10)
    return fio2_est

def _to_fio2_mask(flow_rate_l_min):
    """
    Convert an O2 flow rate to an estimated FiO2 value for a rebreather mask.
    Return FiO2 as a percentage.
    """

    fio2_est = EMPTY_FIELD
    if flow_rate_l_min >= 5 and flow_rate_l_min <= 10:
        return 35 + 4 * (flow_rate_l_min - 5)
    return fio2_est

def _to_fio2_nasocath(flow_rate_l_min):
    """
    Convert an O2 flow rate to an estimated FiO2 value for a nasopharyngeal
    catheter.  Return FiO2 as a percentage.
    """

    fio2_est = EMPTY_FIELD
    if flow_rate_l_min >= 4 and flow_rate_l_min <= 6:
        return 40 + 10*(flow_rate_l_min - 4)
    return fio2_est

    
# all device capture group names are keys
# each is mapped to an FiO2 conversion fn taking O2 flow_rate as arg
_DEVICE_MAP = {
    'nc':_to_fio2_nc,
    'nrb':_to_fio2_nrb,
    'ra':None,
    'venturi':_to_fio2_venturi,
    'bvm':None,
    'bipap':None,
    'mask':_to_fio2_mask,
    'air':None,
    'nasocath':_to_fio2_nasocath
}

_str_device = r'\(?' +\
    r'(' + _str_device_nc + r')'       + r'|' +\
    r'(' + _str_device_nrb + r')'      + r'|' +\
    r'(' + _str_device_ra + r')'       + r'|' +\
    r'(' + _str_device_venturi + r')'  + r'|' +\
    r'(' + _str_device_bvm + r')'      + r'|' +\
    r'(' + _str_device_bipap + r')'    + r'|' +\
    r'(' + _str_device_mask + r')'     + r'|' +\
    r'(' + _str_device_air + r')'      + r'|' +\
    r'(' + _str_device_nasocath + r')'        +\
    r'\)?'

# finds "spo2: 98% on 2L NC" and similar
_str_o2_1 = _str_o2_sat_hdr + r'(' + _str_connector + r')?' + _str_o2_val    +\
    r'(' + _str_connector + r')?' + _str_flow_rate                           +\
    r'(' + _str_connector + r')?' + r'(?P<device>' + _str_device + r')'
_regex_o2_1 = re.compile(_str_o2_1, re.IGNORECASE)

# finds "spo2: 98%/NC" and similar
_str_o2_2 = _str_o2_sat_hdr + r'(' + _str_connector + r')?' + _str_o2_val    +\
    r'(' + _str_connector + r')?' + r'(?P<device>' + _str_device + r')'
_regex_o2_2 = re.compile(_str_o2_2, re.IGNORECASE)

# finds "spo2: 98%/3L" and similar
_str_o2_3 = _str_o2_sat_hdr + r'(' + _str_connector + r')?' + _str_o2_val    +\
    r'(' + _str_connector + r')?' + _str_flow_rate
_regex_o2_3 = re.compile(_str_o2_3, re.IGNORECASE)

# finds "spo2=98%" and similar
_str_o2_4 = _str_o2_sat_hdr + r'(' + _str_connector + r')?' + _str_o2_val
_regex_o2_4 = re.compile(_str_o2_4, re.IGNORECASE)

# finds "98% RA" and similar (value to the left)
_str_o2_5 = r'(?<![-:=/])(?<=\s)' + _str_o2_val + r'(' + _str_connector + r')?' +\
    r'(' + _str_flow_rate + r')?\s?' +\
    r'(?P<device>' + _str_device +r')'
_regex_o2_5 = re.compile(_str_o2_5, re.IGNORECASE)

# like the first regex, but finds flow rate after device
_str_o2_6 = _str_o2_sat_hdr + r'(' + _str_connector + r')?' + _str_o2_val    +\
    r'(' + _str_connector + r')?' + r'(?P<device>' + _str_device + r')'      +\
    r'(' + _str_connector + r')?' + _str_flow_rate
_regex_o2_6 = re.compile(_str_o2_6, re.IGNORECASE)

# finds "using BVM with O2 sats 74%" (device prior to O2 saturation header)
_str_o2_7 = r'(?P<device>' + _str_device + r')'         +\
    r'(' + _str_connector + r')?' + _str_o2_sat_hdr     +\
    r'(' + _str_connector + r')?' + _str_o2_val         +\
    r'(' + _str_connector + _str_flow_rate + r')?'
_regex_o2_7 = re.compile(_str_o2_7, re.IGNORECASE)

_SAO2_REGEXES = [
    _regex_o2_1,
    _regex_o2_2,
    _regex_o2_3,
    _regex_o2_4,
    _regex_o2_5,
    _regex_o2_6,
    _regex_o2_7,
]

# o2 partial pressure (don't capture first part of PaO2 / FiO2
_str_pao2 = r'\b(pao2|partial pressure of (oxygen|o2))(?!/)(?! /)' +\
    r'(' + _str_connector + r')?' +  _str_o2_val
_regex_pao2 = re.compile(_str_pao2, re.IGNORECASE)

# fraction of inspired oxygen (prevent matches to pao2 / fio2)
_str_fio2 = r'\b(?<!/)(?<!/\s)fio2' +\
    r'(' + _str_connector + r')?' + _str_o2_val
_regex_fio2 = re.compile(_str_fio2, re.IGNORECASE)

# p/f ratio
_str_pf_ratio = r'\b(pao2|p)\s?/\s?(fio2|f)(\s?ratio)?' +\
    r'(' + _str_connector + r')?' + _str_o2_val
_regex_pf_ratio = re.compile(_str_pf_ratio, re.IGNORECASE)


# convert SpO2 to PaO2
_SPO2_TO_PAO2 = {
    80:44,
    81:45,
    82:46,
    83:47,
    84:49,
    85:50,
    86:52,
    87:53,
    88:55,
    89:57,
    90:60,
    91:62,
    92:65,
    93:69,
    94:73,
    95:79,
    96:86,
    97:96,
    98:112,
    99:145
}


###############################################################################
def _enable_debug():

    global _TRACE
    _TRACE = True
    

###############################################################################
def _cleanup(sentence):
    """
    Apply some cleanup operations to the sentence and return the
    cleaned sentence.
    """

    # replace ' w/ ' with 'with'
    sentence = re.sub(r'\sw/\s', ' with ', sentence)
    
    # replace some chars with whitespace
    sentence = re.sub(r'[,&]', ' ', sentence)

    # collapse repeated whitespace
    sentence = re.sub(r'\s+', ' ', sentence)

    return sentence


###############################################################################
def _estimate_fio2(flow_rate, device):
    """
    Estimate the FiO2 value (fraction of inspired oxygen, as a percentage)
    from the given flow rate in L/min and device.

    The device argument is encoded as follows: 'device_string|device_type',
    where 'device_type' is a regex group name.
    """

    # caller should have checked this
    assert device is not None

    if _TRACE:
        print('Calling _estimate_fio2...')
    
    device_str, device_type = device.split('|')
    
    if _TRACE:
        print('\t   device_str: {0}'.format(device_str))
        print('\t  device_type: {0}'.format(device_type))
        
    if device_type not in _DEVICE_MAP:
        if _TRACE: print('\tdevice type not in device map')
        return device_str, EMPTY_FIELD

    if flow_rate is None:
        if _TRACE: print('\t  no flow rate available, exiting...')
        return device_str, EMPTY_FIELD
    
    fio2_est = EMPTY_FIELD
    for dt in _DEVICE_MAP:
        if dt == device_type:
            # lookup a conversion function
            conversion_fn = _DEVICE_MAP[dt]
            if conversion_fn is not None:
                fio2_est = conversion_fn(flow_rate)
                break

    return device_str, fio2_est
    

###############################################################################
def _estimate_pao2(spo2):
    """
    Return a PaO2 estimate in mmHg from a given SpO2 percentage.
    The estimate is computed by linear piecewise approximation.
    """

    if spo2 is None:
        return EMPTY_FIELD

    p = None
    if spo2 >= 99:
        p = 145
    elif spo2 <= 80:
        p = 44
    else:
        for s0 in range(80, 99):
            # find known bounds on the SpO2 value, then linearly interpolate
            if spo2 >= s0 and spo2 < (s0 + 1.0):
                p0 = _SPO2_TO_PAO2[s0]
                p1 = _SPO2_TO_PAO2[s0+1]
                # slope m = delta_p/delta_s
                m = (p1 - p0) # denom == (s0+1 - s0) == 1
                p = p0 + m * (spo2 - s0)
                break

    assert p is not None
    return p


###############################################################################
def _extract_values(match_obj):
    """
    Find the 'val', 'val1', and 'val2' groups from the matchobj groupdict.
    """

    val1 = None
    val2 = None
    for k,v in match_obj.groupdict().items():
        if v is None:
            continue
        if 'val' == k or 'val1' == k:
            val1 = float(v)
        elif 'val2' == k:
            val2 = float(v)

    return (val1, val2)
    

###############################################################################
def _regex_match(sentence, regex_list):
    """
    """
    
    candidates = []
    for i, regex in enumerate(regex_list):
        iterator = regex.finditer(sentence)
        for match in iterator:
        #match = regex.search(sentence)
        #if match:
            match_text = match.group().strip()
            start = match.start()
            end   = start + len(match_text)
            candidates.append(overlap.Candidate(start, end, match_text, regex,
                                                other=match))
            if _TRACE:
                print('[{0:2}]: [{1:3}, {2:3})\tMATCH TEXT: ->{3}<-'.
                      format(i, start, end, match_text))

    if 0 == len(candidates):
        return []
                
    # sort the candidates in descending order of length, which is needed for
    # one-pass overlap resolution later on
    candidates = sorted(candidates, key=lambda x: x.end-x.start, reverse=True)

    if _TRACE:
        print('\tCandidate matches: ')
        index = 0
        for c in candidates:
            print('\t[{0:2}]\t[{1},{2}): {3}'.
                  format(index, c.start, c.end, c.match_text, c.regex))
            index += 1
        print()

    pruned_candidates = overlap.remove_overlap(candidates, _TRACE)

    if _TRACE:
        print('\tcandidate count after overlap removal: {0}'.
              format(len(pruned_candidates)))
        print('\tPruned candidates: ')
        for c in pruned_candidates:
            print('\t\t[{0},{1}): {2}'.format(c.start, c.end, c.match_text))
        print()

    return pruned_candidates
    

###############################################################################
def run(sentence):
    """
    Find values related to oxygen saturation, flow rates, etc. Compute values
    such as P/F ratio when possible. Returns a JSON array containing info
    on all values extracted or computed.
    """

    results = []
    cleaned_sentence = _cleanup(sentence)

    # could have ovelapping SaO2 matches
    sao2_candidates = _regex_match(cleaned_sentence, _SAO2_REGEXES)

    # only a single match for pao2, fio2, p_to_f_ratio
    
    pao2 = EMPTY_FIELD
    pao2_candidates = _regex_match(cleaned_sentence, [_regex_pao2])
    if len(pao2_candidates) > 0:
        assert 1 == len(pao2_candidates)
        match_obj = pao2_candidates[0].other
        pao2, pao2_2 = _extract_values(match_obj)

    fio2 = EMPTY_FIELD
    fio2_candidates = _regex_match(cleaned_sentence, [_regex_fio2])
    if len(fio2_candidates) > 0:
        assert 1 == len(fio2_candidates)
        match_obj = fio2_candidates[0].other
        fio2, fio2_2 = _extract_values(match_obj)
        # convert fio2 to a percentage
        if fio2 < 1.0:
            fio2 *= 100.0

    p_to_f_ratio = EMPTY_FIELD
    pf_candidates = _regex_match(cleaned_sentence, [_regex_pf_ratio])
    if len(pf_candidates) > 0:
        assert 1 == len(pf_candidates)
        match_obj = pf_candidates[0].other
        p_to_f_ratio, p_to_f_ratio_2 = _extract_values(match_obj)

    if _TRACE:
        print('Extracting data from pruned candidates...')

    for pc in sao2_candidates:
        # recover the regex match object from the 'other' field
        match = pc.other
        assert match is not None
                
        o2_sat           = EMPTY_FIELD
        flow_rate        = EMPTY_FIELD
        device           = EMPTY_FIELD
        value            = EMPTY_FIELD
        value2           = EMPTY_FIELD
        pao2_est         = EMPTY_FIELD
        fio2_est         = EMPTY_FIELD
        p_to_f_ratio_est = EMPTY_FIELD

        if _TRACE:
            print('match.groupdict entries: ')
        for k,v in match.groupdict().items():
            if _TRACE:
                print('\t{0} => {1}'.format(k,v))
            if v is None:
                continue
            if 'val1' == k or 'val' == k:
                value = float(v)
                o2_sat = value
            elif 'val2' == k:
                value2 = float(v)
            elif 'flow_rate' == k:
                flow_rate = float(v)
            elif k in _DEVICE_MAP:
                device_type = k
                device = '{0}|{1}'.format(v,k)

        # compute estimated PaO2 from SpO2
        if EMPTY_FIELD == pao2:
            pao2_est = _estimate_pao2(o2_sat)

        # compute estimated FiO2 from flow rate and device
        if EMPTY_FIELD == fio2 and device is not None:
            device, fio2_est = _estimate_fio2(flow_rate, device)

        # get a pao2 value, with stated taking precedence over estimated
        pao2_val = None
        if pao2 != EMPTY_FIELD or pao2_est != EMPTY_FIELD:
            if pao2 != EMPTY_FIELD:
                pao2_val = pao2
            else:
                pao2_val = pao2_est

        # get an fio2 value, with stated taking precedence over estimated
        fio2_val = None
        if fio2 != EMPTY_FIELD or fio2_est != EMPTY_FIELD:
            if fio2 != EMPTY_FIELD:
                fio2_val = fio2
            else:
                fio2_val = fio2_est

        # compute estimated P/F ratio from whatever values are available
        if pao2_val != EMPTY_FIELD and fio2_val != EMPTY_FIELD:
                p_to_f_ratio_est = pao2_val / (0.01 * fio2_val)

        # room air FiO2 is ~20%
        if fio2_val is None and pao2_val is not None and device is not None:
            if -1 != device.find('air'):
                p_to_f_ratio_est = pao2_val / 0.2
                
        o2_tuple = O2Tuple(
            text = pc.match_text,
            start = pc.start,
            end = pc.end,
            o2_sat = o2_sat,
            pao2 = pao2,
            fio2 = fio2,
            p_to_f_ratio = p_to_f_ratio,
            flow_rate = flow_rate,
            device = device,
            value = value,
            value2 = value2,
            pao2_est = pao2_est,
            fio2_est = fio2_est,
            p_to_f_ratio_est = p_to_f_ratio_est
        )
        results.append(o2_tuple)

    # sort results to match order of occurrence in sentence
    results = sorted(results, key=lambda x: x.start)

    # convert to list of dicts to preserve field names in JSON output
    return json.dumps([r._asdict() for r in results], indent=4)
    

###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)

                        
###############################################################################
if __name__ == '__main__':

    # for command-line testing only

    parser = argparse.ArgumentParser(
        description='test P/F ratio task locally')

    parser.add_argument('--debug',
                        action='store_true',
                        help='print debugging information')

    args = parser.parse_args()

    if 'debug' in args and args.debug:
        _enable_debug()

    SENTENCES = [
        'Vitals were HR=120, BP=109/44, RR=29, POx=93% on 8L FM',
        'Vitals: T: 96.0  BP: 90/54 P: 88 R: 16 18 O2:88/NRB',
        'Vitals: T 98.9 F BP 138/56 P 89 RR 28 SaO2 100% on NRB',
        'Vitals were T 98 BP 163/64 HR 73 O2 95% on 55% venti mask',
        'VS: T 95.6 HR 45 BP 75/30 RR 17 98% RA.',
        'VS T97.3 P84 BP120/56 RR16 O2Sat98 2LNC',
        'Vitals: T: 99 BP: 115/68 P: 79 R:21 O2: 97',
        'Vitals - T 95.5 BP 132/65 HR 78 RR 20 SpO2 98%/3L',
        'VS: T=98 BP= 122/58  HR= 7 RR= 20  O2 sat= 100% 2L NC',
        'Vitals: T: 97.7 P:100 R:16 BP:126/95 SaO2:100 Ra',
        'VS:  T-100.6, HR-105, BP-93/46, RR-16, Sats-98% 3L/NC',
        #'VS - Temp. 98.5F, BP115/65 , HR103 , R16 , 96O2-sat % RA',
        'Vitals: Temp 100.2 HR 72 BP 184/56 RR 16 sats 96% on RA',
        'PHYSICAL EXAM: O: T: 98.8 BP: 123/60   HR:97    R 16  O2Sats100%',
        'VS before transfer were 85 BP 99/34 RR 20 SpO2% 99/bipap 10/5 50%.',
        'Initial vs were: T 98 P 91 BP 122/63 R 20 O2 sat 95%RA.',
        'Initial vitals were HR 106 BP 88/56 RR 20 O2 Sat 85% 3L.',
        'Initial vs were: T=99.3 P=120 BP=111/57 RR=24 POx=100%.',        
        'At transfer vitals were HR=120 BP=109/44 RR=29 POx=93% on 8L FM.',
        "Vitals as follows: BP 120/80 HR 60-80's RR  SaO2 96% 6L NC.",
        'Vital signs were T 97.5 HR 62 BP 168/60 RR 18 95% RA.',
        'T 99.4 P 160 R 56 BP 60/36 mean 44 O2 sat 97% Wt 3025 grams ',
        'HR 107 RR 28 and SpO2 91% on NRB.',
        'BP 143/79 RR 16 and O2 sat 92% on room air and 100% on 3 L/min nc',
        'RR: 28 BP: 84/43 O2Sat: 88 O2 Flow: 100 (Non-Rebreather).',
        'Vitals were T 97.1 HR 76 BP 148/80 RR 25 SpO2 92%/RA.',
        'Tm 96.4, BP= 90-109/49-82, HR= paced at 70, RR= 24, O2 sat= 96% on 4L',
        # what does 50% flowmask mean? 'Vitals were T 97.1 BP 80/70 AR 80 RR 24 O2 sat 70% on 50% flowmask',
        # what does PS 18/10 mean? 'HR 84 bpm RR 13 bpm O2: 100% PS 18/10 FiO2 40%',
        'BP 91/50, HR 63, RR 12, satting 95% on trach mask',
        'O2 sats 98-100%',
        'Pt. desating to 88%',
        'spo2 difficult to monitor but appeared to remain ~ 96-100% on bipap 8/5',
        'using BVM w/ o2 sats 74% on 4L',
        
        # #'desat to 83 with 100% face tent and 4 l n.c.',

        # 'Ventilator mode: CMV/ASSIST/AutoFlow   Vt (Set): 550 (550 - 550) mL ' +\
        # 'Vt (Spontaneous): 234 (234 - 234) mL   RR (Set): 16 ' +\
        # 'RR (Spontaneous): 0   PEEP: 5 cmH2O   FiO2: 70%   RSBI: 140 ' +\
        # 'PIP: 25 cmH2O   SpO2: 98%   Ve: 14.6 L/min',

        # 'Vt (Spontaneous): 608 (565 - 793) mL   PS : 15 cmH2O   ' +\
        # 'RR (Spontaneous): 27   PEEP: 10 cmH2O   FiO2: 50%   '    +\
        # 'RSBI Deferred: PEEP > 10   PIP: 26 cmH2O   SpO2: 99%   ' +\
        # 'ABG: 7.41/39/81/21/0   Ve: 17.4 L/min   PaO2 / FiO2: 164',
        
        # 'Respiratory: Vt (Set): 600 (600 - 600) mL   Vt (Spontaneous): 743 ' +\
        # '(464 - 816) mL  PS : 5 cmH2O   RR (Set): 14   RR (Spontaneous): 19' +\
        # ' PEEP: 5 cmH2O   FiO2: 50%   RSBI: 49   PIP: 11 cmH2O   '           +\
        # 'Plateau: 20 cmH2O   SPO2: 99%   ABG: 7.34/51/109/25/0   '           +\
        # 'Ve: 10.3 L/min   PaO2 / FiO2: 218',
        
        # 'an oxygen saturation of 96% on 2 liters',

        # 'the respiratory rate was 21,\nand the oxygen saturation was 80% ' +\
        # 'to 92% on a 100% nonrebreather mask',

        # 'temperature 100 F., orally.  O2 saturation 98% on room air',

        # 'o2 sat 93% on 5l',
        # 'O2 sat were 90-95.',
        # 'O2 sat then decreased again to 89 - 90% while on 50% face tent',
        # 'episodes of desaturation overnoc to O2 Sat 80%, on RBM & O2 NC 8L',
    ]

    for i, sentence in enumerate(SENTENCES):
        print('[{0:2d}]: {1}'.format(i, sentence))
        result = run(sentence)
        #print(result)

        data = json.loads(result)
        for d in data:
            for k,v in d.items():
                print('\t\t{0} => {1}'.format(k, v))
            
        
        # print('\t      o2_sat: {0}'.format(o2_sat))
        # print('\t        pao2: {0}'.format(pao2))
        # print('\t        fio2: {0}'.format(fio2))
        # print('\tp_to_f_ratio: {0}'.format(p_to_f_ratio))
        # print('\t   flow rate: {0}'.format(flow_rate))
        # print('\t      device: {0}'.format(device))
        # print('\t       value: {0}'.format(value))
        # print('\t      value2: {0}'.format(value2))


    
###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)
