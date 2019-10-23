#!/usr/bin/env python3
"""


OVERVIEW:


This module attempts to improve upon spaCy's sentence tokenization. Clinical
notes are often heavily abbreviated, and they include spatial measurements
and other features not generally found in standard written English.
NLP tools make mistakes in sentence tokenization for such texts. These
errors can be greatly reduced by first substituting a single token for
the constructs that trip up the tokenizer, then restoring the original text
afterwards. This module does these substitutions and applies other
empirically-deterimined corrections as well.


OUTPUT:


A list of sentence strings.


USAGE:


The 'parse_sentences' method of the Segmentation class does the main work of
the module. This method takes a single argument:

    text:        the text to be tokenized into sentences


The module can be run from the command line for testing and debugging. It will
process a JSON file properly configured for ClarityNLP SOLR ingest (i.e. each
JSON record needs a 'report_text' field), extract the 'report_text' field,
split it into sentences, and print each sentence to the screen. Help for
command line operation can be obtained with this command:

        python3 ./segmentation.py --help


Some examples:

To tokenize all reports in myfile.json and print each sentence to stdout:

        python3 ./segmentation.py -f /path/to/myfile.json

To tokenize only the first 10 reports (indices begin with 0):

        python3 ./segmentation.py -f myfile.json --end 9

To tokenize reports 115 through 134 inclusive, and to also show the report text
after cleanup and token substitution (immediately prior to tokenization):

        python3 ./segmentation.py -f myfile.json --start 115 --end 134 --debug


"""

import re
import os
import sys
import json
import time
import optparse
import en_core_web_sm as english_model
from nltk.tokenize import sent_tokenize
from claritynlp_logging import log, ERROR, DEBUG

if __name__ == '__main__':
    import segmentation_helper as seg_helper
else:
    from algorithms.segmentation import segmentation_helper as seg_helper

VERSION_MAJOR = 0
VERSION_MINOR = 1

# set to True to enable debug output
TRACE = False

MODULE_NAME = 'segmentation.py'

data = {}
loading_status = 'none'


###############################################################################
def segmentation_init(tries=0):
    if tries > 0:
        log('Retrying, try%d' % tries)

    global loading_status
    if loading_status == 'none' and 'nlp' not in data:
        try:
            log('Segmentation init...')
            loading_status = 'loading'
            data['nlp'] = english_model.load()
            loading_status = 'done'
        except Exception as exc:
            log(exc, ERROR)
            loading_status = 'none'
    elif loading_status == 'loading' and tries < 30:
        time.sleep(10)
        if loading_status == 'loading':
            new_tries = tries + 1
            return segmentation_init(tries=new_tries)

    return data['nlp']


###############################################################################
def parse_sentences_spacy(text, spacy=None):

    # spacy = segmentation_init()
    # doc = spacy(text)
    # return [sent.string.strip() for sent in doc.sents]
    if not spacy:
        spacy = segmentation_init()

    # Do some cleanup and substitutions before tokenizing. The substitutions
    # replace strings of tokens that tend to be incorrectly split with
    # a single token that will not be split.
    text = seg_helper.cleanup_report(text)
    text = seg_helper.do_substitutions(text)

    # now do the sentence tokenization with the substitutions in place
    doc = spacy(text)
    sentences = [sent.string.strip() for sent in doc.sents]

    # fix various problems and undo the substitutions
    sentences = seg_helper.split_concatenated_sentences(sentences)

    # do this, if at all, BEFORE undoing the substitutions
    #sentences = seg_helper.split_section_headers(sentences)
    
    sentences = seg_helper.undo_substitutions(sentences)
    sentences = seg_helper.fixup_sentences(sentences)
    sentences = seg_helper.delete_junk(sentences)

    return sentences


###############################################################################
class Segmentation(object):

    def __init__(self):
        self.regex_multi_space = re.compile(r' +')
        self.regex_multi_newline = re.compile(r'\n+')

    def remove_newlines(self, text):

        # replace newline with space
        no_newlines = self.regex_multi_newline.sub(' ', text)

        # replace multiple consecutive spaces with single space
        cleaned_text = self.regex_multi_space.sub(' ', no_newlines)
        return cleaned_text

    def parse_sentences(self, text, spacy=None):
        return parse_sentences_spacy(text, spacy)

    def parse_sentences_nltk(self, text):
        # needs punkt
        return sent_tokenize(self, text)


###############################################################################
def run_tests():

    seg_obj = Segmentation()

    # sentences for testing vitals recognition
    SENTENCES = [
        'VS: T 95.6 HR 45 BP 75/30 RR 17 98% RA.',
        'VS T97.3 P84 BP120/56 RR16 O2Sat98 2LNC',
        'Height: (in) 74 Weight (lb): 199 BSA (m2): 2.17 m2 '                +\
        'BP (mm Hg): 140/91 HR (bpm): 53',
        'Vitals: T: 99 BP: 115/68 P: 79 R:21 O2: 97',
        'Vitals - T 95.5 BP 132/65 HR 78 RR 20 SpO2 98%/3L',
        'VS: T=98 BP= 122/58  HR= 7 RR= 20  O2 sat= 100% 2L NC',
        'VS:  T-100.6, HR-105, BP-93/46, RR-16, Sats-98% 3L/NC',
        'VS - Temp. 98.5F, BP115/65 , HR103 , R16 , 96O2-sat % RA',
        'Vitals: Temp 100.2 HR 72 BP 184/56 RR 16 sats 96% on RA',
        'PHYSICAL EXAM: O: T: 98.8 BP: 123/60   HR:97    R 16  O2Sats100%',
        'VS before transfer were 85 BP 99/34 RR 20 SpO2% 99/bipap 10/5 50%.',
        'In the ED, initial vs were: T 98 P 91 BP 122/63 R 20 O2 sat 95%RA.',
        'In the ED initial vitals were HR 106, BP 88/56, RR 20, O2 Sat '     +\
        '85% 3L.',
        'In the ED, initial vs were: T=99.3, P=120, BP=111/57, RR=24, '      +\
        'POx=100%.',
        'Upon transfer her vitals were HR=120, BP=109/44, RR=29, POx=93% '   +\
        'on 8L FM.',
        'Vitals in PACU post-op as follows: BP 120/80 HR 60-80s RR  '        +\
        'SaO2 96% 6L NC.',
        'In the ED, initial vital signs were T 97.5, HR 62, BP 168/60, '     +\
        'RR 18, 95% RA.',
        'T 99.4 P 160 R 56 BP 60/36 mean 44 O2 sat 97% Wt 3025 grams '       +\
        'Lt 18.5 inches HC 35 cm',
        'In the ED, initial vital signs were T 97.0, BP 85/44, HR 107, '     +\
        'RR 28, and SpO2 91% on NRB.',
        'Prior to transfer, his vitals were BP 119/53 (105/43 sleeping), '   +\
        'HR 103, RR 15, and SpO2 97% on NRB.',
        'In the ED inital vitals were, Temperature 100.8, Pulse: 103, '      +\
        'RR: 28, BP: 84/43, O2Sat: 88, O2 Flow: 100 (Non-Rebreather).',
        'At clinic, he was noted to have increased peripheral edema and '    +\
        'was sent to the ED where his vitals were T 97.1 HR 76 BP 148/80 '   +\
        'RR 25 SpO2 92%/RA.',
    ]

    seg_helper.enable_debug()

    count = 0
    for s in SENTENCES:
        log(s)
        sentences = seg_obj.parse_sentences(s)
        log('\t[{0:3}]\t{1}\n'.format(count, s))
        count += 1


###############################################################################
def get_version():
    str1 = '{0} {1}.{2}'.format(MODULE_NAME, VERSION_MAJOR, VERSION_MINOR)
    str2 = seg_helper.get_version()
    version = '{0}\n{1}'.format(str1, str2)
    return version


###############################################################################
def show_help():
    log(get_version())
    log("""
    USAGE: python3 ./{0} -f <filename> [-s <start_indx> -e <end_indx>] [-dhvz]

    OPTIONS:

        -f, --file     <quoted string>     Path to input JSON file.
        -s, --start    <integer>           Index of first record to process.
        -e, --end      <integer>           Index of final record to process.
                                           Indexing begins at 0.

    FLAGS:

        -d, --debug          Enable debug output.
        -h, --help           Print this information and exit.
        -v, --version        Print version information and exit.
        -z, --selftest       Run self-tests and exit.

    """.format(MODULE_NAME))


###############################################################################
if __name__ == '__main__':

    seg_obj = Segmentation()

    optparser = optparse.OptionParser(add_help_option=False)
    optparser.add_option('-f', '--file', action='store',
                         dest='filepath')
    optparser.add_option('-s', '--start', action='store',
                         dest='start_index')
    optparser.add_option('-e', '--end', action='store',
                         dest='end_index')
    optparser.add_option('-v', '--version', action='store_true',
                         dest='get_version')
    optparser.add_option('-d', '--debug', action='store_true',
                         dest='debug', default=False)
    optparser.add_option('-h', '--help', action='store_true',
                         dest='show_help', default=False)
    optparser.add_option('-z', '--selftest', action='store_true',
                         dest='selftest', default=False)

    opts, other = optparser.parse_args(sys.argv)

    if 1 == len(sys.argv) or opts.show_help:
        show_help()
        sys.exit(0)

    if opts.get_version:
        log(get_version())
        sys.exit(0)

    if opts.selftest:
        run_tests()
        sys.exit(0)

    start_index = None
    if opts.start_index:
        start_index = int(opts.start_index)

    if start_index is not None and start_index < 0:
        log('Start index must be a nonnegative integer.')
        sys.exit(-1)

    end_index = None
    if opts.end_index:
        end_index = int(opts.end_index)

    if end_index is not None:
        if start_index is not None and end_index < start_index:
            log('End index must be >= start_index.')
            sys.exit(-1)
        elif end_index < 0:
            log('End index must be a nonnegative integer.')
            sys.exit(-1)

    json_file = opts.filepath
    if not os.path.isfile(json_file):
        log("File not found: '{0}'".format(json_file))
        sys.exit(-1)

    try:
        infile = open(json_file, 'rt')
        file_data = json.load(infile)
    except:
        log("Could not open file {0}.".format(json_file))
        sys.exit(-1)

    infile.close()

    if opts.debug:
        seg_helper.enable_debug()

    # explicitly initialize for interactive testing
    seg_helper.init()
        
    ok = True
    index = 0
    while (ok):

        if start_index is not None and index < start_index:
           index += 1
           continue

        try:
            if 'response' in file_data and 'docs' in file_data['response']:
                # json file has a Solr query response header
                report = file_data['response']['docs'][index]['report_text']
            else:
                # assume json file is just an array of docs
                report = file_data[index]['report_text']
        except:
            ok = False
            break

        sentences = seg_obj.parse_sentences(report)

        # print all sentences for this report
        count = 0
        log('\nSENTENCES: ')
        for s in sentences:
            log('[{0:3}]\t{1}'.format(count, s))
            count = count + 1

        log("\n\n*** END OF REPORT {0} ***\n\n".format(index))

        index += 1

        if end_index is not None and index > end_index:
            break

    log("Processed {0} reports.".format(index))
