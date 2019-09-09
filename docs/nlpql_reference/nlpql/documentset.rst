.. _documentset:

documentset
===========
ClarityNLP modules in NLPQL that defines how documents are to be queried in Solr.

Functions
---------

Clarity.createReportTagList
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Uses the ClarityNLP document ontology. Mapped using the Report Type Mapper.



::

    documentset RadiologyNotes:
        Clarity.createReportTagList(["Radiology"]);


----

Clarity.createDocumentSet
~~~~~~~~~~~~~~~~~~~~~~~~~

Uses arguments to build a custom Solr query to retrieve document set. All arguments are optional, but at least one must be present.

=====================  ================  ===============================================================
         Name                 Type                                        Notes
=====================  ================  ===============================================================
report_types           List[str]         List of report types. Corresponds to `report_types` in Solr.
report_tags            List[str]         List of report tags. Report tags mapped to document ontology.
source                 str OR List[str]  List of sources to map to. Use array of strings or string, separated by commas.
filter_query           str               Use single quote (') to quote. Corresponds to Solr `fq` parameter. See `here <https://lucene.apache.org/solr/guide/7_4/common-query-parameters.html#fq-filter-query-parameter>`_.*
query                  str               Use single quote (') to quote. Corresponds to Solr `q` parameter. See `here <https://lucene.apache.org/solr/guide/7_4/the-standard-query-parser.html#the-standard-query-parser>`_.*
=====================  ================  ===============================================================

\* See more about the ClarityNLP Solr fields `here <../../developer_guide/technical_background/solr.html>`_.


::

    documentset AmoxDischargeNotes:
     Clarity.createDocumentSet({
         "report_types":["Discharge summary"],
         "report_tags": [],
         "filter_query": "",
         "source": ["MIMIC","FDA Drug Labels"],
         "query":"report_text:amoxicillin"});



----

Clarity.createReportTypeList
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Uses an explicit report type list of string to match from the `report_type` field.


::

    documentset ChestXRDocs:
        Clarity.createReportTypeList(["CHEST XR", "CHEST X-RAY"]);


----
