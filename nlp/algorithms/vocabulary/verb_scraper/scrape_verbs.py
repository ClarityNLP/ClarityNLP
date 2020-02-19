#!/usr/bin/env python3
"""

    Scrape irregular verbs from Wikipedia and the 1000 most common English
    verbs from poetrysoup.com. Correct for some inconsistencies between
    Wikipedia and Wiktionary also.

    Run as follows:

        python3 ./scrape_verbs.py

    Generates two output files:
    
        verb_list.txt      - list of unique verbs found
        irregular_verbs.py - code to cut and paste into verb_inflector.py

"""

import re
import os
import sys
import optparse
import requests
from bs4 import BeautifulSoup
from claritynlp_logging import log, ERROR, DEBUG


VERSION_MAJOR = 0
VERSION_MINOR = 1

IGNORE_ARCHAIC = True

MODULE_NAME = 'scrape_verbs.py'

OUTPUT_FILE = 'verb_list.txt'
OUTPUT_PYTHON_FILE = 'irregular_verbs.py'

url_irregular = 'https://en.wikipedia.org/wiki/List_of_English_irregular_verbs'
url_common = 'https://www.poetrysoup.com/common_words/common_verbs.aspx'

NONE_TEXT = '(none)'

###############################################################################
def get_comment_block():
    """
    Generate the comment block to be written into the output python file.
    """

    return ("# The following dictionary of irregular verbs was constructed with data\n"
            "# scraped from this link:\n"
            "#     'https://en.wikipedia.org/wiki/List_of_English_irregular_verbs'\n"
            "\n"
            "# Verbs marked as archaic are omitted unless their Wiktionary entry\n"
            "# indicates that they are actually NOT archaic. There are lots of discrepancies\n"
            "# between Wiktionary and Wikipedia for these verbs. An attempt at resolving\n"
            "# these has been performed by the associated scraping code.\n"
            "#\n"
            "# Each entry has the form:\n"
            "#\n"
            "#     base_form:[ [past tense (preterite) forms], [past participle forms]]\n")


###############################################################################
def split_on_fwdslash(match_text):
    """
    Split word1/word2/.../wordN into ['word1', 'word2', ..., 'wordN'].
    """

    word_list = []
    match_text_wds = match_text.split('/')
    for w in match_text_wds:
        if IGNORE_ARCHAIC and w.startswith('*'):
            continue
        else:
            word_list.append(w)
    return word_list

###############################################################################
def extract_components(text):
    """
    """

    chunks = []
    prev_end = 0
    # Wikipedia article uses EN DASH character instead of '-'
    # need to split on space{EN_DASH}space
    iterator = re.finditer(r' [-\u2013] ', text)
    for match in iterator:
        match_text = text[prev_end:match.start()]
        chunks.append(match_text)
        prev_end = match.end()
    # final chunk
    chunks.append(text[prev_end:])

    assert(len(chunks) >= 1)
    #log('chunks: {0}'.format(chunks))

    components = []

    # chunk0 is the infinitive
    infinitive = chunks[0]

    # remove bracketed comments, if any
    infinitive = re.sub(r'\[[^\]]+\]', '', infinitive)
    infinitive = infinitive.strip()

    # removed parenthesized comments, if any
    infinitive = re.sub(r'\([^)]+\)', '', infinitive)
    infinitive = infinitive.strip()
    
    components.append(infinitive)

    if 1 == len(chunks):
        components.append([])
        components.append([])
        return components
    
    # chunk1 is the simple past tense
    if -1 != chunks[1].find('no other forms'):
        components.append([])
        components.append([])
        return components
    
    if -1 != chunks[1].find('/'):
        word_list = split_on_fwdslash(chunks[1])
        components.append(word_list)
    else:
        components.append([chunks[1]])

    if 2 == len(chunks):
        components.append([])
        return components

    if -1 != chunks[2].find('none'):
        components.append([])
        return components
    
    # chunk2 is the past participle
    if -1 != chunks[2].find('/'):
        word_list = split_on_fwdslash(chunks[2])
        components.append(word_list)
    else:
        components.append([chunks[2]])

    return components
        

###############################################################################
def scrape_irregular_verbs():
    """
    Scrape the list of irregular verbs from Wikipedia.
    """
    
    page = requests.get(url_irregular)
    if 200 != page.status_code:
        log('Error getting url: ' + url_irregular)
        sys.exit(-1)

    soup = BeautifulSoup(page.text, 'html.parser')

    verbs = []
    
    # get all table rows except for the first row which contains the table headers
    rows = soup.find_all('tr')[1:]

    for row in rows:

        # get the first column in this row
        col = row.find('td')

        has_dl = None is not col.find('dl')

        if not has_dl:
            inf_text = col.get_text()
        else:
            # get the <i> elements
            i_elts = col.find_all('i')

            dl = col.find('dl')
            first_dl_i_text = dl.find('i').get_text()

            i_texts = []
            for elt in i_elts:
                elt_text = elt.get_text()
                if elt_text == first_dl_i_text:
                    break
                else:
                    i_texts.append(elt_text)
            inf_text = ' '.join(i_texts)

        # archaic usages are prefixed with '*'
        if IGNORE_ARCHAIC and inf_text.startswith('*'):
            pass
            #log('ARCHAIC: ' + inf_text)
        elif inf_text.startswith('ache'):
            # double entries for ache are obsolete forms, according to Wictionary
            inf_components = ['ache', ['ached'], ['ached']]
            verbs.append(inf_components)
        else:
            #log('->' + inf_text + '<-')

            # split inf_text on Unicode 'EN DASH' character (/u2013) surrounded by spaces
            inf_components = extract_components(inf_text)
            #log('\t{0}'.format(inf_components))

            verbs.append(inf_components)

        if has_dl:
            i_elts = dl.find_all('i')
            for elt in i_elts:
                elt_text = elt.get_text()
                if IGNORE_ARCHAIC and elt_text.startswith('*'):
                    continue
                components = extract_components(elt_text)
                #log('\t{0}'.format(components))

                # correct an error with 'become'
                if 'become' == components[0] and [] == components[1] and [] == components[2]:
                    continue

                verbs.append(components)

    # sort in alphabetical order by infinitive
    verbs = sorted(verbs, key=lambda x: x[0])

    # log as python code that can be cut and pasted
    prev_base_form = ''

    saved_verbs = []
    saved_lines = []
    inverse_map = {}
    
    # write out in dict form, for cut-and-pasting into other code
    for entry in verbs:
        # prevent duplicates
        if entry[0] == prev_base_form:
            continue

        base_form = entry[0]

        # skip obsolete verbs
        if 'forfret' == base_form:
            continue
        
        preterite_forms = entry[1]
        past_part_forms = entry[2]
        
        # correct errors and other issues on the page
        # https://en.wikipedia.org/wiki/List_of_English_irregular_verbs
        if 'be' == base_form:
            preterite_forms = ['was', 'were']
        elif 'backslide' == base_form:
            # add missing forms
            preterite_forms = ['backslid', 'backslided']
            past_part_forms = ['backslidden', 'backslid', 'backslided']
        elif 'broadcast' == base_form:
            # add missing forms
            preterite_forms = ['broadcast', 'broadcasted']
            past_part_forms = ['broadcast', 'broadcasted']
        elif 'clad' == base_form:
            # missing 'cladded'
            preterite_forms = ['clad', 'cladded']
            past_part_forms = ['clad', 'cladded']
        elif 'downcast' == base_form:
            # missing 'downcasted'
            preterite_forms = ['downcast', 'downcasted']
            past_part_forms = ['downcast', 'downcasted']
        elif 'forecast' == base_form:
            # missing 'forecasted'
            preterite_forms = ['forecast', 'forecasted']
            past_part_forms = ['forecast', 'forecasted']
        elif 'input' == base_form:
            # correct a misspelling
            preterite_forms = ['input', 'inputted']
            past_part_forms = ['input', 'inputted']
        elif 'inset' == base_form:
            # correct a misspelling
            preterite_forms = ['inset', 'insetted']
            past_part_forms = ['inset', 'insetted']
        elif 'interweave' == base_form:
            # missing some forms
            preterite_forms = ['interwove', 'interweaved']
            past_part_forms = ['interwoven', 'interweaved']
        elif 'offset' == base_form:
            # add missing forms
            preterite_forms = ['offset', 'offsetted']
            past_part_forms = ['offset', 'offsetted']
        elif 'outbid' == base_form:
            # add missing forms
            past_part_forms = ['outbid', 'outbidden']
        elif 'output' == base_form:
            # add missing forms
            preterite_forms = ['output', 'outputted']
            past_part_forms = ['output', 'outputted']
        elif 'outshine' == base_form:
            preterite_forms = ['outshone', 'outshined']
            past_part_forms = ['outshone', 'outshined']
        elif 'outthrust' == base_form:
            # entry is wrong
            preterite_forms = ['outthrusted']
            past_part_forms = ['outthrusted']
        elif 'overlay' == base_form:
            # entry is wrong, forms not archaic
            preterite_forms = ['overlaid', 'overlayed']
            past_part_forms = ['overlaid', 'overlayed']
        elif 'overshine' == base_form:
            preterite_forms = ['overshone', 'overshined']
            past_part_forms = ['overshone', 'overshined']
        elif 'overstride' == base_form:
            # entry is wrong
            past_part_forms = ['overstrode', 'overstridden']
        elif 'overwork' == base_form:
            # entry is wrong, forms not archaic
            preterite_forms = ['overworked', 'overwrought']
            past_part_forms = ['overworked', 'overwrought']
        elif 'plead' == base_form:
            preterite_forms = ['pleaded', 'pled', 'plead']
            past_part_forms = ['pleaded', 'pled', 'plead']
        elif 'podcast' == base_form:
            # missing forms
            preterite_forms = ['podcast', 'podcasted']
            past_part_forms = ['podcast', 'podcasted']
        elif 'prepay' == base_form:
            # wrong, forms not archaic
            past_part_forms = ['prepayed', 'prepaid']
        elif 'read read read' == base_form:
            # entry has complicated pronunciation data that causes errors
            base_form       = 'read'
            preterite_forms = ['read']
            past_part_forms = ['read']
        elif 'rend' == base_form:
            # entry is wrong
            preterite_forms = ['rent', 'rended']
            past_part_forms = ['rent', 'rended']
        elif 'retread' == base_form:
            # entry is wrong
            past_part_forms = ['retrodden']
        elif 'simulcast' == base_form:
            # add missing forms
            preterite_forms = ['simulcast', 'simulcasted']
            past_part_forms = ['simulcast', 'simulcasted']
        elif 'shite' == base_form:
            # add missing forms
            preterite_forms = ['shited', 'shit', 'shat']
            past_part_forms = ['shited', 'shitten']
        elif 'show' == base_form:
            # remove preterite 'shew' and pp 'showed', archaic and rare
            preterite_forms = ['showed']
            past_part_forms = ['shown']
        elif 'smite' == base_form:
            # correct misspelling
            past_part_forms = ['smitten', 'smited']
        elif 'telecast' == base_form:
            # add missing forms
            preterite_forms = ['telecast', 'telecasted']
            past_part_forms = ['telecast', 'telecasted']
        elif 'thrust' == base_form:
            preterite_forms = ['thrust', 'thrusted']
            past_part_forms = ['thrust', 'thrusted']
        elif 'typecast' == base_form:
            # add missing forms
            preterite_forms = ['typecast', 'typecasted']
            past_part_forms = ['typecast', 'typecasted']
        elif 'underbear' == base_form:
            # correct errors
            preterite_forms = ['underbore']
            past_part_forms = ['underborne', 'underborn']
        elif 'underbet' == base_form:
            # correct errors
            preterite_forms = ['underbet']
            past_part_forms = ['underbet']
        elif 'upcast' == base_form:
            # add missing forms
            preterite_forms = ['upcast', 'upcasted']
            past_part_forms = ['upcast', 'upcasted']
        elif 'updraw' == base_form:
            # spelling error in past participle
            past_part_forms = ['updrawn']
        elif 'upheave' == base_form:
            # some forms not archaic
            preterite_forms = ['upheaved', 'uphove']
            past_part_forms = ['upheaved']
        elif 'weave' == base_form:
            # some forms not archaic
            preterite_forms = ['wove', 'weaved']
            past_part_forms = ['woven', 'weaved']
        elif 'wreak' == base_form:
            # some forms not archaic
            preterite_forms = ['wreaked', 'wrought']
            past_part_forms = ['wreaked', 'wrought']

        # generate entry for irregular_verbs.py
        line = "'{0}':[{1},{2}],".format(base_form, preterite_forms, past_part_forms)
        saved_lines.append(line)
        prev_base_form = base_form
        saved_verbs.append(base_form)

        # update inverse map
        for v in preterite_forms:
            inverse_map[v] = base_form
        for v in past_part_forms:
            inverse_map[v] = base_form
        
    # write out as python data structures

    INDENT = '    '
    outfile = open(OUTPUT_PYTHON_FILE, 'w')
    outfile.write(get_comment_block() + '\n')
    outfile.write('VERBS = {\n')
    for l in saved_lines:
        outfile.write(INDENT + l + '\n')
    outfile.write('}\n')
    outfile.write('\n')

    outfile.write('INFLECTION_MAP = {\n')
    for inflected_form, base_form in inverse_map.items():
        outfile.write(INDENT + "'{0}':'{1}',\n".format(inflected_form, base_form))
    outfile.write('}\n')
    outfile.close()

    return saved_verbs


###############################################################################
def scrape_common_verbs():
    """
    Scrape a list of the 100 most common English verbs.
    """
    
    page = requests.get(url_common)
    if 200 != page.status_code:
        log('Error getting url: ' + url)
        sys.exit(-1)

    soup = BeautifulSoup(page.text, 'html.parser')

    verbs = []

    # get all 'a' elements, look for the first one with href='/dictionary/be'
    a_elts = soup.find_all('a')

    start=0
    for a in a_elts:
        if 'be' == a.get_text().strip().lower():
            break
        else:
            start += 1

    # skip the verb 'be', which has a complex entry
    for i in range(start+1, start+1000):
        verb = a_elts[i].get_text().strip().lower()
        verbs.append(verb)

    return verbs

    
###############################################################################
if __name__ == '__main__':

    irregular_verbs = scrape_irregular_verbs()
    common_verbs = scrape_common_verbs()

    #remove duplicates
    verb_set = set()
    for v in irregular_verbs:
        verb_set.add(v)
    for v in common_verbs:
        verb_set.add(v)
    verbs = sorted(list(verb_set))
    
    # write to file
    outfile = open(OUTPUT_FILE, 'w')
    for v in verbs:
        outfile.write(v + '\n')
    outfile.close()
