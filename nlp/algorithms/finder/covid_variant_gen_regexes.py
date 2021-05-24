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
import requests

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# set to True to enable debug output
_TRACE = False

_EMPTY_STRING = ''

# output file
_OUTPUT_FILE = 'covid_variant_regexes.txt'

# Nextstrain global Covid subsampling page
_NEXTSTRAIN_GLOBAL_URL = 'https://nextstrain.org/ncov/global'

# PANGO Covid lineage page
_PANGO_URL = 'https://cov-lineages.org/lineages.html'

_EXTRA_PLACES = ['Britain', 'Bristol', 'United States']


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
def _extract_items(text,
                   str_section_start,
                   str_section_end=None,
                   extra_items = []):
    """
    Extract all items from the <span> elements  and return a properly-escaped
    regex string for recognizing them.

    Extra is a list of additional strings to add to the item list.
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
            # clades could have a '/' character; split at that char and
            # also enter both parts separately, as well as the whole thing
            # see https://nextstrain.org/ncov/global?f_pango_lineage=A&gmin=113
            pos = item.find('/')
            if -1 != pos:
                first = item[:pos]
                second = item[pos+1:]
                items.append(first)
                items.append(second)
                
            items.append(item)

    # add any extra items
    items.extend(extra_items)
            
    return _to_regex_string(items)


###############################################################################
def _extract_amino_mutations(yaml_file_list):
    """
    """

    amino_mutations = set()
    for f in yaml_file_list:
        with open(f, 'rt') as infile:
            for line in infile:
                match = re.search(r'\bamino-acid-change: (?P<change>[^\n]+)\n\Z', line)
                if match:
                    amino_mutations.add(match.group('change').strip())

    amino_mutations = list(amino_mutations)

    # Sometimes the amino acid changes have a space, i.e. "N 203K" instead of
    # "N203K". Enter both forms in the list.
    new_aminos = []
    for a in amino_mutations:
        amino_with_space = a[0] + ' ' + a[1:]
        new_aminos.append(amino_with_space)
    amino_mutations.extend(new_aminos)
    
    return _to_regex_string(amino_mutations)
                    

###############################################################################
def _get_pango_lineages():
    """
    """

    html = requests.get(_PANGO_URL).text

    # the lineages are contained inside specific <a> elements
    lineages = []
    iterator = re.finditer(r'<a href="/lineages/lineage_[^>]+>(?P<lineage>[^<]+)</a>', html)
    for match in iterator:
        lineage = match.group('lineage')
        # skip single-char lineages
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
    parser.add_argument('-p', '--phe',
                        help='path to clone of the Public Health England ' \
                        '"variant_definitions" GitHub repository: ' \
                        'https://github.com/phe-genomics/variant_definitions',
                        dest='phe_dir')

    args = parser.parse_args()

    if args.version:
        print(get_version())
        sys.exit(0)

    if args.filepath is None:
        print('\n*** Missing --file argument ***')
        sys.exit(-1)

    if args.phe_dir is None:
        print('\n*** Missing --phe_dir argument ***')
        sys.exit(-1)

    phe_dir = args.phe_dir
    if not os.path.isdir(phe_dir):
        print('\n*** Directory does not exist: "{0}" ***'.format(phe_dir))
        
    # set path to the YAML folder in the clone of the PHE repo
    yaml_dir = os.path.join(phe_dir, 'variant_yaml')
    if not os.path.isdir(yaml_dir):
        print('\n*** The "variant_yaml" subdirectory of the PHE repo was not found. ***')
        sys.exit(-1)

    # get all YAML files in this dir
    yaml_files = []
    items = os.listdir(yaml_dir)
    for f in items:
        fullpath = os.path.join(yaml_dir, f)
        if os.path.isfile(fullpath):
            yaml_files.append(fullpath)
    print('Found {0} .yaml files in {1}.'.format(len(yaml_files), yaml_dir))
        
    html_file = args.filepath
    if not os.path.isfile(html_file):
        print('\n*** File does not exist: "{0}" ***.'.format(html_file))
        sys.exit(-1)

    # load the Nextstrain HTML file
    with open(html_file, 'rt') as infile:
        # read entire contents
        text = infile.read()
    text = text.lower()

    regex_string_clades = _extract_items(text,
                                         'filter by clade',
                                         'filter by emerging lineage')
    print(regex_string_clades)

    regex_string_places = _extract_items(text,
                                         'filter by country',
                                         'filter by host',
                                         _EXTRA_PLACES)
    print(regex_string_places)
    
    #regex_string_lineages = _extract_items(text, 'filter by pango lineage')
    #print(regex_string_lineages)

    regex_string_lineages = _get_pango_lineages()
    print(regex_string_lineages)
    
    # extract amino acid mutations from YAML files
    regex_string_amino = _extract_amino_mutations(yaml_files)
    print(regex_string_amino)
    
    # write regex strings to output file
    with open(_OUTPUT_FILE, 'w') as outfile:
        outfile.write('{0}\n'.format(regex_string_clades))
        outfile.write('\n')
        outfile.write('{0}\n'.format(regex_string_places))
        outfile.write('\n')
        outfile.write('{0}\n'.format(regex_string_lineages))
        outfile.write('\n')
        outfile.write('{0}\n'.format(regex_string_amino))
