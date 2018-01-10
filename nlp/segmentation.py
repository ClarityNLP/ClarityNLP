import spacy
import spacy.lang.en

nlp = spacy.load('en')


def parse_sentences(text):
    doc = nlp(text)
    return [sent.string.strip() for sent in doc.sents]


if __name__ == '__main__':
    print(parse_sentences("My name is bob. I'm a pal."))
