from itertools import product

import regex as re
import json
from data_access import Measurement
from algorithms.segmentation import *
from algorithms.value_extraction import run_value_extractor

print('Initializing models for value extractor...')
segmentor = Segmentation()
print('Done initializing models for value extractor...')


def run_value_extractor_full(term_list, text, minimum_value, maximum_value, enumlist=list(), is_case_sensitive_text=False, denom_only=False):

    sentence_list = segmentor.parse_sentences(text)
    process_results = []
    matchers = [re.compile(r"\b%s\b" % t, re.IGNORECASE) for t in term_list]
    vals = product(sentence_list, matchers)
    for v in vals:
        sentence = v[0]
        matcher = v[1]
        match = matcher.search(sentence)
        if match:
            term = match.group(0)
            value_str = run_value_extractor(term, sentence, str_minval=minimum_value, str_maxval=maximum_value, enumlist=enumlist, is_case_sensitive=is_case_sensitive_text, is_denom_only=denom_only)
            if len(value_str) > 0:
                value_results = json.loads(value_str)
                if 'measurementList' in value_results:
                    measurement_results = value_results['measurementList']
                    for x in measurement_results:
                        process_results.append(
                            Measurement(sentence=sentence, text=x['matchingTerm'], start=x['start'], end=x['end'],
                                        condition=x['condition'], X=x['x'], Y=x['y']))

    return process_results


if __name__ == '__main__':
    res = run_value_extractor_full(["temperature", "temp", "T", "BP", "HR", "Sp02"],
                                   'Prior to transfer, his vitals were BP 119/53 and BP 105/43 sleeping, '
                                   'HR 103, RR 15, and SpO2 97% on NRB.',
                                   10, 500, is_case_sensitive_text=False)

    [print(str(t.to_json())) for t in res]
