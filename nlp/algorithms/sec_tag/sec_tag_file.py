#!/usr/bin/env python3
"""
Process a JSON file with the section tagger and log results to stdout.
"""

import re
import os
import sys
import json
import nltk
from nltk.tokenize import sent_tokenize
import util
from claritynlp_logging import log, ERROR, DEBUG

from section_tagger import section_tagger_init
from section_tagger import process_report

# XML character entity
regex_xml_character_entity = re.compile(r'&(?:#([0-9]+)|#x([0-9a-fA-F]+)|([0-9a-zA-Z]+));');

# one or more spaces and newlines
regex_multi_space   = re.compile(r' +')
regex_multi_newline = re.compile(r'\n+')

###############################################################################
def show_help():
    log ("""\nUsage: python3 ./sec_tag_file.py <report_file.json> [report_count] """)
    log()
    log("\tThe 'report_file' argument is required, must be JSON format.")
    log("\tUse 'report_count' to limit the number of reports processed, must be an integer.")
    log()
    log("\tFor example, to process 15 reports:")
    log("\n\t\tpython3 ./sec_tag_file reports.json 15")
    log()

###############################################################################
if __name__ == '__main__':

    if 1 == len(sys.argv):
        show_help()
        sys.exit(-1)

    # first arg is the report file
    json_file = sys.argv[1]

    # next arg, if present, is the number of reports to process
    max_reports = 0
    if 3 == len(sys.argv):
        max_reports = int(sys.argv[2])
    
    try:
        infile = open(json_file, 'rt')
        data = json.load(infile)
    except:
        log("Could not open file {0}.".format(json_file), ERROR)
        sys.exit(-1)

    infile.close()

    # initialize everything
    if not section_tagger_init():
        sys.exit(-1)
    
    ok = True
    index = 0
    while (ok):
        try:
            report = data['response']['docs'][index][util.solr_text_field]
        except:
            ok = False
            break

        # remove explicit XML entities
        no_xml_entities = regex_xml_character_entity.sub(' ', report)

        # collapse repeated newlines into a single newline
        single_newline_report = regex_multi_newline.sub('\n', no_xml_entities)

        # collapse repeated spaces into a single space
        clean_report = regex_multi_space.sub(' ', single_newline_report)

        section_headers, section_texts = process_report(clean_report)
        for i in range(len(section_headers)):
            log("<{0}>\n\t{1}".format(section_headers[i].to_output_string(), section_texts[i]))

        log("\n\n*** END OF REPORT {0} ***\n\n".format(index))
        
        index += 1
        if max_reports > 0 and index >= max_reports:
            break

    log("Processed {0} reports.".format(index))
