/ngram_cohort
-------------

*GET*

**About:** 

Generating n-grams of the Report Text for a particular Cohort. API has to accept the Cohort ID, the _n_ in n-gram, and frequency (the minimum occurrence of a particular n-gram). The API also accepts a keyword. If given the keyword, only n-grams which contain that keyword are returned. 

**Parameters:**

- Cohort ID : mandatory
- Keyword : optional
- n : mandatory
- frequency : mandatory

**Example usage:** 

::

    ~/ngram_cohort?cohort_id=6&n=15&frequency=10

    ~/ngram_cohort?cohort_id=6&keyword=cancer&n=15&frequency=10
