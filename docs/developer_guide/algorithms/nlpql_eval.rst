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



