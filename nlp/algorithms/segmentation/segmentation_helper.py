#!/usr/bin/env python3
"""

This is a helper module for segmentation.py.

For import only.

"""

import re
import os
import sys
import json

try:
    # for normal operation via NLP pipeline
    from algorithms.finder import time_finder as tf
    from algorithms.finder import date_finder as df
    from algorithms.finder import size_measurement_finder as smf
    from algorithms.finder import lab_value_matcher as lvm
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

    import time_finder as tf
    import date_finder as df
    import size_measurement_finder as smf
    import lab_value_matcher as lvm

_VERSION_MAJOR = 0
_VERSION_MINOR = 3
_MODULE_NAME = 'segmentation_helper.py'

# set to True to enable debug output
_TRACE = False

# regex for locating an anonymized item [** ... **]
_str_anon = r'\[\*\*[^\]]+\]'
_regex_anon = re.compile(_str_anon)

# regex for locating a contrast agent expression
_str_contrast = r'\bContrast:\s+(None|[a-zA-Z]+\s+Amt:\s+\d+(cc|CC)?)'
_regex_contrast = re.compile(_str_contrast)

# regex for locating a field of view expression
_str_fov = r'\bField of view:\s+\d+'
_regex_fov = re.compile(_str_fov)

# start of a numbered section, such as a list, but with no whitespace
# separating the numbers from the adjacent text
_str_list_start_no_space = r'\b(?P<listnum>\d+(\.|\)))(?P<word>[a-zA-Z]+)'
_regex_list_start_no_space = re.compile(_str_list_start_no_space)

# find numbered sentences: look for digits followed by '.' or ')',
# whitespace, then a capital letter starting a word
_str_list_start = r'\b(?P<listnum>\d+(\.|\)))\s+'
_str_list_item = _str_list_start + r'([A-Z][a-z]+|\d)\b'
_regex_list_start = re.compile(_str_list_start)
_regex_list_item  = re.compile(_str_list_item)

# find captialized headers
_str_caps_word = r'\b([123]-?D|[-_A-Z]+|[-_A-Z]+/[-_A-Z]+)\b'
_str_caps_header = r'(' + _str_caps_word + r'\s+)*' + _str_caps_word + r'\s*#?:'
_regex_caps_header = re.compile(_str_caps_header)

# find sentences that end with a dash followed by a word
_str_ending_dashword = r'\-[a-z]+\Z'
_regex_ending_dashword = re.compile(_str_ending_dashword, re.IGNORECASE)

# find sentences that begin with a number list
_str_startswith_number_list = r'\A[\d.,]+\s[\d.,]+'
_regex_startswith_number_list = re.compile(_str_startswith_number_list)

# find sentences that consist of a single word
_str_single_word = r'\A[-a-z]+\Z'
_regex_single_word = re.compile(_str_single_word, re.IGNORECASE)

# find concatenated sentences with no space after the period

# need at least two chars before '.', to avoid matching C.Diff, M.Smith, etc.
# neg lookahead prevents capturing inside abbreviations such as Sust.Rel.
_regex_two_sentences = re.compile(r'\b[a-zA-Z]{2,}\.[A-Z][a-z]+(?!\.)')

# prescription information
_str_word         = r'\b[-a-z]+\b'
_str_words        = r'(' + _str_word + r'\s*)*' + _str_word
_str_drug_name    = r'\b[-A-Za-z]+(/[-A-Za-z]+)?\b'
_str_amount_num   = r'\d+(\.\d+)?'
_str_amount       = r'(' + _str_amount_num + r'(/' + _str_amount_num + r')?)?'
_str_units        = r'\b[a-z]+\.?'
_str_abbrev       = r'([a-zA-Z]\.){1,3}'
_str_abbrevs      = r'(' + _str_abbrev + r'\s+)*' + _str_abbrev
_str_prescription = _str_drug_name + r'\s+' + _str_amount + r'\s*' + _str_units + \
                   r'\s+' + _str_abbrevs + r'\s+' + _str_words
_regex_prescription = re.compile(_str_prescription)

# abbreviations
_str_weekday  = r'((Mon|Tues|Wed|Thurs|Thur|Thu|Fri|Sat|Sun)\.)'
_str_h_o      = r'(\.?H/O)'
_str_r_o      = r'(r/o(ut)?)'
_str_with     = r'(w/)'
_str_s_p      = r'(s/p)'
_str_r_l      = r'((Right|Left)\s+[A-Z]+)'
_str_sust_rel = r'(Sust\.?\s?Rel\.?)'
_str_sig      = r'(Sig\s?:\s?[a-z0-9]+)'

_str_abbrev = r'\b(' + _str_weekday + r'|' + _str_h_o      + r'|' +\
    _str_r_o + r'|'  + _str_s_p     + r'|' + _str_with     + r'|' +\
    _str_s_p + r'|'  + _str_r_l     + r'|' + _str_sust_rel + r'|' +\
    _str_sig + r')'
_regex_abbrev = re.compile(_str_abbrev, re.IGNORECASE)

# gender
_str_gender   = r'\b(sex|gender)\s*:\s*(male|female|m\.?|f\.?)'
_regex_gender = re.compile(_str_gender, re.IGNORECASE)

# operators except for '-' that might appear in the text
_operator_set = {
    '+', '*', '/', '%', '^', '>=', '>', '<=', '<', '=', '!='
}

# lists to keep track of token substitutions
_fov_subs          = []
_anon_subs         = []
_contrast_subs     = []
_size_meas_subs    = []
_header_subs       = []
_prescription_subs = []
_vitals_subs       = []
_abbrev_subs       = []
_gender_subs       = []
_date_subs         = []
_time_subs         = []


###############################################################################
def enable_debug():
    
    global _TRACE
    _TRACE = True

    #lvm.enable_debug()

    
###############################################################################
def init():

    lvm.init()
    

###############################################################################
def _make_token(token_text, counter):
    """
    Generate a token string for textual replacement.
    """

    return '|{0}{1:04}|'.format(token_text, counter)

    
###############################################################################
def _insert_tokens(report, token_text, tuple_list, sub_list):
    """
    The tuple_list is a list of (start, end, match_text) tuples. For each
    tuple in this list, replace report[start:end] with a token of the form
    'TOKEN0001', TOKEN0002', etc. Store the substitutions in sub_list and
    return the new report.
    """

    if 0 == len(tuple_list):
        return report

    counter = 0
    prev_end = 0
    new_report = ''
    for start, end, match_text in tuple_list:
        chunk1 = report[prev_end:start]
        replacement = _make_token(token_text, counter)
        new_report += chunk1 + replacement
        prev_end = end
        sub_list.append( (replacement, match_text) )
        counter += 1
    new_report += report[prev_end:]

    return new_report
    
    
###############################################################################
def _find_size_meas_subs(report, sub_list, token_text):
    """
    Run the size measurement finder to find measurements such as 3 cm. x 4 cm.
    The standard NLP sentence tokenizers can incorrectly split such 
    measurements after the first '.'.
    """

    json_string = smf.run(report)
    if '[]' == json_string:
        return report
    
    json_data = json.loads(json_string)

    # unpack JSON result into a list of SizeMeasurement namedtuples
    measurements = [smf.SizeMeasurement(**m) for m in json_data]

    # convert to a list of (start, end, match_text) tuples
    tuple_list = [(m.start, m.end, m.text) for m in measurements]

    if _TRACE:
        print('*** SIZE MEASUREMENTS ***')
        for t in tuple_list:
            print('[{0:4},{1:4}): {2}'.format(t[0], t[1], t[2]))
        print()

    new_report = _insert_tokens(report, token_text, tuple_list, sub_list)
    return new_report


###############################################################################
def _find_date_subs(report, sub_list, token_text):
    """
    Run date_finder to find dates in the report text and replace with tokens.
    """

    json_string = df.run(report)
    if '[]' == json_string:
        return report

    json_data = json.loads(json_string)

    # unpack JSON result into a list of DateValue namedtuples
    dates = [df.DateValue(**d) for d in json_data]

    # convert to a list of (start, end, match_text) tuples
    # ignore all-digit matches, since could likely be a measured value    
    tuple_list = [(d.start, d.end, d.text) for d in dates
                  if not d.text.isdigit()]

    if _TRACE:
        print('*** DATES ***')
        for t in tuple_list:
            print('[{0:4},{1:4}): {2}'.format(t[0], t[1], t[2]))
        print()

    new_report = _insert_tokens(report, token_text, tuple_list, sub_list)            
    return new_report


###############################################################################
def _find_time_subs(report, sub_list, token_text):
    """
    Run time_finder to find time expressions in the report text and
    replace with tokens.
    """

    json_string = tf.run(report)
    if '[]' == json_string:
        return report
        
    json_data = json.loads(json_string)

    # unpack JSON result into a list of TimeValue namedtuples
    times = [tf.TimeValue(**t) for t in json_data]

    # convert to a list of (start, end, match_text) tuples
    # ignore any all-digit matches, could be a measured value
    tuple_list = [(t.start, t.end, t.text) for t in times
                  if not t.text.isdigit()]

    if _TRACE:
        print('*** TIMES ***')
        for t in tuple_list:
            print('[{0:4},{1:4}): {2}'.format(t[0], t[1], t[2]))
        print()

    new_report = _insert_tokens(report, token_text, tuple_list, sub_list)
    return new_report


###############################################################################
def _find_vitals_subs(report, sub_list, token_text):
    """
    Run the lab_value_matcher to find vital signs and replace with tokens.
    """

    # use lab_value_matcher to find all vitals, lab value lists, etc.
    vitals = lvm.run(report)
    tuple_list = [(v.start, v.end, v.match_text) for v in vitals]
    
    if _TRACE:
        print('*** VITALS ***')
        for t in tuple_list:
            print('[{0:4},{1:4}): {2}'.format(t[0], t[1], t[2]))
        print()
        
    new_report = _insert_tokens(report, token_text, tuple_list, sub_list)
    return new_report
    

###############################################################################
def _find_substitutions(report, regex_or_subs, sub_list, token_text):
    """
    """

    if list != type(regex_or_subs):
        # regex_or_subs is a regex
        regex = regex_or_subs
        tuple_list = []

        iterator = regex.finditer(report)
        for match in iterator:
            tuple_list.append( (match.start(), match.end(), match.group()) )
    else:
        tuple_list = regex_or_subs    
            
    if 0 == len(tuple_list):
        return report

    if _TRACE:
        print('*** {0} ***'.format(token_text))
        for t in tuple_list:
            print('[{0:4},{1:4}): {2}'.format(t[0], t[1], t[2]))
        print()
    
    new_report = _insert_tokens(report, token_text, tuple_list, sub_list)
    return new_report
        
        
###############################################################################
def do_substitutions(report):
    """
    """

    _anon_subs.clear()
    _contrast_subs.clear()
    _fov_subs.clear()
    _size_meas_subs.clear()
    _header_subs.clear()
    _prescription_subs.clear()
    _vitals_subs.clear()
    _abbrev_subs.clear()
    _gender_subs.clear()
    _date_subs.clear()

    report = _find_substitutions(report, _regex_abbrev, _abbrev_subs, 'ABBREV')

    report = _find_vitals_subs(report, _vitals_subs, 'VITALS')
    
    report = _find_substitutions(report, _regex_caps_header,
                                 _header_subs, 'HEADER')

    report = _find_date_subs(report, _date_subs, 'DATE')
    report = _find_time_subs(report, _time_subs, 'TIME')
    
    report = _find_substitutions(report, _regex_anon, _anon_subs, 'ANON')    
    
    report = _find_substitutions(report, _regex_contrast,
                                 _contrast_subs, 'CONTRAST')
    report = _find_substitutions(report, _regex_fov, _fov_subs, 'FOV')
    report = _find_size_meas_subs(report, _size_meas_subs, 'MEAS')
    report = _find_substitutions(report, _regex_prescription,
                                 _prescription_subs, 'PRESCRIPTION')
    report = _find_substitutions(report, _regex_gender, _gender_subs, 'GENDER')

    if _TRACE:
        print('REPORT AFTER SUBSTITUTIONS: \n' + report + '\n')

    return report


###############################################################################
def _replace_text(sentence_list, sub_list):
    """
    For each sentence in sentence_list, replace all tokens with the original
    text. The sub_list is a list of tuples of the form
    (substituted_token, original_text).
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
    Undo the textual substitutions in 'do_substitions', but in the reverse
    order.
    """

    sentence_list = _replace_text(sentence_list, _gender_subs)
    sentence_list = _replace_text(sentence_list, _prescription_subs)
    sentence_list = _replace_text(sentence_list, _size_meas_subs)
    sentence_list = _replace_text(sentence_list, _fov_subs)
    sentence_list = _replace_text(sentence_list, _contrast_subs)
    sentence_list = _replace_text(sentence_list, _anon_subs)
    sentence_list = _replace_text(sentence_list, _time_subs)
    sentence_list = _replace_text(sentence_list, _date_subs)
    sentence_list = _replace_text(sentence_list, _header_subs)
    sentence_list = _replace_text(sentence_list, _vitals_subs)
    sentence_list = _replace_text(sentence_list, _abbrev_subs)

    return sentence_list
        

###############################################################################
def _erase_spans(report, span_list):
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
    Do some basic cleanup operations on the report text.
    """

    # remove (Over) ... (Cont) inserts (found in MIMIC data)
    spans = []
    iterator = re.finditer(r'\(Over\)', report)
    for match_over in iterator:
        start = match_over.start()
        chunk = report[match_over.end():]
        match_cont = re.search(r'\(Cont\)', chunk)
        if match_cont:
            end = match_over.end() + match_cont.end()
            spans.append( (start, end))
            
    report = _erase_spans(report, spans)

    # insert a space between list numbers and subsequent text, makes
    # lists and start-of-sentence negations easier to identify
    prev_end = 0
    new_report = ''
    iterator = _regex_list_start_no_space.finditer(report)
    for match in iterator:
        # end of list num (digits followed by '.' or ')'
        end = match.end('listnum')
        # start of following (concatenated) word
        start = match.start('word')
        new_report += report[prev_end:end]
        new_report += ' '
        prev_end = start
    new_report += report[prev_end:]
    report = new_report

    # remove numbering in lists
    spans = []
    iterator = _regex_list_item.finditer(report)
    for match in iterator:
        start = match.start('listnum')
        end   = match.end('listnum')
        spans.append( (start, end))

    report = _erase_spans(report, spans)
        
    # Remove long runs of dashes, underscores, or stars
    report = re.sub(r'[-_*]{3,}', ' ', report)
    
    # collapse repeated whitespace (including newlines) into a single space
    report = re.sub(r'\s+', ' ', report)

    # convert unicode left and right quotation marks to ascii
    report = re.sub(r'(\u2018|\u2019)', "'", report)
    
    return report
    

###############################################################################
def fixup_sentences(sentence_list):
    """
    Move punctuation from the start of a sentence to the end of the previous
    sentence.
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

    # Dashes are often used to demarcate phrases. If a sentence ends with a
    # single word preceded by a dash, merge with the following sentence.

    merged_sentences = []

    i = 0
    while i < num:
        s = sentence_list[i]
        match = _regex_ending_dashword.search(s)
        if match:
            merged_sentences.append(s + ' ' + sentence_list[i+1])
            i += 2
        else:
            merged_sentences.append(s)
            i += 1

    # check for opportunities to merge a sentence with the previous one
    num = len(merged_sentences)
    results = [merged_sentences[0]]
    for i in range(1, len(merged_sentences)): 
        s = merged_sentences[i]
        
        # Is the first char of the sentence an operator?
        c = s[0]
        starts_with_op = c in _operator_set

        # Does the sentence starts with a list of numbers (and hence
        # no header to identify what the numbers are)?
        match1 = _regex_startswith_number_list.match(s)

        # Does the sentence consist of a single word?
        match2 = _regex_single_word.match(s)
        
        if match1 or match2 or starts_with_op:
            
            if _TRACE:
                print('Appending sentence: "{0}"'.format(s))
            
            results[-1] = results[-1] + ' ' + s
        else:
            results.append(s)
            
    return results


###############################################################################
def split_section_headers(sentence_list):
    """
    Put an all caps section header in a separate sentence from the subsequent
    text.
    """

    sentences = []
    for s in sentence_list:
        subs = []
        iterator = _regex_caps_header.finditer(s)
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
        match = _regex_two_sentences.search(s)
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
        match = _regex_list_start.match(s)
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
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)

