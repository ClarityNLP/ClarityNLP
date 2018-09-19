.. _cohort:

cohort
======

Limits Solr query patients by ones matching the cohort.



Functions
---------

**OHDSI.getCohort(cohortId)**

Returns a list of patients matching the OHDSI cohort id. Will limit patients in the Solr query.


::

    cohort SocialSupportPatients:OHDSI.getCohort(100);


`cohort` can then be passed as an argument in tasks. For example:

::

    define Widowed:
        Clarity.ProviderAssertion({
            cohort:SocialSupportPatients,
            termset:[WidowedTerms]
        });

