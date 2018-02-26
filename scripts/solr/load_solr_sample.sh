#!/usr/bin/env bash

/home/solr/bin/solr create -c sample

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
           "preserveOriginal":"0" }]}}
}' http://localhost:8983/solr/sample/schema

curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field":{"name":"report_date","type":"date","indexed":true,"stored":true},
"add-field":{"name":"report_id","type":"string","indexed":true,"stored":true},
"add-field":{"name":"report_text","type":"searchText","indexed":true,"stored":true,"termPositions":true,"termVectors":true,"docValues":false,"required":true},
"add-field":{"name":"source","type":"string","indexed":true,"stored":true},
"add-field":{"name":"subject","type":"string","indexed":true,"stored":true},"add-field":{"name":"report_type","type":"string","indexed":true,"stored":true}
}' http://localhost:8983/solr/sample/schema

curl -X POST -H 'Content-type:application/json' --data-binary '{
 "add-dynamic-field":{"name":"*_section","type":"searchText","indexed":true,"stored":false},
"add-dynamic-field":{"name":"*_id","type":"long","indexed":true,"stored":true},
"add-dynamic-field":{"name":"*_ids","type":"long","multiValued":true,"indexed":true,"stored":true},
"add-dynamic-field":{"name":"*_system","type":"string","indexed":true,"stored":true},
"add-dynamic-field":{"name":"*_attr","type":"string","indexed":true,"stored":true},
"add-dynamic-field":{"name":"*_attrs","type":"string","multiValued":true,"indexed":true,"stored":true}
}' http://localhost:8983/solr/sample/schema

/home/solr/bin/post -c sample