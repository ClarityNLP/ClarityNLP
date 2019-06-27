.. _intro-overview:

ClarityNLP at a Glance
======================

ClarityNLP is designed to simplify the process of analyzing unstructured data (eg. provider notes, radiology reports, pathology results, etc) to find particular data or patients from electronic medical records.

We refer to the definition of what you are trying to find as a *phenotype*.  Phenotypes are useful for research, clinical, quality, or payment purposes, because they allow a very explicit definition of the criteria that make up a patient of interest.  With ClarityNLP, these criteria can be shared using machine-interpretable code that can be run on any clinical dataset.

How is this accomplished?  ClarityNLP uses a query syntax called **Natural Language Processing Query Language (NLPQL)**, based on the `CQL <http://www.hl7.org/implement/standards/product_brief.cfm?product_id=400>`_ syntax from HL7. The ClarityNLP platform provides mapping tools that allow NLPQL phenotypes to run on any dataset.

Let's take a look at how NLPQL works.

Example NLPQL Phenotype Walkthrough
===================================

Imagine you have a dataset with thousands of clinical documents and would like to extract a particular data element.  You can create an NLPQL file to specify what you would like to extract.

*Here is a basic NLPQL phenotype that extracts Temperature values from Nursing notes.*

.. code-block:: java

     phenotype "Patient Temperatures" version "2";

     include ClarityCore version "1.0" called Clarity;

     documentset NursingNotes:
        Clarity.createReportTagList(["Nurse"]);

     termset TemperatureTerms:
        ["temp","temperature","t"];

      define Temperature:
        Clarity.ValueExtraction({
          termset:[TemperatureTerms],
          documentset: [NursingNotes],
          minimum_value: "96",
          maximum_value: "106"
          });

      define final hasFever:
          where Temperature.value >= 100.4;

Let's break down the NLPQL above.

Phenotype Name
--------------

.. code-block:: java

     phenotype "Patient Temperatures" version "2";

Every ClarityNLP phenotype definition needs a name.  We give it a name (and optionally a version) using the ``phenotype`` command.  Here, we are just declaring that our phenotype will be called "Patient Temperatures".

Libraries
---------

.. code-block:: java

     include ClarityCore version "1.0" called Clarity;

NLPQL is designed to be extensible and make it easy for developers to build new NLP algorithms and run them using the ClarityNLP platform. A common paradigm for making software extensible is the use of libraries.  Using the ``include`` command, we are saying to include the core Clarity library which has lots of handy commands and NLP algorithms built-in. The ``called`` phrase allows us to select a short name to refer to the library in the NLPQL that follows. In this case, we have selected to call it "Clarity".

Document Sets
-------------

.. code-block:: java

  documentset NursingNotes:
     Clarity.createReportTagList(["Nurse"]);

:ref:`Document sets<documentset>` are lists of document types that you would like ClarityNLP to process.  (If no document sets are created, ClarityNLP will simply analyze all documents in your repository.)  Built into the Clarity core library is the ``createReportTagList`` function, which allows you to enumerate a set of document type tags from the `LOINC document ontology <https://loinc.org/document-ontology/current-version/>`_.  Typically, these tags are assigned to your documents at the time of ingestion through use of the `Report Type Mapper <https://github.com/ClarityNLP/report-type-mapper-api>`_.
             
In this case, we have declared a document set called "Nursing Notes" and included in it all documents with the Nurse tag.  We could have selected another provider type (eg. Physician), a specialty type (eg. Endocrinology), a setting type (eg. Emergency Department), or a combination such as ``["Physician","Emergency Department"]``.

.. code-block:: java

    documentset AmoxDischargeNotes:
         Clarity.createDocumentSet({
             "report_types":["Discharge summary"],
             "report_tags": [],
             "filter_query": "",
             "query":"report_text:amoxicillin"});
             
ClarityNLP provides an additional document set, ``createDocumentSet``, which provides more control over document section, allowing users to select report tags or report types, and provides flexibility to write custom queries.

Term Sets
---------

.. code-block:: java

  termset TemperatureTerms:
     ["temp","temperature","t"];

:ref:`Term sets<termset>` are lists of terms or tokens you would like to input into an NLP method.  You can create these lists manually (as shown in this example) or generate them based on ontologies.  Furthermore you can extend termsets with synonyms and lexical variants.

In this case, we have created a term set called "TemperatureTerms" and included three common ways temperature is  referenced in a clinical note ("temperature", "temp", and "t").

Phenotype Features
------------------

*Features* are the clinical elements that you wish to find and analyze in order to identify your patients of interest.  Features specify an :ref:`NLPQL task<nlpqlref>` you'd like to run as well as optional parameters such as document sets, term sets, patient cohorts, and more.  See the `NLPQL examples <https://github.com/ClarityNLP/ClarityNLP/tree/master/nlpql>`_ to get a better sense of how different features can be created.

We have two features in our example NLPQL.  Let's take a look at each.

.. code-block:: java

  define Temperature:
     Clarity.ValueExtraction({
       termset:[TemperatureTerms],
       documentset: [NursingNotes],
       minimum_value: "96",
       maximum_value: "106"
       });

Features are specified in NLPQL using the ``define`` keyword followed by a feature name and a function.  In this case, we are assigning the name "Temperature" to the output of a particular NLP method that is included in the Clarity core library called :ref:`Value Extraction<general-value-extraction>`.  (This could just as easily have been an NLP method from another Python library or an external API using :ref:`External NLP Method Integration<customtaskalgo>`.)

In the example, we provide the Value Extraction method with a set of parameters including our document set ("NursingNotes"), term set ("TemperatureTerms"), and min/max values to include in the temperature results. The accuray of this definition for temperature can be evaluated using the ClarityNLP validation framework, which is a feature built into the :ref:`Results Viewer<ui_results_viewer>`.

Now on to the second feature in the example:

**Final Features**

.. code-block:: java

  define final hasFever:
      where Temperature.value >= 100.4;

With this statement, we are creating a new feature called "hasFever" that includes any patients with a temperature value greater than 100.4.  There are two things to note about this syntax.

  - ``final`` A phenotype may involve the creation of numerous intermediate features that are extracted by NLP processes but are not themselves the final result of the analysis.  For example, we may be interested only in patients with a fever, rather than any patient who has a temperature value recorded.  The :ref:`final<nlpqlref>` keyword allows us to indicate the final output or outputs of the phenotype definition.
    
  - ``value`` Every NLP method returns a result.  The specific format and content of these results will vary by method. As a convenience, ClarityNLP returns a ``value`` parameter for most methods.  The :ref:`Value Extraction<general-value-extraction>` method used here also returns several other parameters.   ClarityNLP is flexible in that it can take any parameter you provide and perform operations on it.  However, this will only work if the method being called returns that parameter.  Please consult the documentation for individual methods to see what parameters can be referenced.

Running NLPQL Queries
=====================

In the full guide, we will walk you through the steps of ingesting and mapping your own data.  Once in place, you will be able to run queries by hitting the :ref:`nlpql API endpoint<apiref>` on your local server or by visiting ``<your_server url>:5000/nlpql``.  But to run a quick test, feel free to use our `NLPQL test page <https://nlpql.apps.hdap.gatech.edu/>`_.


**Next Steps**

The next steps for you are to :ref:`install ClarityNLP<setupindex>`,
follow through some of our
`Cooking with Clarity <https://github.com/ClarityNLP/ClarityNLP/tree/master/notebooks/cooking>`_
tutorials to learn how to create a full-blown ClarityNLP project, and
`join our channel <https://join.slack.com/t/claritynlp/shared_invite/enQtNTE5NTUzNzk4MTk5LTFmNWY1NWVmZTA4Yjc5MDUwNTRhZTBmNTA0MWM0ZDNmYjdlNTAzYmViYzAzMTkwZDkzODA2YTJhYzQ1ZTliZTQ>`_ on Slack.
Thanks for your interest!

.. _NLPQL Launcher: https://scrapy.org/community/
.. _NLPQL API: https://en.wikipedia.org/wiki/Web_scraping
