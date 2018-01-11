import psycopg2
import psycopg2.extras
from .base_model import BaseModel


class NlpJob(BaseModel):

    description = ''
    date_ended = None

    def __init__(self, name, description, owner, id, status, date_started, date_ended):
        self.name = name
        self.description = description
        self.owner = owner
        self.id = id
        self.status = status
        self.date_started = date_started
        self.date_ended = date_ended
        self.type = type


def create_new_job(job: NlpJob, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cursor.execute("""
                INSERT INTO nlp.nlp_job (name, job_type, description, owner, status, date_started, date_ended)
                VALUES (%s, %s, %s, %s, current_timestamp, null) RETURNING pipeline_id""",
                       job.name, job.job_type, job.description, job.owner,
                       job.status, job.date_started, job.date_ended)

        job_id = cursor.fetchone()[0]
        return job_id
    except Exception as e:
        print(e)
    finally:
        conn.close()

    return -1


def get_job_status(job_id: str, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cursor.execute("""SELECT status from nlp.nlp_job where nlp_job = %s""",
                       job_id)

        status = cursor.fetchone()[0]
        return status
    except Exception as e:
        print(e)
    finally:
        conn.close()

    return "UNKNOWN"
