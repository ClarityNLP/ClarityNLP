import datetime
import sys
import traceback
from functools import reduce
import pandas as pd

from data_access import PhenotypeModel, PipelineConfig, PhenotypeEntity, PhenotypeOperations

DEBUG_LIMIT = 100
COL_LIST = ["_id", "report_date", 'report_id', 'subject', 'sentence']

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
        if not (
                k == 'owner' or k == 'limit' or k == 'owner' or k == "name" or k == "config_type" or k == "terms" or k == "cohort"):
            if k in pipeline_keys:
                try:
                    pipeline[k] = e[k]
                except Exception as ex:
                    traceback.print_exc(file=sys.stdout)
                    print(ex)


def get_cohort_items(cohort_name, cohort_source):
    cohorts = list()
    if type(cohort_name) == str:
        if cohort_name in cohort_source:
            cohorts.append(cohort_source[cohort_name])
    elif type(cohort_name) == list:
        for name in cohort_name:
            if name in cohort_source:
                cohorts.extend(cohort_source[name])

    return cohorts


def data_entities_to_pipelines(e: PhenotypeEntity, report_tags, all_terms, owner, debug, cohorts):
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

        if 'cohort' in e['named_arguments']:
            cohort = get_cohort_items(e['named_arguments']['cohort'], cohorts)
        elif 'cohorts' in e['named_arguments']:
            cohort = get_cohort_items(e['named_arguments']['cohorts'], cohorts)
        else:
            cohort = list()

        pipeline = PipelineConfig(e['funct'], e['name'],
                                  get_terms_by_keys(all_terms, terms,
                                                    e['named_arguments']['value_sets']
                                                    ),
                                  owner=owner,
                                  limit=limit,
                                  cohort=cohort,
                                  report_tags=tags,
                                  is_phenotype=True)
        map_arguments(pipeline, e)
        map_arguments(pipeline, e['named_arguments'])
        return pipeline
    else:
        raise ValueError("External pipelines not yet supported")


def get_cohorts(model: PhenotypeModel):
    cohorts = dict()
    if model.cohorts:
        for c in model.cohorts:
            try:
                c_name = c['name']
                if c['library'] == 'OHDSI' and c['funct'] == 'getCohort' and len(c['arguments']) > 0:
                    cohorts[c_name] = c['arguments'][0]

            except Exception as ex:
                print(ex)
                traceback.print_exc(file=sys.stderr)
    return cohorts


def get_pipelines_from_phenotype(model: PhenotypeModel):
    pipelines = list()
    if model and model.data_entities and len(model.data_entities) > 0:
        all_terms = get_terms(model)
        report_tags = get_report_tags(model)
        cohorts = get_cohorts(model)
        for e in model.data_entities:
            pipelines.append(data_entities_to_pipelines(e, report_tags, all_terms, model.owner, model.debug, cohorts))
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


def process_operations(db, job, phenotype: PhenotypeModel, phenotype_id, phenotype_owner, c: PhenotypeOperations,
                       final=False):
    operation_name = c['name']

    if phenotype.context == 'Document':
        on = 'report_id'
    else:
        on = 'subject'

    lookup_key = "nlpql_feature"

    col_list = COL_LIST
    col_list.append(lookup_key)

    if 'data_entities' in c:
        action = c['action']
        data_entities = c['data_entities']
        entity_features = list()

        for de in data_entities:
            if not is_value(de):
                e, a = get_data_entity_split(de)
                entity_features.append(e)

        query = {"job_id": int(job), lookup_key: {"$in": entity_features}}
        cursor = db.phenotype_results.find(query)
        df = pd.DataFrame(list(cursor))

        if len(df) == 0:
            print('Empty dataframe!')
            return

        dfs = []
        output = None
        if action == 'AND':
            how = 'inner'

            for de in data_entities:
                ent, attr = get_data_entity_split(de)
                new_df = df[df[lookup_key] == ent]
                new_df = new_df[col_list]
                dfs.append(new_df.copy())
                del new_df

            if len(dfs) > 0:
                ret = reduce(lambda x, y: pd.merge(x, y, on=on, how=how), dfs)
                ret['job_id'] = job
                ret['phenotype_id'] = phenotype_id
                ret['owner'] = phenotype_owner
                ret['job_date'] = datetime.datetime.now()
                ret['context_type'] = on
                ret['raw_definition_text'] = c['raw_text']
                ret['nlpql_feature'] = operation_name
                ret['phenotype_final'] = c['final']

                for d in dfs:
                    del d

                if '_id' in ret.columns:
                    ret['orig_id'] = ret['_id']
                    ret = ret.drop(columns=['_id'])

                output = ret.to_dict('records')
                del ret
        elif action == 'OR':
            q = '| '.join([("(%s == '%s')" % (lookup_key, x)) for x in data_entities])
            ret = df.query(q)
            ret['job_id'] = job
            ret['phenotype_id'] = phenotype_id
            ret['owner'] = phenotype_owner
            ret['job_date'] = datetime.datetime.now()
            ret['context_type'] = on
            ret['raw_definition_text'] = c['raw_text']
            ret['nlpql_feature'] = operation_name
            ret['phenotype_final'] = c['final']
            if '_id' in ret.columns:
                ret['orig_id'] = ret['_id']
                ret = ret.drop(columns=['_id'])

            output = ret.to_dict('records')
            del ret
        elif action in numeric_comp_operators:
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
            ret['nlpql_feature'] = operation_name
            ret['phenotype_final'] = c['final']
            if '_id' in ret.columns:
                ret['orig_id'] = ret['_id']
                ret = ret.drop(columns=['_id'])

            output = ret.to_dict('records')
            del ret

        if output and len(output) > 0:
            db.phenotype_results.insert_many(output)
            del output


def write_phenotype_results(db, job, phenotype, phenotype_id, phenotype_owner):
    pd.options.mode.chained_assignment = None
    if phenotype.operations:

        final_ops = list()
        regular_ops = list()

        for c in phenotype.operations:
            # TODO make sure all ops are in the right order
            if c['final']:
                final_ops.append(c)
            else:
                regular_ops.append(c)

        for c in regular_ops:
            process_operations(db, job, phenotype, phenotype_id, phenotype_owner, c)
        for c in final_ops:
            process_operations(db, job, phenotype, phenotype_id, phenotype_owner, c, final=True)


def validate_phenotype(p_cfg: PhenotypeModel):
    # TODO a lot more checks need to be done
    error = None

    try:
        if not error:
            if not p_cfg:
                error = "Empty phenotype object"

        if not error and len(p_cfg.data_entities) == 0:
            error = "Must have at least one data entity (define)"
        if not error and len(p_cfg.operations) > 0 and len(p_cfg.data_entities) == 0:
            error = "Operations (define) require at least one data entity (define)"
    except Exception as ex:
        print(ex)
        error = ''.join(traceback.format_stack())

    if not error:
        return {"success": True}
    else:
        return {"success": False, "error": error}
