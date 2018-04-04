import datetime
from functools import reduce

import pandas as pd

from data_access import PhenotypeModel, PipelineConfig, PhenotypeEntity

valid_operations = ["AND", "OR", "NOT", "GREATER_THAN", "LESS_THAN", "GREATER_THAN_OR_EQUAL",
                    "LESS_THAN_OR_EQUAL", "SUBTRACT", "ADD", "MULTIPLY", "DIVIDE", "MODULO"]


def get_terms(model: PhenotypeModel):
    terms = dict()
    if model:
        if model.term_sets and len(model.term_sets) > 0:
            for t in model.term_sets:
                terms[t['name']] = t['values']
        # TODO expand concept_sets

    return terms


def get_terms_by_keys(term_dict, term_keys: list, concept_keys: list):
    terms = list()
    for k in term_keys:
        terms.extend(term_dict[k])
    for k in concept_keys:
        terms.extend(term_dict[k])

    return terms


def get_report_tags(model):
    types = dict()
    # TODO
    if model.document_sets:
        for d in model.document_sets:
            if d['library'] == "Clarity" and d['funct'] == "createReportTagList":
                types[d['name']] = d['arguments']
    return types


def get_report_tags_by_keys(report_tag_dict, keys: list):
    tags = list()
    for k in keys:
        tags.extend(report_tag_dict[k])
    return tags


def data_entities_to_pipelines(e: PhenotypeEntity, report_tags, all_terms, owner, debug):
    if e['named_arguments'] is None:
        e['named_arguments'] = dict()
    if 'value_sets' not in e['named_arguments']:
        e['named_arguments']['value_sets'] = []
    if 'termsets' not in e['named_arguments']:
        e['named_arguments']['termsets'] = []

    if e['library'] == "Clarity":
        # config_type, name, description, terms
        tags = get_report_tags_by_keys(report_tags, e['named_arguments']['documentsets'])
        if debug:
            limit = 100
        else:
            limit = 0
        pipeline = PipelineConfig(e['funct'], e['name'],
                                  get_terms_by_keys(all_terms, e['named_arguments']['termsets'],
                                                    e['named_arguments']['value_sets']
                                                    ),
                                  owner=owner,
                                  limit=limit,
                                  report_tags=tags)
        return pipeline
    else:
        raise ValueError("External pipelines not yet supported")


def get_pipelines_from_phenotype(model: PhenotypeModel):
    pipelines = list()
    if model and model.data_entities and len(model.data_entities) > 0:
        all_terms = get_terms(model)
        report_tags = get_report_tags(model)
        for e in model.data_entities:
            pipelines.append(data_entities_to_pipelines(e, report_tags, all_terms, model.owner, model.debug))
    return pipelines


def write_phenotype_results(db, job, phenotype, phenotype_id, phenotype_owner):
    if phenotype.operations:
        cursor = db.pipeline_results.find({"job_id": int(job)})
        df = pd.DataFrame(list(cursor))

        for c in phenotype.operations:
            operation_name = c['name']

            if phenotype.context == 'Document':
                on = 'report_id'
            else:
                on = 'subject'
            col_list = ["_id", "nlpql_feature", "report_date", 'report_id', 'subject', 'sentence']

            if c['final']:
                if 'data_entities' in c:
                    action = c['action']
                    data_entities = c['data_entities']

                    dfs = []
                    if action == 'AND' or action == 'OR' or action == 'NOT':
                        if action == 'OR':
                            how = "outer"
                        elif action == 'AND':
                            how = "inner"
                        else:
                            how = "left"

                        for de in data_entities:
                            new_df = df.loc[df['nlpql_feature'] == de]
                            new_df = new_df[col_list]
                            dfs.append(new_df)

                        if len(dfs) > 0:
                            ret = reduce(lambda x, y: pd.merge(x, y, on=on, how=how), dfs)
                            ret['job_id'] = job
                            ret['phenotype_id'] = phenotype_id
                            ret['owner'] = phenotype_owner
                            ret['job_date'] = datetime.datetime.now()
                            ret['context_type'] = on
                            ret['raw_definition_text'] = c['raw_text']
                            ret['result_name'] = operation_name

                            db.phenotype_results.insert_many(ret.to_dict('records'))

            else:
                print('nothing to do for ' + operation_name)
