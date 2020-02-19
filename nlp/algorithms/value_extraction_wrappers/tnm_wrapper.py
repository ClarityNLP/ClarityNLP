from algorithms.segmentation import *
from algorithms.value_extraction.tnm_stage_extractor import run as run_tnm_stager
from itertools import product
from claritynlp_logging import log, ERROR, DEBUG


import regex as re
import json

segmentor = Segmentation()


def run_tnm_from_sentence(sentence, term: str = ''):
    results = list()
    json_string = run_tnm_stager(sentence)
    json_data = json.loads(json_string)
    for j in json_data:
        j['sentence'] = sentence
        results.append(j)
    return results


def run_tnm_stager_full(text, term_list=None):
    if term_list is None:
        term_list = list()
    res = list()

    sentences = segmentor.parse_sentences(text)
    if len(term_list) > 0:
        matchers = [re.compile(r"\b%s\b" % t, re.IGNORECASE) for t in term_list]
        vals = product(sentences, matchers)
        for v in vals:
            sentence = v[0]
            matcher = v[1]
            match = matcher.search(sentence)
            if match:
                res.extend(run_tnm_from_sentence(sentence))

    else:
        for sentence in sentences:
            res.extend(run_tnm_from_sentence(sentence))

    return res


if __name__ == "__main__":
    result = run_tnm_stager_full("pT3pN1M1 colon cancer with resection for cure of "
                                 "both the primary tumor and a liver metastasis; R0 (colon); R0 (liver)."
                                 " The tumor is classified as pT4bpN1bM0 (stage IIIC).")
    log(result)
