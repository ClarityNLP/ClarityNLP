import util
from algorithms import segmentation, segmentation_init
from claritynlp_logging import log, ERROR, DEBUG

try:
    from .solr_data import query, query_doc_size
except Exception:
    from solr_data import query, query_doc_size
    

segment = segmentation.Segmentation()

solr_url = "http://18.224.57.156:8983/solr/sample"
headers = {
    'Content-type': 'application/json',
}
batch_size = 10
doc_size = 0
spacy = segmentation_init()


def document_sentences(txt):
    sentence_list = segment.parse_sentences(txt, spacy=spacy)
    return sentence_list


def document_text(doc, clean=True):
    if doc and util.solr_text_field in doc:
        txt = doc[util.solr_text_field]
        if type(txt) == str:
            txt_val = txt
        elif type(txt) == list:
            txt_val = ' '.join(txt)
        else:
            txt_val = str(txt)

        if clean:
            return txt_val.encode("ascii", errors="ignore").decode()
        else:
            return txt_val
    else:
        return ''


def do_something(q, n):
    try:
        docs = query(q, solr_url=solr_url, mapper_inst=util.report_mapper_inst,
                     mapper_key=util.report_mapper_key,
                     mapper_url=util.report_mapper_url, start=n, rows=batch_size)
        for doc in docs:
            txt = document_text(doc, clean=True)
            # do something
    except Exception as ex:
        log('exception getting docs')
        log(ex)
        return False
    return True


def get_documents(q):
    global doc_size
    doc_size = query_doc_size(q, solr_url=solr_url, mapper_inst=util.report_mapper_inst,
                              mapper_key=util.report_mapper_key, mapper_url=util.report_mapper_url)

    i = 0
    while i < doc_size:
        log("on batch %d" % i)
        do_something(q, i)

        i += batch_size


if __name__ == "__main__":
    log('get_solr_docs')
    # qry = "*:*"
    # get_documents(qry)
