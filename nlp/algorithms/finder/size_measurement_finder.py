#!/usr/bin/env python3
"""


OVERVIEW:


The code in this module finds size measurements in a sentence and returns a
JSON array containing information on each. A 'size measurement' is a 1D, 2D,
or 3D expression involving lengths, such as:

        3 mm                                    (1D measurement)
        1.2 cm x 3.6 cm                         (2D measurement)
        2 by 3 by 4 mm                          (3D measurement)
        1.1, 2.3, 8.5, and 12.6 cm              (list of lengths)
        1.5 cm2, 4.3 mm3                        (area and volume)
        2.3 - 4.5 cm                            (range)
        1.5 cm craniocaudal x 2.2 cm transverse (measurement with views)

All numeric values are converted to mm, mm2, or mm3 in the JSON results.


OUTPUT:


The set of JSON fields present in the output for each measurement includes:

        text           text of the complete measurement
        start          offset of first char in the matching text
        end            offset of final char in the matching text plus 1

        temporality    indication of when measurement occurred
                       values: 'CURRENT', 'PREVIOUS'
        units          units of the x, y, and z fields
                       values: 'MILLIMETERS', 'SQUARE_MILLIMETERS', 'CUBIC_MILLIMETERS'
        condition      numeric ranges will have this field set to 'RANGE'
                       all other measurements will set this field to 'EQUAL'

        x              numeric value of first number
        y              numeric value of second number
        z              numeric value of third number

        values         If list is present, a JSON array of values in list.
                       If list not present, values will be in x, y, and z.

        xView          view specification for x value
        yView          view specification for y value
        zView          view specification for z value

        minValue       either min([x, y, z]) or min(values)
        maxValue       either max([x, y, z]) or max(values)

All JSON results will have an identical number of fields.

Fields that are not applicable to a given measurement will have a value of 
EMPTY_FIELD.
        
All string matching is case-insensitive. JSON results are written to stdout.


USAGE:


To use this code as an imported module, add the following lines to the
import list in the importing module:

        import json
        import size_measurement_finder as smf

To find measurements in a sentence and capture the JSON result:

        json_string = smf.run(sentence)

To unpack the JSON into a list of SizeMeasurement namedtuples:

        json_data = json.loads(json_string)
        measurements = [smf.SizeMeasurement(**m) for m in json_data]

To access the fields in each measurement:

        for m in measurements:
            text = m.text
            start = int(m.start)
            end   = int(m.end)
            etc.


ACKNOWLEDGEMENTS:


Acknowledgement is made to the authors of the article listed below. Some of the 
regular expressions provided in this reference were used as the starting point 
for this code.

Reference: Natural Language Processing Techniques for Extracting and
           Categorizing Finding Measurements in Narrative Radiology
           Reports, M. Sevenster, J. Buurman, P. Liu, J. F. Peters,
           and P. J. Chang, Applied Clinical Informatics 2015 (6)
           600-610.

"""

import os
import sys
import json
import regex as re
from copy import deepcopy
from enum import Enum, unique
from collections import namedtuple
from claritynlp_logging import log, ERROR, DEBUG



# namedtuple used for serialization
EMPTY_FIELD = None
SIZE_MEASUREMENT_FIELDS = [
    'text',
    'start',
    'end',
    'temporality',
    'units',
    'condition',
    'x',
    'y',
    'z',
    'values',
    'xView',
    'yView',
    'zView',
    'minValue',
    'maxValue'
]
SizeMeasurement = namedtuple('SizeMeasurement', SIZE_MEASUREMENT_FIELDS)

# values for the temporality field
STR_CURRENT  = 'CURRENT'
STR_PREVIOUS = 'PREVIOUS'


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 7
_MODULE_NAME   = 'size_measurement_finder.py'

# set to True to enable debug output
_TRACE = False

# The regex for finding numeric values is called '_x'. The negative lookbehind
# prevents matching the rightmost portion of a BP measurement, such as 120/80.
_x = r'(?<![\d/])(\d+\.\d+|\.\d+|\d+)'

_by = r'\s*(by|x)\s*'
_to = r'\s*(to|-)\s*'
_vol = r'\s*(square|sq\.?|cubic|cu\.?)\s*'
_view = r'\s*([a-z]+)'

# The string 'in' as an abbreviation for 'inches' is difficult to disambiguate
# from 'in' used as a preposition. Assume that these words cannot follow 'in'
# when used to mean 'inches':
_str_in_meas = r'in[\.23]?(?!\sthe)(?!\sthis)(?!\sthat)(?!\sthose)'        +\
    r'(?!\swhich)(?!\shis)(?!\sher)(?!\sour)(?!\syour)(?!\smy)(?!\sorder)'

# generates a SINGLE capture group for the units
_strUnits = r'(mm[\.23]?|cm[\.23]?|' + _str_in_meas      +\
           r'|cc\.?|millimeters?|centimeters?|inch|inches)'

# Must have the final space after the negative lookahead group 'per', to
#distinguish "per second" or "per hour" from "peripherally" or other words.
# Must also prevent "mm Hg" from being interpreted as just mm.
_cm = r'[\-\s]*' + _strUnits +\
    r'(?![a-z/])(?!\sper\s)(?!\s[hH]g)(?!\sof\smercury)'
_regex_units = re.compile(r'\A' + _strUnits + r'\Z')

_str_is_area_unit = r'(square|sq\.?|mm2|cm2|in2)'
_regex_is_area_unit = re.compile(_str_is_area_unit)

_str_is_vol_unit  = r'(cubic|cu\.?|mm3|cm3|in3|cc\.?)'
_regex_is_vol_unit = re.compile(_str_is_vol_unit)

_str_x_cm         = _x + _cm
_str_x_vol_cm     = _x + _vol + _cm
_str_x_to_x_cm    = _x + _to  + _x  + _cm
_str_x_cm_to_x_cm = _x + _cm  + _to + _x  + _cm
_str_x_by_x_cm    = _x + _by  + _x  + _cm
_str_xy2  = _x + _cm + _by   + _x  + _cm
_str_xy3  = _x + _cm + _view + _by + _x  + _cm + _view
_str_xyz1 = _x + _by + _x    + _by + _x  + _cm
_str_xyz2 = _x + _by + _x    + _cm + _by + _x  + _cm
_str_xyz3 = _x + _cm + _by   + _x  + _cm + _by + _x    + _cm
_str_xyz4 = _x + _cm + _view + _by + _x  + _cm + _view + _by + _x + _cm + _view

# measurement finder regex
_str_m = r'(' +\
    _str_xyz4 +      r'|' + _str_xyz3 +      r'|' + _str_xyz2 +      r'|' +\
    _str_xyz1 +      r'|' + _str_xy3  +      r'|' + _str_xy2  +      r'|' +\
    _str_x_by_x_cm + r'|' + _str_x_to_x_cm + r'|' + _str_x_vol_cm +  r'|' +\
    _str_x_cm + r')'

_regex_x     = re.compile(_str_x_cm)
_regex_x_vol = re.compile(_str_x_vol_cm)
_regex_xx1   = re.compile(_str_x_to_x_cm)
_regex_xx2   = re.compile(_str_x_cm_to_x_cm)
_regex_xy1   = re.compile(_str_x_by_x_cm)
_regex_xy2   = re.compile(_str_xy2)
_regex_xy3   = re.compile(_str_xy3)
_regex_xyz1  = re.compile(_str_xyz1)
_regex_xyz2  = re.compile(_str_xyz2)
_regex_xyz3  = re.compile(_str_xyz3)
_regex_xyz4  = re.compile(_str_xyz4)

_str_seen   = r'(observed|identified|seen|appreciated|noted|'  +\
    r'confirmed|demonstrated|present)'
_str_approx = r'((approximately|about|up to|at least|at most|' +\
    r'in aggregate)\\s+)?'

_regex_number = re.compile(r'\A' + _x + r'\Z')

# Lists must be preceded by whitespace, to avoid capturing the digit
# in 'fio2' and similar abbreviations. Also, lists ALWAYS have an 'and'
# before the final item, and must contain at least two items.
_str_list_item = _x + r'\s*[-,]?(\s*and\s*)?'
_str_list = r'(?<=\s)(' + _str_list_item + r'\s*)*' + _x +\
    r'\s*[-,]?\s*and\s*' + _x + r'\s*[-,]?\s*' + _cm
_regex_list = re.compile(_str_list)
_regex_list_units = re.compile(_cm)

# expressions for finding 'previous' measurements
_prev1 = r'previously\s*measur(ed|ing)\s*' + _str_approx + _str_m
_prev2 = r'(previously\s*)?' + _str_seen + _str_approx + r'(as\s*)?' + _str_m
_prev3 = r'(previously|prev)\s*' + _str_approx + _str_m
_prev4 = r'compared\s*to\s*' + _str_approx + _str_m
_prev5 = r'(was|versus|vs)\s*' + _str_approx + _str_m
_prev6 = r'(enlarged|changed|decreased)\s*(in size\s*)?from\s*' +\
    _str_approx + _str_m
_prev7 = r'compared\s*to\s*(prior\s*of\s*)?' + _str_approx + _str_m
_prev8 = r'(in comparison|compared)\s*to\s*' + _str_approx + _str_m
_prev9 = r'(prior|earlier|previous)\s*measurement(s)?\s*of\s*' +\
    _str_approx + _str_m
_prev10 = r'from\s*' + _str_approx + _str_m + r'\s*to\s*' +\
    _str_approx + _str_m
_prev11 = r're(\-)?(identified|demon_strated)\s*(is\s*)?(an?\s*)?' +\
    _str_approx + _str_m
_prev12 = _str_approx + _str_m + r'\s*then\s*'

_str_previous = r'(' +\
    _prev1 + r'|' + _prev2  + r'|' + _prev3  + r'|' + _prev4  + r'|' +\
    _prev5 + r'|' + _prev6  + r'|' + _prev7  + r'|' + _prev8  + r'|' +\
    _prev9 + r'|' + _prev10 + r'|' + _prev11 + r'|' + _prev12 + r')'

_regex_previous = re.compile(_str_previous);

# match (), {}, and []
_str_brackets = r'[(){}\[\]]'
_regex_brackets = re.compile(_str_brackets)

# all meas recognizer regexes
regexes = [
    _regex_xyz4,   # 0
    _regex_xyz3,   # 1
    _regex_xyz2,   # 2
    _regex_xyz1,   # 3
    _regex_xy3,    # 4
    _regex_xy2,    # 5
    _regex_xy1,    # 6
    _regex_xx1,    # 7
    _regex_xx2,    # 8
    _regex_x_vol,  # 9
    _regex_x,      # 10
    _regex_list    # 11
]

@unique
class _TokenLabel(Enum):
    DIM1    = 1,
    DIM2    = 2,
    DIM3    = 3,
    AREA    = 4,
    VOLUME  = 5,
    VIEW1   = 6,
    VIEW2   = 7,
    VIEW3   = 8
    RANGE1  = 9,
    RANGE2  = 10,
    LISTNUM = 11,
    UNITS   = 12,
    UNITS2  = 13,
    UNITS3  = 14

_TOKEN_VALUE_NONE = -1
    
# A token is a component of a measurement.
# The 'value' is the numeric value, if any.
_Token = namedtuple('_Token', 'text label value')

# convert from cm to mm
_CM_TO_MM    = 10.0
_CM_TO_MM_SQ = _CM_TO_MM * _CM_TO_MM

# convert from inches to mm
_IN_TO_MM    = 25.4
_IN_TO_MM_SQ = _IN_TO_MM * _IN_TO_MM

_CHAR_SPACE = ' '

_LIST_TOKENIZER_FUNCTION_NAME = '_tokenize_list'

# namedtuple objects found by this code - internal use only
_MEAS_FIELDS = [
    'text', 'start', 'end', 'temporality', 'subject', 'location', 'token_list']
_Measurement = namedtuple('_Measurement', _MEAS_FIELDS)


###############################################################################
def enable_debug():

    global _TRACE
    _TRACE = True


###############################################################################
def _to_json(measurement_list):
    """
    Convert a list of _Measurement namedtuples to a JSON string.

    Convert each _Measurement to a dict, add each to a list of dicts, and
    then serialize the entire list of dicts.
    """

    # order the measurements by their position in the sentence
    measurement_list = sorted(measurement_list, key=lambda x: x.start)

    dict_list = []
    for m in measurement_list:
        m_dict = {}
        m_dict['text'] = m.text
        m_dict['start'] = m.start
        m_dict['end'] = m.end
        m_dict['temporality'] = m.temporality

        dim_count = 0
        is_range = False
        is_list = False
        is_area = False
        is_vol = False
        is_area_units = False
        is_vol_units = False

        # count dimensions and determine if area or volume measurement
        for t in m.token_list:
            if _TokenLabel.DIM1 == t.label or _TokenLabel.DIM2 == t.label or _TokenLabel.DIM3 == t.label:
                dim_count += 1
            elif _TokenLabel.RANGE1 == t.label or _TokenLabel.RANGE2 == t.label:
                is_range = True
                dim_count += 1
            elif _TokenLabel.AREA == t.label:
                is_area = True
            elif _TokenLabel.VOLUME == t.label:
                is_vol = True
            elif _TokenLabel.LISTNUM == t.label:
                is_list = True
                dim_count += 1
            elif _TokenLabel.UNITS2 == t.label:
                is_area_units = True
            elif _TokenLabel.UNITS3 == t.label:
                is_vol_units = True

        if is_area or is_area_units:
            units = 'SQUARE_MILLIMETERS'
        elif is_vol or is_vol_units:
            units = 'CUBIC_MILLIMETERS'
        else:
            units = 'MILLIMETERS'

        if is_range:
            condition = 'RANGE'
        else:
            condition = 'EQUAL'

        m_dict['units'] = units
        m_dict['condition'] = condition

        # give all fields values for ease of serialization
        m_dict['values'] = EMPTY_FIELD
        m_dict['x']      = EMPTY_FIELD
        m_dict['y']      = EMPTY_FIELD
        m_dict['z']      = EMPTY_FIELD
        m_dict['xView']  = EMPTY_FIELD
        m_dict['yView']  = EMPTY_FIELD
        m_dict['zView']  = EMPTY_FIELD

        if is_list:
            m_dict['values'] = []

        for t in m.token_list:
            if _TokenLabel.DIM1 == t.label or _TokenLabel.RANGE1 == t.label:
                m_dict['x'] = t.value
                dim_count -= 1
            elif _TokenLabel.DIM2 == t.label or _TokenLabel.RANGE2 == t.label:
                m_dict['y'] = t.value
                dim_count -= 1
            elif _TokenLabel.DIM3 == t.label:
                m_dict['z'] = t.value
                dim_count -= 1
            elif _TokenLabel.VIEW1 == t.label:
                m_dict['xView'] = t.text
            elif _TokenLabel.VIEW2 == t.label:
                m_dict['yView'] = t.text
            elif _TokenLabel.VIEW3 == t.label:
                m_dict['zView'] = t.text
            elif _TokenLabel.LISTNUM == t.label:
                m_dict['values'].append(t.value)
                dim_count -= 1

        assert 0 == dim_count

        # compute minValue and maxValue
        if is_list:
            minValue = min(m_dict['values'])
            maxValue = max(m_dict['values'])
        else:
            # compute min and max values of [x, y, z]
            data = []
            if EMPTY_FIELD != m_dict['x']:
                data.append(m_dict['x'])
            if EMPTY_FIELD != m_dict['y']:
                data.append(m_dict['y'])
            if EMPTY_FIELD != m_dict['z']:
                data.append(m_dict['z'])

            # something wrong if empty dict
            if 0 == len(data):
                log('size_measurement::_to_json: DATA LIST IS EMPTY')
                log(m_dict)
                assert len(data) > 0

            minValue = min(data)
            maxValue = max(data)
            
        m_dict['minValue'] = minValue
        m_dict['maxValue'] = maxValue
        
        # this measurement has now been converted
        dict_list.append(m_dict)

    # serialize the entire list of dicts
    return json.dumps(dict_list, indent=4)


###############################################################################
def _log_tokens(token_list):
    """
    log token data for debugging.
    """

    index = 0

    log('TOKENS: ')
    for token in token_list:
        log('\t[{0:2}]: {1:16} {2:6.2f} {3}'.format(index,
                                                      token.label,
                                                      token.value,
                                                      token.text))
        index += 1


###############################################################################
def _close_enough(str_x, str_y):
    """
    Return a Boolean indicating whether two floats are within EPSILON
    of each other.
    """

    EPSILON = 1.0e-5

    x = float(str_x)
    y = float(str_y)
    return abs(x-y) <= EPSILON


###############################################################################
def _num_to_float(num_str):
    """
    Convert a string representing a number to its floating point equivalent.
    The number string may contain embedded spaces.
    """

    # replace any embedded spaces with the empty string
    str_no_spaces = re.sub('\s', '', num_str)
    return float(str_no_spaces)


###############################################################################
def _is_area_unit(units_text):
    """
    Determine whether the given units text represents a unit of area and
    return a Boolean result.
    """

    match = _regex_is_area_unit.search(units_text)
    if match:
        return True
    else:
        return False


###############################################################################
def _is_vol_unit(units_text):
    """
    Determine whether the given units text represents a unit of volume and
    return a Boolean result.
    """

    match = _regex_is_vol_unit.search(units_text)
    if match:
        return True
    else:
        return False


###############################################################################
def _convert_units(value, units, is_area_measurement, is_vol_measurement):
    """
    Given a token value in the indicated units, convert to mm and return
    the new value.
    """

    convert_cm = units.startswith('cm') or    \
                 units.startswith('centi') or \
                 units.startswith('cc')
    convert_in = units.startswith('in')
    is_area    = is_area_measurement or _is_area_unit(units)
    is_volume  = is_vol_measurement or _is_vol_unit(units)

    if _TRACE:
        log('_convert_units::is_area: {0}'.format(is_area))
        log('_convert_units::is_volume: {0}'.format(is_volume))
    
    if convert_cm:
        # convert from cm to mm
        value = value * _CM_TO_MM
        if is_area:
            value = value * _CM_TO_MM
        elif is_volume:
            value = value * _CM_TO_MM_SQ
    elif convert_in:
        # convert from inches to mm
        value = value * _IN_TO_MM
        if is_area:
            value = value * _IN_TO_MM
        elif is_volume:
            value = value * _IN_TO_MM_SQ

    return value


###############################################################################
def _tokenize_complete_list(sentence, list_text, list_start):
    """
    Convert a list of numbers into individual tokens.
    """

    # Scan the list text and replace any occurrences of 'and' with a comma
    # followed by two spaces (i.e. preserve the sentence length). This will
    # make the subsequent tokenization code simpler. Also replace any dash
    # chars with a space.

    list_text = re.sub(r'and', r',  ', list_text)
    list_text = re.sub(r'-', r' ', list_text)

    units_match = _regex_list_units.search(list_text)
    if units_match:
        list_text_no_units = list_text[0:units_match.start()]
    else:
        # no units, invalid list
        return []

    if _TRACE:
        log('\tLIST TEXT NO UNITS: ->{0}<-'.format(list_text_no_units))

    # split list into list items at the commas
    items = list_text_no_units.split(',')

    tokens = []
    
    prev_index = list_start
    for item in items:
        if _TRACE:
            log('\tNEXT LIST ITEM: ->{0}<-'.format(item))

        match = _regex_number.search(item.strip())
        if match:
            # skip initial space chars, if any
            item_offset = 0
            c = item[item_offset:item_offset+1]
            while _CHAR_SPACE == c:
                item_offset += 1
                c = item[item_offset:item_offset+1]

            # find offset of this string in the sentence
            number_text = item[item_offset:].strip()
            offset = sentence.find(number_text, prev_index)

            # convert to floating point value
            value = _num_to_float(number_text)

            tokens.append( _Token(number_text, _TokenLabel.LISTNUM, value))
            prev_index = offset + 1
            
            if _TRACE:
                log('\tFound list numeric token: ->{0}<-'.format(number_text))

    # tokenize the units string
    units_text = units_match.group().strip()
    if _TRACE:
        log('\tList units_text: ->{0}<-'.format(units_text))

    is_area = _is_area_unit(units_text)
    is_vol  = _is_vol_unit(units_text)

    units_label = _TokenLabel.UNITS
    if is_area:
        units_label = _TokenLabel.UNITS2
    elif is_vol:
        units_label = _TokenLabel.UNITS3
        
    tokens.append( _Token(units_text, units_label, _TOKEN_VALUE_NONE))

    # convert the units of the list items and set all listnumbers to label DIM1
    for i in range(len(tokens)):
        token = tokens[i]
        if _TokenLabel.LISTNUM == token.label:
            value = _convert_units(token.value, units_text, False, False)
            tokens[i] = _Token(token.text, _TokenLabel.LISTNUM, value)

    return tokens
    

###############################################################################
def _tokenize_list(match, sentence):
    """
    Extract numeric values and measurements from a list.
    """

    list_text = match.group()
    tokens = _tokenize_complete_list(sentence, list_text, match.start())
    return (tokens, list_text)
    

###############################################################################
def _tokenize_xyz4(match):
    """
    Tokenizes measurements of the form:

            1.5 cm craniocaudal x 1.8 cm transverse x 2.1 cm anterior
    """
    
    assert 11 == len(match.groups())

    tokens = []
    
    # group 1 is the first number
    num = _num_to_float(match.group(1))

    # group 2 is the units of the first number
    value = _convert_units(num, match.group(2), False, False)

    # group 3 is the view

    tokens.append( _Token(match.group(1), _TokenLabel.DIM1, value))
    tokens.append( _Token(match.group(2), _TokenLabel.UNITS, _TOKEN_VALUE_NONE))
    tokens.append( _Token(match.group(3), _TokenLabel.VIEW1, _TOKEN_VALUE_NONE))

    # group 4 is the 'by' token (ignore)

    # group 5 is the second number
    num = _num_to_float(match.group(5))

    # group 6 is the units of the second number
    value = _convert_units(num, match.group(6), False, False)

    # group 7 is the second view

    tokens.append( _Token(match.group(5), _TokenLabel.DIM2, value))
    tokens.append( _Token(match.group(6), _TokenLabel.UNITS, _TOKEN_VALUE_NONE))
    tokens.append( _Token(match.group(7), _TokenLabel.VIEW2, _TOKEN_VALUE_NONE))
    
    #group 8 is the second 'by' token (ignore)

    # group 9 is the third number
    num = _num_to_float(match.group(9))

    # group 10 is the units of the third number
    value = _convert_units(num, match.group(10), False, False)

    # group 11 is the third view
    
    tokens.append( _Token(match.group(9), _TokenLabel.DIM3, value))
    tokens.append( _Token(match.group(10), _TokenLabel.UNITS, _TOKEN_VALUE_NONE))
    tokens.append( _Token(match.group(11), _TokenLabel.VIEW3, _TOKEN_VALUE_NONE))
    
    return tokens


###############################################################################
def _tokenize_xyz3(match):
    """
    Tokenizes measurements of the form: 

            1.5cm x 1.8cm x 2.1cm
    """
    assert 8 == len(match.groups())

    tokens = []
    
    # group 1 is the first number
    num = _num_to_float(match.group(1))

    # group 2 is the units of the first number
    value = _convert_units(num, match.group(2), False, False)

    tokens.append( _Token(match.group(1), _TokenLabel.DIM1, value))
    tokens.append( _Token(match.group(2), _TokenLabel.UNITS, _TOKEN_VALUE_NONE))

    # group 3 is the 'by' token (ignore)

    # group 4 is the second number
    num = _num_to_float(match.group(4))

    # group 5 is the units of the second number
    value = _convert_units(num, match.group(5), False, False)

    tokens.append( _Token(match.group(4), _TokenLabel.DIM2, value))
    tokens.append( _Token(match.group(5), _TokenLabel.UNITS, _TOKEN_VALUE_NONE))
    
    # group 6 is the second 'by' token (ignore)

    # group 7 is the third number
    num = _num_to_float(match.group(7))

    # group 8 is the units of the third number
    value = _convert_units(num, match.group(8), False, False)

    tokens.append( _Token(match.group(7), _TokenLabel.DIM3, value))
    tokens.append( _Token(match.group(8), _TokenLabel.UNITS, _TOKEN_VALUE_NONE))
    
    return tokens


###############################################################################
def _tokenize_xyz2(match):
    """
    Tokenizes measurements of the form:

            1.5 x 1.8cm x 2.1cm
    """

    assert 7 == len(match.groups())

    tokens = []

    # group 1 is the first number
    num1 = _num_to_float(match.group(1))

    # group 2 is the 'by' token (ignore)

    # group 3 is the second number
    num2 = _num_to_float(match.group(3))

    # group 4 is the units of the second number (and first number)
    value1 = _convert_units(num1, match.group(4), False, False)
    value2 = _convert_units(num2, match.group(4), False, False)

    tokens.append( _Token(match.group(1), _TokenLabel.DIM1, value1))
    tokens.append( _Token(match.group(3), _TokenLabel.DIM2, value2))
    tokens.append( _Token(match.group(4), _TokenLabel.UNITS, _TOKEN_VALUE_NONE))

    # group 5 is the second 'by' token (ignore)

    # group 6 is the third number
    num3 = _num_to_float(match.group(6))

    # group 7 is the units of the third number
    value3 = _convert_units(num3, match.group(7), False, False)

    tokens.append( _Token(match.group(6), _TokenLabel.DIM3, value3))
    tokens.append( _Token(match.group(7), _TokenLabel.UNITS, _TOKEN_VALUE_NONE))

    return tokens


###############################################################################
def _tokenize_xyz1(match):
    """
    Tokenizes measurements of the form:

            1.5 x 1.8 x 2.1 cm
    """

    assert 6 == len(match.groups())

    tokens = []

    # group 1 is the first number
    num1 = _num_to_float(match.group(1))

    # group 2 is the 'by' token (ignore)

    # group 3 is the second number
    num2 = _num_to_float(match.group(3))

    # group 4 is the second 'by' token (ignore)
    
    # group 5 is the third number
    num3 = _num_to_float(match.group(5))

    # group 6 is the units
    value1 = _convert_units(num1, match.group(6), False, False)
    value2 = _convert_units(num2, match.group(6), False, False)
    value3 = _convert_units(num3, match.group(6), False, False)

    tokens.append( _Token(match.group(1), _TokenLabel.DIM1, value1))
    tokens.append( _Token(match.group(3), _TokenLabel.DIM2, value2))
    tokens.append( _Token(match.group(5), _TokenLabel.DIM3, value3))
    tokens.append( _Token(match.group(6), _TokenLabel.UNITS, _TOKEN_VALUE_NONE))

    return tokens


###############################################################################
def _tokenize_xy3(match):
    """
    Tokenizes measurements of the form:

            1.5 cm craniocaudal by 1.8 cm transverse

    """
    
    assert 7 == len(match.groups())

    tokens = []
    
    # group 1 is the first number
    num = _num_to_float(match.group(1))

    # group 2 is the units of the first number
    value = _convert_units(num, match.group(2), False, False)

    # group 3 is the view

    tokens.append( _Token(match.group(1), _TokenLabel.DIM1, value))
    tokens.append( _Token(match.group(2), _TokenLabel.UNITS, _TOKEN_VALUE_NONE))
    tokens.append( _Token(match.group(3), _TokenLabel.VIEW1, _TOKEN_VALUE_NONE))

    # group 4 is the 'by' token (ignore)

    # group 5 is the second number
    num = _num_to_float(match.group(5))

    # group 6 is the units of the second number
    value = _convert_units(num, match.group(6), False, False)

    # group 7 is the second view

    tokens.append( _Token(match.group(5), _TokenLabel.DIM2, value))
    tokens.append( _Token(match.group(6), _TokenLabel.UNITS, _TOKEN_VALUE_NONE))
    tokens.append( _Token(match.group(7), _TokenLabel.VIEW2, _TOKEN_VALUE_NONE))
    
    return tokens


###############################################################################
def _tokenize_xy2(match):
    """
    Tokenizes measurements of the form: 

            1.5cm x 1.8cm
    """
    assert 5 == len(match.groups())

    tokens = []
    
    # group 1 is the first number
    num = _num_to_float(match.group(1))

    # group 2 is the units of the first number
    value = _convert_units(num, match.group(2), False, False)

    tokens.append( _Token(match.group(1), _TokenLabel.DIM1, value))
    tokens.append( _Token(match.group(2), _TokenLabel.UNITS, _TOKEN_VALUE_NONE))

    # group 3 is the 'by' token (ignore)

    # group 4 is the second number
    num = _num_to_float(match.group(4))

    # group 5 is the units of the second number
    value = _convert_units(num, match.group(5), False, False)

    tokens.append( _Token(match.group(4), _TokenLabel.DIM2, value))
    tokens.append( _Token(match.group(5), _TokenLabel.UNITS, _TOKEN_VALUE_NONE))
    
    return tokens


###############################################################################
def _tokenize_xy1(match):
    """
    Tokenizes measurements of the form:

            1.5 x 1.8 cm
    """

    assert 4 == len(match.groups())

    tokens = []

    # group 1 is the first number
    num1 = _num_to_float(match.group(1))

    # group 2 is the 'by' token (ignore)
    
    # group 3 is the second number
    num2 = _num_to_float(match.group(3))

    # group 4 is the units
    value1 = _convert_units(num1, match.group(4), False, False)
    value2 = _convert_units(num2, match.group(4), False, False)

    tokens.append( _Token(match.group(1), _TokenLabel.DIM1, value1))
    tokens.append( _Token(match.group(3), _TokenLabel.DIM2, value2))
    tokens.append( _Token(match.group(4), _TokenLabel.UNITS, _TOKEN_VALUE_NONE))

    return tokens


###############################################################################
def _tokenize_xx1(match):
    """
    Tokenizes measurements of the form:

            1.5 to 1.8 cm
    """

    assert 4 == len(match.groups())

    tokens = []

    # group 1 is the first number
    num1 = _num_to_float(match.group(1))

    # group 2 is the 'to' token (ignore)
    
    # group 3 is the second number
    num2 = _num_to_float(match.group(3))

    # group 4 is the units
    units_text = match.group(4)

    # check for area or volume units
    is_area = _is_area_unit(units_text)
    is_vol  = _is_vol_unit(units_text)

    # can't have both
    if is_area or is_vol:
        assert is_area ^ is_vol

    units_label = _TokenLabel.UNITS
    if is_area:
        units_label = _TokenLabel.UNITS2
    if is_vol:
        units_label = _TokenLabel.UNITS3
        
    value1 = _convert_units(num1, units_text, is_area, is_vol)
    value2 = _convert_units(num2, units_text, is_area, is_vol)

    tokens.append( _Token(match.group(1), _TokenLabel.RANGE1, value1))
    tokens.append( _Token(match.group(3), _TokenLabel.RANGE2, value2))
    tokens.append( _Token(match.group(4), units_label, _TOKEN_VALUE_NONE))

    return tokens


###############################################################################
def _tokenize_xx2(match):
    """
    Tokenizes measurements of the form:

            1.5 cm to 1.8 cm
    """

    assert 5 == len(match.groups())

    tokens = []

    # group 1 is the first number
    num1 = _num_to_float(match.group(1))

    # group 2 is the first units token
    units_text = match.group(2)

    # check for area or volume units
    is_area = _is_area_unit(units_text)
    is_vol  = _is_vol_unit(units_text)

    # can't have both
    if is_area or is_vol:
        assert is_area ^ is_vol

    units1_label = _TokenLabel.UNITS
    if is_area:
        units1_label = _TokenLabel.UNITS2
    if is_vol:
        units1_label = _TokenLabel.UNITS3

    value1 = _convert_units(num1, units_text, is_area, is_vol)

    # group 3 is the 'to' token (ignore)

    # group 4 is the second number
    num2 = _num_to_float(match.group(4))

    # group 5 is the second units token
    units_text = match.group(5)

    # check for area or volume units
    is_area = _is_area_unit(units_text)
    is_vol  = _is_vol_unit(units_text)

    # can't have both
    if is_area or is_vol:
        assert is_area ^ is_vol

    units2_label = _TokenLabel.UNITS
    if is_area:
        units2_label = _TokenLabel.UNITS2
    if is_vol:
        units2_label = _TokenLabel.UNITS3

    value2 = _convert_units(num2, units_text, is_area, is_vol)

    tokens.append( _Token(match.group(1), _TokenLabel.RANGE1, value1))
    tokens.append( _Token(match.group(2), units1_label, _TOKEN_VALUE_NONE))
    tokens.append( _Token(match.group(4), _TokenLabel.RANGE2, value2))
    tokens.append( _Token(match.group(5), units2_label, _TOKEN_VALUE_NONE))

    return tokens


###############################################################################
def _tokenize_xvol(match):
    """
    Tokenizes measurements of the form:

            1.5 cubic centimeters
            1.5 sq. cm
            others with square or cubic cm units
    """

    assert 3 == len(match.groups())

    tokens = []

    # group 1 is the first number
    num1 = _num_to_float(match.group(1))

    # group 2 is the 'volume' token
    vol_text = match.group(2)

    is_area = _is_area_unit(vol_text)
    is_vol  = _is_vol_unit(vol_text)

    # is_area and is_vol cannot both simultaneously be true
    assert is_area ^ is_vol
    
    # group 3 is the units
    value1 = _convert_units(num1, match.group(3), is_area, is_vol)

    # only area or volume possible with this regex
    if is_area:
        units_label = _TokenLabel.UNITS2
    else:
        units_label = _TokenLabel.UNITS3
    
    tokens.append( _Token(match.group(1), _TokenLabel.DIM1, value1))
    tokens.append( _Token(match.group(2), _TokenLabel.VOLUME, _TOKEN_VALUE_NONE))
    tokens.append( _Token(match.group(3), units_label, _TOKEN_VALUE_NONE))

    return tokens


###############################################################################
def _tokenize_x(match):
    """
    Tokenizes measurements of the form:

            1.5 cm
    """

    assert 2 == len(match.groups())

    tokens = []

    # group 1 is the first number
    num1 = _num_to_float(match.group(1))

    # group 2 is the units
    units_text = match.group(2)
    value1 = _convert_units(num1, units_text, False, False)

    is_area = _is_area_unit(units_text)
    is_vol  = _is_vol_unit(units_text)

    units_label = _TokenLabel.UNITS
    if is_area:
        units_label = _TokenLabel.UNITS2
    elif is_vol:
        units_label = _TokenLabel.UNITS3
    
    tokens.append( _Token(match.group(1), _TokenLabel.DIM1, value1))
    tokens.append( _Token(match.group(2), units_label, _TOKEN_VALUE_NONE))

    return tokens


###############################################################################
def _range_overlap(start1, end1, start2, end2):
    """
    Spans [start1, end1) and [start2, end2) are two substring spans. Examine
    both for overlap and return True if overlap, False if not.
    """

    if start2 >= end1:
        # interval2 is to the right of interval 1
        return False
    elif end2 <= start1:
        # interval 2 is to the left of interval 1
        return False
    else:
        return True

###############################################################################
def _clean_sentence(sentence):
    """
    Do some preliminary processing on the sentence.
    """

    # erase [], {}, or () from the sentence
    #sentence = _regex_brackets.sub(' ', sentence)

    # convert sentence to lowercase
    sentence = sentence.lower()

    return sentence


###############################################################################
def run(sentence):
    """

    Search the sentence for size measurements and construct a _Measurement
    namedtuple for each measurement found. Returns a JSON string.
    
    """

    # associates a regex index with its measurement tokenizer function
    TOKENIZER_MAP = {0:_tokenize_xyz4,
                     1:_tokenize_xyz3,
                     2:_tokenize_xyz2,
                     3:_tokenize_xyz1,
                     4:_tokenize_xy3,
                     5:_tokenize_xy2,
                     6:_tokenize_xy1,
                     7:_tokenize_xx1,
                     8:_tokenize_xx2,
                     9:_tokenize_xvol,
                    10:_tokenize_x,
                    11:_tokenize_list
    }
    
    original_sentence = sentence
    sentence = _clean_sentence(sentence)
    
    measurements = []
    
    # current sentence fragment, which is the entire sentence to start
    s = sentence
    
    prev_end=0
    more_to_go = True

    while more_to_go:
        more_to_go = False

        # data for the regex that gives the longest match overall
        best_matcher = None
        best_regex_index = -1
        best_match_text = ''
        match_start = 9999999
        match_end = 0
        
        for i in range(len(regexes)):
            match = regexes[i].search(s)
            if match:
                match_text = match.group()
                start = match.start()
                end = match.end()

                # if not contained within an existing measurement
                if (start < match_start) or ( (start == match_start) and (end > match_end)):
                    best_matcher = match
                    best_regex_index = i
                    best_match_text = match_text
                    match_start = start
                    match_end = end

        if _TRACE:
            log('best regex index: {0}'.format(best_regex_index)) 
                    
        if -1 != best_regex_index:
            # attempt to match a 'previous' form
            prev_match_text = ''
            iterator = _regex_previous.finditer(s)
            for match_prev in iterator:
                if not _range_overlap(match_start, match_end,
                                      match_prev.start(), match_prev.end()):
                    continue
                else:
                    prev_match_text = match_prev.group()
                    break

            if _TRACE:
                log(' MATCHING TEXT: ->{0}<-'.format(best_matcher.group()))
                log('    PREV MATCH: ->{0}<-'.format(prev_match_text))

            # assume current temporality unless proven otherwise
            str_temporal = STR_CURRENT
            if '' != prev_match_text:
                str_temporal = STR_PREVIOUS

            # keep looping until no matches found
            more_to_go = True

            # extract tokens according to the matching regex
            tokenizer_function = TOKENIZER_MAP[best_regex_index]
            if _LIST_TOKENIZER_FUNCTION_NAME == tokenizer_function.__name__:
                tokens, list_text = _tokenize_list(best_matcher, s)
                best_match_text = list_text
            else:
                tokens = tokenizer_function(best_matcher)

            if _TRACE:
                _log_tokens(tokens)

            measurement = _Measurement(text = best_match_text,
                                       start = prev_end + match_start,
                                       end = prev_end + match_end,
                                       temporality = str_temporal,
                                       subject = '',
                                       location = '',
                                       token_list = deepcopy(tokens))
            measurements.append(measurement)

            if _TRACE:
                log(measurement)

            prev_end += match_end
            tokens = []

            # use unmatched portion of sentence for next iteration
            s = sentence[prev_end:]
            if 0 == len(s):
                break

    # convert list to JSON
    return _to_json(measurements)


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)
