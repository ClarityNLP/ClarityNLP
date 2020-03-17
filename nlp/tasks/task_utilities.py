import datetime
import json
import sys
import traceback

import luigi
from cachetools import LRUCache, cached, keys
from pymongo import MongoClient

import util
from algorithms import segmentation
from algorithms.sec_tag import *
from data_access import base_model
from data_access import jobs
from data_access import pipeline_config
from data_access import pipeline_config as config
from data_access import solr_data
from claritynlp_logging import log, ERROR, DEBUG
from xml.sax import saxutils as su

sentences_key = "sentence_attrs"
section_names_key = "section_name_attrs"
section_text_key = "section_text_attrs"
doc_fields = ['report_id', 'subject', 'report_date', 'report_type', 'source', 'solr_id']
pipeline_cache = LRUCache(maxsize=5000)
document_cache = LRUCache(maxsize=5000)
init_cache = LRUCache(maxsize=1000)
segment = segmentation.Segmentation()


@cached(document_cache)
def _get_document_by_id(document_id):
    util.add_cache_compute_count()
    return solr_data.query_doc_by_id(document_id, solr_url=util.solr_url)


def get_document_by_id(document_id):
    doc = None

    if util.use_redis_caching == "true":
        util.add_cache_query_count()
        txt = util.get_from_redis_cache("doc:" + document_id)
        if not txt:
            util.add_cache_compute_count()
            doc = solr_data.query_doc_by_id(document_id, solr_url=util.solr_url)
            util.write_to_redis_cache("doc:" + document_id, json.dumps(doc))
        else:
            doc = json.loads(txt)
    elif util.use_memory_caching == "true":
        util.add_cache_query_count()
        doc = _get_document_by_id(document_id)

    if not doc:
        return solr_data.query_doc_by_id(document_id, solr_url=util.solr_url)
    else:
        return doc


def document_sections(doc):
    if util.use_precomputed_segmentation == "true" and section_names_key in doc and len(doc[section_names_key]) > 0:
        return doc[section_names_key], doc[section_text_key]
    else:
        txt = document_text(doc)
        section_headers, section_texts = [UNKNOWN], [txt]
        try:
            section_headers, section_texts = sec_tag_process(txt)
        except Exception as e:
            log(e)
        names = [x.concept for x in section_headers]
        return names, section_texts


def document_sentences(doc):
    if util.use_precomputed_segmentation == "true" and sentences_key in doc and len(doc[sentences_key]) > 0:
        return doc[sentences_key]
    else:
        txt = document_text(doc)
        sentence_list = segment.parse_sentences(txt)
        return sentence_list


def document_text(doc, clean=False):
    if doc and util.solr_text_field in doc:
        t = doc.get(util.solr_text_field)
        if type(t) == str:
            txt_val = t
        elif type(t) == list:
            txt_val = ' '.join(t)
        else:
            txt_val = str(t)
        txt_val = su.unescape(txt_val)
        if clean:
            return txt_val.encode("ascii", errors="ignore").decode()
        else:
            return txt_val
    else:
        return ''


def get_config_boolean(pipeline_config, key, default=False):
    if key in pipeline_config.custom_arguments:
        try:
            val = bool(pipeline_config.custom_arguments[key])
        except Exception as ex:
            val = default
        return val
    return default


def get_config_integer(pipeline_config, key, default=-1):
    if key in pipeline_config.custom_arguments:
        try:
            val = int(pipeline_config.custom_arguments[key])
        except Exception as ex:
            val = default
        return val
    return default


def get_config_string(pipeline_config, key, default=''):
    if key in pipeline_config.custom_arguments:
        try:
            val = str(pipeline_config.custom_arguments[key])
        except Exception as ex:
            val = default
        return val
    return default


def pipeline_mongo_writer(client, pipeline_id, pipeline_type, job, batch, p_config: pipeline_config.PipelineConfig,
                          doc, data_fields: dict, prefix: str = '', phenotype_final: bool = False):
    db = client[util.mongo_db]

    if not data_fields:
        log('must have additional data fields', ERROR)
        return None

    if not p_config:
        log('must have pipeline config', ERROR)
        return None

    # log('writing results...', DEBUG)
    data_fields["pipeline_type"] = pipeline_type
    data_fields["pipeline_id"] = int(pipeline_id)
    data_fields["job_id"] = int(job)
    data_fields["batch"] = batch
    data_fields["owner"] = p_config.owner
    data_fields["nlpql_feature"] = (prefix + p_config.name)
    data_fields["inserted_date"] = datetime.datetime.now()
    data_fields["concept_code"] = p_config.concept_code
    data_fields["concept_code_system"] = p_config.concept_code_system
    data_fields["phenotype_final"] = (phenotype_final or p_config.final)
    data_fields["display_name"] = p_config.display_name

    if doc:
        data_fields["report_id"] = doc[util.solr_report_id_field]
        data_fields["subject"] = doc[util.solr_subject_field]
        data_fields["report_date"] = doc[util.solr_report_date_field]
        data_fields["report_type"] = doc[util.solr_report_type_field]
        data_fields["source"] = doc[util.solr_source_field]
        data_fields["solr_id"] = doc[util.solr_id_field]
    else:
        for df in doc_fields:
            if df not in data_fields:
                data_fields[df] = ''

    highlight_fields = ['term', 'text', 'value', 'units', 'word', 'highlight', 'highlights']
    if "result_display" not in data_fields:
        s = data_fields.get('start')
        e = data_fields.get('end')
        if not s:
            s = 0
        if not e:
            e = 0

        highlights = []
        for h in highlight_fields:
            txt = data_fields.get(h, '')
            # the field might not be a string, so check
            if isinstance(txt, str) and len(txt) > 0:
                highlights.append(txt)
                break
            elif isinstance(txt, int):
                highlights.append(str(txt))
                break
            elif isinstance(txt, float):
                highlights.append(str(txt))
                break
        data_fields["result_display"] = {
            "date": data_fields.get('report_date'),
            "result_content": data_fields.get('sentence'),
            "highlights": highlights,
            "sentence": data_fields.get('sentence'),
            'start': [s],
            'end': [e]
        }
    else:
        display = data_fields.get('result_display')
        highlights = display.get("highlights", list())
        if len(highlights) == 0:
            highlights = []
            for h in highlight_fields:
                txt = data_fields.get(h, '')
                if len(txt) > 0:
                    highlights.append(txt)
                    break
            data_fields['result_display']['highlights'] = highlights

    inserted = config.insert_pipeline_results(p_config, db, data_fields)
    log('(job={}; pipeline={}) inserted into mongodb {}'.format(job, pipeline_id, repr(inserted.inserted_id)), DEBUG)

    return inserted


class BaseCollector(base_model.BaseModel):
    collector_name = "ClarityNLPLuigiCollector"

    def run(self, pipeline_id, job, owner, pipeline_type, p_config):
        client = util.mongo_client()
        db = client[util.mongo_db]

        try:
            jobs.update_job_status(job, util.conn_string, jobs.IN_PROGRESS, "Running Collector")
            self.run_custom_task(pipeline_id, job, owner, pipeline_type, p_config, client, db)
        except Exception as ex:
            jobs.update_job_status(job, util.conn_string, jobs.WARNING, ''.join(traceback.format_stack()))
            log(ex, ERROR)
        finally:
            client.close()

    def run_custom_task(self, pipeline_id, job, owner, pipeline_type, p_config, client, db):
        log('please implement run_custom_task')

    def custom_cleanup(self, pipeline_id, job, owner, pipeline_type, p_config, client, db):
        log('custom cleanup')

    def cleanup(self, pipeline_id, job, owner, pipeline_type, p_config):
        client = util.mongo_client()
        db = client[util.mongo_db]

        try:
            jobs.update_job_status(job, util.conn_string, jobs.IN_PROGRESS, "Running Collector Cleanup")
            self.custom_cleanup(pipeline_id, job, owner, pipeline_type, p_config, client, db)
        except Exception as ex:
            jobs.update_job_status(job, util.conn_string, jobs.WARNING, ''.join(traceback.format_stack()))
            log(ex, ERROR)
        finally:
            client.close()


class BaseTask(luigi.Task):
    pipeline = luigi.IntParameter()
    job = luigi.IntParameter()
    start = luigi.IntParameter()
    solr_query = luigi.Parameter()
    batch = luigi.IntParameter()
    parallel_task = True
    task_name = "ClarityNLPLuigiTask"
    docs = list()
    pipeline_config = config.PipelineConfig('', '')
    segment = segmentation.Segmentation()

    def run(self):
        task_family_name = str(self.task_family)
        if self.task_name == "ClarityNLPLuigiTask":
            self.task_name = task_family_name
        client = util.mongo_client()

        try:
            with self.output().open('w') as temp_file:
                temp_file.write("start writing custom task")
                jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS, "Running Batch %s" %
                                       self.batch)

                self.pipeline_config = config.get_pipeline_config(self.pipeline, util.conn_string)
                jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS, "Running Solr query")
                self.docs = solr_data.query(self.solr_query, rows=util.row_count, start=self.start,
                                            solr_url=util.solr_url,
                                            tags=self.pipeline_config.report_tags, mapper_inst=util.report_mapper_inst,
                                            mapper_url=util.report_mapper_url, mapper_key=util.report_mapper_key,
                                            types=self.pipeline_config.report_types,
                                            sources=self.pipeline_config.sources,
                                            filter_query=self.pipeline_config.filter_query,
                                            cohort_ids=self.pipeline_config.cohort,
                                            job_results_filters=self.pipeline_config.job_results)

                for d in self.docs:
                    doc_id = d[util.solr_report_id_field]
                    if util.use_memory_caching == "true":
                        k = keys.hashkey(doc_id)
                        document_cache[k] = d
                    if util.use_redis_caching == "true":
                        util.write_to_redis_cache("doc:" + doc_id, json.dumps(d))
                jobs.update_job_status(str(self.job), util.conn_string, jobs.IN_PROGRESS,
                                       "Running %s main task" % self.task_name)
                self.run_custom_task(temp_file, client)
                temp_file.write("Done writing custom task!")

            self.docs = list()
        except Exception as ex:
            jobs.update_job_status(str(self.job), util.conn_string, jobs.WARNING, ''.join(traceback.format_stack()))
            log(ex, ERROR)
        finally:
            client.close()

    def output(self):
        return luigi.LocalTarget("%s/pipeline_job%s_%s_batch%s.txt" % (util.tmp_dir, str(self.job), self.task_name,
                                                                       str(self.start)))

    def set_name(self, name):
        self.task_name = name

    def write_result_data(self, temp_file, mongo_client, doc, data: dict, prefix: str = ''):
        inserted = pipeline_mongo_writer(mongo_client, self.pipeline, self.task_name, self.job, self.batch,
                                         self.pipeline_config, doc, data, prefix=prefix)
        if temp_file is not None:
            temp_file.write(str(inserted))
            temp_file.write('\n')
        return inserted

    def write_multiple_result_data(self, temp_file, mongo_client, doc, data: list, prefix: str = ''):
        ids = list()
        for d in data:
            inserted = pipeline_mongo_writer(mongo_client, self.pipeline, self.task_name, self.job, self.batch,
                                             self.pipeline_config, doc, d, prefix=prefix)
            ids.append(inserted)
            if temp_file is not None:
                temp_file.write(str(inserted))
                temp_file.write('\n')

        return ids

    def write_log_data(self, job_status, status_message):
        jobs.update_job_status(str(self.job), util.conn_string, job_status, status_message)

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        log("Implement your custom functionality here ")

    def get_document_text(self, doc, clean=True):
        return document_text(doc, clean=clean)

    def get_boolean(self, key, default=False):
        return get_config_boolean(self.pipeline_config, key, default=default)

    def get_integer(self, key, default=-1):
        return get_config_integer(self.pipeline_config, key, default=default)

    def get_string(self, key, default=''):
        return get_config_string(self.pipeline_config, key, default=default)

    def get_document_sentences(self, doc):
        return document_sentences(doc)

    def get_document_sections(self, doc):
        names, section_texts = document_sections(doc)
        return names, section_texts
