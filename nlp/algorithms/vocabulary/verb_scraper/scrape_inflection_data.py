#!/usr/bin/env python3
"""

    Scrape the inflection truth data from Wiktionary for a list of verbs:

        python3 ./scrape_inflection_data.py

    Requires the file 'verb_list.txt' as input (one verb per line).

    Generates the output file 'raw_inflection_data.txt' containing the
    Wiktionary inflection entry for each verb.

    This code is rather slow - would be better to process each page as text
    and extract the inflection data via regexes.

    Some Wiktionary pages may be unavailable when scraping. These requests
    return a 404 HTTP status code. The number of such pages is displayed
    as the scraping proceeds. A few missing pages will not severely impact
    the testing of the verb inflector.

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

MODULE_NAME = 'scrape_inflection_data.py'

INPUT_FILE = 'verb_list.txt'
OUTPUT_FILE = 'raw_inflection_data.txt'

###############################################################################
if __name__ == '__main__':

    verbs = []

    ISE_VERBS = ['characterise', 'criticise',
                 'emphasise', 'organise', 'realise', 'recognise']

    # load the verb list
    infile = open(INPUT_FILE, 'r')
    with infile:
        for line in infile:
            verb = line.strip()
            verbs.append(verb)

    verb_count = len(verbs)
    
    log('Scraping inflection data for {0} verbs...'.format(verb_count))

    outfile = open(OUTPUT_FILE, 'w')

    failure_count = 0    
    counter = 0
    num_written = 0
    prev_verb = ''
    #for verb in verbs:
    for i in range(len(verbs)):
        
        verb = verbs[i]
        counter = counter + 1
        
        if 'going' == verb:
            # skip 'going', since 'go' is already in the list
            continue
        elif 'born' == verb:
            # skip since 'bear' is already in the list
            continue
            
        # change from British to American spelling
        if verb in ISE_VERBS:
            verb = verb[:-3] + 'ize'
        elif 'analyse' == verb:
            verb = 'analyze'
        elif 'centre' == verb:
            verb = 'center'
        elif 'fulfil' == verb:
            verb = 'fulfill'
        elif 'practise' == verb:
            verb = 'practice'

        #log('verb: {0}, prev_verb: {1}'.format(verb, prev_verb))
            
        # construct the Wiktionary URL for this verb and get its page
        url = 'https://en.wiktionary.org/wiki/' + verb + '#Verb'
        page = requests.get(url)
        if 200 != page.status_code:
            log('Error getting url: ' + url)
            log('\tStatus code: {0}'.format(page.status_code))
            failure_count += 1
            continue

        soup2 = BeautifulSoup(page.text, 'html.parser')

        if 'abide' == verb:
            # remove archaic forms
            text = 'abide (third-person singular simple present abides, ' \
                   'present participle abiding, ' \
                   'simple past (archaic) abode or abided, ' \
                   'past participle (archaic) abode or abided or (rare) abidden)'
        elif 'bear' == verb:
            # scrapes the first entry; the second entry is the one needed
            text = 'bear (third-person singular simple present bears, ' \
                   'present participle bearing, ' \
                   'simple past bore or (archaic) bare, ' \
                   'past participle borne or (see usage notes) born)'
        elif 'belay' == verb:
            # correct for archaic forms
            text = 'belay (third-person singular simple present belays, ' \
                   'present participle belaying, ' \
                   'simple past and past participle (archaic) belayed or belaid)'
        elif 'beseech' == verb:
            # correct for archaic forms
            text = 'beseech (third-person singular simple present beseeches, ' \
                   'present participle beseeching, ' \
                   'simple past and past participle beseeched or (archaic) besought)'
        elif 'bestride' == verb:
            # remove archaic forms
            text = 'bestride (third-person singular simple present bestrides, ' \
                   'present participle bestriding, ' \
                   'simple past bestrode, ' \
                   'past participle bestridden)'
        elif 'betide' == verb:
            # remove archaic forms
            text = 'betide (third-person singular simple present betides, ' \
                   'present participle betiding, ' \
                   'simple past and past participle betided)'
        elif 'bless' == verb:
            # remove archaic forms
            text = 'bless (third-person singular simple present blesses, ' \
                   'present participle blessing, ' \
                   'simple past and past participle (archaic) blest or blessed)'
        elif 'bid' == verb:
            # remove archaic forms
            text = 'bid (third-person singular simple present bids, ' \
                   'present participle bidding, simple past bid, '    \
                   'past participle bid)'
        elif 'call' == verb:
            # remove archaic call'd as a past participle form
            text = 'call (third-person singular simple present calls, ' \
                   'present participle calling, ' \
                   "simple past and past participle called or (archaic) call'd)"
        elif 'chide' == verb:
            # remove archaic forms
            text = 'chide (third-person singular simple present chides, ' \
                   'present participle chiding, ' \
                   'simple past chid or chided or (archaic) chode, ' \
                   'past participle chid or chided or chidden)'
        elif 'equip' == verb:
            # remove archaic forms
            text = 'equip (third-person singular simple present equips, ' \
                   'present participle equipping, simple past equipped, ' \
                   'past participle equipped)'
        elif 'fix' == verb:
            # 'fixt' is actually archaic
            text = 'fix (third-person singular simple present fixes, ' \
                   'present participle fixing, ' \
                   'simple past and past participle fixed or (archaic) fixt)'
        elif 'fret' == verb:
            # remove archaic forms
            text = 'fret (third-person singular simple present frets, ' \
                   'present participle fretting, ' \
                   'simple past fretted or frate, ' \
                   'past participle fretted or (usually in compounds) fretten)'
        elif 'gird' == verb:
            # remove archaic forms
            text = 'gird (third-person singular simple present girds, ' \
                   'present participle girding, ' \
                   'simple past and past participle girded)'
        elif 'hamstring' == verb:
            # remove archaic forms
            text = 'hamstring (third-person singular simple present hamstrings, ' \
                   'present participle hamstringing, ' \
                   'simple past and past participle hamstrung or (archaic) hamstringed)'
        elif 'heave' == verb:
            # remove archaic forms
            text = 'heave (third-person singular simple present heaves, ' \
                   'present participle heaving, ' \
                   'simple past heaved or (archaic) hove, ' \
                   'past participle heaved)'
        elif 'inhold' == verb:
            # remove archaic forms
            text = 'inhold (third-person singular simple present inholds, ' \
                   'present participle inholding, ' \
                   'simple past inheld, ' \
                   'past participle inheld or (archaic) inholden)'
        elif 'lead' == verb:
            # scrapes the first entry, pronounced 'led'
            text = 'lead (third-person singular simple present leads, ' \
                   'present participle leading, ' \
                   'simple past and past participle led)'
        elif 'mix' == verb:
            # 'mixt' is archaic 
            text = 'mix (third-person singular simple present mixes, ' \
                   'present participle mixing, ' \
                   'simple past and past participle mixed or (archaic) mixt)'
        elif 'must' == verb:
            # remove simple past form, which is just literary
            text = 'must (third-person singular simple present must, ' \
                   'present participle -, simple past -, past participle -)'
        elif 'press' == verb:
            # 'prest' is actually archaic
            text = 'press (third-person singular simple present presses, ' \
                   'present participle pressing, ' \
                   'simple past and past participle pressed or (archaic) prest)'
        elif 'retread' == verb:
            # scrapes wrong entry
            text = 'retread (third-person singular simple present retreads, ' \
                   'present participle retreading, ' \
                   'simple past retrod, ' \
                   'past participle retrodden)'
        elif 'ring' == verb:
            # scrapes the wrong entry
            text = 'ring (third-person singular simple present rings, ' \
                   'present participle ringing, ' \
                   'simple past rang or (nonstandard) rung, ' \
                   'past participle rung)'
        elif 'shit' == verb:
            # remove archaic form
            text = 'shit (third-person singular simple present shits, ' \
                   'present participle shitting, ' \
                   'simple past shit or shitted or shat, ' \
                   'past participle shit or shitted or shat or (archaic) shitten)'
        elif 'show' == verb:
            # commentary on the Wiktionary page says that 'shew' is archaic
            text = 'show (third-person singular simple present shows, ' \
                   'present participle showing, ' \
                   'simple past showed or (archaic) shew, ' \
                   'past participle shown or (rare) showed)'
        elif 'sling' == verb:
            # fix archaic form
            text = 'sling (third-person singular simple present slings, ' \
                   'present participle slinging, ' \
                   'simple past slung or (archaic) slang, ' \
                   'past participle slung)'
        elif 'spit' == verb:
            # scrapes wrong entry
            text = 'spit (third-person singular simple present spits, ' \
                   'present participle spitting, ' \
                   'simple past and past participle spat or spit)'
        elif 'stick' == verb:
            # scrapes the wrong entry
            text = 'stick (third-person singular simple present sticks, ' \
                   'present participle sticking, ' \
                   'simple past and past participle stuck or (archaic) sticked)'
        elif 'stride' == verb:
            # remove obsolete forms
            text = 'stride (third-person singular simple present strides, ' \
                   'present participle striding, ' \
                   'simple past strode, ' \
                   'past participle stridden)' 
        elif 'time' == verb:
            # Wiktionary page contains 'Lua error: not enough memory'
            text = 'time (third-person singular simple present times, ' \
                   'present participle timing, ' \
                   'simple past and past participle timed)'
        elif 'tread' == verb:
            # remove obsolete forms
            text = 'tread (third-person singular simple present treads, ' \
                   'present participle treading, ' \
                   'simple past trod or (archaic) tread, ' \
                   'past participle trod or (archaic) tread or trodden)'
        elif 'underbear' == verb:
            # remove obsolete forms and add missing form
            text = 'underbear (third-person singular simple present underbears, ' \
                   'present participle underbearing, ' \
                   'simple past underbore or (obsolete) underbare, ' \
                   'past participle underborne or underborn)'
        elif 'upheave' == verb:
            # remove archaic forms
            text = 'upheave (third-person singular simple present upheaves, ' \
                   'present participle upheaving, ' \
                   'simple past upheaved or uphove, ' \
                   'past participle upheaved or (archaic) uphoven)'
        elif 'wake' == verb:
            # 'woked' is archaic
            text = 'wake (third-person singular simple present wakes, ' \
                   'present participle waking, ' \
                   'simple past woke or (archaic) waked, ' \
                   'past participle woken or (archaic) waked)'            
        elif 'wind' == verb:
            # extracts the regular variant, pronounced with a short i
            text = 'wind (third-person singular simple present winds, ' \
                   'present participle winding, ' \
                   'simple past and past participle wound)'            
        else:
            found_it = False
            i_elt = soup2.find(string='third-person singular simple present')
            if i_elt is not None:
                p_elt = i_elt.find_parent('p')
                if p_elt is not None:
                    text = p_elt.get_text().strip()
                    found_it = True

            if not found_it:
                # no verb entry for this word...
                log("\tno inflection data for '{0}'".format(verb))
                failure_count += 1
                continue
            
        # remove any garbage from the end of the line (past close parens)
        pos = text.rfind(')')
        if -1 != pos:
            text = text[:pos+1]

        if prev_verb != verb:
            num_written += 1
            outfile.write('{0:4}\t{1}\n'.format(num_written, text))
            #log('\tverb = {0}, wrote {1}'.format(verb, text[:20]))
            prev_verb = verb
            
        # progress indicator
        if 0 == (counter % 10):
            log('Completed {0}/{1} requests, {2} failed'.
                  format(counter, verb_count, failure_count), flush=True)
        
