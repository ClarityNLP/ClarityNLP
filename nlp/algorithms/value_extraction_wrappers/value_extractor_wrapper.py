from itertools import product

import regex as re

from data_access import Measurement
from algorithms.segmentation import *
from algorithms.value_extraction.value_extractor import extract_value

print('Initializing models for value extractor...')
segmentor = Segmentation()
print('Done initializing models for value extractor...')


def run_value_extractor_full(term_list, text, minimum_value, maximum_value, is_case_sensitive_text=False, denom_only=False):
    # convert terms to lowercase unless doing a case-sensitive match
    if not is_case_sensitive_text:
        term_list = [term.lower() for term in term_list]
        text = text.lower()

    # do range check on numerator values for fractions
    if isinstance(minimum_value, str):
        if -1 != minimum_value.find('/'):
            minimum_value = minimum_value.split('/')[0]

    if isinstance(maximum_value, str):
        if -1 != maximum_value.find('/'):
            maximum_value = maximum_value.split('/')[0]

    minval = float(minimum_value)
    maxval = float(maximum_value)

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
            value_results = extract_value(term, sentence, minval, maxval, denom_only=denom_only)
            if len(value_results) > 0:
                for x in value_results:
                    process_results.append(
                        Measurement(sentence=sentence, text=x.matching_term, start=x.start, end=x.end,
                                    condition=x.cond, X=x.num1, Y=x.num2))

    return process_results


if __name__ == '__main__':
    res = run_value_extractor_full(["temperature", "temp", "T"],
                                   "Temp was 99-101",
                                   96, 106, False)

    [print(str(t.to_json())) for t in res]
