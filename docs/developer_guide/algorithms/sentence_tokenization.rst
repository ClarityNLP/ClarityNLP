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
which restores original text in a set of improved sentences.
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

The ``parse_sentences`` method returns a list of strings, which are the
individual sentences.

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

Additional explanations for some of these items are provided below.
   
Text Cleanup
------------

The text cleanup process first searches the report text for cut-and-paste
section headers found between ``(Over)`` and ``(Cont)`` tokens. These headers
are often inserted directly into a sentence, producing a confusing result.
Here is an example:
   
| "There are two subcentimeter right renal hypodensities, 1 in\\n                                                             (Over)\\n\\n [\**2728-6-8\**] 5:24 PM\\n CT CHEST W/CONTRAST; CT ABD & PELVIS W & W/O CONTRAST, ADDL SECTIONSClip # [\**Telephone/Fax (1) 103840\**]\\n Reason: Evaluate for metastasis/lymphadenopathy related to ? GI [\**Country \**]\\n Admitting Diagnosis: UPPER GI BLEED\\n  Contrast: OMNIPAQUE Amt: 130\\n ______________________________________________________________________________\\n                                 FINAL REPORT\\n (Cont)\\n the upper pole and 1 in the lower pole, both of which are too small to\\n characterize."


By looking at this text closely, you can see how the ``(Over)..(Cont)`` section
has been pasted into this sentence:

**"There are two subcentimeter right renal hypodensities, 1 in the**
**upper pole and 1 in the lower pole, both of which are too small to\\n**
**characterize."**

The meaning of this passage is not obvious to a human observer on first
inspection, and it completely confuses a sentence tokenizer trained on
standard English text.

ClarityNLP finds these pasted report headers and removes them.

The next step in the cleanup process is the identification of numbered lists.
The numbers are removed and the narrative descriptions following the numbers
are retained.

As is visible in the pasted section header example above, electronic health
records often contain long runs of dashes, asterisks, or other symbols. These
strings are used to delimit sections in the report, but they are of no use for
machine interpretation, so ClarityNLP searches for and removes such strings.

Finally, ClarityNLP locates any instances of repeated whitespace (which
includes spaces, newlines, and tabs) and replaces them with a single space.

Textual Substitutions
---------------------

ClarityNLP performs several different types of textual substitution prior to
sentence tokenization. All of these constructs can potentially cause problems:

==================  ==================================================
Construct           Example
==================  ==================================================
Abbreviations       .H/O, Sust. Rel., w/
Vital Signs         VS T97.3 P84 BP120/56 RR16 O2Sat98 2LNC
Capitalized Header  INDICATION:
Anonymizations      [\**2728-6-8\**], [\**Telephone/Fax (1) 103840\**]
Contrast Agents     Conrast: OMNIPAQUE Amt: 130
Field of View       Field of view: 40
Size Measurement    3.1 x 4.2 mm
Dispensing Info     Protonix 40 mg p.o. q. day.
Gender              Sex: M
==================  ==================================================

ClarityNLP uses regular expressions to find instances of these constructs.
Wherever they occur they are replaced with single-word tokens such as
"ANON000", "ABBREV001", "MEAS002", etc. Replacements of each type are numbered
sequentially. The sentence tokenizer sees these replacements as single words,
and it preserves them unchanged through the tokenization process. These
replacements can be easily searched for and replaced in the resulting
sentences.

Split Consecutive Sentences
---------------------------

The punctuation in electronic health records does not always follow standard
forms. Sometimes consecutive sentences in a report have a missing space after
the period of the first sentence, which can cause the sentence tokenizer to
treat both sentences together as a single run-on sentence. ClarityNLP
detects these occurrences and separates the sentences. It also avoids
separating valid abbreviations such as *C.Diff.*, *G.Jones*, etc.

Perform Additional Sentence Fixups
----------------------------------

Sometimes the sentence tokenizer generates sentences that begin with a
punctuation character such as ``:`` or ``,``.  ClarityNLP looks for such
occurrences and moves the punctuation to the end of the preceding sentence.

Delete Remaining Errors
-----------------------

ClarityNLP scans the resulting set of sentences and takes these actions:

* deletes any remaining list numbering
* deletes any sentences consisting only of list numbering
* removes any sentences that consist only of '#1', '#2', etc.
* removes any sentences consisting entirely of nonalphanumeric symbols
* concatenates sentences that incorrectly split an age in years
* concatenates sentences that split the subject of a measurement from the measurement

Example
=======

Here is a before and after example illustrating several of the tokenization
problems discussed above. The data is taken from one of the reports in the
MIMIC data set.

**BEFORE:** Each numbered string below is a sentence that emerges
from the sentence tokenizer without ClarityNLP's additional processing. Note
that the anonymized date and name tokens ``[** ... **]`` are broken apart, as
are numbered lists, drug dispensing information, vital signs, etc. You can see
how the sentence tokenizer performs better for the narrative sections, but
the abbreviations and other nonstandard forms confuse it and cause errors:

.. literalinclude:: sentence_tokenization_before.txt

**AFTER:** Here is the same report after ClarityNLP does the cleanup,
substitutions, and additional processing described above:
                    
.. literalinclude:: sentence_tokenization_after.txt

Note that there are fewer sentences overall, and that each sentence has a much
more standard form than those in the 'before' panel above. The drug dispensing
instructions have been been corrected, the list numbering has been removed,
and the patient temperature that was split across sentences 56 and 57 has
been restored (new sentence 32).

Command Line Interface
======================

The sentence tokenizer has a command line interface that can be used for
inspecting the generated sentences. The input data must be a
JSON-formatted file with the proper ClarityNLP fields. This file can be
produced by querying SOLR for the reports of interest and dumping the results
as a JSON-formatted file. The sentence tokenization module will read the
input file, split the text into sentences as described above, and write the
results to stdout. Help for the command line interface can be obtained by
running this command from the ``nlp/algorithms/segmentation`` folder:
::
   python3 ./segmentation.py --help

Some examples:

To tokenize all reports in myreports.json and print each sentence to stdout:
::
   python3 ./segmentation.py --file /path/to/myreports.json

To tokenize only the first 10 reports (indices begin with 0):
::
   python3 ./segmentation.py --file myreports.json --end 9``

To tokenize reports 115 through 134 inclusive, and to also show the report text
after cleanup and token substitution (i.e. the actual input to the spaCy
sentence tokenizer):
::
   python3 ./segmentation.py --file myreports.json --start 115 --end 134 --debug
