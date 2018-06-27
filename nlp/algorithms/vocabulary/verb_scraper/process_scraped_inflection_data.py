#!/usr/bin/env python3
"""

    This code generates a file of truth data used for testing the verb 
    inflector. 

    Requires the file 'raw_inflection_data.txt' as input.

    Generates the file 'inflection_truth_data.txt'.

    Run as follows:

        python3 ./process_scraped_inflection_data.py

"""

import re
import os
import sys
import optparse

VERSION_MAJOR = 0
VERSION_MINOR = 1

INPUT_FILENAME = 'raw_inflection_data.txt'
OUTPUT_FILENAME = 'inflection_truth_data.txt'

# words can contain apostrophe characters (see data for call)
str_word = r"['a-z]+"

# recognize parenthesized text
str_parens = r'\([^)]+\)'
regex_parens = re.compile(str_parens, re.IGNORECASE)

# list of words separated by 'or'
str_list = r'\b(' + str_word + r'\s+or\s*)*' + str_word
regex_list = re.compile(str_list, re.IGNORECASE)

# recognize 'or (word1, word2, ..., wordN) word' forms
str_or_parens_word = r'(\bor\s+)?\((?P<text_in_parens>[,\sa-z\']+)\)\s+' + str_word
regex_or_parens_word = re.compile(str_or_parens_word, re.IGNORECASE)

# words in parens indicating that the word following the parens is ignorable
str_ignorable = r'(archaic|obsolete|dialectal|poetic|chiefly\s+UK|'   +\
                r'rare|informal|nonstandard|regional|dated|'          +\
                r'mostly\s+Commonwealth|southern\s+US|colloquial|UK|' +\
                r'proscribed)'
regex_ignorable = re.compile(str_ignorable, re.IGNORECASE)

# base form of the verb
str_base = r'\d+\s+(?P<base>' + str_word + r')\s+\('
regex_base = re.compile(str_base, re.IGNORECASE)

# 3rd person singular present
str_3rd  = r'\bthird-person singular simple present\s+(?P<third>' +\
           str_list + r'),'
regex_3rd = re.compile(str_3rd, re.IGNORECASE)

# find stray 'or' left over from erasure
str_stray_or = r'\b(participle|past)\s+(?P<stray_or>or)\s+' + str_word
regex_stray_or = re.compile(str_stray_or, re.IGNORECASE)

# present participle
str_pres_part = r'\bpresent participle\s+(?P<pres_part>' +\
                str_list + r')'
regex_pres_part = re.compile(str_pres_part, re.IGNORECASE)

# simple past and past participle
str_past_and_pp = r'\bsimple past and past participle\s+(?P<past_and_pp>' +\
                  str_list + r')'
regex_past_and_pp = re.compile(str_past_and_pp, re.IGNORECASE)

# simple past
str_past = r'\bsimple past\s+(?P<past>' + str_list + r')'
regex_past = re.compile(str_past, re.IGNORECASE)

# past participle
str_pp = r'\bpast participle\s+(?P<pp>' + str_list + r')'
regex_pp = re.compile(str_pp, re.IGNORECASE)

###############################################################################
def erase(text, start, end):
    """
    Overwrite a section of text with whitespace.
    """

    new_text = text[:start] + ' '*(end-start) + text[end:]
    return new_text

###############################################################################
def parse_list(text):
    """
    Separate 'word1 or word2 or ... wordN' into individual words and return
    those words.
    """

    words = text.split(' or ')
    words = [w.strip() for w in words]
    return words

###############################################################################
def extract_inflections(text):
    """
    """

    inflections = []

    match = regex_base.search(text)
    if match:
        inflections.append(match.group('base'))
    else:
        inflections.append('')
        
    # remove ignorable words
    iterator = regex_or_parens_word.finditer(text)
    for match in iterator:
        text_in_parens = match.group('text_in_parens')
        # if 'America' is in the parenthesized text, not ignorable
        if -1 != text_in_parens.lower().find('america'):
            continue
        match2 = regex_ignorable.search(text_in_parens)
        if match2:
            # ignorable, erase entire match from sentence
            text = erase(text, match.start(), match.end())
            #print('{0}\tIGNORE: {1}'.format(match.group(), text_in_parens))

    # remove any remaining parenthesized text after the first parens
    pos = text.find('(')
    text = regex_parens.sub('', text[pos+1:])
    
    # remove any stray 'or' words
    iterator = regex_stray_or.finditer(text)
    for match in iterator:
        #print('\tSTRAY OR: ' + match.group())
        text = erase(text, match.start('stray_or'), match.end('stray_or'))

    # the text from which to extract the inflections
    #print(text)
        
    match = regex_3rd.search(text)
    if match:
        matching_text = match.group('third')
        words = parse_list(matching_text)
        inflections.append(words)
    else:
        inflections.append([])

    match = regex_pres_part.search(text)
    if match:
        matching_text = match.group('pres_part')
        words = parse_list(matching_text)
        inflections.append(words)
    else:
        inflections.append([])

    match = regex_past_and_pp.search(text)
    if match:
        matching_text = match.group('past_and_pp')
        words = parse_list(matching_text)
        inflections.append(words)
        inflections.append(words)
    else:
        match = regex_past.search(text)
        if match:
            matching_text = match.group('past')
            words = parse_list(matching_text)
            inflections.append(words)
        else:
            inflections.append([])

        match = regex_pp.search(text)
        if match:
            matching_text = match.group('pp')
            words = parse_list(matching_text)
            inflections.append(words)
        else:
            inflections.append([])

    assert 5 == len(inflections)
    return inflections

lines = []

infile = open(INPUT_FILENAME, 'r')
for line in infile:
    text = line.strip()

    inflections = extract_inflections(text)
    if '' == inflections[0]:
        continue

    # print as CSV data
    base      = inflections[0]
    third     = ' '.join(inflections[1])
    pres_part = ' '.join(inflections[2])
    past      = ' '.join(inflections[3])
    past_part = ' '.join(inflections[4])
    line = '{0},{1},{2},{3},{4}\n'.format(base, third, pres_part, past, past_part)
    lines.append(line)

infile.close()

outfile = open(OUTPUT_FILENAME, 'w')
for line in lines:
    outfile.write(line)
outfile.close()


