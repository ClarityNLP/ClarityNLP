NLPQL Expression Evaluation
***************************

Overview
========

In this section we describe the mechanisms that ClarityNLP uses to evaluate
NLPQL expressions. NLPQL expressions can either be mathematical or logical in
nature. Expression evaluation takes place after ClarityNLP tasks have finished
running and have written their individual results to MongoDB.

Recall that the processing stages for a ClarityNLP job proceed roughly as
follows:

1. Parse the NLPQL file and determine which NLP tasks to run.
2. Formulate a Solr query to find relevant source documents, partition the
   source documents into subsets, and assign subsets to tasks.
3. Run the tasks in parallel and write individual task results to MongoDB.
   Each individual result from an NLP task comprises a *task result document*
   in the Mongo database. Here the term *document* is taken from MongoDB
   parlance. Result documents consist of key-value pairs and should not be
   confused with Solr source documents, which are electronic health records.
4. Evaluate NLPQL expressions using the task result documents as the source
   data. Write expression evaluation results to MongoDB as separate result
   documents.

We now turn our attention to the operations in step 4. We should state at the
outset that the descriptions below apply to an expression evaluator based on
MongoDB. This evaluator is currently in a testing phase and must be explicitly
enabled by adding the following line to the project.cfg file in the ``[local]``
section:
::
   evaluator=mongo

If this line is absent or is commented out with a `#` character, a Pandas-based
evaluator will be used. The Pandas evaluator uses different techniques from
those described below.

NLPQL Expressions
-----------------

An NLPQL mathematical expression is found in a ``define`` statement such as:
::
   define hasFever:
        where Temperature.value >= 100.4;

The ``where`` portion of the statement is the mathematical expression. These
expressions feature mathematical operations on variables of the form
``nlpql_feature.variable_name`` such as ``Temperature.value``,
``LesionMeasurement.dimension_X``, etc. They can also include numeric literals
such as ``100.4``.

NLPQL mathematical expressions produce a numerical result from data contained
in a **single** task result document. Since each task result document
comprises a row in the intermediate results CSV file, the evaluation of
mathematical expressions is also called a **single-row operation**.  The
numerical result from the expression evaluation is written to a new MongoDB
result document which has an ``_id`` field different from that of its source
document.

An NLPQL logical expression is also found in a ``define`` statement and
involves the logical operators ``AND``, ``OR``, and ``NOT``, such as:
::

   define hasSepsis:
       where hasFever AND hasSepsisSymptoms;

The ``where`` portion of the statement is the logical expression. NLPQL logical
expressions use data from **one or more** task result documents and compute a
new set of results, which get written back to MongoDB as new result documents.
The evaluation of a logical expressions is also called a
**multi-row operation**.

The evaluation mechanisms used for mathematical and logical operations are
quite different. To fully understand the issues involved, it helps to 
understand the structure of the 'intermediate' and 'final' phenotype results.

Phenotype Result CSV Files
--------------------------

Upon submission of a new job, ClarityNLP prints information to stdout that
looks similar to this:
::
    HTTP/1.0 200 OK
    Content-Type: text/html; charset=utf-8
    Content-Length: 1024
    Access-Control-Allow-Origin: *
    Server: Werkzeug/0.14.1 Python/3.6.4
    Date: Fri, 23 Nov 2018 18:40:38 GMT
    {
       "job_id": "11108",
       "phenotype_id": "11020",
       "phenotype_config": "http://localhost:5000/phenotype_id/11020",
       "pipeline_ids": [
            12529,
            12530,
            12531,
            12532,
            12533,
            12534,
            12535
        ],
        "pipeline_configs": [
            "http://localhost:5000/pipeline_id/12529",
            "http://localhost:5000/pipeline_id/12530",
            "http://localhost:5000/pipeline_id/12531",
            "http://localhost:5000/pipeline_id/12532",
            "http://localhost:5000/pipeline_id/12533",
            "http://localhost:5000/pipeline_id/12534",
            "http://localhost:5000/pipeline_id/12535"
        ],
        "status_endpoint": "http://localhost:5000/status/11108",
        "results_viewer": "?job=11108",
        "luigi_task_monitoring": "http://localhost:8082/static/visualiser/index.html#search__search=job=11108",
        "intermediate_results_csv": "http://localhost:5000/job_results/11108/phenotype_intermediate",
        "main_results_csv": "http://localhost:5000/job_results/11108/phenotype"
    }

Here we see various items relevant to the job submission. Each submission
receives a *job_id*, which is a unique numerical identifier for the run.
ClarityNLP writes all results from all jobs to MongoDB, so the job_id is
needed to distinguish the data belonging to each run.

We also see URLs for 'intermediate' and 'main' phenotype results. These are
convenience API functions that cause CSV files to be generated. The data in the
intermediate result CSV file contains the output from each NLPQL
task not marked as ``final``. The main result CSV contains the results
from any final tasks or final expression evaluations. The CSV file can be
viewed in Excel or in another spreadsheet application.

Each NLP task generates a result document distinguished by a particular value
of the ``nlpql_feature`` field. For instance, the statement
::
   define hasFever:
        where Temperature.value >= 100.4;

generates a set of rows in the intermediate CSV file with the
``nlpql_feature`` field set to ``hasFever``.  The NLP tasks
::
    // nlpql_feature `hasRigors`
    define hasRigors:
        Clarity.ProviderAssertion({
            termset: [RigorsTerms],
            documentset: [ProviderNotes]
        });

    // nlpql_feature `hasDyspnea`
    define hasDyspnea:
        Clarity.ProviderAssertion({
            termset: [DyspneaTerms],
            documentset: [ProviderNotes]
        });

generate two blocks of rows in the CSV file, the first block having the
``nlpql_feature`` field set to ``hasRigors`` and the next block having it
set to ``hasDyspnea``.  The different nlpql_feature blocks appear in order
as listed in the source NLPQL file. The presence of these nlpql_feature
blocks makes locating the results of each NLP task a relatively simple
matter.

Evaluation of Single-Row Expressions
====================================

