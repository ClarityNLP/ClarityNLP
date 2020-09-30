import os
import re
import sys
import gzip
import json
import spacy
import difflib
from collections import defaultdict, namedtuple

if __name__ == '__main__':
    # for interactive testing only
    match = re.search(r'nlp/', sys.path[0])
    if match:
        nlp_dir = sys.path[0][:match.end()]
        sys.path.append(nlp_dir)
    else:
        print('\n*** covid_finder.py: nlp dir not found ***\n')
        sys.exit(0)

    import covid_finder
        
_DATA_DIR = '/Users/richardboyd/data/covid19/data'

# finds "/ 7 days ago", "/ 1 week ago", etc.
_str_sep = r'/\s\d+\s(week|day)s?\sago'
_regex_sep = re.compile(_str_sep, re.IGNORECASE)


_nlp = spacy.load("en_core_web_sm")

_EMPTY_STRING = ''
_CHAR_SPACE   = ' '

_FinderResult = namedtuple('_FinderResult', ['frag', 'count'])
_EMPTY_FINDER_RESULT = _FinderResult(frag = _EMPTY_STRING, count = 0)


###############################################################################
def _extract_text(raw):
    """
    Extract the text from a covid19 scraper-generated JSON file.
    """

    _KEY_TEXT = 'full_text'
    
    obj = json.loads(raw)

    texts = []
    for i,doc in enumerate(obj):
        if _KEY_TEXT in doc:
            text = doc[_KEY_TEXT]
            if text is None:
                continue
            if len(text) > 0 and not text.isspace():
                texts.append(text)

    return texts
    

###############################################################################
def _split_on_regex(regex, text):

    sentences = []
    
    prev = 0
    iterator = regex.finditer(text)
    for match in iterator:
        start = match.start()
        end   = match.end()
        match_text = text[prev:start]
        sentences.append(match_text)
        prev = end
    sentences.append(text[prev:])
    return sentences


###############################################################################
def _extract_uniques(covid_finder_result, deduped, matcher):
    """
    """

    KEY_CASE = 'value_case'
    KEY_SENT = 'sentence'
    
    data = json.loads(covid_finder_result)
    for d in data:
        if KEY_CASE in d:
            case_count = d[KEY_CASE]
            if case_count is None:
                continue
            elif case_count > 1:
                cleaned_sentence = d[KEY_SENT]
                # get extent of cleaned sentence captured with the case count
                case_start = d['case_start']
                case_end   = d['case_end']
                frag = cleaned_sentence[case_start:case_end]
                print('CLEANED: "{0}"'.format(cleaned_sentence))
                print('   FRAG: "{0}"'.format(frag))

                if case_count not in deduped:
                    # first occurrence of this case count
                    deduped[case_count].add(cleaned_sentence)
                    print('\tadding cleaned sentence (first occurrence)')
                else:
                    # check against existing sentences
                    sentence_set = deduped[case_count]

                    if cleaned_sentence in sentence_set:
                        # this is a duplicate, so skip
                        continue
                    else:
                        # find longest common substring between the current
                        # cleaned sentence and the others in the set
                        n = len(cleaned_sentence)
                        has_overlap = False
                        for s in sentence_set:
                            matcher.set_seqs(cleaned_sentence, s)
                            match = matcher.find_longest_match(0, n, 0, len(s))
                            start = match.a
                            end   = match.a + match.size
                            lcs = cleaned_sentence[start:end]

                            # check for overlap of lcs with frag;
                            # overlap must include the case count
                            #if case_end < start or case_start >= end:
                            if case_end > start and case_start < end:
                                # frag is a substring of an existing sentence                                
                                has_overlap = True
                                print('\tFrag overlaps "{0}"'.format(s))
                                break

                        if not has_overlap:
                            # add to set for this count
                            deduped[case_count].add(cleaned_sentence)
                            print('\tadding cleaned sentence (no overlap)')

###############################################################################
def _print_count_map(count_map):
    
    print()
    print('COUNT MAP: ')
    for count,frag_map in count_map.items():
        print(count)
        if 0 == len(frag_map):
            print('\tempty count map')
        else:
            for frag,index_list in frag_map.items():
                print('\t"{0}" => {1}'.format(frag, index_list))
    print()
                                

###############################################################################
def _build_count_map(finder_results):

    count_map = defaultdict(list)    
    for i, fr in enumerate(finder_results):
        count_map[fr.count].append(i)

    # group each list according to fragments
    replacements = {}
    for count, index_list in count_map.items():
        the_map = defaultdict(list)
        for i in index_list:
            frag = finder_results[i].frag
            if len(frag) > 0:
                the_map[frag].append(i)
        replacements[count] = the_map

    count_map = replacements

    if 1 == len(count_map):
        keys = [k for k in count_map.keys()]
        frag_map = count_map[keys[0]]
        if 0 == len(frag_map):
            return {}
    
    return count_map

    
###############################################################################
def _fuzzy_match(str1, str2):
    """
    Determine whether two Covid case count fragments have the same meaning.
    """

    str_coronavirus = r'(covid([-\s]?19)?|(novel\s)?(corona)?virus|disease)' \
        r'([-\s]related)?\s?'

    # erase coronavirus string
    str1 = re.sub(str_coronavirus, _EMPTY_STRING, str1)
    str2 = re.sub(str_coronavirus, _EMPTY_STRING, str2)

    # erase qualifiers
    str_qual = r'\b(new|additional|more(\sthan)?|(self\-)?reported|confirmed|' \
        r'suspected|active|positive|over)\b'
    str1 = re.sub(str_qual, _EMPTY_STRING, str1)
    str2 = re.sub(str_qual, _EMPTY_STRING, str2)

    # collapse repeated whitspace
    str1 = re.sub(r'\s+', _CHAR_SPACE, str1).strip()
    str2 = re.sub(r'\s+', _CHAR_SPACE, str2).strip()    
    if str1 == str2:
        return True

    print('NO MATCH: ')
    print('\tstr1: "{0}"'.format(str1))
    print('\tstr2: "{0}"'.format(str2))

    return False
            

###############################################################################
def _process_all_files(output_file, directory):
    """
    """

    for d in os.listdir(directory):
        fullpath = os.path.join(directory, d)
        if os.path.isdir(fullpath):
            for f in os.listdir(fullpath):
                filepath = os.path.join(fullpath, f)
                if os.path.isfile(filepath):
                    print(filepath)
                    text_list = []
                    finder_results = []
                    if filepath.endswith('.json'):
                        with open(filepath, 'rt') as infile:
                            raw = infile.read()
                            text_list = _extract_text(raw)
                    elif filepath.endswith('.json.gz'):
                        with gzip.open(filepath, 'rb') as infile:
                            raw = infile.read()
                            text_list = _extract_text(raw)
                    if len(text_list) > 0:
                        for text in text_list:
                            # use spacy to tokenize sentences
                            doc = _nlp(text)
                            sentences = [sent.text for sent in doc.sents]
                            for i,sentence in enumerate(sentences):
                                sentence = re.sub(r'\s+', ' ', sentence)
                                sentences2 = _split_on_regex(_regex_sep, sentence)
                                for s2 in sentences2:
                                    result = covid_finder.run(s2)
                                    data = json.loads(result)
                                    if 0 == len(data):
                                        finder_results.append(_EMPTY_FINDER_RESULT )
                                    else:
                                        for d in data:
                                            count = d['value_case']
                                            if count is None:
                                                break
                                            cleaned_sentence = d['sentence']
                                            start = d['case_start']
                                            end = d['case_end']
                                            frag = cleaned_sentence[start:end]
                                            fr = _FinderResult(frag, count)
                                            finder_results.append(fr)

                        # collect all items having identical counts
                        count_map = _build_count_map(finder_results)
                        _print_count_map(count_map)

                        # fuzzy match on fragments with identical counts
                        for count, frag_map in count_map.items():
                            # all fragments having this count
                            fragment_list = [k for k in frag_map.keys()]
                            num_fragments = len(fragment_list)
                            if 1 == num_fragments:
                                continue

                            to_merge = []
                            for i in range(num_fragments):
                                for j in range(i+1, num_fragments):
                                    frag_i = fragment_list[i]
                                    frag_j = fragment_list[j]

                                    identical = _fuzzy_match(frag_i, frag_j)
                                    if identical:
                                        to_merge.append( (i, j) )
                                        print('fuzzy match for "{0}" and "{1}"'.format(frag_i, frag_j))

                            for i,j in to_merge:
                                # add j's indices to i's, delete j
                                frag_i = fragment_list[i]
                                frag_j = fragment_list[j]
                                frag_map[frag_i].extend(frag_map[frag_j])
                                del frag_map[frag_j]

                            # remove any duplicates in the fragment lists
                            for k in frag_map.keys():
                                v = frag_map[k]
                                frag_map[k] = sorted(list(set(v)))

                        print(filepath)
                        _print_count_map(count_map)
                                    
    
# ###############################################################################
# def _process_all_files(output_file, directory):

#     with open(output_file, 'wt') as outfile:
    
#         for d in os.listdir(directory):
#             fullpath = os.path.join(directory, d)
#             if os.path.isdir(fullpath):
#                 for f in os.listdir(fullpath):
#                     filepath = os.path.join(fullpath, f)
#                     if os.path.isfile(filepath):
#                         print(filepath)
#                         text_list = []
#                         if filepath.endswith('.json'):
#                             with open(filepath, 'rt') as infile:
#                                 raw = infile.read()
#                                 text_list = _extract_text(raw)
#                         elif filepath.endswith('.json.gz'):
#                             with gzip.open(filepath, 'rb') as infile:
#                                 raw = infile.read()
#                                 text_list = _extract_text(raw)
#                         if len(text_list) > 0:
#                             outfile.write('{0}\n'.format(f))
#                             for text in text_list:
#                                 doc = _nlp(text)
#                                 sentences = [sent.text for sent in doc.sents]
#                                 results = []
#                                 for i,sentence in enumerate(sentences):
#                                     sentence = re.sub(r'\s+', ' ', sentence)
#                                     sentences2 = _split_on_regex(_regex_sep, sentence)
#                                     for s2 in sentences2:
#                                         finder_result = covid_finder.run(s2)
#                                         _extract_uniques(finder_result, deduped, matcher)
#                                 #         data = json.loads(finder_result)
#                                 #         for d in data:
#                                 #             if 'value_case' in d:
#                                 #                 case_count = d['value_case']
#                                 #                 if case_count is None:
#                                 #                     continue
#                                 #                 elif case_count > 1:
#                                 #                     #start = d['case_start']
#                                 #                     #end   = d['case_end']
#                                 #                     #matching_text = sentence[start:end]
#                                 #                     results.append( (case_count, s2) )
#                                 #                     #outfile.write('\t[{0}]:\t{1}\n'.format(i, sentence))
#                                 #                     #outfile.write('\t\t{0}\n'.format(case_count))

#                                 # prev = ''
#                                 # for count,sent in results:
#                                 #     if sent in written:
#                                 #         continue
#                                 #     if sent != prev:
#                                 #         outfile.write('\t{0}\n'.format(sent))
#                                 #         prev = sent
#                                 #         written.add(sent)
#                                 #     outfile.write('\t\t{0}\n'.format(count))

                                                                

###############################################################################
if __name__ == '__main__':

    _process_all_files('outbreaks.txt', _DATA_DIR)
    sys.exit(0)

    # from '20200903_TN_wate_news.json'
    STRINGS = [
        # 1502
	"Schools, teachers considered 'essential' Video Tennessee Coronavirus: 1,502 new COVID-19 cases reported on Wednesday; an increase of less than 1% by Jack Lail / Sep 2, 2020 NASHVILLE, Tenn.",
        "(WATE) Tennessee reported 1,502 new coronavirus cases on Wednesday, a 0.96% increase.",
	"Tennessee Coronavirus: 1,502 new COVID-19 cases reported on Wednesday; an increase of less than 1% Video Dollywoods Harvest Festival, Great Pumpkin LumiNights returning Sept. 25 Video Suspect accused of killing mother, stabbing grandmother in Sevier County home still at large Video It sucksI",
	"Click here for more coverage of Baby Joe Clyde Daniels Man found shirtless with pants halfway down in Nashville couples home is charged, police say Tennessee Coronavirus: 1,502 new COVID-19 cases reported on Wednesday; an increase of less than 1% Hearing in Baby Joe case postponed after witnesses exposed to COVID-19 ",
	"Read the Full Article Video Tennessee Coronavirus: 1,502 new COVID-19 cases reported on Wednesday; an increase of less than 1% by Jack Lail / Sep 2, 2020 NASHVILLE, Tenn."
	"Tennessee Coronavirus: 1,502 new COVID-19 cases reported on Wednesday;",

        # 288
	"Officials also confirmed 288 new cases of the virus, for a total now of at least 119,426 across the state.",
	"Massachusetts reports 22 new COVID deaths, 288 coronavirus cases on WednesdayBrockton and Sutton downgraded on coronavirus risk map to moderate risk; 8 communities now at high riskCoronavirus in Mass.:",
	"Massachusetts reports 22 new COVID deaths, 288 coronavirus cases on WednesdayUS surpasses 6 million COVID cases, but pace slowing; 25 million infected worldwideMassachusetts approved for additional unemployment funds after weekly $600 federal aid expiredCoronavirus in Mass.:",

        # 849
	 "Video Ohio coronavirus numbers: 849 more cases reported Coronavirus ",
	"10-1 Ohio State football player says hes recovering well after shooting Video Ohio coronavirus numbers: 849 more cases reported Coronavirus ",
	"According to the State of Ohio COVID-19 dashboard, there have now been 115, 651 cases of coronavirus reported since the pandemic began.",
	"Thats 849 additional cases since Sunday."

        # 6
	"Black Hills State University reported six self-reported positive cases among students, and 17 students and staff members are currently in isolation, according to information provided by the university. ",
	"Meade County reported six new cases for a total of 176 cases.",

        # 3100
	"On Saturday, Arizona reported more than 3,100 new coronavirus cases, another daily record, according to the state Health Services Department.",
	"The Arizona Department of Health Services has now reported more than 3,100 coronavirus cases on back-to-back days with its latest update.",

        # 1157
	"CDC asking states to be ready to distribute COVID-19 vaccine as early as October Youngstown businesses reopen doors as YSU students return to campus Video Men accused of spray painting Trump onto political signs, mailboxes and driveways in Trumbull County Visiting judge assigned to candidate complicity case in Columbiana County Tractor-trailer crash causes traffic delays in Hubbard Township Activist calls on others to take stand against Youngstowns failing school district Video Boardman school buses sprayed with extra layer of protection from COVID-19 New military plane takes to skies above Valley for training Video Restoration service sends local team to help with Hurricane Laura recovery efforts Video New Castle man arrested in womans 2016 overdose death Coronavirus in Ohio Wednesday update: 1,157 new cases, 11 additional deaths Video Iowa man charged with sexually assaulting runaway teen from Lawrence County ",
	"Men accused of spray painting Trump onto political signs, mailboxes and driveways in Trumbull County Visiting judge assigned to candidate complicity case in Columbiana County Tractor-trailer crash causes traffic delays in Hubbard Township Activist calls on others to take stand against Youngstowns failing school district Boardman school buses sprayed with extra layer of protection from COVID-19 New military plane takes to skies above Valley for training Restoration service sends local team to help with Hurricane Laura recovery efforts New Castle man arrested in womans 2016 overdose death Coronavirus in Ohio Wednesday update: 1,157 new cases, 11 additional deaths Video Iowa man charged with sexually assaulting runaway teen from Lawrence County ",

        # 239
	"Data released Wednesday notes 239 new COVID-19 cases in Nevada and 141 in Clark County.",
	"There were 239 new cases reported in the last day. ",
	"Of Nevadas 239 new COVID-19 cases, 141 of them were reported in Clark County on Tuesday, according to data released by theSouthern Nevada Health District (SNHD)on Wednesday. ",
        
    ]

    num_strings = len(STRINGS)    
    

    # get simplified CovidFinder results
    finder_results = []
    for s in STRINGS:
        result = covid_finder.run(s)
        data = json.loads(result)
        if 0 == len(data):
            finder_results.append( EMPTY_FINDER_RESULT )
        else:
            for d in data:
                count = d['value_case']
                if count is None:
                    break
                cleaned_sentence = d['sentence']
                start = d['case_start']
                end = d['case_end']
                frag = cleaned_sentence[start:end]
                fr = _FinderResult(frag, count)
                finder_results.append(fr)

    # collect all items having identical counts
    count_map = _build_count_map(finder_results)
    _print_count_map(count_map)
            
    # fuzzy match on fragments with identical counts
    for count, frag_map in count_map.items():
        # all fragments having this count
        fragment_list = [k for k in frag_map.keys()]
        num_fragments = len(fragment_list)
        if 1 == num_fragments:
            continue

        to_merge = []
        for i in range(num_fragments):
            for j in range(i+1, num_fragments):
                frag_i = fragment_list[i]
                frag_j = fragment_list[j]

                identical = _fuzzy_match(frag_i, frag_j)
                if identical:
                    to_merge.append( (i, j) )
                    print('fuzzy match for "{0}" and "{1}"'.format(frag_i, frag_j))
                    
        for i,j in to_merge:
            # add j's indices to i's, delete j
            frag_i = fragment_list[i]
            frag_j = fragment_list[j]
            frag_map[frag_i].extend(frag_map[frag_j])
            del frag_map[frag_j]

        # remove any duplicates in the fragment lists
        for k in frag_map.keys():
            v = frag_map[k]
            frag_map[k] = sorted(list(set(v)))

    _print_count_map(count_map)
        
    # IMPORTANT to set autojunk to False
    # matcher = difflib.SequenceMatcher(isjunk=None, autojunk=False)

    # lcs_map = defaultdict(set)

    # num_strings = len(STRINGS)
    # for i in range(num_strings):
    #     if 0 == len(finder_results[i]):
    #         continue

    #     si      = finder_results[i].cleaned_sentence
    #     start_i = finder_results[i].start
    #     end_i   = finder_results[i].end
    #     frag_i  = finder_results[i].frag
    #     print('    si: "{0}"'.format(si))
    #     print('frag_i: "{0}"'.format(frag_i))
        
    #     for j in range(i+1, num_strings):
    #         if 0 == len(finder_results[j]):
    #             continue

    #         sj      = finder_results[j].cleaned_sentence
    #         start_j = finder_results[j].start
    #         end_j   = finder_results[j].end
    #         frag_j  = finder_results[j].frag

    #         matcher.set_seqs(si, sj)
    #         match = matcher.find_longest_match(0, len(si), 0, len(sj))
    #         start = match.a
    #         end   = match.a + match.size
    #         # lcs = longest common substring
    #         lcs = si[start:end].strip()
    #         print('\tLCS ({0}, {1}):\t{2}'.format(i, j, lcs))

    #         # look for a number in the lcs (not covid-19)
    #         match = re.search(r'(?<!covid[-\s])\d{1,3}((,\d\d\d)+)?', lcs)
    #         if not match:
    #             continue

    #         # entries at indices i and j share the same lcs
    #         lcs_map[lcs].add(i)
    #         lcs_map[lcs].add(j)

    # # find any results that share the same covid case count fragment            
    # frag_map = defaultdict(set)
    # index = 0
    # for lcs,index_set in lcs_map.items():
    #     for index in index_set:
    #         frag = finder_results[index].frag
    #         frag_map[frag].add(index)

    # print()
    # print('FRAG MAP: ')
    # for k,v in frag_map.items():
    #     print('"{0}" => "{1}"'.format(k, v))
    #     for index in v:
    #         print('\t{0}'.format(finder_results[index].frag))
            
    # print()
    # print('LCS MAP: ')
    # for k,v in lcs_map.items():
    #     print('"{0}" => "{1}"'.format(k, len(v)))



    
    # deduped = defaultdict(set)    
    # for sentence in STRINGS:
    #     finder_result = covid_finder.run(sentence)
    #     _extract_uniques(finder_result, deduped, matcher)
    # for k,v in deduped.items():
    #     print('{0} => {1}'.format(k,v))
