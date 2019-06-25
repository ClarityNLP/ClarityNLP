# Solr Setup and Configuration

## Data types
We use standard Solr data types with one custom data type, `searchText`.  `searchText` is a text field, tokenized on spaces, with filtering to support case insensitivity.


## Fields
All documents in ClarityNLP are stored in Solr. These are the minimal required fields:
```json
 {
        "report_type":"Report Type",
        "id":"1",
        "report_id":"1",
        "source":"My Institution",
        "report_date":"1970-01-01T00:00:00Z",
        "subject":"the_patient_id_or_other_identifier",
        "report_text":"Report text here"
    }
```

`id` and `report_id` should be unique in the data set, but can be equal. `report_text` should be plain text. `subject` is generally the patient identifier, but could also be some other identifier, such as `drug_name`.
`source` is generally your institution or the name of the document set.

Additional fields can be added to store additional metadata. The following fields are allowable as dynamic fields:
	

* `*_section` (searchText); e.g. `past_medical_history_section` (for indexing specific sections of notes)
* `*_id` (long) e.g.`doctor_id` (any other id you wish to store) 
* `*_ids` (long, multiValued) e.g. `medication_ids` (any other id as an array)
* `*_system` (string) e.g. `code_system` (noting any system values)
* `*_attr` (string) e.g.`clinic_name_attr` (any single value custom attribute) 
* `*_attrs` (string, multiValued) e.g. `insurer_names` (any multi valued custom attribute) 


## Custom Solr Setup
This should be completed for you if you are using Docker. However, here are the commands to setup Solr.

* [Install Solr](https://cwiki.apache.org/confluence/display/solr/Installing+Solr)
* Setup custom tokenized field type:
```bash
curl -X POST -H 'Content-type:application/json' --data-binary '{
      "add-field-type" : {
         "name":"searchText",
         "class":"solr.TextField",
         "positionIncrementGap":"100",
         "analyzer" : {
            "charFilters":[{
               "class":"solr.PatternReplaceCharFilterFactory",
               "replacement":"$1$1",
               "pattern":"([a-zA-Z])\\\\1+" }],
            "tokenizer":{
               "class":"solr.WhitespaceTokenizerFactory" },
            "filters":[{
               "class":"solr.WordDelimiterFilterFactory",
               "preserveOriginal":"0" },
               {"class": "solr.LowerCaseFilterFactory"
               }]}}
    }' http://localhost:8983/solr/report_core/schema
```
* Add standard fields (Solr 6):
```bash
curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field":{"name":"report_date","type":"date","indexed":true,"stored":true,"default":"NOW"},
  "add-field":{"name":"report_id","type":"string","indexed":true,"stored":true},
  "add-field":{"name":"report_text","type":"searchText","indexed":true,"stored":true,"termPositions":true,"termVectors":true,"docValues":false,"required":true},
  "add-field":{"name":"source","type":"string","indexed":true,"stored":true},
  "add-field":{"name":"subject","type":"string","indexed":true,"stored":true},
  "add-field":{"name":"report_type","type":"string","indexed":true,"stored":true}
}' http://localhost:8983/solr/report_core/schema
```

* Add standard fields (Solr 7 and later):
```bash
curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field":{"name":"report_date","type":"pdate","indexed":true,"stored":true,"default":"NOW"},
  "add-field":{"name":"report_id","type":"string","indexed":true,"stored":true},
  "add-field":{"name":"report_text","type":"searchText","indexed":true,"stored":true,"termPositions":true,"termVectors":true,"docValues":false,"required":true},
  "add-field":{"name":"source","type":"string","indexed":true,"stored":true},
  "add-field":{"name":"subject","type":"string","indexed":true,"stored":true},
  "add-field":{"name":"report_type","type":"string","indexed":true,"stored":true}
}' http://localhost:8983/solr/report_core/schema
```


* Add dynamic fields (Solr 6):
```bash
curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-dynamic-field":{"name":"*_section","type":"searchText","indexed":true,"stored":false},
  "add-dynamic-field":{"name":"*_id","type":"long","indexed":true,"stored":true},
  "add-dynamic-field":{"name":"*_ids","type":"long","multiValued":true,"indexed":true,"stored":true},
  "add-dynamic-field":{"name":"*_system","type":"string","indexed":true,"stored":true},
  "add-dynamic-field":{"name":"*_attr","type":"string","indexed":true,"stored":true},
  "add-dynamic-field":{"name":"*_attrs","type":"string","multiValued":true,"indexed":true,"stored":true}
}' http://localhost:8983/solr/report_core/schema
```

* Add dynamic fields (Solr 7 and later):
```bash
curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-dynamic-field":{"name":"*_section","type":"searchText","indexed":true,"stored":false},
  "add-dynamic-field":{"name":"*_id","type":"plong","indexed":true,"stored":true},
  "add-dynamic-field":{"name":"*_ids","type":"plongs","multiValued":true,"indexed":true,"stored":true},
  "add-dynamic-field":{"name":"*_system","type":"string","indexed":true,"stored":true},
  "add-dynamic-field":{"name":"*_attr","type":"string","indexed":true,"stored":true},
  "add-dynamic-field":{"name":"*_attrs","type":"strings","multiValued":true,"indexed":true,"stored":true}
}' http://localhost:8983/solr/report_core/schema
```

* [Ingest data](../../setup/ingest/generic_ingestion.html)

## Deleting documents
**These commands will permanently delete your documents; use with caution.**

Delete documents based on a custom query:
```bash
curl "http://localhost:8983/solr/report_core/update?commit=true" -H "Content-Type: text/xml" --data-binary '<delete><query>source:"My Source"</query></delete>'
```

Delete all documents:
```bash
curl "http://localhost:8983/solr/report_core/update?commit=true" -H "Content-Type: text/xml" --data-binary '<delete><query>*:*</query></delete>'
```
