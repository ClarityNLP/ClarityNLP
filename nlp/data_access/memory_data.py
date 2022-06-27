import os
import re
import sys
import json
from collections import deque

if __name__ == '__main__':
    DISPLAY = print
else:
    from claritynlp_logging import log, ERROR, DEBUG
    DISPLAY = log

IN_MEMORY_DATA = 'memory'
    
# set to True for debug output
_TRACE = False


# buffer in which to store data
_BUFFER = []


###############################################################################
def _clear_buffer():
    global _BUFFER
    _BUFFER = []


###############################################################################
def get_document_count():
    return len(_BUFFER)

    
###############################################################################
def load_buffer(list_of_dicts):
    
    assert type(list_of_dicts) == list
    for item in list_of_dicts:
        assert dict == type(item)

    _clear_buffer()
    for item in list_of_dicts:
        _BUFFER.append(item)
    

###############################################################################
def query(qry, mapper_url='', mapper_inst='', mapper_key='', tags: list=None,
          sort='', start=0, rows=10, cohort_ids: list=None, types: list=None,
          filter_query='', job_results_filters: dict=None, sources=None,
          report_type_query='', solr_url='http://nlp-solr:8983/solr/sample'):
    """
    Return docs in the buffer beginning with index 'start'.
    """

    return _BUFFER[start:]


###############################################################################
def query_doc_size(qry, mapper_url, mapper_inst, mapper_key, tags: list=None,
                   sort='', start=0, rows=10, cohort_ids: list=None, types: list=None,
                   filter_query='', job_results_filters: dict=None, sources: list=None,
                   report_type_query='', solr_url='http://nlp-solr:8983/solr/sample'):
    """
    Count and return the number of docs in the buffer.
    """

    return len(_BUFFER)


###############################################################################
def query_doc_by_id(report_id, solr_url='http://nlp-solr:8983/solr/sample'):
    """
    Return the document with the specified report_id in the buffer. If not
    found return an empty dict.
    """

    for doc in _BUFFER:
        if dict == type(doc) and 'report_id' in doc and report_id == doc['report_id']:
            return doc

    return {}


