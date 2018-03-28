import luigi
from luigi_pipeline import PipelineTask
import data_access
import util
from pymongo import MongoClient


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
            with self.output().open('w') as outfile:
                # TODO logic
                outfile.write("TODO")
                outfile.write('\n')
        except Exception as ex:
            data_access.update_job_status(str(self.job), util.conn_string, data_access.FAILURE, str(ex))
            print(ex)
        finally:
            client.close()
        print("TODO")

    def output(self):
        return luigi.LocalTarget("%s/phenotype_job%s_output.txt" % (util.tmp_dir, str(self.job)))
