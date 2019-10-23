import logging
from time import localtime, strftime
import inspect
from os import environ
import sys
import traceback

the_app = None

DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
CRITICAL = "CRITICAL"


def log(obj='', level=INFO, file=sys.stdout):
    the_stack = inspect.stack()[1]
    the_caller = the_stack[0].f_locals.get('self', None)

    if isinstance(obj, Exception):
        obj = '\n'.join(traceback.format_tb(obj.__traceback__))

    if the_caller:
        the_caller = "({}) ".format(repr(the_caller.__class__.__name__))
    else:
        the_caller = ''

    if level == ERROR or level == CRITICAL:
        if file == sys.stdout:
            file = sys.stderr

    if the_app:
        message = "{}{}".format(the_caller, repr(obj))
        if level == DEBUG:
            the_app.logger.debug(message)
        elif level == WARNING:
            the_app.logger.warning(message)
        elif level == ERROR:
            the_app.logger.error(message)
        elif level == CRITICAL:
            the_app.logger.critical(message)
        else:
            the_app.logger.info(message)
    else:
        message = repr(obj)
        the_time = strftime("%Y-%m-%d %H:%M:%S-%Z", localtime())
        print("[{}] {} in claritynlp_logging: {}{}".format(the_time, level, the_caller, message), file=file)


def setup_log(app):
    global the_app
    the_app = app

    use_gunicorn_logger = environ.get('USE_GUNICORN', False)
    if use_gunicorn_logger:
        gunicorn_logger = logging.getLogger("gunicorn.error")
        the_app.logger.handlers = gunicorn_logger.handlers
        the_app.logger.setLevel(gunicorn_logger.level)

