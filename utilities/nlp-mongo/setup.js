db.pipeline_results.createIndex( {  "subject":1 })
db.pipeline_results.createIndex( {  "job_id":1 })
db.pipeline_results.createIndex( {  "nlpql_name":1 })
db.pipeline_results.createIndex( {  "pipeline_id":1  })


db.phenotype_results.createIndex( {  "subject":1 })
db.phenotype_results.createIndex( {  "job_id":1 })
db.phenotype_results.createIndex( {  "nlpql_feature":1 })
db.phenotype_results.createIndex( {  "pipeline_id":1  })