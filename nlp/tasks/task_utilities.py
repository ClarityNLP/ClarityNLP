import luigi
from data_access import pipeline_config
from data_access import pipeline_config as config
import datetime
import util


def pipeline_mongo_writer(client, pipeline_id, pipeline_type, job, batch, p_config: pipeline_config.PipelineConfig,
                          doc, data_fields: dict):
    db = client[util.mongo_db]

    data_fields["pipeline_type"] = pipeline_type
    data_fields["pipeline_id"] = pipeline_id
    data_fields["job_id"] = job
    data_fields["batch"] = batch
    data_fields["owner"] = p_config.owner
    data_fields["nlpql_feature"] = p_config.name
    data_fields["inserted_date"] = datetime.datetime.now()
    data_fields["report_id"] = doc["report_id"]
    data_fields["subject"] = doc["subject"]
    data_fields["report_date"] = doc["report_date"]
    data_fields["concept_code"] = p_config.concept_code
    data_fields["phenotype_final"] = False

    inserted = config.insert_pipeline_results(p_config, db, data_fields)

    return inserted


