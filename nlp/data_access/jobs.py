import psycopg2
import psycopg2.extras
import configparser
import json
import util
import sys
import traceback
from pymongo import MongoClient
from datetime import datetime, timezone

try:
    from .base_model import BaseModel
    from .results import phenotype_stats
except Exception as e:
    print(e)
    from base_model import BaseModel
    from results import phenotype_stats


STARTED = "STARTED"
COMPLETED = "COMPLETED"
IN_PROGRESS = "IN_PROGRESS"
FAILURE = "FAILURE"
WARNING = "WARNING"
KILLED = "KILLED"
STATS = "STATS"
PROPERTIES = "PROPERTIES"


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
        dt = datetime.now()
        cursor.execute("""
                INSERT INTO nlp.nlp_job (name, job_type, description, owner, status, pipeline_id, phenotype_id, 
                    date_started)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING nlp_job_id""",
                       (job.name, job.job_type, job.description, job.owner, job.status, job.pipeline_id,
                        job.phenotype_id, dt))

        job_id = cursor.fetchone()[0]

        cursor.execute("""
                INSERT INTO nlp.nlp_job_status (status, description, date_updated, nlp_job_id)
                VALUES (%s, 'Starting Job', %s, %s) RETURNING nlp_job_status_id""",
                       (job.status, dt, job_id))
        conn.commit()

        return job_id
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
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

        cursor.execute("""
            SELECT status, description, date_updated, nlp_job_status_id from nlp.nlp_job_status
            where nlp_job_id = %s order by date_updated
            """,
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
        traceback.print_exc(file=sys.stdout)
    finally:
        conn.close()

    return status_dict


def update_job_status(job_id: str, connection_string: str, updated_status: str, description: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    flag = -1 # To determine whether the update was successful or not
    dt = datetime.now()

    try:
        if not updated_status.startswith(PROPERTIES) and not updated_status.startswith(STATS):
            cursor.execute("""UPDATE nlp.nlp_job set status = %s where nlp_job_id = %s""", (updated_status, job_id))

        cursor.execute("""
                INSERT INTO nlp.nlp_job_status (status, description, date_updated, nlp_job_id)
                VALUES (%s, %s, %s, %s) RETURNING nlp_job_status_id""",
                       (updated_status, description, dt, job_id))

        if updated_status == COMPLETED or updated_status == FAILURE or updated_status == KILLED:
            cursor.execute("""UPDATE nlp.nlp_job set date_ended = %s where nlp_job_id = %s""", (dt, job_id))

        flag = 1
        conn.commit()

    except Exception as e:
        flag = -1
        traceback.print_exc(file=sys.stdout)
    finally:
        conn.close()

    return flag


def delete_job(job_id: str, connection_string: str):
    conn = psycopg2.connect(connection_string)
    client = MongoClient(util.mongo_host, util.mongo_port)

    cursor = conn.cursor()
    flag = -1 # To determine whether the update was successful or not

    try:
        cursor.execute("DELETE FROM nlp.nlp_job_status  WHERE nlp_job_id=" + job_id)
        cursor.execute("DELETE FROM nlp.nlp_job WHERE nlp_job_id=" + job_id)
        conn.commit()

        db = client[util.mongo_db]
        db.phenotype_results.remove({
            "job_id": int(job_id)
        })

        flag = 1
    except Exception as e:
        flag = -1
        traceback.print_exc(file=sys.stdout)
    finally:
        conn.close()
        client.close()

    return flag


def query_phenotype_jobs(status: str, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    jobs = list()

    try:
        if status == '' or status == 'ALL':
            cursor.execute("""select jb.*, pt.config, pt.nlpql, pt.name as phenotype_name from nlp.nlp_job as jb
                               INNER JOIN nlp.phenotype pt on pt.phenotype_id = jb.phenotype_id
                              where jb.job_type = 'PHENOTYPE'
                              order by jb.date_started DESC""")
        else:
            cursor.execute("""select jb.*, pt.config, pt.nlpql, pt.name as phenotype_name from nlp.nlp_job as jb
                             INNER JOIN nlp.phenotype pt on pt.phenotype_id = jb.phenotype_id
                            where jb.job_type = 'PHENOTYPE'
                            and jb.status = %s 
                            order by jb.date_started DESC""",
                           [status])
        rows = cursor.fetchall()
        for row in rows:
            name = row['phenotype_name']
            if not name or name.strip() == '':
                name = "Phenotype %s" % str(row['phenotype_id'])
                row['phenotype_name'] = name
            jobs.append(row)
        return jobs
    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
    finally:
        conn.close()

    return jobs


def query_phenotype_job_by_id(job_id: str, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    job = {}

    try:
        cursor.execute("""select jb.*, pt.config, pt.nlpql from nlp.nlp_job as jb
                         INNER JOIN nlp.phenotype pt on pt.phenotype_id = jb.phenotype_id
                        where jb.job_type = 'PHENOTYPE'
                        and jb.nlp_job_id = %s 
                        order by jb.date_started DESC""",
                       [job_id])
        rows = cursor.fetchall()
        for row in rows:
            name = row['name']
            if not name or name.strip() == '':
                name = "Phenotype %s" % str(row['phenotype_id'])
                row['name'] = name
            job = row
            break
        return job
    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
    finally:
        conn.close()

    return job


def get_job_performance(job_id: int, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    performance = {
        "status": "UNKNOWN",
        "total_time_as_seconds": 0.0,
        "total_time_as_minutes": 0.0,
        "total_time_as_hours": 0.0,
        "final_results": 0,
        "final_subjects": 0,
        "intermediate_results": 0,
        "intermediate_subjects": 0
    }

    try:
        cursor.execute("""SELECT status from nlp.nlp_job where nlp_job_id = %s""",
                       [job_id])

        status = cursor.fetchone()[0]
        performance["status"] = status

        cursor.execute("""
            SELECT status, description, date_updated, nlp_job_status_id from nlp.nlp_job_status
            where nlp_job_id = %s order by date_updated
            """,
                       [job_id])
        updates = cursor.fetchall()

        started = None
        ended = None
        counts_found = 0
        for row in updates:
            status_name = row[0]
            status_date = row[2]
            status_value = row[1]
            if not ended or status_date > ended:
                ended = status_date

            if status_name == 'STARTED':
                started = status_date
            elif status_name == 'STATS_FINAL_SUBJECTS':
                performance['final_subjects'] = status_value
                counts_found += 1
            elif status_name == 'STATS_FINAL_RESULTS':
                performance['final_results'] = status_value
                counts_found += 1
            elif status_name == 'STATS_INTERMEDIATE_SUBJECTS':
                performance['intermediate_subjects'] = status_value
                counts_found += 1
            elif status_name == 'STATS_INTERMEDIATE_RESULTS':
                performance['intermediate_results'] = status_value
                counts_found += 1

        if counts_found == 0:
            intermediate_stats = phenotype_stats(str(job_id), False)
            stats = phenotype_stats(str(job_id), True)

            performance['intermediate_subjects'] = intermediate_stats["subjects"]
            performance['intermediate_results'] = intermediate_stats["results"]

            performance['final_subjects'] = stats["subjects"]
            performance['final_results'] = stats["results"]

        if started and ended:
            runtime = ended - started
            performance['total_time_as_seconds'] = runtime.total_seconds()
            performance['total_time_as_minutes'] = performance['total_time_as_seconds']/60
            performance['total_time_as_hours'] = performance['total_time_as_minutes']/60
            print(runtime)
    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
    finally:
        conn.close()

    return performance


if __name__ == "__main__":
    conn_string = util.conn_string
    # status = get_job_status(117, conn_string)
    res = get_job_performance(200, conn_string)
    print(json.dumps(res, indent=4))


