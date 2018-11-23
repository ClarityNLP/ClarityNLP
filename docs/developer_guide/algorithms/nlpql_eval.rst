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
mathematical expressions produce a numerical result from data contained in a
single task result document. The numerical result gets written to a new
MongoDB document.

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
needed to distinguish the data belonging to each separate run.

We also see URLs for 'intermediate' and 'main' phenotype results. These are
convenience API functions that cause CSV files to be generated. The data in the
intermediate result CSV file contains the output from each NLPQL
task not marked as ``final``, while the main result CSV contains the final
task(s). The CSV can be viewed in Excel or in another spreadsheet application
and is a convenient technique for viewing results for testing.

Example
-------

Here is an NLPQL file that will be used to illustrate these concepts. This
is a modified version of the ``sepsis.nlpql`` sample file that omits
the OMOP cohort and uses fewer terms. It also adds a 3-way AND for purposes
of illustration.
::
    limit 300;

    // Phenotype library name
    phenotype "Sepsis Lite" version "1";

    include ClarityCore version "1.0" called Clarity;

    documentset ProviderNotes:
        Clarity.createReportTagList([
            "Physician", "Nurse", "Note", "Discharge Summary"
        ]);

    termset RigorsTerms: [
        "Rigors",
        "Rigoring",
        "Shivers",
        "Shivering"
    ];

    termset DyspneaTerms: [
        "Labored respiration",
        "Shortness of breath",
        "Short of breath",
        "SOB",
        "Respiration labored",
        "Labored breathing",
        "Dyspnea",
        "Difficulty breathing"
    ];

    termset NauseaTerms: [
        "Nausea",
        "Nauseated",
        "Nauseous",
        "Queasy"
    ];

    termset VomitingTerms: [
        "Vomiting",
        "Vomited",
        "Vomit",
        "Emesis",
        "Hyperemesis",
        "N/V"
    ];

    termset TachycardiaTerms: [
        "Tachycardia",
        "Tachycardic",
        "Rapid HR",
        "Tachy"
    ];

    termset ShockTerms: [
        "Shock"
    ];

    termset TempTerms: [
        "temp",
        "temperature",
        "t"
    ];

    // nlpql_feature "hasRigors", pipeline_type "ProviderAssertion"
    define hasRigors:
        Clarity.ProviderAssertion({
            termset: [RigorsTerms],
            documentset: [ProviderNotes]
        });

    // nlpql_feature "hasDyspnea"
    define hasDyspnea:
        Clarity.ProviderAssertion({
            termset: [DyspneaTerms],
            documentset: [ProviderNotes]
        });

    // nlpql_feature "hasNausea"
    define hasNausea:
        Clarity.ProviderAssertion({
            termset: [NauseaTerms],
            documentset: [ProviderNotes]
        });

    // nlpql_feature "hasVomiting"
    define hasVomiting:
        Clarity.ProviderAssertion({
            termset: [VomitingTerms],
            documentset: [ProviderNotes]
        });

    // nlpql_feature "hasShock"
    define hasShock:
        Clarity.ProviderAssertion({
            termset: [ShockTerms],
            documentset: [ProviderNotes]
        });

    // nlpql_feature "hasTachycardia"
    define hasTachycardia:
        Clarity.ProviderAssertion({
            termset: [TachycardiaTerms],
            documentset: [ProviderNotes]
        });

    // nlpql_feature "Temperature", pipeline_type "ValueExtraction"
    define Temperature:
        Clarity.ValueExtraction({
            termset:[TempTerms],
            minimum_value: "96",
            maximum_value: "106"
        });

    // patient context, want to find patient IDs ("subject" field)
    context Patient;

    // single-row mathematical expression, 
    define hasFever:
        where Temperature.value >= 100.4;

    // multi-row logic expression
    define hasDNV:
        where hasDyspnea AND hasNausea AND hasVomiting;

    // multi-row logic expression
    define hasSepsisSymptoms:
        where hasRigors OR hasDyspnea OR hasVomiting OR hasNausea OR hasShock OR hasTachycardia;

    // multi-row logic expression
    define final hasSepsis:
        where hasFever AND hasSepsisSymptoms;

    
The NLPQL statements define a set of documents as well as several termsets
related to sepsis. Following the termset list is a set of ProviderAssertions
``hasRigors``, ``hasDypsnea``, etc. These each generate a set of
``ProviderAssertion`` result documents having the fields listed in the
"Results" section of the ``ProviderAssertion`` API documentation:
https://claritynlp.readthedocs.io/en/latest/api_reference/nlpql/provider_assert.html.

After the ProviderAssertions is a ``ValueExtraction`` task called
``Temperature`` that searches the input documents for occurrences of
``TempTerms`` and extracts the associated temperature values. This value
extraction task generates a different set of result fields from the
provider assertion tasks; these fields can be found in the API documentation
for ``ValueExtraction``:
https://claritynlp.readthedocs.io/en/latest/api_reference/nlpql/valueextractor.html.

Following the ValueExtraction task is a ``context`` statement that sets the
context to ``Patient``. The context is important for logic operations, and it
controls the conditions for comparing two sets. We will have much more to say
about context later in this document.

The ``hasFever`` statement defines a mathematical expression that compares each
extracted temperature value with ``100.4`` and generates a new result document
if the condition is satisfied. This result document has its ``nlpql_feature``
field set to ``hasFever``, and it includes the source fields from the
``ValueExtraction`` result.

Three logical expressions follow the ``hasFever`` definition. The first is a
three-way logical AND, the second is a six-way logical OR, and the last is a
two way AND defining the ``hasSepsis`` condition. These logic operators are
applied to **sets** of results as a whole. The ``hasDNV`` expression is
evaluated for **all** ``hasDyspnea``, ``hasNausea``, and ``hasVomiting``
result documents, and a new document is generated only if any are found
satisfying all three conditions simultaneously.

The presence of the ``final`` modifier means that any ``hasSepsis`` results
will be written to the ``main_results_csv`` file instead of the intermediate
results CSV file.

Intermediate Results File
------------------------

A run of the above NLPQL file on the MIMIC-III data set generated an
intermediate result file of 7852 rows. The first row contains the column
definitions, and the subsequent rows are interpreted as follows:

+-----------+----------+--------------------+-------------------+
| Start Row | End Row  | NLPQL Feature      | Pipeline Type     |
+-----------+----------+--------------------+-------------------+
| 2         |  482     | hasRigors          | ProviderAssertion |
+-----------+----------+--------------------+-------------------+
| 483       |  1031    | hasDyspnea         | ProviderAssertion |
+-----------+----------+--------------------+-------------------+
| 1032      |  1691    | hasNausea          | ProviderAssertion |
+-----------+----------+--------------------+-------------------+
| 1692      |  2541    | hasVomiting        | ProviderAssertion |
+-----------+----------+--------------------+-------------------+
| 2542      |  2924    |  hasShock          | ProviderAssertion |
+-----------+----------+--------------------+-------------------+
| 2925      |  3633    |  hasTachycardia    | ProviderAssertion |
+-----------+----------+--------------------+-------------------+
| 3634      |  3999    |  Temperature       | ValueExtraction   |
+-----------+----------+--------------------+-------------------+
| 4000      |  4216    |  hasFever          | ValueExtractor    |
+-----------+----------+--------------------+-------------------+
| 4217      |  4220    |  hasDNV            | ProviderAssertion |
+-----------+----------+--------------------+-------------------+
| 4221      |  7852    |  hasSepsisSymptoms | ProviderAssertion |
+-----------+----------+--------------------+-------------------+

Note that the number of rows with the NLPQL feature ``hasSepsis`` is equal to
7852 - 4221 + 1 = 3632 rows, which is the same as the total number of rows
with features ``hasRigors``, ``hasDyspnea``, ``hasNausea``, ``hasVomiting``,
``hasShock``, and ``hasTachycardia``. The condition ``hasSepsisSymptoms`` is
defined by a logical OR of these six features, so each individual feature is
equivalent to the condition ``hasSepsisSymptoms``. Thus the cardinality of the
set ``hasSepsisSymptoms`` is the sum of the cardinalities of the individual
feature sets.

The ``hasFever`` condition spans 217 rows, which is less than the 366 rows
spanned by the ``Temperature`` measurements. The obvious reason for this is
that some of the extracted temperatures are less than the cutoff value of
100.4.

The ``hasDNV`` condition is defined by a logical AND of the individual
features ``hasDyspnea``, ``hasNausea``, and ``hasVomiting``. The evaluation
of this condition requires an intersection of these three component sets.
As mentioned above, the context field determines the meaning of set
intersection. This will be discussed in more detail below, but suffice it
to say that a common value of the ``subject`` field is sufficient to determine
membership in the intersection set. There are only four rows satisfying
this condition, all for patient ID 9347.

Array Arguments
---------------

All of the evaluated results in the intermediate file produce array arguments.
An "evaluated result" is a result that is not the direct output of either a
built-in or custom ClarityNLP task. Hence the ``hasFever``, ``hasDNV``, and
``hasSepsisSymptoms`` entries contain array arguments. The reason for array
arguments is that any computed result depends on source arguments that
participate equally in determining the final result. These source arguments
are accumulated as elements of arrays during evaluation and carried along as
the computation progresses.

To illustrate, the ``reportID`` field for the ``hasDNV`` entries is a
three-component array, since the ``hasDNV`` condition is defined by a three-
way logical AND. These entries from the run described above are all equal
to ``['1259487', '1277786', '1277788']``, which are the report IDs of the
MIMIC-III source documents from which these results were generated.


Main Results File
------------------------

The main results file contains the results of all NLPQL expressions marked with
the ``final`` keyword. In the NLPQL example above there is only one such
expression, that for ``hasSepsis``. Evaluation of this logical expression
is carried out exacly as for those of the intermediate results.

One difference between the intermediate and final results is that array
fields are NOT generated for the final result set. Array fields are
flattened into individual numbered fields with numeric suffixes of ``_1``,
``_2``, etc.


Direct MongoDB Queries
======================


