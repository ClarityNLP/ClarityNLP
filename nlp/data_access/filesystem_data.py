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


# file extensions supported by the filesystem_data interface of ClarityNLP
_EXTENSIONS = {'.json'}

# set to True for debug output
_TRACE = False


###############################################################################
def _convert_types(types: list):
    """
    Convert a list of document types to filesystem directory names.
    """
    
    # convert types to those found in the filetree
    new_types = []
    for t in types:
        # convert to lowercase
        new_type = t.lower()
        # replace forward slash and whitespace with underscore
        new_type = re.sub(r'[/ ]', '_', new_type)
        new_types.append(new_type)

    if _TRACE:
        DISPLAY('    TYPES: {0}'.format(types))
        DISPLAY('NEW TYPES: {0}'.format(new_types))

    return new_types


###############################################################################
def query(qry, mapper_url='', mapper_inst='', mapper_key='', tags: list=None,
          sort='', start=0, rows=10, cohort_ids: list=None, types: list=None,
          filter_query='', job_results_filters: dict=None, sources=None,
          report_type_query='', solr_url='http://nlp-solr:8983/solr/sample'):
    """
    Return all docs in the given subdirectories indicated by the types param.
    """

    if not os.path.isdir(solr_url):
        return []
    
    # convert types to subdirectories
    new_types = _convert_types(types)

    dir_list = []
    if types is None or 0 == len(types):
        # no subdirs to search, so search the current dir for docs
        dir_list.append(solr_url)
    else:
        for t in types:
            dirname = os.path.join(solr_url, t)
            if os.path.isdir(dirname):
                dir_list.append(dirname)

    docs = []
    for path in dir_list:
        assert os.path.isdir(path)
        if _TRACE:
            DISPLAY('query: Loading files in directory "{0}"'.format(path))
        for item in os.listdir(path):
            fullpath = os.path.join(path, item)
            if os.path.isfile(fullpath):
                # found a file, check for supported extension
                f, ext = os.path.splitext(item)
                if ext in _EXTENSIONS:
                    with open(fullpath, 'rt') as infile:
                        text = infile.read()
                        json_obj = json.loads(text)
                        docs.append(json_obj)

    return docs[start:]


###############################################################################
def query_doc_size(qry, mapper_url, mapper_inst, mapper_key, tags: list=None,
                   sort='', start=0, rows=10, cohort_ids: list=None, types: list=None,
                   filter_query='', job_results_filters: dict=None, sources: list=None,
                   report_type_query='', solr_url='http://nlp-solr:8983/solr/sample'):
    """
    Count and return the number of files with a supported extension in the
    given directory.
    """

    # Scan the directory and count docs of each type.
    if not os.path.isdir(solr_url):
        return 0
    
    # convert types to subdirectories
    new_types = _convert_types(types)

    # deque is used a simple queue of directories in which to count files
    # push == append, pop == popleft
    queue = deque()
    queue.append(solr_url)
    
    file_count = 0
    while len(queue) > 0:
        path = queue.popleft()
        assert os.path.isdir(path)
        if _TRACE:
            DISPLAY('query_doc_size: counting files in directory "{0}"'.format(path))
        for item in os.listdir(path):
            fullpath = os.path.join(path, item)
            if os.path.isfile(fullpath):
                # found a file, so check for supported extension
                f, ext = os.path.splitext(item)
                if ext in _EXTENSIONS:
                    file_count += 1
                    if _TRACE:
                        DISPLAY('Found file "{0}"'.format(item))
            elif os.path.isdir(fullpath) and item in new_types:
                # found a subdir of the requested type, save it
                queue.append(fullpath)

    return file_count


###############################################################################
def query_doc_by_id(report_id, solr_url='http://nlp-solr:8983/solr/sample'):
    """
    Return the document with the specified report_id in the file_tree rooted
    at solr_url. If not found return an empty dict.
    """

    if not os.path.isdir(solr_url):
        return {}

    target_filenames = set()
    for ext in _EXTENSIONS:
        filename = '{0}{1}'.format(report_id, ext)
        target_filenames.add(filename)

    if _TRACE:
        DISPLAY('query_doc_by_id: dearching for any of these files: {0}'.
              format(target_filenames))
    
    # deque is used as a simple queue of directories
    # push == append, pop == popleft
    queue = deque()
    queue.append(solr_url)

    while len(queue) > 0:
        path = queue.popleft()
        assert os.path.isdir(path)
        if _TRACE:
            DISPLAY('query_doc_by_id: searching in directory "{0}"'.format(path))
        for item in os.listdir(path):
            fullpath = os.path.join(path, item)
            if os.path.isfile(fullpath):
                # found a file, check for supported extension
                f, ext = os.path.splitext(item)
                if ext in _EXTENSIONS:
                    # files are named with the report_id
                    if item in target_filenames:
                        with open(fullpath, 'rt') as infile:
                            text = infile.read()
                            json_obj = json.loads(text)
                            return json_obj
                            
            elif os.path.isdir(fullpath):
                # found a subdir, save it for later searching
                queue.append(fullpath)

    return {}


###############################################################################
def banner(msg, width=70):
    space_count = (width - len(msg))//2
    print('\n{0}'.format('*' * width))
    print('{0}{1}{2}'.format(' '*space_count, msg, ' '*space_count))
    print('{0}'.format('*' * width))


###############################################################################          
if __name__ == '__main__':

    rootdir = '/Users/rb230/data/claritynlp_data/'
    types = ['CLARITYNLP_VALIDATION_0'] #['Discharge summary', 'Physician', 'Social Work']

    banner('query_doc_size')
    count = query_doc_size(qry=None,
                           mapper_url=None,
                           mapper_inst=None,
                           mapper_key=None,
                           types=types,
                           solr_url=rootdir)
    DISPLAY('\nFound {0} docs with types {1}'.format(count, types))

    banner('query_doc_by_id')
    report_id = 6
    doc = query_doc_by_id(report_id, solr_url=rootdir)
    DISPLAY('\nFound this doc with report_id={0}:\n{1}'.format(report_id, doc))

    banner('query')
    docs = query(qry=None, types=types, solr_url=rootdir)
    DISPLAY('Query returned {0} docs with these report_text fields: '.format(len(docs)))
    for i, d in enumerate(docs):
        DISPLAY('\t[{0}]: {1}'.format(i, d['report_text']))
