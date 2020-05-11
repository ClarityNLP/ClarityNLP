import regex as re
import json
from data_access import Measurement
from algorithms.segmentation import *
from algorithms.value_extraction import run_value_extractor
from claritynlp_logging import log, ERROR, DEBUG

log('Initializing models for value extractor...')
segmentor = Segmentation()
log('Done initializing models for value extractor...')


def run_value_extractor_full(term_list,
                             text,
                             minimum_value,
                             maximum_value,
                             enumlist=None,
                             is_case_sensitive_text=False,
                             denom_only=False,
                             values_before_terms=False):

    if enumlist is None:
        enumlist = list()
    sentence_list = segmentor.parse_sentences(text)
    process_results = []

    for sentence in sentence_list:

        json_string = run_value_extractor(
            term_list,
            sentence,
            str_minval = minimum_value,
            str_maxval = maximum_value,
            str_enumlist = enumlist,
            is_case_sensitive = is_case_sensitive_text,
            is_denom_only = denom_only,
            values_before_terms = values_before_terms)

        if json_string is not None and len(json_string) > 0:

            # parse the JSON result
            json_data = json.loads(json_string)

            # the individual value extractions are in the 'measurementList'
            if 'measurementList' in json_data:
                measurements = json_data['measurementList']
                for m in measurements:
                    process_results.append(
                        Measurement(
                            sentence       = sentence,
                            text           = m['text'],
                            start          = m['start'],
                            end            = m['end'],
                            condition      = m['condition'],
                            X              = m['x'],
                            Y              = m['y'],
                            matching_terms = m['matchingTerm'],
                            min_value      = m['minValue'],
                            max_value      = m['maxValue']
                        )
                    )

    return process_results


if __name__ == '__main__':
    res = run_value_extractor_full(["temperature", "temp", "T", "BP", "HR", "Sp02"],
                                   'Prior to transfer, his vitals were BP 119/53 and BP 105/43 sleeping, '
                                   'HR 103, RR 15, and SpO2 97% on NRB.',
                                   10, 500, is_case_sensitive_text=False)

    [log(str(t.to_json())) for t in res]
