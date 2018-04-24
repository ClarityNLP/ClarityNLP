import datetime
from functools import reduce

import pandas as pd

from data_access import PhenotypeModel, PipelineConfig, PhenotypeEntity

DEBUG_LIMIT = 1000

pipeline_keys = PipelineConfig('test', 'test', 'test').__dict__.keys()
numeric_comp_operators = ['==', '='
                                '>',
                          '<',
                          '<=',
                          '>=']


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
                args = d['arguments']
                if len(args) == 1 and type(args[0]) == list:
                    types[d['name']] = args[0]
                else:
                    types[d['name']] = args
    return types


def get_report_tags_by_keys(report_tag_dict, keys: list):
    tags = list()
    for k in keys:
        tags.extend(report_tag_dict[k])
    return tags


def map_arguments(pipeline: PipelineConfig, e):
    for k in e.keys():
        if not (k == 'owner' or k == 'limit' or k == 'owner' or k == "name" or k == "config_type" or k == "terms"):
            if k in pipeline_keys:
                try:
                    pipeline[k] = e[k]
                except Exception as ex:
                    print(ex)


def data_entities_to_pipelines(e: PhenotypeEntity, report_tags, all_terms, owner, debug):
    if e['named_arguments'] is None:
        e['named_arguments'] = dict()
    if 'value_sets' not in e['named_arguments']:
        e['named_arguments']['value_sets'] = []
    if 'termsets' not in e['named_arguments']:
        e['named_arguments']['termsets'] = []

    if e['library'] == "Clarity":
        # config_type, name, description, terms

        if 'documentsets' in e['named_arguments']:
            doc_sets = e['named_arguments']['documentsets']
        elif 'documentset' in e['named_arguments']:
            doc_sets = e['named_arguments']['documentset']
        else:
            doc_sets = list()

        tags = get_report_tags_by_keys(report_tags, doc_sets)
        if debug:
            limit = DEBUG_LIMIT
        else:
            limit = 0
        if 'termset' in e['named_arguments']:
            terms = e['named_arguments']["termset"]
        elif 'termsets' in e['named_arguments']:
            terms = e['named_arguments']["termsets"]
        else:
            terms = list()
        pipeline = PipelineConfig(e['funct'], e['name'],
                                  get_terms_by_keys(all_terms, terms,
                                                    e['named_arguments']['value_sets']
                                                    ),
                                  owner=owner,
                                  limit=limit,
                                  report_tags=tags)
        map_arguments(pipeline, e)
        map_arguments(pipeline, e['named_arguments'])
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


def get_data_entity_split(de):
    spl = de.split('.', 1)
    entity = spl[0]
    if len(spl) > 1:
        attr = spl[1]
    else:
        attr = ''
    return entity, attr


def is_value(test: str):
    if test.isdigit():
        return True

    try:
        float(test)
        return True
    except ValueError:
        return False


def get_numeric_comparison_df(action, df, ent, attr, value_comp):
    value_comp = float(value_comp)
    new_df = df.query("(nlpql_feature == '%s') & (%s %s %d)" % (ent, attr, action, value_comp))
    return new_df


def write_phenotype_results(db, job, phenotype, phenotype_id, phenotype_owner):
    if phenotype.operations:
        cursor = db.pipeline_results.find({"job_id": int(job)})
        df = pd.DataFrame(list(cursor))

        ops = sorted(phenotype.operations, key=lambda o: o['final'])
        # TODO make sure all ops are in the right order

        for c in ops:
            operation_name = c['name']

            if phenotype.context == 'Document':
                on = 'report_id'
            else:
                on = 'subject'
            col_list = ["_id", "nlpql_feature", "report_date", 'report_id', 'subject', 'sentence']

            if 'data_entities' in c:
                action = c['action']
                data_entities = c['data_entities']

                dfs = []
                output = None
                ret = None
                if action == 'AND' or action == 'OR' or action == 'NOT':
                    if action == 'OR':
                        how = "outer"
                    elif action == 'AND':
                        how = "inner"
                    else:
                        how = "left"

                    for de in data_entities:
                        ent, attr = get_data_entity_split(de)
                        new_df = df.loc[df['nlpql_feature'] == ent]
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
                        ret['final'] = c['final']

                        output = ret.to_dict('records')

                if action in numeric_comp_operators:
                    print(action)
                    value_comp = ''
                    ent = ''
                    attr = ''
                    if not len(data_entities) == 2:
                        raise ValueError("Only 2 data entities for comparisons")
                    for de in data_entities:
                        if is_value(de):
                            value_comp = de
                        else:
                            e, a = get_data_entity_split(de)
                            ent = e
                            attr = a

                    ret = get_numeric_comparison_df(action, df, ent, attr, value_comp)

                    ret['job_id'] = job
                    ret['phenotype_id'] = phenotype_id
                    ret['owner'] = phenotype_owner
                    ret['job_date'] = datetime.datetime.now()
                    ret['context_type'] = on
                    ret['raw_definition_text'] = c['raw_text']
                    ret['result_name'] = operation_name
                    ret['final'] = c['final']

                    output = ret.to_dict('records')

                if output and len(output) > 0:
                    db.phenotype_results.insert_many(output)

            else:
                print('nothing to do for ' + operation_name)
