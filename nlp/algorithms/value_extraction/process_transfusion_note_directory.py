#!/usr/bin/env python3
"""

Example showing how to intgrate the Columbia transfusion note reader module
into a larger Python program.

This code recursively traverses a directory tree of transfusion note files
and logs the extracted data to stdout.

"""

import os
import sys
import json
import optparse
from collections import namedtuple
import columbia_transfusion_note_reader as ctnr
from claritynlp_logging import log, ERROR, DEBUG


VERSION_MAJOR = 0
VERSION_MINOR = 2

MODULE_NAME = 'integration_example.py'

###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(MODULE_NAME, VERSION_MAJOR, VERSION_MINOR)

###############################################################################
def show_help():
    log(get_version())
    log("""
    USAGE: python3 ./{0} -d <dirname>  [-hv]

    OPTIONS:

        -d, --dir <quoted string>  Path to directory containing transfusion notes.

    FLAGS:

        -h, --help           log this information and exit.
        -v, --version        log version information and exit.

    """.format(MODULE_NAME))

###############################################################################
if __name__ == '__main__':

    optparser = optparse.OptionParser(add_help_option=False)
    optparser.add_option('-d', '--dir', action='store',
                         dest='directory')
    optparser.add_option('-v', '--version',  action='store_true',
                         dest='get_version')
    optparser.add_option('-h', '--help',     action='store_true',
                         dest='show_help', default=False)

    opts, other = optparser.parse_args(sys.argv)

    # show help if no command line arguments
    if opts.show_help or 1 == len(sys.argv):
        show_help()
        sys.exit(0)

    if opts.get_version:
        log(get_version())
        sys.exit(0)

    directory = opts.directory
    if directory is None:
        log('error: a directory must be specified on the command line')
        sys.exit(-1)

    if not os.path.isdir(directory):
        log('error: directory {0} does not exist'.format(directory))
        sys.exit(-1)

    # find the max length of all the data fields, to align output
    maxlen_t = len(max(ctnr.TRANSFUSION_NOTE_FIELDS, key=len))
    maxlen_v = len(max(ctnr.VITALS_FIELDS, key=len))
    maxlen = max(maxlen_t, maxlen_v)

    # recurse through the file tree rooted at 'directory' and process each file
    file_count = 0
    for root, subdirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            
            log('*** FILE: {0} ***'.format(filepath))

            # process the next file
            json_string = ctnr.run(filepath)
            file_count += 1
            
            # prettylog the result to stdout

            # parse the JSON result
            json_data = json.loads(json_string)

            # unpack to a list of TransfusionNote namedtuples
            note_list = [ctnr.TransfusionNote(**record) for record in json_data]
    
            # log all valid fields in each note
            for note in note_list:
                # get non-vitals field names and values
                for field in ctnr.TRANSFUSION_NOTE_FIELDS:
                    val = getattr(note, field)
                    # if a valid field, log it
                    if ctnr.EMPTY_FIELD != val:
                        if 'vitals' != field:
                            indent = ' '*(maxlen - len(field))
                            log('{0}{1}: {2}'.format(indent, field, val))
                        else:
                            # extract vitals into a VitalsRecord namedtuple
                            v_record = ctnr.VitalsRecord(**val)
                            # extract field names and values for vitals
                            for v_field in ctnr.VITALS_FIELDS:
                                v_val = getattr(v_record, v_field)
                                # if valid field, log it
                                if ctnr.EMPTY_FIELD != v_val:
                                    indent = ' '*(maxlen - len(v_field))
                                    log('{0}{1}: {2}'.format(indent, v_field, v_val))
                                        
                # log blank line after each note
                log()

    log('processed {0} files'.format(file_count))


