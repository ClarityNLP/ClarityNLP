import sys
from urllib import request
from urllib.parse import quote
import simplejson
import requests
import util
from ohdsi import getCohort
import traceback
import sys
import json
from claritynlp_logging import log, ERROR, DEBUG

try:
    from .results import phenotype_results_by_context
except Exception:
    from results import phenotype_results_by_context

HEADERS = {
        'Content-Type': 'application/json',
    }


def normalize_tag(tag):
    lower_tag = tag.lower().strip()
    norm_tag = "_".join(lower_tag.split(" "))
    return norm_tag


def get_report_type_mappings(url, inst, key):
    tag_lookup_dict = {}

    try:
        if len(url) > 0:
            url = "%s/institutes/%s/reportTypes?apiToken=%s" % (url, inst, key)
            connection = request.urlopen(url)
            response = simplejson.load(connection)

            for rep in response:
                if len(rep['tags']) > 0:
                    for tag_dict in rep['tags']:
                        tag = tag_dict['documentSubjectMatterDomain']
                        lookup_tag = normalize_tag(tag)
                        if lookup_tag not in tag_lookup_dict:
                            tag_lookup_dict[lookup_tag] = list()
                        tag_lookup_dict[lookup_tag].append(rep['name'])
    except Exception as ex:
        if util.debug_mode:
            # traceback.print_exc(file=sys.stderr)
            log(ex)

    return tag_lookup_dict


def make_url(qry, fq, sort, start, rows, solr_url):
    url = '%s/select?q=%s&wt=json&start=%d&rows=%d' % (solr_url, quote(qry), start, rows)

    if fq:
        url += ("&fq=%s" % quote(fq))

    if sort:
        url += ("&sort=%s" % sort)

    return url


def make_fq(types, tags, fq, mapper_url, mapper_inst, mapper_key, report_type_query, cohort_ids, job_results_filter,
            sources):
    new_fq = fq

    subjects = list()
    documents = list()

    if types and len(types) > 0:
        if len(new_fq) > 0:
            new_fq += ' AND '
        report_type_fq = util.solr_report_type_field + ': ("' + '" OR "'.join(types) + '")'
        new_fq += report_type_fq

    if len(report_type_query) > 0:
        if len(new_fq) > 0:
            new_fq += ' AND '
        report_types = util.solr_report_type_field  + ': (' + report_type_query + ')'
        new_fq += report_types

    if job_results_filter:
        for k in job_results_filter.keys():
            job_filter = job_results_filter[k]
            context = job_filter.pop('context', None)
            results = phenotype_results_by_context(context, job_filter)
            if context.lower() == 'patient' or context.lower() == 'subject':
                subjects.extend(set([str(x['subject']) for x in results]))
            else:
                documents.extend(set([str(x['report_id']) for x in results]))

            del results

    if len(cohort_ids) > 0:
        for c in cohort_ids:
            patients = getCohort(c)['Patients']
            subjects.extend([str(x['subjectId']) for x in patients])
            del patients

    if len(tags) > 0:
        mapped_items = get_report_type_mappings(mapper_url, mapper_inst, mapper_key)
        if len(new_fq) > 0:
            new_fq += ' AND '
        matched_reports = list()
        for tag in tags:
            try:
                lookup_tag = normalize_tag(tag)
                if lookup_tag in mapped_items:
                    matched_reports.extend(mapped_items[lookup_tag])
            except Exception as e:
                if util.debug_mode:
                    traceback.print_exc(file=sys.stderr)
                    log("Unable to map tag %s" % tag)
        if len(matched_reports) > 0:
            match_report_clause = '" OR "'.join(matched_reports)
            report_types = util.solr_report_type_field + ': ("' + match_report_clause + '")'
            new_fq += report_types

    if len(subjects) > 0:
        if len(new_fq) > 0:
            new_fq += ' AND '
        subject_fq = util.solr_subject_field + ': (' + ' OR '.join(subjects) + ')'
        new_fq += subject_fq

    if len(documents) > 0:
        if len(new_fq) > 0:
            new_fq += ' AND '
        doc_fq = util.solr_report_id_field + ': (' + ' OR '.join(subjects) + ')'
        new_fq += doc_fq


    if sources and len(sources) > 0:
        if len(new_fq) > 0:
            new_fq += ' AND '
        sources_fq = util.solr_source_field + ': ("' + '" OR "'.join(sources) + '")'
        new_fq += sources_fq

    return new_fq


def get_headers():
    return HEADERS


def make_post_body(qry, fq, sort, start, rows):
    data = dict()
    data['query'] = qry
    if fq and len(fq) > 0:
        data['filter'] = fq
    if sort and len(sort) > 0:
        data['sort'] = sort
    data['offset'] = start
    data['limit'] = rows
    data['params'] = {
        'wt': 'json'
    }
    return data


def query(qry, mapper_url='', mapper_inst='', mapper_key='', tags: list=None,
          sort='', start=0, rows=10, cohort_ids: list=None, types: list=None,
          filter_query='', job_results_filters: dict=None, sources=None,
          report_type_query='', solr_url='http://nlp-solr:8983/solr/sample'):

    if tags is None:
        tags = list()
    if cohort_ids is None:
        cohort_ids = list()
    if types is None:
        types = list()
    if job_results_filters is None:
        job_results_filters = dict()
    if sources is None:
        sources = list()

    url = solr_url + '/select'
    fq = make_fq(types, tags, filter_query, mapper_url, mapper_inst, mapper_key, report_type_query, cohort_ids,
                 job_results_filters, sources)
    data = make_post_body(qry,  fq, sort, start, rows)
    post_data = json.dumps(data, indent=4)

    # if util.debug_mode == "true":
    #     log("Querying " + url)
    #     log(post_data)

    # Getting ID for new cohort
    response = requests.post(url, headers=get_headers(), data=post_data)

    # log(response['response']['numFound'], "documents found.")

    # for document in response['response']['docs']:
    #     print ("  Report id =", document['report_id'])

    if response.status_code != 200:

        return list()

    doc_results = response.json()['response']['docs']
    return doc_results


def query_doc_size(qry, mapper_url, mapper_inst, mapper_key, tags: list=None,
                   sort='', start=0, rows=10, cohort_ids: list=None, types: list=None,
                   filter_query='', job_results_filters: dict=None, sources: list=None,
                   report_type_query='', solr_url='http://nlp-solr:8983/solr/sample'):

    if tags is None:
        tags = list()
    if cohort_ids is None:
        cohort_ids = list()
    if types is None:
        types = list()
    if job_results_filters is None:
        job_results_filters = dict()
    if sources is None:
        sources = list()
    
    url = solr_url + '/select'
    fq = make_fq(types, tags, filter_query, mapper_url, mapper_inst, mapper_key, report_type_query, cohort_ids,
                 job_results_filters, sources)
    data = make_post_body(qry, fq, sort, start, rows)
    post_data = json.dumps(data)

    if util.debug_mode == "true":
        log("Querying to get counts " + url, DEBUG)
        log(post_data, DEBUG)

    # Getting ID for new cohort
    response = requests.post(url, headers=get_headers(), data=post_data)
    if response.status_code != 200:
        return 0

    num_found = int(response.json()['response']['numFound'])
    log("found {} solr docs".format(num_found))
    return num_found


def query_doc_by_id(report_id, solr_url='http://nlp-solr:8983/solr/sample'):

    url = solr_url + '/select'
    data = make_post_body("report_id:" + report_id, '', '', 0, 1)
    post_data = json.dumps(data)

    # if util.debug_mode == "true":
    #     log("Querying to get document " + url, DEBUG)
    #     log(post_data, DEBUG)

    response = requests.post(url, headers=get_headers(), data=post_data)
    if response.status_code != 200:
        return {}

    return response.json()['response']['docs'][0]


if __name__ == '__main__':
    log("solr_data", DEBUG)
    # solr = util.solr_url
    # if len(sys.argv) > 1:
    #     q = sys.argv[1]
    # else:
    #     q = "%s:*" % util.solr_text_field
    # res = query(q, solr_url=solr)
    # log(simplejson.dumps(res, indent=4*' '))
    #
    # report_mapper_url = util.report_mapper_url
    # report_mapper_key = util.report_mapper_key
    # report_mapper_inst = util.report_mapper_inst
    # mappings = get_report_type_mappings(report_mapper_url, report_mapper_inst, report_mapper_key)
    #
    # log(simplejson.dumps(mappings, indent=4*' '))
    #
    # sys.exit(1)
