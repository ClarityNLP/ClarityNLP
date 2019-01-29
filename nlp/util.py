import configparser
from os import getenv, environ, path
import redis

SCRIPT_DIR = path.dirname(__file__)
config = configparser.RawConfigParser()
config.read(path.join(SCRIPT_DIR, 'project.cfg'))
properties = dict()
delimiter = ','
quote_character = '"'
EXPIRE_TIME_SECONDS = 604800


def read_property(env_name, config_tuple, default=''):
    property_name = default
    try:
        if getenv(env_name):
            property_name = environ.get(env_name)
        else:
            property_name = config.get(config_tuple[0], config_tuple[1])
        if not property_name:
            property_name = default
        if len(env_name) > 0 and 'PASSWORD' not in env_name:
            properties[env_name] = property_name
    except Exception as ex:
        print(ex)
        properties[env_name] = default
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
mongo_working_index = read_property('NLP_MONGO_WORKING_INDEX', ('mongo', 'working_index'))
mongo_working_collection = read_property('NLP_MONGO_WORKING_COLLECTION', ('mongo', 'working_collection'))
tmp_dir = read_property('NLP_API_TMP_DIR', ('tmp', 'dir'))
log_dir = read_property('NLP_API_LOG_DIR', ('log', 'dir'))
luigi_scheduler = read_property('LUIGI_SCHEDULER_URL', ('luigi', 'scheduler'))
luigi_url = read_property('LUIGI_URL', ('luigi', 'url'))
luigi_workers = read_property('LUIGI_WORKERS', ('luigi', 'workers'))
results_viewer_url = read_property('RESULTS_CLIENT_URL', ('results_client', 'url'))
main_url = read_property('NLP_API_URL', ('main', 'url'))
row_count = read_property('BATCH_SIZE', ('solr', 'batch_size'), default='10')
report_mapper_url = read_property('MAPPER_API_URL', ('report_mapper', 'url'))
report_mapper_key = read_property('MAPPER_API_KEY', ('report_mapper', 'key'))
report_mapper_inst = read_property('MAPPER_API_INSTITUTE', ('report_mapper', 'institute'))
ohdsi_url = read_property('OHDSI_WEBAPI_URL', ('ohdsi', 'webapi'))
debug_mode = read_property('NLP_API_DEBUG_MODE', ('local', 'debug'))
azure_key = read_property('NLP_AZURE_KEY', ('apis', 'azure_key'))
solr_text_field = read_property('SOLR_TEXT_FIELD', ('solr', 'text_field'))
solr_id_field = read_property('SOLR_ID_FIELD', ('solr', 'id_field'))
solr_report_id_field = read_property('SOLR_REPORT_ID_FIELD', ('solr', 'report_id_field'))
solr_source_field = read_property('SOLR_SOURCE_FIELD', ('solr', 'source_field'))
solr_report_date_field = read_property('SOLR_REPORT_DATE_FIELD', ('solr', 'date_field'))
solr_subject_field = read_property('SOLR_SUBJECT_FIELD', ('solr', 'subject_field'))
solr_report_type_field = read_property('SOLR_REPORT_TYPE_FIELD', ('solr', 'type_field'))
expression_evaluator = read_property('NLP_EXPRESSION_EVALUATOR', ('local', 'evaluator'))
redis_hostname = read_property('REDIS_HOSTNAME', ('redis', 'hostname'))
redis_host_port = read_property('REDIS_HOST_PORT', ('redis', 'host_port'))
redis_container_port = read_property('REDIS_CONTAINER_PORT', ('redis', 'container_port'))
use_memory_caching = read_property('USE_MEMORY_CACHING', ('optimizations', 'use_memory_cache'),
                                   default='true')
use_precomputed_segmentation = read_property('USE_PRECOMPUTED_SEGMENTATION',
                                             ('optimizations', 'use_precomputed_segmentation'),
                                             default='false')
use_reordered_nlpql = read_property('USE_REORDERED_NLPQL',
                                             ('optimizations', 'use_reordered_nlpql'),
                                             default='false')
use_chained_queries = read_property('USE_CHAINED_QUERIES',
                                    ('optimizations', 'use_chained_queries'),
                                    default='false')

use_redis_caching = read_property('USE_REDIS_CACHING',
                                             ('optimizations', 'use_redis_caching'),
                                             default='false')
use_dl_trained_terms = read_property('USE_DL_TRAINED_TERMS',
                                             ('optimizations', 'use_dl_trained_terms'),
                                             default='false')
# TODO this out a bit more, this is more for experimental evaluation
cache_counts = {
    'compute': 0,
    'query': 0
}

try:
    redis_conn = redis.Redis(host=redis_hostname, port=redis_host_port, decode_responses=True)
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
