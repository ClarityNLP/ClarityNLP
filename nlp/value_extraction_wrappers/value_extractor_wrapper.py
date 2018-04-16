from nlp.segmentation import *

from data_access import Measurement
from nlp.value_extraction.value_extractor import extract_value, clean_sentence

print('Initializing models for value extractor...')
segmentor = Segmentation()
print('Done initializing models for value extractor...')


def run_value_extractor_full(term_list, text, minimum_value, maximum_value, is_case_sensitive_text=False):
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
    for s in sentence_list:
        s = clean_sentence(s, is_case_sensitive_text)

        for term in term_list:
            value_results = extract_value(term, s, minval, maxval)
            if len(value_results) > 0:
                for x in value_results:
                    process_results.append(Measurement(sentence=s, text=s[x.start:x.end], start=x.start, end=x.end,
                                                       condition=x.cond, X=x.num1, Y=x.num2))

    return process_results


if __name__ == '__main__':
    res = run_value_extractor_full(["bp", "blood pressure"],
                                "BP was between 100/60 and 120/80 then BP range: 105/75 - 120/70. "
                                "Her BP on 3/27 measured 110/70 and her BP on 4/01 measured 115/80.",
                                20, 250, False)

    [print(str(t.to_json())) for t in res]
