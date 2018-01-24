import glob
import util


def job_results(prefix: str, job: str):
    result_dir = "%s/%s_job%s_*.txt" % (util.tmp_dir, prefix, job)
    files = glob.glob(result_dir)

    res = ''
    for matched_file in files:
        with open(matched_file) as f:
            res = res + "\n" + f.read()
    return res
