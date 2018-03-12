import re
import en_core_web_md
from nltk.tokenize import sent_tokenize
import time

data = {}
loading_status = 'none'


def segmentation_init(tries=0):
    if tries > 0:
        print('Retrying, try%d' % tries)

    global loading_status
    if loading_status == 'none' and 'nlp' not in data:
        try:
            print('Segmentation init...')
            loading_status = 'loading'
            data['nlp'] = en_core_web_md.load()
            loading_status = 'done'
        except Exception as exc:
            print(exc)
            loading_status = 'none'
    elif loading_status == 'loading' and tries < 30:
        time.sleep(10)
        if loading_status == 'loading':
            new_tries = tries + 1
            return segmentation_init(tries=new_tries)

    return data['nlp']


def parse_sentences_spacy(text):
    spacy = segmentation_init()
    doc = spacy(text)
    return [sent.string.strip() for sent in doc.sents]


class Segmentation(object):

    def __init__(self):
        self.regex_multi_space = re.compile(r' +')
        self.regex_multi_newline = re.compile(r'\n+')

    def remove_newlines(self, text):

        # replace newline with space
        no_newlines = self.regex_multi_newline.sub(' ', text)

        # replace multiple consecutive spaces with single space
        cleaned_text = self.regex_multi_space.sub(' ', no_newlines)
        return cleaned_text

    def parse_sentences(self, text):
        return parse_sentences_spacy(text)

    def parse_sentences_nltk(self, text):
        # needs punkt
        return sent_tokenize(self, text)


# if __name__ == '__main__':
    # seg = Segmentation()
    # print(seg.parse_sentences("My name is Bob. I'm a doctor."))
