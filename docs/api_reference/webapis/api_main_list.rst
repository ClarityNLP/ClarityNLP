/kill_job/<int:job_id>
----------------------
GET pids of NLPQL tasks. Attemps to kill running Luigi workers. Will only work when NLP API and Luigi are deployed on the same instance.


/measurement_finder
-------------------
POST JSON to extract measurements. Sample input JSON `here <https://github.com/ClarityNLP/ClarityNLP/blob/master/nlp/samples/library_inputs/sample_measurement_finder.json>`_.


/named_entity_recognition
-------------------------
POST JSON to run spaCy's NER. Sample input JSON `here <https://github.com/ClarityNLP/ClarityNLP/blob/master/nlp/samples//library_inputs/sample_ner.json>`_.


/nlpql
------
POST NLPQL plain text file to run phenotype against data in Solr. Returns links to view job status and results.
Learn more about NLPQL :ref:`here<intro-overview>` and see samples of NLPQL `here <https://github.com/ClarityNLP/ClarityNLP/tree/master/nlpql>`_.

.. _nlpql_tester_api:

/nlpql_tester
-------------
POST NLPQL text file to test if parses successfully. Either returns phenotype JSON or errors, if any.
Learn more about NLPQL :ref:`here<intro-overview>` and see samples of NLPQL `here <https://github.com/ClarityNLP/ClarityNLP/tree/master/nlpql>`_.


/nlpql_expander
---------------
POST to expand NLPQL termset macros. Read more :ref:`here<macros>`.


/nlpql_samples
--------------
GET a list of NLPQL samples.


/nlpql_text/<string:name>
-------------------------
GET NLPQL sample by name.


/phenotype
----------
POST Phenotype JSON to run phenotype against data in Solr. Same as posting to `/nlpql`, but with the finalized JSON structured instead of raw NLPQL. Using `/nlpql` will be preferred for most users.
See sample `here <https://github.com/ClarityNLP/ClarityNLP/tree/master/nlp/samples/phenotype>`_.


/phenotype_feature_results/<int:job_id>/<string:feature>/<string:subject>
-------------------------------------------------------------------------
GET phenotype results for a given feature, job and patient/subject.


/phenotype_id/<int:phenotype_id>
--------------------------------
GET a pipeline JSON based on the phenotype_id.


/phenotype_job_by_id/<string:id>
--------------------------------
GET a phenotype jobs JSON by id.


/phenotype_jobs/<string:status_string>
--------------------------------------
GET a phenotype job list JSON based on the job status.


/phenotype_paged_results/<int:job_id>/<string:phenotype_final_str>
------------------------------------------------------------------
GET paged phenotype results.


/phenotype_result_by_id/<string:id>
-----------------------------------
GET phenotype result for a given mongo identifier.


/phenotype_results_by_id/<string:ids>
-------------------------------------
GET phenotype results for a comma-separated list of ids.


/phenotype_structure/<int:id>
-----------------------------
GET phenotype structure parsed out.


/phenotype_subject_results/<int:job_id>/<string:phenotype_final_str>/<string:subject>
-------------------------------------------------------------------------------------
GET phenotype results for a given subject.


/phenotype_subjects/<int:job_id>/<string:phenotype_final_str>
-------------------------------------------------------------
GET phenotype_subjects.


/pipeline
---------
POST a pipeline job (JSON) to run on the Luigi pipeline. Most users will use `/nlpql`.
Read more about pipelines `here <../../developer_guide/technical_background/pipelines.html>`_.
See sample JSON `here <https://github.com/ClarityNLP/ClarityNLP/tree/master/nlp/samples/pipelines>`_.

/pipeline_id/<int:pipeline_id>
------------------------------
GET a pipeline JSON based on the pipeline_id.


/pipeline_types
---------------
GET a list of valid pipeline types.


/pos_tagger
-----------
POST JSON to run spaCy's POS Tagger. (Only recommended on smaller text documents.) Sample input JSON `here <https://github.com/ClarityNLP/ClarityNLP/blob/master/nlp/samples//library_inputs/sample_pos_tag_text.json>`_.


/report_type_mappings
---------------------
GET a dictionary of report type mappings.


/sections
---------
GET source file for sections and synonyms.


/status/<int:job_id>
--------------------
GET status for a given job.


/term_finder
------------
POST JSON to extract terms, context, negex, sections from text. Sample input JSON `here <https://github.com/ClarityNLP/ClarityNLP/blob/master/nlp/samples/library_inputs/sample_term_finder.json>`_.


/tnm_stage
----------
POST JSON to extract TNM staging from text. Sample input JSON `here <https://github.com/ClarityNLP/ClarityNLP/blob/master/nlp/samples/library_inputs/sample_tnm_stage.json>`_.


/value_extractor
----------------
POST JSON to extract values such as BP, LVEF, Vital Signs etc. Sample input JSON `here <https://github.com/ClarityNLP/ClarityNLP/blob/master/nlp/samples//library_inputs/sample_value_extractor.json>`_.
