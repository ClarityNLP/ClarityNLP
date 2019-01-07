## ClarityNLP

[![Build Status](https://travis-ci.com/ClarityNLP/ClarityNLP.svg?branch=master)](https://travis-ci.com/ClarityNLP/ClarityNLP)

**What is ClarityNLP?**

ClarityNLP is a clinical natural language processing platform focused on making healthcare NLP more accessible and reproducible.  Over the past decade, NLP methods have far outstripped our ability to use them effectively.

ClarityNLP combines NLP techniques and libraries with a powerful query language, NLPQL, to identify patients and their clinical observations, extracted from text.
ClarityNLP gives you insights into clinical (and other) text without a lot of custom configuration, and NLPQL lets you write your own definitions to find the patients and features that are relevant to your project.  

ClarityNLP's NLP engine is built in Python, powered by Luigi, using spaCy and other NLP libraries. We have provided a Docker Compose configuration to integrate all the services ClarityNLP uses, or you can run standalone. To begin exploring ClarityNLP, follow the Quick Start guide below or read the full documentation [here](http://claritynlp.readthedocs.io/en/latest/index.html).

### ClarityNLP Quick Start

1. [Install ClarityNLP with Docker](http://claritynlp.readthedocs.io/en/latest/setup/local-docker.html#running-locally)

2. You should now be running all the services ClarityNLP needs. The main NLP service will be running at [http://localhost:5000](http://localhost:5000). You'll need to use a tool like [Postman](https://www.getpostman.com/apps) to interact with ClarityNLP.

3. ClarityNLP has been pre-loaded with documents from the FDA Drug Labels data set, but you can get an idea on how to load more documents [here](http://claritynlp.readthedocs.io/en/latest/setup/index.html#data-ingestion).

4. Now we can test some NLPQL. See some sample NLPQL [here](https://github.com/ClarityNLP/ClarityNLP/tree/master/nlpql) and learn more about NLPQL [here](http://claritynlp.readthedocs.io/en/latest/user_guide/intro/overview.html#example-nlpql-phenotype-walkthrough). Let's try on creating a simple NLPQL to find drug allergies in this text.
Using Postman, we'll POST the NLPQL below as plain text to [http://localhost:5000/nlpql](http://localhost:5000/nlpql).

<details><summary>Sample NLPQL</summary>
<p>

```
debug;

// Phenotype library name
phenotype "Drug Allergy" version "1";

/* Phenotype library description */
description "Sample NLPQL to find drug allergies.";

// # Structured Data Model #
datamodel OMOP version "5.3";

// # Referenced libraries #
// The ClarityCore library provides common functions for simplifying NLP pipeline creation
include ClarityCore version "1.0" called Clarity;
include OHDSIHelpers version "1.0" called OHDSI;

// ## Code Systems ##
codesystem OMOP: "http://omop.org"; // OMOP vocabulary https://github.com/OHDSI/Vocabulary-v5.0;


// #Manual Term sets#
// simple example-- termset "Vegetables":["brocolli","carrots","cauliflower"]
// can add expansion of structured concepts from terminologies as well with OMOPHelpers

documentset ProviderNotes:
    Clarity.createReportTagList(["Physician","Nurse","Note","Discharge Summary"]);

termset PenicillinTerms: [
"Amoxicillin",
"Ampicillin",
"Dicloxacillin",
"Nafcillin",
"Oxacillin",
"Penicillin G",
"Penicillin V",
"Piperacillin",
"Ticarcillin"];

termset AllergyTerms: [
"allergy",
"Skin rash",
"Hives",
"Itching",
"Fever",
"Swelling",
"Shortness of breath",
"Wheezing",
"Runny nose",
"Itchy eyes",
"watery eyes",
"Anaphylaxis"];

define isPenicillin:
  Clarity.ProviderAssertion({
    termset: [PenicillinTerms],
    documentset: [ProviderNotes]
  });

define hasAllergy:
  Clarity.ProviderAssertion({
    termset: [AllergyTerms],
    documentset: [ProviderNotes]
  });


//CDS logical Context (Patient, Document)
context Patient;

define final hasSepsis:
  where isPenicillin AND hasAllergy;

```
</p>
</details>



5. We should receive a response that tells a few things but the most important thing is the link to access results.
<details><summary>Sample Results</summary>
<p>

```
{
    "job_id": "1",
    "phenotype_id": "1",
    "phenotype_config": "http://localhost:5000/phenotype_id/1",
    "pipeline_ids": [
        1,
        2
    ],
    "pipeline_configs": [
        "http://localhost:5000/pipeline_id/1",
        "http://localhost:5000/pipeline_id/2"
    ],
    "status_endpoint": "http://localhost:5000/status/1",
    "luigi_task_monitoring": "http://localhost:8082/static/visualiser/index.html#search__search=job=1",
    "intermediate_results_endpoint": "http://localhost:5000/job_results/1/phenotype_intermediate",
    "main_results_endpoint": "http://localhost:5000/job_results/1/phenotype"
}
```

</p>
</details>


6. Now, we should be able to download results using the `main_results_endpoint` as soon as the job is *COMPLETED*.
We can check if the job is *COMPLETED* via the `status_endpoint`.




### Full ClarityNLP Documentation
You can read the full ClarityNLP documentation here:
[Read the Docs](http://claritynlp.readthedocs.io/en/latest/).


### Slack
Connect with us on [Slack](https://join.slack.com/t/claritynlp/shared_invite/enQtNTE5NTUzNzk4MTk5LTFmNWY1NWVmZTA4Yjc5MDUwNTRhZTBmNTA0MWM0ZDNmYjdlNTAzYmViYzAzMTkwZDkzODA2YTJhYzQ1ZTliZTQ)
