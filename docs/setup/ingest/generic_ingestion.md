### General Document Ingestion

See guide to [Solr](../../developer_guide/technical_background/solr.html) for
more information about Solr setup with ClarityNLP.

Solr has built-in APIs for ingesting documents, which are documented [here](https://lucene.apache.org/solr/guide/7_3/uploading-data-with-index-handlers.html). The simplest way is generally to use `curl` to upload JSON, CSV, or XML. Documents need to be pre-processed as plain text before they are uploaded into ClarityNLP.

Sample JSON upload for ClarityNLP:
```bash
curl -X POST -H 'Content-Type: application/json' 'http://localhost:8983/solr/report_core/update/json/docs' --data-binary '
 {
        "report_type":"Report Type",
        "id":"1",
        "report_id":"1",
        "source":"My Institution",
        "report_date":"1970-01-01T00:00:00Z",
        "subject":"the_patient_id_or_other_identifier",
        "report_text":"Report text here"
    }'
```

#### Upload Scripts

A collection of scripts for ingesting popular datasets (MIMIC, AACT Clinical Trials, Gleason Pathology Documents, etc.) is available [here](https://github.com/ClarityNLP/Utilities).
