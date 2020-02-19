#!/usr/bin/env python3
"""



OVERVIEW:



    This module expands macros in NLPQL termsets. The supported macros are:

        Clarity.Synonyms          (WordNet synonyms for NOUN, ADJ, ADV)
        Clarity.Plurals
        Clarity.VerbInflections
        Clarity.LexicalVariants   (verb inflections followed by plurals)
        OHDSI.Synonyms
        OHDSI.Ancestors
        OHDSI.Descendants

        others TBD


SYNTAX:


    Macro names follow the namespace.function syntax. If the namespace is
    omitted, the default namespace of Clarity is used. Thus

        Clarity.Synonyms
        Synonyms

    both refer to the same Clarity synonym expansion macro.

    Macros support single arguments as well as arrays, which are enclosed
    in square brackets:

        Clarity.Synonyms("term1")
        Clarity.Synonyms(["term1"])
        Clarity.Synonyms(["term1", "term2", "term3"])

    The first example shows the use of a single-term argument. The next example
    shows the use of a single-term array, and the third example shows the use
    of a multi-term array.

    Macros can also be nested to arbitrary depth, but currently a hard limit of
    single nesting is enforced.  For instance, to find synonyms first, then
    plurals of each synonym, this syntax could be used:

        Clarity.Plurals(Clarity.Synonyms(["term1", "term2"]))

    Nested macros can cause an explosion in the number of result strings (since
    the code computes the Cartesian product of all possibilities), so use macro
    nesting with caution.

    The macro sytax supports multi-word terms as well:

        Clarity.Synonyms(["term1", "multi word term2"])

    This macro would return synonyms for "term1", as well as for
    "multi word term2" as a whole. It would then find all nouns, adjectives,
    and adverbs inside of "multi word term2", find synonyms for each, and
    return the Cartesian product of all possibilities.

    To illustrate, consider the termset

        termset MyTermset: [
            Clarity.Synonyms("the person walks the animal")
        ],

    Suppose the synonyms for 'person' are: {'man', 'boy', girl'}, and the
    synonyms for 'animal' are {'dog', 'cat', 'bird'}.  The macro would expand
    to these strings inside the termset:

        termset MyTermset: [
            'the man walks the dog',
            'the man walks the cat',
            'the man walks the bird',
            'the boy walks the dog',
            'the boy walks the cat',
            'the boy walks the bird',
            'the girl walks the dog',
            'the girl walks the cat',
            'the girl walks the bird'
        ];


    Macros can also be applied to selected terms inside strings.  For instance:

    termset MyTermset: [
        "term1",
        "term2",
        "multi word Clarity.Synonyms("term3") term4",
        "term5"
    ];



USAGE:



    Run from the command line as follows:

        python3 ./termset_expander.py -f /path/to/file.nlpql > expanded.nlpql



"""

import re
import os
import sys
import spacy
import errno
import optparse
from nltk.corpus import wordnet
from nltk.corpus import cmudict
from spacy.symbols import ORTH, LEMMA, POS, TAG
from claritynlp_logging import log, ERROR, DEBUG


try:
    from .pluralize import plural
    from .verb_inflector import get_inflections
    from .irregular_verbs import INFLECTION_MAP
    from .vocabulary import get_synonyms as ohdsi_get_synonyms
    from .vocabulary import get_ancestors as ohdsi_get_ancestors
    from .vocabulary import get_descendants as ohdsi_get_descendants
except Exception as e:
    log(e)
    from pluralize import plural
    from verb_inflector import get_inflections
    from irregular_verbs import INFLECTION_MAP
    from vocabulary import get_synonyms as ohdsi_get_synonyms
    from vocabulary import get_ancestors as ohdsi_get_ancestors
    from vocabulary import get_descendants as ohdsi_get_descendants

# Need to import 'util.py', which lives in the nlp directory two levels up.
# This is a hack, and we really need a better solution...
module_dir = sys.path[0]
pos = module_dir.find('/nlp')
if -1 != pos:
    # get path to nlp directory and append to sys.path
    nlp_dir = module_dir[:pos+4]
    sys.path.append(nlp_dir)
import util

VERSION_MAJOR = 0
VERSION_MINOR = 7

MODULE_NAME = 'termset_expander.py'

global DEBUG
DEBUG = False

# load Spacy's English model
nlp = spacy.load('en_core_web_sm')

# initialize the CMU phoneme dictionary
cmu_dict = cmudict.dict()

# regexes for locating termsets in NLPQL files

# line comment - match everything from // up to but NOT including the newline
# also, don't match the // in a URL
str_line_comment = r'(?<!http:)(?<!https:)//.*(?=\n)'
regex_line_comment = re.compile(str_line_comment, re.IGNORECASE)

# multiline comment
str_multiline_comment = r'/\*.*?\*/'
regex_multiline_comment = re.compile(str_multiline_comment,
                                     re.IGNORECASE | re.DOTALL)

# a term is anything enclosed in double quotes
str_term = r'\"[^"]+\"'

# a term list is a final term, preceded by 0 or more terms, each
# of which is followed by a comma and optional whitespace
str_term_list = r'(' + str_term + r'\s*,\s*)*' + str_term

# nongreedy match up until final \*]; sequence
str_termset = r'\b(?P<termset>termset\s+(?P<termset_name>[^:]+)\s*:\s*' +\
              r'\[\s*(?P<term_list>[^;]+?)\s*\](?=[\s{1,80};]))'
regex_termset = re.compile(str_termset, re.IGNORECASE)

# macro components
str_namespace = r'[a-z]+'
str_macro_op = r'(Synonyms|LexicalVariants|Plurals|VerbInflections|' +\
               r'Descendants|Ancestors)'
str_macro_name = r'((?P<namespace>' + str_namespace + r')\.)?' +\
                 r'(?P<macro_op>' + str_macro_op + r')'

# the opening \s\[ and closing \s\] appear only in macros with array ags
str_macro_args = r'\s*\((\s*\[)?' +\
                 r'(?P<args>' + str_term_list + r')' +\
                 r'(\s*\])?\s*\)'

# comma following macro, if any
str_macro_comma = r'\s*(?P<comma>,?)'

str_macro = str_macro_name + str_macro_args + str_macro_comma
regex_macro = re.compile(str_macro, re.IGNORECASE)

# for finding comments that have been erased
COMMENT_REPLACEMENT_CHAR = '\x00' # will not occur in normal text
regex_erased_comment = re.compile(COMMENT_REPLACEMENT_CHAR + r'+',
                                  re.IGNORECASE)

EMPTY_STRING = ''
CHAR_SPACE   = ' '

# strings for operator matching
OP_STRING_PLURALS          = 'lural'
OP_STRING_SYNONYMS         = 'ynonym'
OP_STRING_VERB_INFLECTIONS = 'nflection'
OP_STRING_LEXICAL_VARIANTS = 'ariant'
OP_STRING_DESCENDANTS      = 'escendant'
OP_STRING_ANCESTORS        = 'ncestor'

MAX_NESTED_DEPTH = 2

NAMESPACE_CLARITY = 'clarity'
NAMESPACE_OHDSI   = 'ohdsi'

RETURN_TYPE_STRING = 0
RETURN_TYPE_LIST   = 1

str_consonant_ieds_end = r'[^aeiou]ie[ds]\Z'
regex_consonant_ieds_end = re.compile(str_consonant_ieds_end, re.IGNORECASE)

str_vowel_eds_end = r'[aeiou]e[ds]\Z'
regex_vowel_eds_end = re.compile(str_vowel_eds_end, re.IGNORECASE)

###############################################################################
def to_string(term_list, suffix=''):
    """
    Convert a list of terms to a single string representing the result of
    macro expansion.
    """

    if 0 == len(term_list):
        return None

    terms = ['"' + t + suffix + '"' for t in term_list]
    term_string = ','.join(terms)

    # enclose in brackets to represent an array
    term_string = '[' + term_string + ']'
    return term_string


###############################################################################
def log_token(token):
    """
    log useful token data to the screen for debugging.
    """

    log('[{0:3}]: {1:30}\t{2:6}\t{3:8}\t{4:12}\t{5}'.format(token.i,
                                                              token.text,
                                                              token.tag_,
                                                              token.pos_,
                                                              token.dep_,
                                                              token.head))

    
###############################################################################
def log_tokens(doc):
    """
    log all tokens in a SpaCy document.
    """

    log('\nTokens: ')
    log('{0:7}{1:30}\t{2:6}\t{3:8}\t{4:12}\t{5}'.format('INDEX', 'TOKEN', 'TAG',
                                                          'POS', 'DEP', 'HEAD'))
    for token in doc:
        log_token(token)


###############################################################################
def get_pronunciations(word):
    """
    Return the list of pronunciations for the given word, if any.
    """

    phoneme_lists = []
    try:
        phoneme_lists = cmu_dict[word]
    except:
        pass

    return phoneme_lists


###############################################################################
def expand(sentence, index_map):
    """
    Generates new sentences from the given sentence and the substitutions in
    the index map.

    Sentence: string containing words separated by whitespace
    index_map: dict, word_index_in_sentence -> list of words to substitute

    Example: sentence = 'the man walks the dog on Monday'

    index_map = {
        1:['man', 'boy', 'girl'],
        4:['dog', 'cat', 'bird'],
        6:['Monday', 'Tuesday', 'Wednesday']
    }

    This means the word at index 1 in the sentence ('man') needs to be
    substituted with ['man', 'boy', 'girl'] and similarly for the others.

    Note that the initial entries for each substitution list are the words
    in the original sentence.

    Generates new sentences, as many as len(cartesian_product) of all
    substitution lists. Duplicates are removed, though.
    """

    results = []

    # list of indices in which to make substitutions in word_list
    indices = [*index_map]

    # generate initial set of new sentences using substitutions[0] for all
    index = indices[0]
    substitutions = index_map[index]
    word_list = sentence.split()
    for w in substitutions:
        word_list[index] = w
        new_sentence = ' '.join(word_list)
        if new_sentence not in results:
            results.append(new_sentence)
    num_entries = len(results)

    # now use substitutions[1:] for all
    for index in indices[1:]:
        # get substitutions for this index
        substitutions = index_map[index]
        #log('subs: {0}'.format(substitutions))
        for w in substitutions[1:]:
            # for each result so far
            for r in results[:num_entries]:
                # substitute the word and form a new sentence
                word_list = r.split()
                word_list[index] = w
                new_sentence = ' '.join(word_list)
                if new_sentence not in results:
                    results.append(new_sentence)
        num_entries = len(results)

    return results


###############################################################################
def get_verb_base_form(word):
    """
    Attempt to get the base or bare infinitive form of the given verb by
    recognizing common verb endings and undoing them.
    """

    SPECIAL_CASES = {
        'has':'have',
        'having':'have',
        'is':'be',
        'are':'be',
        'being':'be',
    }

    verb = word.lower()

    # Is this a known irregular verb form?
    if verb in INFLECTION_MAP:
        return INFLECTION_MAP[verb]

    if verb in SPECIAL_CASES:
        return SPECIAL_CASES[verb]

    trial = verb

    if verb.endswith('cking') or verb.endswith('cked'):
        # assume base form ends with 'c' and a 'k' was added for cons doubling
        kpos = verb.rfind('k')
        trial = verb[:kpos]

        # if this is a word known to the CMU dict, return it
        if wordnet.morphy(trial, wordnet.VERB) is not None:
            return trial
        else:
            # keep the 'k'
            return verb[:kpos+1]

    if verb.endswith('ying'):
        # assume base form ends with 'ie', which was changed to 'ying'
        trial = verb[:-4] + 'ie'
        if wordnet.morphy(trial, wordnet.VERB) is not None:
            return trial
        else:
            # keep the y
            return verb[:-3]

    if verb.endswith('ing'):

        if len(verb) > 5:
            # check for repeated char before 'ing'
            if verb[-5] == verb[-4]:
                trial = verb[:-4]
                if wordnet.morphy(trial, wordnet.VERB) is not None:
                    return trial

            # assume base form ends with 'e', was dropped to add 'ing'
            trial = verb[:-3] + 'e'
            if wordnet.morphy(trial, wordnet.VERB) is not None:
                return trial

        # just return the word with 'ing' removed
        return verb[:-3]

    # check for -ied or -ies ending
    match = regex_consonant_ieds_end.search(verb)
    if match:
        # assume base form ends in consonant-y, which was
        # changed to consonant-ied
        trial = verb[:-3] + 'y'
        if wordnet.morphy(trial, wordnet.VERB) is not None:
            return trial

    # check for vowel-ed or vowel-es ending
    match = regex_vowel_eds_end.search(verb)
    if match:
        # drop the ending
        trial = verb[:-2]
        if wordnet.morphy(trial, wordnet.VERB) is not None:
            return trial

    # check for -ed, -es ending
    if verb.endswith('ed') or verb.endswith('es'):

        # drop the final char
        trial = verb[:-1]
        if wordnet.morphy(trial, wordnet.VERB) is not None:
            return trial

        # drop the ending
        trial = verb[:-2]
        if wordnet.morphy(trial, wordnet.VERB) is not None:
            return trial

        if len(verb) > 4:
            # check for repeated ending char
            if verb[-4] == verb[-3]:
                trial = verb[:-3]
                if wordnet.morphy(trial, wordnet.VERB) is not None:
                    return trial

    # check for -s ending
    if verb.endswith('s'):
        trial = verb[:-1]
        if wordnet.morphy(trial, wordnet.VERB) is not None:
            return trial

    return trial


###############################################################################
def get_single_word_synonyms(namespace, word, pos):
    """
    Return a list of synonyms for the given word with part of speech 'pos'.
    """

    assert pos==wordnet.NOUN or pos==wordnet.ADJ or pos==wordnet.ADV

    synonyms = []
    
    if NAMESPACE_CLARITY == namespace:
        # get all sets of synonyms from Wordnet
        synsets = wordnet.synsets(word.lower(), pos)
        for s in synsets:
            # the 'lemmas' for each set are the synonyms
            synonyms.extend(s.lemma_names())
    elif NAMESPACE_OHDSI == namespace:
        # get OHDSI synonyms from Postgres database (returns list of tuples)
        tuple_list = ohdsi_get_synonyms(util.conn_string, word.lower(), None)
        for t in tuple_list:
            synonyms.append(t[0])

    if len(synonyms) > 0:
        synonyms = [s.lower() for s in synonyms]
        uniques = sorted(list(set(synonyms)))
    else:
        uniques = [word]

    # rearrange so that the given word comes first
    if len(uniques) > 1:
        swap_index = uniques.index(word)
        uniques[0], uniques[swap_index] = uniques[swap_index], uniques[0]

    return uniques
        
            
###############################################################################
def get_synonyms(namespace, term_list, return_type=RETURN_TYPE_STRING):

    if DEBUG:
        debug_suffix = '_' + namespace + '_syn'
        return to_string(term_list, debug_suffix)

    synonyms = []
    for t in term_list:

        # if t contains a space, assume multiword term
        is_multiword = -1 != t.find(CHAR_SPACE)

        # get synonyms for term as a whole, whether multiword or not
        pos = [wordnet.NOUN, wordnet.ADJ, wordnet.ADV]
        for p in pos:
            new_syns = get_single_word_synonyms(namespace, t, p)
            synonyms.extend(new_syns)

        # include the term itself if not already present
        if t not in synonyms:
            synonyms.append(t)

        if is_multiword:
            # get parts of speech
            doc = nlp(t)
            if 1 == len(doc):
                continue

            # multi-word
            index_map = {}
            for token in doc:
                if 'NOUN' == token.pos_:
                    index_map[token.i] = (token.text, wordnet.NOUN)
                elif 'ADJ' == token.pos_:
                    index_map[token.i] = (token.text, wordnet.ADJ)
                elif 'ADV' == token.pos_:
                    index_map[token.i] = (token.text, wordnet.ADV)

            # if no entries, nothing to do
            if not index_map:
                continue
            else:
                # split into individual words
                words = t.split()

                # update indices in case spacy did not fully tokenize
                ok = True
                for index, token_and_pos in index_map.items():
                    if index < len(words):
                        token = token_and_pos[0]
                        if words[index] == token:
                            continue

                    # spacy tokenization is different from t.split()
                    for j in len(words):
                        if words[j] == token:
                            del index_map[index]
                            index_map[j] = token_and_pos
                        else:
                            # not found
                            ok = False
                            break

                    if not ok:
                        # treat this term t as being a single word
                        break

                if not ok:
                    continue

            # rebuild the index map with all synonyms
            for index, token_and_pos in index_map.items():
                token = token_and_pos[0]
                pos   = token_and_pos[1]
                syns = get_single_word_synonyms(namespace, token, pos)
                index_map[index] = syns
                
            # do the expansion
            #log('index map: {0}'.format(index_map))
            new_phrases = expand(t, index_map)
            #log('new phrases: {0}'.format(new_phrases))
            synonyms.extend(new_phrases)

    # convert to lowercase, remove duplicates, and sort
    if len(synonyms) > 0:
        synonyms = [s.lower() for s in synonyms]
        term_list = sorted(list(set(synonyms)))

    # remove WordNet underscores
    if NAMESPACE_CLARITY == namespace:
        term_list = [re.sub(r'_', ' ', t) for t in term_list]

    if RETURN_TYPE_LIST == return_type:
        return term_list
    else:
        return to_string(term_list)


###############################################################################
def get_plurals(namespace, term_list, return_type=RETURN_TYPE_STRING):

    if DEBUG:
        debug_suffix = '_' + namespace + '_p'
        return to_string(term_list, debug_suffix)

    new_terms = []
    for t in term_list:
        # include the original term also
        new_terms.append(t)
        plural_terms = plural(t.lower())
        new_terms.extend(plural_terms)
    term_list = new_terms

    if RETURN_TYPE_LIST == return_type:
        return term_list
    else:
        return to_string(term_list)


###############################################################################
def unique_inflections(inflections):
    """
    Convert the nested list of verb inflections to a set of unique values.
    """

    verb_list = [inflections[0]]

    for i in range(1, len(inflections)):
        verb_list.extend(inflections[i])

    unique_verb_list = list(set(verb_list))
    return unique_verb_list


###############################################################################
def get_single_verb_inflections(term):
    """
    Get all inflections for the given term.
    """

    verb = term.lower()
    base_form = get_verb_base_form(verb)
    inflections = get_inflections(base_form)
    # remove duplicates in the inflections
    verbs = unique_inflections(inflections)
    return verbs


###############################################################################
def get_verb_inflections(namespace, term_list, return_type=RETURN_TYPE_STRING):

    if DEBUG:
        debug_suffix = '_' + namespace + '_vi'
        return to_string(term_list, debug_suffix)

    new_terms = []
    for t in term_list:

        # if t contains a space, assume multiword term
        is_multiword = -1 != t.find(CHAR_SPACE)

        # assume verb if single word
        if not is_multiword:
            verbs = get_single_verb_inflections(t)
            new_terms.extend(verbs)
        else:
            # get parts of speech and find verbs
            doc = nlp(t)
            if 1 == len(doc):
                verbs = get_single_verb_inflections(t)
                new_terms.extend(verbs)
                continue

            # multi-word
            index_map = {}
            for token in doc:
                if 'VERB' == token.pos_:
                    index_map[token.i] = token.text

            # if no verbs, no inflections to compute
            if not index_map:
                verbs = get_single_verb_inflections(t)
                new_terms.extend(verbs)
                continue
            else:
                # split into individual words
                words = t.split()

                # update indices in case spacy did not fully tokenize
                ok = True
                for index, token in index_map.items():
                    if index < len(words):
                        token = index_map[index]
                        if words[index] == token:
                            continue

                    # spacy tokenization is different from t.split()
                    for j in len(words):
                        if words[j] == token:
                            del index_map[index]
                            index_map[j] = token
                        else:
                            # not found
                            ok = False
                            break

                    if not ok:
                        # treat as single word
                        verbs = get_single_verb_inflections(t)
                        new_terms.extend(verbs)
                        break

                if not ok:
                    continue

            # rebuild the index map with all inflections
            for index, token in index_map.items():
                verbs = get_single_verb_inflections(token)
                index_map[index] = verbs

            # do the expansion
            new_phrases = expand(t, index_map)
            new_terms.extend(new_phrases)

    # remove duplicates
    if len(new_terms) > 0:
        term_list = sorted(list(set(new_terms)))

    if RETURN_TYPE_LIST == return_type:
        return term_list
    else:
        return to_string(term_list)


###############################################################################
def get_lexical_variants(namespace, term_list):

    if DEBUG:
        debug_suffix = '_' + namespace + '_lv'
        return to_string(term_list, debug_suffix)
    
    if NAMESPACE_CLARITY == namespace:
        inflected_terms = get_verb_inflections(namespace, term_list, RETURN_TYPE_LIST)
        new_terms = get_plurals(namespace, inflected_terms, RETURN_TYPE_LIST)

        # remove duplicates and sort
        if len(new_terms) > 0:
            term_list = sorted(list(set(new_terms)))

    return to_string(term_list)


###############################################################################
def get_descendants(namespace, term_list, return_type=RETURN_TYPE_STRING):

    if DEBUG:
        debug_suffix = '_' + namespace + '_d'
        return to_string(term_list, debug_suffix)

    descendants = []
    if NAMESPACE_OHDSI == namespace:
        for t in term_list:
            term_descendants = ohdsi_get_descendants(util.conn_string, t.lower(), None)

            # term_descendants is a list of tuples, so convert to list
            for td in term_descendants:
                descendants.append(td[0])

    # remove duplicates
    if len(descendants) > 0:
        descendants = [d.lower() for d in descendants]
        descendants = sorted(list(set(descendants)))

    if RETURN_TYPE_LIST == return_type:
        return descendants
    else:
        return to_string(descendants)


###############################################################################
def get_ancestors(namespace, term_list, return_type=RETURN_TYPE_STRING):

    if DEBUG:
        debug_suffix = '_' + namespace + '_a'
        return to_string(term_list, debug_suffix)

    ancestors = []
    if NAMESPACE_OHDSI == namespace:
        for t in term_list:
            term_ancestors = ohdsi_get_ancestors(util.conn_string, t.lower(), None)

            # term_ancestors is a list of tuples, so convert to list
            for ta in term_ancestors:
                ancestors.append(ta[0])

    # remove duplicates
    if len(ancestors) > 0:
        ancestors = [a.lower() for a in ancestors]
        term_list = sorted(list(set(ancestors)))

    if RETURN_TYPE_LIST == return_type:
        return term_list
    else:
        return to_string(term_list)


###############################################################################
def expand_macros(str_termlist):
    """
    Rewrite an NLPQL termlist to include expanded terms.
    
    """

    text = str_termlist    
    for i in range(MAX_NESTED_DEPTH):
        matched_it = False
        prev_end = 0
        new_text = ''
        new_terms = []
        iterator = regex_macro.finditer(text)
        for match in iterator:
            matched_it = True
            matching_text = match.group()

            has_comma = False
            if match.group('comma') is not None:
                has_comma = True
                comma_group = match.group('comma')

            start = match.start()
            end   = match.end()
            if has_comma:
                end = end - len(comma_group)
            args = match.group('args').split(',')
            terms = [t.strip().strip('"') for t in args]

            macro_op = match.group('macro_op')
            if macro_op is None:
                log('Unsupported macro: {0}'.format(matching_text))
                sys.exit(-1)
            
            namespace = match.group('namespace')
            if namespace is None:
                namespace = NAMESPACE_CLARITY
            namespace = namespace.lower()

            if -1 != macro_op.find(OP_STRING_SYNONYMS):
                expansion_string = get_synonyms(namespace, terms)
            elif -1 != macro_op.find(OP_STRING_LEXICAL_VARIANTS):
                expansion_string = get_lexical_variants(namespace, terms)
            elif -1 != macro_op.find(OP_STRING_PLURALS):
                expansion_string = get_plurals(namespace, terms)
            elif -1 != macro_op.find(OP_STRING_VERB_INFLECTIONS):
                expansion_string = get_verb_inflections(namespace, terms)
            elif -1 != macro_op.find(OP_STRING_DESCENDANTS):
                expansion_string = get_descendants(namespace, terms)
            elif -1 != macro_op.find(OP_STRING_ANCESTORS):
                expansion_string = get_ancestors(namespace, terms)

            # invalid macros are not recognized and are ignored; the
            # syntax checker will eventually catch them

            # replace the macro with the expansion results, if any
            if expansion_string is not None:
                # found macro, expanded to a nonempty string
                new_text += text[prev_end:start]
                new_text += expansion_string
                if has_comma:
                    new_text += comma_group
                    end += len(comma_group)
            else:
                # found a macro, but it expanded to nothing, erase macro text
                new_text += text[prev_end:start]
                if has_comma:
                    end += len(comma_group)
            prev_end = end

        # append remaining text after the last macro
        new_text += text[prev_end:]
        text = new_text

        if not matched_it:
            break

    # remove any remaining bracket chars from the expansion
    text = re.sub(r'[\[\]]', '', text)

    # # remove duplicate terms and sort
    # terms = text.split(',')
    # terms = [t.strip() for t in terms]
    # terms = sorted(list(set(terms)))
    # text = ',\n'.join(terms)

    return text


###############################################################################
def expand_nlpql(nlpql_text):
    """
    Find all termsets with termset names in termset_name_list and add 
    plurals of each term.
    """

    prev_end = 0
    new_nlpql_text = ''

    # scan the string, find the term sets and expansion macros
    iterator = regex_termset.finditer(nlpql_text)
    for match in iterator:

        match_text = match.group()
        
        # locate the final closing bracket
        pos = match_text.rfind(']')
        
        termset_name = match.group('termset_name').strip().lower()
        termset_start  = match.start('termset')
        termset_end    = match.end('termset')
        termlist       = match.group('term_list')
        termlist_start = match.start('term_list')
        termlist_end   = match.end('term_list')

        # do the macro expansion
        expanded_termlist = expand_macros(termlist)

        # include the expansion in the result text
        new_nlpql_text += nlpql_text[prev_end:termlist_start]
        new_nlpql_text += expanded_termlist
        prev_end = termlist_end

    # final piece
    new_nlpql_text += nlpql_text[prev_end:]
    return new_nlpql_text

    
###############################################################################
def run(nlpql_text):
    """
    Perform the main work of this module.
    """

    if 0 == len(nlpql_text):
        return EMPTY_STRING

    # scan for comments and record the [start, end) spans for each comment
    comment_spans = []
    
    # scan for multi-line comments
    iterator = regex_multiline_comment.finditer(nlpql_text)
    for match in iterator:
        start = match.start()
        end   = match.end()
        comment_spans.append( (start, end))

    # scan for single-line comments
    iterator = regex_line_comment.finditer(nlpql_text)
    for match in iterator:
        matching_text = match.group()
        start = match.start()
        end   = match.end()
        
        # include in comment_spans if not included in a multiline comment
        include_it = True
        for cs in comment_spans:
            if start >= cs[0] and end <= cs[1]:
                include_it = False
                break
        if include_it:
            comment_spans.append( (start, end))

    # sort the comment spans by starting offset
    comment_spans = sorted(comment_spans, key=lambda x: x[0])

    # replace all comment spans with COMMENT_REPLACEMENT_CHAR
    nlpql_no_comments = ''
    prev_end = 0
    for cs in comment_spans:
        start = cs[0]
        end   = cs[1]
        nlpql_no_comments += nlpql_text[prev_end:start]
        nlpql_no_comments += COMMENT_REPLACEMENT_CHAR*(end - start) 
        prev_end = end
    nlpql_no_comments += nlpql_text[prev_end:]

    # do the macro expansion
    expanded_nlpql = expand_nlpql(nlpql_no_comments)

    # restore the comment strings
    i = 0
    restored_text = ''
    prev_end = 0
    iterator = regex_erased_comment.finditer(expanded_nlpql)
    for match in iterator:
        # replace these chars in expanded_nlpql
        start = match.start()
        end   = match.end()

        # with this text from nlpql_text
        cs = comment_spans[i]
        cs_start = cs[0]
        cs_end   = cs[1]
        assert cs_end-cs_start == end-start

        restored_text += expanded_nlpql[prev_end:start]
        restored_text += nlpql_text[cs_start:cs_end]
        prev_end = end
        i = i + 1

    # append final piece
    restored_text += expanded_nlpql[prev_end:]
    
    return restored_text


###############################################################################
def run_from_file(filepath):
    """
    Load the input file, read the data into a string, and perform macro
    expansion on the string.
    """

    if not filepath:
        raise ValueError('input file not specified')

    # make sure the input file exists
    if not os.path.isfile(filepath):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filepath)

    # load the file contents into a string
    try:
        infile = open(filepath, 'r')
    except (OSError, IOError) as e:
        return EMPTY_STRING
    except Exception as e:
        return EMPTY_STRING

    with infile:
        try:
            nlpql_text = infile.read()
        except UnicodeDecodeError as e:
            return EMPTY_STRING
        except (OSError, IOError) as e:
            return EMPTY_STRING
        except Exception as e:
            return EMPTY_STRING

    return run(nlpql_text)


###############################################################################
def run_tests():

    test_data = {
        'being':'be',
        'has':'have',
        'carrying':'carry',
        'carried':'carry',
        'carries':'carry',
        'identifying':'identify',
        'identified':'identify',
        'identifies':'identify',
        'echoing':'echo',
        'echoed':'echo',
        'echoes':'echo',
        'outdoing':'outdo',
        'outdid':'outdo',
        'outdone':'outdo',
        'trying':'try',
        'tried':'try',
        'tries':'try',
        'panicking':'panic',
        'panicked':'panic',
        'panics':'panic',
        'renewing':'renew',
        'renewed':'renew',
        'renews':'renew',
        'perplexing':'perplex',
        'perplexed':'perplex',
        'perplexes':'perplex',
        'shipping':'ship',
        'shipped':'ship',
        'ships':'ship',
        'viewing':'view',
        'viewed':'view',
        'views':'view',
        'dining':'dine',
        'dined':'dine',
        'canoeing':'canoe',
        'canoed':'canoe',
        'canoes':'canoe',
        'trotting':'trot',
        'trotted':'trot',
        'trots':'trot',
        'commenting':'comment',
        'commented':'comment',
        'comments':'comment',
        'seeing':'see',
        'saw':'see',
        'seen':'see',
        'dyeing':'dye',
        'dyed':'dye',
        'guessing':'guess',
        'guessed':'guess',
    }

    for verb, base in test_data.items():
        trial = get_verb_base_form(verb)
        if trial != base:
            log('get_base_form: verb: {0}, expected base form {1}, got {2}'.
                  format(verb, base, trial))

    # test expansion manually
    sentence = 'the man walks the dog on monday'
    index_map = {
        1:['man', 'boy', 'girl'],
        4:['dog', 'cat', 'bird'],
        6:['monday', 'tuesday', 'wednesday']
    }

    sentences = expand(sentence, index_map)
    log('Original: {0}'.format(sentence))
    for i in range(len(sentences)):
        log('\t[{0}]: {1}'.format(i, sentences[i]))
        
    # verb inflection
    sentences = get_verb_inflections(NAMESPACE_CLARITY, [sentence], RETURN_TYPE_LIST)
    log('\nOriginal: {0}'.format(sentence))
    for i in range(len(sentences)):
        log('\t[{0}]: {1}'.format(i, sentences[i]))

    # synonyms
    sentences = ['the food tastes great', 'the man owns a vehicle',
                 'the large vehicle', 'the sweetly singing bird']
    for s in sentences:
        new_phrases = get_synonyms(NAMESPACE_CLARITY, [s], RETURN_TYPE_LIST)
        log('\nOriginal: {0}'.format(s))
        for i in range(len(new_phrases)):
            log('\t[{0}]: {1}'.format(i, new_phrases[i]))


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(MODULE_NAME, VERSION_MAJOR, VERSION_MINOR)


###############################################################################
def show_help():
    log(get_version())
    log("""
    USAGE: python3 ./{0} -f <filename> [-hvsd]

    OPTIONS:

        -f, --file     <quoted string>               Path to NLPQL file.

    FLAGS:

        -h, --help           log this information and exit.
        -v, --version        log version information and exit.
        -s, --selftest       Run self-tests and exit.
        -d, --debug          Run in debug mode.

    """.format(MODULE_NAME))


###############################################################################
if __name__ == '__main__':

    optparser = optparse.OptionParser(add_help_option=False)
    optparser.add_option('-f', '--file', action='store',
                         dest='filepath')
    optparser.add_option('-v', '--version',  action='store_true',
                         dest='get_version')
    optparser.add_option('-h', '--help',     action='store_true',
                         dest='show_help', default=False)
    optparser.add_option('-s', '--selftest', action='store_true',
                         dest='selftest')
    optparser.add_option('-d', '--debug', action='store_true',
                         dest='debug')

    opts, other = optparser.parse_args(sys.argv)

    # show help if no command line arguments
    if opts.show_help or 1 == len(sys.argv):
        show_help()
        sys.exit(0)

    if opts.get_version:
        log(get_version())
        sys.exit(0)

    if opts.debug:
        DEBUG = True

    if opts.selftest:
        run_tests()
        sys.exit(0)

    expanded_nlpql = run_from_file(opts.filepath)

    # write results to stdout
    log(expanded_nlpql)
