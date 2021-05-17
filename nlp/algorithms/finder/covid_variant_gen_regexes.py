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
def _extract_items(text, str_section_start, str_section_end=None):
    """
    Extract all items from the <span> elements  and return a properly-escaped
    regex string for recognizing them.
    """

    # locate the appropriate section of the file
    pos1 = text.find(str_section_start)
    if -1 == pos1:
        return _EMPTY_STRING

    if str_section_end is not None:
        pos2 = text.find(str_section_end)
        item_text = text[pos1:pos2]
    else:
        item_text = text[pos1:]

    # are located inside the subsequent <span> elements

    items = []
    iterator = re.finditer(r'<span>(?P<item>[^(]+)\(\d+\)</span>',
                           item_text)
    for match in iterator:
        # trim trailing space
        item = match.group('item').strip()
        if len(item) > 1:
            items.append(item)

    return _to_regex_string(items)

    
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

    #regex_string_clades = _extract_clades(text)
    regex_string_clades = _extract_items(text, 'filter by clade', 'filter by emerging lineage')
    print(regex_string_clades)
    
    regex_string_places = _extract_items(text, 'filter by country', 'filter by host')
    print(regex_string_places)
    
    regex_string_lineages = _extract_items(text, 'filter by pango lineage')
    print(regex_string_lineages)

    # write regex strings to output file
    with open(_OUTPUT_FILE, 'w') as outfile:
        outfile.write('{0}\n'.format(regex_string_clades))
        outfile.write('\n')
        outfile.write('{0}\n'.format(regex_string_places))
        outfile.write('\n')
        outfile.write('{0}\n'.format(regex_string_lineages))
