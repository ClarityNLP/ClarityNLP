import configparser
import sys
from urllib import request
from urllib.parse import quote
import simplejson


def get_report_type_mappings(url, inst, key):
    tag_lookup = {}

    if len(url) > 0:
        url = "%s/institutes/%s/reportTypes?apiToken=%s" % (url, inst, key)
        connection = request.urlopen(url)
        response = simplejson.load(connection)

        for rep in response:
            if len(rep['tags']) > 0:
                for tag_dict in rep['tags']:
                    tag = tag_dict['documentSubjectMatterDomain']
                    if tag not in tag_lookup:
                        tag_lookup[tag] = list()
                    tag_lookup[tag].append(rep['name'])

    return tag_lookup


def make_url(qry, fq, sort, start, rows, solr_url):
    url = '%s/select?q=%s&wt=json&start=%d&rows=%d' % (solr_url, quote(qry), start, rows)

    if fq:
        url += ("&fq=%s" % quote(fq))

    if sort:
        url += ("&sort=%s" % sort)

    return url


def make_fq(tags, fq, mapper_url, mapper_inst, mapper_key):
    new_fq = fq

    mapped_items = get_report_type_mappings(mapper_url, mapper_inst, mapper_key)

    if len(tags) > 0:
        if len(new_fq) > 0:
            new_fq += ' AND '
        matched_reports = list()
        for tag in tags:
            try:
                matched_reports.extend(mapped_items[tag])
            except Exception as e:
                print("Unable to map tag %s" % tag)
        if len(matched_reports) > 0:
            report_types = 'report_type: ("' + '" OR "'.join(matched_reports) + '")'
            new_fq += report_types

    return new_fq


def query(qry, mapper_url='', mapper_inst='', mapper_key='', tags=list(), fq='', sort='', start=0, rows=10, solr_url='http://localhost:8983/solr/mimic'):
    url = make_url(qry, make_fq(tags, fq, mapper_url, mapper_inst, mapper_key), sort, start, rows, solr_url)

    print("Querying " + url)
    connection = request.urlopen(url)
    response = simplejson.load(connection)

    # print(response['response']['numFound'], "documents found.")

    # for document in response['response']['docs']:
    #     print ("  Report id =", document['report_id'])

    return response['response']['docs']


def query_doc_size(qry, mapper_url, mapper_inst, mapper_key, tags=list(), fq='', sort='', start=0, rows=10, solr_url='http://localhost:8983/solr/mimic'):
    url = make_url(qry, make_fq(tags, fq, mapper_url, mapper_inst, mapper_key), sort, start, rows, solr_url)

    print("Querying " + url)
    connection = request.urlopen(url)
    response = simplejson.load(connection)

    return int(response['response']['numFound'])


if __name__ == '__main__':
    config = configparser.RawConfigParser()
    config.read('../project.cfg')
    solr = config.get('solr', 'url')
    if len(sys.argv) > 1:
        q = sys.argv[1]
    else:
        q = "report_text:*"
    query(q, solr_url=solr)

    report_mapper_url = config.get('report_mapper', 'url')
    report_mapper_key = config.get('report_mapper', 'key')
    report_mapper_inst = config.get('report_mapper', 'institute')
    mappings = get_report_type_mappings(report_mapper_url, report_mapper_inst, report_mapper_key)

    sys.exit(1)
