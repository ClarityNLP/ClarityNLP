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

import regex as re
import os
import sys
import json
import optparse
from copy import deepcopy
from enum import Enum, unique
from collections import namedtuple

VERSION_MAJOR = 0
VERSION_MINOR = 5

# set to True to enable debug output
TRACE = False

# namedtuple used for serialization
EMPTY_FIELD = -1
SIZE_MEASUREMENT_FIELDS = ['text', 'start', 'end', 'temporality', 'units',
                           'condition', 'x', 'y', 'z', 'values', 'xView',
                           'yView', 'zView', 'minValue', 'maxValue']
SizeMeasurement = namedtuple('SizeMeasurement', SIZE_MEASUREMENT_FIELDS)

# values for the temporality field
STR_CURRENT  = 'CURRENT'
STR_PREVIOUS = 'PREVIOUS'

# The regex for finding numeric values is called 'x'. The negative lookbehind
# prevents matching the rightmost portion of a BP measurement, such as 120/80.
x = r'(?<![\d/])(\d+\.\s?\d+|\d+\s?\.\d+|\.\d+|\d+)\s*'

by = r'\s*(by|x)\s*'
to = r'\s*(to|-)\s*'
vol = r'\s*(square|sq\.?|cubic|cu\.?)\s*'
view = r'\s*([a-z]+)\s*'

# The string 'in' as an abbreviation for 'inches' is difficult to disambiguate
# from 'in' used as a preposition. Assume that these words cannot follow 'in'
# when used to mean 'inches':
str_in_meas = r'in[2,3]?(?!\sthe)(?!\sthis)(?!\sthat)(?!\sthose)(?!\swhich)' + \
              r'(?!\shis)(?!\sher)(?!\sour)(?!\syour)(?!\smy)(?!\sorder)'

# generates a SINGLE capture group for the units
strUnits = r'(mm[2,3]?|cm[2,3]?|' + str_in_meas + \
           r'|cc|millimeters?|centimeters?|inch|inches)'

# Must have the final space after the negative lookahead group 'per', to distinguish
# "per second" or "per hour" from "peripherally" or other words. Must also prevent
# "mm Hg" from being interpreted as just mm.
cm = r'[\-\s]*' + strUnits + r'(?![a-z/])(?!\sper\s)(?!\s[hH]g)(?!\sof\smercury)'
regex_units = re.compile(r'\A' + strUnits + r'\Z')

str_is_area_unit = r'(square|sq\.?|mm2|cm2|in2)'
regex_is_area_unit = re.compile(str_is_area_unit)

str_is_vol_unit  = r'(cubic|cu\.?|mm3|cm3|in3|cc)'
regex_is_vol_unit = re.compile(str_is_vol_unit)

str_x_cm  = x + cm
str_x_vol_cm = x + vol + cm
str_x_to_x_cm = x + to + x + cm
str_x_cm_to_x_cm = x + cm + to + x + cm
str_x_by_x_cm = x + by + x + cm
str_xy2 = x + cm + by + x + cm
str_xy3 = x + cm + view + by + x + cm + view
str_xyz1 = x + by + x + by + x + cm
str_xyz2 = x + by + x + cm + by + x + cm
str_xyz3 = x + cm + by + x + cm + by + x + cm
str_xyz4 = x + cm + view + by + x + cm + view + by + x + cm + view

str_m = r'(' + str_xyz4 + r'|' + str_xyz3 + r'|' + str_xyz2 + r'|' + str_xyz1 + \
        r'|' + str_xy3 + r'|' + str_xy2 + r'|' + str_x_by_x_cm +                \
        r'|' + str_x_to_x_cm + r'|' + str_x_vol_cm + r'|' + str_x_cm + r')'

regex_x     = re.compile(str_x_cm)
regex_x_vol = re.compile(str_x_vol_cm)
regex_xx1   = re.compile(str_x_to_x_cm)
regex_xx2   = re.compile(str_x_cm_to_x_cm)
regex_xy1   = re.compile(str_x_by_x_cm)
regex_xy2   = re.compile(str_xy2)
regex_xy3   = re.compile(str_xy3)
regex_xyz1  = re.compile(str_xyz1)
regex_xyz2  = re.compile(str_xyz2)
regex_xyz3  = re.compile(str_xyz3)
regex_xyz4  = re.compile(str_xyz4)

seen   = r'(observed|identified|seen|appreciated|noted|confirmed|demonstrated|present)'
approx = r'((approximately|about|up to|at least|at most|in aggregate)\\s+)?'

regex_number = re.compile(r'\A' + x + r'\Z')

# lists must be preceded by whitespace, to avoid capturing the digit
# in 'fio2' and similar abbreviations
str_list_item = x + r'\s*[-,]?(\s*and\s*)?'
str_list = r'(?<=\s)(' + str_list_item + r'\s*)*' + str_list_item + cm
regex_list = re.compile(str_list)

# expressions for finding 'previous' measurements
prev1 = r'previously\s*measur(ed|ing)\s*' + approx + str_m
prev2 = r'(previously\s*)?' + seen + approx + r'(as\s*)?' + str_m
prev3 = r'(previously|prev)\s*' + approx + str_m
prev4 = r'compared\s*to\s*' + approx + str_m
prev5 = r'(was|versus|vs)\s*' + approx + str_m
prev6 = r'(enlarged|changed|decreased)\s*(in size\s*)?from\s*' + approx + str_m
prev7 = r'compared\s*to\s*(prior\s*of\s*)?' + approx + str_m
prev8 = r'(in comparison|compared)\s*to\s*' + approx + str_m
prev9 = r'(prior|earlier|previous)\s*measurement(s)?\s*of\s*' + approx + str_m
prev10 = r'from\s*' + approx + str_m + r'\s*to\s*' + approx + str_m
prev11 = r're(\-)?(identified|demonstrated)\s*(is\s*)?(an?\s*)?' + approx + str_m
prev12 = approx + str_m + r'\s*then\s*'

str_previous = r'(' + prev1 + r'|' + prev2 + r'|' + prev3 + r'|' + prev4 + r'|' + \
               prev5 + r'|' + prev6 + r'|' + prev7 + r'|' + prev8 + r'|' + \
               prev9 + r'|' + prev10 + r'|' + prev11 + r'|' + prev12 + r')'

regex_previous = re.compile(str_previous);

# match (), {}, and []
str_brackets = r'[(){}\[\]]'
regex_brackets = re.compile(str_brackets)

@unique
class TokenLabel(Enum):
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

TOKEN_VALUE_NONE = -1
    
# A token is a component of a measurement.
# The 'value' is the numeric value, if any.
Token = namedtuple('Token', 'text label value')

# convert from cm to mm
CM_TO_MM    = 10.0
CM_TO_MM_SQ = CM_TO_MM * CM_TO_MM

# convert from inches to mm
IN_TO_MM    = 25.4
IN_TO_MM_SQ = IN_TO_MM * IN_TO_MM

CHAR_SPACE = ' '

# namedtuple objects found by this code - internal use only
Measurement = namedtuple('Measurement',
                         'text start end temporality subject location token_list')

###############################################################################
def to_json(measurement_list):
    """
    Convert a list of Measurement namedtuples to a JSON string.

    Convert each Measurement to a dict, add each to a list of dicts, and
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
            if TokenLabel.DIM1 == t.label or TokenLabel.DIM2 == t.label or TokenLabel.DIM3 == t.label:
                dim_count += 1
            elif TokenLabel.RANGE1 == t.label or TokenLabel.RANGE2 == t.label:
                is_range = True
                dim_count += 1
            elif TokenLabel.AREA == t.label:
                is_area = True
            elif TokenLabel.VOLUME == t.label:
                is_vol = True
            elif TokenLabel.LISTNUM == t.label:
                is_list = True
                dim_count += 1
            elif TokenLabel.UNITS2 == t.label:
                is_area_units = True
            elif TokenLabel.UNITS3 == t.label:
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
            if TokenLabel.DIM1 == t.label or TokenLabel.RANGE1 == t.label:
                m_dict['x'] = t.value
                dim_count -= 1
            elif TokenLabel.DIM2 == t.label or TokenLabel.RANGE2 == t.label:
                m_dict['y'] = t.value
                dim_count -= 1
            elif TokenLabel.DIM3 == t.label:
                m_dict['z'] = t.value
                dim_count -= 1
            elif TokenLabel.VIEW1 == t.label:
                m_dict['xView'] = t.text
            elif TokenLabel.VIEW2 == t.label:
                m_dict['yView'] = t.text
            elif TokenLabel.VIEW3 == t.label:
                m_dict['zView'] = t.text
            elif TokenLabel.LISTNUM == t.label:
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
            minValue = min(data)
            maxValue = max(data)
            
        m_dict['minValue'] = minValue
        m_dict['maxValue'] = maxValue
        
        # this measurement has now been converted
        dict_list.append(m_dict)

    # serialize the entire list of dicts
    return json.dumps(dict_list, indent=4)

###############################################################################
def print_tokens(token_list):
    """
    Print token data for debugging.
    """

    index = 0

    print('TOKENS: ')
    for token in token_list:
        print('\t[{0:2}]: {1:16} {2:6.2f} {3}'.format(index,
                                                      token.label,
                                                      token.value,
                                                      token.text))
        index += 1

###############################################################################
def num_to_float(num_str):
    """
    Convert a string representing a number to its floating point equivalent.
    The number string may contain embedded spaces.
    """

    # replace any embedded spaces with the empty string
    str_no_spaces = re.sub('\s', '', num_str)
    return float(str_no_spaces)

###############################################################################
def is_area_unit(units_text):
    """
    Determine whether the given units text represents a unit of area and
    return a Boolean result.
    """

    match = regex_is_area_unit.search(units_text)
    if match:
        return True
    else:
        return False

###############################################################################
def is_vol_unit(units_text):
    """
    Determine whether the given units text represents a unit of volume and
    return a Boolean result.
    """

    match = regex_is_vol_unit.search(units_text)
    if match:
        return True
    else:
        return False
    
###############################################################################
def convert_units(value, units, is_area_measurement, is_vol_measurement):
    """
    Given a token value in the indicated units, convert to mm and return
    the new value.
    """

    convert_cm = units.startswith('cm') or    \
                 units.startswith('centi') or \
                 units.startswith('cc')
    convert_in = units.startswith('in')
    is_area    = is_area_measurement or is_area_unit(units)
    is_volume  = is_vol_measurement or is_vol_unit(units)

    if TRACE:
        print('convert_units::is_area: {0}'.format(is_area))
        print('convert_units::is_volume: {0}'.format(is_volume))
    
    if convert_cm:
        # convert from cm to mm
        value = value * CM_TO_MM
        if is_area:
            value = value * CM_TO_MM
        elif is_volume:
            value = value * CM_TO_MM_SQ
    elif convert_in:
        # convert from inches to mm
        value = value * IN_TO_MM
        if is_area:
            value = value * IN_TO_MM
        elif is_volume:
            value = value * IN_TO_MM_SQ

    return value


###############################################################################
def tokenize_complete_list(sentence, list_text, list_start):
    """
    Convert a list of numbers into individual tokens.
    """

    # Scan the list text and replace any occurrences of 'and' with a comma
    # followed by two spaces (i.e. preserve the sentence length). This will
    # make the subsequent tokenization code simpler. Also replace any dash
    # chars with a space.

    list_text = re.sub(r'and', r',  ', list_text)
    list_text = re.sub(r'-', r' ', list_text)

    # find the position immediately prior to the units string
    pos = len(list_text) - 1
    c = list_text[pos:pos+1]
    while CHAR_SPACE != c:
        pos -= 1
        if pos < 0:
            break;
        c = list_text[pos:pos+1]

    if pos < 0:
        # no units, invalid list
        return []
        
    # remove the units from the end and keep the list part
    list_text_no_units = list_text[0:pos]

    if TRACE:
        print('\tLIST TEXT NO UNITS: ->{0}<-'.format(list_text_no_units))

    # split list into list items at the commas
    items = list_text_no_units.split(',')

    tokens = []
    
    prev_index = list_start
    for item in items:
        if TRACE:
            print('\tNEXT LIST ITEM: ->{0}<-'.format(item))

        match = regex_number.search(item.strip())
        if match:
            # skip initial space chars, if any
            item_offset = 0
            c = item[item_offset:item_offset+1]
            while CHAR_SPACE == c:
                item_offset += 1
                c = item[item_offset:item_offset+1]

            # find offset of this string in the sentence
            number_text = item[item_offset:].strip()
            offset = sentence.find(number_text, prev_index)

            # convert to floating point value
            value = num_to_float(number_text)

            tokens.append( Token(number_text, TokenLabel.LISTNUM, value))
            prev_index = offset + 1
            
            if TRACE:
                print('\tFound list numeric token: ->{0}<-'.format(number_text))

    # tokenize the units string
    match = regex_units.search(list_text[pos+1:])
    if match:
        units_text = match.group()

        is_area = is_area_unit(units_text)
        is_vol  = is_vol_unit(units_text)

        units_label = TokenLabel.UNITS
        if is_area:
            units_label = TokenLabel.UNITS2
        elif is_vol:
            units_label = TokenLabel.UNITS3
        
        tokens.append( Token(units_text, units_label, TOKEN_VALUE_NONE))

    # convert the units of the list items and set all listnumbers to label DIM1
    for i in range(len(tokens)):
        token = tokens[i]
        if TokenLabel.LISTNUM == token.label:
            value = convert_units(token.value, units_text, False, False)
            tokens[i] = Token(token.text, TokenLabel.LISTNUM, value)

    return tokens
    

###############################################################################
def tokenize_list(match, sentence):
    """
    Extract numeric values and measurements from a list.
    """

    list_text = match.group()
    tokens = tokenize_complete_list(sentence, list_text, match.start())
    return (tokens, list_text)
    

###############################################################################
def tokenize_xyz4(match):
    """
    Tokenizes measurements of the form:

            1.5 cm craniocaudal x 1.8 cm transverse x 2.1 cm anterior
    """
    
    assert 11 == len(match.groups())

    tokens = []
    
    # group 1 is the first number
    num = num_to_float(match.group(1))

    # group 2 is the units of the first number
    value = convert_units(num, match.group(2), False, False)

    # group 3 is the view

    tokens.append( Token(match.group(1), TokenLabel.DIM1, value))
    tokens.append( Token(match.group(2), TokenLabel.UNITS, TOKEN_VALUE_NONE))
    tokens.append( Token(match.group(3), TokenLabel.VIEW1, TOKEN_VALUE_NONE))

    # group 4 is the 'by' token (ignore)

    # group 5 is the second number
    num = num_to_float(match.group(5))

    # group 6 is the units of the second number
    value = convert_units(num, match.group(6), False, False)

    # group 7 is the second view

    tokens.append( Token(match.group(5), TokenLabel.DIM2, value))
    tokens.append( Token(match.group(6), TokenLabel.UNITS, TOKEN_VALUE_NONE))
    tokens.append( Token(match.group(7), TokenLabel.VIEW2, TOKEN_VALUE_NONE))
    
    #group 8 is the second 'by' token (ignore)

    # group 9 is the third number
    num = num_to_float(match.group(9))

    # group 10 is the units of the third number
    value = convert_units(num, match.group(10), False, False)

    # group 11 is the third view
    
    tokens.append( Token(match.group(9), TokenLabel.DIM3, value))
    tokens.append( Token(match.group(10), TokenLabel.UNITS, TOKEN_VALUE_NONE))
    tokens.append( Token(match.group(11), TokenLabel.VIEW3, TOKEN_VALUE_NONE))
    
    return tokens

###############################################################################
def tokenize_xyz3(match):
    """
    Tokenizes measurements of the form: 

            1.5cm x 1.8cm x 2.1cm
    """
    assert 8 == len(match.groups())

    tokens = []
    
    # group 1 is the first number
    num = num_to_float(match.group(1))

    # group 2 is the units of the first number
    value = convert_units(num, match.group(2), False, False)

    tokens.append( Token(match.group(1), TokenLabel.DIM1, value))
    tokens.append( Token(match.group(2), TokenLabel.UNITS, TOKEN_VALUE_NONE))

    # group 3 is the 'by' token (ignore)

    # group 4 is the second number
    num = num_to_float(match.group(4))

    # group 5 is the units of the second number
    value = convert_units(num, match.group(5), False, False)

    tokens.append( Token(match.group(4), TokenLabel.DIM2, value))
    tokens.append( Token(match.group(5), TokenLabel.UNITS, TOKEN_VALUE_NONE))
    
    # group 6 is the second 'by' token (ignore)

    # group 7 is the third number
    num = num_to_float(match.group(7))

    # group 8 is the units of the third number
    value = convert_units(num, match.group(8), False, False)

    tokens.append( Token(match.group(7), TokenLabel.DIM3, value))
    tokens.append( Token(match.group(8), TokenLabel.UNITS, TOKEN_VALUE_NONE))
    
    return tokens

###############################################################################
def tokenize_xyz2(match):
    """
    Tokenizes measurements of the form:

            1.5 x 1.8cm x 2.1cm
    """

    assert 7 == len(match.groups())

    tokens = []

    # group 1 is the first number
    num1 = num_to_float(match.group(1))

    # group 2 is the 'by' token (ignore)

    # group 3 is the second number
    num2 = num_to_float(match.group(3))

    # group 4 is the units of the second number (and first number)
    value1 = convert_units(num1, match.group(4), False, False)
    value2 = convert_units(num2, match.group(4), False, False)

    tokens.append( Token(match.group(1), TokenLabel.DIM1, value1))
    tokens.append( Token(match.group(3), TokenLabel.DIM2, value2))
    tokens.append( Token(match.group(4), TokenLabel.UNITS, TOKEN_VALUE_NONE))

    # group 5 is the second 'by' token (ignore)

    # group 6 is the third number
    num3 = num_to_float(match.group(6))

    # group 7 is the units of the third number
    value3 = convert_units(num3, match.group(7), False, False)

    tokens.append( Token(match.group(6), TokenLabel.DIM3, value3))
    tokens.append( Token(match.group(7), TokenLabel.UNITS, TOKEN_VALUE_NONE))

    return tokens

###############################################################################
def tokenize_xyz1(match):
    """
    Tokenizes measurements of the form:

            1.5 x 1.8 x 2.1 cm
    """

    assert 6 == len(match.groups())

    tokens = []

    # group 1 is the first number
    num1 = num_to_float(match.group(1))

    # group 2 is the 'by' token (ignore)

    # group 3 is the second number
    num2 = num_to_float(match.group(3))

    # group 4 is the second 'by' token (ignore)
    
    # group 5 is the third number
    num3 = num_to_float(match.group(5))

    # group 6 is the units
    value1 = convert_units(num1, match.group(6), False, False)
    value2 = convert_units(num2, match.group(6), False, False)
    value3 = convert_units(num3, match.group(6), False, False)

    tokens.append( Token(match.group(1), TokenLabel.DIM1, value1))
    tokens.append( Token(match.group(3), TokenLabel.DIM2, value2))
    tokens.append( Token(match.group(5), TokenLabel.DIM3, value3))
    tokens.append( Token(match.group(6), TokenLabel.UNITS, TOKEN_VALUE_NONE))

    return tokens

###############################################################################
def tokenize_xy3(match):
    """
    Tokenizes measurements of the form:

            1.5 cm craniocaudal by 1.8 cm transverse

    """
    
    assert 7 == len(match.groups())

    tokens = []
    
    # group 1 is the first number
    num = num_to_float(match.group(1))

    # group 2 is the units of the first number
    value = convert_units(num, match.group(2), False, False)

    # group 3 is the view

    tokens.append( Token(match.group(1), TokenLabel.DIM1, value))
    tokens.append( Token(match.group(2), TokenLabel.UNITS, TOKEN_VALUE_NONE))
    tokens.append( Token(match.group(3), TokenLabel.VIEW1, TOKEN_VALUE_NONE))

    # group 4 is the 'by' token (ignore)

    # group 5 is the second number
    num = num_to_float(match.group(5))

    # group 6 is the units of the second number
    value = convert_units(num, match.group(6), False, False)

    # group 7 is the second view

    tokens.append( Token(match.group(5), TokenLabel.DIM2, value))
    tokens.append( Token(match.group(6), TokenLabel.UNITS, TOKEN_VALUE_NONE))
    tokens.append( Token(match.group(7), TokenLabel.VIEW2, TOKEN_VALUE_NONE))
    
    return tokens

###############################################################################
def tokenize_xy2(match):
    """
    Tokenizes measurements of the form: 

            1.5cm x 1.8cm
    """
    assert 5 == len(match.groups())

    tokens = []
    
    # group 1 is the first number
    num = num_to_float(match.group(1))

    # group 2 is the units of the first number
    value = convert_units(num, match.group(2), False, False)

    tokens.append( Token(match.group(1), TokenLabel.DIM1, value))
    tokens.append( Token(match.group(2), TokenLabel.UNITS, TOKEN_VALUE_NONE))

    # group 3 is the 'by' token (ignore)

    # group 4 is the second number
    num = num_to_float(match.group(4))

    # group 5 is the units of the second number
    value = convert_units(num, match.group(5), False, False)

    tokens.append( Token(match.group(4), TokenLabel.DIM2, value))
    tokens.append( Token(match.group(5), TokenLabel.UNITS, TOKEN_VALUE_NONE))
    
    return tokens

###############################################################################
def tokenize_xy1(match):
    """
    Tokenizes measurements of the form:

            1.5 x 1.8 cm
    """

    assert 4 == len(match.groups())

    tokens = []

    # group 1 is the first number
    num1 = num_to_float(match.group(1))

    # group 2 is the 'by' token (ignore)
    
    # group 3 is the second number
    num2 = num_to_float(match.group(3))

    # group 4 is the units
    value1 = convert_units(num1, match.group(4), False, False)
    value2 = convert_units(num2, match.group(4), False, False)

    tokens.append( Token(match.group(1), TokenLabel.DIM1, value1))
    tokens.append( Token(match.group(3), TokenLabel.DIM2, value2))
    tokens.append( Token(match.group(4), TokenLabel.UNITS, TOKEN_VALUE_NONE))

    return tokens

###############################################################################
def tokenize_xx1(match):
    """
    Tokenizes measurements of the form:

            1.5 to 1.8 cm
    """

    assert 4 == len(match.groups())

    tokens = []

    # group 1 is the first number
    num1 = num_to_float(match.group(1))

    # group 2 is the 'to' token (ignore)
    
    # group 3 is the second number
    num2 = num_to_float(match.group(3))

    # group 4 is the units
    units_text = match.group(4)

    # check for area or volume units
    is_area = is_area_unit(units_text)
    is_vol  = is_vol_unit(units_text)

    # can't have both
    if is_area or is_vol:
        assert is_area ^ is_vol

    units_label = TokenLabel.UNITS
    if is_area:
        units_label = TokenLabel.UNITS2
    if is_vol:
        units_label = TokenLabel.UNITS3
        
    value1 = convert_units(num1, units_text, is_area, is_vol)
    value2 = convert_units(num2, units_text, is_area, is_vol)

    tokens.append( Token(match.group(1), TokenLabel.RANGE1, value1))
    tokens.append( Token(match.group(3), TokenLabel.RANGE2, value2))
    tokens.append( Token(match.group(4), units_label, TOKEN_VALUE_NONE))

    return tokens

###############################################################################
def tokenize_xx2(match):
    """
    Tokenizes measurements of the form:

            1.5 cm to 1.8 cm
    """

    assert 5 == len(match.groups())

    tokens = []

    # group 1 is the first number
    num1 = num_to_float(match.group(1))

    # group 2 is the first units token
    units_text = match.group(2)

    # check for area or volume units
    is_area = is_area_unit(units_text)
    is_vol  = is_vol_unit(units_text)

    # can't have both
    if is_area or is_vol:
        assert is_area ^ is_vol

    units1_label = TokenLabel.UNITS
    if is_area:
        units1_label = TokenLabel.UNITS2
    if is_vol:
        units1_label = TokenLabel.UNITS3

    value1 = convert_units(num1, units_text, is_area, is_vol)

    # group 3 is the 'to' token (ignore)

    # group 4 is the second number
    num2 = num_to_float(match.group(4))

    # group 5 is the second units token
    units_text = match.group(5)

    # check for area or volume units
    is_area = is_area_unit(units_text)
    is_vol  = is_vol_unit(units_text)

    # can't have both
    if is_area or is_vol:
        assert is_area ^ is_vol

    units2_label = TokenLabel.UNITS
    if is_area:
        units2_label = TokenLabel.UNITS2
    if is_vol:
        units2_label = TokenLabel.UNITS3

    value2 = convert_units(num2, units_text, is_area, is_vol)

    tokens.append( Token(match.group(1), TokenLabel.RANGE1, value1))
    tokens.append( Token(match.group(2), units1_label, TOKEN_VALUE_NONE))
    tokens.append( Token(match.group(4), TokenLabel.RANGE2, value2))
    tokens.append( Token(match.group(5), units2_label, TOKEN_VALUE_NONE))

    return tokens


###############################################################################
def tokenize_xvol(match):
    """
    Tokenizes measurements of the form:

            1.5 cubic centimeters
            1.5 sq. cm
            others with square or cubic cm units
    """

    assert 3 == len(match.groups())

    tokens = []

    # group 1 is the first number
    num1 = num_to_float(match.group(1))

    # group 2 is the 'volume' token
    vol_text = match.group(2)

    is_area = is_area_unit(vol_text)
    is_vol  = is_vol_unit(vol_text)

    # is_area and is_vol cannot both simultaneously be true
    assert is_area ^ is_vol
    
    # group 3 is the units
    value1 = convert_units(num1, match.group(3), is_area, is_vol)

    # only area or volume possible with this regex
    if is_area:
        units_label = TokenLabel.UNITS2
    else:
        units_label = TokenLabel.UNITS3
    
    tokens.append( Token(match.group(1), TokenLabel.DIM1, value1))
    tokens.append( Token(match.group(2), TokenLabel.VOLUME, TOKEN_VALUE_NONE))
    tokens.append( Token(match.group(3), units_label, TOKEN_VALUE_NONE))

    return tokens

###############################################################################
def tokenize_x(match):
    """
    Tokenizes measurements of the form:

            1.5 cm
    """

    assert 2 == len(match.groups())

    tokens = []

    # group 1 is the first number
    num1 = num_to_float(match.group(1))

    # group 2 is the units
    units_text = match.group(2)
    value1 = convert_units(num1, units_text, False, False)

    is_area = is_area_unit(units_text)
    is_vol  = is_vol_unit(units_text)

    units_label = TokenLabel.UNITS
    if is_area:
        units_label = TokenLabel.UNITS2
    elif is_vol:
        units_label = TokenLabel.UNITS3
    
    tokens.append( Token(match.group(1), TokenLabel.DIM1, value1))
    tokens.append( Token(match.group(2), units_label, TOKEN_VALUE_NONE))

    return tokens

###############################################################################
regexes = [
    regex_xyz4,   # 0
    regex_xyz3,   # 1
    regex_xyz2,   # 2
    regex_xyz1,   # 3
    regex_xy3,    # 4
    regex_xy2,    # 5
    regex_xy1,    # 6
    regex_xx1,    # 7
    regex_xx2,    # 8
    regex_x_vol,  # 9
    regex_x,      # 10
    regex_list    # 11
]

# associates a regex index with its measurement tokenizer function
tokenizer_map = {0:tokenize_xyz4,
                 1:tokenize_xyz3,
                 2:tokenize_xyz2,
                 3:tokenize_xyz1,
                 4:tokenize_xy3,
                 5:tokenize_xy2,
                 6:tokenize_xy1,
                 7:tokenize_xx1,
                 8:tokenize_xx2,
                 9:tokenize_xvol,
                10:tokenize_x,
                11:tokenize_list
}

LIST_TOKENIZER_FUNCTION_NAME = 'tokenize_list'
        
###############################################################################
def range_overlap(start1, end1, start2, end2):
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
def clean_sentence(sentence):
    """
    Do some preliminary processing on the sentence.
    """

    # erase [], {}, or () from the sentence
    sentence = regex_brackets.sub(' ', sentence)

    # convert sentence to lowercase
    sentence = sentence.lower()

    return sentence

###############################################################################
def run(sentence):
    """

    Search the sentence for size measurements and construct a Measurement
    namedtuple for each measurement found. Returns a JSON string.
    
    """    

    original_sentence = sentence
    sentence = clean_sentence(sentence)
    
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

        if TRACE:
            print('best regex index: {0}'.format(best_regex_index)) 
                    
        if -1 != best_regex_index:
            # attempt to match a 'previous' form
            prev_match_text = ''
            iterator = regex_previous.finditer(s)
            for match_prev in iterator:
                if not range_overlap(match_start, match_end, match_prev.start(), match_prev.end()):
                    continue
                else:
                    prev_match_text = match_prev.group()
                    break

            if TRACE:
                print(' MATCHING TEXT: ->{0}<-'.format(best_matcher.group()))
                print('    PREV MATCH: ->{0}<-'.format(prev_match_text))

            # assume current temporality unless proven otherwise
            str_temporal = STR_CURRENT
            if '' != prev_match_text:
                str_temporal = STR_PREVIOUS

            # keep looping until no matches found
            more_to_go = True

            # extract tokens according to the matching regex
            tokenizer_function = tokenizer_map[best_regex_index]
            if LIST_TOKENIZER_FUNCTION_NAME == tokenizer_function.__name__:
                tokens, list_text = tokenize_list(best_matcher, s)
                best_match_text = list_text
            else:
                tokens = tokenizer_function(best_matcher)

            if TRACE:
                print_tokens(tokens)

            measurement = Measurement(text = best_match_text,
                                      start = prev_end + match_start,
                                      end = prev_end + match_end,
                                      temporality = str_temporal,
                                      subject = '',
                                      location = '',
                                      token_list = deepcopy(tokens))
            measurements.append(measurement)

            prev_end += match_end
            tokens = []

            # use unmatched portion of sentence for next iteration
            s = sentence[prev_end:]
            if 0 == len(s):
                break

    # convert list to JSON
    return to_json(measurements)

###############################################################################
def get_version():
    return 'size_measurement_finder {0}.{1}'.format(VERSION_MAJOR, VERSION_MINOR)
        
###############################################################################
def show_help():
    print(get_version())
    print("""
    USAGE: python3 ./size_measurement_finder.py -s <sentence> [-hvz]

    OPTIONS:

        -s, --sentence <quoted string>  Sentence to be processed.

    FLAGS:

        -h, --help                      Print this information and exit.
        -v, --version                   Print version information and exit.
        -z, --selftest                  Run internal tests and print results.

    """)

###############################################################################
if __name__ == '__main__':

    TEST_SENTENCES = [

        # str_x_cm (x)
        "The result is 1.5 cm in my estimation.",
        "The result is 1.5-cm in my estimation.",
        "The result is 1.5cm in my estimation.",
        "The result is 1.5cm2 in my estimation.",
        "The result is 1.5 cm3 in my estimation.",
        "The result is 1.5 cc in my estimation.",
        "The current result is 1.5 cm; previously it was 1.8 cm.",

        # x vol cm (xvol)
        "The result is 1.5 cubic centimeters in my estimation.",
        "The result is 1.5 cu. cm in my estimation.",
        "The result is 1.6 square centimeters in my estimation.",

        # str_x_to_x_cm (xx1, ranges)
        "The result is 1.5 to 1.8 cm in my estimation.",
        "The result is 1.5 - 1.8 cm in my estimation.",
        "The result is 1.5-1.8cm in my estimation.",
        "The result is 1 .5-1. 8cm in my estimation.",
        "The result is 1.5-1.8 cm2 in my estimation.",

        # str_x_cm_to_x_cm (xx2, ranges)
        "The result is 1.5 cm to 1.8 cm in my estimation.",
        "The result is 1.5cm - 1.8 cm in my estimation.",
        "The result is 1.5mm-1.8cm in my estimation.",
        "The result is 1 .5 cm -1. 8cm in my estimation.",
        "The result is 1.5cm2-1.8 cm2 in my estimation.",

        # str x_by_x_cm (xy1)
        "The result is 1.5 x 1.8 cm in my estimation.",
        "The result is 1.5x1.8cm in my estimation.",
        "The result is 1.5x1.8 cm in my estimation.",
        "The result is 1. 5x1. 8cm in my estimation.",

        # str_x_cm_by_x_cm (xy2)
        "The result is 1.5 cm by 1.8 cm in my estimation.",
        "The result is 1.5cm x 1.8cm in my estimation.",
        "The result is 1 .5 cm x 1. 8cm in my estimation.",
        "The result is 1. 5cm x 1. 8cm in my estimation.",
        "The result is 1.5 cm x 1.8 mm in my estimation.",

        # x cm view by x cm view (xy3)
        "The result is 1.5 cm craniocaudal by 1.8 cm transverse in my estimation.",
        "The result is 1.5cm craniocaudal x 1.8 cm transverse in my estimation.",
        "The result is 1. 5cm craniocaudal by 1 .8cm transverse in my estimation.",

        # x by x by x cm (xyz1)
        "The result is 1.5 x 1.8 x 2.1 cm in my estimation.",
        "The result is 1.5x1.8x2.1cm in my estimation.",
        "The result is 1.5x 1.8x 2.1 cm in my estimation.",
        "The result is 1 .5 by 1. 8 by 2. 1 cm in my estimation.",

        # x by x cm by x cm (xyz2)
        "The result is 1.5 x 1.8cm x 2.1cm in my estimation.",
        "The result is 1.5 x 1.8 cm x 2.1 cm in my estimation.",
        "The result is 1.5x 1.8cm x2.1cm in my estimation.",
        "The result is 1 .5x 1.8 cm x2. 1cm in my estimation.",
        "The result is 1.5 x 1.8 cm x 2.1 mm in my estimation.",

        # x cm by x cm by x cm (xyz3)
        "The result is 1.5cm x 1.8cm x 2.1cm in my estimation.",
        "The result is 1.5 cm by 1.8 cm by 2.1 cm in my estimation.",
        "The result is 1.5 cm by 1.8 cm x 2.1 cm in my estimation.",
        "The result is 1.5cm by1. 8cm x2 .1 cm in my estimation.",
        "The result is 1.5 cm x 1.8 mm x 2.1 cm in my estimation.",
        "The result is .1cm x .2cm x .3 mm in my estimation.",
        
        # x cm view by x cm view by x cm view (xyz4)
        "The result is 1.5 cm craniocaudal by 1.8 cm transverse by 2.1 cm anterior in my estimation.",
        "The result is 1.5 cm craniocaudal x  1.8 mm transverse x  2.1 cm anterior in my estimation.",
        "The result is 1.5cm craniocaudal x 1.8cm transverse x 2.1cm anterior in my estimation.",
        "The result is 1. 5cm craniocaudal x1 .8mm transverse x2 .1 cm anterior in my estimation.",
        "The result is 1.5 in craniocaudal x 1 .8in transverse x 2.1 in anterior in my estimation.",
                                        
        # list end (needed to find lists such as 1.0, 1.1, 1.2, and 1.3 cm)
        "The result is 1.5, 1.3, and 2.6 cm in my estimation.",
        "The result is 1.5 and 1.8 cm in my estimation.",
        "The result is 1.5- and 1.8-cm in my estimation.",
        "The result is 1.5, and 1.8 cm in my estimation.",
        "The results are 1.5, 1.8, and 2.1 cm in my estimation.",
        "The results are 1.5 and 1.8 cm and the other results are " \
        "2.3 and 4.8 cm in my estimation.",
        "The results are 1.5, 1.8, and 2.1 cm2 in my estimation.",
        "The results are 1.5, 1.8, 2.1, 2.2, and 2.3 cm3 in my estimation.",
        "The left greater saphenous vein is patent with diameters of 0.26, 0.26, 0.39, " \
        "0.24, and 0.37 and 0.75 cm at the ankle, calf, knee, low thigh, high thigh, " \
        "and saphenofemoral junction respectively.",
        "The peak systolic velocities are\n 99, 80, and 77 centimeters per second " \
        "for the ICA, CCA, and ECA, respectively.",

        # do not interpret the preposition 'in' as 'inches'
        "Peak systolic velocities on the left in centimeters per second are " \
        "as follows: 219, 140, 137, and 96 in the native vessel proximally, " \
        "proximal anastomosis, distal anastomosis, and native vessel distally.",
        "In NICU still pale with pink mm, improving perfusion O2 sat 100 in " \
        "room air, tmep 97.2",

        # same; note that "was" causes temporality to be "PREVIOUS"; could also be "CURRENT"
        "On admission, height was 75 inches, weight 134 kilograms; heart " \
        "rate was 59 in sinus rhythm; blood pressure 114/69.",

        # do not interpret speeds as linear measurements
        "Within the graft from proximal to distal, the velocities are " \
        "68, 128, 98, 75, 105, and 141 centimeters per second.",

        # do not interpret mm Hg as mm
        "Blood pressure was 112/71 mm Hg while lying flat.",
        "Aortic Valve - Peak Gradient:  *70 mm Hg  < 20 mm Hg",
        "The aortic valve was bicuspid with severely thickened and deformed " \
        "leaflets, and there was\n" \
        "moderate aortic stenosis with a peak gradient of 82 millimeters of " \
        "mercury and a\nmean gradient of 52 millimeters of mercury.",
        
        # newline in measurement
        "Additional lesions include a 6\n"                                      \
        "mm ring-enhancing mass within the left lentiform nucleus, a 10\n"      \
        "mm peripherally based mass within the anterior left frontal lobe\n"    \
        "as well as a more confluent plaque-like mass with a broad base along " \
        "the tentorial surface measuring approximately 2\n" +
        "cm in greatest dimension.",

        # temporality
        "The previously seen hepatic hemangioma has increased slightly in " \
        "size to 4.0 x\n3.5 cm (previously 3.8 x 2.2 cm).",

        "There is an interval decrease in the size of target lesion 1 which is a\n" \
        "precarinal node (2:24, 1.1 x 1.3 cm now versus 2:24, 1.1 cm x 2 cm then)."
    ]

    optparser = optparse.OptionParser(add_help_option=False)
    optparser.add_option('-s', '--sentence', action='store',      dest='sentence')                        
    optparser.add_option('-v', '--version',  action='store_true', dest='get_version')
    optparser.add_option('-z', '--selftest', action='store_true', dest='run_tests', default=False)
    optparser.add_option('-h', '--help',     action='store_true', dest='show_help', default=False)
    
    if 1 == len(sys.argv):
        show_help()
        sys.exit(0)

    opts, other = optparser.parse_args(sys.argv)

    if opts.show_help:
        show_help()
        sys.exit(0)

    if opts.get_version:
        print(get_version())
        sys.exit(0)

    run_tests = opts.run_tests
    sentence = opts.sentence

    if not sentence and not run_tests:
        print('A sentence must be specified on the command line.')
        sys.exit(-1)

    sentences = []
    if run_tests:
        sentences = TEST_SENTENCES
    else:
        sentences.append(sentence)

    for sentence in sentences:

        if run_tests:
            print(sentence)

        # find the measurements and print JSON result to stdout
        json_result = run(sentence)
        print(json_result)
