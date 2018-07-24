import configparser
from os import getenv, environ, path

SCRIPT_DIR = path.dirname(__file__)
config = configparser.RawConfigParser()
config.read(path.join(SCRIPT_DIR, 'project.cfg'))


def read_property(env_name, config_tuple):
    property_name = ''
    if getenv(env_name):
        property_name = environ.get(env_name)
    else:
        try:
            property_name = config.get(config_tuple[0], config_tuple[1])
        except Exception as ex:
            print(ex)
    return property_name


solr_url = read_property('NLP_SOLR_URL', ('solr', 'url'))

conn_string = "host='%s' dbname='%s' user='%s' password='%s' port=%s" % (read_property('NLP_PG_HOSTNAME', ('pg', 'host')),
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

main_url = read_property('NLP_API_URL', ('main', 'url'))

row_count = 25
delimiter = ','
quote_character = '"'

report_mapper_url = read_property('MAPPER_API_URL', ('report_mapper', 'url'))
report_mapper_key = read_property('MAPPER_API_KEY', ('report_mapper', 'key'))
report_mapper_inst = read_property('MAPPER_API_INSTITUTE', ('report_mapper', 'institute'))

ohdsi_url = read_property('OHDSI_WEBAPI_URL', ('ohdsi', 'webapi'))

debug_mode = read_property('NLP_API_DEBUG_MODE', ('local', 'debug'))

solr_text_field = read_property('SOLR_TEXT_FIELD', ('solr', 'text_field'))
solr_id_field = read_property('SOLR_ID_FIELD', ('solr', 'id_field'))
solr_report_id_field = read_property('SOLR_REPORT_ID_FIELD', ('solr', 'report_id_field'))
solr_source_field = read_property('SOLR_SOURCE_FIELD', ('solr', 'source_field'))
solr_report_date_field = read_property('SOLR_REPORT_DATE_FIELD', ('solr', 'date_field'))
solr_subject_field = read_property('SOLR_SUBJECT_FIELD', ('solr', 'subject_field'))
solr_report_type_field = read_property('SOLR_REPORT_TYPE_FIELD', ('solr', 'type_field'))


def cmp_2_key(mycmp):
    # https://bytes.com/topic/python/answers/844614-python-3-sorting-comparison-function
    class K:
        def __init__(self, obj, *args):
            self.obj = obj

        def __cmp__(self, other):
            return mycmp(self.obj, other.obj)
    return K

