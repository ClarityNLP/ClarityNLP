import requests
import time
import sys
from subprocess import call
from os import listdir
from os.path import isfile, join
import time

max_workers = 1
max_jobs = 100
cur_job = 0

env_path = './synthetic_query_gen/notebooks/env_files'
evaluated_env_path = './synthetic_query_gen/notebooks/evaluated_env/'
target_env_path = './'
ip = '18.224.57.156'

url = 'http://' + ip + ':5000/'
nlpql_url = url + 'nlpql'
delete_url = url + 'delete_job/'


def get_active_workers():
    res = requests.get("http://" + ip + ":8082/api/task_list?data={%22status%22:%22RUNNING%22}")
    if res.status_code == 200:
        json_res = res.json()
        keys = (json_res['response'].keys())
        return len(keys)

    return 0


def run_nlpql(i, filename='query'):
    file = open('./synthetic_query_gen/notebooks/gen_nlpql/%s_%d.nlpql' % (filename, i), "r")
    nlpql = file.read()

    res = requests.post(nlpql_url, data=nlpql, headers={'content-type': 'text/plain'})
    if res.ok:
        print("Running job %d" % i)
        time.sleep(30)
    else:
        print('Failed to run job %d' % i)
        sys.exit(1)


def cleanup(job_id):
    res = requests.get(delete_url + str(job_id), data={})
    if res.ok:
        print('successfully deleted job ' + str(job_id))
    else:
        print('delete the job ' + str(job_id))


def job_runner(fname, jobs, current):
    for i in range(jobs):
        if i < current:
            pass
        else:
            print('Attempting job %d' % i)
            if get_active_workers() < max_workers:
                run_nlpql(i, filename=fname)
            else:
                while get_active_workers() >= max_workers:
                    print('At max workers for job %d sleeping for 60 secs...' % i)
                    time.sleep(60)
                run_nlpql(i, filename=fname)


if __name__ == "__main__":

    run_jobs = True
    if run_jobs:
        # files = sorted([f for f in listdir(env_path) if isfile(join(env_path, f))])
        # current_env = target_env_path + '/.env'
        # backup_env = target_env_path + '/.env.bak'
        # call(["cp", current_env, backup_env])
        # for file in files:
        #     print('running ' + file)
        #     sample_file = env_path + '/' + file
        #     call(['cp', sample_file, current_env])
        #     call(["docker-compose", "up", "-d", "--build"])
        #     print('sleeping for 3 minutes; running next')
        #     print('will evaluate the following files:')
        #     print(files)
        #     print('current file:')
        #     print(file)
        #     time.sleep(180)
        #     # job_runner('feature', 27, 0)
        #     job_runner('query', 100, 0)
        #     while get_active_workers() > 0:
        #         print('jobs still running wait to shut down docker')
        #         time.sleep(120)
        #     call(["mv", sample_file, evaluated_env_path])
        #     print('shutting down docker')
        #     call(["docker-compose", "down"])
        #     print('sleeping for a minute')
        #     time.sleep(60)
        # print('done; restoring backup')
        # call(["cp", backup_env, current_env])
        # call(["docker-compose", "up", "-d", "--build"])
        job_runner('query', 100, 0)
    else:
        startid = 295
        for n in range(startid, startid + 500):
            cleanup(n)
