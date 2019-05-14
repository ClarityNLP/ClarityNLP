.. _cqleval:

Clarity.CQLExecutionTask
========================

Description
-----------

This is a custom task that allows ClarityNLP to send CQL
`(Clinical Quality Language) <https://cql.hl7.org/>`_ queries to a FHIR
`(Fast Healthcare Interoperability Resources) <https://www.hl7.org/fhir/overview.html>`_
server and retrieve structured data for a given patient.

ClarityNLP was originally designed to process unstructured text documents.
In a typical workflow the user specifies a :ref:`documentset` in an NLPQL
file, along with the tasks and expressions needed to process the documents.
ClarityNLP issues a Solr query to retrieve the matching documents, which it
separates into batches. ClarityNLP launches a different task per batch to
process the documents in parallel. The number of tasks spawned by the Luigi
scheduler depends on the number of *unstructured* documents returned by the
Solr query. In general, the results obtained include data from multiple
patients.

ClarityNLP can also support patient-specific structured CQL queries with a few
simple modifications to the documentset. For CQL queries the documentset must
be specified in the NLPQL file so that it limits the unstructured documents to
those for a **single** patient only. FHIR is essentially a single-patient
readonly data retrieval standard. Each patient with data stored on a FHIR
server has a unique ID. This ID must be used in the documentset statement and
in the ``Clarity.CQLExecutionTask`` body itself, as illustrated below. The
documentset specifies the unstructured docs for the patient, and the CQL query
specifies the structured data for the patient.

Additional Parameters
---------------------

Several additional parameters must be provided in either the ``.env`` file or
in the ``project.cfg`` file. For the ``.env`` file, the parameters are listed
in the next text box:

::
   
   FHIR_SERVICE_URI=Terminology Service Endpoint
   FHIR_DATA_SERVICE_URI=https://apps.hdap.gatech.edu/gt-fhir/fhir/
   FHIR_TERMINOLOGY_SERVICE_URI=https://cts.nlm.nih.gov/fhir/
   FHIR_TERMINOLOGY_USER=username
   FHIR_TERMINOLOGY_PASSWORD=password

For the ``project.cfg`` file the params would be listed in the ``[local]``
section as follows:
   
::
   
   [local]
   fhir_service_uri=Terminology Service Endpoint
   fhir_data_service_uri=https://apps.hdap.gatech.edu/gt-fhir/fhir/
   fhir_terminology_service_uri=https://cts.nlm.nih.gov/fhir/
   fhir_terminology_user=username
   fhir_terminology_password=password

**NOTE: you should set the values of these parameters to those**
**suitable for your FHIR infrastructure.**

   
Example
-------

Here is an example of how to use the ``CQLExecutionTask``.  In the text box
below there is a documentset creation statement followed by an invocation of
the ``CQLExecutionTask``.  The documentset consists of all indexed documents
for patient ``99999`` with a ``source`` field equal to ``MYDOCS``.  These
documents are specified explicitly in the ``CQLExecutionTask`` invocation that
follows. This patient ID of ``99999`` is also used explicitly in the
``patient_id`` parameter for the ``CQLExecutionTask``.

The ``fhir_url``parameter is the URL for the FHIR server's CQL evaluation API
endpoint.

The ``task_index`` parameter is used in an interprocess communication scheme
for controlling task execution. ClarityNLP's Luigi scheduler creates worker
task clones in proportion to the number of unstructured documents in the
documentset. If each of the task clones were to connect to the FHIR server
and run the CQL query it would result in a waste of network resources and
needless duplication of work. Only a single task from among the clones should
actually run the CQL query and retrieve the structured data.

ClarityNLP uses the ``task_index`` parameter to identify the single task
that should execute the CQL query. Any NLPQL file can contain multiple
invocations of ``Clarity.CQLExecutionTask``. Each of these should have
a ``task_index`` parameter, and they should be numbered sequentially starting
with 0.  In other words, each ``define`` statement containing an invocation
of ``Clarity.CQLExecutionTask`` should have a unique value for the zero-based
``task_index``.

::
   
   documentset PatientDocs:
    Clarity.createDocumentSet({
        "filter_query":"source:MYDOCS AND subject:99999"
    });

    define WBC:
        Clarity.CQLExecutionTask({
            documentset: [PatientDocs],
            "task_index": 0,
            "patient_id":"99999",
            "fhir_url":"https://gt-apps.hdap.gatech.edu/cql/evaluate",
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

=====================  ===================  ========= ======================================
         Name                 Type          Required                  Notes
=====================  ===================  ========= ======================================
documentset            :ref:`documentset`   Yes       Documents for a SINGLE patient only.
task_index             int                  Yes       Each CQLExecutionTask must have a unique value of this index.
patient_id             str                  Yes       CQL query executed on FHIR server for this patient.
fhir_url               str                  Yes       FHIR server CQL evaluation API endpoint.
cql                    triple-quoted str    Yes       Properly-formatted CQL query, sent verbatim to FHIR server.
=====================  ===================  ========= ======================================



Results
-------

The specific fields returned by the CQL query are dependent on the type of FHIR
resource that contains the data. ClarityNLP can decode these FHIR resource types:
``Patient``, ``Procedure``, ``Condition``, and ``Observation``. It can also decode
bundles of these resource types.

Fields in the MongoDB result documents are prefixed with the type of FHIR resource
from which they were taken. The prefixes for each are:

=================== =========
FHIR Resource Type   Prefix
=================== =========
Patient             patient
Procedure           procedure
Condition           condition
Observation         obs
=================== =========

The fields returned for the ``Patient`` resource are:

====================== =============================================================================
Field Name             Meaning
====================== =============================================================================
patient_subject        patient id
patient_fname_1        patient first name (could have multiple first names, numbered sequentially)
patient_lname_1        patient last name (could have multiple last names, numbered sequentially)
patient_gender         gender of the patient
patient_date_of_birth  date of birth in YYYY-MM-DD format
====================== =============================================================================

The fields returned for the ``Procedure`` resource are:

============================== =============================================================================
Field Name                     Meaning
============================== =============================================================================
procedure_id_value             ID of the procedure
procedure_status               status indicator for the procedure
procedure_codesys_code_1       code for the procedure; multiple codes are numbered sequentially
procedure_codesys_system_1     code system; multiple code systems are numbered sequentially
procedure_codesys_display_1    code system procedure name; multiple names are numbered sequentially
procedure_subject_ref          typically the string 'Patient/' followed by a patient ID, i.e. Patient/99999
procedure_subject_display      patient full name string
procedure_context_ref          typically the string 'Encounter/' followed by a number, i.e. Encounter/31491
procedure_performed_date_time  timestamp of the procedure in YYYY-MM-DDTHH:mm:ss+hhmm format
============================== =============================================================================

The fields returned for the ``Condition`` resource are:

============================== =============================================================================
Field Name                     Meaning
============================== =============================================================================
condition_id_value             ID of the condition
condition_category_code_1      category code value; multiple codes are numbered sequentially
condition_category_system_1    category code system; multiple code systems are numbered sequentially
condition_category_display_1   category name; multiple names are numbered sequentially
condition_codesys_code_1       code for the condition; multiple codes are numbered sequentially
condition_codesys_system_1     code system; multiple code systems are numbered sequentially
condition_codesys_display_1    code system condition name; multiple names are numbered sequentially
condition_subject_ref          typically the string 'Patient/' followed by a patient ID, i.e. Patient/99999
condition_subject_display      patient full name string
condition_context_ref          typically the string 'Encounter/' followed by a number, i.e. Encounter/31491
condition_onset_date_time      timestamp of condition onset in YYYY-MM-DDTHH:mm:ss+hhmm format
condition_abatement_date_time  timestamp of condition abatement in YYYY-MM-DDTHH:mm:ss+hhmm format
============================== =============================================================================

The fields returned for the ``Observation`` resource are:

============================== =============================================================================
Field Name                     Meaning
============================== =============================================================================
obs_codesys_code_1             code for the observation; multiple codes are numbered sequentially
obs_codesys_system_1           code system; multiple code systems are numbered sequentially
obs_codesys_display_1          code system observation name; multiple names are numbered sequentially
obs_subject_ref                typically the string 'Patient/' followed by a patient ID, i.e. Patient/99999
obs_subject_display            patient full name string
obs_context_ref                typically the string 'Encounter/' followed by a number, i.e. Encounter/31491
obs_value                      numberic value of what was observed or measured
obs_unit                       string identifying the units for the value observed
obs_unit_system                typically a URL with information on the units used
obs_unit_code                  unit string with customary abbreviations
obs_effective_date_time        timestamp in YYYY-MM-DDTHH:mm:ss+hhmm format
============================== =============================================================================


Collector
---------
No
