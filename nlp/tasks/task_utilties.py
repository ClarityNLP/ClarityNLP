import luigi
from data_access import pipeline_config
from data_access import pipeline_config as config
import datetime
import util


# Support for <3.5
def merge_objects(x, y):
    z = x.copy()
    z.update(y)
    return z


def pipeline_mongo_writer(client, pipeline_id, pipeline_type, job, batch, p_config: pipeline_config.PipelineConfig,
                          doc, data_fields: dict):
    db = client[util.mongo_db]

    standard_obj = {
        "pipeline_type": pipeline_type,
        "pipeline_id": pipeline_id,
        "job_id": job,
        "batch": batch,
        "owner": p_config.owner,
        "nlpql_feature": p_config.name,
        "inserted_date": datetime.datetime.now(),
        "report_id": doc["report_id"],
        "subject": doc["subject"],
        "report_date": doc["report_date"],
        "concept_code": p_config.concept_code,
        "phenotype_final": False
    }

    obj = merge_objects(standard_obj, data_fields)

    inserted = config.insert_pipeline_results(p_config, db, obj)

    return inserted


def term_finder_mongo_writer(term):
    obj = {
        "sentence": term.sentence,
        "section": term.section,
        "term": term.term,
        "start": term.start,
        "end": term.end,
        "negation": term.negex,
        "temporality": term.temporality,
        "experiencer": term.experiencer
    }