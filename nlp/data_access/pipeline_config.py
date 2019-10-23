import sys

import psycopg2
import psycopg2.extras

import util
from claritynlp_logging import log, ERROR, DEBUG


try:
    from .base_model import BaseModel
except Exception as ex:
    log(ex)
    from base_model import BaseModel


class Pipeline(BaseModel):

    def __init__(self, pipeline_id, owner, name, description, config_string, pipeline_type, date_created, date_updated):
        self.pipeline_id = pipeline_id
        self.owner = owner
        self.config = config_string
        self.date_created = date_created
        self.date_updated = date_updated
        self.pipeline_type = pipeline_type
        self.name = name
        self.description = description


class PipelineConfig(BaseModel):

    def __init__(self, config_type, name, terms: list = None, excluded_terms=None, description='', limit=0,
                 concept_code='', concept_code_system='',
                 owner='system', include_synonyms=False, include_descendants=False, include_ancestors=False,
                 report_tags: list = None, vocabulary='SNOMED', sections: list = None, report_type_query='',
                 minimum_value=0, maximum_value=10000, case_sensitive=False, cohort: list = None, sources: list = None,
                 is_phenotype=False, report_types: list = None, custom_query='', filter_query='',
                 custom_arguments: dict = None, enum_list: list = None, final: bool = False, job_results: dict = None,
                 pipeline_id=-1, cql='', display_name=''):

        # This code initializes mutable params in a manner that prevents the
        # "mutable default argument" bug. In this function the types of the
        # mutable params are list and dict. If a call to PipelineConfig omits a
        # value for a mutable param, that param is assigned the value 'None',
        # which causes the mutable param to be re-initialized to an empty list
        # or dict.

        # A construct such as 'param: list=list()' only runs the
        # default initializer on the first call. On subsequent calls the param
        # is not re-initialized to an empty list.

        self.config_type = config_type
        self.name = name
        if terms is None:
            self.terms = list()
        else:
            self.terms = terms

        if excluded_terms is None:
            self.excluded_terms = list()
        else:
            self.excluded_terms = excluded_terms
        self.description = description
        self.limit = limit
        self.concept_code = concept_code
        self.concept_code_system = concept_code_system
        self.owner = owner
        self.include_synonyms = include_synonyms
        self.include_descendants = include_descendants
        self.include_ancestors = include_ancestors
        if report_tags is None:
            self.report_tags = list()
        else:
            self.report_tags = report_tags
        self.vocabulary = vocabulary
        if sections is None:
            self.sections = list()
        else:
            self.sections = sections
        self.report_type_query = report_type_query
        self.minimum_value = minimum_value
        self.maximum_value = maximum_value
        self.case_sensitive = case_sensitive
        if cohort is None:
            self.cohort = list()
        else:
            self.cohort = cohort
        self.is_phenotype = is_phenotype
        if report_types is None:
            self.report_types = list()
        else:
            self.report_types = report_types
        self.custom_query = custom_query
        self.filter_query = filter_query
        if custom_arguments is None:
            self.custom_arguments = dict()
        else:
            self.custom_arguments = custom_arguments
        if enum_list is None:
            self.enum_list = list()
        else:
            self.enum_list = enum_list
        self.final = final
        if job_results is None:
            self.job_results = dict()
        else:
            self.job_results = job_results
        if sources is None:
            self.sources = list()
        else:
            self.sources = sources
        self.pipeline_id = pipeline_id
        self.cql = cql
        self.display_name = display_name


def insert_pipeline_config(pipeline: PipelineConfig, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    pipeline_id = -1

    try:
        if pipeline:
            pipeline_json = pipeline.to_json()
            cursor.execute("""
                          INSERT INTO
                          nlp.pipeline_config(owner, config, pipeline_type, name, description, date_created)
                          VALUES(%s, %s, %s, %s, %s, current_timestamp) RETURNING pipeline_id
                          """,
                           (pipeline.owner, pipeline_json, pipeline.config_type, pipeline.name, pipeline.description))

            pipeline_id = cursor.fetchone()[0]
            conn.commit()

    except Exception as ex:
        log('failed to insert pipeline')
        log(ex)
    finally:
        conn.close()

    return pipeline_id


def update_pipeline_config(pipeline: PipelineConfig, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    try:
        if pipeline and pipeline['pipeline_id'] > -1:
            pipeline_json = pipeline.to_json()
            cursor.execute("""
                           UPDATE nlp.pipeline_config SET config = %s WHERE pipeline_id = %s
                          """, (pipeline_json, str(pipeline['pipeline_id'])))

            conn.commit()
            success = True
    except Exception as ex:
        log('failed to insert pipeline')
        log(ex)
        success = True
    finally:
        conn.close()

    return success


def get_pipeline_config(pipeline_id, connection_string):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    try:
        cursor.execute("""
                     SELECT  *
                     FROM    nlp.pipeline_config
                     WHERE   pipeline_id = %s
                     """, [str(pipeline_id)])

        row = cursor.fetchone()
        if row:
            obj = PipelineConfig.from_json(row[2])
            if obj:
                return obj
            else:
                return get_default_config()
        else:
            log("no rows returned")
    except Exception as ex:
        log(ex)
    finally:
        conn.close()

    return get_default_config()


def get_default_config():
    return PipelineConfig('UNKNOWN', 'UNKNOWN', [])


def get_query(custom_query='', terms=None):
    if terms is None:
        terms = list()
    query = ''
    if len(terms) > 0:
        query = util.solr_text_field + ':("' + '" OR "'.join(terms) + '")'
    if custom_query and len(custom_query) > 0:
        if len(query) > 0:
            query += " AND "
        query += custom_query

    if len(query) == 0:
        return '*:*'
    else:
        return query


def get_limit(doc_count, p_config: PipelineConfig):
    if p_config.limit is not None and int(p_config.limit) > 0:
        return min(int(p_config.limit), doc_count)
    else:
        return int(doc_count)


def insert_pipeline_results(pipeline_config: PipelineConfig, db, obj):
    if pipeline_config.is_phenotype:
        inserted = db.phenotype_results.insert_one(obj)
    else:
        inserted = db.pipeline_results.insert_one(obj)
    return inserted


if __name__ == '__main__':
    if len(sys.argv) > 1:
        q = sys.argv[1]
        conn_string = util.conn_string
        config = (get_pipeline_config(q, conn_string))
        log(config)
        sys.exit(1)
    else:
        log("Enter pipeline id")
        sys.exit(-1)
