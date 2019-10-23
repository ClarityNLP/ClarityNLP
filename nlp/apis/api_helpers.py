from algorithms import *
from claritynlp_logging import log, ERROR, DEBUG

init_status = "none"


def init():
    global init_status
    if init_status == "none" or init_status == "error":
        try:
            init_status = "loading"
            section_tagger_init()
            segmentation_init()
            context_init()
            lab_value_matcher_init()
            init_status = "done"
        except Exception as ex:
            log(ex, ERROR)
            init_status = "error"
