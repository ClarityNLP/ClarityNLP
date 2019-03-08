import psycopg2
import psycopg2.extras
import configparser
import json
import util
import sys
import traceback
from datetime import datetime, timezone

try:
    from .base_model import BaseModel
except Exception as e:
    print(e)
    from base_model import BaseModel


class NLPQL(BaseModel):
    def __init__(self, nlpql_raw, nlpql_json):
        self.raw = nlpql_raw
        self.json = nlpql_json


def create_new_nlpql(nlpql: NLPQL, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    try:
        dt = datetime.now()
        cursor.execute("""
                INSERT INTO nlp.nlpql_library (nlpql_raw, nlpql_json, date_added)
                VALUES (%s, %s, %s) RETURNING nlpql_id""",
                       (nlpql.raw, nlpql.json, dt))
        nlpql_id = cursor.fetchone()[0]
        conn.commit()

        return nlpql_id
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    finally:
        conn.close()

    return -1
