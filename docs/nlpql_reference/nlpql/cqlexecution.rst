.. _cqlexecutiontask:

Clarity.CQLExecutionTask
************************

Description
-----------

This is a custom task that allows ClarityNLP to execute
`CQL <https://cql.hl7.org/>`_ (Clinical Quality Language) queries embedded in
NLPQL files. ClarityNLP directs CQL code to a running instance of the
`CQL Engine <https://github.com/gt-health/cql_execution_service>`_, which
processes the CQL and translates it into requests for a FHIR 
`(Fast Healthcare Interoperability Resources) <https://www.hl7.org/fhir/overview.html>`_
server. The FHIR server runs the query and retrieves structured data for
a **single** patient. The data returned from the CQL query appears in the
results for the job associated with the NLPQL file.

The CQL query requires several FHIR-related parameters, such as the patient
ID, the URL of the FHIR server, and several others to be described below.
These parameters can either be specified in the NLPQL file itself or supplied
by `ClarityNLP as a Service <https://github.com/ClarityNLP/ClarityNLPaaS>`_.

Documentsets for Unstructured and Structured Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ClarityNLP was originally designed to process *unstructured* text documents.
In a typical workflow the user specifies a :ref:`documentset` in an NLPQL
file, along with the tasks and NLPQL expressions needed to process the
documents. ClarityNLP issues a Solr query to retrieve the matching documents,
which it divides into batches. ClarityNLP launches a separate task per batch
to process the documents in parallel. The number of tasks spawned by the Luigi
scheduler depends on the number of *unstructured* documents returned by the
Solr query. In general, the results obtained include data from multiple
patients.

ClarityNLP can also support single-patient structured CQL queries with a few
simple modifications to the documentset. For CQL queries the documentset must
be specified in the NLPQL file so that it limits the unstructured documents to
those for a **single** patient only. FHIR is essentially a single-patient
readonly data retrieval standard. Each patient with data stored on a FHIR
server has a unique patient ID. This ID must be used in the documentset
statement and in the ``Clarity.CQLExecutionTask`` body itself, as illustrated
below. The documentset specifies the unstructured data for the patient, and
the CQL query specifies the structured data for the patient.

Relevant FHIR Parameters
------------------------

These parameters are needed to connect to the CQL Engine and the FHIR server,
evaluate the CQL statements, and retrieve the results. They can be provided
directly as parameters in the ``CQLExecutionTask`` statement (see below), or
indirectly via `ClarityNLPaaS <https://github.com/ClarityNLP/ClarityNLPaaS>`_:

=================================  =================================================
Parameter                          Meaning
=================================  =================================================
fhir_version                       Either DSTU2 or DSTU3
cql_eval_url                       URL of the FHIR server's CQL Execution Service
patient_id                         Unique ID of patient whose data will be accessed
fhir_data_service_uri              FHIR server base URL
cql                                CQL code surrounded by """ (triple quotes)
=================================  =================================================

Time Filtering
--------------

This task supports a time filtering capability for the CQL query results. Two
**optional** parameters, ``time_start`` and ``time_end``, can be used to
specify a time window. Any results whose timestamps lie *outside* of this
window will be discarded. If the time window parameters are omitted, all
results from the CQL query will be kept.

The ``time_start`` and ``time_end`` parameters must be quoted strings with
syntax as follows:
::
   DATETIME(YYYY, MM, DD, HH, mm, ss)
   DATE(YYYY, MM, DD)
   EARLIEST()
   LATEST()

An optional offset in days can be added or subtracted to these:
::
   LATEST() - 7d
   DATE(2010, 7, 15) + 20d

The offset consists of digits followed by a ``d`` character, indicating days.

**Both ``time_start`` and ``time_end`` are assumed to be expressed in**
**Universal Coordinated Time (UTC).**

Here are some time window examples:

1. Discard any results not occurring in March, 2016:
::
   "time_start":"DATE(2016, 03, 01)",
     "time_end":"DATE(2016, 03, 31)"

2. Keep all results within one week of the most recent result:
::
   "time_start":"LATEST() - 7d",
     "time_end":"LATEST()"

3. Keep all results within a window of 20 days beginning July 4, 2018, at 3 PM:
::
   "time_start":"DATETIME(2018, 7, 4, 15, 0, 0)",
     "time_end":"DATETIME(2018, 7, 4, 15, 0, 0) + 20d"

Note that the strings to the left and right of the colon must be surrounded
by quotes.


Example
-------

Here is an example of how to use the ``CQLExecutionTask`` directly, *without*
using ClarityNLPaaS. In the text box below there is a documentset creation
statement followed by an invocation of the ``CQLExecutionTask``. The
documentset consists of all indexed documents for patient ``99999`` with a
``source`` field equal to ``MYDOCS``.  These documents are specified explicitly
in the ``CQLExecutionTask`` invocation that follows, to limit the source
documents to those for patient 99999 only.

The ``task_index`` parameter is used in an interprocess communication scheme
for controlling task execution. ClarityNLP's Luigi scheduler creates worker
task clones in proportion to the number of *unstructured* documents in the
documentset. Only a single task from among the clones should actually connect
to the FHIR server, run the CQL query, and retrieve the structured data.

ClarityNLP uses the ``task_index`` parameter to identify the single task
that should execute the CQL query. Any NLPQL file can contain multiple
invocations of ``Clarity.CQLExecutionTask``. Each of these should have
a ``task_index`` parameter, and they should be numbered sequentially starting
with 0.  In other words, each ``define`` statement containing an invocation
of ``Clarity.CQLExecutionTask`` should have a unique value for the zero-based
``task_index``. If you limit your CQL use to a single query per NLPQL file,
the value of ``task_index`` should always be set to 0.

The ``patient_id`` parameter identifies the patient whose data will be accessed
by the CQL query. This ID should match that specified in the documentset
creation statement.

The remaining parameters from the table above are set to values appropriate for
GA Tech's FHIR infrastructure. You should change them to match your FHIR
installation.

The ``cql`` parameter is a triple-quoted string containing the CQL query. the
triple quotes can be comprised of either single or double quotes.
This CQL code is assumed to be syntactically correct and is passed to the FHIR
server's CQL evaluation service unaltered. All CQL code should be checked for
syntax errors and other problems prior to its use in an NLPQL file.

This example omits the optional time window parameters.

::
   
   documentset PatientDocs:
    Clarity.createDocumentSet({
        "filter_query":"source:MYDOCS AND subject:99999"
    });

    define WBC:
        Clarity.CQLExecutionTask({
            documentset: [PatientDocs],
            "task_index": 0,
            "fhir_version":"DSTU2",
            "patient_id":"99999",
            "cql_eval_url":"https://gt-apps.hdap.gatech.edu/cql/evaluate",
            "fhir_data_service_uri":"https://apps.hdap.gatech.edu/gt-fhir/fhir/",
            cql: """
                 library Retrieve2 version '1.0'

                 using FHIR version '3.0.0'

                 include FHIRHelpers version '3.0.0' called FHIRHelpers

                 codesystem "LOINC": 'http://loinc.org'

                 define "WBC": Concept {
                     Code '26464-8' from "LOINC",
                     Code '804-5' from "LOINC",
                     Code '6690-2' from "LOINC",
                     Code '49498-9' from "LOINC"
                 }

                 context Patient

                 define "result":
                     [Observation: Code in "WBC"]
                 """
        });

        context Patient;

Extends
-------
:ref:`base_task`


Arguments
---------

=================================  ===================  ========= ======================================
         Name                      Type                 Required  Notes
=================================  ===================  ========= ======================================
documentset                        :ref:`documentset`   Yes       Documents for a SINGLE patient only.
task_index                         int                  Yes       Each CQLExecutionTask statement must have a unique value of this index.
fhir_version                       str                  No        Either "DSTU2" (default) or "STU3"
patient_id                         str                  Yes       CQL query executed on FHIR server for this patient.
cql_eval_url                       str                  Yes       See table above.
fhir_data_service_uri              str                  Yes       See table above.
cql                                triple-quoted str    Yes       Properly-formatted CQL query, sent verbatim to FHIR server.
time_start                         str                  No        Optional, discard results with timestamp < time_start
time_end                           str                  No        Optional, discard results with timestamp > time_end
=================================  ===================  ========= ======================================

Results
-------

The specific fields returned by the CQL query are dependent on the type of FHIR
resource that contains the data. ClarityNLP can process the FHIR resources in
the next table:

+--------------------------+
| FHIR Resource Type       |
+==========================+
| Patient                  |
+--------------------------+
| Procedure                |
+--------------------------+
| Condition                |
+--------------------------+
| Observation              |
+--------------------------+
| MedicationOrder          |
+--------------------------+
| MedicationRequest        |
+--------------------------+
| MedicationStatement      |
+--------------------------+
| MedicationAdministration |
+--------------------------+

ClarityNLP returns a *flattened* version of the JSON representation of each
resource, the meaning of which is explained
`here <https://github.com/amirziai/flatten>`_. Essentially, the key for a
flattened JSON object contains underscores for each nested object boundary
(delimited by the ``{`` character), and a numeric index for each array
boundary (delimited by the ``[`` character).

To illustrate, consider this JSON object:
::
   {
       "field1":"value1",
       "field2":{"field3":"value3"},
       "field4":[{"field5":"value5", "field6":"value6"}],
       "field7":[{"field8":[{"field9":"value9", "field10":"value10"}]}]
   }

The flattened version is:
::
   {
       "field1":"value1",
       "field2_field3":"value3",
       "field4_0_field5":"value5",
       "field4_1_field6":"value6",
       "field7_0_field8_0_field9":"value9",
       "field7_0_field8_1_field10":"value10"
   }

The FHIR resource data structures can be represented as nested JSON objects.
The DSTU2 resources can be found `here <http://hl7.org/fhir/DSTU2/resourcelist.html>`_
and the DSTU3 resources can be found `here <http://hl7.org/fhir/STU3/resourcelist.html>`_.

For a specific FHIR example, consider the DSTU2
`general condition example <http://hl7.org/fhir/DSTU2/condition-example.json.html>`_:
::
   {
       "resourceType": "Condition",
       "id": "example",
       "text":
       {
           "status": "generated",
           "div": "<div>Severe burn of left ear (Date: 24-May 2012)</div>"
       },
       "patient":
       {
           "reference": "Patient/example"
       },
       "code":
       {
           "coding":
           [
               {
                   "system": "http://snomed.info/sct",
                   "code": "39065001",
                   "display": "Burn of ear"
               }
           ],
           "text": "Burnt Ear"
       },
       "category":
       {
           "coding":
           [
               {
                   "system": "http://hl7.org/fhir/condition-category",
                   "code": "diagnosis",
                   "display": "Diagnosis"
               },
               {
                   "fhir_comments":
                   [
                       "  and also a SNOMED CT coding  "
                   ],
                   "system": "http://snomed.info/sct",
                   "code": "439401001",
                   "display": "Diagnosis"
               }
           ]
       },
       "verificationStatus": "confirmed",
       "severity":
       {
           "coding":
           [
               {
                   "system": "http://snomed.info/sct",
                   "code": "24484000",
                   "display": "Severe"
               }
           ]
       },
       "onsetDateTime": "2012-05-24",
       "bodySite":
       [
           {
               "coding":
               [
                   {
                       "system": "http://snomed.info/sct",
                       "code": "49521004",
                       "display": "Left external ear structure"
                   }
               ],
               "text": "Left Ear"
           }
       ]
    }

The flattened version of this example, with quotes removed for clarity, is:
::
   	resourceType: Condition
	id: example
	text_status: generated
	text_div: <div xmlns="http://www.w3.org/1999/xhtml">Severe burn of left ear (Date: 24-May 2012)</div>
	clinicalStatus: active
	verificationStatus: confirmed
	category_0_coding_0_system: http://hl7.org/fhir/condition-category
	category_0_coding_0_code: encounter-diagnosis
	category_0_coding_0_display: Encounter Diagnosis
	category_0_coding_1_system: http://snomed.info/sct
	category_0_coding_1_code: 439401001
	category_0_coding_1_display: Diagnosis
	severity_coding_0_system: http://snomed.info/sct
	severity_coding_0_code: 24484000
	severity_coding_0_display: Severe
	code_coding_0_system: http://snomed.info/sct
	code_coding_0_code: 39065001
	code_coding_0_display: Burn of ear
	code_text: Burnt Ear
	bodySite_0_coding_0_system: http://snomed.info/sct
	bodySite_0_coding_0_code: 49521004
	bodySite_0_coding_0_display: Left external ear structure
	bodySite_0_text: Left Ear
	subject_reference: Patient/example
	onsetDateTime: 2012-05-24 00:00:00
	date_time: 2012-05-24 00:00:00
	len_code_coding: 1
	len_severity_coding: 1
	len_bodySite: 1
	len_bodySite_0_coding: 1
	len_category: 1
	len_category_0_coding: 2
	value_name: Burn of ear

Note the additional fields at the end, such as ``date_time`` and the fields
prefixed with ``len_``. ClarityNLP adds the ``date_time`` field to enable
time sorting on the results (see above). The ``len_`` prefixed fields
provide the lengths of all lists in the flattened data. These are convenience
fields, inserted so that consumers of the data will not have to separately
determine the presence and size of the embedded lists.

The exact set of fields returned for the different FHIR resources depends
on the nature and complexity of the FHIR server's data. The documentation
for the `DSTU2 <http://hl7.org/fhir/DSTU2/resourcelist.htm>`_ and
`DSTU3 <http://hl7.org/fhir/STU3/resourcelist.html>`_ resources can be used
to interpret the results.

Collector
---------
No
