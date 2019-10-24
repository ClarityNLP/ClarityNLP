import configparser
from claritynlp_logging import log, ERROR
from os import getenv, environ, path

import pymongo
import redis
from pymongo import MongoClient

SCRIPT_DIR = path.dirname(__file__)
config = configparser.RawConfigParser()
config.read(path.join(SCRIPT_DIR, 'project.cfg'))
properties = dict()
delimiter = ','
quote_character = '"'
EXPIRE_TIME_SECONDS = 604800


def read_property(env_name, config_tuple, default='', key_name=None):
    if not key_name:
        key_name = env_name
    global properties
    property_name = default
    try:
        if getenv(env_name):
            property_name = environ.get(env_name)
        else:
            property_name = config.get(config_tuple[0], config_tuple[1])
        if not property_name:
            property_name = default
        if len(key_name) > 0 and 'PASSWORD' not in key_name and 'KEY' not in key_name and 'USERNAME' not in key_name:
            properties[key_name] = property_name
    except Exception as ex:
        log(repr(ex), ERROR)
        properties[key_name] = default
    return property_name


def read_boolean_property(prop, default=False):
    try:
        if isinstance(prop, bool):
            val = prop
        else:
            strval = str(prop).lower()
            if strval == '1' or strval == 'true' or strval == 't':
                val = True
            elif strval == '0' or strval == 'false' or strval == 'f':
                val = False
            else:
                val = default
    except Exception as ex:
        val = default
    return val


solr_url = read_property('NLP_SOLR_URL', ('solr', 'url'))
conn_string = "host='%s' dbname='%s' user='%s' password='%s' port=%s" % (
    read_property('NLP_PG_HOSTNAME', ('pg', 'host')),
    read_property('NLP_PG_DATABASE', ('pg', 'dbname')),
    read_property('NLP_PG_USER', ('pg', 'user')),
    read_property('NLP_PG_PASSWORD', ('pg', 'password')),
    str(read_property('NLP_PG_CONTAINER_PORT', ('pg', 'port'))))
mongo_host = read_property('NLP_MONGO_HOSTNAME', ('mongo', 'host'))
mongo_port = int(read_property('NLP_MONGO_CONTAINER_PORT', ('mongo', 'port')))
mongo_db = read_property('NLP_MONGO_DATABASE', ('mongo', 'db'))
mongo_working_index = read_property(
    'NLP_MONGO_WORKING_INDEX', ('mongo', 'working_index'))
mongo_working_collection = read_property(
    'NLP_MONGO_WORKING_COLLECTION', ('mongo', 'working_collection'))
mongo_username = read_property('NLP_MONGO_USERNAME', ('mongo', 'username'))
mongo_password = read_property('NLP_MONGO_PASSWORD', ('mongo', 'password'))
tmp_dir = read_property('NLP_API_TMP_DIR', ('tmp', 'dir'))
log_dir = read_property('NLP_API_LOG_DIR', ('log', 'dir'))
luigi_scheduler = read_property('LUIGI_SCHEDULER_URL', ('luigi', 'scheduler'))
luigi_url = read_property('SCHEDULER_VIRTUAL_HOST', ('luigi', 'url'))
luigi_workers = read_property('LUIGI_WORKERS', ('luigi', 'workers'), default='5')
results_viewer_url = read_property(
    'RESULTS_CLIENT_URL', ('results_client', 'url'))
main_url = read_property(
    'IDENTITY_AND_ACCESS_PROXY_VIRTUAL_HOST', ('main', 'url'))
row_count = read_property('BATCH_SIZE', ('solr', 'batch_size'), default='10')
report_mapper_url = read_property('MAPPER_API_URL', ('report_mapper', 'url'))
report_mapper_key = read_property('MAPPER_API_KEY', ('report_mapper', 'key'))
report_mapper_inst = read_property(
    'MAPPER_API_INSTITUTE', ('report_mapper', 'institute'))
ohdsi_url = read_property('OHDSI_WEBAPI_URL', ('ohdsi', 'webapi'))
debug_mode = read_property('NLP_API_DEBUG_MODE', ('local', 'debug'))
azure_key = read_property('NLP_AZURE_KEY', ('apis', 'azure_key'))
solr_text_field = read_property('SOLR_TEXT_FIELD', ('solr', 'text_field'))
solr_id_field = read_property('SOLR_ID_FIELD', ('solr', 'id_field'))
solr_report_id_field = read_property(
    'SOLR_REPORT_ID_FIELD', ('solr', 'report_id_field'))
solr_source_field = read_property(
    'SOLR_SOURCE_FIELD', ('solr', 'source_field'))
solr_report_date_field = read_property(
    'SOLR_REPORT_DATE_FIELD', ('solr', 'date_field'))
solr_subject_field = read_property(
    'SOLR_SUBJECT_FIELD', ('solr', 'subject_field'))
solr_report_type_field = read_property(
    'SOLR_REPORT_TYPE_FIELD', ('solr', 'type_field'))
expression_evaluator = read_property(
    'NLP_EXPRESSION_EVALUATOR', ('local', 'evaluator'))
redis_hostname = read_property('REDIS_HOSTNAME', ('redis', 'hostname'))
redis_host_port = read_property('REDIS_HOST_PORT', ('redis', 'host_port'))
redis_container_port = read_property(
    'REDIS_CONTAINER_PORT', ('redis', 'container_port'))
use_memory_caching = read_property('USE_MEMORY_CACHING', ('optimizations', 'use_memory_cache'),
                                   default='true')
use_precomputed_segmentation = read_property('USE_PRECOMPUTED_SEGMENTATION',
                                             ('optimizations',
                                              'use_precomputed_segmentation'),
                                             default='true')
use_reordered_nlpql = read_property('USE_REORDERED_NLPQL',
                                    ('optimizations', 'use_reordered_nlpql'),
                                    default='false')

use_redis_caching = read_property('USE_REDIS_CACHING',
                                  ('optimizations', 'use_redis_caching'),
                                  default='true')

cql_eval_url = read_property('FHIR_CQL_EVAL_URL', ('local', 'cql_eval_url'), key_name='cql_eval_url')
fhir_data_service_uri = read_property('FHIR_DATA_SERVICE_URI', ('local', 'fhir_data_service_uri'),
                                      key_name='fhir_data_service_uri')
fhir_auth_type = read_property('FHIR_AUTH_TYPE', ('local', 'fhir_auth_type'), key_name='fhir_auth_type')
fhir_auth_token = read_property('FHIR_AUTH_TOKEN', ('local', 'fhir_auth_token'), key_name='fhir_auth_token')
fhir_terminology_service_uri = read_property('FHIR_TERMINOLOGY_SERVICE_URI', ('local', 'fhir_terminology_service_uri'),
                                             key_name='fhir_terminology_service_uri')
fhir_terminology_service_endpoint = read_property('FHIR_TERMINOLOGY_SERVICE_ENDPOINT',
                                                  ('local', 'fhir_terminology_service_endpoint'),
                                                  key_name='fhir_terminology_service_endpoint')
fhir_terminology_user_name = read_property('FHIR_TERMINOLOGY_USER_NAME', ('local', 'fhir_terminology_user'),
                                           key_name='fhir_terminology_user_name')
fhir_terminology_user_password = read_property('FHIR_TERMINOLOGY_USER_PASSWORD', ('local', 'fhir_terminology_password'),
                                               key_name='fhir_terminology_user_password')

# TODO this out a bit more, this is more for experimental evaluation
cache_counts = {
    'compute': 0,
    'query': 0
}

try:
    redis_conn = redis.Redis(
        host=redis_hostname, port=redis_host_port, decode_responses=True)
    redis_conn.set('clarity_cache_compute', 0)
    redis_conn.set('clarity_cache_query', 0)
except Exception as ex:
    redis_conn = None


def write_to_redis_cache(key, value):
    if redis_conn:
        redis_conn.set(key, value)
        redis_conn.expire(key, EXPIRE_TIME_SECONDS)


def get_from_redis_cache(key):
    if redis_conn:
        return redis_conn.get(key)
    return None


def add_cache_compute_count():
    if redis_conn:
        redis_conn.incr('clarity_cache_compute', 1)


def add_cache_query_count():
    if redis_conn:
        redis_conn.incr('clarity_cache_query', 1)


def get_cache_compute_count():
    if redis_conn:
        return redis_conn.get('clarity_cache_compute')
    else:
        return 0


def get_cache_query_count():
    if redis_conn:
        return redis_conn.get('clarity_cache_query')
    else:
        return 0


def get_cache_hit_ratio():
    if not redis_conn:
        return 0.0
    query_count = float(get_cache_query_count())
    compute_count = float(get_cache_compute_count())
    if query_count == 0.0:
        return 0.0
    ratio = (query_count - compute_count) / query_count
    return ratio


def cmp_2_key(mycmp):
    # https://bytes.com/topic/python/answers/844614-python-3-sorting-comparison-function
    class K:
        def __init__(self, obj, *args):
            self.obj = obj

        def __cmp__(self, other):
            return mycmp(self.obj, other.obj)

    return K


def mongo_client(host=None, port=None, username=None, password=None):
    if not host:
        host = mongo_host

    if not port:
        port = mongo_port

    if not username:
        username = mongo_username

    if not password:
        password = mongo_password

    # log('Mongo port: {}; host: {}'.format(port, host))
    if username and len(username) > 0 and password and len(password) > 0:
        # print('authenticated mongo')
        _mongo_client = MongoClient(host=host, port=port, username=username,
                                    password=password, socketTimeoutMS=15000, maxPoolSize=500,
                                    maxIdleTimeMS=30000)
    else:
        # print('unauthenticated mongo')
        _mongo_client = MongoClient(host, port)
    return _mongo_client
