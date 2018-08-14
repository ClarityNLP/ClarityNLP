#!/usr/bin/env python3

# PROBLEMS in radiology_1000.json:
# report 39: dispensing info messed up
# report 47, sentences 4-6: vitals broken up
# report 50: sentence starts with comma, could merge
# report 55: .H/O broken up
# report 61 sentences 5-6: no need to split on w/
# report 67 sentence 13-15: single word sentences, could merge
# report 68 sentence 11: 10:20 a.m. broken up
# report 82 sentence 4: sentence split after Mon. abbreviation
# report 76 sentence 6: parenthetical expressions broken up

import re
import os
import sys
import json
import spacy
import segmentation as seg

module_dir = sys.path[0]
pos = module_dir.find('/nlp')
assert -1 != pos
# get path to nlp/algorithms/finder and append to sys.path
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

# find numbered sentences: look for digits followed by '.' or ')',
# whitespace, then a capital letter starting a word
str_list_item = r'\b(?P<listnum>\d+(\.|\)))\s+[A-Z][a-z]+\b'
regex_list_item = re.compile(str_list_item)

# find captialized headers
str_caps_word = r'\b([123]-?D|[-_A-Z]+|[-_A-Z]+/[-_A-Z]+)\b'
str_caps_header = r'(' + str_caps_word + r'\s+)*' + str_caps_word + r'\s*#?:'
regex_caps_header = re.compile(str_caps_header)

# find concatenated sentences with no space after the period

# need at least two chars before '.', to avoid matching C.Diff, M.Smith, etc.
# neg lookahead prevents capturing inside abbreviations such as Sust.Rel.
regex_two_sentences = re.compile(r'\b[a-zA-Z]{2,}\.[A-Z][a-z]+(?!\.)')

# prescription information
str_word       = r'\b[-a-z]+\b'
str_words      = r'(' + str_word + r'\s*)*' + str_word
str_drug_name  = r'\b[-A-Za-z]+(/[-A-Za-z]+)?\b'
#str_amount_num = r'(\d+|0\.\d+|\d+\.\d+)'
str_amount_num = r'\d+(\.\d+)?'
#str_amount     = r'(' + str_amount_num + r'(/' + str_amount_num + r')?' +\
#                 r'|' + str_words + r')'
str_amount    = r'(' + str_amount_num + r'(/' + str_amount_num + r')?)?'
str_units     = r'\b[a-z]+\.?'
str_abbrev    = r'([a-zA-Z]\.){1,3}'
str_abbrevs   = r'(' + str_abbrev + r'\s+)*' + str_abbrev
str_prescription = str_drug_name + r'\s+' + str_amount + r'\s*' + str_units + \
                   r'\s+' + str_abbrevs + r'\s+' + str_words
regex_prescription = re.compile(str_prescription)

# vitals
str_sep      = r'([-:=\s]\s*)?'
str_temp     = r'\b(T\.?|Temp\.?|Temperature)' + str_sep +\
               r'(' + str_words + r')?' + str_amount_num + r'\s*'
str_height   = r'\bHeight:?\s+(\(in\.?\):?\s*)?' + str_amount_num + r'\s*'
str_weight   = r'\bWeight:?\s+(\(lbs?\.?\):?\s*)?' + str_amount_num + r'\s*'
str_bsa      = r'\bBSA:?\s+(\(m2\):?\s*)?' + str_amount_num + r'(\s+m2)?\s*'
str_bp       = r'\bBP' + str_sep + r'(\(mm\s+hg\):?\s*)?\d+/\d+\s*'
str_hr       = r'\b(P|HR)' + str_sep + r'(\(bpm\):?\s*)?' + str_amount_num + r'\s*'
str_rr       = r'\bRR?' + str_sep + r'(' + str_words + r')?' + str_amount_num + r'\s*'
str_o2       = r'\b(O2|SpO2|SaO2|O2Sats?|O2\s+sat|Sats?)' + str_sep +\
               r'(' + str_words + r')?' + str_amount_num + r'\s*%?\s*' +\
               r'(/\dL|(on\s+)?RA|\dL(/|\s*)?NC)?'
str_status   = r'\bStatus:\s+(In|Out)patient\s*'
str_vitals   = r'(' + str_temp + r'|' + str_height + r'|' + str_weight + r'|' +\
               str_bsa + r'|' + str_bp + r'|' + str_hr + r'|' + str_rr + r'|' +\
               str_status + r'|' + str_o2 + r')+'
regex_vitals = re.compile(str_vitals, re.IGNORECASE)

fov_subs          = []
anon_subs         = []
contrast_subs     = []
size_meas_subs    = []
header_subs       = []
prescription_subs = []
vitals_subs       = []

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
    global header_subs
    global prescription_subs
    global vitals_subs

    anon_subs         = []
    contrast_subs     = []
    fov_subs          = []
    size_meas_subs    = []
    header_subs       = []
    prescription_subs = []
    vitals_subs       = []

    report = find_substitutions(report, regex_vitals, vitals_subs, 'VITALS')
    report = find_substitutions(report, regex_caps_header, header_subs, 'HEADER')
    report = find_substitutions(report, regex_anon, anon_subs, 'ANON')
    report = find_substitutions(report, regex_contrast, contrast_subs, 'CONTRAST')
    report = find_substitutions(report, regex_fov, fov_subs, 'FOV')
    report = find_size_meas_subs(report, size_meas_subs, 'MEAS')
    report = find_substitutions(report, regex_prescription, prescription_subs, 'PRESCRIPTION')

    print('REPORT AFTER SUBSTITUTIONS: \n' + report + '\n')
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
    global header_subs
    global prescription_subs
    global vitals_subs

    # undo in reverse order from that in 'do_substitutions'
    sentence_list = replace_text(sentence_list, prescription_subs)
    sentence_list = replace_text(sentence_list, size_meas_subs)
    sentence_list = replace_text(sentence_list, fov_subs)
    sentence_list = replace_text(sentence_list, contrast_subs)
    sentence_list = replace_text(sentence_list, anon_subs)
    sentence_list = replace_text(sentence_list, header_subs)
    sentence_list = replace_text(sentence_list, vitals_subs)

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

    sentences = []
    for s in sentence_list:
        subs = []
        iterator = regex_caps_header.finditer(s)
        for match in iterator:
            subs.append( (match.start(), match.end()) )
        if len(subs) > 0:
            prev_end = 0
            for start, end in subs:
                before = s[prev_end:start].strip()
                header = s[start:end].strip()
                prev_end = end
                if len(before) > 0:
                    sentences.append(before)
                sentences.append(header)
            after = s[prev_end:].strip()
            if len(after) > 0:
                sentences.append(after)
        else:
            sentences.append(s)

    # str_header_word = r'[-_A-Z/]{3,}'
    # str_header = r'\b(' + str_header_word + r'\s+)*' + str_header_word + r'\s*:\s*'
    # regex_header = re.compile(str_header)

    # sentences = []

    # for s in sentence_list:
    #     match = regex_header.search(s)
    #     if match:
    #         before = s[:match.start()]
    #         header = match.group()
    #         after  = s[match.end():]
    #         if len(before) > 0:
    #             sentences.append(before)
    #         sentences.append(header)
    #         if len(after) > 0:
    #             sentences.append(after)
    #     else:
    #         sentences.append(s)

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
def run(report, segmentation=None):
    """
    Cleanup the report, do substitutions, tokenize into sentences, fixup
    problems, undo substitutions, and return the tokenized sentences.
    """

    if segmentation is None:
        segmentation = seg.Segmentation()

    report = cleanup_report(report)
    report = do_substitutions(report)

    sentences = segmentation.parse_sentences(report)

    sentences = undo_substitutions(sentences)
    sentences = merge_broken_headers(sentences)
    sentences = split_section_headers(sentences)
    sentences = split_concatenated_sentences(sentences)
    sentences = delete_junk_sentences(sentences)

    #sentences = split_section_headers(sentences)

    return sentences


###############################################################################
def run_tests():

    segmentation = seg.Segmentation()

    SENTENCES = [
        'VS: T 95.6 HR 45 BP 75/30 RR 17 98% RA.',
        'VS T97.3 P84 BP120/56 RR16 O2Sat98 2LNC',
        'Height: (in) 74 Weight (lb): 199 BSA (m2): 2.17 m2 ' +\
        'BP (mm Hg): 140/91 HR (bpm): 53',
        'Vitals: T: 99 BP: 115/68 P: 79 R:21 O2: 97',
        'Vitals - T 95.5 BP 132/65 HR 78 RR 20 SpO2 98%/3L',
        'VS: T=98 BP= 122/58  HR= 7 RR= 20  O2 sat= 100% 2L NC',
        'VS:  T-100.6, HR-105, BP-93/46, RR-16, Sats-98% 3L/NC',
        'VS - Temp. 98.5F, BP115/65 , HR103 , R16 , 96O2-sat % RA',
        'Vitals: Temp 100.2 HR 72 BP 184/56 RR 16 sats 96% on RA',
        'PHYSICAL EXAM: O: T: 98.8 BP: 123/60   HR:97    R 16  O2Sats100%',
    ]

    count = 0
    for s in SENTENCES:
        print(s)
        sentences = run(s, segmentation)
        print('\t[{0:3}]\t{1}\n'.format(count, s))
        count += 1

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

    run_tests()
    sys.exit(0)

    segmentation = seg.Segmentation()
    
    ok = True
    index = 0
    while (ok):
        try:
            report = data['response']['docs'][index]['report_text']
        except:
            ok = False
            break

        sentences = run(report, segmentation)

        # print all sentences for this report
        count = 0
        for s in sentences:
            print('[{0:3}]\t{1}'.format(count, s))
            count = count + 1
        
        print("\n\n*** END OF REPORT {0} ***\n\n".format(index))
        
        index += 1
        if max_reports > 0 and index >= max_reports:
            break

    print("Processed {0} reports.".format(index))
    
