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
   source documents into batches, and assign batches to computational tasks.
3. Run the tasks in parallel and write individual task results to MongoDB.
   Each individual result from an NLP task comprises a *task result document*
   in the Mongo database. Here the term *document* is used in the MongoDB
   sense, meaning an object containing key-value pairs. The MongoDB 'documents'
   should not be confused with the Solr source documents, which are electronic
   health records.
4. Evaluate NLPQL expressions using the task result documents as the source
   data. Write expression evaluation results to MongoDB as separate result
   documents.

We now turn our attention to the operations in step 4. We should state at the
outset that the descriptions below apply to an expression evaluator based on
MongoDB aggregation. This evaluator is currently in a testing phase and must
be explicitly enabled by adding the following line to the project.cfg file in
the ``[local]`` section:
::
   evaluator=mongo

If this line is absent or is commented out with a `#` character, a Pandas-based
evaluator will be used. The Pandas evaluator uses different techniques from
those described below.

So why use MongoDB aggregation to evaluate NLPQL expressions? The basic reason
is that the data resides in MongoDB, and the aggregation framework provides
a convenient and powerful mechanism on which to build an evaluation engine.
Use of anything other than MongoDB requires a set of queries to extract the data
from MongoDB; a possible network transmission if the Mongo instance is hosted
remotely; ingest into another evaluation engine; computation of results;
transmission back to the Mongo host; and insertion back into the database.
Use of the aggregation framework should prove to be much more efficient, since
all data is kept internal to MongoDB.


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
result document.

An NLPQL logical expression is also found in a ``define`` statement and
involves the logical operators ``AND``, ``OR``, and ``NOT``, such as:
::

   define hasSepsis:
       where hasFever AND hasSepsisSymptoms;

The ``where`` portion of the statement is the logical expression. Logical
expressions operate on high-level NLPQL features such as ``hasFever`` and
``hasSepsisSymptoms``, not on individual variables such as
``Temperature.value``. The presence of an ``nlpql_feature.variable_name``
token indicates that the expression is actually single-row, not multi-row.

NLPQL logical expressions use data from **one or more** task result documents
and compute a new set of results. The results get written back to MongoDB as
a set of new result documents. The evaluation of a logical expressions is also
called a **multi-row operation**, since it typically consumes and generates
multiple rows in the intermediate results CSV file.

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
ClarityNLP writes all task results from all jobs to the ``phenotype_results``
collection in a Mongo database named ``nlp``. The job_id is
needed to distinguish the data belonging to each run.

We also see URLs for 'intermediate' and 'main' phenotype results. These are
convenience APIs that export the results to CSV files. The data in the
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

The NLPQL front end parses the NLPQL file and generates a string of
whitespace-separated tokens for each expression. The token string is passed
to the evaluator which determines if it is a single-row expression (i.e. a
mathematical expression described above), a multi-row expression, or something
else that cannot be evaluated. If single-row, the string is tokenized and
the nlpql_feature and field list are extracted.  To illustrate, consider
these single-row expressions:
::
   where Temperature.value >= 100.4
   where LesionMeasurement.dimension_X < 5 AND LesionMeasurement.dimension_Y < 5
   
The first expression has an ``nlpql_feature`` of ``Temperature`` and a field list
containing the single entry ``value``. The second expression has an
``nlpql_feature`` of ``LesionMeasurement`` and a field list consisting of the
entries ``dimension_X`` and ``dimension_Y``.

Initial Pipeline Stage
----------------------

The next task for the evaluator is to convert the expression into a sequence of
MongoDB aggregation pipeline stages. This process involves the generation of an
initial ``$match`` query to filter out everything but the data for the current
job. The match query also checks for the existence of all entries in the field
list and that they have non-null values. **A simple existence check is not**
**sufficient**, since a null field actually exists but has a value that cannot
be used for computation. Hence checks for existence and a non-null value are
both necessary.

For the two examples above, the initial ``$match`` query generates a pipeline
filter stage that looks like this, assuming a job_id of 11116:
::
   // first example
   {
       $match : {
           "job_id" : 11116,
           "nlpql_feature" : {$exists:true, $ne:null},
           "value"         : {$exists:true, $ne:null}
       }
   }

   // second example
   {
       $match : {
           "job_id" : 11116,
           "nlpql_feature" : {$exists:true, $ne:null},
           "dimension_X"   : {$exists:true, $ne:null},
           "dimension_Y"   : {$exists:true, $ne:null}
       }
   }

This ``$match`` pipeline stage runs first and performs coarse filtering on the
data in the MongoDB result database. It finds only those task result documents
matching the specified job_id, and it further restricts consideration to
those documents having valid entries for the expression's fields.

Note that the validity checks imply that any fields used in NLPQL expressions
will only generate results if valid entries for those fields exist. For the
LesionMeasurement statement above, if a task result measurement is missing the
Y dimension, the NLPQL statement will not generate a result for that
particular measurment. The NLQPL example below will help make this clear.

Subsequent Pipeline Stages
--------------------------

After generation of the initial ``$match`` filter stage, the expression is
further transformed so that additional MongoDB aggregation pipeline stages
can be generated to evaluate it. The ``nlpql_feature`` is extracted and
inserted as an additional matching operation. For the examples above, the
evaluator rewrites the expressions as:
::
   (nlpql_feature == Temperature) and (value >= 100.4)
   (nlpql_feature == LesionMeasurement) and (dimension_X < 5 and dimension_Y < 5)

In this form the variables used in each statement match the fields
actually stored in the task result documents in MongoDB.

Note that both of these expressions are in infix form. Direct evaluation of an
infix expression is complicated by parenthesization and operator precedence
issues. Evaluation of a mathematical expression is greatly simplified by first
converting to postfix form. Postfix expressions require no parentheses, and a
simple stack-based evaluator can be used to evaluate them directly.

Accordingly, a conversion to postifx form takes place next. This conversion
process requires an operator precedence table. The NLPQL operator precedence
levels match those of Python and are listed here for reference. Lower numbers
imply lower precedence, so ``or`` has a lower precedence than ``and``, which
has a lower precedence than ``+``, etc.

========  ================
Operator  Precedence Value
========  ================
or        1
and       2
not       3
<         4
<=        4
>         4
>=        4
!=        4
==        4
\+        9
\-        9
\*        10
/         10
%         10
^         12
========  ================

Conversion from infix to postfix is unambiguous if operator precedence and
associativity are known. Operator precedence is given by the table above.
All NLPQL operators are left-associative except for exponentiation, which is
right-associative. The infix-to-postfix conversion algorithm is the standard
one and can be found in the function ``_infix_to_postfix`` in the file
``nlp/data_access/mongo_eval.py``.

After conversion to postfix, the two expressions above become lists of tokens:
::
   'nlpql_feature', 'Temperature', '==', 'value', '100.4', '>=', 'and'
   'nlpql_feature', 'LesionMeasurement', '==', 'dimension_X', '5', '<', 'dimension_Y', '5', '<', 'and', 'and'


The postfix expressions are then 'evaluated' by a stack-based mechanism, which
can be found in the function ``_to_mongo_pipeline`` in the file
``nlp/data_access/mongo_eval.py``. The result of the evaluation process is
**not** the actual expression value, but a set of MongoDB aggregation commands
that tell MongoDB how to compute the result. The evaluation process is
essentially string formatting that follows the aggregation syntax rules. More
information about the aggregation pipeline can be found here:
https://docs.mongodb.com/manual/aggregation/.

The pipeline actually does a ``$project`` operation and creates a new document
with a Boolean field called ``value``.  This field has a value of True or False
according to whether the source document satisfied the mathematical expression.
The ``_id`` field of the projected document matches that of the original, so
that a simple query on these ``_id`` fields can be used to recover the desired
documents.

After generation of the MongoDB commands, the aggregation pipelines for the two
examples above become:
::
    // (nlpql_feature == Temperature) and (value >= 100.4)
    {
       $match : {
           "job_id" : 11116,
           "nlpql_feature" : {$exists:true, $ne:null},
           "value"         : {$exists:true, $ne:null}
       }
    },
    {
        "$project" : {
            "value" : {
                "$and" : [
                    {"$eq"  : ["$nlpql_feature", "Temperature"]},
                    {"$gte" : ["$value", 100.4]}
                ]
            }
        }
    }
    
    // (nlpql_feature == LesionMeasurement) and (dimension_X < 5 and dimension_Y < 5)
    {
        "$match" : {
            "job_id" : 11116,
            "nlpql_feature" : {$exists:true, $ne:null},
            "dimension_X"   : {$exists:true, $ne:null},
            "dimension_Y"   : {$exists:true, $ne:null}
        }
    },
    {
        "$project" : {
            "value" : {
                "$and" : [
                    {
                        "$eq" : ["$nlpql_feature", "LesionMeasurement"]
                    },
                    {
                        "$and" : [
                            {"$lt" : ["$dimension_X", 5]},
                            {"$lt" : ["$dimension_Y", 5]}
                        ]
                    }
                ]
            }
        }
    }

The completed aggregation pipeline stages are sent to MongoDB for evaluation.
Mongo performs the initial filtering operation, applies the subsequent
pipeline stages to all surviving documents, and sets the "value" Boolean
result. A final query extracts the matching documents and writes new result
documents with an ``nlpql_feature`` field equal to that of the single-row
operation.


****
< insert lesion_test.nlpql example here>
*****


Evaluation of Multi-Row Expressions
===================================




