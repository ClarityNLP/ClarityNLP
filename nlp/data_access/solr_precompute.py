import util
import json
import requests
from algorithms import segmentation, segmentation_init
from algorithms.sec_tag import *
from claritynlp_logging import log, ERROR, DEBUG

try:
    from .solr_data import query, query_doc_size
except Exception:
    from solr_data import query, query_doc_size

segment = segmentation.Segmentation()
batch_size = 10
solr_url = "http://18.220.133.76:8983/solr/sample"
sentences_key = "sentence_attrs"
section_names_key = "section_name_attrs"
section_text_key = "section_text_attrs"
url = solr_url + '/update?commit=true'
headers = {
    'Content-type': 'application/json',
}
doc_size = 0
spacy = segmentation_init(tries=2)


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


def retry(docs):
    updated_docs = list()

    for d in docs:
        d[section_names_key] = []
        d[section_text_key] = []
        updated_docs.append(d)
    data = json.dumps(updated_docs)
    response2 = requests.post(url, headers=headers, data=data)

    if response2.status_code == 200:
        log('successful retry!!!')
    else:
        log('failed retry: ', response2.reason)
        log(response2.content)


def pre_compute(n):
    try:
        docs = query("-sentence_attrs:*", solr_url=solr_url, mapper_inst=util.report_mapper_inst,
                     mapper_key=util.report_mapper_key, sort="source DESC",
                     mapper_url=util.report_mapper_url, start=n, rows=batch_size)
        updated_docs = list()
        ids = list()
        for doc in docs:
            txt = document_text(doc, clean=True)
            updates = False
            if sentences_key not in doc:
                sentences = document_sentences(txt)
                doc[sentences_key] = sentences
                updates = True

            if section_names_key not in doc:
                section_headers, section_texts = [UNKNOWN], [txt]
                try:
                    section_headers, section_texts = sec_tag_process(txt)
                except Exception as e:
                    log(e)
                names = [x.concept for x in section_headers]
                doc[section_names_key] = names
                doc[section_text_key] = section_texts
                updates = True

            if updates:
                ids.append(doc[util.solr_report_id_field])
                updated_docs.append(doc)

        log('updating the following docs: ', ids)
        if n % 10 == 0:
            log("******************************")
            done_doc_size = query_doc_size("sentence_attrs:*", solr_url=solr_url, mapper_inst=util.report_mapper_inst,
                                      mapper_key=util.report_mapper_key, mapper_url=util.report_mapper_url)

            pct = (float(done_doc_size) / float(doc_size)) * 100.0
            log("updated overall: %d/%d (%f pct)" % (done_doc_size, doc_size, pct))
            log("******************************")
        data = json.dumps(updated_docs)
        response2 = requests.post(url, headers=headers, data=data)

        if response2.status_code == 200:
            log('success!!!')
        else:
            log('fail: ', response2.reason)
            log(response2.content)
            retry(updated_docs)
    except Exception as ex:
        log('exception updating docs')
        return False
    return True


def get_documents():
    global doc_size
    doc_size = query_doc_size("*:*", solr_url=solr_url, mapper_inst=util.report_mapper_inst,
                              mapper_key=util.report_mapper_key, mapper_url=util.report_mapper_url)

    i = 0
    while i < doc_size:
        log("on batch %d" % i)
        pre_compute(i)

        i += batch_size


if __name__ == "__main__":
    log('update values')
    get_documents()
