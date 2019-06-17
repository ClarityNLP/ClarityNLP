.. _cqleval:

Clarity.CQLExecutionTask
========================

Description
-----------

This is a custom task that allows ClarityNLP to execute
`CQL <https://cql.hl7.org/>`_ (Clinical Quality Language) queries embedded in
NLPQL files. ClarityNLP directs CQL code to a FHIR
`(Fast Healthcare Interoperability Resources) <https://www.hl7.org/fhir/overview.html>`_
server, which runs the query and retrieves structured data for a **single**
patient. The data returned from the CQL query appears in the job results for
the NLPQL file.

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

These parameters are needed to connect to the FHIR server, evaluate the CQL
statements, and retrieve the results. They can be provided directly as
parameters in the ``CQLExecutionTask`` statement (see below), or indirectly
via `ClarityNLPaaS <https://github.com/ClarityNLP/ClarityNLPaaS>`_:

=================================  ==================
Parameter                          Meaning
=================================  ==================
cql_eval_url                       URL of the FHIR server's CQL Execution Service
patient_id                         Unique ID of patient whose data will be accessed
fhir_data_service_uri              FHIR service base URL
fhir_terminology_service_endpoint  Set to ``Terminology Service Endpoint``
fhir_terminology_service_uri       URI for a service that conforms to the FHIR Terminology Service Capability Statement
fhir_terminology_user_name         Username for terminology service authentication
fhir_terminology_user_password     Password for terminology service authentication
=================================  ==================

The terminology user name and password parameters may not be required,
depending on whether the terminology server requires password authentication
or not.

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
``task_index``.

The ``patient_id`` parameter identifies the patient whose data will be accessed
by the CQL query. This ID should match that specified in the documentset
creation statement.

The remaining parameters from the table above are set to values appropriate for
GA Tech's FHIR infrastructure.

The ``cql`` parameter is a triple-quoted string containing the CQL query.
This CQL code is assumed to be syntactically correct and is passed to the FHIR
server's CQL evaluation service unaltered. All CQL code should be checked for
syntax errors and other problems prior to its use in an NLPQL file.

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
            "cql_eval_url":"https://gt-apps.hdap.gatech.edu/cql/evaluate",
            "fhir_data_service_uri":"https://apps.hdap.gatech.edu/gt-fhir/fhir/",
            "fhir_terminology_service_uri":"https://cts.nlm.nih.gov/fhir/",
            "fhir_terminology_service_endpoint":"Terminology Service Endpoint",
            "fhir_terminology_user_name":"username",
            "fhir_terminology_user_password":"password",
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
patient_id                         str                  Yes       CQL query executed on FHIR server for this patient.
cql_eval_url                       str                  Yes       See table above.
fhir_data_service_uri              str                  Yes       See table above.
fhir_terminology_service_uri       str                  Yes       See table above.
fhir_terminology_service_endpoint  str                  Yes       See table above.
fhir_terminology_user_name         str                  No        Optional, depends on configuration of terminology server
fhir_terminology_user_password     str                  No        Optional, depends on configuration of terminology server
cql                                triple-quoted str    Yes       Properly-formatted CQL query, sent verbatim to FHIR server.
=================================  ===================  ========= ======================================


Results
-------

The specific fields returned by the CQL query are dependent on the type of FHIR
resource that contains the data. ClarityNLP can decode these FHIR resource types:
``Patient``, ``Procedure``, ``Condition``, and ``Observation``. It can also decode
bundles of these resource types.

Fields in the MongoDB result documents are prefixed with the type of FHIR resource
from which they were taken except for the ``datetime`` field, which omits the
prefix to enable date-based sorting. The prefixes for each are:

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
datetime                       identical to procedure_performed_date_time
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
datetime                       identical to condition_onset_date_time
condition_abatement_date_time  timestamp of condition abatement in YYYY-MM-DDTHH:mm:ss+hhmm format
end_datetime                   identical to condition_abatement_date_time
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
datetime                       identical to obs_effective_date_time
============================== =============================================================================


Collector
---------
No
