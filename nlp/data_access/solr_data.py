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
        traceback.print_exc(file=sys.stderr)
        print(ex)

    return tag_lookup_dict


def make_url(qry, fq, sort, start, rows, solr_url):
    url = '%s/select?q=%s&wt=json&start=%d&rows=%d' % (solr_url, quote(qry), start, rows)

    if fq:
        url += ("&fq=%s" % quote(fq))

    if sort:
        url += ("&sort=%s" % sort)

    return url


def make_fq(types, tags, fq, mapper_url, mapper_inst, mapper_key, report_type_query, cohort_ids):
    new_fq = fq

    mapped_items = get_report_type_mappings(mapper_url, mapper_inst, mapper_key)

    if types and len(types) > 0:
        if len(new_fq) > 0:
            new_fq += ' AND '
        report_type_fq = 'report_type: ("' + '" OR "'.join(types) + '")'
        new_fq += report_type_fq

    if len(report_type_query) > 0:
        if len(new_fq) > 0:
            new_fq += ' AND '
        report_types = 'report_type: (' + report_type_query + ')'
        new_fq += report_types

    if len(cohort_ids) > 0:
        subjects = list()
        for c in cohort_ids:
            patients = getCohort(c)['Patients']
            subjects.extend([str(x['subjectId']) for x in patients])
            del patients
        if len(subjects) > 0:
            if len(new_fq) > 0:
                new_fq += ' AND '
            subject_fq = 'subject: (' + ' OR '.join(subjects) + ')'
            new_fq += subject_fq

    if len(tags) > 0:
        if len(new_fq) > 0:
            new_fq += ' AND '
        matched_reports = list()
        for tag in tags:
            try:
                lookup_tag = normalize_tag(tag)
                matched_reports.extend(mapped_items[lookup_tag])
            except Exception as e:
                traceback.print_exc(file=sys.stderr)
                print("Unable to map tag %s" % tag)
        if len(matched_reports) > 0:
            match_report_clause = '" OR "'.join(matched_reports)
            report_types = 'report_type: ("' + match_report_clause + '")'
            new_fq += report_types

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


def query(qry, mapper_url='', mapper_inst='', mapper_key='', tags=list(), sort='', start=0, rows=10,
          cohort_ids: list = list(), types: list = list(), filter_query='',
          report_type_query='', solr_url='http://nlp-solr:8983/solr/sample'):
    url = solr_url + '/select'
    fq = make_fq(types, tags, filter_query, mapper_url, mapper_inst, mapper_key, report_type_query, cohort_ids)
    data = make_post_body(qry,  fq, sort, start, rows)

    print("Querying " + url)
    post_data = json.dumps(data, indent=4)
    print(post_data)

    # Getting ID for new cohort
    response = requests.post(url, headers=get_headers(), data=post_data)

    # print(response['response']['numFound'], "documents found.")

    # for document in response['response']['docs']:
    #     print ("  Report id =", document['report_id'])

    if response.status_code != 200:
        return list()

    return response.json()['response']['docs']


def query_doc_size(qry, mapper_url, mapper_inst, mapper_key, tags=list(), sort='', start=0, rows=10,
                   cohort_ids: list = list(), types: list = list(), filter_query='',
                   report_type_query='', solr_url='http://nlp-solr:8983/solr/sample'):

    url = solr_url + '/select'
    fq = make_fq(types, tags, filter_query, mapper_url, mapper_inst, mapper_key, report_type_query, cohort_ids)
    data = make_post_body(qry, fq, sort, start, rows)

    print("Querying to get counts " + url)
    post_data = json.dumps(data)
    print(post_data)

    # Getting ID for new cohort
    response = requests.post(url, headers=get_headers(), data=post_data)
    if response.status_code != 200:
        return 0

    return int(response.json()['response']['numFound'])


if __name__ == '__main__':
    solr = util.solr_url
    if len(sys.argv) > 1:
        q = sys.argv[1]
    else:
        q = "report_text:*"
    query(q, solr_url=solr)

    report_mapper_url = util.report_mapper_url
    report_mapper_key = util.report_mapper_key
    report_mapper_inst = util.report_mapper_inst
    mappings = get_report_type_mappings(report_mapper_url, report_mapper_inst, report_mapper_key)

    print(simplejson.dumps(mappings, indent=4*' '))
    sys.exit(1)
