import requests
import time
import sys

max_workers = 10
max_jobs = 100
cur_job = 2
url = 'http://18.220.133.76:5000/'
nlpql_url = url + 'nlpql'


def get_active_workers():
    res = requests.get("http://18.220.133.76:8082/api/task_list?data={%22status%22:%22RUNNING%22}")
    if res.status_code == 200:
        json_res = res.json()
        keys = (json_res['response'].keys())
        return len(keys)

    return 0


def run_nlpql(i):
    file = open('gen_nlpql/query_%d.nlpql' % i, "r")
    nlpql = file.read()

    res = requests.post(nlpql_url, data=nlpql, headers={'content-type': 'text/plain'})
    if res.ok:
        print("Running job %d" % i)
        time.sleep(300)
    else:
        print('Failed to run job')
        sys.exit(1)


if __name__ == "__main__":

    for i in range(max_jobs):
        if i < cur_job:
            pass
        else:
            if get_active_workers() < max_workers:
                run_nlpql(i)
            else:
                while get_active_workers() >= max_workers:
                    print('At max workers sleeping...')
                    time.sleep(60)
                run_nlpql(i)
