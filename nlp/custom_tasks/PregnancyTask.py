# A custom task for determining dates releated to pregnancy.

import re
import os
import sys
import json
from pymongo import MongoClient
from datetime import date, timedelta

# modify path for local testing
if __name__ == '__main__':
    cur_dir = sys.path[0]
    nlp_dir, tail = os.path.split(cur_dir)
    sys.path.append(nlp_dir)
    sys.path.append(os.path.join(nlp_dir, 'tasks'))
    sys.path.append(os.path.join(nlp_dir, 'data_access'))

# ClarityNLP imports
import util
from tasks.task_utilities import BaseTask
from claritynlp_logging import log, ERROR, DEBUG
    
_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# set to True to enable debug output
_TRACE = True

_str_num = r'(\d+\.\d+|\.\d+|\d+)'
_str_duration = r'\b(weeks|months)\b'

# ranges: 10-12 weeks pregnant
_str_preg0 = r'\b(?P<num1>' + _str_num + r')\s?\-\s?'  +\
    r'(?P<num2>' + _str_num + r')\s?' +\
    r'(?P<duration>(weeks|wks\.?|wk|months|mo\.?|mos))\s?'    +\
    r'\b(preg|prg)'
_regex_preg0 = re.compile(_str_preg0, re.IGNORECASE)

# stated duration: 28 weeks pregnant
_str_preg1 = r'\b(?P<num>' + _str_num + r')' + r'\s?'      +\
    r'(?P<duration>(weeks|wks\.?|wk|months|mo\.?|mos))\s?'    +\
    r'\b(preg|prg)'
_regex_preg1 = re.compile(_str_preg1, re.IGNORECASE)

# pregnancy first: pregnant 24 wks
_str_preg2 = r'\b((pregnan(cy|t))|(woman|girl|female)\sat)[a-z\s]+'    +\
    r'(?P<num>' + _str_num + r')\s?' +\
    r'(?P<duration>(weeks|wks\.?|wk|months|mo\.?|mos))'
_regex_preg2 = re.compile(_str_preg2, re.IGNORECASE)

# coded: G4P2 @ 12 wks
_str_preg3 = r'\b(\d+)?G\d+(P\d+)?\s(at|@)\s(?P<num>' + _str_num + r')\s?' +\
    r'(?P<duration>(weeks|wks\.?|wk|months|mo\.?|mos))?'
_regex_preg3 = re.compile(_str_preg3, re.IGNORECASE)

# weeks and days: 19 week - 4 day pregnancy
_str_preg4 = r'\b(?P<num_wks>' + _str_num + r')\s?' +\
    r'(weeks?|wks?)\.?\s?(and|\-)\s?' +\
    r'(?P<num_days>' + _str_num + r')\s?' +\
    r'days?\spreg'
_regex_preg4 = re.compile(_str_preg4, re.IGNORECASE)

# conversion factors
_MONTHS_TO_WEEKS = 52.1429 / 12.0
_DAYS_TO_WEEKS   = 1.0 / 7.0


###############################################################################
def _cleanup_sentence(s):

    # strip commas
    s = re.sub(r',', '', s)
    
    # replace repeated whitespace with a single space
    s = re.sub(r'\s+', ' ', s)
    
    return s


###############################################################################
def _str_to_num(matchobj, group_name):
    """
    Convert a numeric match contained in the given match object to either
    a float or an int, depending on the presence of a decimal point.
    """
    
    num_str = matchobj.group(group_name).strip()
    if -1 == num_str.find('.'):
        num = int(num_str)
    else:
        num = float(num_str)

    return num


###############################################################################
def _get_duration(num, matchobj):
    """
    Compute the length of pregnancy in weeks and return.
    """
    
    weeks = None

    duration = matchobj.group('duration')
    if duration is not None:
        duration = duration.lower()
        if duration.startswith('w'):
            weeks = num
        elif duration.startswith('m'):
            weeks = num * _MONTHS_TO_WEEKS
        else:
            weeks = num * _DAYS_TO_WEEKS
    else:
        # no duration specified, assume weeks
        weeks = num

    return weeks


###############################################################################
def _compute_pregnancy_term(weeks_in, str_date):
    """
    Given a document date of the form 2162-02-16T00:00:00Z, compute the dates
    of conception and delivery assuming a standard 40 week pregnancy term.

    The parameter 'weeks_in' is a floating point number.

    Returns dates in ISO format.
    """

    pos = str_date.find('T')
    if -1 == pos:
        # unexpected format
        return None, None

    substr = str_date[:pos]
    year, month, day = substr.split('-')

    t0 = date(int(year), int(month), int(day))

    # compute integer weeks and days since conception
    int_weeks = int(weeks_in)
    fractional_weeks = weeks_in - float(int_weeks)
    int_days = int(fractional_weeks * 7.0)

    # timedelta object representing time since conception
    delta = timedelta(
        weeks = int_weeks,
        days  = int_days
    )

    conception_date = t0 - delta

    # compute integer weeks and days until delivery
    remaining_weeks = 40.0 - weeks_in
    int_weeks = int(remaining_weeks)
    fractional_weeks = remaining_weeks - float(int_weeks)
    remaining_days = int(fractional_weeks * 7.0)

    # timedelta object representing time until delivery
    delta = timedelta(
        weeks = int_weeks,
        days  = int_days
    )

    delivery_date = t0 + delta

    return conception_date.isoformat(), delivery_date.isoformat()
    

###############################################################################
def _find_weeks_pregnant(sentence):
    """
    Search for a pregnancy duration statement in the sentence, convert to weeks,
    and return as a floating point number.
    """

    s = _cleanup_sentence(sentence)

    num = None
    weeks = None
    match = None

    # find range, if any
    match = _regex_preg0.search(s)
    if match:
        num1 = _str_to_num(match, 'num1')
        num2 = _str_to_num(match, 'num2')
        # take the average
        num = 0.5 * (num1 + num2)
        weeks = _get_duration(num, match)

    if match is None:
        match = _regex_preg1.search(s)
        if match:
            num = _str_to_num(match, 'num')
            weeks = _get_duration(num, match)

    if match is None:
        match = _regex_preg2.search(s)
        if match:
            num = _str_to_num(match, 'num')
            weeks = _get_duration(num, match)

    if match is None:
        match = _regex_preg3.search(s)
        if match:
            num = _str_to_num(match, 'num')
            weeks = _get_duration(num, match)

    if match is None:
        match = _regex_preg4.search(s)
        if match:
            weeks = _str_to_num(match, 'num_wks')
            days = _str_to_num(match, 'num_days')
            weeks += days * _DAYS_TO_WEEKS

    if match is not None:
        return weeks, match.start(), match.end()
    else:
        return None, None, None
        

###############################################################################
class PregnancyTask(BaseTask):
    """
    A custom task for finding pregnancy-related temporal data.
    """

    # use this name in NLPQL
    task_name = "PregnancyTask"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):

        # for each document...
        for doc in self.docs:

            # get all sentences in this document
            sentence_list = self.get_document_sentences(doc)

            # document date, for relative time calculatios
            # format is 2162-02-16T00:00:00Z
            doc_date = doc['report_date']

            # find a pregnancy duration statement, if any, in the sentence
            for sentence in sentence_list:
                weeks, start, end = _find_weeks_pregnant(sentence)
                if weeks is None:
                    continue

                if weeks < 0:
                    continue
                
                # compute trimester
                if weeks <= 13:
                    trimester = 1
                elif weeks >= 14 and weeks <= 26:
                    trimester = 2
                else:
                    trimester = 3

                # compute weeks remaining
                weeks_remaining = 40 - weeks

                # compute estimated dates of conception and delivery
                date_conception, date_delivery = _compute_pregnancy_term(weeks, doc_date)
                highlights = []
                if start > -1:
                    if len(sentence) > end - 1:
                        end = end - 1
                    string = sentence[start:end]
                    highlights.append(string)
                obj = {
                    'sentence':sentence,
                    'start':start,
                    'end':end,
                    'weeks_pregnant':weeks,
                    'weeks_remaining':weeks_remaining,
                    'trimester':trimester,
                    'date_conception':date_conception,
                    'date_delivery':date_delivery,
                    'result_display': {
                        'sentence': sentence,
                        'highlights': highlights,
                        'start':[start],
                        'end':[end],
                        'result_content':sentence
                    }
                }

                self.write_result_data(temp_file, mongo_client, doc, obj)


###############################################################################
if __name__ == '__main__':

    TEST_STRINGS = [
        'she is approx. 28 weeks pregnant',
        'she is 21wks pregnant',
        'she is 2.5 months pregnant',
        'she is pregnant at 26wks',
        'she is 25 weeks preganant',
        'she is 23 wk pregnant',
        'she is 24 WEEKS PREGNANT',
        'she is approx. 10-12 weeks pregnant',
        'patient is a 23 year G4P2 @ 27',
        'patient is a 28G5P2 at 28.0wks',
        'patient is a 29 yo G1 @ 5.3wks',
        '25 year old woman with pregnancy, approx 6 weeks',
        '28 year old woman G1P0 , 6 WEEKS PREG',
        '30 y/o 24wks pregnant',
        '31 year old woman with 19 week - 4 day pregnancy (19wks and 4 days)',
        'Pregnant 16 weeks',
        '37 year old woman at 29 weeks',
        '29 year old woman at 31 weeks pregnant',
        '21 year old woman with 16 wks preganant',
        '30 year old woman who is 6 weeks pregnant',
        '39 year old woman with 20 wk pregnancy',
        '25 year old woman',
    ]

    for i,s in enumerate(TEST_STRINGS):
        
        print('[{0:2d}] {1}'.format(i, s))
        weeks, start, end = _find_weeks_pregnant(s)
        if weeks is not None:
            print('\t[{0}, {1}): weeks = {2}'.format(start, end, weeks))
            
            t0 = '2019-07-01T00:00:00Z'
            date_conception, date_delivery = _compute_pregnancy_term(weeks, t0)
            print('\tdate of conception: {0}'.format(date_conception))
            print('\t  date of delivery: {0}'.format(date_delivery))
        else:
            print('\tno match')
