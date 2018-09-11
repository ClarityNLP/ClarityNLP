import datetime
import sys
import traceback
from functools import reduce

import pandas as pd
import util
from pymongo import MongoClient

from data_access import PhenotypeModel, PipelineConfig, PhenotypeEntity, PhenotypeOperations, mongo_eval, results
from ohdsi import getCohort


DEBUG_LIMIT = 1000
COL_LIST = ["_id", "report_date", 'report_id', 'subject', 'sentence']

pipeline_keys = PipelineConfig('test', 'test', 'test').__dict__.keys()
numeric_comp_operators = ['==', '=', '>', '<', '<=', '>=']


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


def get_document_set_attributes(model):
    tags = dict()
    types = dict()
    custom_query = dict()
    filter_query = dict()
    # Clarity.createDocumentSet({
    #     report_tags: [optional]
    #     report_types: [optional],
    #     "filter_query": "
    # query: "query"
    if model.document_sets:
        for d in model.document_sets:
            print(d)
            if d['library'] == "Clarity" or d["library"] == "ClarityNLP":
                args = d['arguments']
                named_args = d['named_arguments']
                funct = d['funct']
                doc_set_name = d['name']
                if funct == "createReportTagList":
                    if len(args) == 1 and type(args[0]) == list:
                        tags[doc_set_name] = args[0]
                    else:
                        tags[doc_set_name] = args
                elif funct == "createDocumentSet":
                    if named_args:
                        if "report_tags" in named_args:
                            arg_report_tags = named_args["report_tags"]
                            if len(arg_report_tags) == 1 and type(arg_report_tags[0]) == list:
                                tags[doc_set_name] = arg_report_tags[0]
                            else:
                                tags[doc_set_name] = arg_report_tags
                        if "report_types" in named_args:
                            types[doc_set_name] = named_args["report_types"]
                        if "filter_query" in named_args:
                            filter_query[doc_set_name] = named_args["filter_query"]
                        if "query" in named_args:
                            custom_query[doc_set_name] = named_args["query"]
                elif funct == "createReportTypeList":
                    if len(args) == 1 and type(args[0]) == list:
                        types[doc_set_name] = args[0]
                    else:
                        types[doc_set_name] = args

    return tags, types, custom_query, filter_query


def get_item_list_by_key(dictionary, keys: list):
    items = list()
    for k in keys:
        if k in dictionary:
            items.extend(dictionary[k])
    return items


def get_item_by_key(dictionary, keys: list):
    # there can really only be one of these, so it will just return the first match
    for k in keys:
        if k in dictionary:
            return dictionary[k]
    return ''


def map_arguments(pipeline: PipelineConfig, e):
    for k in e.keys():
        if not (
                k == 'owner' or k == 'limit' or k == 'owner' or k == "name" or k == "config_type" or k == "terms" or
                k == "cohort"):
            if k in pipeline_keys:
                try:
                    pipeline[k] = e[k]
                except Exception as ex:
                    traceback.print_exc(file=sys.stdout)
                    print(ex)
            else:
                try:
                    pipeline.custom_arguments[k] = e[k]
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


def data_entities_to_pipelines(e: PhenotypeEntity, report_tags, all_terms, owner, debug, cohorts, phenotype_limit=0,
                               report_types=dict(), custom_query=dict(), filter_query=dict()):
    if e['named_arguments'] is None:
        e['named_arguments'] = dict()
    if 'value_sets' not in e['named_arguments']:
        e['named_arguments']['value_sets'] = []
    if 'termsets' not in e['named_arguments']:
        e['named_arguments']['termsets'] = []

    if e['library'] == "Clarity" or e['library'] == 'ClarityNLP':
        # config_type, name, description, terms

        if 'documentsets' in e['named_arguments']:
            doc_sets = e['named_arguments']['documentsets']
        elif 'documentset' in e['named_arguments']:
            doc_sets = e['named_arguments']['documentset']
        else:
            doc_sets = list()

        if phenotype_limit > 0:
            limit = phenotype_limit
        elif debug:
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

        tags = get_item_list_by_key(report_tags, doc_sets)
        types = get_item_list_by_key(report_types, doc_sets)
        query = get_item_by_key(custom_query, doc_sets)
        fq = get_item_by_key(filter_query, doc_sets)

        pipeline = PipelineConfig(e['funct'], e['name'],
                                  get_terms_by_keys(all_terms, terms,
                                                    e['named_arguments']['value_sets']
                                                    ),
                                  owner=owner,
                                  limit=limit,
                                  cohort=cohort,
                                  report_tags=tags,
                                  report_types=types,
                                  custom_query=query,
                                  filter_query=fq,
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
        report_tags, report_types, custom_query, filter_query = get_document_set_attributes(model)
        cohorts = get_cohorts(model)
        for e in model.data_entities:
            pipelines.append(data_entities_to_pipelines(e, report_tags, all_terms, model.owner, model.debug, cohorts,
                                                        model.limit, report_types, custom_query, filter_query))
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
    new_df = df.query("(nlpql_feature == '%s') & (%s %s %f)" % (ent, attr, action, value_comp))
    return new_df


def string_to_datetime(stringdt):
    # "2196-05-06T00:00:00Z",
    return datetime.datetime.strptime(stringdt, "%Y-%m-%dT%H:%M:%SZ")


def long_to_datetime(longdt):
    return datetime.datetime.fromtimestamp(float(longdt / 1000))


def get_ohdsi_cohort(ent: str, attr: str, phenotype: PhenotypeModel):
    if len(phenotype['cohorts']) > 0:
        for c in phenotype['cohorts']:
            if c['name'] == ent and c['library'] == 'OHDSI' and c['funct'] == 'getCohort' and len(c['arguments']) > 0:
                cohort = getCohort(c['arguments'][0])['Patients']
                df = pd.DataFrame.from_records(cohort)
                df['cohortStartDate'] = df['cohortStartDate'].apply(long_to_datetime)
                df['cohortEndDate'] = df['cohortEndDate'].apply(long_to_datetime)
                df['subject'] = df['subjectId'].astype(int)
                return df

    return pd.DataFrame({'nothing': []})


def convert_days_to_years(days):
    days *= 1.0
    years = days / 365.0
    return years


def convert_days_to_months(days):
    days *= 1.0
    months = days / 30.4167
    return months


def nlpql_results_to_dataframe(db, job, lookup_key, entity_features, final):
    query = {"job_id": int(job), lookup_key: {"$in": entity_features}}
    cursor = db.phenotype_results.find(query)
    df = pd.DataFrame(list(cursor))
    if not df.empty:
        df['subject'] = df['subject'].astype(int)
    return df


def process_date_diff(pe: PhenotypeEntity, db, job, phenotype: PhenotypeModel, phenotype_id, phenotype_owner,
                      final=False):
    args = pe['arguments']
    nlpql_name = pe['name']
    if not len(args) == 3:
        raise ValueError("dateDiff only accepts 3 arguments")
    ent1, attr1 = get_data_entity_split(args[0])
    ent2, attr2 = get_data_entity_split(args[1])
    time_unit = args[2]

    df1 = get_ohdsi_cohort(ent1, attr1, phenotype)
    df2 = get_ohdsi_cohort(ent2, attr2, phenotype)
    empty = False
    if df1.empty:
        df1 = nlpql_results_to_dataframe(db, job, 'nlpql_feature', [ent1], final)
        if not df1.empty:
            df1[attr1] = df1[attr1].apply(string_to_datetime)
        else:
            empty = True
    if df2.empty:
        df2 = nlpql_results_to_dataframe(db, job, 'nlpql_feature', [ent2], final)
        if not df2.empty:
            df2[attr2] = df2[attr2].apply(string_to_datetime)
        else:
            empty = True
    if not empty:
        merged = pd.merge(df1, df2, on='subject', how='inner')
        if not merged.empty:
            merged['nlpql_feature'] = nlpql_name
            merged['phenotype_id'] = phenotype_id
            merged['phenotype_owner'] = phenotype_owner
            if attr1 == attr2:
                attr1 += '_x'
                attr2 += '_y'
            merged['timedelta'] = merged[attr1] - merged[attr2]
            # todo work if not y|m|d
            merged['value'] = merged['timedelta'].apply(lambda x: x.days)
            if time_unit == 'y':
                merged['value'] = merged['value'].apply(convert_days_to_years)
            elif time_unit == 'm':
                merged['value'] = merged['value'].apply(convert_days_to_months)

            if '_id' in merged.columns:
                merged['orig_id'] = merged['_id']
                merged = merged.drop(columns=['_id'])

            # delete timedelta
            merged = merged.drop(columns=['timedelta'])

            output = merged.to_dict('records')
            del merged
            db.phenotype_results.insert_many(output)
            del output


def process_nested_data_entity(de, new_de_name, db, job, phenotype: PhenotypeModel, phenotype_id, phenotype_owner):
    if de['library'] == "Clarity" or de['library'] == "ClarityNLP":
        if de['funct'] == "dateDiff":
            de["name"] = new_de_name
            process_date_diff(de, db, job, phenotype, phenotype_id, phenotype_owner)


def process_operations(db, job, phenotype: PhenotypeModel, phenotype_id, phenotype_owner, c: PhenotypeOperations,
                       final=False):
    pandas_process_operations(db, job, phenotype, phenotype_id, phenotype_owner, c, final)
    # mongo_process_operations(db, job, phenotype, phenotype_id, phenotype_owner, c, final=False)


def pandas_process_operations(db, job, phenotype: PhenotypeModel, phenotype_id, phenotype_owner, c: PhenotypeOperations,
                       final=False):
    operation_name = c['name']

    if phenotype.context == 'Document':
        on = 'report_id'
    else:
        on = 'subject'

    lookup_key = "nlpql_feature"
    name = c["name"]

    col_list = COL_LIST
    col_list.append(lookup_key)

    if 'data_entities' in c:
        action = c['action']
        data_entities = c['data_entities']
        entity_features = list()

        i = 0
        nested = False
        flat_data_entities = list()
        for de in data_entities:
            if type(de) == dict:
                # this is a function type
                if "arguments" in de:
                    new_name = name + "_" + "inner" + str(i)
                    entity_features.append(new_name)
                    process_nested_data_entity(de, new_name, db, job, phenotype, phenotype_id, phenotype_owner)
                    new_data_entity = new_name + '.value'
                    flat_data_entities.append(new_data_entity)
                nested = True
            elif not is_value(de):
                e, a = get_data_entity_split(de)
                entity_features.append(e)
                flat_data_entities.append(e)
            else:
                flat_data_entities.append(de)
            i += 1

        if nested:
            data_entities = flat_data_entities

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


def mongo_process_operations(db, job, phenotype: PhenotypeModel, phenotype_id, phenotype_owner, c: PhenotypeOperations,
                       final=False):
    client = MongoClient(util.mongo_host, util.mongo_port)
    mongo_db_obj = client[util.mongo_db]
    mongo_collection_obj = mongo_db_obj['phenotype_results']

    try:
        operation_name = c['name']
        if phenotype.context == 'Document':
            on = 'report_id'
        else:
            on = 'subject'
        expression = c['raw_text']
        mongo_ids = mongo_eval.run(mongo_collection_obj, expression, {
            "job_id": job
        })
        mongo_docs = results.lookup_phenotype_results_by_id(mongo_ids)

        output = list()
        for doc in mongo_docs['results']:
            ret = doc
            ret['job_id'] = job
            ret['phenotype_id'] = phenotype_id
            ret['owner'] = phenotype_owner
            ret['job_date'] = datetime.datetime.now()
            ret['context_type'] = on
            ret['raw_definition_text'] = expression
            ret['nlpql_feature'] = operation_name
            ret['phenotype_final'] = c['final']

            if '_id' in ret.columns:
                ret['orig_id'] = ret['_id']
                ret = ret.drop(columns=['_id'])

            output.append(ret)

        if len(output) > 0:
            db.phenotype_results.insert_many(output)
        else:
            print('No phenotype matches on %s.' % expression)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    finally:
        client.close()



def get_dependencies(po, deps: list):
    for de in po['data_entities']:
        if type(de) == dict:
            get_dependencies(de, deps)
        if "arguments" in de:
            for arg in de["arguments"]:
                e, a = get_data_entity_split(arg)
                deps.append(e)
        if is_value(de):
            continue
        else:
            e, a = get_data_entity_split(de)
            deps.append(e)


def compare_phenotype(x: PhenotypeOperations, y: PhenotypeOperations):
    x_deps = list()
    y_deps = list()
    x_name = x["name"]
    y_name = y["name"]
    get_dependencies(x, x_deps)
    get_dependencies(y, y_deps)

    if x_name in x_deps:
        return -1
    elif y_name in y_deps:
        return 1
    else:
        return 0


def write_phenotype_results(db, job, phenotype, phenotype_id, phenotype_owner):
    pd.options.mode.chained_assignment = None

    if phenotype.operations:
        # TODO implement sort
        # for c in phenotype.operations.sort(key=util.cmp_2_key(lambda a, b: compare_phenotype(a,b))):
        for c in phenotype.operations:
            process_operations(db, job, phenotype, phenotype_id, phenotype_owner, c, final=c["final"])


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
