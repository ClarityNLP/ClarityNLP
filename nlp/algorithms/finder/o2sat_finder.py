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
(From the supplemental appendix to:
    Vlaar A, Toy P, Fung M, et. al. "A consensus redefinition of transfusion-
    related acute lung injury", Transfusion (59) 2465-2476, 2019.)

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
FiO2 = 0.20 + (0.04) * (flow_rate_l_per_min-1), 1 <= flow_rate <= 10


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
    # for interactive testing only
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

# values for the 'condition' field in the result namedtuple
STR_O2_APPROX         = 'APPROX'
STR_O2_LT             = 'LESS_THAN'
STR_O2_LTE            = 'LESS_THAN_OR_EQUAL'
STR_O2_GT             = 'GREATER_THAN'
STR_O2_GTE            = 'GREATER_THAN_OR_EQUAL'
STR_O2_EQUAL          = 'EQUAL'
STR_O2_RANGE          = 'RANGE'

O2_TUPLE_FIELDS = [
    'sentence',
    'text',
    'start',
    'end',
    'pao2',             # [mmHg]
    'pao2_est',         # estimated from o2_sat
    'fio2',             # [%]
    'fio2_est',         # estimated from flow_rate
    'p_to_f_ratio',
    'p_to_f_ratio_est', # estimated
    'flow_rate',        # [L/min]
    'device',
    'condition',        # STR_APPROX, STR_LT, etc.
    'value',            # [%] (O2 saturation value)
    'value2',           # [%] (second O2 saturation value for ranges)
]
O2Tuple = namedtuple('O2Tuple', O2_TUPLE_FIELDS)


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 1
_MODULE_NAME   = 'o2sat_finder.py'

# set to True to enable debug output
_TRACE = False

# connectors between portions of the regexes below; either symbols or words
_str_cond = r'(?P<cond>(~=|>=|<=|[-/:<>=~\s.@^]+|\s[a-z\s]+)+)?'

# words, possibly hyphenated or abbreviated, nongreedy match
_str_words = r'([-a-z\s./:~]+?)?'

# wordy relationships
_str_equal     = r'\b(equal|eq\.?)'
_str_approx    = r'(~=|~|\b(approx\.?|approximately|near(ly)?|about))'
_str_less_than = r'\b(less\s+than|lt\.?|up\s+to|under|below)'
_str_gt_than   = r'\b(greater\s+than|gt\.?|exceed(ing|s)|above|over)'

_str_lt  = r'(<|' + _str_less_than + r')'
_str_lte = r'(<=|</=|' + _str_less_than + r'\s+or\s+' + _str_equal + r')'
_str_gt  = r'(>|' + _str_gt_than + r')'
_str_gte = r'(>=|>/=|' + _str_gt_than + r'\s+or\s+' + _str_equal + r')'

_regex_lt     = re.compile(_str_lt,     re.IGNORECASE)
_regex_lte    = re.compile(_str_lte,    re.IGNORECASE)
_regex_gt     = re.compile(_str_gt,     re.IGNORECASE)
_regex_gte    = re.compile(_str_gte,    re.IGNORECASE)
_regex_approx = re.compile(_str_approx, re.IGNORECASE)

# O2 saturation header
# do not capture 'sat up', such as 'sat up in bed'
_str_o2_sat_hdr = r'(?<![a-z])(spo2|sao2|pox|so2|'                    +\
    r'(o2|oxygen)[-\s]?saturation|o2[-\s]sat\.?s?|satting|o2sats?|'   +\
    r'sat\.?s|sat(?!\sup)|pulse ox|o2(?!\s?flow)|desatt?ing|desat\.?)\s?%?'

_str_units = r'\(?(percent|pct\.?|%|mmHg)\)?'

# o2 saturation value
_str_o2_val_range = r'\b(was|from)?\s?(?P<val1>\d\d?)(\s?' + _str_units + r')?' +\
    r'(\s?(\-|to)\s?)(?P<val2>(100|\d\d?))(\s?' + _str_units + r')?'
_regex_o2_val_range = re.compile(_str_o2_val_range, re.IGNORECASE)

# prevent capture of ages, such as '\d+ years old', '\d+yo', etc.
_str_o2_value = r'(?<!o)(?P<val>(100|\d\d?)(?![Ly])(?! y))(\s?' + _str_units + r')?'
_str_o2_val = r'(' + _str_o2_val_range + r'|' + _str_o2_value + r')'

# O2 flow rate in L/min
_str_flow_rate = r'(?P<flow_rate>\d+)\s?(Liters|L)(/min\.?|pm)?'

# devices and related acronyms
#         RA : right atrial, usually via fiberoptic oximetry
#         FM : face mask
#        BVM : bag valve mask
#        RBM : rebreather mask
#  venti mask: Venturi mask
#       bipap: bilevel positive airway pressure

# sometimes see NC called "O2 NC"; also called "nasal prongs", abbrev NP
# do not capture 'HEENT:NC', in which case the 'NC' means 'normocephalic'
_str_device_nc  = r'(?P<nc>(O2\s)?'                                   +\
    r'(?<!HEENT:)(?<!HEENT :)(?<!HEENT: )(?<!HEENT : )'               +\
    r'(n\.?[cp]\.?|n/c|(nas[ae]l[-\s]?)?(cannula|prongs?))(?![a-z]))'
_str_device_nrb = r'(?P<nrb>(\d+%?\s)?(n\.?r\.?b\.?|'                 +\
    r'non[-\s]?rebreather(\smask)?)(?![a-z]))'
_str_device_ra  = r'(?P<ra>(?<![a-z])(r\.?a\.?|radial[-\s]?artery)(?![a-z]))'
_str_device_venturi = r'(?P<venturi>((venturi|venti)[-\s]?mask|'      +\
    r'\d+\s?%\s?(venturi|venti)[-\s]?mask)(?![a-z]))'
_str_device_bvm = r'(?P<bvm>(b\.?v\.?m\.?|bag[-\s]valve\smask))'
_str_device_bipap = r'(?P<bipap>(bipap\s\d+/\d+\s?(with\s\d+L|\d+%)|' +\
    r'bipap(\s\d+/\d+)?))'
# vent(?!ilation))
_str_device_mask = r'(?P<mask>(f\.?m\.?|rbm|'                         +\
    r'[a-z]+\s?([a-z]+\s?)?[-\s]?mask|'                               +\
    r'(ventilator|vent(?![a-z]))(?!\s(setting|mode))|'                +\
    r'\d+%\s?[a-z]+[-\s]?mask|mask))'
_str_device_tent = r'(?P<tent>\d+\s?%\s?face\s?tent)'
# face tent with a nasal cannula; flow rate prior to NC
_str_device_tent_nc = r'(?P<tent2>\d+\s?%\s?face\s?tent)[a-z\s]+'     +\
    r'(?P<flow_rate2>\d+)\s?(Liters|L)(/min\.?)?\s?'                  +\
    r'(?P<nc2>(O2\s)?(n\.?c\.?|nasal[-\s]?cannula|cannula))'
# face tent with a nasal cannula; flow rate after NC
_str_device_tent_nc2 = r'(?P<tent3>\d+\s?%\s?face\s?tent)[a-z\s]+'    +\
    r'(?P<nc3>(O2\s)?(n\.?c\.?|nasal[-\s]?cannula|cannula))[a-z\s]+'  +\
    r'(?P<flow_rate3>\d+)\s?(Liters|L)(/min\.?)?\s?'
_str_device_air = r'(?P<air>(?<![a-z])(room[-\s]air|air))'
_str_device_nasocath = r'(?P<nasocath>(naso[-\.\s]?(pharyngeal)?'     +\
    r'[-\s]?cath\.?(eter)?))'

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
# each is mapped to an FiO2 conversion function taking O2 flow_rate as arg
_DEVICE_NC  = 'nc'
_DEVICE_NRB = 'nrb'
_DEVICE_RA  = 'ra'
_DEVICE_VENTURI = 'venturi'
_DEVICE_BVM = 'bvm'
_DEVICE_BIPAP = 'bipap'
_DEVICE_MASK = 'mask'
_DEVICE_AIR = 'air'
_DEVICE_NASOCATH = 'nasocath'
_DEVICE_TENT = 'tent'
_DEVICE_TENT2 = 'tent2'

# devices that use a mask with possibly a stated percentage FiO2
_DEVICES_WITH_FIO2_PCT = {
    _DEVICE_NRB, _DEVICE_VENTURI, _DEVICE_BIPAP, _DEVICE_MASK, _DEVICE_TENT
}

# maps a device to an FiO2 conversion/estimation function
_DEVICE_MAP = {
    _DEVICE_NC       : _to_fio2_nc,
    _DEVICE_NRB      : _to_fio2_nrb,
    _DEVICE_RA       : None,
    _DEVICE_VENTURI  : _to_fio2_venturi,
    _DEVICE_BVM      : None,
    _DEVICE_BIPAP    : None,
    _DEVICE_MASK     : _to_fio2_mask,
    _DEVICE_AIR      : None,
    _DEVICE_NASOCATH : _to_fio2_nasocath,
    _DEVICE_TENT     : None,
    _DEVICE_TENT2    : None,
}

# master regex for all devices
_str_device = r'\(?(o2\s?delivery\sdevice\s?:\s?)?(?P<device>' +\
    r'(' + _str_device_nc + r')'       + r'|' +\
    r'(' + _str_device_nrb + r')'      + r'|' +\
    r'(' + _str_device_ra + r')'       + r'|' +\
    r'(' + _str_device_venturi + r')'  + r'|' +\
    r'(' + _str_device_bvm + r')'      + r'|' +\
    r'(' + _str_device_bipap + r')'    + r'|' +\
    r'(' + _str_device_mask + r')'     + r'|' +\
    r'(' + _str_device_tent_nc + r')'  + r'|' +\
    r'(' + _str_device_tent_nc2 + r')' + r'|' +\
    r'(' + _str_device_tent + r')'     + r'|' +\
    r'(' + _str_device_air + r')'      + r'|' +\
    r'(' + _str_device_nasocath + r'))'       +\
    r'\)?'
_regex_device = re.compile(_str_device, re.IGNORECASE)

# character used to encode the device
_DEVICE_ENC_CHAR = '|'

# finds "spo2: 98% on 2L NC" and similar
_str0 = _str_o2_sat_hdr + _str_cond + _str_o2_val           +\
    _str_words + _str_flow_rate + _str_words + _str_device
_regex0 = re.compile(_str0, re.IGNORECASE)

# finds "spo2: 98%/NC" and similar
_str1 = _str_o2_sat_hdr + _str_cond + _str_o2_val + _str_words + _str_device
_regex1 = re.compile(_str1, re.IGNORECASE)

# finds "spo2: 98%/3L" and similar
_str2= _str_o2_sat_hdr + _str_cond + _str_o2_val + _str_words + _str_flow_rate
_regex2 = re.compile(_str2, re.IGNORECASE)

# finds "spo2=98%" and similar
_str3 = _str_o2_sat_hdr + _str_cond + _str_o2_val
_regex3 = re.compile(_str3, re.IGNORECASE)

# finds "98% RA" and similar (value to the left)
_str4 = r'(?<![-:=/\d])(?<![-:=/]\s)(?<!MAP [<>])' + _str_o2_val +\
    r'(' + _str_o2_sat_hdr + r')?' + _str_words                  +\
    r'(' + _str_flow_rate + _str_words + r')?' + _str_device
_regex4 = re.compile(_str4, re.IGNORECASE)

# like the first regex, but finds flow rate after device
_str5 = _str_o2_sat_hdr + _str_cond + _str_o2_val + _str_words +\
    _str_device + _str_words + _str_flow_rate
_regex5 = re.compile(_str5, re.IGNORECASE)

# finds device prior to O2 saturation header
_str6 = _str_device + _str_words + _str_o2_sat_hdr + _str_cond + _str_o2_val +\
    r'(' + _str_words + _str_flow_rate + r')?'
_regex6 = re.compile(_str6, re.IGNORECASE)

# finds flow rate prior to device and O2 saturation header
_str7 = _str_flow_rate + _str_words + _str_device + _str_words +\
    _str_o2_sat_hdr + _str_cond + _str_o2_val
_regex7 = re.compile(_str7, re.IGNORECASE)

# finds O2 header then device then sat value
_str8 = _str_o2_sat_hdr + _str_words + r'(' + _str_flow_rate + r')?' +\
    _str_device + _str_cond + _str_o2_val
_regex8 = re.compile(_str8, re.IGNORECASE)

_SAO2_REGEXES = [
    _regex0,
    _regex1,
    _regex2,
    _regex3,
    _regex4,
    _regex5,
    _regex6,
    _regex7,
    _regex8,
]

# o2 partial pressure (prevent captures of 'PaO2 / FiO2')
_str_pao2 = r'\b(pao2|partial pressure of (oxygen|o2))(?!/)(?! /)' +\
    r'(' + _str_cond+ r')?' +  r'(?P<val>\d+)'
_regex_pao2 = re.compile(_str_pao2, re.IGNORECASE)

# fraction of inspired oxygen (prevent capture of 'pao2 / fio2');
# case 1: value follows the 'fio2' string
# The Earth's atmosphere is ~21% O2, but sometimes the respiratory literature
# uses 20% instead. So 20% is the min acceptable value in these regexes.
#
# also: 'Fi02' has been seen in MIMIC (note the number '0', not the letter 'O')
_str_fio2_1 = r'\b(?<!/)(?<!/\s)(fi[o0]2|o2\sflow)' +\
    r'(' + _str_cond + r')?' + r'(?P<val>(100|[2-9][0-9]))\s?%?'
_regex_fio2_1 = re.compile(_str_fio2_1, re.IGNORECASE)

# case 2: value precedes the 'fio2' string
_str_fio2_2 = r'(?<!\d)(?P<val>(100|[2-9][0-9]))\s?%?\s?(fi[o0]2|o2\sflow)'
_regex_fio2_2 = re.compile(_str_fio2_2, re.IGNORECASE)

# case 3: FiO2 <words> <value>
_str_fio2_3 = r'\b(?<!/)(?<!/\s)(fi[o0]2|o2\sflow)' + _str_words +\
    r'(?P<val>(100|[2-9][0-9]))\s?%?'
_regex_fio2_3 = re.compile(_str_fio2_3, re.IGNORECASE)

_FIO2_REGEXES = [
    _regex_fio2_1,
    _regex_fio2_2,
    _regex_fio2_3,
]

# p/f ratio
_str_pf_ratio = r'\b(pao2|p)\s?/\s?(fio2|f)(\s?ratio)?' +\
    r'(' + _str_cond + r')?' + r'(?P<val>\d+(\.\d+)?)'
_regex_pf_ratio = re.compile(_str_pf_ratio, re.IGNORECASE)

# convert SpO2 to PaO2
# https://www.intensive.org/epic2/Documents/Estimation%20of%20PO2%20and%20FiO2.pdf
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

# The minimum acceptable value for SpO2. Some Covid-19 patients have had O2
# sats this low. Some hemoglobinopathies can cause SpO2 readings in the 70%
# range. See this article, for instance:
#     https://www.karger.com/Article/FullText/451030
_MIN_SPO2_PCT = 50


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

    # replace ' w/ ' with ' with '
    sentence = re.sub(r'\sw/\s', ' with ', sentence)
    
    # replace selected chars with whitespace
    sentence = re.sub(r'[,&]', ' ', sentence)

    # collapse repeated whitespace
    sentence = re.sub(r'\s+', ' ', sentence)

    return sentence


###############################################################################
def _cond_to_string(str_cond):
    """
    Determine the relationship between the query term and the value.
    """

    if _regex_approx.search(str_cond):
        result = STR_O2_APPROX
    elif _regex_lte.search(str_cond):
        result = STR_O2_LTE
    elif _regex_gte.search(str_cond):
        result = STR_O2_GTE
    elif _regex_lt.search(str_cond):
        result = STR_O2_LT
    elif _regex_gt.search(str_cond):
        result = STR_O2_GT
    else:
        result = STR_O2_EQUAL
    
    return result


###############################################################################
def _estimate_fio2(flow_rate, device):
    """
    Estimate the FiO2 value (fraction of inspired oxygen, as a percentage)
    from the given flow rate in L/min and device.

    The device argument is encoded as follows: 'device_string|device_type',
    where 'device_type' is a regex group name.
    """

    # caller should have already checked this condition
    assert device is not None
    
    fio2_est = EMPTY_FIELD
    
    if _TRACE:
        print('Calling _estimate_fio2...')
        print('\tflow_rate: {0}'.format(flow_rate))
        print('\t   device: {0}'.format(device))
    
    device_str, device_type = device.split('|')
    
    if _TRACE:
        print('\t   device_str: {0}'.format(device_str))
        print('\t  device_type: {0}'.format(device_type))
        
    if device_type not in _DEVICE_MAP:
        if _TRACE: print('\tdevice type not in device map')
        return device_str, EMPTY_FIELD

    # can get FiO2 from stated percentage of nonrebreather mask
    if device_type in _DEVICES_WITH_FIO2_PCT:
        match = re.search(r'(?P<pct>\d+)\s?%', device_str)
        if match:
            fio2_est = float(match.group('pct'))
    
    if fio2_est is None:
        if flow_rate is None:
            if _TRACE: print('\t  no flow rate available, exiting...')
            return device_str, EMPTY_FIELD
        else:
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
            match_text = match.group().strip()

            # Special case for regex index 6. Prevent a match on the bracketed
            # portion of something like this:
            #       "<RA. Pt was initially satting 95%> on NRB.".
            #
            # In other words, the sentence segmentation should have started
            # a new sentence at "Pt", in which case the match would be correct.
            special_match = re.search(r'\.\s[A-Z][a-z]+', match_text)
            if special_match:
                continue
            
            start = match.start()
            end   = start + len(match_text)
            candidates.append(overlap.Candidate(start, end, match_text, regex,
                                                other=match))
            if _TRACE:
                print('[{0:2}]: [{1:3}, {2:3})\tMATCH TEXT: ->{3}<-'.
                      format(i, start, end, match_text))
                print('\tmatch.groupdict entries: ')
                for k,v in match.groupdict().items():
                    print('\t\t{0} => {1}'.format(k,v))
                

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

    # if two overlap exactly, keep candidate with longer device string
    prev_start = candidates[0].start
    prev_end = candidates[0].end
    delete_index = None
    for i in range(1, len(candidates)):
        c = candidates[i]
        if c.start == prev_start and c.end == prev_end:
            if _TRACE:
                print('\tCandidates at indices {0} and {1} have ' \
                      'identical overlap'.format(i-1, i))
            # the regex match object is stored in the 'other' field
            matchobj = c.other
            matchobj_prev = candidates[i-1].other
            if 'device' in matchobj.groupdict() and 'device' in matchobj_prev.groupdict():
                device = matchobj.group('device')
                device_prev = matchobj_prev.group('device')
                if device is not None and device_prev is not None:
                    len_device = len(device)
                    len_device_prev = len(device_prev)
                    if _TRACE:
                        print('\t\tdevice string for index {0}: {1}'.
                              format(i-1, device_prev))
                        print('\t\tdevice string for index {0}: {1}'.
                              format(i, device))
                    if len_device > len_device_prev:
                        delete_index = i-1
                    else:
                        delete_index = i
                    if _TRACE:
                        print('\t\t\tdelete_index: {0}'.format(delete_index))
                    break
        prev_start = c.start
        prev_end = c.end

    if delete_index is not None:
        del candidates[delete_index]
        if _TRACE:
            print('\tRemoved candidate at index {0} with shorter device string'.
                  format(delete_index))

    # remove any that are proper substrings of another, exploiting the fact
    # that the candidate list is sorted in decreasing order of length
    discard_set = set()
    for i in range(1, len(candidates)):
        start = candidates[i].start
        end   = candidates[i].end
        for j in range(0, i):
            prev_start = candidates[j].start
            prev_end   = candidates[j].end
            if start >= prev_start and end <= prev_end:
                discard_set.add(i)
                if _TRACE:
                    print('\t[{0:2}] is a substring of [{1}], discarding...'.
                          format(i, j))
                break

    survivors = []
    for i in range(len(candidates)):
        if i not in discard_set:
            survivors.append(candidates[i])

    candidates = survivors
        
    # Check for any 'complete' candidates. A complete candidate has an O2
    # saturation value, a device, and a flow rate. If one or more of these,
    # restrict consideration to these only.

    complete_candidates = []
    for c in candidates:
        # match object stored in the 'other' field
        gd = c.other.groupdict()
        count = 0
        if 'val' in gd and gd['val'] is not None:
            count += 1
        if 'flow_rate' in gd and gd['flow_rate'] is not None:
            count += 1
        if 'flow_rate2' in gd and gd['flow_rate2'] is not None:
            count += 1
        if 'flow_rate3' in gd and gd['flow_rate3'] is not None:
            count += 1
        if 'device' in gd and gd['device'] is not None:
            count += 1
            # room air will not have a flow rate, but it is nontheless complete
            device_str = gd['device']
            if -1 != device_str.find(' air'):
                count += 1
        if count >= 3:
            complete_candidates.append(c)
            if _TRACE:
                print('\tFound complete candidate "{0}"'.format(c.match_text))

    if len(complete_candidates) > 0:
        candidates = complete_candidates

        # Now find the maximum number of non-overlapping candidates. This is an
        # instance of the equal-weight interval scheduling problem, which has an
        # optimal greedy solution. See the book "Algorithm Design" by Kleinberg and
        # Tardos, ch. 4.

        # sort candidates in increasing order of their END points
        candidates = sorted(candidates, key=lambda x: x.end)

        pruned_candidates = [candidates[0]]
        prev_end = pruned_candidates[0].end
        for i in range(1, len(candidates)):
            c = candidates[i]
            if c.start >= prev_end:
                pruned_candidates.append(c)
                prev_end = c.end

    else:
        # run the usual overlap resolution
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
def _encode_device(k, v):
    """
    Encode a device string as v|k, where the string 'k' is a key in
    _DEVICE_MAP, and 'v' is the value for that device extracted from the text.
    """

    # strip the leading prepositions, if any
    if v.startswith('on '):
        v = v[3:]
    elif v.startswith('on a '):
        v = v[5:]
    elif v.startswith('with '):
        v = v[5:]

    device_type = k
    # encode as 'v|k'
    device_str = '{0}{1}{2}'.format(v.strip(), _DEVICE_ENC_CHAR, k)
    return device_type, device_str
    

###############################################################################
def _erase(sentence, candidates):
    """
    Erase all candidate matches from the sentence. Only substitute a single
    whitespace for the region, since this is performed on the previously
    cleaned sentence.
    """

    new_sentence = sentence
    for c in candidates:
        start = c.start
        end = c.end
        s1 = new_sentence[:start]
        s2 = ' '
        s3 = new_sentence[end:]
        new_sentence = s1 + s2 + s3

    # collapse repeated whitespace, if any
    new_sentence = re.sub(r'\s+', ' ', new_sentence)
        
    return new_sentence


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
    if _TRACE:
        print('SaO2 candidates: ')
    sao2_candidates = _regex_match(cleaned_sentence, _SAO2_REGEXES)

    # erase these matches from the sentence
    remaining_sentence = _erase(cleaned_sentence, sao2_candidates)
    
    # only a single match for pao2, fio2, p_to_f_ratio

    if _TRACE:
        print('PaO2 candidates: ')
    pao2 = EMPTY_FIELD
    pao2_candidates = _regex_match(remaining_sentence, [_regex_pao2])
    if len(pao2_candidates) > 0:
        # take the first match
        match_obj = pao2_candidates[0].other
        pao2, pao2_2 = _extract_values(match_obj)

    # erase these matches also
    remaining_sentence = _erase(remaining_sentence, pao2_candidates)

    if _TRACE:
        print('FiO2 candidates: ')
    fio2 = EMPTY_FIELD
    fio2_candidates = _regex_match(remaining_sentence, _FIO2_REGEXES)
    if len(fio2_candidates) > 0:
        # take the first match
        match_obj = fio2_candidates[0].other
        fio2, fio2_2 = _extract_values(match_obj)
        # convert fio2 to a percentage
        if fio2 < 1.0:
            fio2 *= 100.0

    # erase these matches
    remaining_sentence = _erase(remaining_sentence, fio2_candidates)
            
    if _TRACE:
        print('PaO2/FiO2 candidates: ')
    p_to_f_ratio = EMPTY_FIELD
    pf_candidates = _regex_match(cleaned_sentence, [_regex_pf_ratio])
    if len(pf_candidates) > 0:
        # take the first match
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
        tent2            = EMPTY_FIELD
        flow_rate2       = EMPTY_FIELD
        nc2              = EMPTY_FIELD
        tent3            = EMPTY_FIELD
        flow_rate3       = EMPTY_FIELD
        nc3              = EMPTY_FIELD
        condition        = STR_O2_EQUAL

        for k,v in match.groupdict().items():
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
                device_type, device = _encode_device(k, v)
            elif 'cond' == k:
                condition = _cond_to_string(v)
            elif 'flow_rate2' == k:
                flow_rate2 = float(v)
            elif 'flow_rate3' == k:
                flow_rate3 = float(v)
            elif 'nc2' == k:
                nc2 = v
            elif 'nc3' == k:
                nc3 = v

        # check oxygen saturation for valid range
        if o2_sat < _MIN_SPO2_PCT:
            continue

        # if no device found, check device regex independently
        if EMPTY_FIELD == device:
            device_candidates = _regex_match(cleaned_sentence, [_regex_device])
            if len(device_candidates) > 0:
                # take the first match
                for k,v in device_candidates[0].other.groupdict().items():
                    if v is None:
                        continue
                    if k in _DEVICE_MAP:
                        device_type, device = _encode_device(k,v)
                
        # compute estimated FiO2 from flow rate and device
        if EMPTY_FIELD == fio2 and device is not None:
            device, fio2_est = _estimate_fio2(flow_rate, device)

        # handle face tent with nasal cannula
        if EMPTY_FIELD == flow_rate and EMPTY_FIELD == fio2_est:
            if EMPTY_FIELD != flow_rate2 and EMPTY_FIELD != nc2:
                device, fio2_est = _estimate_fio2(flow_rate2,'{0}|{1}'.
                                                  format(_DEVICE_NC, _DEVICE_NC))
            elif EMPTY_FIELD != flow_rate3 and EMPTY_FIELD != nc3:
                device, fio2_est = _estimate_fio2(flow_rate3, '{0}|{1}'.
                                                  format(_DEVICE_NC, _DEVICE_NC))

        # unencode the device if no fio2 estimate could be performed
        if EMPTY_FIELD != device:
            device = device.split(_DEVICE_ENC_CHAR)[0].strip()
            if 'none' == device.lower():
                device = EMPTY_FIELD
            
        # Check for the situation of a stated p_to_f, a stated fio2, and no
        # pao2. In this case compute the pao2 value from the p_to_f and fio2
        # values.
        if EMPTY_FIELD != p_to_f_ratio and EMPTY_FIELD != fio2 and EMPTY_FIELD == pao2:
            pao2_est = p_to_f_ratio * 0.01 * fio2;

        # compute estimated PaO2 from SpO2
        if EMPTY_FIELD == pao2 and EMPTY_FIELD == pao2_est:
            pao2_est = _estimate_pao2(o2_sat)
            
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
        if EMPTY_FIELD == p_to_f_ratio and pao2_val != EMPTY_FIELD and fio2_val != EMPTY_FIELD:
                p_to_f_ratio_est = pao2_val / (0.01 * fio2_val)

        # dry air contains about 20.95% O2, round to 21%
        if fio2_val is None and pao2_val is not None and device is not None:
            if -1 != device.find(_DEVICE_AIR):
                fio2_est = 21
                p_to_f_ratio_est = pao2_val / 0.21

        # round estimates to nearest integer, does not have to be exact
        if EMPTY_FIELD != pao2_est:
            pao2_est = int(pao2_est + 0.5)
        if EMPTY_FIELD != fio2_est:
            fio2_est = int(fio2_est + 0.5)
        if EMPTY_FIELD != p_to_f_ratio_est:
            p_to_f_ratio_est = int(p_to_f_ratio_est + 0.5)

        # set the condition to RANGE if two values were found
        if EMPTY_FIELD != value and EMPTY_FIELD != value2:
            condition = STR_O2_RANGE
            
        o2_tuple = O2Tuple(
            sentence         = cleaned_sentence,
            text             = pc.match_text,
            start            = pc.start,
            end              = pc.end,
            flow_rate        = flow_rate,
            device           = device,
            condition        = condition,
            value            = value,
            value2           = value2,
            pao2             = pao2,
            pao2_est         = pao2_est,
            fio2             = fio2,
            fio2_est         = fio2_est,
            p_to_f_ratio     = p_to_f_ratio,            
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
        'VS - Temp. 98.5F, BP115/65 , HR103 , R16 , 96O2-sat % RA',
        'Vitals: Temp 100.2 HR 72 BP 184/56 RR 16 sats 96% on RA',
        'PHYSICAL EXAM: O: T: 98.8 BP: 123/60   HR:97    R 16  O2Sats100%',
        'VS before transfer were 85 BP 99/34 RR 20 SpO2% 99/bipap 10/5 50%.',
        'Initial vs were: T 98 P 91 BP 122/63 R 20 O2 sat 95%RA.',
        'Initial vitals were HR 106 BP 88/56 RR 20 O2 Sat 85% 3L.',
        'Initial vs were: T=99.3 P=120 BP=111/57 RR=24 POx=100%.',        
        "Vitals as follows: BP 120/80 HR 60-80's RR  SaO2 96% 6L NC.",
        'Vital signs were T 97.5 HR 62 BP 168/60 RR 18 95% RA.',
        'T 99.4 P 160 R 56 BP 60/36 mean 44 O2 sat 97% Wt 3025 grams ',
        'HR 107 RR 28 and SpO2 91% on NRB.',
        'BP 143/79 RR 16 and O2 sat 92% on room air and 100% on 3 L/min nc',
        'RR: 28 BP: 84/43 O2Sat: 88 O2 Flow: 100 (Non-Rebreather).',
        'Vitals were T 97.1 HR 76 BP 148/80 RR 25 SpO2 92%/RA.',
        'Tm 96.4, BP= 90-109/49-82, HR= paced at 70, RR= 24, O2 sat= 96% on 4L',
        'Vitals were T 97.1 BP 80/70 AR 80 RR 24 O2 sat 70% on 50% flowmask',
        'HR 84 bpm RR 13 bpm O2: 100% PS 18/10 FiO2 40%',
        'BP 91/50, HR 63, RR 12, satting 95% on trach mask',
        'O2 sats 98-100%',
        'Pt. desating to 88%',
        'spo2 difficult to monitor but appeared to remain ~ 96-100% on bipap 8/5',
        'using BVM w/ o2 sats 74% on 4L',
        
        'desat to 83 with 100% face tent and 4 l n.c.',
        'desat to 83 with 100% face tent and nc of approximately 4l',

        'Ventilator mode: CMV/ASSIST/AutoFlow   Vt (Set): 550 (550 - 550) mL ' +\
        'Vt (Spontaneous): 234 (234 - 234) mL   RR (Set): 16 ' +\
        'RR (Spontaneous): 0   PEEP: 5 cmH2O   FiO2: 70%   RSBI: 140 ' +\
        'PIP: 25 cmH2O   SpO2: 98%   Ve: 14.6 L/min',

        'Vt (Spontaneous): 608 (565 - 793) mL   PS : 15 cmH2O   ' +\
        'RR (Spontaneous): 27   PEEP: 10 cmH2O   FiO2: 50%   '    +\
        'RSBI Deferred: PEEP > 10   PIP: 26 cmH2O   SpO2: 99%   ' +\
        'ABG: 7.41/39/81/21/0   Ve: 17.4 L/min   PaO2 / FiO2: 164',

        'Respiratory: Vt (Set): 600 (600 - 600) mL   Vt (Spontaneous): 743 ' +\
        '(464 - 816) mL  PS : 5 cmH2O   RR (Set): 14   RR (Spontaneous): 19' +\
        ' PEEP: 5 cmH2O   FiO2: 50%   RSBI: 49   PIP: 11 cmH2O   '           +\
        'Plateau: 20 cmH2O   SPO2: 99%   ABG: 7.34/51/109/25/0   '           +\
        'Ve: 10.3 L/min   PaO2 / FiO2: 218',
        
        'an oxygen saturation of 96% on 2 liters',
        'an oxygen saturation of 96% on 2 liters with a nasal cannula',
        
        'the respiratory rate was 21,\nand the oxygen saturation was 80% ' +\
        'to 92% on a 100% nonrebreather mask',

        'temperature 100 F., orally.  O2 saturation 98% on room air',

        'o2 sat 93% on 5l',
        'O2 sat were 90-95.',
        'O2 sat then decreased again to 89 - 90% while on 50% face tent',

        'O2sat >93',
        'patient spo2 < 93 % all night',
        'an oxygen saturation ~=90 for prev. 5 hrs',

        'This morning SpO2 values began to improve again able to wean ' +\
        'back peep to 5 SpO2 holding at 94%',
        'O2 sats ^ 96%.',
        'O2 sats ^ back to 96-98%.',
        'O2 sats improving over course of shift and O2 further weaned ' +\
        'to 5lpm nasal prongs: O2 sats 99%.',
        'O2 sats 93-94% on 50% face tent.',
        
        'O2 SATS WERE BELOW 86',
        'O2 sats down to 88',
        'She arrived with B/P 182/80, O2 sats on 100% NRB were 100&.',
        'Plan:  Wean o2 to maintain o2 sats >85%',
        'At start of shift, LS with rhonchi throughout and ' +\
        'O2 sats > 94% on 5  liters.',
        'O2 sats are 92-94% on 3L NP & 91-93% on room air.',
        'Pt. taken off mask ventilation and put on NRM with ' +\
        '6lpm nasal prongs. O2 sats 96%.',
        'Oxygen again weaned in   evening to 6L n.c. while pt ' +\
        'eating dinner O2 sats 91-92%.',
        
        'episodes of desaturation overnoc to O2 Sat 80%, on RBM & O2 NC 8L',        
        'Pt initially put on nasal prongs, O2 sats low @ 89% and patient changed over to NRM.',
        'O2 at 2 l nc, o2 sats 98 %, resp rate 16-24, Lungs diminished throughout',
        'Changed to 4 liters n/c O2 sats   86%,  increased to 6 liters n/c ~ O2 sats 88%',
        'Pt with trach mask 50% FiO2 and oxygen saturation 98-100%  Lungs rhonchorous.',

        # negative example - don't capture the 'ra' in 'keppra'
        'Upon arrival left pupil blown to 6mm mannitol 100gm given along with keppra.',

        # negative example - don't capture the 'air' in 'repair'
        '78 yo F s/p laparoscopic paraesophageal hernia repair with Collis gastroplasty',
        
        # note the zero '0' character in Fi02
        'Fi02 also weaned to 40% as 02 sat ~100%.',

        'Respiratory support O2 Delivery Device: Nasal cannula SpO2: 95%',
        'found with O2 sat of 65% on RA. Pt was initially satting 95% on NRB',

        # negative example - don't capture the 'NC' in 'HEENT: NC'
        # only capture "SpO2: 98%'
        'SpO2: 98% Physical Examination General: sleeping in NAD easily ' \
        'arousable HEENT: NC',

        '- Pressors for MAP >60 - Mechanical ventilation daily SBT wean vent settings as tolerat',

        "LFT's nl. - IVF boluses to keep MAP >65 - Vanc Zosyn Levofloxacin",

        # fix this - device is NC not 50% face tent
        'Pt has weaned to nasal cannula from 50% face tent and still sats are 95-100%.',
    ]

    for i, sentence in enumerate(SENTENCES):
        print('\n[{0:2d}]: {1}'.format(i, sentence))
        result = run(sentence)
        #print(result)

        data = json.loads(result)
        for d in data:
            for k,v in d.items():
                print('\t\t{0} = {1}'.format(k, v))
            
        
###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)
