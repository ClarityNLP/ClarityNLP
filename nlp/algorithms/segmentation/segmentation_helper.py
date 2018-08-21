#!/usr/bin/env python3
"""

This is a helper module for segmentation.py.

For import only.

"""

import re
import os
import sys
import json

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
def enable_debug():
    global TRACE
    TRACE = True


###############################################################################
def disable_debug():
    global TRACE
    TRACE = False


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
    report = re.sub(r'\s+', ' ', report)
    
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
    Put an all caps section header in a separate sentence from the subsequent
    text.
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
def get_version():
    return '{0} {1}.{2}'.format(MODULE_NAME, VERSION_MAJOR, VERSION_MINOR)

