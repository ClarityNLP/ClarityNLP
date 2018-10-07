import re

# Race is sourced form nlp.custom_tasks.RaceFinderTask
str_sep = r'(\s-\s|-\s|\s-|\s)'

str_category = r'\b(american indian|'                      +\
               r'alaska native|asian|'                     +\
               r'african american|black|negro|'            +\
               r'native hawaiian|'                         +\
               r'other pacific islander|'   +\
               r'pacific islander|'                        +\
               r'native american|'                         +\
               r'white|caucasian|european)\b'

regex_race1 = re.compile(str_category, re.IGNORECASE)

RACE_REGEXES = [regex_race1]


def find_race(sentence_list):
    """
    Scan a list of sentences and run race-finding regexes on each.
    Returns a list of RaceFinderResult namedtuples. Currently returns only
    the first result found.
    """

    result_list = []

    found_match = False
    for i in range(len(sentence_list)):
        s = sentence_list[i]
        for regex in RACE_REGEXES:
            match = regex.search(s)
            if match:
                match_text = match.group('category')
                start = match.start()
                end   = match.end()
                result = (i, start, end, match_text)
                result_list.append(result)
                found_match = True
                break

        # Reports are unlikely to have more than one sentence stating the
        # patient's race.
        if found_match:
            break
    if len(result_list) > 0:
        print(result_list[0])
        return result_list[0]
    else:
        return ''


if __name__ == "__main__":
    print('parse')
    find_race("white")

