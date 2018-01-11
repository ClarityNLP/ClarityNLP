import psycopg2
import psycopg2.extras
import sys
import json
import configparser
from .base_model import BaseModel


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

    def __init__(self, type, name, description, terms, limit):
        self.type = type
        self.name = name
        self.description = description
        self.terms = terms
        self.limit = limit


def get_pipeline_config(pipeline_id, connection_string):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cursor.execute("""
                     SELECT  *
                     FROM    nlp.pipeline_config
                     WHERE   pipeline_id = %s 
                     """, str(pipeline_id))

        row = cursor.fetchone()
        if row:
            print(row)
            obj = json.loads(row["config"])
            print(obj)
            if obj:
                return obj
            else:
                return get_default_config()
    except Exception as e:
        print(e)
    finally:
        conn.close()

    return get_default_config()


def get_default_config():
    return {}


def get_query(p_config):
    if 'override_query' in p_config and p_config['override_query']:
        return p_config['override_query']
    elif 'terms' in p_config and len(p_config['terms']) > 0:
        return 'report_text:("' + '" OR "'.join(p_config['terms']) + '")'
    else:
        return '*'


def get_limit(doc_count, p_config):
    if 'limit' in p_config:
        return int(p_config['limit'])
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

        print(get_pipeline_config(q, conn_string))
        sys.exit(1)
    else:
        print("Enter pipeline id")
        sys.exit(-1)
