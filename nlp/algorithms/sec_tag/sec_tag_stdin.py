#!/usr/bin/env python3

import os
import re
import sys
import json

from sec_tag import process_report
from sec_tag import section_tagger_init
from claritynlp_logging import log, ERROR, DEBUG


# XML character entities
regex_xml_character_entity = re.compile(r'&(?:#([0-9]+)|#x([0-9a-fA-F]+)|([0-9a-zA-Z]+));');

# one or more spaces and newlines
regex_multi_space   = re.compile(r' +')
regex_multi_newline = re.compile(r'\n+')

# initialize the section tagger
if not section_tagger_init():
    sys.exit(-1)

# process all reports sent via command line
report = ""
report_index = 0
reportComplete = False

for line in sys.stdin:

    # report text delimited by "===>" and "<==="
    if line.startswith("===>"):
        report = line[4:]
    elif line.endswith("<===\n"):
        report += line[0:-5]
        reportComplete = True
    else:
        report += line

    if reportComplete:
        #log("Here is the report:\n{0}".format(report))

        reportComplete = False

        # replace any XML entities with a space
        no_xml_entities = regex_xml_character_entity.sub(' ', report)

        # replace repeated newlines with a single newline
        single_newline_report = regex_multi_newline.sub('\n', no_xml_entities)

        # replace repeated spaces with a single space
        clean_report = regex_multi_space.sub(' ', single_newline_report)

        # run the section tagger and log results to stdout
        process_report(clean_report)
        log("\n\n*** END OF REPORT {0} ***\n\n".format(report_index))
        report_index += 1
        
