import sys
from urllib import request
from urllib.parse import quote
import simplejson
import util


def normalize_tag(tag):
    lower_tag = tag.lower().strip()
    norm_tag = "_".join(lower_tag.split(" "))
    return norm_tag


def get_report_type_mappings(url, inst, key):
    tag_lookup_dict = {}

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

    return tag_lookup_dict


def make_url(qry, fq, sort, start, rows, solr_url):
    url = '%s/select?q=%s&wt=json&start=%d&rows=%d' % (solr_url, quote(qry), start, rows)

    if fq:
        url += ("&fq=%s" % quote(fq))

    if sort:
        url += ("&sort=%s" % sort)

    return url


def make_fq(tags, fq, mapper_url, mapper_inst, mapper_key, report_type_query):
    new_fq = fq

    mapped_items = get_report_type_mappings(mapper_url, mapper_inst, mapper_key)

    if len(report_type_query) > 0:
        report_types = 'report_type: ("' + report_type_query + '")'
        new_fq += report_types

    if len(tags) > 0:
        if len(new_fq) > 0:
            new_fq += ' AND '
        matched_reports = list()
        for tag in tags:
            try:
                lookup_tag = normalize_tag(tag)
                matched_reports.extend(mapped_items[lookup_tag])
            except Exception as e:
                print("Unable to map tag %s" % tag)
        if len(matched_reports) > 0:
            match_report_clause = '" OR "'.join(matched_reports)
            report_types = 'report_type: ("' + match_report_clause + '")'
            new_fq += report_types

    return new_fq


def query(qry, mapper_url='', mapper_inst='', mapper_key='', tags=list(), fq='', sort='', start=0, rows=10,
          report_type_query='', solr_url='http://nlp-solr:8983/solr/sample'):
    url = make_url(qry, make_fq(tags, fq, mapper_url, mapper_inst, mapper_key, report_type_query), sort, start, rows, solr_url)

    print("Querying " + url)
    connection = request.urlopen(url)
    response = simplejson.load(connection)

    # print(response['response']['numFound'], "documents found.")

    # for document in response['response']['docs']:
    #     print ("  Report id =", document['report_id'])

    return response['response']['docs']


def query_doc_size(qry, mapper_url, mapper_inst, mapper_key, tags=list(), fq='', sort='', start=0, rows=10,
                   report_type_query='', solr_url='http://nlp-solr:8983/solr/sample'):
    url = make_url(qry, make_fq(tags, fq, mapper_url, mapper_inst, mapper_key, report_type_query), sort, start, rows, solr_url)

    print("Querying " + url)
    connection = request.urlopen(url)
    response = simplejson.load(connection)

    return int(response['response']['numFound'])


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
