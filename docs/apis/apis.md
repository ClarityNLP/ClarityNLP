## Pipeline Types
*GET* `http://nlp-api:5000/pipeline_types`

Get a list of valid pipeline types

## Report Type Mappings
*GET* `http://nlp-api:5000/report_type_mappings`

Get a dictionary of report type mappings

## Sections
*GET* `http://nlp-api:5000/sections`

Get source file for sections and synonyms

## Status
*GET* `http://nlp-api:5000/status/<int:job_id>`

Get status for a given job

## Upload
See section on [Ingestion](http://clarity-nlp.readthedocs.io/en/latest/#document-ingestion).


## NLPQL
*POST* `http://nlp-api:5000/nlpql`

Post NLPQL text file to run phenotype against data in Solr. Returns links to view job status and results.
Learn more about NLPQL [here](http://clarity-nlp.readthedocs.io/en/latest/nlpql.html) and see samples of NLPQL [here](https://github.com/ClarityNLP/ClarityNLP/tree/master/nlp/samples/nlpql).

## NLPQL tester
*POST* `http://nlp-api:5000/nlpql_tester`

Post NLPQL text file to test if parses successfully. Either returns phenotype JSON or errors, if any.
Learn more about NLPQL [here](http://clarity-nlp.readthedocs.io/en/latest/nlpql.html) and see samples of NLPQL [here](https://github.com/ClarityNLP/ClarityNLP/tree/master/nlp/samples/nlpql).


## Phenotype
*POST* `http://nlp-api:5000/nlpql_tester`

Post Phenotype JSON to run phenotype against data in Solr. Same as posting to `/nlpql`, but with the finalized JSON structured instead of raw NLPQL. Using `/nlpql` will be preferred for most users.
See sample [here](https://github.com/ClarityNLP/ClarityNLP/tree/master/nlp/samples/nlpql/NLPQL_JSON).

## Pipeline
*POST* `http://nlp-api:5000/pipeline`

Post a pipeline job (JSON) to run on the Luigi pipeline. Most users will use `/nlpql`. 
Read more about pipelines [here](http://clarity-nlp.readthedocs.io/en/latest/pipelines.html). 
See sample JSON [here](https://github.com/ClarityNLP/ClarityNLP/tree/master/nlp/samples/pipelines)

## Term Finder
*POST* `http://nlp-api:5000/term_finder`

POST JSON to extract terms, context, negex, sections from text. Sample input JSON [here](https://github.com/ClarityNLP/ClarityNLP/blob/master/nlp/samples/library_inputs/sample_term_finder.json).

## Measurement Finder
*POST* `http://nlp-api:5000/measurement_finder`

POST JSON to extract measurements. Sample input JSON [here](https://github.com/ClarityNLP/ClarityNLP/blob/master/nlp/samples/library_inputs/sample_measurement_finder.json).

## Value Extractor
*POST* `http://nlp-api:5000/value_extractor`

POST JSON to extract values such as BP, LVEF, Vital Signs etc. Sample input JSON [here](https://github.com/ClarityNLP/ClarityNLP/blob/master/nlp/samples//library_inputs/sample_value_extractor.json).

## TNM Stage
*POST* `http://nlp-api:5000/tnm_stage`

POST JSON to extract TNM staging from text. Sample input JSON [here](https://github.com/ClarityNLP/ClarityNLP/blob/master/nlp/samples/library_inputs/sample_tnm_stage.json).

## Named Entity Recognition
*POST* `http://nlp-api:5000/named_entity_recognition`

POST JSON to run spaCy's NER. Sample input JSON [here](https://github.com/ClarityNLP/ClarityNLP/blob/master/nlp/samples//library_inputs/sample_ner.json).

## Part of Speech Tagger
*POST* `http://nlp-api:5000/pos_tagger`

POST JSON to run spaCy's POS Tagger. (Only recommended on smaller text documents.) Sample input JSON [here](https://github.com/ClarityNLP/ClarityNLP/blob/master/nlp/samples//library_inputs/sample_pos_tag_text.json).