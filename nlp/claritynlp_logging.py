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
        log("EXCEPTION: {}".format(repr(obj), level=ERROR))
        for t in traceback.format_tb(obj.__traceback__):
            lines = t.split('\n')
            for l in lines:
                if l.strip() == '':
                    continue
                log("     {}".format(l), level=ERROR)
        return

    repr_obj = repr(obj)
    if '\n' in repr_obj:
        for l in repr_obj.split('\n'):
            log(l, level=level)
        return

    if the_caller:
        the_caller = "({}) ".format(repr(the_caller.__class__.__name__))
    else:
        the_caller = ''

    if level == ERROR or level == CRITICAL:
        if file == sys.stdout:
            file = sys.stderr

    if the_app:
        message = "{}{}".format(the_caller, repr_obj)
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
        message = repr_obj
        the_time = strftime("%Y-%m-%d %H:%M:%S-%Z", localtime())
        print("[{}] {} in claritynlp_logging: {}{}".format(the_time, level, the_caller, message), file=file)


def setup_log(app):
    global the_app
    the_app = app

    use_gunicorn_logger = environ.get('USE_GUNICORN', "false")
    if use_gunicorn_logger == "true":
        gunicorn_logger = logging.getLogger("gunicorn.error")
        the_app.logger.handlers = gunicorn_logger.handlers
        the_app.logger.setLevel(gunicorn_logger.level)

