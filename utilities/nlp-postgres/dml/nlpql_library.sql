INSERT INTO nlp.nlpql_library (nlpql_id, nlpql_name, nlpql_version, nlpql_raw, nlpql_json, date_added) VALUES (1, 'Prostate Cancer Term Proximity', '1.0', ' phenotype "Prostate Cancer Term Proximity" version "1";

define final TermProximityFunction:
    Clarity.TermProximityTask({
        "termset1": "prostate",
        "termset2": "cancer, Gleason, Gleason''s, Gleasons,adenocarcinoma, carcinoma",
        "word_distance": 6,
        "any_order": "False"
    });
', '{
    "owner": "claritynlp",
    "name": "Prostate Cancer Term Proximity",
    "population": "All",
    "context": "Patient",
    "phenotype": {
        "name": "Prostate Cancer Term Proximity",
        "declaration": "phenotype",
        "version": "1",
        "alias": "",
        "arguments": [],
        "named_arguments": {},
        "library": "ClarityNLP",
        "funct": "",
        "values": [],
        "description": "",
        "concept": ""
    },
    "valid": true,
    "data_entities": [
        {
            "name": "TermProximityFunction",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "termset1": "prostate",
                "termset2": "cancer, Gleason, Gleason''s, Gleasons,adenocarcinoma, carcinoma",
                "word_distance": 6,
                "any_order": false
            },
            "library": "Clarity",
            "funct": "TermProximityTask",
            "values": [],
            "description": "",
            "concept": "",
            "final": true,
            "raw_text": "",
            "job_results": []
        }
    ],
    "debug": false,
    "limit": 0,
    "phenotype_id": 1
}', '2019-03-26 15:18:25.356000');
INSERT INTO nlp.nlpql_library (nlpql_id, nlpql_name, nlpql_version, nlpql_raw, nlpql_json, date_added) VALUES (2, 'Breast Cancer with Low ECOG', '1.0', 'phenotype "Breast Cancer Trials with low ECOG scores (Healthy Patients)";

documentset InclusionNotes:
     Clarity.createDocumentSet({
         "filter_query":"source:AACT"});

termset EcogTerms: [
        "ecog",
        "Eastern Cooperative Oncology Group"
        ];

define EcogScore:
  Clarity.ValueExtraction({
    documentset: [InclusionNotes],
    termset:[EcogTerms],
    minimum_value: "0",
    maximum_value: "5"
    });

define lowEcog:
   where EcogScore.value <= 2;


termset BrcaTerms:["BRCA", "br ca",
    "breast cancer", "breast carcinoma", "carcinoma of the breast",
    "Mammary Carcinoma", "cancer of the breast"];

define BrcaMention:
  Clarity.ProviderAssertion({
      documentset: [InclusionNotes],
    termset:[BrcaTerms]
    });

context Patient;

define final lowEcogAndBrca:
   where BrcaMention and lowEcog;
', '{
    "owner": "claritynlp",
    "name": "Breast Cancer Trials with low ECOG scores (Healthy Patients)",
    "population": "All",
    "context": "Patient",
    "phenotype": {
        "name": "Breast Cancer Trials with low ECOG scores (Healthy Patients)",
        "declaration": "phenotype",
        "version": "",
        "alias": "",
        "arguments": [],
        "named_arguments": {},
        "library": "ClarityNLP",
        "funct": "",
        "values": [],
        "description": "",
        "concept": ""
    },
    "valid": true,
    "term_sets": [
        {
            "name": "EcogTerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "ecog",
                "Eastern Cooperative Oncology Group"
            ],
            "description": "",
            "concept": ""
        },
        {
            "name": "BrcaTerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "BRCA",
                "br ca",
                "breast cancer",
                "breast carcinoma",
                "carcinoma of the breast",
                "Mammary Carcinoma",
                "cancer of the breast"
            ],
            "description": "",
            "concept": ""
        }
    ],
    "document_sets": [
        {
            "name": "InclusionNotes",
            "declaration": "documentset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "filter_query": "source:AACT"
            },
            "library": "Clarity",
            "funct": "createDocumentSet",
            "values": [],
            "description": "",
            "concept": ""
        }
    ],
    "data_entities": [
        {
            "name": "EcogScore",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "documentset": [
                    "InclusionNotes"
                ],
                "termset": [
                    "EcogTerms"
                ],
                "minimum_value": 0,
                "maximum_value": 5
            },
            "library": "Clarity",
            "funct": "ValueExtraction",
            "values": [],
            "description": "",
            "concept": "",
            "final": false,
            "raw_text": "",
            "job_results": []
        },
        {
            "name": "BrcaMention",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "documentset": [
                    "InclusionNotes"
                ],
                "termset": [
                    "BrcaTerms"
                ]
            },
            "library": "Clarity",
            "funct": "ProviderAssertion",
            "values": [],
            "description": "",
            "concept": "",
            "final": false,
            "raw_text": "",
            "job_results": []
        }
    ],
    "operations": [
        {
            "name": "lowEcog",
            "action": "<=",
            "data_entities": [
                "EcogScore.value",
                "2"
            ],
            "final": false,
            "raw_text": "EcogScore.value <= 2"
        },
        {
            "name": "lowEcogAndBrca",
            "action": "and",
            "data_entities": [
                "BrcaMention",
                "lowEcog"
            ],
            "final": true,
            "raw_text": "BrcaMention and lowEcog"
        }
    ],
    "debug": false,
    "limit": 0,
    "phenotype_id": 1
}', '2019-03-26 15:19:19.784000');
INSERT INTO nlp.nlpql_library (nlpql_id, nlpql_name, nlpql_version, nlpql_raw, nlpql_json, date_added) VALUES (3, 'Migraines and Mental Health', '1.0', 'phenotype "History of Migraines and Mental Health Symptoms";

termset MigraineTerms: [
        "migraine",
        "migraines"
        ];

define MigrainesMention:
  Clarity.ProviderAssertion({
    termset:[MigraineTerms]
    });

termset DepressionTerms:
   ["depression", "depressive"]
;

define DepressionMention:
  Clarity.ProviderAssertion({
    termset:[DepressionTerms]
    });

termset AnxietyTerms:
   ["Anxiety", "anxious", "panic disorder"]
;

define AnxietyMention:
  Clarity.ProviderAssertion({
    termset:[AnxietyTerms]
    });

termset PTSDTerms:
    ["PTSD", "post trauma", "post traumatic"];

define PTSDMention:
  Clarity.ProviderAssertion({
    termset:[PTSDTerms]
    });

termset StressTerms:
    ["stress", "stressful", "stressed"];

define StressMention:
  Clarity.ProviderAssertion({
    termset:[StressTerms]
    });

context Patient;

define final hasMigrainesAndOtherSymptoms:
   where MigrainesMention and (AnxietyMention or DepressionMention or PTSDMention or StressMention);
', '{
    "owner": "claritynlp",
    "name": "History of Migraines and Mental Health Symptoms",
    "population": "All",
    "context": "Patient",
    "phenotype": {
        "name": "History of Migraines and Mental Health Symptoms",
        "declaration": "phenotype",
        "version": "",
        "alias": "",
        "arguments": [],
        "named_arguments": {},
        "library": "ClarityNLP",
        "funct": "",
        "values": [],
        "description": "",
        "concept": ""
    },
    "valid": true,
    "term_sets": [
        {
            "name": "MigraineTerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "migraine",
                "migraines"
            ],
            "description": "",
            "concept": ""
        },
        {
            "name": "DepressionTerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "depression",
                "depressive"
            ],
            "description": "",
            "concept": ""
        },
        {
            "name": "AnxietyTerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "Anxiety",
                "anxious",
                "panic disorder"
            ],
            "description": "",
            "concept": ""
        },
        {
            "name": "PTSDTerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "PTSD",
                "post trauma",
                "post traumatic"
            ],
            "description": "",
            "concept": ""
        },
        {
            "name": "StressTerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "stress",
                "stressful",
                "stressed"
            ],
            "description": "",
            "concept": ""
        }
    ],
    "data_entities": [
        {
            "name": "MigrainesMention",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "termset": [
                    "MigraineTerms"
                ]
            },
            "library": "Clarity",
            "funct": "ProviderAssertion",
            "values": [],
            "description": "",
            "concept": "",
            "final": false,
            "raw_text": "",
            "job_results": []
        },
        {
            "name": "DepressionMention",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "termset": [
                    "DepressionTerms"
                ]
            },
            "library": "Clarity",
            "funct": "ProviderAssertion",
            "values": [],
            "description": "",
            "concept": "",
            "final": false,
            "raw_text": "",
            "job_results": []
        },
        {
            "name": "AnxietyMention",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "termset": [
                    "AnxietyTerms"
                ]
            },
            "library": "Clarity",
            "funct": "ProviderAssertion",
            "values": [],
            "description": "",
            "concept": "",
            "final": false,
            "raw_text": "",
            "job_results": []
        },
        {
            "name": "PTSDMention",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "termset": [
                    "PTSDTerms"
                ]
            },
            "library": "Clarity",
            "funct": "ProviderAssertion",
            "values": [],
            "description": "",
            "concept": "",
            "final": false,
            "raw_text": "",
            "job_results": []
        },
        {
            "name": "StressMention",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "termset": [
                    "StressTerms"
                ]
            },
            "library": "Clarity",
            "funct": "ProviderAssertion",
            "values": [],
            "description": "",
            "concept": "",
            "final": false,
            "raw_text": "",
            "job_results": []
        }
    ],
    "operations": [
        {
            "name": "hasMigrainesAndOtherSymptoms",
            "action": "and",
            "data_entities": [
                "MigrainesMention",
                "(AnxietyMentionorDepressionMentionorPTSDMentionorStressMention)"
            ],
            "final": true,
            "raw_text": "MigrainesMention and (AnxietyMentionorDepressionMentionorPTSDMentionorStressMention)"
        }
    ],
    "debug": false,
    "limit": 0,
    "phenotype_id": 1
}', '2019-03-26 15:21:03.253000');
INSERT INTO nlp.nlpql_library (nlpql_id, nlpql_name, nlpql_version, nlpql_raw, nlpql_json, date_added) VALUES (4, 'Pain n-grams', '1.0', ' phenotype "Pain n-gram" version "2";

 include ClarityCore version "1.0" called Clarity;

 termset PainTerms:
    ["pain", "distress", "distressed", "suffering","agony"];

  define final painNgrams:
    Clarity.ngram({
      termset:[PainTerms],
      "n": "3",
      "filter_nums": true,
      "filter_stops": true,
      "filter_punct": true,
      "min_freq": 1,
      "lemmas": true,
      "limit_to_termset": true
      });
', '{
    "owner": "claritynlp",
    "name": "Pain n-gram",
    "population": "All",
    "context": "Patient",
    "phenotype": {
        "name": "Pain n-gram",
        "declaration": "phenotype",
        "version": "2",
        "alias": "",
        "arguments": [],
        "named_arguments": {},
        "library": "ClarityNLP",
        "funct": "",
        "values": [],
        "description": "",
        "concept": ""
    },
    "valid": true,
    "includes": [
        {
            "name": "ClarityCore",
            "declaration": "include",
            "version": "1.0",
            "alias": "Clarity",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [],
            "description": "",
            "concept": ""
        }
    ],
    "term_sets": [
        {
            "name": "PainTerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "pain",
                "distress",
                "distressed",
                "suffering",
                "agony"
            ],
            "description": "",
            "concept": ""
        }
    ],
    "data_entities": [
        {
            "name": "painNgrams",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "termset": [
                    "PainTerms"
                ],
                "n": 3,
                "filter_nums": true,
                "filter_stops": true,
                "filter_punct": true,
                "min_freq": 1,
                "lemmas": true,
                "limit_to_termset": true
            },
            "library": "Clarity",
            "funct": "ngram",
            "values": [],
            "description": "",
            "concept": "",
            "final": true,
            "raw_text": "",
            "job_results": []
        }
    ],
    "debug": false,
    "limit": 0,
    "phenotype_id": 1
}', '2019-03-26 15:22:10.857000');
