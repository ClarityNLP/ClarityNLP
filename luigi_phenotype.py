import datetime

import luigi
from pymongo import MongoClient
from pymongo.errors import BulkWriteError

import data_access
import phenotype_helper
import util
from luigi_pipeline import PipelineTask
import sys
import traceback


class PhenotypeTask(luigi.Task):
    phenotype = luigi.IntParameter()
    job = luigi.IntParameter()
    owner = luigi.Parameter()
    client = MongoClient(util.mongo_host, util.mongo_port)

    def requires(self):
        tasks = list()
        pipeline_ids = data_access.query_pipeline_ids(int(self.phenotype), util.conn_string)
        print("getting ready to execute pipelines...")
        print(pipeline_ids)
        if len(pipeline_ids) > 0:
            for pipeline_id in pipeline_ids:
                pipeline_config = data_access.get_pipeline_config(pipeline_id, util.conn_string)
                tasks.append(PipelineTask(pipeline=pipeline_id, job=self.job, owner=self.owner,
                                          pipelinetype=pipeline_config.config_type))
        print(tasks)

        return tasks

    def run(self):
        print('dependencies done; run phenotype reconciliation')
        client = MongoClient(util.mongo_host, util.mongo_port)

        try:
            data_access.update_job_status(str(self.job), util.conn_string, data_access.IN_PROGRESS,
                                          "Finished Pipelines")

            phenotype = data_access.query_phenotype(int(self.phenotype), util.conn_string)
            print(phenotype)

            db = client[util.mongo_db]

            data_access.update_job_status(str(self.job), util.conn_string, data_access.IN_PROGRESS,
                                          "Filtering Results")

            with self.output().open('w') as outfile:
                phenotype_helper.write_phenotype_results(db, self.job, phenotype, self.phenotype, self.phenotype)
                data_access.update_job_status(str(self.job), util.conn_string, data_access.COMPLETED,
                                              "Job completed successfully")
                outfile.write("DONE!")
                outfile.write('\n')
        except BulkWriteError as bwe:
            print(bwe.details)
            data_access.update_job_status(str(self.job), util.conn_string, data_access.WARNING, str(bwe.details))
        except Exception as ex:
            traceback.print_exc(file=sys.stdout)
            data_access.update_job_status(str(self.job), util.conn_string, data_access.FAILURE, str(ex))
            print(ex)
        finally:
            client.close()

    def output(self):
        return luigi.LocalTarget("%s/phenotype_job%s_output.txt" % (util.tmp_dir, str(self.job)))


if __name__ == "__main__":
    owner = "tester"
    p_id = "2000"
    the_job_id = data_access.create_new_job(
        data_access.NlpJob(job_id=-1, name="Test Phenotype", description="Test Phenotype",
                           owner=owner, status=data_access.STARTED, date_ended=None,
                           phenotype_id=int(p_id), pipeline_id=-1, date_started=datetime.datetime.now(),
                           job_type='PHENOTYPE'), util.conn_string)
    luigi.run(['PhenotypeTask', '--phenotype', p_id, '--job', str(the_job_id), '--owner', 'tester'])
