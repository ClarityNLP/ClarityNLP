#!/usr/bin/env python3
"""


OVERVIEW:


This module attempts to improve sentence tokenization results. It replaces
text that the spaCy sentence tokenizer erroneously splits apart with single-word
tokens that cannot be split. The original text is replaced after the sentence
tokenizer generates its results.


OUTPUT:


A list of sentence strings.


USAGE:


The 'run' function does the main work of the module. Run takes two arguments:

    report:        the text to be tokenized into sentences
    segmentation:  an instance of the ClarityNLP Segmentation() class


To use this code as an imported module, add the following lines to the
import list in the importing module:

        import segmentation_helper


The module can also be run from the command line. It will process a JSON file,
extract the 'report_text' field, split it into sentences, and print each
sentence to the screen. Help for command line operation can be obtained with
this command:

        python3 ./segmentation_helper.py --help


For example, to process all reports in myfile.json:

        python3 ./segmentation_helper.py -f /path/to/myfile.json

To process only the first 10 reports (indices begin with 0):

        python3 ./segmentation_helper.py -f myfile.json --end 9


"""

import re
import os
import sys
import json
import spacy
import optparse
import segmentation as seg

# imports from other ClarityNLP modules
try:
    # for normal operation via NLP pipeline
    from algorithms.finder.date_finder import run as \
        run_date_finder, DateValue, EMPTY_FIELD as EMPTY_DATE_FIELD
    from algorithms.finder.size_measurement_finder import run as \
        run_size_measurement, SizeMeasurement, EMPTY_FIELD as EMPTY_SMF_FIELD
except Exception as e:
    # If here, this module was executed directly from the segmentation
    # folder for testing. Construct path to nlp/algorithms/finder and
    # perform the imports above. This is a hack to allow an import from
    # higher-level package.
    this_module_dir = sys.path[0]
    pos = this_module_dir.find('/nlp')
    assert -1 != pos
    # get path to nlp/algorithms/finder and append to sys.path
    nlp_dir =  this_module_dir[:pos+4]
    finder_dir = os.path.join(nlp_dir, 'algorithms', 'finder')
    sys.path.append(finder_dir)
    from date_finder import run as run_date_finder, \
        DateValue, EMPTY_FIELD as EMPTY_DATE_FIELD
    from size_measurement_finder import run as \
        run_size_measurement, SizeMeasurement, EMPTY_FIELD as \
        EMPTY_SMF_FIELD

VERSION_MAJOR = 0
VERSION_MINOR = 1

# set to True to enable debug output
TRACE = False

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
str_list_start = r'\b(?P<listnum>\d+(\.|\)))\s+'
str_list_item = str_list_start + r'([A-Z][a-z]+|\d)\b'
regex_list_start = re.compile(str_list_start)
regex_list_item  = re.compile(str_list_item)

# find captialized headers
str_caps_word = r'\b([123]-?D|[-_A-Z]+|[-_A-Z]+/[-_A-Z]+)\b'
str_caps_header = r'(' + str_caps_word + r'\s+)*' + str_caps_word + r'\s*#?:'
regex_caps_header = re.compile(str_caps_header)

# find concatenated sentences with no space after the period

# need at least two chars before '.', to avoid matching C.Diff, M.Smith, etc.
# neg lookahead prevents capturing inside abbreviations such as Sust.Rel.
regex_two_sentences = re.compile(r'\b[a-zA-Z]{2,}\.[A-Z][a-z]+(?!\.)')

# prescription information
str_word         = r'\b[-a-z]+\b'
str_words        = r'(' + str_word + r'\s*)*' + str_word
str_drug_name    = r'\b[-A-Za-z]+(/[-A-Za-z]+)?\b'
str_amount_num   = r'\d+(\.\d+)?'
str_amount       = r'(' + str_amount_num + r'(/' + str_amount_num + r')?)?'
str_units        = r'\b[a-z]+\.?'
str_abbrev       = r'([a-zA-Z]\.){1,3}'
str_abbrevs      = r'(' + str_abbrev + r'\s+)*' + str_abbrev
str_prescription = str_drug_name + r'\s+' + str_amount + r'\s*' + str_units + \
                   r'\s+' + str_abbrevs + r'\s+' + str_words
regex_prescription = re.compile(str_prescription)

# vitals
str_sep      = r'([-:=\s]\s*)?'
str_temp     = r'\b(T\.?|Temp\.?|Temperature)' + str_sep +\
               r'(' + str_words + r')?' + str_amount_num + r'\s*'
str_height   = r'\b(Height|Ht\.?)' + str_sep + r'(\(in\.?\):?\s*)?' +\
               str_amount_num + r'\s*(inches|in\.?|feet|ft\.?|meters|m\.?)?\s*'
str_weight   = r'\b(Weight|Wt\.?)' + str_sep + r'(\(lbs?\.?\):?\s*)?' +\
               str_amount_num + r'\s*(grams|gm\.?|g\.?|ounces|oz\.?|pounds|lbs\.?|kilograms|kg\.?)?\s*'
str_bsa      = r'\bBSA:?\s+(\(m2\):?\s*)?' + str_amount_num + r'(\s+m2)?\s*'
str_bp       = r'\bBP' + str_sep + r'(\(mm\s+hg\):?\s*)?\d+/\d+\s*'
str_hr       = r'\b(Pulse|P|HR)' + str_sep + r'(\(bpm\):?\s*)?' + str_amount_num + r'\s*'
str_rr       = r'\bRR?' + str_sep + r'(' + str_words + r')?' + str_amount_num + r'\s*'
str_o2       = r'\b(SpO2%?|SaO2|O2Sats?|O2\s+sat|O2\s+Flow|Sats?|POx|O2)' + str_sep +\
               r'(' + str_words + r')?' + str_amount_num + r'(/bipap|\s*%?\s*)' +\
               r'((/|on\s+)?(RA|NRB)|\dL(/|\s*)?NC|on\s+\d\s*L\s+(FM|NC|RA|NRB)|/?\dL)?'
str_status   = r'\bStatus:\s+(In|Out)patient\s*'
str_vitals   = r'(' + str_temp + r'|' + str_height + r'|' + str_weight + r'|' +\
               str_bsa + r'|' + str_bp + r'|' + str_hr + r'|' + str_rr + r'|' +\
               str_status + r'|' + str_o2 + r')+'
regex_vitals = re.compile(str_vitals, re.IGNORECASE)

# abbreviations
str_weekday  = r'\b(Mon|Tues|Wed|Thurs|Thur|Thu|Fri|Sat|Sun)\.'
str_h_o      = r'\b\.?H/O'
str_r_o      = r'\br/o(ut)?'
str_with     = r'\bw/'
str_am_pm    = r'\b(a|p)\.m\.'
str_time     = r'(2[0-3]|1[0-9]|[0-9]):[0-5][0-9]\s*(a|A|p|P)(\s*\.)?(m|M)(\s*\.)?'
str_s_p      = r'\bs/p'
str_r_l      = r'\b(Right|Left)\s+[A-Z]+'
str_sust_rel = r'\bSust\.?\s*Rel\.?'
str_sig      = r'\bSig\s*:\s*[a-z0-9]+'
str_abbrev   = r'(' + str_weekday + r'|' + str_h_o + r'|' + str_r_o + r'|'   +\
               str_with + r'|' + str_time + r'|' + str_am_pm + r'|'          +\
               str_s_p + r'|' + str_r_l + r'|' + str_sust_rel + r'|'         +\
               str_sig + r')'
regex_abbrev = re.compile(str_abbrev, re.IGNORECASE)

# gender
str_gender   = r'\b(sex|gender)\s*:\s*(male|female|m\.?|f\.?)'
regex_gender = re.compile(str_gender, re.IGNORECASE)

fov_subs          = []
anon_subs         = []
contrast_subs     = []
size_meas_subs    = []
header_subs       = []
prescription_subs = []
vitals_subs       = []
abbrev_subs       = []
gender_subs       = []

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
    global abbrev_subs
    global gender_subs

    anon_subs         = []
    contrast_subs     = []
    fov_subs          = []
    size_meas_subs    = []
    header_subs       = []
    prescription_subs = []
    vitals_subs       = []
    abbrev_subs       = []
    gender_subs       = []

    report = find_substitutions(report, regex_abbrev, abbrev_subs, 'ABBREV')
    report = find_substitutions(report, regex_vitals, vitals_subs, 'VITALS')
    report = find_substitutions(report, regex_caps_header, header_subs, 'HEADER')
    report = find_substitutions(report, regex_anon, anon_subs, 'ANON')
    report = find_substitutions(report, regex_contrast, contrast_subs, 'CONTRAST')
    report = find_substitutions(report, regex_fov, fov_subs, 'FOV')
    report = find_size_meas_subs(report, size_meas_subs, 'MEAS')
    report = find_substitutions(report, regex_prescription, prescription_subs, 'PRESCRIPTION')
    report = find_substitutions(report, regex_gender, gender_subs, 'GENDER')

    if TRACE:
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
    global abbrev_subs
    global gender_subs

    # undo in reverse order from that in 'do_substitutions'

    sentence_list = replace_text(sentence_list, gender_subs)
    sentence_list = replace_text(sentence_list, prescription_subs)
    sentence_list = replace_text(sentence_list, size_meas_subs)
    sentence_list = replace_text(sentence_list, fov_subs)
    sentence_list = replace_text(sentence_list, contrast_subs)
    sentence_list = replace_text(sentence_list, anon_subs)
    sentence_list = replace_text(sentence_list, header_subs)
    sentence_list = replace_text(sentence_list, vitals_subs)
    sentence_list = replace_text(sentence_list, abbrev_subs)

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
        
    # Remove long runs of dashes, underscores, or stars
    report = re.sub(r'[-_*]{3,}', ' ', report)
    
    # collapse repeated whitespace (including newlines) into a single space
    report = re.sub(r'\s+', r' ', report)
    
    return report
    

###############################################################################
def fixup_sentences(sentence_list):
    """
    Move punctuation from one sentence to another, if necessary.
    """

    num = len(sentence_list)
    
    i = 1
    while i < num:
        s = sentence_list[i]
        if s.startswith(':') or s.startswith(','):
            # move to end of previous sentence
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
def delete_junk(sentence_list):
    """
    """

    sentences = []
    num = len(sentence_list)

    #for s in sentence_list:
    i = 0
    while i < num:
        s = sentence_list[i]

        # delete any remaining list numbering
        match = regex_list_start.match(s)
        if match:
            s = s[match.end():]

        # remove any sentences that consist of just '1.', '2.', etc.
        match = re.match(r'\A\s*\d+(\.|\))\s*\Z', s)
        if match:
            i += 1
            continue

        # remove any sentences that consist of '#1', '#2', etc.
        match = re.match(r'\A\s*#\d+\s*\Z', s)
        if match:
            i += 1
            continue

        # remove any sentences consisting entirely of symbols
        match = re.match(r'\A\s*[^a-zA-Z0-9]+\s*\Z', s)
        if match:
            i += 1
            continue

        # merge isolated age + year
        if i < num-1:
            if s.isdigit() and sentence_list[i+1].startswith('y'):
                s = s + ' ' + sentence_list[i+1]
                i += 1

        # if next sentence starts with 'now measures', merge with current
        if i < num-1:
            if sentence_list[i+1].startswith('now measures'):
                s = s + ' ' + sentence_list[i+1]
                i += 1

        sentences.append(s)
        i += 1

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

    sentences = split_concatenated_sentences(sentences)
    sentences = undo_substitutions(sentences)
    sentences = fixup_sentences(sentences)
    sentences = split_section_headers(sentences)
    sentences = delete_junk(sentences)

    return sentences


###############################################################################
def run_tests():

    segmentation = seg.Segmentation()

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

    count = 0
    for s in SENTENCES:
        print(s)
        sentences = run(s, segmentation)
        print('\t[{0:3}]\t{1}\n'.format(count, s))
        count += 1


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(MODULE_NAME, VERSION_MAJOR, VERSION_MINOR)


###############################################################################
def show_help():
    print(get_version())
    print("""
    USAGE: python3 ./{0} -f <filename> [-s <start_index> -e <end_index>] [-hvz]

    OPTIONS:

        -f, --file     <quoted string>     Path to input JSON file.
        -s, --start    <integer>           Index of first record to process.
        -e, --end      <integer>           Index of final record to process.
                                           Indexing begins at 0.

    FLAGS:

        -h, --help           Print this information and exit.
        -v, --version        Print version information and exit.
        -z, --selftest       Run self-tests and exit.

    """.format(MODULE_NAME))


###############################################################################
if __name__ == '__main__':

    optparser = optparse.OptionParser(add_help_option=False)
    optparser.add_option('-f', '--file', action='store',
                         dest='filepath')
    optparser.add_option('-s', '--start', action='store',
                         dest='start_index')
    optparser.add_option('-e', '--end', action='store',
                         dest='end_index')
    optparser.add_option('-v', '--version',  action='store_true',
                         dest='get_version')
    optparser.add_option('-h', '--help',     action='store_true',
                         dest='show_help', default=False)
    optparser.add_option('-z', '--selftest', action='store_true',
                         dest='selftest', default=False)

    opts, other = optparser.parse_args(sys.argv)

    if 1 == len(sys.argv) or opts.show_help:
        show_help()
        sys.exit(0)

    if opts.get_version:
        print(get_version())
        sys.exit(0)

    if opts.selftest:
        run_tests()
        sys.exit(0)

    start_index = None
    if opts.start_index:
        start_index = int(opts.start_index)

    if start_index is not None and start_index < 0:
        print('Start index must be a nonnegative integer.')
        sys.exit(-1)

    end_index = None
    if opts.end_index:
        end_index = int(opts.end_index)

    if end_index is not None:
        if start_index is not None and end_index < start_index:
            print('End index must be >= start_index.')
            sys.exit(-1)
        elif end_index < 0:
            print('End index must be a nonnegative integer.')
            sys.exit(-1)

    json_file = opts.filepath
    if not os.path.isfile(json_file):
        print("File not found: '{0}'".format(json_file))
        sys.exit(-1)

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

        if start_index is not None and index < start_index:
           index += 1
           continue

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

        if end_index is not None and index > end_index:
            break

    print("Processed {0} reports.".format(index))
    
