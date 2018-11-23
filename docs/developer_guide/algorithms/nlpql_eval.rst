NLPQL Expression Evaluation
***************************

Overview
========

In this section we describe the mechanisms that ClarityNLP uses to evaluate
NLPQL expressions. NLPQL expressions can either be mathematical or logical in
nature. Expression evaluation takes place after ClarityNLP tasks have finished
running and have written their individual results to MongoDB. Each individual
result written to MongoDB is called a 'task result document'. The term
*document* is taken from MongoDB parlance. Result documents consist of
key-value pairs and should not be confused with Solr source documents,
which are electronic health records.

An NLPQL mathematical expression is found in a ``define`` statement such as:
::
   define hasFever:
        where Temperature.value >= 100.4;

The ``where`` portion of the statement is the mathematical expression. NLPQL
mathematical expressions cause a numerical result to be computed from data
contained in a single task result document. The numerical result
gets written to a new MongoDB document.

An NLPQL logical expression is also found in a ``define`` statement and
involves the logical operators ``AND``, ``OR``, and ``NOT``, such as:
::

   define hasSepsis:
       where hasFever AND hasSepsisSymptoms;

The ``where`` portion of the statement is the logical expression. NLPQL logical
expressions use data from one or more task result documents and compute a new set
of results, which get written back to MongoDB as new result documents.

The evaluation mechanisms used for mathematical and logical operations are
quite different. To fully understand the issues involved, we will first need
to understand the meaning of the 'intermediate' and 'final' phenotype results.

Intermediate and Final Phenotype Results
----------------------------------------

Upon submission of a new job, ClarityNLP prints information to stdout that
looks similar to this:
::
   HTTP/1.0 200 OK
   Content-Type: text/html; charset=utf-8
   Content-Length: 628
   Access-Control-Allow-Origin: *
   Server: Werkzeug/0.14.1 Python/3.6.4
   Date: Fri, 23 Nov 2018 13:40:01 GMT
   
   {
       "job_id": "11099",
       "phenotype_id": "11011",
       "phenotype_config": "http://localhost:5000/phenotype_id/11011",
        "pipeline_ids": [
            12506
        ],
        "pipeline_configs": [
            "http://localhost:5000/pipeline_id/12506"
        ],
        "status_endpoint": "http://localhost:5000/status/11099",
        "results_viewer": "?job=11099",
        "luigi_task_monitoring": "http://localhost:8082/static/visualiser/index.html#search__search=job=11099",
        "intermediate_results_csv": "http://localhost:5000/job_results/11099/phenotype_intermediate",
        "main_results_csv": "http://localhost:5000/job_results/11099/phenotype"
    }   

Here we see various items relevant to the job submission. Each submission
receives a *job_id*, which is a unique numerical identifier for the run.
ClarityNLP writes all results from all jobs to MongoDB, so the job_id is
needed to distinguish the data belonging to each separate run.

We also see URLs for 'intermediate' and 'main' phenotype results. These are
convenience API functions that cause CSV files to be generated. The data in the
intermediate result CSV file contains the output from each NLPQL
task not marked as ``final``, while the main result CSV contains the final
task(s). The CSV can be viewed in Excel or in another spreadsheet application
and is a convenient technique for viewing results for testing.

Example
=======

Here is an NLPQL file that will be used to illustrate these concepts:
::

