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

try:
    from .report import Report
except Exception as e:
    log(e)
    from report import Report

IN_MEMORY_DATA = 'memory'
    
# set to True for debug output
_TRACE = False


# buffer in which to store data
_BUFFER = {}


###############################################################################
def _clear_buffer(_source_id):
    if _source_id:
        _source_id = str(_source_id)
        global _BUFFER
        if _source_id in _BUFFER:
            del _BUFFER[_source_id]


###############################################################################
def cleanup(_source_id):
    _clear_buffer(_source_id)


###############################################################################
def _filter_docs_by_type(types: list, _source_id: object):
    """
    Return all docs of the given type in the buffer.
    """
    if _source_id:
        _source_id = str(_source_id)
        docs = []
        source = _BUFFER.get(_source_id, list())
        for doc in source:
            if len(types) > 0:
                if 'report_type' in doc and doc['report_type'] in types:
                    docs.append(doc)
            else:
                docs.append(doc)
        log('found {} in-memory docs for job {}'.format(len(docs), _source_id))
        return docs
    return []


###############################################################################
def get_document_count(_id):
    if _id:
        return len(_BUFFER.get(_id))
    return 0


###############################################################################
def load_buffer(_id, list_of_dicts):

    if _id:
        assert type(list_of_dicts) == list
        for item in list_of_dicts:
            assert (dict == type(item)) or (Report == type(item))
        _id = str(_id)
        _clear_buffer(_id)
        _BUFFER[_id] = list()
        for item in list_of_dicts:
            _BUFFER[_id].append(item)

        log('memory_data: loaded {0} docs into buffer'.format(len(_BUFFER[_id])))

    

###############################################################################
def query(qry, mapper_url='', mapper_inst='', mapper_key='', tags: list=None,
          sort='', start=0, rows=10, cohort_ids: list=None, types: list=None,
          filter_query='', job_results_filters: dict=None, sources=None,
          report_type_query='', solr_url='http://nlp-solr:8983/solr/sample'):
    """
    Return the next 'rows' docs in the buffer beginning with index 'start'.
    """
    if sources and len(sources) > 0:
        source_id = sources[0]
        docs = _filter_docs_by_type(types, source_id)
        return docs[start:start+int(rows)]
    return []


###############################################################################
def query_doc_size(qry, mapper_url, mapper_inst, mapper_key, tags: list=None,
                   sort='', start=0, rows=10, cohort_ids: list=None, types: list=None,
                   filter_query='', job_results_filters: dict=None, sources: list=None,
                   report_type_query='', solr_url='http://nlp-solr:8983/solr/sample'):
    """
    Count and return the number of docs in the buffer of the specified types.
    """
    log(sources)
    if sources and len(sources) > 0:
        source_id = sources[0]
        docs = _filter_docs_by_type(types, source_id)
        return len(docs)
    return 0


###############################################################################
def query_doc_by_id(report_id, solr_url='http://nlp-solr:8983/solr/sample'):
    """
    Return the document with the specified report_id in the buffer. If not
    found return an empty dict.
    """

    for vals in _BUFFER.values():
        for doc in vals:
            if (dict == type(doc)) or (Report == type(doc)) and 'report_id' in doc and report_id == doc['report_id']:
                return doc

    return {}


