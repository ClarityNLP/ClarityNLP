#!/usr/bin/env python3
"""
This code extracts various items related to Covid-19 variants from the
Nextstrain global analysis page: https://nextstrain.org/ncov/global.

Browse to that website and save the page to a separate file. The saved .html
page is the input to this code.
"""

import os
import re
import sys
import argparse


_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# set to True to enable debug output
_TRACE = False

_EMPTY_STRING = ''

# output file
_OUTPUT_FILE = 'covid_variant_regexes.txt'


###############################################################################
def enable_debug():

    global _TRACE
    _TRACE = True


###############################################################################
def _to_regex_string(item_list):
    """
    """

    # reverse sort by length
    item_list = sorted(item_list, key=lambda x: len(x), reverse=True)
    item_list = [re.escape(item) for item in item_list]
    regex_string = r'(' + r'|'.join(item_list) + r')'
    return regex_string

    
###############################################################################
def _extract_places(text):
    """
    Extract all countries, admin divisions, and locations and return a
    properly-escaped regex string for recognizing them.

    Returns an empty string if none are found.
    """

    # locate the appropriate section of the file
    pos1 = text.find('filter by country')
    if -1 == pos1:
        return _EMPTY_STRING

    pos2 = text.find('filter by host')
    place_text = text[pos1:pos2]

    # places are located inside the subsequent <span> elements
    
    places = []
    iterator = re.finditer(r'<span>(?P<place>[^\s]+)\s\(\d+\)</span>',
                           place_text)
    for match in iterator:
        place = match.group('place')
        # skip the 'USA' abbreviation
        if 'usa' != place:
            places.append(place)

    return _to_regex_string(places)
    
    
###############################################################################
def _extract_pango_lineages(text):
    """
    Extract the PANGO lineages and returns a properly-escaped regex string
    for recognizing them.

    Returns an empty string if none are found.
    """

    # locate the appropriate section of the file
    pos = text.find('filter by pango lineage')
    if -1 == pos:
        return _EMPTY_STRING

    text = text[pos:]

    # lineages are located inside the subsequent <span> elements

    lineages = []

    iterator = re.finditer(r'<span>(?P<lineage>[a-z\d.]+)\s\(\d+\)</span>', text)
    for match in iterator:
        lineage = match.group('lineage')
        # ignore any single-char lineages (such as 'a', 'b')
        if len(lineage) > 1:
            lineages.append(lineage)

    return _to_regex_string(lineages)

    
###############################################################################
def get_version():
    path, module_name = os.path.split(__file__)
    return '{0} {1}.{2}'.format(module_name, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':

    
    parser = argparse.ArgumentParser(
        description='Extract information on Covid-19 variants from text.'
    )

    parser.add_argument('-v', '--version',
                        help='show version and exit',
                        action='store_true')
    parser.add_argument('-d', '--debug',
                        help='print debug information to stdout',
                        action='store_true')
    parser.add_argument('-f', '--file',
                        help='Nexstrain HTML input file',
                        dest='filepath')

    args = parser.parse_args()

    if args.version:
        print(get_version())
        sys.exit(0)

    if args.filepath is None:
        print('\n*** Missing --file argument ***')
        sys.exit(-1)

    html_file = args.filepath
    if not os.path.isfile(html_file):
        print('\n*** File not found: "{0}" ***.'.format(html_file))
        sys.exit(-1)

    with open(html_file, 'rt') as infile:
        # read entire contents
        text = infile.read()

    text = text.lower()

    regex_string_places = _extract_places(text)
    print(regex_string_places)
    
    regex_string_lineages = _extract_pango_lineages(text)
    print(regex_string_lineages)

    # write regex strings to output file
    with open(_OUTPUT_FILE, 'w') as outfile:
        outfile.write('{0}\n'.format(regex_string_places))
        outfile.write('\n')
        outfile.write('{0}\n'.format(regex_string_lineages))
