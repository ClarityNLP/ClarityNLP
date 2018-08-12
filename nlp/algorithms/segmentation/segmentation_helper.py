#!/usr/bin/env python3

# PROBLEMS in radiology_1000.json:
# report 38: ANON000 still present
# report 39: dispensing info messed up
# report 47, sentences 4-6: vitals broken up
# report 50: sentence starts with comma, could merge
# report 55: .H/O broken up
# report 67 sentence 13-15: single word sentences, could merge
# report 68 sentence 11: 10:20 a.m. broken up
# report 82 sentence 4: sentence split after Mon. abbreviation
# report 76 sentence 6: parenthetical expressions broken up
# report 90 sentence 22: still have list numbering
# report 91 sentence 38: measurement broken up

import re
import os
import sys
import json
import spacy
import segmentation as seg

module_dir = sys.path[0]
pos = module_dir.find('/nlp')
assert -1 != pos
# get path to nlp/algorithms/finder and append
nlp_dir =  module_dir[:pos+4]
finder_dir = os.path.join(nlp_dir, 'algorithms', 'finder')
sys.path.append(finder_dir)
from date_finder import run as run_date_finder, \
    DateValue, EMPTY_FIELD as EMPTY_DATE_FIELD
from size_measurement_finder import run as \
    run_size_measurement, SizeMeasurement, EMPTY_FIELD as \
    EMPTY_SMF_FIELD

VERSION_MAJOR = 0
VERSION_MINOR = 1

MODULE_NAME = 'segmentation_helper.py'

# load spacy's English model
nlp = spacy.load('en')

# regex for locating an anonymized item [** ... **]
str_anon = r'\[\*\*[^\]]+\]'
regex_anon = re.compile(str_anon)

# regex for locating a contrast agent expression
str_contrast = r'\bContrast:\s+(None|[a-zA-Z]+\s+Amt:\s+\d+(cc|CC)?)'
regex_contrast = re.compile(str_contrast)

# regex for locating a field of view expression
str_fov = r'\bField of view:\s+\d+'
regex_fov = re.compile(str_fov)

# numbered lists (for up to 9 items), denoted by period or right parens
str_list_item = r'(?P<listnum>[1-9](\.|\)))\s+[^\d]+\.'
regex_list_item = re.compile(str_list_item)

# find concatenated sentences with no space after the period

# need at least two chars before '.', to avoid matching C.Diff, M.Smith, etc.
# neg lookahead prevents capturing inside abbreviations such as Sust.Rel.
regex_two_sentences = re.compile(r'\b[a-zA-Z]{2,}\.[A-Z][a-z]+(?!\.)')

fov_subs       = []
anon_subs      = []
contrast_subs  = []
size_meas_subs = []


###############################################################################
def find_size_meas_subs(report, sub_list, text):
    """
    """

    json_string = run_size_measurement(report)
    if '[]' == json_string:
        return report
    
    json_data = json.loads(json_string)

    # unpack JSON result into a list of SizeMeasurement namedtuples
    measurements = [SizeMeasurement(**m) for m in json_data]

    counter = 0
    prev_end = 0
    new_report = ''
    for m in measurements:
        chunk1 = report[prev_end:m.start]
        replacement = '{0}{1:03}'.format(text, counter)
        new_report += chunk1 + replacement
        prev_end = m.end
        sub_list.append( (replacement, m.text) )
        counter += 1
    new_report += report[prev_end:]

    return new_report


###############################################################################
def find_substitutions(report, regex, sub_list, text):
    """
    """

    subs = []

    iterator = regex.finditer(report)
    for match in iterator:
        subs.append( (match.start(), match.end(), match.group()) )

    if 0 == len(subs):
        return report

    # counter = 0
    # for match_text in subs:
    #     replacement = '{0}{1:03}'.format(text, counter)
    #     report = report.replace(match_text, replacement)
    #     sub_list.append( (replacement, match_text) )
    #     counter += 1
    
    counter = 0
    prev_end = 0
    new_report = ''
    for start, end, match_text in subs:
        chunk1 = report[prev_end:start]
        replacement = '{0}{1:03}'.format(text, counter)
        new_report += chunk1 + replacement
        prev_end = end
        sub_list.append( (replacement, match_text) )
        counter += 1
    new_report += report[prev_end:]

    return new_report
        
        
###############################################################################
def do_substitutions(report):
    """
    """

    global anon_subs
    global contrast_subs
    global fov_subs
    global size_meas_subs

    anon_subs      = []
    contrast_subs  = []
    fov_subs       = []
    size_meas_subs = []
    
    report = find_substitutions(report, regex_anon, anon_subs, 'ANON')
    report = find_substitutions(report, regex_contrast, contrast_subs, 'CONTRAST')
    report = find_substitutions(report, regex_fov, fov_subs, 'FOV')
    report = find_size_meas_subs(report, size_meas_subs, 'MEAS')

    #print('REPORT AFTER SUBSTITUTIONS: \n' + report)
    return report


###############################################################################
def replace_text(sentence_list, sub_list):
    """
    """

    num = len(sentence_list)
    for i in range(num):
        count = 0
        replacements = []
        sentence = sentence_list[i]
        for entry in sub_list:
            sub = entry[0]
            orig = entry[1]
            if -1 != sentence.find(sub):
                sentence = sentence.replace(sub, orig)
                replacements.append(sub)
                count += 1

        # remove used entries from sub_list
        if count > 0:
            sub_list = sub_list[count:]

        # update the sentence in the sentence list
        if len(replacements) > 0:
            sentence_list[i] = sentence

    return sentence_list
            

###############################################################################
def undo_substitutions(sentence_list):
    """
    """

    global anon_subs
    global contrast_subs
    global fov_subs
    global size_meas_subs    

    # undo in reverse order from that in 'do_substitutions'
    sentence_list = replace_text(sentence_list, size_meas_subs)
    sentence_list = replace_text(sentence_list, fov_subs)
    sentence_list = replace_text(sentence_list, contrast_subs)
    sentence_list = replace_text(sentence_list, anon_subs)

    return sentence_list
        

###############################################################################
def erase_spans(report, span_list):
    """
    Erase all report chars bounded by each [start, end) span.
    """

    if len(span_list) > 0:
        prev_end = 0
        new_report = ''
        for span in span_list:
            start = span[0]
            end   = span[1]
            new_report += report[prev_end:start]
            prev_end = end
        new_report += report[prev_end:]
        report = new_report

    return report


###############################################################################
def cleanup_report(report):
    """
    """

    # remove (Over) ... (Cont) inserts
    spans = []
    iterator = re.finditer(r'\(Over\)', report)
    for match_over in iterator:
        start = match_over.start()
        chunk = report[match_over.end():]
        match_cont = re.search(r'\(Cont\)', chunk)
        if match_cont:
            end = match_over.end() + match_cont.end()
            spans.append( (start, end))
            
    report = erase_spans(report, spans)

    # remove numbering in lists
    spans = []
    iterator = regex_list_item.finditer(report)
    for match in iterator:
        start = match.start('listnum')
        end   = match.end('listnum')
        spans.append( (start, end))

    report = erase_spans(report, spans)
        
    # Remove long runs of dashes and/or underscores
    report = re.sub(r'[-_]{3,}', ' ', report)
    
    # collapse repeated whitespace (including newlines) into a single space
    report = re.sub(r'\s+', r' ', report)
    
    return report
    

###############################################################################
def merge_broken_headers(sentence_list):
    """
    Merge any sentences that begin with a colon.
    """

    num = len(sentence_list)
    
    i = 1
    while i < num:
        s = sentence_list[i]
        if s.startswith(':'):
            sprev = sentence_list[i-1]
            sentence_list[i-1] = sprev + ':'
            sentence_list[i]   = s[1:].lstrip()
        i += 1
            
    return sentence_list


###############################################################################
def split_section_headers(sentence_list):
    """
    """

    str_header_word = r'[-_A-Z/]{3,}'
    str_header = r'\b(' + str_header_word + r'\s+)*' + str_header_word + r'\s*:\s*'
    regex_header = re.compile(str_header)
    
    sentences = []

    for s in sentence_list:
        match = regex_header.search(s)
        if match:
            before = s[:match.start()]
            header = match.group()
            after  = s[match.end():]
            if len(before) > 0:
                sentences.append(before)
            sentences.append(header)
            if len(after) > 0:
                sentences.append(after)
        else:
            sentences.append(s)

    return sentences
        

###############################################################################
def split_concatenated_sentences(sentence_list):
    """
    """

    sentences = []
    for s in sentence_list:
        match = regex_two_sentences.search(s)
        if match:
            s1 = s[:match.end()]
            s2 = s[match.end():]
            sentences.append(s1)
            sentences.append(s2)
        else:
            sentences.append(s)

    return sentences


###############################################################################
def delete_junk_sentences(sentence_list):
    """
    """

    sentences = []
    
    for s in sentence_list:
        # delete sentences consisting of a number followed by '.' or ')'
        if re.match(r'\A\d(\.|\))\Z', s):
            continue
        else:
            sentences.append(s)

    return sentences


###############################################################################
def show_help():
    print ("""\nUsage: python3 ./{0} <report_file.json> [report_count] """.
           format(MODULE_NAME))
    print()
    print("\tThe 'report_file' argument is required, must be JSON format.")
    print("\tUse 'report_count' to limit the number of reports processed, " \
          "must be an integer.")
    print()
    print("\tFor example, to process 15 reports:")
    print("\n\t\tpython3 ./{0} reports.json 15".format(MODULE_NAME))
    print()
    

###############################################################################
if __name__ == '__main__':

    if 1 == len(sys.argv):
        show_help()
        sys.exit(0)

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
        print("Could not open file {0}.".format(json_file))
        sys.exit(-1)

    infile.close()

    segmentation = seg.Segmentation()
    
    ok = True
    index = 0
    while (ok):
        try:
            report = data['response']['docs'][index]['report_text']
        except:
            ok = False
            break

        clean_report = cleanup_report(report)
        clean_report = do_substitutions(clean_report)

        sentences = segmentation.parse_sentences(clean_report)

        sentences = merge_broken_headers(sentences)
        sentences = split_section_headers(sentences)
        sentences = split_concatenated_sentences(sentences)
        sentences = delete_junk_sentences(sentences)

        sentences = undo_substitutions(sentences)
        
        count = 0
        for s in sentences:
            print('[{0:3}]\t{1}'.format(count, s))
            count = count + 1
        
        print("\n\n*** END OF REPORT {0} ***\n\n".format(index))
        
        index += 1
        if max_reports > 0 and index >= max_reports:
            break

    print("Processed {0} reports.".format(index))
    
