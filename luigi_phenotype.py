import luigi
from luigi_pipeline import PipelineTask
import data_access
import util
import pandas as pd
import numpy as np
import datetime
from pymongo import MongoClient
from functools import reduce



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
                # TODO logic
                if phenotype.operations:
                    cursor = db.pipeline_results.find({"job_id": int(self.job)})
                    df = pd.DataFrame(list(cursor))

                    for c in phenotype.operations:
                        operation_name = c['name']

                        if phenotype.context == 'Document':
                            on = 'report_id'
                        else:
                            on = 'subject'
                        col_list = ["feature_id", "feature_name", "feature_date", "context_id"]

                        if c['final']:
                            if 'data_entities' in c:
                                action = c['action']
                                data_entities = c['data_entities']

                                dfs = []
                                if action == 'AND' or action == 'OR' or action == 'NOT':
                                    if action == 'OR':
                                        how = "outer"
                                    elif action == 'AND':
                                        how = "inner"
                                    else:
                                        how = "left"

                                    for de in data_entities:
                                        new_df = df.loc[df['nlpql_feature'] == de]
                                        # new_df['feature_id'] = new_df['_id']
                                        # new_df['feature_name'] = new_df['nlpql_feature']
                                        # new_df['context_id'] = new_df[on]
                                        # new_df['feature_date'] = new_df['report_date']

                                        # TODO fix copy logic
                                        
                                        new_df = new_df[col_list]
                                        dfs.append(new_df)

                                    if len(dfs) > 0:
                                        ret = reduce(lambda x, y: pd.merge(x, y, on=on, how=how), dfs)
                                        ret['job_id'] = self.job
                                        ret['phenotype_id'] = self.phenotype
                                        ret['owner'] = self.owner
                                        ret['job_date'] = datetime.datetime.now()
                                        ret['context_type'] = on
                                        ret['raw_definition_text'] = c['raw_text']
                                        ret['result_name'] = operation_name

                                        db.phenotype_results.insert_many(ret.to_dict('records'))

                        else:
                            print('nothing to do for ' + operation_name)

                outfile.write("DONE!")
                outfile.write('\n')
        except Exception as ex:
            data_access.update_job_status(str(self.job), util.conn_string, data_access.FAILURE, str(ex))
            print(ex)
        finally:
            client.close()
        print("TODO")

    def output(self):
        return luigi.LocalTarget("%s/phenotype_job%s_output.txt" % (util.tmp_dir, str(self.job)))


if __name__ == "__main__":
    owner = "tester"
    p_id = "12"
    the_job_id = data_access.create_new_job(data_access.NlpJob(job_id=-1, name="Test Phenotype", description="Test Phenotype",
                                             owner=owner, status=data_access.STARTED, date_ended=None,
                                             phenotype_id=int(p_id), pipeline_id=-1, date_started=datetime.datetime.now(),
                                             job_type='PHENOTYPE'), util.conn_string)
    luigi.run(['PhenotypeTask', '--phenotype', p_id, '--job', str(the_job_id), '--owner', 'tester'])
