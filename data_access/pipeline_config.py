import psycopg2
import psycopg2.extras
import sys
import json
import configparser

try:
    from .base_model import BaseModel
except Exception as e:
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

    def __init__(self, config_type, name, description, terms, limit=1000, concept_code=-1, owner='system', include_synonyms=False,
                 include_descendants=False, include_ancestors=False, report_tags=list(), vocabulary='SNOMED'):
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
        self.vocabulary = vocabulary


def insert_pipeline_config(pipeline: PipelineConfig, connection_string: str):

    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    pipeline_id = -1

    try:
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
        print(str(ex))
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
    return PipelineConfig('UNKNOWN', 'UNKNOWN', 'UNKNOWN', [], -1, -1, 'none')


def get_query(terms: PipelineConfig):
    if terms is not None and len(terms) > 0:
        return 'report_text:("' + '" OR "'.join(terms) + '")'
    else:
        return '*'


def get_limit(doc_count, p_config: PipelineConfig):
    if p_config.limit is not None and int(p_config.limit) > 0:
        return min(int(p_config.limit), doc_count)
    else:
        return int(doc_count)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        q = sys.argv[1]

        config = configparser.RawConfigParser()
        config.read('../project.cfg')
        conn_string = "host='%s' dbname='%s' user='%s' password='%s' port=%s" % (config.get('pg', 'host'),
                                                                                 config.get('pg', 'dbname'),
                                                                                 config.get('pg', 'user'),
                                                                                 config.get('pg', 'password'),
                                                                                 config.get('pg', 'port'))

        config = (get_pipeline_config(q, conn_string))
        print(config)
        sys.exit(1)
    else:
        print("Enter pipeline id")
        sys.exit(-1)
