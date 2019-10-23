#!/usr/bin/env python3
"""


OVERVIEW:


This module generates plural forms of words and phrases.


FUNCTIONS:


    Use this function for phrases or if the part of speech is unknown. Returns
    a list of strings representing the plural forms of the input string.

        plural(text_string)

    Use one of these functions if the part of speech is known. All return a
    list of strings representing the plural forms of the input string:

        plural_noun(noun_string)
        plural_verb(verb_string)
        plural_adj(adjective_string)

    This module also provides the capability to generate plural forms for
    NLPQL termsets. Given an NLPQL file and a list of termset names, call
    the run function to generate NLPQL with the plural forms added to the
    specified termsets:

        run(nlpql_filepath, termset_name_list)

    This capability can also be accessed via command line. For instance,
    to generate plural forms for the termsets named 'BoneTermset' and 
    'LiverTermset' in the NLPQL file 'condition.nlpql', run this command:

        python3 ./pluralize.py -f "condition.nlpql" -t "BoneTermset, LiverTermset" > out.nlpql

"""

import re
import os
import sys
import inflect
import optparse
from claritynlp_logging import log, ERROR, DEBUG

VERSION_MAJOR = 0
VERSION_MINOR = 1

MODULE_NAME = 'pluralize.py'

engine = inflect.engine()

# regexes for locating termsets in NLPQL files

# a term is anything enclosed in double quotes
str_term = r'\"[^"]+\"'

# a term list is a final term, preceded by 0 or more terms, each
# of which is followed by a comma and optional whitespace
str_term_list = r'(' + str_term + r',\s*)*' + str_term

str_termset = r'\b(?P<termset>termset\s+(?P<termset_name>[^:]+):\s*\[\s*' +\
              r'(?P<term_list>' + str_term_list + r')\s*\];)'

regex_termset = re.compile(str_termset, re.IGNORECASE)

EMPTY_STRING = ''

# mapping of word or phrase to list of plurals
# all words/phrases that inflect gets wrong should go here, with corrections
MISTAKES = {
    'punched out bone':['punched out bones'],
    'punched out lesion':['punched out lesions'],
    'punched out region':['punched out regions'],
}

###############################################################################
def plural_noun(str_noun):
    """
    Return a list of plural forms for the given SINGULAR noun.

    Examples:
        plural_noun('I')    => 'we'
        plural_noun('mine') => 'ours'
        plural_noun('car')  => 'cars'
    """

    result_list = []

    if text in MISTAKES:
        result_list.extend(MISTAKES[str_noun])
    else:
        modern_plural = engine.plural_noun(str_noun)
        result_list.append(modern_plural)

        engine.classical()
        classical_plural = engine.plural_noun(str_noun)
        if classical_plural not in result_list:
            result_list.append(classical_plural)
        engine.classical(all=False)

    return result_list

###############################################################################
def plural_verb(str_verb):
    """
    Return a list of plural forms for the given SINGULAR verb.

    Examples: 
        plural_verb('is') => 'are'
        plural_verb('am') => 'are'
    """

    result_list = []

    if text in MISTAKES:
        result_list.extend(MISTAKES[str_verb])
    else:
        modern_plural = engine.plural_verb(str_verb)
        result_list.append(modern_plural)

        engine.classical()
        classical_plural = engine.plural_verb(str_verb)
        if classical_plural not in result_list:
            result_list.append(classical_plural)
        engine.classical(all=False)

    return result_list


###############################################################################
def plural_adj(str_adj):
    """
    Return a list of plural forms for the given SINGULAR adjective.

    Examples:
        plural_adj('a')    => 'some'
        plural_adj('this') => 'these
    """

    result_list = []

    if text in MISTAKES:
        result_list.extend(MISTAKES[str_adj])
    else:
        modern_plural = engine.plural_adj(str_adj)
        result_list.append(modern_plural)

        engine.classical()
        classical_plural = engine.plural_adj(str_adj)
        if classical_plural not in result_list:
            result_list.append(classical_plural)
        engine.classical(all=False)

    return result_list


###############################################################################
def plural(text):
    """
    The input text is either a single word or a phrase, assumed SINGULAR.

    This function determines the plural forms of the input text and returns
    a list of those forms. Both modern and 'classical' plurals are returned.
    """

    result_list = []

    if text in MISTAKES:
        result_list.extend(MISTAKES[text])
    else:
        modern_plural = engine.plural(text)
        result_list.append(modern_plural)

        engine.classical()
        classical_plural = engine.plural(text)
        if classical_plural not in result_list:
            result_list.append(classical_plural)
        engine.classical(all=False)

    return result_list


###############################################################################
def pluralize_termlist(str_termlist):
    """
    Rewrite an NLPQL termlist to include plural forms.
    """

    terms = str_termlist.split(',')

    # remove newlines and double quotes
    terms = [t.strip().strip('"') for t in terms]

    terms_with_plurals = []
    for t in terms:
        # include the original term
        terms_with_plurals.append('"' + t + '"')
    
        # as well as any plurals
        plurals = plural(t)
        for p in plurals:
            terms_with_plurals.append('"' + p + '"')

    # append all new terms with comma separator (except for the last)
    new_list = [t + ',\n' for t in terms_with_plurals[:-1]]
    new_termlist = ''.join(new_list)

    # append final term
    new_termlist += terms_with_plurals[-1]
    return new_termlist


###############################################################################
def pluralize_nlpql(nlpql_text, termset_name_list):
    """
    Find all termsets with termset names in termset_name_list and add 
    plurals of each term.
    """

    prev_end = 0
    new_nlpql_text = ''

    pluralize_all_termsets = 0 == len(termset_name_list)

    # scan the string, find the term sets, and add plurals to the term lists
    iterator = regex_termset.finditer(nlpql_text)
    for match in iterator:

        if not pluralize_all_termsets:
            termset_name = match.group('termset_name').strip().lower()
            if not termset_name in termset_name_list:
                continue

        termset_start  = match.start('termset')
        termset_end    = match.end('termset')
        termlist       = match.group('term_list')
        termlist_start = match.start('term_list')
        termlist_end   = match.end('term_list')
        
        termlist_with_plurals = pluralize_termlist(termlist)

        new_nlpql_text += nlpql_text[prev_end:termlist_start]
        new_nlpql_text += termlist_with_plurals
        prev_end = termlist_end

    new_nlpql_text += nlpql_text[prev_end:]
    return new_nlpql_text

    
###############################################################################
def run(filepath, termset_name_list):
    """
    Perform the main work of this module.
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

    if 0 == len(nlpql_text):
        return EMPTY_STRING

    new_nlpql_text = pluralize_nlpql(nlpql_text, termset_name_list)
    return new_nlpql_text

###############################################################################
def split_option_args(option, opt, value, parser):
    """
    Extract individual option args from a comma-separated list.
    """

    item_list = value.split(',')
    item_names = [item.strip().lower() for item in item_list]
    setattr(parser.values, option.dest, item_names)

###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(MODULE_NAME, VERSION_MAJOR, VERSION_MINOR)
        
###############################################################################
def show_help():
    log(get_version())
    log("""
    USAGE: python3 ./{0} -f <filename> [-t termset_names] [-hv]

    OPTIONS:

        -f, --file     <quoted string>               Path to NLPQL file to be pluralized.
        -t, --termsets <quoted comma-separated list> Names of termsets to pluralize.

    FLAGS:

        -h, --help           log this information and exit.
        -v, --version        log version information and exit.

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
    optparser.add_option('-t', '--termsets', type='string',
                         action='callback',
                         dest='termset_name_list',
                         callback=split_option_args)

    opts, other = optparser.parse_args(sys.argv)

    # show help if no command line arguments
    if opts.show_help or 1 == len(sys.argv):
        show_help()
        sys.exit(0)

    if opts.get_version:
        log(get_version())
        sys.exit(0)

    termset_name_list = []
    if opts.termset_name_list:
        termset_name_list = opts.termset_name_list

    pluralized_nlpql = run(opts.filepath, termset_name_list)

    # write results to stdout
    log(pluralized_nlpql)
