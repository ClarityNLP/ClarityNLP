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

The text cleanup process first searches the report text for cut-and-paste
section headers found between ``(Over)`` and ``(Cont)`` tokens. These headers
are often inserted directly into a sentence, producing a confusing result.
Here is an example:

There are two subcentimeter right renal hypodensities, 1 in\\n                                                             (Over)\\n\\n [**2728-6-8**] 5:24 PM\\n CT CHEST W/CONTRAST; CT ABD & PELVIS W & W/O CONTRAST, ADDL SECTIONSClip # [**Telephone/Fax (1) 103840**]\\n Reason: Evaluate for metastasis/lymphadenopathy related to ? GI [**Country **]\\n Admitting Diagnosis: UPPER GI BLEED\\n  Contrast: OMNIPAQUE Amt: 130\\n ______________________________________________________________________________\\n                                 FINAL REPORT\\n (Cont)\\n the upper pole and 1 in the lower pole, both of which are too small to\\n characterize.

Observe how the ``(Over)..(Cont)`` section has been pasted into this
sentence:

**"There are two subcentimeter right renal hypodensities, 1 in the**
**upper pole and 1 in the lower pole, both of which are too small to \\n**
**characterize."**

The meaning of this passage is not obvious on first inspection to a human
observer, and it would completely confuse a sentence tokenizer trained on
formal written English text.

ClarityNLP finds these pasted report headers and removes them.

The next step in the cleanup process is the identification of numbered lists.
The numbers are removed and the narrative descriptions following the numbers
are retained.

As is visible in the pasted section header example above, electronic health
records often contain long runs of dashes, asterisks, or other symbols. These
strings are used to delimit sections in the report, but they are of no use for
automated interpretation, so ClarityNLP searches for and removes such strings.

Finally, ClarityNLP locates any instances of repeated whitespace and replaces
them with a single space.


Textual Substitutions
---------------------

Run the spaCy Sentence Tokenizer
--------------------------------

Split Consecutive Sentences
---------------------------

Undo the Substitutions
----------------------

Perform Additional Sentence Fixups
----------------------------------

Place All-Caps Section Headers in Their Own Sentence
----------------------------------------------------

Delete Remaining Errors
-----------------------

