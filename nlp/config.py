import multiprocessing
from os import environ
from claritynlp_logging import log

workers = multiprocessing.cpu_count() + 1
threads = multiprocessing.cpu_count()

PORT = int(environ.get("NLP_API_CONTAINER_PORT", 5000))
environ["PORT"] = str(PORT)
environ["USE_GUNICORN"] = "true"
log('done setting up config.py on port {}, workers: {}, '
      'threads: {}'.format(PORT, workers, threads))

