Sentence Tokenization
*********************

Overview
========

Sentence tokenization is the process of splitting text into individual
sentences. For literature, journalism, and formal documents the tokenization
algorithms built in to spaCy perform well, since the tokenizer is trained
on a corpus of formal English text. The sentence tokenizer performs less well
for electronic health records featuring abbreviations, medical terms, spatial
measurements, and other forms not found in standard written English.

ClarityNLP attempts to improve the results of the sentence tokenizer for
electronic health records. It does this by looking for the types of textual
constructs that confuse the tokenizer and replacing them with single words.
The sentence tokenizer will not split an individual word, so the offending
text, in replacement form, is preserved intact during the tokenization process.
After generating the individual sentences, the reverse substitutions are made,
which restores original text in a set of (hopefully) improved sentences.
ClarityNLP also performs additional fixups of the sentences to further improve
the results.  This document will describe the process and illustrate with an
example.

Source Code
===========

The source code for the sentence tokenizer is located in
``nlp/algorithms/segmentation/segmentation.py``, with supporting code in
``nlp/algorithms/segmentation/segmentation_helper.py``.

Inputs
------

The entry point to the sentence tokenizer is the ``parse_sentences`` method of
the ``Segmentation`` class. This function takes a single argument, the text
string to be split into sentences.


Outputs
-------

The ``parse_sentences`` method returns a list of strings, representing the
individual sentences, as the result.

Example
-------

.. code-block:: python
   :linenos:

   seg_obj = Segmentation()
   sentence_list = seg_obj.parse_sentences(my_text)

Algorithm
=========

The improvement process proceeds through several stages, which are:

1. Perform cleanup operations on the report text.
2. Perform textual substitutions.
3. Run the spaCy sentence tokenizer on the cleaned, substituted text.
4. Find and split two consecutive sentences with no space after the period.
5. Undo the substitutions.
6. Perform additional sentence fixups for some easily-detectable errors.
7. Place all-caps section headers in their own sentence.
8. Scan the resulting sentences and delete any remaining errors.

Text Cleanup
------------

