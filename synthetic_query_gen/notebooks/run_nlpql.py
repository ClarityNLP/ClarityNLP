import requests
import time
import sys

max_workers = 5
max_jobs = 100
cur_job = 0

url = 'http://18.220.133.76:5000/'
nlpql_url = url + 'nlpql'
delete_url = url + 'delete_job/'


def get_active_workers():
    res = requests.get("http://18.220.133.76:8082/api/task_list?data={%22status%22:%22RUNNING%22}")
    if res.status_code == 200:
        json_res = res.json()
        keys = (json_res['response'].keys())
        return len(keys)

    return 0


def run_nlpql(i, filename='query'):
    file = open('gen_nlpql/%s_%d.nlpql' % (filename, i), "r")
    nlpql = file.read()

    res = requests.post(nlpql_url, data=nlpql, headers={'content-type': 'text/plain'})
    if res.ok:
        print("Running job %d" % i)
        time.sleep(60)
    else:
        print('Failed to run job %d' % i)
        sys.exit(1)


def cleanup(job_id):
    res = requests.get(delete_url + str(job_id), data={})
    if res.ok:
        print('successfully deleted job ' + str(job_id))
    else:
        print('delete the job ' + str(job_id))


if __name__ == "__main__":

    run_jobs = True
    max_jobs = 27
    cur_job = 1
    filename = 'feature'
    if run_jobs:
        for i in range(max_jobs):
            if i < cur_job:
                pass
            else:
                print('Attempting job %d' % i)
                if get_active_workers() < max_workers:
                    run_nlpql(i, filename=filename)
                else:
                    while get_active_workers() >= max_workers:
                        print('At max workers for job %d sleeping for 30 secs...' % i)
                        time.sleep(30)
                    run_nlpql(i, filename=filename)
    else:
        startid = 742
        for i in range(startid, startid + 100):
            cleanup(i)
