import configparser
import sys
from urllib import request
from urllib.parse import quote
import simplejson


def make_url(qry, fq, sort, start, rows, solr_url):
    url = '%s/select?q=%s&wt=json&start=%d&rows=%d' % (solr_url, quote(qry), start, rows)

    if fq:
        url += ("&fq=%s" % quote(fq))

    if sort:
        url += ("&sort=%s" % sort)

    return url


def query(qry, fq='', sort='', start=0, rows=10, solr_url='http://localhost:8983/solr/mimic'):
    url = make_url(qry, fq, sort, start, rows, solr_url)

    print("Querying " + url)
    connection = request.urlopen(url)
    response = simplejson.load(connection)

    # print(response['response']['numFound'], "documents found.")

    # for document in response['response']['docs']:
    #     print ("  Report id =", document['report_id'])

    return response['response']['docs']


def query_doc_size(qry, fq='', sort='', start=0, rows=10, solr_url='http://localhost:8983/solr/mimic'):
    url = make_url(qry, fq, sort, start, rows, solr_url)

    print("Querying " + url)
    connection = request.urlopen(url)
    response = simplejson.load(connection)

    return int(response['response']['numFound'])


if __name__ == '__main__':
    if len(sys.argv) > 1:
        config = configparser.RawConfigParser()
        config.read('../project.cfg')
        solr = config.get('solr', 'url')
        q = sys.argv[1]
        query(q, solr_url=solr)
        sys.exit(1)
    else:
        print("Enter query")
        sys.exit(-1)
