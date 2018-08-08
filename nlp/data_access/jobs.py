import psycopg2
import psycopg2.extras
import configparser
import json
import util
try:
    from .base_model import BaseModel
except Exception as e:
    print(e)
    from base_model import BaseModel


STARTED = "STARTED"
COMPLETED = "COMPLETED"
IN_PROGRESS = "IN_PROGRESS"
FAILURE = "FAILURE"
WARNING = "WARNING"


class NlpJob(BaseModel):

    description = ''
    date_ended = None

    def __init__(self, name, description, owner, job_id, pipeline_id, phenotype_id, status, date_started, date_ended, job_type):
        self.name = name
        self.description = description
        self.owner = owner
        self.job_id = job_id
        self.pipeline_id = pipeline_id
        self.phenotype_id = phenotype_id
        self.status = status
        self.date_started = date_started
        self.date_ended = date_ended
        self.job_type = job_type


def create_new_job(job: NlpJob, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    try:
        cursor.execute("""
                INSERT INTO nlp.nlp_job (name, job_type, description, owner, status, pipeline_id, phenotype_id, date_started)
                VALUES (%s, %s, %s, %s, %s, %s, %s, current_timestamp) RETURNING nlp_job_id""",
                       (job.name, job.job_type, job.description, job.owner, job.status, job.pipeline_id, job.phenotype_id))

        job_id = cursor.fetchone()[0]

        cursor.execute("""
                INSERT INTO nlp.nlp_job_status (status, description, date_updated, nlp_job_id)
                VALUES (%s, 'Starting Job', current_timestamp, %s) RETURNING nlp_job_status_id""",
                       (job.status, job_id))
        conn.commit()

        return job_id
    except Exception as e:
        print(e)
    finally:
        conn.close()

    return -1


def get_job_status(job_id: int, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    status_dict = {
        "status": "UNKNOWN",
        "updates": list()
    }

    try:
        cursor.execute("""SELECT status from nlp.nlp_job where nlp_job_id = %s""",
                       [job_id])

        status = cursor.fetchone()[0]
        status_dict["status"] = status

        cursor.execute("""SELECT status, description, date_updated, nlp_job_status_id from nlp.nlp_job_status where nlp_job_id = %s order by date_updated""",
                       [job_id])
        updates = cursor.fetchall()
        for row in updates:
            udict = dict()
            udict["nlp_job_status_id"] = row[3]
            udict["date_updated"] = (row[2]).strftime("%Y-%m-%d %H:%M:%S")
            udict["status"] = row[0]
            udict["description"] = row[1]
            status_dict["updates"].append(udict)

        return status_dict
    except Exception as ex:
        print(ex)
    finally:
        conn.close()

    return status_dict


def update_job_status(job_id: str, connection_string: str, updated_status: str, description: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    flag = -1 # To determine whether the update was successful or not

    try:
        cursor.execute("""UPDATE nlp.nlp_job set status = %s where nlp_job_id = %s""", (updated_status, job_id))

        cursor.execute("""
                INSERT INTO nlp.nlp_job_status (status, description, date_updated, nlp_job_id)
                VALUES (%s, %s, current_timestamp, %s) RETURNING nlp_job_status_id""",
                       (updated_status, description, job_id))
        flag = 1
        conn.commit()

    except Exception as e:
        flag = -1
        print(e)
    finally:
        conn.close()

    return flag


def query_phenotype_jobs(status: str, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    jobs = list()

    try:
        cursor.execute("""select jb.*, pt.nlpql from nlp.nlp_job as jb
                         INNER JOIN nlp.phenotype pt on pt.phenotype_id = jb.phenotype_id
                        where jb.job_type = 'PHENOTYPE'
                        and jb.status = %s""",
                       [status])
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        return rows
    except Exception as ex:
        print(ex)
    finally:
        conn.close()

    return jobs


if __name__ == "__main__":
    conn_string = util.conn_string
    status = get_job_status(117, conn_string)
    print(json.dumps(status, indent=4))
