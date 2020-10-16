"""
This is an import-only module for textual numbers and related conversions.

These are examples of textual numbers: 'twelve', 'thirty-one', 'two hundred'.
This module finds such text strings and converts them to their
integer equivalents.
"""

import re

_VERSION_MAJOR = 0
_VERSION_MINOR = 1


# textual numbers and related regexes
_str_tnum_digit = r'\b(one|two|three|four|five|six|seven|eight|nine|zero)'
_str_tnum_10s  = r'\b(ten|eleven|twelve|(thir|four|fif|six|seven|eight|nine)teen)'
_str_tnum_20s  = r'\b(twenty[-\s]?' + _str_tnum_digit + r'|twenty)'
_str_tnum_30s  = r'\b(thirty[-\s]?' + _str_tnum_digit + r'|thirty)'
_str_tnum_40s  = r'\b(forty[-\s]?' + _str_tnum_digit + r'|forty)'
_str_tnum_50s  = r'\b(fifty[-\s]?' + _str_tnum_digit + r'|fifty)'
_str_tnum_60s  = r'\b(sixty[-\s]?' + _str_tnum_digit + r'|sixty)'
_str_tnum_70s  = r'\b(seventy[-\s]?' + _str_tnum_digit + r'|seventy)'
_str_tnum_80s  = r'\b(eighty[-\s]?' + _str_tnum_digit + r'|eighty)'
_str_tnum_90s  = r'\b(ninety[-\s]?' + _str_tnum_digit + r'|ninety)'
_str_tnum_100s = _str_tnum_digit + r'[-\s]hundred[-\s](and[-\s])?' +\
    r'(' +\
    _str_tnum_90s + r'|' + _str_tnum_80s + r'|' + _str_tnum_70s + r'|' +\
    _str_tnum_60s + r'|' + _str_tnum_50s + r'|' + _str_tnum_40s + r'|' +\
    _str_tnum_30s + r'|' + _str_tnum_20s + r'|' + _str_tnum_20s + r'|' +\
    _str_tnum_10s + r'|' + _str_tnum_digit +\
    r')?'

_str_tnum_dozen = r'\b((one|two|three|four|five|six|seven|eight|nine)\sdozen)'

# _regex_tnum_digit = re.compile(_str_tnum_digit)
# _regex_tnum_10s   = re.compile(_str_tnum_10s)
# _regex_tnum_20s   = re.compile(_str_tnum_20s)
# _regex_tnum_30s   = re.compile(_str_tnum_30s)
# _regex_tnum_40s   = re.compile(_str_tnum_40s)
# _regex_tnum_50s   = re.compile(_str_tnum_50s)
# _regex_tnum_60s   = re.compile(_str_tnum_60s)
# _regex_tnum_70s   = re.compile(_str_tnum_70s)
# _regex_tnum_80s   = re.compile(_str_tnum_80s)
# _regex_tnum_90s   = re.compile(_str_tnum_90s)
# _regex_tnum_100s  = re.compile(_str_tnum_100s)

_regex_hundreds = re.compile(_str_tnum_digit + r'[-\s]?hundred[-\s]?', re.IGNORECASE)

# used for conversions from tnum to int
_tnum_to_int_map = {
    'one':1, 'two':2, 'three':3, 'four':4, 'five':5, 'six':6, 'seven':7,
    'eight':8, 'nine':9, 'ten':10, 'eleven':11, 'twelve':12, 'thirteen':13,
    'fourteen':14, 'fifteen':15, 'sixteen':16, 'seventeen':17, 'eighteen':18,
    'nineteen':19, 'twenty':20, 'thirty':30, 'forty':40, 'fifty':50,
    'sixty':60, 'seventy':70, 'eighty':80, 'ninety':90,
    'zero':0,
}

# enumerations

# used for conversions from enum to int
_enum_to_int_map = {
    'zeroth':0,
    'first':1, '1st':1, 'second':2, '2nd':2, 'third':3, '3rd':3,
    'fourth':4, '4th':4, 'fifth':5, '5th':5, 'sixth':6, '6th':6,
    'seventh':7, '7th':7, 'eighth':8, '8th':8, 'ninth':9, '9th':9,
    'tenth':10, '10th':10, 'eleventh':11, '11th':11, 'twelfth':12, '12th':12,
    'thirteenth':13, '13th':13, 'fourteenth':14, '14th':14,
    'fifteenth':15, '15th':15, 'sixteenth':16, '16th':16,
    'seventeenth':17, '17th':17, 'eighteenth':18, '18th':18,
    'ninenteenth':19, '19th':19, 'twentieth':20, '20th':20,
    'thirtieth':30, '30th':30, 'fortieth':40, '40th':40,
    'fiftieth':50, '50th':50, 'sixtieth':60, '60th':60,
    'seventieth':70, '70th':70, 'eightieth':80, '80th':80,
    'ninetieth':90, '90th':90,
}

###############################################################################
#                                                                             #
#                            E X P O R T S                                    #
#                                                                             #
#           Everything below this banner is exported by this module.          #
#                                                                             #
###############################################################################

str_tnum = r'(' + _str_tnum_dozen + r'|' +\
    _str_tnum_100s + r'|' + _str_tnum_90s + r'|' + _str_tnum_80s + r'|' +\
    _str_tnum_70s +  r'|' + _str_tnum_60s + r'|' + _str_tnum_50s + r'|' +\
    _str_tnum_40s +  r'|' + _str_tnum_30s + r'|' + _str_tnum_20s + r'|' +\
    _str_tnum_10s +  r'|' + _str_tnum_digit +\
    r')(?![a-z])(?!\-)'

# 'no' is needed for "no new cases" and similar
str_enum = r'(first|second|third|fourth|fifth|sixth|seventh|eighth|' +\
    r'ninth|tenth|eleventh|twelfth|'                                  +\
    r'(thir|four|fif|six|seven|eight|nine)teenth|'                    +\
    r'1[0-9]th|[2-9]0th|[4-9]th|3rd|2nd|1st|'                         +\
    r'(twen|thir|for|fif|six|seven|eigh|nine)tieth)'


###############################################################################
def enum_to_int(str_enum):
    """
    Convert an enumerated count such as 'third' or 'ninenteenth' to an int.
    """

    val = None
    text = str_enum.strip()
    if text in _enum_to_int_map:
        val = _enum_to_int_map[text]

    return val


###############################################################################
def tnum_to_int(str_tnum, debug=False):
    """
    Convert a textual number to an integer. Returns None if number cannot
    be converted, or the actual integer value.
    """

    if debug:
        print('calling _tnum_to_int...')
        print('\tstr_tnum: "{0}"'.format(str_tnum))

    # replace dashes with a space and collapse any repeated spaces
    text = re.sub(r'\-', ' ', str_tnum)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    if debug:
        print('\ttnum after dash replacement: "{0}"'.format(text))

    pos = str_tnum.find('dozen')
    if -1 != pos:
        str_num = str_tnum[:pos-1]
        if str_num.isdigit():
            val = int(str_num) * 12
        elif str_num in _tnum_to_int_map:
            val = _tnum_to_int_map[str_num] * 12
        return val
        
    if text in _tnum_to_int_map:
        return _tnum_to_int_map[text]

    val_h = 0
    val_t = 0
    val_o = 0
    
    # extract hundreds, if any
    match = _regex_hundreds.match(text)
    if match:
        tnum = match.group().split()[0].strip()
        if tnum in _tnum_to_int_map:
            val_h += _tnum_to_int_map[tnum]
            text = text[match.end():].strip()
        else:
            # invalid number
            if debug:
                print('invalid textual number: "{0}"'.format(text))
                return None

    if len(text) > 0:

        # strip 'and', if any
        pos = text.find('and')
        if -1 != pos:
            text = text[pos+3:]
            text = text.strip()

        # extract tens
        words = text.split()
        assert len(words) <= 2
        if 2 == len(words):
            if words[0] not in _tnum_to_int_map or words[1] not in _tnum_to_int_map:
                # invalid number
                if debug:
                    print('invalid textual number: "{0}"'.format(text))
                    return None

            val_t = _tnum_to_int_map[words[0]]
            val_o = _tnum_to_int_map[words[1]]
        else:
            if words[0] not in _tnum_to_int_map:
                # invalid number
                if debug:
                    print('invalid textual number: "{0}"'.format(text))
                    return None
            val_o = _tnum_to_int_map[words[0]]                                       

    # for val_t, a textual number such as "forty-four" will return 40 from the
    # map lookup, so no need to multiply by 10
    return 100*val_h + val_t + val_o
