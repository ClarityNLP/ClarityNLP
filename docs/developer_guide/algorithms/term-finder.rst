.. _termfinderalgo:

Term Finder
******************

The most basic algorithm, which uses regular expressions to identify terms. In addition, the algorithm will return section, negation, experiencer and temporality. Runs the :ref:`contextalgo` and
:ref:`section tagging<sectiontagging>` algorithms.

Provider Assertion
******************

An extension of Term Finder, which uses regular expressions to identify terms. In addition, the algorithm will return section, negation, experiencer and temporality from :ref:`contextalgo`, but will filter them such that the follow conditions are met:

* **Negation**: Affirmed
* **Experiencer**: Patient
* **Temporality**: Historical OR Recent

