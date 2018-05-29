## Pipelines

Pipelines are the lowest level type jobs that can be ran with Luigi and ClarityNLP. 
Generally they have one purpose such as finding provider assertions or extracting temperature measurements.
NLPQL is generally composed of one or more pipelines, so usually pipelines don't need to be ran standalone, but can be for testing purposes.
They can be ran from the command line through Luigi (see below), or via POSTing pipeline JSON to the endpoint `http://nlp-api:5000/pipeline`.

#### Running a standalone pipeline from the command line
```bash
PYTHONPATH='.' luigi --module luigi_pipeline NERPipeline --pipeline 1 --job 1234 --owner user 
```

