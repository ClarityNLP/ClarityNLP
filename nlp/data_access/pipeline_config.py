import psycopg2
import psycopg2.extras
import sys
import util

try:
    from .base_model import BaseModel
except Exception as ex:
    print(ex)
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

    def __init__(self, config_type, name, terms=list(), description='', limit=0, concept_code=-1, owner='system',
                 include_synonyms=False, include_descendants=False, include_ancestors=False, report_tags=list(),
                 vocabulary='SNOMED', sections=list(), report_type_query='', minimum_value=0, maximum_value=10000,
                 case_sensitive=False, cohort=list(), is_phenotype=False, report_types=list(), custom_query='', filter_query='',
                 custom_arguments: dict=dict(), enum_list: list=list()):
        self.config_type = config_type
        self.name = name
        self.description = description
        self.terms = terms
        self.limit = limit
        self.concept_code = concept_code
        self.owner = owner
        self.include_synonyms = include_synonyms
        self.include_descendants = include_descendants
        self.include_ancestors = include_ancestors
        self.report_tags = report_tags
        self.report_types = report_types
        self.custom_query = custom_query
        self.filter_query = filter_query
        self.vocabulary = vocabulary
        self.sections = sections
        self.report_type_query = report_type_query
        self.minimum_value = minimum_value
        self.maximum_value = maximum_value
        self.case_sensitive = case_sensitive
        self.cohort = cohort
        self.is_phenotype = is_phenotype
        self.custom_arguments = custom_arguments
        self.enum_list = enum_list


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
                          """, (pipeline.owner, pipeline_json, pipeline.config_type, pipeline.name, pipeline.description))

            pipeline_id = cursor.fetchone()[0]
            conn.commit()

    except Exception as ex:
        print('failed to insert pipeline')
        print(ex)
    finally:
        conn.close()

    return pipeline_id


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
            print("no rows returned")
    except Exception as ex:
        print(ex)
    finally:
        conn.close()

    return get_default_config()


def get_default_config():
    return PipelineConfig('UNKNOWN', 'UNKNOWN', [])


def get_query(custom_query='', terms: list = list()):
    if custom_query and len(custom_query) > 0:
        return custom_query
    elif terms is not None and len(terms) > 0:
        return util.solr_text_field + ':("' + '" OR "'.join(terms) + '")'
    else:
        return '*'


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
        print(config)
        sys.exit(1)
    else:
        print("Enter pipeline id")
        sys.exit(-1)
