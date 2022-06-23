import os
import re
import sys

import json
from claritynlp_logging import log, ERROR, DEBUG

def query(qry, mapper_url='', mapper_inst='', mapper_key='', tags: list=None,
          sort='', start=0, rows=10, cohort_ids: list=None, types: list=None,
          filter_query='', job_results_filters: dict=None, sources=None,
          report_type_query='', solr_url='http://nlp-solr:8983/solr/sample'):
    """
    Return a list of dicts, each of which is a 'document' with a minimal set of fields.
    """

    return []

def query_doc_size(qry, mapper_url, mapper_inst, mapper_key, tags: list=None,
                   sort='', start=0, rows=10, cohort_ids: list=None, types: list=None,
                   filter_query='', job_results_filters: dict=None, sources: list=None,
                   report_type_query='', solr_url='http://nlp-solr:8983/solr/sample'):
    """
    Return the number of documents satisfying the query.
    """

    return 0

def query_doc_by_id(report_id, solr_url='http://nlp-solr:8983/solr/sample'):
    """
    Return the document (a dict, see the comment string for query) matching the specified report_id.

    Only seems to be used by the caching scheme and the RaceFinder task that was
    rewritten to support caching.
    """

    return None
    

    
