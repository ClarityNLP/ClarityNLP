import os
import nlpql
import pandas as pd
import numpy as np
from collections import OrderedDict

SCRIPT_DIR = os.path.dirname(__file__)


def reorder_query_default(parsed_query):
    path = os.path.join(SCRIPT_DIR, "inclusion_criteria_ranked.csv")
    return reorder_query(parsed_query, pd.read_csv(path, header=0))


def reorder_query(parsed_query, downselection_df):

    new_query = parsed_query

    termset_ranks = OrderedDict()
    data_entities_ranks = OrderedDict()
    operation_ranks = OrderedDict()

    counter_a = 0

    # STEP 1: Order the term-sets by downselection potential (will only rank based on pre-identified primitives)
    for set in parsed_query['term_sets']:

        termset_ranks[counter_a] = {"set": set, "rank": np.inf, "name": set['name']}

        for value in set['values']:
            if value.lower() in list(downselection_df['category']):
                rank = list(downselection_df['category']).index(value.lower())
                termset_ranks[counter_a]["rank"] = rank
                break # keep this?

        counter_a += 1

    # Order by down-selection potential, so that termset with greatest down-selection potential gets run first
    termsets_ordered_by_downselect = OrderedDict(sorted(termset_ranks.items(), key=lambda v: v[1]['rank']))


    # If len == 1, there's only one termset, so downselection order won't matter
    if len(termsets_ordered_by_downselect.keys()) > 1:
        new_key = 0

        for _,v in termsets_ordered_by_downselect.items():
            new_query['term_sets'][new_key] = v['set']
            new_key += 1

    # Step 2: Order the data entities based on downselection potential of the termsets they include, as determined above
    counter_b = 0

    for entity in parsed_query['data_entities']:
        data_entities_ranks[counter_b] = {"entity": entity, "rank": np.inf, "termset_name": entity['named_arguments']['termset'],
                                          "name":entity["name"]}

        for k,v in termsets_ordered_by_downselect.items():
            if entity['named_arguments']['termset'][0] == v['name']:
                data_entities_ranks[counter_b]['rank'] = v['rank']

        counter_b += 1

    entities_ordered_by_downselect = OrderedDict(sorted(data_entities_ranks.items(), key=lambda v: v[1]['rank']))

    # If len == 1, there's only one termset, so downselection order won't matter
    if len(entities_ordered_by_downselect.keys()) > 1:

        new_key = 0

        for _, v in entities_ordered_by_downselect.items():
            new_query['data_entities'][new_key] = v['entity']
            new_key +=1

    # Step 3: Order the operations based on downselection potential of data entities, as determined above
    counter_c = 0

    if len(parsed_query['operations']) > 0:

        operations = parsed_query['operations'][0]

        for entity in operations['data_entities']:
            operation_ranks[counter_c] = {"op": entity, "rank": np.inf}

            for k, v in entities_ordered_by_downselect.items():
                if entity == v['name']:
                     operation_ranks[counter_c]['rank'] = v['rank']
            counter_c += 1

        ops_ordered_by_downselect = OrderedDict(sorted(operation_ranks.items(), key=lambda v: v[1]['rank']))

        if len(ops_ordered_by_downselect.keys()) > 1:
            new_key = 0

            for _, v in ops_ordered_by_downselect.items():
                new_query['operations'][0]['data_entities'][new_key] = v['op']
                new_key += 1

        # TODO: this is a hack that we should fix for generalized implementation over nested boolean statements (need to parse AST and selectively replace)
        action = parsed_query['operations'][0]['action']
        raw_text = '{} {} {}'.format(new_query['operations'][0]['data_entities'][0], action, new_query['operations'][0]['data_entities'][1])

        new_query['operations'][0]['raw_text'] = raw_text

    return new_query


if __name__ == '__main__':

    counter = 0

    primitives_ranked_by_downselection = pd.read_csv("./inclusion_criteria_ranked_by_downselection.csv", header=0)

    for query in os.listdir("./gen_nlpql"):

        if "feature" in query:
            continue
        else:

            query_number = query.split("_")[1].split(".")[0]

            with open('./gen_nlpql/{}'.format(query)) as f:
                nlpql_txt = f.read()
                results = nlpql.run_nlpql_parser(nlpql_txt)

                if results['has_errors'] or results['has_warnings']:
                    continue

                else:

                    with open('./parsed_nlpql/parsed_query_{}.json'.format(query_number), "w+") as out_file:
                        out_file.write(results['phenotype'].to_json())

                    reordered_nlpql = reorder_query(results['phenotype'], primitives_ranked_by_downselection)

                    with open('./reordered_parsed_nlpql/reordered_parsed_query_{}.json'.format(query_number), "w+") as out_file2:
                        out_file2.write(reordered_nlpql.to_json())

