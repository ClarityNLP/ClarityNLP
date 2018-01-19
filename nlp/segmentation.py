import re
import spacy
import en_core_web_md
import nltk
from nltk.tokenize import sent_tokenize

nlp = en_core_web_md.load()
regex_multi_space = re.compile(r' +')
regex_multi_newline = re.compile(r'\n+')


def remove_newlines(text):

    # replace newline with space
    no_newlines = regex_multi_newline.sub(' ', text)

    # replace multiple consecutive spaces with single space
    cleaned_text = regex_multi_space.sub(' ', no_newlines)
    return cleaned_text


def parse_sentences(text):
    return parse_sentences_nltk(text)


def parse_sentences_nltk(text):
    return sent_tokenize(text)


def parse_sentences_spacy(text):
    doc = nlp(text)
    return [sent.string.strip() for sent in doc.sents]


if __name__ == '__main__':
    print(parse_sentences("My name is Bob. I'm a doctor."))
