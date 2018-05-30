# Building Phenotypes with NLPQL
Phenotypes can be created using the [NLPQL language](http://clarity-nlp.readthedocs.io/en/latest/nlpql.html) and executed over the [ClarityNLP API](http://clarity-nlp.readthedocs.io/en/latest/apis/apis.html#nlpql). 
NLPQL is parsed to JSON using [ANTLR](http://www.antlr.org/), and then processed using Luigi.


# Luigi
Phenotype jobs are orchestrated with [Luigi](http://luigi.readthedocs.io/en/stable/), which spawns multiple workers to execute pipelines in batches of documents.

# Phenotypes and Pipelines
Phenotypes are generally composed of multiple pipelines and logical rules to determine phenotype results.


# Phenotype Results
Phenotype results consist of 2 types: intermediate and final. Intermediate results are results of any pipeline. Final phenotype results are the output of the phenotypes against the phenotype logic and anything that was labeled `final` in NLPQL.