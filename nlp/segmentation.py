import re
import en_core_web_md
from nltk.tokenize import sent_tokenize


class Segmentation(object):

    def __init__(self):
        self.nlp = en_core_web_md.load()
        self.regex_multi_space = re.compile(r' +')
        self.regex_multi_newline = re.compile(r'\n+')

    def remove_newlines(self, text):

        # replace newline with space
        no_newlines = self.regex_multi_newline.sub(' ', text)

        # replace multiple consecutive spaces with single space
        cleaned_text = self.regex_multi_space.sub(' ', no_newlines)
        return cleaned_text

    def parse_sentences(self, text):
        return self.parse_sentences_spacy(text)

    def parse_sentences_nltk(self, text):
        # needs punkt
        return sent_tokenize(self, text)

    def parse_sentences_spacy(self, text):
        doc = self.nlp(text)
        return [sent.string.strip() for sent in doc.sents]


if __name__ == '__main__':
    seg = Segmentation()
    print(seg.parse_sentences("My name is Bob. I'm a doctor."))
