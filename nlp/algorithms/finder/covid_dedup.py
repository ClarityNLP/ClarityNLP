#!/usr/bin/env python3
"""
This module deduplicates the case reports returned by the covid finder.

Still experimental, not yet integrated into CovidFinder custom task.

"""

import os
import re
import sys
import gzip
import json
import math
import argparse
from collections import defaultdict, namedtuple

if __name__ == '__main__':
    # interactive testing
    match = re.search(r'nlp/', sys.path[0])
    if match:
        nlp_dir = sys.path[0][:match.end()]
        sys.path.append(nlp_dir)
    else:
        path, module_name = os.path.split(__file__)
        print('\n*** {0}: nlp dir not found ***\n'.format(module_name))
        sys.exit(0)

from algorithms.finder import covid_finder
from algorithms.segmentation import segmentation
from algorithms.finder import text_number as tnum
from algorithms.segmentation import segmentation_helper as seg_helper


_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# set to True for debug output
_TRACE = False

# finds variants of "7 days ago", "/ 1 week ago", etc.
_str_sep = r'(updated\s)?(?<!\d)\d+\s(week|day|hr|min)s?\sago'
_regex_sep = re.compile(_str_sep, re.IGNORECASE)

# regex for recognizing textual numbers
_regex_tnum = re.compile(tnum.str_tnum, re.IGNORECASE)

# integers with commas
_regex_comma_num = re.compile(r'\d{1,3}(,\d\d\d)+')

_STR_THROWAWAY = r'\b(there (were|are|is)|there\'s|theres|and|an|are|as|'    \
    r'by|for a|for|isn\'t|isnt|is|it|just|nor|no|of|or|some|so|'             \
    r'such|than|that|these|the|this|those|too|to|)\b'

_EMPTY_STRING = ''
_CHAR_SPACE   = ' '

_FINDER_RESULT_FIELDS = [
    'frag', 'count', 'start', 'end',
    'sentence_index', 'cleaned_sentence', 'obj_index'
]
_FinderResult = namedtuple('_FinderResult', _FINDER_RESULT_FIELDS)


###############################################################################
def enable_debug():

    global _TRACE
    _TRACE = True
    

###############################################################################
def _split_at_positions(text, pos_list):
    """
    Split a string at the list of positions in the string and return a list
    of chunks.
    """

    chunks = []
    prev_end = 0
    for pos in pos_list:
        chunk = text[prev_end:pos]
        chunks.append(chunk)
        prev_end = pos
    chunks.append(text[prev_end:])
    return chunks


###############################################################################
def _cleanup_text(text):

    # find occurrences of ' 0\n \n...' and replace with whitespace
    # this is junk that shows up in the scraped news articles
    text = re.sub(r'\s0\s+', _CHAR_SPACE, text)
    
    # strip parenthesized or bracketed numbers, since these tend to indicate
    # numbered items in news articles
    text = re.sub(r'[\({\[]\d+[\)}\]]', _CHAR_SPACE, text)

    # insert a space in any 'word' where the capitalization changes from
    # two or more lowercase letters to an uppercase letter, or where a two or
    # more digits are adjacent to an uppercase letter
    space_pos = []
    iterator = re.finditer(r'([a-z][a-z]+|\d\d+)(?P<upper>[A-Z][a-zA-Z]+)', text)
    for match in iterator:
        # position where the space is needed
        pos = match.start('upper')
        space_pos.append(pos)
    chunks = _split_at_positions(text, space_pos)
    text = ' '.join(chunks)
    
    # collapse repeated whitespace
    text = re.sub(r'\s+', _CHAR_SPACE, text)
    return text


###############################################################################
def _split_on_regex(regex, text):
    """
    Split the given text into shorter texts using the regex match as the
    start and end of the split points. The regex matches are excluded from
    the returned list. This function exists to cleanup and remove irrelevant
    headers and similar things from scraped news articles.
    """

    sentences = []
    
    prev = 0
    iterator = regex.finditer(text)
    for match in iterator:
        start = match.start()
        end   = match.end()
        match_text = text[prev:start]
        sentences.append(match_text)
        prev = end
    sentences.append(text[prev:])
    return sentences


###############################################################################
def _extract_sentences(texts, segmentor):
    """
    Extract the UNIQUE sentences from one or more texts.
    """

    sentence_set = set()

    unique_sentences = []
    for text in texts:
        # tokenize this text into sentences
        sentences = segmentor.parse_sentences(text)
        for sentence in sentences:
            # collapse repeated whitespace
            sentence = re.sub(r'\s+', ' ', sentence)
            # do additional sentence splitting if needed
            sentences2 = _split_on_regex(_regex_sep, sentence)
            for s2 in sentences2:
                # skip empty or whitespace-only strings
                if 0 == len(s2) or s2.isspace():
                    continue
                if s2 in sentence_set:
                    # have already seen this sentence
                    continue
                else:
                    s2 = s2.strip()
                    unique_sentences.append(s2)

    if _TRACE:
        # useful to have sentences for debugging
        with open('sentences.txt', 'wt') as outfile:
            for i,s in enumerate(unique_sentences):
                outfile.write('[{0}]:\t{1}\n'.format(i, s))
                    
    return unique_sentences
                            

###############################################################################
def _print_count_map(count_map, msg):
    """
    The 'count_map' is a dict that maps an integer count to another map, the
    'frag_map'. The frag_map is another dict that maps a sentence fragment
    to a list of sentence indices for all sentences that share that fragment.
    """

    # sort the counts
    keys = sorted(count_map.keys())
    
    print()
    print('COUNT MAP {0}: '.format(msg))
    for count in keys:
        frag_map = count_map[count]
        if 0 == len(frag_map):
            continue
        print('\t{0}'.format(count))
        for frag, obj_list in frag_map.items():
            index_list = [obj.sentence_index for obj in obj_list]
            print('\t\t"{0}" => {1}'.format(frag, index_list))
    print()
    sys.stdout.flush()

    
###############################################################################
def _print_obj(obj):
    """
    Print data from a _FinderResult object to stdout.
    Used by _print_results only, mainly for debugging.
    """

    # number of border chars for each sentence
    B = 32    
    
    cleaned_sentence = obj.cleaned_sentence
    start = obj.start
    end   = obj.end
    # extract a boundary of B chars on each side of the fragment
    # pad the left chunk with whitespace to align fragments
    if start > B:
        l = '...' + cleaned_sentence[start-B+3:start]
    else:
        l = cleaned_sentence[:start]
        l = _CHAR_SPACE*(B-len(l)) + l
        assert len(l) == B
    frag = cleaned_sentence[start:end]
    assert frag == obj.frag
    if len(cleaned_sentence) - B > end:
        r = cleaned_sentence[end:end+B-3] + '...'
    else:
        r = cleaned_sentence[end:]
    display_chunk = l + '|' + frag + '|' + r
    print('\t[{0:4d}]: {1}'.format(obj.sentence_index, display_chunk))

    
###############################################################################
def _print_results(merged_dict, unmerged_dict, finder_obj_list):

    # print counts in sorted order
    dicts = [merged_dict, unmerged_dict]
    
    for i,d in enumerate(dicts):
        if 0 == i:
            print('\nMERGED (duplicates): ')
        else:
            print('\nUNMERGED (uniques): ')
        counts = sorted(d.keys())
        for count in counts:
            obj_list = d[count]
            # get CovidFinder result indices
            indices = []
            for obj in obj_list:
                indices.append(obj.obj_index)
            indices = sorted(indices)
            print('{0} cases, object indices {1}: '.format(count, indices))
            for obj in obj_list:
                _print_obj(obj)
                #print('\tvalue_case: {0}'.format(finder_obj_list[obj.obj_index]['value_case']))
        

###############################################################################
def _get_results(count_map):
    """
    """

    merged = defaultdict(list)
    unmerged = defaultdict(list)
    for count, frag_map in count_map.items():
        if 0 == len(frag_map):
            continue
        for frag, obj_list in frag_map.items():
            if len(obj_list) > 1:
                # more than one means objects in the list were merged
                merged[count].extend(obj_list)
            else:
                unmerged[count].extend(obj_list)

    return merged, unmerged

            
###############################################################################
def _build_count_map(finder_results):
    """
    """

    count_map = defaultdict(list)    
    for i, fr in enumerate(finder_results):
        count = fr.count
        if isinstance(count, float):
            # convert floating point to int if possible
            # all counts are >= 0
            int_count = int(count)
            if math.floor(count) == int_count:
                count = int_count
        count_map[count].append(i)

    # group each list according to fragments
    replacements = {}
    for count, index_list in count_map.items():
        the_map = defaultdict(list)
        for i in index_list:
            frag = finder_results[i].frag
            if len(frag) > 0:
                the_map[frag].append(finder_results[i])
        replacements[count] = the_map

    count_map = replacements

    if 1 == len(count_map):
        keys = [k for k in count_map.keys()]
        frag_map = count_map[keys[0]]
        if 0 == len(frag_map):
            return {}
    
    return count_map


###############################################################################
def _standardize_ints(text):
    """
    Replace text ints (such as 'two', 'twenty-one', etc.), and ints with commas
    or suffixes with with digit strings and return the updated text.
    """
    
    match = _regex_tnum.search(text)
    if match:
        start = match.start()
        end   = match.end()
        val   = tnum.tnum_to_int(text[start:end])
        new_text = text[:start] + _CHAR_SPACE + str(val) +\
            _CHAR_SPACE + text[end:]
        new_text = re.sub(r'\s+', _CHAR_SPACE, new_text)
        return new_text

    match = _regex_comma_num.search(text)
    if match:
        start = match.start()
        end   = match.end()
        comma_text = text[start:end]
        no_comma_text = re.sub(r',', _EMPTY_STRING, comma_text)
        val = int(no_comma_text)
        new_text = text[:start] + _CHAR_SPACE + str(val) +\
            _CHAR_SPACE + text[end:]
        return new_text

    match = re.search(r'\d+(k|m)', text)
    if match:
        start = match.start()
        end   = match.end()
        match_text = text[start:end]
        multiplier = 1000
        if match_text.endswith('m'):
            multiplier = 1000000
        no_suffix_text = match_text[:-1]
        val = multiplier * int(no_suffix_text)
        new_text = text[:start] + _CHAR_SPACE + str(val) +\
            _CHAR_SPACE + text[end:]
        return new_text
    
    return text

                
###############################################################################
def _fuzzy_match(str1, str2):
    """
    Determine whether two Covid case count fragments have the same meaning.
    """

    str_coronavirus = r'(covid([-\s]?19)?|(novel\s)?(corona)?virus|disease)' \
        r'([-\s]related)?\s?'

    # erase coronavirus string
    str1 = re.sub(str_coronavirus, _EMPTY_STRING, str1)
    str2 = re.sub(str_coronavirus, _EMPTY_STRING, str2)

    # erase qualifiers
    str_qual = r'\b((newly[-\s])?confirmed|new|positive|suspected|'         \
        r'probable|diagnosed|more( than)?|total(ed)?|active|estimated|'     \
        r'self[-\s]reported|reported|additional|nearly|daily|over|'         \
        r'number of|remain at)\b'
    
    str1 = re.sub(str_qual, _EMPTY_STRING, str1)
    str2 = re.sub(str_qual, _EMPTY_STRING, str2)

    # convert ints to numeric digits only
    str1 = _standardize_ints(str1)
    str2 = _standardize_ints(str2)

    # remove throwaways
    str1 = re.sub(_STR_THROWAWAY, _EMPTY_STRING, str1)
    str2 = re.sub(_STR_THROWAWAY, _EMPTY_STRING, str2)

    # remove 'case' or 'cases'
    str_case = r'\bcase(s)?\b'
    str1 = re.sub(str_case, _EMPTY_STRING, str1)
    str2 = re.sub(str_case, _EMPTY_STRING, str2)
    
    # collapse repeated whitspace
    str1 = re.sub(r'\s+', _CHAR_SPACE, str1).strip()
    str2 = re.sub(r'\s+', _CHAR_SPACE, str2).strip()

    set1 = set(str1.split())
    set2 = set(str2.split())
    
    if str1 == str2:
        return True

    # if _TRACE:
    #     print('NO FUZZY MATCH: ')
    #     print('\tstr1: "{0}"'.format(str1))
    #     print('\tstr2: "{0}"'.format(str2))

    return False
            

###############################################################################
def _process_texts(raw_texts, segmentor):
    """
    Performs the main work of this module. After cleaning each text and
    breaking it into sentences, the covid finder module examines each sentence
    looking for covid case reports. If it finds any, data from each result is
    saved to 'finder_results'. These finder results are grouped by case count.
    A fuzzy matching procedure is performed on each covid case report fragment.
    Any fragments deemed to be identical by the fuzzy matcher are regarded
    as duplicates and are merged into a particular data structure. The 
    duplicates and uniques are returned.
    """
    
    print(filepath)

    # perform covid-specific cleanup on all texts
    cleaned_texts = []
    for raw in raw_texts:
        cleaned = _cleanup_text(raw)
        cleaned_texts.append(cleaned)

    sentences = _extract_sentences(cleaned_texts, segmentor)
    if 0 == len(sentences):
        if _TRACE:
            print('\t*** NO SENTENCES FOUND ***')
        return

    if _TRACE:
        print('Found {0} unique sentences.'.format(len(sentences)))

    # list of (case_count_fragment, count) tuples
    finder_results = []

    # list of decoded CovidFinder objects
    # items are in 1-1 correspondence with finder_results
    finder_obj_list = []

    for sentence_index, sentence in enumerate(sentences):
        # run the covid finder and decode results
        json_result = covid_finder.run(sentence)
        data = json.loads(json_result)
        if 0 == len(data):
            continue
        else:
            # extract case info
            for d in data:
                count = d['value_case']
                if count is None:
                    continue
                cleaned_sentence = d['sentence']
                start = d['case_start']
                end = d['case_end']
                
                # save the case count fragment
                frag = cleaned_sentence[start:end]
                fr = _FinderResult(
                    frag,
                    count,
                    start,
                    end,
                    sentence_index,
                    cleaned_sentence,
                    # the decoded CovidFinder object that generated this result
                    # will be located at this index in the 'finder_results' list
                    obj_index = len(finder_results)
                )
                finder_results.append(fr)
                finder_obj_list.append(d)

    # collect all items having identical counts
    count_map = _build_count_map(finder_results)

    # if _TRACE:
    #     _print_count_map(count_map, '(BEFORE)')    

    # perform a fuzzy match on fragments with identical counts
    # rearranges the frag_map for each count
    unmatched = []
    for count, frag_map in count_map.items():
        # get all fragments having this count
        fragment_list = [k for k in frag_map.keys()]
        num_fragments = len(fragment_list)
        if 1 == num_fragments:
            continue

        # check all fragment pairs for fuzzy match
        to_merge = []
        for i in range(num_fragments):
            for j in range(i+1, num_fragments):
                frag_i = fragment_list[i]
                frag_j = fragment_list[j]

                identical = _fuzzy_match(frag_i, frag_j)
                if identical:
                    to_merge.append( (i, j) )
                    # if _TRACE:
                    #     print('fuzzy match: ')
                    #     print('\t"{0}"\n\t"{1}"'.format(frag_i, frag_j))

        if len(to_merge) > 0:
            
            # if _TRACE:
            #     print('TO MERGE: ')
            #     for i,j in to_merge:
            #         print('({0}, {1})'.format(i, j))

            # associate all mapped indices with each other, bidirectional
            merge_map = defaultdict(list)
            for i,j in to_merge:
                merge_map[i].append(j)
                merge_map[j].append(i)

            # if _TRACE:
            #     print('MERGE MAP: ')
            #     for i,j_list in merge_map.items():
            #         print('({0} => {1})'.format(i, j_list))

            # partition the mapped indices into sets
            merge_sets = []
            for i,j_list in merge_map.items():
                set_i = {i}
                for j in j_list:
                    set_i.add(j)
                if set_i not in merge_sets:
                    merge_sets.append(set_i)

            # if _TRACE:
            #     print('MERGE SETS: ')
            #     for s in merge_sets:
            #         print(s)

            # collect all fragments of mapped indices
            for s in merge_sets:
                s_list = list(s)
                assert len(s_list) > 0
                i = s_list[0]
                frag_i = fragment_list[i]
                for k in range(1, len(s_list)):
                    j = s_list[k]
                    frag_j = fragment_list[j]
                    frag_map[frag_i].extend(frag_map[frag_j])
                    del frag_map[frag_j]

        # remove any duplicates in the fragment lists
        for k in frag_map.keys():
            v = frag_map[k]
            frag_map[k] = sorted(list(set(v)))

    if _TRACE:
        _print_count_map(count_map, '(AFTER)')

    # find merged (duplicated) and unmerged (unique) objects
    duplicate_dict, unique_dict = _get_results(count_map)

    if _TRACE:
        _print_results(duplicate_dict, unique_dict, finder_obj_list)

    return duplicate_dict, unique_dict, finder_obj_list
    

###############################################################################
def _extract_texts_from_file(filepath):
    """
    """
    
    _KEY_TEXT = 'full_text'

    # get raw text
    raw_json = None
    if filepath.endswith('.json'):
        with open(filepath, 'rt') as infile:
            raw_json = infile.read()
    elif filepath.endswith('.json.gz'):
        with gzip.open(filepath, 'rb') as infile:
            raw_json = infile.read()
    
    # decode the entire json string
    obj = json.loads(raw_json)

    # extract raw text of all articles
    raw_texts = []
    for i,doc in enumerate(obj):
        if _KEY_TEXT in doc:
            text = doc[_KEY_TEXT]
            if text is None:
                continue
            if len(text) > 0 and not text.isspace():
                raw_texts.append(text)

    return raw_texts
                

###############################################################################
def _process_directory(directory, segmentor):
    """
    """

    # list all items in the specified directory
    for d in os.listdir(directory):
        fullpath = os.path.join(directory, d)
        if os.path.isdir(fullpath):
            # list all items in this subdir
            for f in os.listdir(fullpath):
                filepath = os.path.join(fullpath, f)
                if os.path.isfile(filepath):
                        raw_texts = _extract_texts_from_file(filepath)
                        duplicate_dict, unique_dict, finder_obj_list = _process_texts(raw_texts,
                                                                                      segmentor)
                        
                    
###############################################################################
def _get_version():
    path, module_name = os.path.split(__file__)
    return '{0} {1}.{2}'.format(module_name, _VERSION_MAJOR, _VERSION_MINOR)
                                                                

###############################################################################
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='deduplicate Covid-19 outbreak data')

    parser.add_argument('-v', '--version',
                        action='store_true',
                        help='show version information and exit')
    parser.add_argument('--debug',
                        action='store_true',
                        help='print debug information to stdout')
    parser.add_argument('-f', '--file',
                        dest='filepath',
                        help='data file from Covid news scraper, .json or .json.gz')
    parser.add_argument('-d', '--dir',
                        dest='directory',
                        help='directory of files from Covid news scraper')
    
    args = parser.parse_args()

    if 'version' in args and args.version:
        print(_get_version())
        sys.exit(0)

    if 'debug' in args and args.debug:
        enable_debug()

    filepath = None
    directory = None

    if args.filepath is not None:
        filepath = args.filepath
        if not os.path.isfile(filepath):
            print('\n*** File not found: "{0}" ***'.format(filepath))
            sys.exit(-1)

    if args.directory is not None:
        directory = args.directory
        if not os.path.isdir(directory):
            print('\n*** Directory not found: "{0}" ***'.format(directory))
            sys.exit(-1)

    # either a file or dir must be specified, not both
    if (filepath is not None and directory is not None) or \
       (filepath is None and directory is None):
        print('\n*** Specify EITHER an input file or a directory. ***')
        sys.exit(-1)
        
    segmentor = segmentation.Segmentation()
    seg_helper.init()

    if filepath is not None:
        #_process_file(filepath, segmentor)
        raw_texts = _extract_texts_from_file(filepath)
        _process_texts(raw_texts, segmentor)
    else:
        _process_directory(directory, segmentor)
    sys.exit(0)
