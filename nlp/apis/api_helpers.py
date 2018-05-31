from algorithms import *

init_status = "none"


def init():
    global init_status
    if init_status == "none" or init_status == "error":
        try:
            init_status = "loading"
            section_tagger_init()
            segmentation_init()
            context_init()
            init_status = "done"
        except Exception as ex:
            print(ex)
            init_status = "error"
