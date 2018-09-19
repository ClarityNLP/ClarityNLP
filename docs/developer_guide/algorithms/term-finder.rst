Term Finder
******************

The most basic algorithm, which uses regular expressions to identify terms. In addition, the algorithm will return section, negation, experiencer and temporality. Runs :ref:`context` and :ref:`sectiontagging`.

Provider Assertion
******************

An extension of Term Finder, which uses regular expressions to identify terms. In addition, the algorithm will return section, negation, experiencer and temporality from :ref:`context`, but will filter them such that the follow conditions are met:

* **Negation**: Affirmed
* **Experiencer**: Patient
* **Temporality**: Historical OR Recent

