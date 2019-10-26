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
import argparse
import en_core_web_sm as english_model
from nltk.tokenize import sent_tokenize

if __name__ == '__main__':

    # interactive testing; add nlp dir to path to find logging class
    match = re.search(r'nlp/', sys.path[0])
    if match:
        nlp_dir = sys.path[0][:match.end()]
        sys.path.append(nlp_dir)
    else:
        print('\n*** test_lab_value_matcher.py: nlp dir not found ***\n')
        sys.exit(0)
    
    import segmentation_helper as seg_helper
else:
    from algorithms.segmentation import segmentation_helper as seg_helper

from claritynlp_logging import log, ERROR, DEBUG


_VERSION_MAJOR = 0
_VERSION_MINOR = 3
_MODULE_NAME = 'segmentation.py'

_data = {}
_loading_status = 'none'


###############################################################################
def segmentation_init(tries=0):
    if tries > 0:
        log('Retrying, try%d' % tries)

    global _loading_status
    if _loading_status == 'none' and 'nlp' not in _data:
        try:
            log('Segmentation init...')
            _loading_status = 'loading'
            _data['nlp'] = english_model.load()
            _loading_status = 'done'
        except Exception as exc:
            log(exc, ERROR)
            _loading_status = 'none'
    elif _loading_status == 'loading' and tries < 30:
        time.sleep(10)
        if _loading_status == 'loading':
            new_tries = tries + 1
            return segmentation_init(tries=new_tries)

    return _data['nlp']


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
def get_version():
    str1 = '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)
    str2 = seg_helper.get_version()
    version = '{0}\n{1}'.format(str1, str2)
    return version


###############################################################################
if __name__ == '__main__':

    # interactive testing, output written to stdout
    
    seg_obj = Segmentation()

    parser = argparse.ArgumentParser(
        description='load Solr docs (JSON format) and display sentence ' \
        'tokenization results')

    parser.add_argument('-v', '--version',
                        help='show version and exit',
                        action='store_true')
    parser.add_argument('-d', '--debug',
                        help='print debug information to stdout',
                        action='store_true')
    parser.add_argument('-f', '--file',
                        dest='filepath',
                        help='JSON file of Solr docs')
    parser.add_argument('-s', '--start',
                        type=int,
                        default=0,
                        dest='start_index',
                        help='index of first document to process')
    parser.add_argument('-e', '--end',
                        dest='end_index',
                        help='index of final document to process')

    args = parser.parse_args()

    if args.version:
        print(get_version())
        sys.exit(0)

    start_index = args.start_index
        
    if start_index < 0:
        print('\n*** Start index must be a nonnegative integer. ***')
        sys.exit(-1)

    end_index = None
    if args.end_index:
        end_index = int(args.end_index)

    if end_index is not None:
        if end_index < start_index:
            print('\n*** End index must be >= start_index. ***')
            sys.exit(-1)
        elif end_index < 0:
            print('\n*** End index must be a nonnegative integer. ***')
            sys.exit(-1)

    if args.filepath is None:
        print('\n*** Missing --file argument ***')
        sys.exit(-1)

    json_file = args.filepath
    if not os.path.isfile(json_file):
        print('\n*** File not found: "{0}" ***'.format(json_file))
        sys.exit(-1)
        

    try:
        infile = open(json_file, 'rt')
        file_data = json.load(infile)
    except:
        print('\n*** Could not open file "{0}" ***.'.format(json_file))
        sys.exit(-1)

    infile.close()

    if args.debug:
        seg_helper.enable_debug()

    try:
        infile = open(json_file, 'rt')
        file_data = json.load(infile)
    except:
        log("Could not open file {0}.".format(json_file))
        sys.exit(-1)

    infile.close()

    # explicitly initialize for interactive testing
    seg_helper.init()
        
    ok = True
    report_count = 0
    index = start_index
    while (ok):

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
        print('\nSENTENCES: ')
        for s in sentences:
            print('[{0:3}]\t{1}'.format(count, s))
            count = count + 1

        print("\n\n*** END OF REPORT {0} ***\n\n".format(index))

        index += 1
        report_count += 1
        
        if end_index is not None and index > end_index:
            break

    term = 'reports'
    if 1 == report_count:
        term = 'report'
    print("Processed {0} {1}.".format(report_count, term))
