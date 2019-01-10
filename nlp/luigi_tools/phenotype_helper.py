import datetime
import sys
import copy
import traceback
from functools import reduce
import collections

import pandas as pd
import util
from pymongo import MongoClient

from data_access import PhenotypeModel, PipelineConfig, PhenotypeEntity, PhenotypeOperations, results
from data_access import expr_eval
from ohdsi import getCohort

#import json
#from bson import json_util, ObjectId

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
    if isinstance(term_keys, collections.Iterable):
        for k in term_keys:
            if k in term_dict:
                terms.extend(term_dict[k])
    if isinstance(concept_keys, collections.Iterable):
        for k in concept_keys:
            if k in term_dict:
                terms.extend(term_dict[k])

    return terms


def normalize_query_quotes(q: str):
    return q.replace("'", '"')


def get_document_set_attributes(model):
    tags = dict()
    types = dict()
    custom_query = dict()
    filter_query = dict()
    source = dict()
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
                            fq = normalize_query_quotes(named_args["filter_query"])
                            filter_query[doc_set_name] = fq
                        if "query" in named_args:
                            query = normalize_query_quotes(named_args["query"])
                            custom_query[doc_set_name] = query
                        if "source" in named_args:
                            if type(named_args["source"]) == str:
                                source[doc_set_name] = named_args["source"].split(",")
                            else:
                                source[doc_set_name] = named_args["source"]
                        elif "sources" in named_args:
                            if type(named_args["sources"]) == str:
                                source[doc_set_name] = named_args["sources"].split(",")
                            else:
                                source[doc_set_name] = named_args["sources"]
                elif funct == "createReportTypeList":
                    if len(args) == 1 and type(args[0]) == list:
                        types[doc_set_name] = args[0]
                    else:
                        types[doc_set_name] = args

    return tags, types, custom_query, filter_query, source


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


def map_arguments(pipeline: PipelineConfig, e, all_terms):
    for k in e.keys():
        if not (
                k == 'owner' or k == 'limit' or k == 'owner' or k == "name" or k == "config_type" or k == "terms" or
                k == "cohort" or k == "job_results"):
            if k in pipeline_keys:
                try:
                    pipeline[k] = e[k]
                except Exception as ex:
                    traceback.print_exc(file=sys.stdout)
                    print(ex)
            else:
                try:
                    term_mappings = get_terms_by_keys(all_terms, e[k], list())
                    if len(term_mappings) > 0:
                        val = term_mappings
                    else:
                        val = e[k]
                    pipeline.custom_arguments[k] = val
                except Exception as ex:
                    traceback.print_exc(file=sys.stdout)
                    print(ex)


def get_cohort_items(cohort_name, cohort_source, job_results):
    cohorts = list()
    job_results_filter = dict()

    if type(cohort_name) == str:
        if cohort_name in cohort_source:
            cohorts.append(cohort_source[cohort_name])
        if cohort_name in job_results:
            job_results_filter[cohort_name] = job_results[cohort_name]

    elif type(cohort_name) == list:
        for name in cohort_name:
            if name in cohort_source:
                cohorts.extend(cohort_source[name])
            if name in job_results:
                job_results_filter[name] = job_results[name]

    return cohorts, job_results_filter


def data_entities_to_pipelines(e: PhenotypeEntity, report_tags, all_terms, owner, debug,
                               cohorts, phenotype_limit=0, report_types: dict=None,
                               custom_query: dict=None, filter_query: dict=None, source: dict=None,
                               job_results: dict=None):
    if report_types is None:
        report_types = dict()
    if custom_query is None:
        custom_query = dict()
    if filter_query is None:
        filter_query = dict()
    if source is None:
        source = dict()
    if job_results is None:
        job_results = dict()

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
            cohort, job_results_filter = get_cohort_items(e['named_arguments']['cohort'], cohorts, job_results)
        elif 'cohorts' in e['named_arguments']:
            cohort, job_results_filter = get_cohort_items(e['named_arguments']['cohorts'], cohorts, job_results)
        else:
            cohort, job_results_filter = list(), dict()

        tags = get_item_list_by_key(report_tags, doc_sets)
        types = get_item_list_by_key(report_types, doc_sets)
        query = get_item_by_key(custom_query, doc_sets)
        fq = get_item_by_key(filter_query, doc_sets)
        sources = get_item_list_by_key(source, doc_sets)

        pipeline = PipelineConfig(e['funct'], e['name'],
                                  get_terms_by_keys(all_terms, terms,
                                                    e['named_arguments']['value_sets']
                                                    ),
                                  owner=owner,
                                  limit=limit,
                                  cohort=cohort,
                                  job_results=job_results_filter,
                                  report_tags=tags,
                                  report_types=types,
                                  sources=sources,
                                  custom_query=query,
                                  filter_query=fq,
                                  is_phenotype=True)
        map_arguments(pipeline, e, all_terms)
        map_arguments(pipeline, e['named_arguments'], all_terms)
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


def get_job_results(model: PhenotypeModel):
    job_results = dict()
    if model.cohorts:
        for c in model.cohorts:
            try:
                c_name = c['name']
                if (c['library'] == 'Clarity' or c['library'] == 'ClarityNLP') and c['funct'] == 'getJobResults' and \
                        'named_arguments' in c:
                    job_results[c_name] = c['named_arguments']

            except Exception as ex:
                print(ex)
                traceback.print_exc(file=sys.stderr)
    return job_results


def get_pipelines_from_phenotype(model: PhenotypeModel):
    pipelines = list()
    if model and model.data_entities and len(model.data_entities) > 0:
        all_terms = get_terms(model)
        report_tags, report_types, custom_query, filter_query, source = get_document_set_attributes(model)
        cohorts = get_cohorts(model)
        job_results = get_job_results(model)
        for e in model.data_entities:
            pipelines.append(data_entities_to_pipelines(e, report_tags, all_terms, model.owner, model.debug, cohorts,
                                                        model.limit, report_types, custom_query, filter_query, source,
                                                        job_results))
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
    try:
        value_comp = float(value_comp)
        new_df = df.query("(nlpql_feature == '%s') & (%s %s %f)" % (ent, attr, action, value_comp))
    except Exception as e:
        new_df = df.query("(nlpql_feature == '%s') & (%s %s %s)" % (ent, attr, action, str(value_comp)))

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


def get_all_names(phenotype: PhenotypeModel):

    names = set()

    if 'data_entities' in phenotype:
        data_entities = phenotype['data_entities']
        for de in data_entities:
            if 'name' in de:
                names.add(de['name'])
                
    if 'operations' in phenotype:
        operations = phenotype['operations']
        for op in operations:
            if 'name' in op:
                names.add(op['name'])
            
    return list(names)
    
            
def process_operations(db, job, phenotype: PhenotypeModel, phenotype_id, phenotype_owner, c: PhenotypeOperations,
                       final=False):

    try:
        evaluator = util.expression_evaluator
    except:
        evaluator = 'pandas'        

    # the NLPQL expression to be evaluated
    expression = c['raw_text']

    # the NLPQL feature name to assign to the result
    nlpql_feature = c['name']

    mongo_failed = False
    if 'mongo' == evaluator:
        print('Using mongo evaluator for expression "{0}"'.format(expression))

        # get the names of the phenotype's data_entities and operations
        names = get_all_names(phenotype)

        # Parse the expression and return a fully-parenthesized version
        # that uses mnemonics for the operators. The evaluator will attempt
        # to resolve any unknown tokens into concatenated names and logic
        # operators. If it finds a token that it cannot resolve into known
        # names it returns an empty list. An empty list is also returned
        # if the expression cannot be evaluated for some other reason.
        parse_result = expr_eval.parse_expression(expression, names)
        if 0 == len(parse_result):
            print('\n*** Expression cannot be evaluated. ***\n')
            mongo_failed = True
        else:
            # generate a list of expr_eval.ExpressionObject items
            expr_list = expr_eval.generate_expressions(nlpql_feature, parse_result)
            if 0 == len(expr_list):
                print('\t\n*** No subexpressions found! ***\n')
                mongo_failed = True
            else:
                mongo_process_operations(expr_list, db, job, phenotype,
                                         phenotype_id, phenotype_owner,c, final)
                
    if 'pandas' == evaluator or mongo_failed:
        print('Using pandas evaluator for expression "{0}"'.format(expression))
        pandas_process_operations(db, job, phenotype, phenotype_id, phenotype_owner, c, final)


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
        elif action == 'NOT':
            how = 'left'

            for de in data_entities:
                ent, attr = get_data_entity_split(de)
                new_df = df[df[lookup_key] == ent]
                new_df = new_df[col_list]
                dfs.append(new_df.copy())
                del new_df

            if len(dfs) > 0:
                ret = reduce(lambda x, y: pd.merge(x, y, on=on, how=how), dfs)
                ret = ret.query(on + "_x not in " + on + "_y")
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


def flatten(l, ltypes=(list, tuple)):
    """
    Non-recursive list and tuple flattener from
    http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html,
    based on code from Mike Fletcher's BasicTypes library.
    """
    
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
        
    return ltype(l)


def flatten_nested_lists(obj):
    """
    Remove nested lists in the given dict and return the flattened 
    equivalent. Does some special handling for empty lists or lists containing
    all identical entries, mainly to simplify the results when viewed in Excel.
    """

    for k,v in obj.items():
        if type(v) == list:
            if 1 == len(v) and '' == v[0]:
                obj[k] = None
            else:
                flattened_list = flatten(v)

                all_none = True
                for item in flattened_list:
                    if item is not None:
                        all_none = False
                        break

                if all_none:
                    obj[k] = None
                else:
                    obj[k] = flattened_list


def remove_arrays(obj):
    """
    Remove arrays in the result dict by creating numbered fields for
    the array elements.
    """
    to_insert = []
    to_remove = []
    
    for k,v in obj.items():
        if type(v) != list:
            continue

        elt_count = len(v)
        if 1 == elt_count:
            obj[k] = v[0]
        else:
            for i in range(elt_count):
                # use 1-based indexing
                field_name = '{0}_{1}'.format(k, i+1)
                to_insert.append( (field_name, copy.deepcopy(v), i) )
            to_remove.append(k)

    for k in to_remove:
        obj.pop(k, None)
    for k,v,i in to_insert:
        obj[k] = v[i]


def mongo_process_operations(expr_obj_list,
                             db,
                             job_id,
                             phenotype: PhenotypeModel,
                             phenotype_id,
                             phenotype_owner,
                             c: PhenotypeOperations,
                             final=False):
    """
    Use MongoDB aggregation to evaluate NLPQL expressions.
    """

    print('mongo_process_operations expr_object_list: ')
    for expr_obj in expr_obj_list:
        print(expr_obj)

    # setup access to the Mongo collection
    client = MongoClient(util.mongo_host, util.mongo_port)
    mongo_db_obj = client[util.mongo_db]
    mongo_collection_obj = mongo_db_obj['phenotype_results']

    is_final       = c['final']
    expression     = c['raw_text']
    operation_name = c['name']
    
    context_var = phenotype.context.lower()
    if 'document' == context_var:
        # document IDs are in the report_id field
        context_field = 'report_id'
    else:
        # patient IDs are in the subject field
        context_field = 'subject'

    # these fields are not copied from source doc to result doc
    NO_COPY_FIELDS = [
        '_id', 'job_id', 'phenotype_id', 'owner',
        'job_date', 'context_type', 'raw_definition_text',
        'nlpql_feature', 'phenotype_final', 'history'
    ]

    for expr_obj in expr_obj_list:

        assert expr_eval.EXPR_TYPE_MATH == expr_obj.expr_type or \
            expr_eval.EXPR_TYPE_LOGIC == expr_obj.expr_type

        if expr_eval.EXPR_TYPE_MATH == expr_obj.expr_type:

            # evaluate a pure math expression
            result = expr_eval.eval_math_expr(job_id,
                                              expr_obj.nlpql_feature,
                                              expr_obj.expr_text,
                                              mongo_collection_obj)
        else:
            # evaluate a pure logic expression
            result = expr_eval.eval_logic_expr(job_id,
                                               context_field,
                                               expr_obj.nlpql_feature,
                                               expr_obj.expr_text,
                                               mongo_collection_obj)
            
        # query MongoDB to get result docs
        cursor = mongo_collection_obj.find({'_id': {'$in': result.doc_ids}})

        # generate output docs
        output_docs = []

        if expr_eval.EXPR_TYPE_MATH == expr_obj.expr_type:

            # no document groups for math results
            for doc in cursor:

                # output doc
                ret = {}
                
                # add doc fields to the output doc as lists
                field_map = {}
                fields = doc.keys()
                fields_to_copy = [f for f in fields if f not in NO_COPY_FIELDS]
                for f in fields_to_copy:
                    if f not in field_map:
                        field_map[f] = [doc[f]]
                    else:
                        field_map[f].append(doc[f])

                for k,v in field_map.items():
                    ret[k] = copy.deepcopy(v)

                # set the context field explicitly
                ret[context_field] = doc[context_field]

                ret['job_id'] = job_id
                ret['phenotype_id'] = phenotype_id
                ret['owner'] = phenotype_owner
                ret['job_date'] = datetime.datetime.now()
                ret['context_type'] = context_field
                ret['raw_definition_text'] = expression
                ret['nlpql_feature'] = operation_name
                ret['phenotype_final'] = c['final']

                # add source _id and nlpql_feature
                if is_final:
                    ret['_ids_1'] = copy.deepcopy(doc['_id'])
                    ret['nlpql_features_1'] = copy.deepcopy(doc['nlpql_feature'])
                else:
                    # use same field names as for logic ops
                    ret['_ids'] = copy.deepcopy(doc['_id'])
                    ret['nlpql_features'] = copy.deepcopy(doc['nlpql_feature'])

                flatten_nested_lists(ret)

                if is_final:
                    remove_arrays(ret)

                output_docs.append(ret)

            if len(output_docs) > 0:
                db.phenotype_results.insert_many(output_docs)
            else:
                print('mongo_process_operations (math): No phenotype matches on %s.' % expression)

        else:

            doc_map, oid_list_of_lists = expr_eval.expand_logical_result(result,
                                                                         mongo_collection_obj)

            # an 'ntuple' is a list of _id values
            for ntuples in oid_list_of_lists:
                for ntuple in ntuples:
                    assert isinstance(ntuple, list)
                    if 0 == len(ntuple):
                        continue

                    # each ntuple supplies the data for a result doc
                    ret = {}
                    history = {
                        'source_ids'  : [],
                        'source_features' : []
                    }

                    # get the shared context field value for this ntuple
                    oid = ntuple[0]
                    doc = doc_map[oid]
                    context_field_value = doc[context_field]
                    
                    # accumulate the source _id and nlpql_feature fields
                    for oid in ntuple:
                        # get the doc associated with this _id
                        doc = doc_map[oid]
                        # print('\t\tdoc id: {0}, nlpql_feature: {1}, ' \
                        #       'report_id: {2}, subject: {3}, start/end: [{4}, {5})'.
                        #       format(doc['_id'], doc['nlpql_feature'],
                        #              doc['report_id'], doc['subject'], doc['start'],
                        #              doc['end']))
                        history['source_ids'].append(str(oid))
                        history['source_features'].append(doc['nlpql_feature'])
                        assert context_field_value == doc[context_field]
                        
                    # add ntuple doc fields to the output doc as lists
                    field_map = {}
                    for oid in ntuple:
                        doc = doc_map[oid]
                        fields = doc.keys()
                        fields_to_copy = [f for f in fields if f not in NO_COPY_FIELDS]
                        for f in fields_to_copy:
                            if f not in field_map:
                                field_map[f] = [doc[f]]
                            else:
                                field_map[f].append(doc[f])

                    for k,v in field_map.items():
                        ret[k] = copy.deepcopy(v)

                    # set the context field value; same value for all ntuple entries
                    ret[context_field] = context_field_value

                    # update fields common to AND/OR
                    ret['job_id'] = job_id
                    ret['phenotype_id'] = phenotype_id
                    ret['owner'] = phenotype_owner
                    ret['job_date'] = datetime.datetime.now()
                    ret['context_type'] = context_field
                    ret['raw_definition_text'] = expression
                    ret['nlpql_feature'] = operation_name
                    ret['phenotype_final'] = c['final']

                    # add source _ids and nlpql_features (1-based indexing)
                    source_count = len(history['source_ids'])
                    if is_final:
                        for i in range(len(history['source_ids'])):
                            field_name = '_ids_{0}'.format(i+1)
                            ret[field_name] = history['source_ids'][i]
                        for i in range(len(history['source_features'])):
                            field_name = 'nlpql_features_{0}'.format(i+1)
                            ret[field_name] = history['source_features'][i]

                        # remove intermediate array fields
                        ret.pop('_ids', None)
                        ret.pop('nlpql_features', None)
                    else:
                        # add intermediate array fields
                        ret['_ids'] = copy.deepcopy(history['source_ids'])
                        ret['nlpql_features'] = copy.deepcopy(history['source_features'])

                    flatten_nested_lists(ret)

                    if is_final:
                        remove_arrays(ret)

                    output_docs.append(ret)

            if len(output_docs) > 0:
                db.phenotype_results.insert_many(output_docs)
            else:
                print('mongo_process_operations (logic): no phenotype matches on {0}.'.
                      format(expression))
                    
        # print('********** RESULT FROM PHENOTYPE_HELPER: **********')
        # print(result)
        # print('***************************************************')
        
    client.close()
            
    
    # # build and run a Mongo aggregation pipeline to evaluate the expression
    # eval_result = mongo_eval.run(mongo_collection_obj,
    #                              infix_tokens,
    #                              on,
    #                              match_filters)
    # if mongo_eval.MONGO_OP_ERROR == eval_result.operation:
    #     # could not compute result
    #     print('mongo_process_operations error: ')
    #     print('\tMONGO_OP_ERROR for operation {0}'.format(operation_name))
    #     client.close()
    #     return

    # output = list()
    # is_final = c['final']

    # # these fields are not copied from source doc to result doc
    # NO_COPY_FIELDS = [
    #     '_id', 'job_id', 'phenotype_id', 'owner',
    #     'job_date', 'context_type', 'raw_definition_text',
    #     'nlpql_feature', 'phenotype_final', 'history'
    # ]

    # # the field to join on should not be copied
    # NO_COPY_FIELDS.append(on)
    
    # if mongo_eval.MONGO_OP_MATH == eval_result.operation:

    #     # single-row evaluation results, both intermediate and final
    #     doc_groups = eval_result.doc_groups
    #     assert 1 == len(doc_groups)
    #     for doc in doc_groups[0]:

    #         # output doc
    #         ret = {}
            
    #         # add doc fields to the output doc as lists
    #         field_map = {}
    #         fields = doc.keys()
    #         fields_to_copy = [f for f in fields if f not in NO_COPY_FIELDS]
    #         for f in fields_to_copy:
    #             if f not in field_map:
    #                 field_map[f] = [doc[f]]
    #             else:
    #                 field_map[f].append(doc[f])

    #         for k,v in field_map.items():
    #             ret[k] = copy.deepcopy(v)

    #         # set the join field explicitly
    #         ret[on] = doc[on]
            
    #         ret['job_id'] = job_id
    #         ret['phenotype_id'] = phenotype_id
    #         ret['owner'] = phenotype_owner
    #         ret['job_date'] = datetime.datetime.now()
    #         ret['context_type'] = on
    #         ret['raw_definition_text'] = expression
    #         ret['nlpql_feature'] = operation_name
    #         ret['phenotype_final'] = c['final']

    #         # add source _id and nlpql_feature
    #         if is_final:
    #             ret['_ids_1'] = copy.deepcopy(doc['_id'])
    #             ret['nlpql_features_1'] = copy.deepcopy(doc['nlpql_feature'])
    #         else:
    #             # use same field names as for logic ops
    #             ret['_ids'] = copy.deepcopy(doc['_id'])
    #             ret['nlpql_features'] = copy.deepcopy(doc['nlpql_feature'])
            
    #         flatten_nested_lists(ret)

    #         if is_final:
    #             remove_arrays(ret)
                
    #         output.append(ret)

    #     if len(output) > 0:
    #         db.phenotype_results.insert_many(output)
    #     else:
    #         print('mongo_process_operations (math): No phenotype matches on %s.' % expression)
            
    # elif (mongo_eval.MONGO_OP_AND == eval_result.operation) or \
    #      (mongo_eval.MONGO_OP_OR  == eval_result.operation):
        
    #     # multi-row evaluation result, n-ary AND, n-ary OR
    #     print('           operation: {0}'.format(eval_result.operation))
    #     print('                   n: {0}'.format(eval_result.n))
    #     print('            is_final: {0}'.format(is_final))
    #     print('           doc count: {0}'.format(len(eval_result.doc_ids)))
    #     print('size of groups array: {0}'.format(len(eval_result.doc_groups)))
        
    #     doc_groups = eval_result.doc_groups
    #     # group_counter = 1
    #     for g in doc_groups:
    #         # print('\tgroup: {0} has {1} members'.format(group_counter, len(g)))
    #         # group_counter += 1

    #         # rearrange the docs in a group as ntuples (n == eval_result.n)
    #         # all docs in a group share the same value of the join variable
    #         if mongo_eval.MONGO_OP_AND == eval_result.operation:
    #             # need n elements for an AND ntuple (OR needs from 1..n)
    #             if len(g) < eval_result.n:
    #                 continue
    #             ntuples = mongo_eval.to_ntuples_AND(g, eval_result.n, other)                
    #         else:
    #             ntuples = mongo_eval.to_ntuples_OR(g, eval_result.n, other)
                
    #         # print('\tntuple count: {0}'.format(len(ntuples)))
    #         for ntuple in ntuples:

    #             # each ntuple supplies the data for a result doc
    #             ret = {}
    #             history = {
    #                 'source_ids'  : [],
    #                 'source_features' : []
    #             }

    #             # accumulate the source doc _id and nlpql_feature fields
    #             for doc in ntuple:
    #                 # print('\t\tdoc id: {0}, nlpql_feature: {1}, dimension_X: {2}, ' \
    #                 #       'report_id: {3}, subject: {4}, start/end: [{5}, {6})'.
    #                 #       format(doc['_id'], doc['nlpql_feature'], doc['dimension_X'],
    #                 #              doc['report_id'], doc['subject'], doc['start'],
    #                 #              doc['end']))

    #                 history['source_ids'].append(str(doc['_id']))
    #                 history['source_features'].append(doc['nlpql_feature'])
                        
    #             # add ntuple doc fields to the output doc as lists
    #             field_map = {}
    #             for doc in ntuple:
    #                 fields = doc.keys()
    #                 fields_to_copy = [f for f in fields if f not in NO_COPY_FIELDS]
    #                 for f in fields_to_copy:
    #                     if f not in field_map:
    #                         field_map[f] = [doc[f]]
    #                     else:
    #                         field_map[f].append(doc[f])

    #             for k,v in field_map.items():
    #                 ret[k] = copy.deepcopy(v)
                            
    #             # set the join field; same value for all ntuple entries
    #             ret[on] = ntuple[0][on]

    #             # update fields common to AND/OR
    #             ret['job_id'] = job_id
    #             ret['phenotype_id'] = phenotype_id
    #             ret['owner'] = phenotype_owner
    #             ret['job_date'] = datetime.datetime.now()
    #             ret['context_type'] = on
    #             ret['raw_definition_text'] = expression
    #             ret['nlpql_feature'] = operation_name
    #             ret['phenotype_final'] = c['final']

    #             # add source _ids and nlpql_features (1-based indexing)
    #             source_count = len(history['source_ids'])
    #             if is_final:
    #                 for i in range(len(history['source_ids'])):
    #                     field_name = '_ids_{0}'.format(i+1)
    #                     ret[field_name] = history['source_ids'][i]
    #                 for i in range(len(history['source_features'])):
    #                     field_name = 'nlpql_features_{0}'.format(i+1)
    #                     ret[field_name] = history['source_features'][i]

    #                 # remove intermediate array fields
    #                 ret.pop('_ids', None)
    #                 ret.pop('nlpql_features', None)
    #             else:
    #                 # add intermediate array fields
    #                 ret['_ids'] = copy.deepcopy(history['source_ids'])
    #                 ret['nlpql_features'] = copy.deepcopy(history['source_features'])
                    
    #             flatten_nested_lists(ret)

    #             if is_final:
    #                 remove_arrays(ret)
                    
    #             output.append(ret)

    #     if len(output) > 0:
    #         db.phenotype_results.insert_many(output)
    #     else:
    #         print('mongo_process_operations ({0}): no phenotype matches on {1}.'.
    #               format(eval_result.operation, expression))

    # elif mongo_eval.MONGO_OP_SETDIFF == eval_result.operation:
    #     # multi-row evaluation result, A NOT B (A SUBTRACT B)
    #     print('           operation: {0}'.format(eval_result.operation))
    #     print('            is_final: {0}'.format(is_final))
    #     print('           doc count: {0}'.format(len(eval_result.doc_ids)))
    #     print('size of groups array: {0}'.format(len(eval_result.doc_groups)))

    #     doc_groups = eval_result.doc_groups
    #     # group_counter = 1
    #     for g in doc_groups:
    #         # print('\tgroup: {0} has {1} members'.format(group_counter, len(g)))
    #         # group_counter += 1
    #         for doc in g:

    #             # no concept of ntuples for SETDIFF, just take docs in order

    #             ret = {}
    #             # print('\t\tdoc id: {0}, nlpql_feature: {1}, dimension_X: {2}, ' \
    #             #       'report_id: {3}, subject: {4}, start/end: [{5}, {6})'.
    #             #       format(doc['_id'], doc['nlpql_feature'], doc['dimension_X'],
    #             #              doc['report_id'], doc['subject'], doc['start'],
    #             #              doc['end']))

    #             # add doc fields to the output doc as lists
    #             field_map = {}
    #             fields = doc.keys()
    #             fields_to_copy = [f for f in fields if f not in NO_COPY_FIELDS]
    #             for f in fields_to_copy:
    #                 if f not in field_map:
    #                     field_map[f] = [doc[f]]
    #                 else:
    #                     field_map[f].append(doc[f])

    #             for k,v in field_map.items():
    #                 ret[k] = copy.deepcopy(v)
                            
    #             # set the join field explicitly
    #             ret[on] = doc[on]
                
    #             ret['job_id'] = job_id
    #             ret['phenotype_id'] = phenotype_id
    #             ret['owner'] = phenotype_owner
    #             ret['job_date'] = datetime.datetime.now()
    #             ret['context_type'] = on
    #             ret['raw_definition_text'] = expression
    #             ret['nlpql_feature'] = operation_name
    #             ret['phenotype_final'] = c['final']

    #             # add source _id and nlpql_features (only the set A features
    #             # are available; the set B features have been removed)
    #             if is_final:
    #                 ret['_ids_1'] = copy.deepcopy(doc['_id'])
    #                 ret['nlpql_features_1'] = copy.deepcopy(doc['nlpql_feature'])
    #             else:
    #                 # use same field names as for logic ops
    #                 ret['_ids'] = copy.deepcopy(doc['_id'])
    #                 ret['nlpql_features'] = copy.deepcopy(doc['nlpql_feature'])
                    
    #             flatten_nested_lists(ret)

    #             if is_final:
    #                 remove_arrays(ret)
                    
    #             output.append(ret)

    #     if len(output) > 0:
    #         db.phenotype_results.insert_many(output)
    #     else:
    #         print('mongo_process_operations ({0}): no phenotype matches on {1}.'.
    #               format(eval_result.operation, expression))


        

        
def mongo_process_operations_OLD(infix_tokens,
                             field_list,
                             db,
                             job_id,
                             phenotype: PhenotypeModel,
                             phenotype_id,
                             phenotype_owner,
                             c: PhenotypeOperations,
                             final=False):
    """
    Use MongoDB aggregation to evaluate NLPQL expressions.
    """

    client = MongoClient(util.mongo_host, util.mongo_port)
    mongo_db_obj = client[util.mongo_db]
    mongo_collection_obj = mongo_db_obj['phenotype_results']

    print('mongo_process_operations field_list: {0}'.format(field_list))

    # the filters for the $match operation will produce something like this,
    # for field_list = ['dimension_X', 'dimension_Y', 'dimension_Z']
    
    # db.phenotype_results.aggregate({
    #    $match : {
    #        "job_id":11116,
    #        "dimension_X" : {$exists:true, $ne:null},
    #        "dimension_Y" : {$exists:true, $ne:null},
    #        "dimension_Z" : {$exists:true, $ne:null}
    #    }
    # });
    
    match_filters = dict()
    match_filters['job_id'] = job_id

    for f in field_list:
        key = "{0}".format(f)
        value = {"$exists":True, "$ne":None}
        match_filters[key] = value

    operation_name = c['name']
    context = phenotype.context.lower()
    if 'document' == context:
        on = 'report_id'
        other = 'subject'
    else:
        on = 'subject'
        other = 'report_id'
    expression = c['raw_text']

    # build and run a Mongo aggregation pipeline to evaluate the expression
    eval_result = mongo_eval.run(mongo_collection_obj,
                                 infix_tokens,
                                 on,
                                 match_filters)
    if mongo_eval.MONGO_OP_ERROR == eval_result.operation:
        # could not compute result
        print('mongo_process_operations error: ')
        print('\tMONGO_OP_ERROR for operation {0}'.format(operation_name))
        client.close()
        return

    output = list()
    is_final = c['final']

    # these fields are not copied from source doc to result doc
    NO_COPY_FIELDS = [
        '_id', 'job_id', 'phenotype_id', 'owner',
        'job_date', 'context_type', 'raw_definition_text',
        'nlpql_feature', 'phenotype_final', 'history'
    ]

    # the field to join on should not be copied
    NO_COPY_FIELDS.append(on)
    
    if mongo_eval.MONGO_OP_MATH == eval_result.operation:

        # single-row evaluation results, both intermediate and final
        doc_groups = eval_result.doc_groups
        assert 1 == len(doc_groups)
        for doc in doc_groups[0]:

            # output doc
            ret = {}
            
            # add doc fields to the output doc as lists
            field_map = {}
            fields = doc.keys()
            fields_to_copy = [f for f in fields if f not in NO_COPY_FIELDS]
            for f in fields_to_copy:
                if f not in field_map:
                    field_map[f] = [doc[f]]
                else:
                    field_map[f].append(doc[f])

            for k,v in field_map.items():
                ret[k] = copy.deepcopy(v)

            # set the join field explicitly
            ret[on] = doc[on]
            
            ret['job_id'] = job_id
            ret['phenotype_id'] = phenotype_id
            ret['owner'] = phenotype_owner
            ret['job_date'] = datetime.datetime.now()
            ret['context_type'] = on
            ret['raw_definition_text'] = expression
            ret['nlpql_feature'] = operation_name
            ret['phenotype_final'] = c['final']

            # add source _id and nlpql_feature
            if is_final:
                ret['_ids_1'] = copy.deepcopy(doc['_id'])
                ret['nlpql_features_1'] = copy.deepcopy(doc['nlpql_feature'])
            else:
                # use same field names as for logic ops
                ret['_ids'] = copy.deepcopy(doc['_id'])
                ret['nlpql_features'] = copy.deepcopy(doc['nlpql_feature'])
            
            flatten_nested_lists(ret)

            if is_final:
                remove_arrays(ret)
                
            output.append(ret)

        if len(output) > 0:
            db.phenotype_results.insert_many(output)
        else:
            print('mongo_process_operations (math): No phenotype matches on %s.' % expression)
            
    elif (mongo_eval.MONGO_OP_AND == eval_result.operation) or \
         (mongo_eval.MONGO_OP_OR  == eval_result.operation):
        
        # multi-row evaluation result, n-ary AND, n-ary OR
        print('           operation: {0}'.format(eval_result.operation))
        print('                   n: {0}'.format(eval_result.n))
        print('            is_final: {0}'.format(is_final))
        print('           doc count: {0}'.format(len(eval_result.doc_ids)))
        print('size of groups array: {0}'.format(len(eval_result.doc_groups)))
        
        doc_groups = eval_result.doc_groups
        # group_counter = 1
        for g in doc_groups:
            # print('\tgroup: {0} has {1} members'.format(group_counter, len(g)))
            # group_counter += 1

            # rearrange the docs in a group as ntuples (n == eval_result.n)
            # all docs in a group share the same value of the join variable
            if mongo_eval.MONGO_OP_AND == eval_result.operation:
                # need n elements for an AND ntuple (OR needs from 1..n)
                if len(g) < eval_result.n:
                    continue
                ntuples = mongo_eval.to_ntuples_AND(g, eval_result.n, other)                
            else:
                ntuples = mongo_eval.to_ntuples_OR(g, eval_result.n, other)
                
            # print('\tntuple count: {0}'.format(len(ntuples)))
            for ntuple in ntuples:

                # each ntuple supplies the data for a result doc
                ret = {}
                history = {
                    'source_ids'  : [],
                    'source_features' : []
                }

                # accumulate the source doc _id and nlpql_feature fields
                for doc in ntuple:
                    # print('\t\tdoc id: {0}, nlpql_feature: {1}, dimension_X: {2}, ' \
                    #       'report_id: {3}, subject: {4}, start/end: [{5}, {6})'.
                    #       format(doc['_id'], doc['nlpql_feature'], doc['dimension_X'],
                    #              doc['report_id'], doc['subject'], doc['start'],
                    #              doc['end']))

                    history['source_ids'].append(str(doc['_id']))
                    history['source_features'].append(doc['nlpql_feature'])
                        
                # add ntuple doc fields to the output doc as lists
                field_map = {}
                for doc in ntuple:
                    fields = doc.keys()
                    fields_to_copy = [f for f in fields if f not in NO_COPY_FIELDS]
                    for f in fields_to_copy:
                        if f not in field_map:
                            field_map[f] = [doc[f]]
                        else:
                            field_map[f].append(doc[f])

                for k,v in field_map.items():
                    ret[k] = copy.deepcopy(v)
                            
                # set the join field; same value for all ntuple entries
                ret[on] = ntuple[0][on]

                # update fields common to AND/OR
                ret['job_id'] = job_id
                ret['phenotype_id'] = phenotype_id
                ret['owner'] = phenotype_owner
                ret['job_date'] = datetime.datetime.now()
                ret['context_type'] = on
                ret['raw_definition_text'] = expression
                ret['nlpql_feature'] = operation_name
                ret['phenotype_final'] = c['final']

                # add source _ids and nlpql_features (1-based indexing)
                source_count = len(history['source_ids'])
                if is_final:
                    for i in range(len(history['source_ids'])):
                        field_name = '_ids_{0}'.format(i+1)
                        ret[field_name] = history['source_ids'][i]
                    for i in range(len(history['source_features'])):
                        field_name = 'nlpql_features_{0}'.format(i+1)
                        ret[field_name] = history['source_features'][i]

                    # remove intermediate array fields
                    ret.pop('_ids', None)
                    ret.pop('nlpql_features', None)
                else:
                    # add intermediate array fields
                    ret['_ids'] = copy.deepcopy(history['source_ids'])
                    ret['nlpql_features'] = copy.deepcopy(history['source_features'])
                    
                flatten_nested_lists(ret)

                if is_final:
                    remove_arrays(ret)
                    
                output.append(ret)

        if len(output) > 0:
            db.phenotype_results.insert_many(output)
        else:
            print('mongo_process_operations ({0}): no phenotype matches on {1}.'.
                  format(eval_result.operation, expression))

    elif mongo_eval.MONGO_OP_SETDIFF == eval_result.operation:
        # multi-row evaluation result, A NOT B (A SUBTRACT B)
        print('           operation: {0}'.format(eval_result.operation))
        print('            is_final: {0}'.format(is_final))
        print('           doc count: {0}'.format(len(eval_result.doc_ids)))
        print('size of groups array: {0}'.format(len(eval_result.doc_groups)))

        doc_groups = eval_result.doc_groups
        # group_counter = 1
        for g in doc_groups:
            # print('\tgroup: {0} has {1} members'.format(group_counter, len(g)))
            # group_counter += 1
            for doc in g:

                # no concept of ntuples for SETDIFF, just take docs in order

                ret = {}
                # print('\t\tdoc id: {0}, nlpql_feature: {1}, dimension_X: {2}, ' \
                #       'report_id: {3}, subject: {4}, start/end: [{5}, {6})'.
                #       format(doc['_id'], doc['nlpql_feature'], doc['dimension_X'],
                #              doc['report_id'], doc['subject'], doc['start'],
                #              doc['end']))

                # add doc fields to the output doc as lists
                field_map = {}
                fields = doc.keys()
                fields_to_copy = [f for f in fields if f not in NO_COPY_FIELDS]
                for f in fields_to_copy:
                    if f not in field_map:
                        field_map[f] = [doc[f]]
                    else:
                        field_map[f].append(doc[f])

                for k,v in field_map.items():
                    ret[k] = copy.deepcopy(v)
                            
                # set the join field explicitly
                ret[on] = doc[on]
                
                ret['job_id'] = job_id
                ret['phenotype_id'] = phenotype_id
                ret['owner'] = phenotype_owner
                ret['job_date'] = datetime.datetime.now()
                ret['context_type'] = on
                ret['raw_definition_text'] = expression
                ret['nlpql_feature'] = operation_name
                ret['phenotype_final'] = c['final']

                # add source _id and nlpql_features (only the set A features
                # are available; the set B features have been removed)
                if is_final:
                    ret['_ids_1'] = copy.deepcopy(doc['_id'])
                    ret['nlpql_features_1'] = copy.deepcopy(doc['nlpql_feature'])
                else:
                    # use same field names as for logic ops
                    ret['_ids'] = copy.deepcopy(doc['_id'])
                    ret['nlpql_features'] = copy.deepcopy(doc['nlpql_feature'])
                    
                flatten_nested_lists(ret)

                if is_final:
                    remove_arrays(ret)
                    
                output.append(ret)

        if len(output) > 0:
            db.phenotype_results.insert_many(output)
        else:
            print('mongo_process_operations ({0}): no phenotype matches on {1}.'.
                  format(eval_result.operation, expression))

    # elif mongo_eval.MONGO_OP_NOT == eval_result.operation:
    #     # multi-row evaluation result, NOT A
    #     print('           operation: {0}'.format(eval_result.operation))
    #     print('                   n: {0}'.format(eval_result.n))
    #     print('            is_final: {0}'.format(is_final))
    #     print('           doc count: {0}'.format(len(eval_result.doc_ids)))
    #     print('size of groups array: {0}'.format(len(eval_result.doc_groups)))

    #     doc_groups = eval_result.doc_groups
    #     group_counter = 1
    #     for g in doc_groups:
    #         print('\tgroup: {0} has {1} members'.format(group_counter, len(g)))
    #         group_counter += 1
    #         for doc in g:
    #             print('\t\tdoc id: {0}, nlpql_feature: {1}, dimension_X: {2}, ' \
    #                   'report_id: {3}, subject: {4}, start/end: [{5}, {6})'.
    #                   format(doc['_id'], doc['nlpql_feature'], doc['dimension_X'],
    #                          doc['report_id'], doc['subject'], doc['start'],
    #                          doc['end']))


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
