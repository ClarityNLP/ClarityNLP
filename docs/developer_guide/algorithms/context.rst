.. _contextalgo:

ConText
*******

Overview
========
ConText is based on the algorithm developed by Chapman, et al. [1]_ [2]_ to determine negation, experiencer and temporality modifiers around clinical concepts.
The algorithm uses rules, and text windows (or spans) along with an input concept to determine the 3 ConText types. Resulting values from ConText can be any of the following, where the bolded item notes the default.

Temporality
-----------
- **Recent**
- Historical
- Hypothetical

Experiencer
-----------
- **Patient**
- Other

Negation
--------
- **Affirmed**
- Negated
- Possible



Source Code
===========
The source code is found in ``nlp/algorithms/context/context.py``.

Concepts
--------
ConText has a pre-defined set of concepts for each ConText type. They can be found at ``nlp/algorithms/context/data``.
Each ConText keyword has a category which either indicates it as a candidate for a ConText type, a pseudo-candidate (which would be excluded), or a term that indicates a change in the sentence phrase, such as a conjunction (which would close a ConText window).


Algorithm
=========
We have a Python implementation of the ConText algorithm.


References
==========

.. [1] | Harkema H, Dowling JN, Thornblade T, Chapman WW
       | **Context: An Algorithm for Determining Negation, Experiencer, and Temporal Status**
       | **from Clinical Reports**
       | *Journal of biomedical informatics.* 2009;42(5):839-851.
       | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2757457/

.. [2] | Chapman WW, Chu D, Dowling JN
       | **ConText: An algorithm for identifying contextual features from clinical text.**
       | *BioNLP Workshop of the Association for Computational Linguistics.* June 29, 2007.
       | http://dl.acm.org/citation.cfm?id=1572408

