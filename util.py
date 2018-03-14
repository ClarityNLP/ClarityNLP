import configparser
import os

SCRIPT_DIR = os.path.dirname(__file__)
config = configparser.RawConfigParser()
config.read(os.path.join(SCRIPT_DIR, 'project.cfg'))

solr_url = os.environ.get('NLP_SOLR_URL', config.get('solr', 'url'))

conn_string = "host='%s' dbname='%s' user='%s' password='%s' port=%s" % (os.environ.get('NLP_PG_HOSTNAME', config.get('pg', 'host')),
                                                                         os.environ.get('NLP_PG_DATABASE', config.get('pg', 'dbname')),
                                                                         os.environ.get('NLP_PG_USER', config.get('pg', 'user')),
                                                                         os.environ.get('NLP_PG_PASSWORD', config.get('pg', 'password')),
                                                                         str(os.environ.get('NLP_PG_CONTAINER_PORT', config.get('pg', 'port'))))

mongo_host = os.environ.get('NLP_MONGO_HOSTNAME', config.get('mongo', 'host'))
mongo_port = int(os.environ.get('NLP_MONGO_CONTAINER_PORT', config.get('mongo', 'port')))
mongo_db = os.environ.get('NLP_MONGO_DATABASE', config.get('mongo', 'db'))
mongo_working_index = os.environ.get('NLP_MONGO_WORKING_INDEX', config.get('mongo', 'working_index'))
mongo_working_collection = os.environ.get('NLP_MONGO_WORKING_COLLECTION', config.get('mongo', 'working_collection'))

tmp_dir = os.environ.get('NLP_API_TMP_DIR', config.get('tmp', 'dir'))
log_dir = os.environ.get('NLP_API_LOG_DIR', config.get('log', 'dir'))

luigi_url = os.environ.get('LUIGI_URL', config.get('luigi', 'url'))
luigi_workers = os.environ.get('LUIGI_WORKERS', config.get('luigi', 'workers'))

main_url = os.environ.get('NLP_API_URL', config.get('main', 'url'))

row_count = 100
delimiter = ','
quote_character = '"'

report_mapper_url = os.environ.get('MAPPER_API_URL', config.get('report_mapper', 'url'))
report_mapper_key = os.environ.get('MAPPER_API_KEY', config.get('report_mapper', 'key'))
report_mapper_inst = os.environ.get('MAPPER_API_INSTITUTE', config.get('report_mapper', 'institute'))
