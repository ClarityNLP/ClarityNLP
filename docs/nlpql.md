# NLPQL
## Overview
### What is NLPQL?
**Natural Language Processing Query Language** (NLPQL) is a _computable phenotyping syntax_ for unstructured data.  It is based on the Clinical Query Language (CQL) standard.

### What is Computable Phenotyping?
**Computable phenotypes** are machine-interpretable objects that explicitly define the features of a patient cohort.  For example, here is a [computable phenotype for hypothyroidism](http://www.ohdsi.org/web/atlas/#/cohortdefinition/414) represented in the syntax used by the OHDSI consortium. This phenotype specifies clinical concepts relevant to hypothyroidism including diagnoses, medications, and laboratories. What makes it "computable" is that the OHDSI definition is in fact a parseable JSON object that includes 1) the specific codes (eg ICD, SNOMED, LOINC, etc) that define each clinical concept and 2) the logic (temporal etc) that combines these concepts into a definition of hypothyroidism.

### What's different about NLPQL?
Prior computable phenotyping efforts have been focused on _structured data_ (eg conditions, drugs, procedures, labs, etc).  NLPQL is designed to support phenotype specifications that include _unstructured text_ (eg. provider notes, radiology reports, pathology reports, etc) as well.

### Does my data need to be in a special model or format to run NLPQL?
No. The ClarityNLP platform can ingest unstructured data from any format and run NLPQL.

### What NLP functions can I use in NLPQL Phenotypes?
See the ClarityNLP Module documentation section for built-in NLP functions and how to incorporate your own NLP modules.

## Basic Syntax
### Basis in CQL
### Basic Rules
### Naming and Aliasing Conventions

## ClarityNLP Document Sets
### createReportTagList

## ClarityNLP Data Entities
### TermFinder
### ProviderAssertion
### ValueExtraction
### MeasurementExtraction
### dateDiff
### NamedEntityRecognition

## OHDSI Connectors
### getCohort


## Operations
### Logical operations
### Comparator operations

## NLPQL Objects

### `phenotype`
### `version`
### `description`
### `datamodel`
### `include`
### `codesystem`
### `valueset`
### `termset`
### `documentset`
### `cohort`
### `population`
### `context`
### `define`

## Running

## Results
