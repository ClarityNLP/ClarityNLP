import re
import collections
import datetime
import sys
import traceback
from functools import reduce

import pandas as pd

import util
from data_access import PhenotypeModel, PipelineConfig, PhenotypeEntity, PhenotypeOperations
from data_access import expr_eval, expr_result
from ohdsi import getCohort
from claritynlp_logging import log, ERROR, DEBUG

# import json
# from bson import json_util, ObjectId

DEBUG_LIMIT = 1000
COL_LIST = ["_id", "report_date", 'report_id', 'subject', 'sentence']

pipeline_keys = PipelineConfig('test', 'test').__dict__.keys()
numeric_comp_operators = ['==', '=', '>', '<', '<=', '>=']

# for time filtering of results
_FILTER_COND_EARLIEST = 0
_FILTER_COND_LATEST   = 1

# timestamp format: YYYY-MM-DDThh:mm:ssZ
_str_report_date = r'\A(?P<year>\d\d\d\d)\-(?P<month>\d\d)\-(?P<day>\d\d)' +\
    r'T(?P<hour>\d\d):(?P<minute>\d\d):(?P<sec>\d\d)Z\Z'
_regex_report_date = re.compile(_str_report_date)


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
            log(d)
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


manually_mapped_keys = ['owner', 'limit', 'name', 'config_type', 'terms', 'cohort', 'job_results', 'concept_code',
                        'concept_code_system', 'cql', 'cql_source', 'named_arguments', 'display_name']


def map_arguments(pipeline: PipelineConfig, e, all_terms):
    for k in e.keys():
        if k not in manually_mapped_keys:
            if k in pipeline_keys:
                try:
                    pipeline[k] = e[k]
                except Exception as ex:
                    traceback.print_exc(file=sys.stdout)
                    log(ex)
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
                    log(ex)


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
                               cohorts, phenotype_limit=0, report_types: dict = None,
                               custom_query: dict = None, filter_query: dict = None, source: dict = None,
                               job_results: dict = None):
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
    if 'excluded_termsets' not in e['named_arguments']:
        e['named_arguments']['excluded_termsets'] = []

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

        if 'excluded_termset' in e['named_arguments']:
            excluded_terms = e['named_arguments']["excluded_termset"]
        elif 'excluded_termsets' in e['named_arguments']:
            excluded_terms = e['named_arguments']["excluded_termsets"]
        else:
            excluded_terms = list()

        if 'code' in e['named_arguments']:
            code = e['named_arguments']["code"]
        elif 'concept_code' in e['named_arguments']:
            code = e['named_arguments']["concept_code"]
        else:
            code = ''

        if 'code_system' in e['named_arguments']:
            code_system = e['named_arguments']["code_system"]
        elif 'concept_code_system' in e['named_arguments']:
            code_system = e['named_arguments']["concept_code_system"]
        elif 'codesystem' in e['named_arguments']:
            code_system = e['named_arguments']["codesystem"]
        else:
            code_system = ''

        if 'cohort' in e['named_arguments']:
            cohort, job_results_filter = get_cohort_items(e['named_arguments']['cohort'], cohorts, job_results)
        elif 'cohorts' in e['named_arguments']:
            cohort, job_results_filter = get_cohort_items(e['named_arguments']['cohorts'], cohorts, job_results)
        else:
            cohort, job_results_filter = list(), dict()

        if 'cql' in e['named_arguments']:
            cql = e['named_arguments']["cql"]
        elif 'cql_source' in e['named_arguments']:
            cql = e['named_arguments']["cql_source"]
        else:
            cql = ''

        if 'display_name' in e['named_arguments']:
            display_name = e['named_arguments']["display_name"]
        elif 'displayname' in e['named_arguments']:
            display_name = e['named_arguments']["display_name"]
        elif 'name' in e['named_arguments']:
            display_name = e['named_arguments']["name"]
        else:
            display_name = e['name']

        tags = get_item_list_by_key(report_tags, doc_sets)
        types = get_item_list_by_key(report_types, doc_sets)
        query = get_item_by_key(custom_query, doc_sets)
        fq = get_item_by_key(filter_query, doc_sets)
        sources = get_item_list_by_key(source, doc_sets)

        pipeline = PipelineConfig(e['funct'], e['name'],
                                  get_terms_by_keys(all_terms, terms,
                                                    e['named_arguments']['value_sets']
                                                    ),
                                  excluded_terms=get_terms_by_keys(all_terms, excluded_terms,
                                                                   e['named_arguments']['value_sets'])
                                  ,
                                  owner=owner,
                                  limit=limit,
                                  cohort=cohort,
                                  job_results=job_results_filter,
                                  report_tags=tags,
                                  report_types=types,
                                  sources=sources,
                                  custom_query=query,
                                  filter_query=fq,
                                  concept_code=code,
                                  concept_code_system=code_system,
                                  cql=cql,
                                  is_phenotype=True,
                                  display_name=display_name)
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
                log(ex)
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
                log(ex)
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
        evaluator = 'mongo'

    # the NLPQL expression to be evaluated
    expression = c['raw_text']

    # the NLPQL feature name to assign to the result
    nlpql_feature = c['name']

    mongo_failed = False
    if 'mongo' == evaluator:
        log('Using mongo evaluator for expression "{0}"'.format(expression))

        # The validate_phenotype function parses the expression and checks it
        # for various errors. A normalized version of the expression is then
        # stored in the operations dict for that expression. If validation has
        # not been performed for some reason, the normalized expression will
        # contain the empty string.
        parse_result = c['normalized_expr']
        if 0 == len(parse_result):
        
            # get the names of the phenotype's data_entities and operations
            names = get_all_names(phenotype)

            # Parse the expression and return a fully-parenthesized version
            # that uses mnemonics for the operators. The evaluator will attempt
            # to resolve any unknown tokens into concatenated names and logic
            # operators. If it finds a token that it cannot resolve into known
            # names it returns an empty string. An empty string is also
            # returned if the expression cannot be evaluated for some other
            # reason.
            parse_result = expr_eval.parse_expression(expression, names)
            
        if 0 == len(parse_result):
            log('\n\t*** Expression cannot be evaluated. ***\n')
            mongo_failed = True
        else:
            # generate a list of expr_eval.ExpressionObject items
            expr_list = expr_eval.generate_expressions(nlpql_feature, parse_result)
            if 0 == len(expr_list):
                log('\t\n*** No subexpressions found! ***\n')
                mongo_failed = True
            else:
                mongo_process_operations(expr_list, db, job, phenotype,
                                         phenotype_id, phenotype_owner, c, final)

    if 'pandas' == evaluator or mongo_failed:
        log('Using pandas evaluator for expression "{0}"'.format(expression))
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
            log('Empty dataframe!')
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
            log(action)
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


def _apply_time_filter(output_docs, filter_condition):
    """
    Scan the outupt_docs list, apply time filter condition, and return
    docs that survive the filter.
    """

    if len(output_docs) <= 1:
        return output_docs
    
    assert filter_condition == _FILTER_COND_EARLIEST or \
        filter_condition == _FILTER_COND_LATEST
    
    # datetime field of interest
    KEY_RD = 'report_date'

    # build list of datetimes
    datetime_list = []
    for doc in output_docs:
        
        # each document must have a report_date field
        assert KEY_RD in doc
        report_date = doc[KEY_RD]
        
        # timestamps should be in YYYY-MM-DDThh:mm:ssZ format
        match = _regex_report_date.match(report_date)
        assert match
        
        if match:
            year = int(match.group('year'))
            month = int(match.group('month'))
            day = int(match.group('day'))
            hr = int(match.group('hour'))
            minute = int(match.group('minute'))
            sec = int(match.group('sec'))
            
            dt = datetime.datetime(year, month, day, hr, minute, sec)
            datetime_list.append(dt)

    assert len(datetime_list) == len(output_docs)
            
    # index denotes the winner
    index = 0
    winner = datetime_list[0]

    for i, dt in enumerate(datetime_list):
        if _FILTER_COND_EARLIEST == filter_condition:
            if dt < winner:
                winner = dt
                index = i
        else:
            if dt > winner:
                winner = dt
                index = i

    results = [output_docs[i]]
    return results


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

    log('mongo_process_operations expr_object_list: ')
    for expr_obj in expr_obj_list:
        log(expr_obj)

    context_var = phenotype.context.lower()
    if 'document' == context_var:
        # document IDs are in the report_id field
        context_field = 'report_id'
    else:
        # patient IDs are in the subject field
        context_field = 'subject'

    # setup access to the Mongo collection
    client = util.mongo_client()
    mongo_db_obj = client[util.mongo_db]
    mongo_collection_obj = mongo_db_obj['phenotype_results']

    # ensure integer job_id; expression evaluator needs to lookup results
    # by job_id, but a job id of 42 is different from a job_id of '42'
    job_id = int(job_id)
    
    try:
        is_final_save = c['final']

        for expr_obj in expr_obj_list:

            # the 'is_final' flag only applies to the last subexpression
            if expr_obj != expr_obj_list[-1]:
                is_final = False
            else:
                is_final = is_final_save

            # evaluate the (sub)expression in expr_obj
            eval_result = expr_eval.evaluate_expression(expr_obj,
                                                        job_id,
                                                        context_field,
                                                        mongo_collection_obj)

            # query MongoDB to get result docs
            cursor = mongo_collection_obj.find({'_id': {'$in': eval_result.doc_ids}})

            # initialize for MongoDB result document generation
            phenotype_info = expr_result.PhenotypeInfo(
                job_id=job_id,
                phenotype_id=phenotype_id,
                owner=phenotype_owner,
                context_field=context_field,
                is_final=is_final
            )

            # generate result documents
            if expr_eval.EXPR_TYPE_MATH == eval_result.expr_type:

                output_docs = expr_result.to_math_result_docs(eval_result,
                                                              phenotype_info,
                                                              cursor)
            else:
                assert expr_eval.EXPR_TYPE_LOGIC == eval_result.expr_type

                # flatten the result set into a set of Mongo documents
                doc_map, oid_list_of_lists = expr_eval.flatten_logical_result(eval_result,
                                                                              mongo_collection_obj)

                output_docs = expr_result.to_logic_result_docs(eval_result,
                                                               phenotype_info,
                                                               doc_map,
                                                               oid_list_of_lists)

            # apply time filter, if any - TBD
            # output_docs = _apply_time_filter(output_docs, filter_condition)
                
            if len(output_docs) > 0:
                log('***** mongo_process_operations: writing {0} ' \
                    'output_docs *****'.format(len(output_docs)))
                try:
                    mongo_collection_obj.insert_many(output_docs)
                except pymongo.errors.BulkWriteError as e:
                    log('****** mongo_process_operations: ' \
                        'mongo insert_many failure ******')
                    log(e)
            else:
                log('mongo_process_operations ({0}): ' \
                      'no phenotype matches on "{1}".'.format(eval_result.expr_type,
                                                              eval_result.expr_text))
    except Exception as exc:
        log(exc, ERROR)
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
        log(ex)
        error = ''.join(traceback.format_stack())

    # Run validity and syntax checks on all expressions, ensure that only
    # defined names are used as variables, etc.

    name_list = get_all_names(p_cfg)

    # get raw text of all expressions
    KEY_RAW  = 'raw_text'    
    expression_list = []    
    for i, op in enumerate(p_cfg.operations):
        if KEY_RAW in op:
            # save expression index and raw text
            expression_list.append( (i, op[KEY_RAW]) )
    
    for i, expr in expression_list:
        # The 'parse_result' is a string of whitespace-separated expression
        # tokens. Invalid expressions cause an empty string to be returned.
        parse_result = expr_eval.parse_expression(expr, name_list)
        if 0 == len(parse_result):
            error = 'Invalid expression: {0}'.format(expr)
            break
        else:
            # saved the parse result for later use
            p_cfg.operations[i]['normalized_expr'] = parse_result
    
    if not error:
        return {"success": True}
    else:
        return {"success": False, "error": error}
