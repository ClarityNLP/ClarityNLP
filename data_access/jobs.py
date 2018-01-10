import psycopg2
import psycopg2.extras
from .base_model import BaseModel


class PhenotypeJob(BaseModel):

    description = ''
    date_ended = None

    def __init__(self, name, description, owner, pipeline_id, status, date_started, date_ended):
        self.name = name
        self.description = description
        self.owner = owner
        self.pipeline_id = pipeline_id
        self.status = status
        self.date_started = date_started
        self.date_ended = date_ended


def create_new_job(pipeline_job: PhenotypeJob, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cursor.execute("""
                INSERT INTO nlp.phenotype_job (name, description, owner, status, date_started, date_ended)
                VALUES (%s, %s, %s, %s, current_timestamp, null) RETURNING pipeline_id""",
                       pipeline_job.name, pipeline_job.description, pipeline_job.owner,
                       pipeline_job.status, pipeline_job.date_started, pipeline_job.date_ended)

        job_id = cursor.fetchone()[0]
        return job_id
    except Exception as e:
        print(e)
    finally:
        conn.close()

    return -1


def get_job_status(pipeline_id: str, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cursor.execute("""SELECT status from nlp.pipeline_job where pipeline_job_id = %s""",
                       pipeline_id)

        status = cursor.fetchone()[0]
        return status
    except Exception as e:
        print(e)
    finally:
        conn.close()

    return "UNKNOWN"
