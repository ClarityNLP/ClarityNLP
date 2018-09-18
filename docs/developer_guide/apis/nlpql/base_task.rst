.. _base_task:

BaseTask
========


Arguments
---------

=====================  =====================  ==================== ======================================
         Name                 Type                   Required                              Notes
=====================  =====================  ==================== ======================================
termset                :ref:`termset`         See implementation
documentset            :ref:`documentset`     No
cohort                 :ref:`cohort`          No
=====================  =====================  ==================== ======================================


Results
-------


=====================  ================  ====================================================================
         Name                 Type                                              Notes
=====================  ================  ====================================================================
pipeline_type          str               Pipeline type internal to ClarityNLP.
pipeline_id            int               Pipeline ID internal to ClarityNLP.
job_id                 int               Job ID
batch                  int               Batch number of documents
owner                  str               Job owner
nlpql_feature          str               Feature used in NLPQL `define`
inserted_date          date              Date result written to data store
concept_code           int               Code specified by user to assign to OMOP concept id.
phenotype_final        bool              `final` flag designated in NLPQL; displays in final results
report_id              str               Document report ID, if document level result
subject                str               Document subject/patient, if document level result
report_date            str               Document report date, if document level result
report_type            str               Document report type, if document level result
source                 str               Document source, if document level result
solr_id                str               Document Solr `id` field, if document level result
=====================  ================  ====================================================================


Functions
---------

**run()**

Main function that sets up documents and runs the task execution.

----

**output()**

Gets Luigi file, used for job communication or temp output

----

**set_name(name)**

Sets name of task

----

**write_result_data(temp_file: File, mongo_client: MongoClient, doc: dict, data: dict, prefix: str='', phenotype_final: bool=False)**

Writes results to MongoDB

----

**write_multiple_result_data(temp_file: File, mongo_client: MongoClient, doc: dict, data: list, prefix: str='')**

Writes results to MongoDB as a list


----

