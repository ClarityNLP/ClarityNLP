import psycopg2
import psycopg2.extras
import configparser
import json
import util
import sys
import traceback
from pymongo import MongoClient
from datetime import datetime, timezone
from claritynlp_logging import log, ERROR, DEBUG


try:
    from .base_model import BaseModel
    from .results import phenotype_stats
except Exception as e:
    log(e)
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


def get_job_status(job_id: int, connection_string: str, get_updates=False):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    status_dict = {
        "status": "UNKNOWN"
    }

    try:
        cursor.execute("""SELECT status from nlp.nlp_job where nlp_job_id = %s""",
                       [job_id])

        status = cursor.fetchone()[0]
        status_dict["status"] = status

        if get_updates:
            status_dict['updates'] = list()
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
    client = util.mongo_client()

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


def query_phenotype_jobs(status: str, connection_string: str, limit=100, skip=0):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    jobs = list()

    limit = str(limit)
    skip = str(skip)
    try:
        if status == '' or status == 'ALL':
            q = """select jb.*, pt.config, pt.nlpql, pt.name as phenotype_name from nlp.nlp_job as jb
                               INNER JOIN nlp.phenotype pt on pt.phenotype_id = jb.phenotype_id
                              where jb.job_type = 'PHENOTYPE'
                              order by jb.date_started DESC 
                              limit %s OFFSET %s"""
            # log(q)
            cursor.execute(q, [limit, skip])
        elif status == 'INCOMPLETE':
            q = """select jb.*, pt.config, pt.nlpql, pt.name as phenotype_name from nlp.nlp_job as jb
                             INNER JOIN nlp.phenotype pt on pt.phenotype_id = jb.phenotype_id
                            where jb.job_type = 'PHENOTYPE'
                            and (jb.status <> %s and jb.status <> %s and jb.status <> %s)
                            order by jb.date_started DESC 
                            limit %s OFFSET %s"""
            # log(q)
            cursor.execute(q, [COMPLETED, FAILURE, KILLED, limit, skip])
        else:
            q = """select jb.*, pt.config, pt.nlpql, pt.name as phenotype_name from nlp.nlp_job as jb
                             INNER JOIN nlp.phenotype pt on pt.phenotype_id = jb.phenotype_id
                            where jb.job_type = 'PHENOTYPE'
                            and jb.status = %s 
                            order by jb.date_started DESC 
                            limit %s OFFSET %s"""
            # log(q)
            cursor.execute(q, [status, limit, skip])

        rows = cursor.fetchall()

        for row in rows:
            name = row['phenotype_name']
            if not name or name.strip() == '':
                name = "Phenotype %s" % str(row['phenotype_id'])
                row['phenotype_name'] = name
            started = row['date_started']
            ended = row['date_ended']
            if started and ended:
                runtime = ended - started
                row['total_time_as_seconds'] = runtime.total_seconds()
                row['total_time_as_minutes'] = row['total_time_as_seconds'] / 60
                row['total_time_as_hours'] = row['total_time_as_minutes'] / 60
            else:
                row['total_time_as_seconds'] = 0.0
                row['total_time_as_minutes'] = 0.0
                row['total_time_as_hours'] = 0.0
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


def get_job_performance(job_ids: list, connection_string: str):
    if not job_ids or len(job_ids) == 0:
        return dict()

    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    metrics = dict()

    try:
        in_clause = ''
        for i in job_ids:
            if len(in_clause) > 0:
                in_clause += ', '
            in_clause += '%s'
        cursor.execute("""
            SELECT status, nlp_job_id from nlp.nlp_job 
            where nlp_job_id in ({})
            """.format(in_clause),
                       job_ids)
        status = None
        job_id = -1
        statuses = cursor.fetchall()
        for s in statuses:
            status = s[0]
            job_id = s[1]

            metrics[job_id] = {
                "status": status,
                "final_results": 0,
                "final_subjects": 0,
                "intermediate_results": 0,
                "intermediate_subjects": 0,
                "counts_found": 0
            }

        cursor.execute("""
            SELECT status, description, date_updated, nlp_job_id from nlp.nlp_job_status
            where nlp_job_id in  ({}) 
            order by date_updated
            """.format(in_clause),
                       job_ids)
        updates = cursor.fetchall()

        for row in updates:
            status_name = row[0]
            status_date = row[2]
            status_value = row[1]
            job_id = row[3]

            performance = metrics[job_id]
            counts_found = performance.get('counts_found', 0)

            if status_name == 'STATS_FINAL_SUBJECTS':
                performance['final_subjects'] = status_value
                counts_found += int(status_value)
            elif status_name == 'STATS_FINAL_RESULTS':
                performance['final_results'] = status_value
                counts_found += int(status_value)
            elif status_name == 'STATS_INTERMEDIATE_SUBJECTS':
                performance['intermediate_subjects'] = status_value
            elif status_name == 'STATS_INTERMEDIATE_RESULTS':
                performance['intermediate_results'] = status_value

            performance['counts_found'] = counts_found
            metrics[job_id] = performance

        for k in metrics.keys():
            performance = metrics[k]
            counts_found = performance.get('counts_found', 0)
            if counts_found == 0 and status == COMPLETED:
                final_subjects = util.get_from_redis_cache('final_subjects_{}'.format(k))
                final_results = util.get_from_redis_cache('final_results{}'.format(k))
                if final_results and final_subjects:
                    performance['final_subjects'] = final_subjects
                    performance['final_results'] = final_results
                else:
                    stats = phenotype_stats(str(job_id), True)

                    performance['final_subjects'] = stats["subjects"]
                    performance['final_results'] = stats["results"]

                    util.write_to_redis_cache('final_subjects_{}'.format(k), stats["subjects"])
                    util.write_to_redis_cache('final_results_{}'.format(k), stats["results"])

                int_subjects = util.get_from_redis_cache('intermediate_subjects_{}'.format(k))
                int_results = util.get_from_redis_cache('intermediate_results{}'.format(k))
                if int_subjects and int_results:
                    performance['intermediate_subjects'] = int_subjects
                    performance['intermediate_results'] = int_results
                else:
                    intermediate_stats = phenotype_stats(str(job_id), False)

                    performance['intermediate_subjects'] = intermediate_stats["subjects"]
                    performance['intermediate_results'] = intermediate_stats["results"]

                    util.write_to_redis_cache('intermediate_subjects_{}'.format(k), intermediate_stats["subjects"])
                    util.write_to_redis_cache('intermediate_results_{}'.format(k), intermediate_stats["results"])

            if 'counts_found' in performance:
                del performance['counts_found']
            metrics[job_id] = performance
    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
    finally:
        conn.close()

    return metrics


if __name__ == "__main__":
    # conn_string = util.conn_string
    # # status = get_job_status(117, conn_string)
    # res = get_job_performance(200, conn_string)
    # log(json.dumps(res, indent=4))
    log("jobs main")


