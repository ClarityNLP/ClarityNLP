import psycopg2
import psycopg2.extras
import sys
import json
import configparser

try:
    from .base_model import BaseModel
except Exception as e:
    print(e)
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

    def __init__(self, config_type, name, description, terms, limit):
        self.config_type = config_type
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
            obj = PipelineConfig.from_json(row["config"])
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
    return PipelineConfig('UNKNOWN', 'UNKNOWN', 'UNKNOWN', [], -1)


def get_query(p_config:PipelineConfig):
    if p_config.terms is not None and len(p_config.terms) > 0:
        return 'report_text:("' + '" OR "'.join(p_config.terms) + '")'
    else:
        return '*'


def get_limit(doc_count, p_config: PipelineConfig):
    if p_config.limit is not None:
        return int(p_config.limit)
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
        config_obj = PipelineConfig.from_dict(config)
        print(config_obj)
        sys.exit(0)
    else:
        print("Enter pipeline id")
        sys.exit(-1)
