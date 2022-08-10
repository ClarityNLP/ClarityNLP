"""
Common functions for the SDOH finder modules.
"""

import os
import re
import sys


# negations
_str_neg = r'\b(denies|without|other than|lacks|understands neither|unable to|' \
    r'cannot|cant|(did )?not|non?( (evidence|mention))?)'
_regex_neg = re.compile(_str_neg, re.IGNORECASE)

# section header, such as "Plan: ..."
_str_header = r'\b[a-z]+:'
_regex_header = re.compile(_str_header, re.IGNORECASE)

_CHAR_SPACE = ' '


###############################################################################
def cleanup(sentence):
    """
    Apply some cleanup operations to the sentence and return the
    cleaned sentence.
    """

    # convert to lowercase
    sentence = sentence.lower()

    # replace MIMIC [** ... **] anonymizations with whitespace
    sentence = re.sub(r'\[\*\*[^\]]+\]', _CHAR_SPACE, sentence)    

    # replace ' w/ ' with ' with '
    sentence = re.sub(r'\sw/', ' with ', sentence)

    # replace 'hx' with ' history '
    sentence = re.sub(r'\bhx\.?', ' history ', sentence)

    # replace 'dx' with diagnosis
    sentence = re.sub(r'\bdx\.?', ' diagnosis ', sentence)

    # replace 'sx' with significant
    sentence = re.sub(r'\bsx\.?', ' significant ', sentence)

    # replace "pt's" with 'patients' (no apostrophe)
    sentence = re.sub(r"\bpt\'?s", ' patients ', sentence)

    # replace 'pt' with 'patient'
    sentence = re.sub(r'\bpt\.?', ' patient ', sentence)

    # replace ' @ ' with ' at '
    sentence = re.sub(r'\s@\s', ' at ', sentence)

    # replace "->" with whitespace
    sentence = re.sub(r'\->', _CHAR_SPACE, sentence)

    # erase apostrophes
    sentence = re.sub(r'[\'`]', '', sentence)

    # replace other chars with whitespace
    # (do NOT erase colons, needed to identify section headers)
    sentence = re.sub(r'[-&(){}\[\]~/;",]', _CHAR_SPACE, sentence)

    # collapse repeated whitespace
    sentence = re.sub(r'\s+', _CHAR_SPACE, sentence)

    sentence = sentence.strip()
    return sentence


###############################################################################
def regex_match(sentence, regex_list):
    """
    """

    match_list = []
    for i, regex in enumerate(regex_list):
        iterator = regex.finditer(sentence)
        for match in iterator:
            # strip any trailing whitespace (invalidates match.end())
            match_text = match.group().rstrip()
            start = match.start()
            end = start + len(match_text)

            # check for negations *prior* to the match
            prior = sentence[:start]

            # Find the closest section header to the match, if any, and
            # keep only the text after the header and before the match as
            # the prior text.
            header_iterator = _regex_header.finditer(prior)
            header_matches = [hm for hm in header_iterator]
            if len(header_matches) > 0:
                header_match = header_matches[-1]
                prior = prior[header_match.end():]

            # search the prior text for negations
            neg_match = _regex_neg.search(prior)
            if neg_match:
                continue

            obj = {
                'matchobj' : match,
                'match_text' : match_text,
                'start' : start,
                'end' : end,
                'prior' : prior
            }
            
            match_list.append(obj)

    return match_list
