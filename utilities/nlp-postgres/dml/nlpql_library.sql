INSERT INTO nlp.nlpql_library (nlpql_id, nlpql_name, nlpql_version, nlpql_raw, nlpql_json, date_added) VALUES (4, 'Pain n-grams', '1.0', ' phenotype "Pain n-gram" version "2";
limit 100;
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
    "limit": 100,
    "phenotype_id": 1
}', '2019-03-26 15:22:10.857000');
INSERT INTO nlp.nlpql_library (nlpql_id, nlpql_name, nlpql_version, nlpql_raw, nlpql_json, date_added) VALUES (1, 'Prostate Cancer Term Proximity', '1.0', 'phenotype "Prostate Cancer Term Proximity" version "1";



documentset Docs:
    Clarity.createDocumentSet({
        "query":"report_text:prostate",
        
        "filter_query":"source:AACT"
    });

define final TermProximityFunction:
    Clarity.TermProximityTask({
        documentset:[Docs],
        "termset1": "prostate",
        "termset2": "cancer, Gleason, Gleason''s, Gleasons,adenocarcinoma, carcinoma",
        "word_distance": 7,
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
    "document_sets": [
        {
            "name": "Docs",
            "declaration": "documentset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "query": "report_text:prostate",
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
            "name": "TermProximityFunction",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "documentset": [
                    "Docs"
                ],
                "termset1": "prostate",
                "termset2": "cancer, Gleason, Gleason''s, Gleasons,adenocarcinoma, carcinoma",
                "word_distance": 7,
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
INSERT INTO nlp.nlpql_library (nlpql_id, nlpql_name, nlpql_version, nlpql_raw, nlpql_json, date_added) VALUES (5, 'Ejection Fraction Ranges', '1.0', 'limit 1000;

//phenotype name
phenotype "Ejection Fraction Values" version "1";

//include Clarity main NLP libraries
include ClarityCore version "1.0" called Clarity;

termset EjectionFractionTerms:
  ["ef","ejection fraction","lvef"];

define EjectionFraction:
  Clarity.ValueExtraction({
    termset:[EjectionFractionTerms],
    minimum_value: "10",
    maximum_value: "85"
    });

//logical Context (Patient, Document)
context Patient;

define final LowEFPatient:
    where EjectionFraction.value < 40;

define final BorderlineLowEFPatient:
    where EjectionFraction.value > 40 AND EjectionFraction.value < 50;

define final NormalLowEFPatient:
    where EjectionFraction.value > 49 AND EjectionFraction.value < 71;
', '{
    "owner": "claritynlp",
    "name": "Ejection Fraction Values",
    "population": "All",
    "context": "Patient",
    "phenotype": {
        "name": "Ejection Fraction Values",
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
            "name": "EjectionFractionTerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "ef",
                "ejection fraction",
                "lvef"
            ],
            "description": "",
            "concept": ""
        }
    ],
    "data_entities": [
        {
            "name": "EjectionFraction",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "termset": [
                    "EjectionFractionTerms"
                ],
                "minimum_value": 10,
                "maximum_value": 85
            },
            "library": "Clarity",
            "funct": "ValueExtraction",
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
            "name": "LowEFPatient",
            "action": "<",
            "data_entities": [
                "EjectionFraction.value",
                "40"
            ],
            "final": true,
            "raw_text": "EjectionFraction.value < 40"
        },
        {
            "name": "BorderlineLowEFPatient",
            "action": "AND",
            "data_entities": [
                "EjectionFraction.value>40",
                "EjectionFraction.value
<50"
            ],
            "final": true,
            "raw_text": "EjectionFraction.value>40 AND EjectionFraction.value
    <50"
        },
        {
            "name": "NormalLowEFPatient",
            "action": "AND",
            "data_entities": [
                "EjectionFraction.value>49",
                "EjectionFraction.value
        <71"
            ],
            "final": true,
            "raw_text": "EjectionFraction.value>49 AND EjectionFraction.value
            <71"
        }
    ],
    "debug": false,
    "limit": 1000,
    "phenotype_id": 1
}', '2019-03-26 22:32:32.815000');
INSERT INTO nlp.nlpql_library (nlpql_id, nlpql_name, nlpql_version, nlpql_raw, nlpql_json, date_added) VALUES (3, 'NLPQL Expression Samples', '1.0', 'limit 50;

phenotype "NLPQL Expression Samples" version "1";
description "Expression evaluation using data from mtsamples.com.";
include ClarityCore version "1.0" called Clarity;

documentset Docs:
    Clarity.createDocumentSet({
        "report_types":[
            "MTSAMPLES"
        ],
        "filter_query":"source:MTSAMPLES"
    });

termset DyspneaTerms: [
    "shortness of breath",
    "short of breath",
    "labored breathing",
    "dyspnea",
    "dyspneic"
];

termset TachycardiaTerms: [
    "tachycardia",
    "tachycardic"
];

termset TempTerms: [
    "temp",
    "temperature",
    "t",
    "t-max"
];

termset LesionTerms: [
    "lesion",
    "mass",
    "wound",
    "density",
    "tumor"
];

termset SmokingTerms: [
    "smoker",
    "history of smoking",
    "had been smoking",
    "has been smoking",
    "quit smoking",
    "former smoker"
];

termset FibrillationTerms: [
    "atrial fibrillation"
];

define hasDyspnea:
    Clarity.ProviderAssertion({
        documentset:[Docs],
        termset:[DyspneaTerms]
    });

define hasTachycardia:
    Clarity.ProviderAssertion({
        documentset:[Docs],
        termset:[TachycardiaTerms]
    });

define hasSmokingHistory:
    Clarity.ProviderAssertion({
        documentset:[Docs],
        termset:[SmokingTerms]
    });

define hasAFib:
    Clarity.ProviderAssertion({
        documentset:[Docs],
        termset:[FibrillationTerms]
    });

define Temperature:
  Clarity.ValueExtraction({
      documentset:[Docs],
      termset:[TempTerms],
      minimum_value: "96",
      maximum_value: "106"
  });

define LesionMeas:
    Clarity.MeasurementFinder({
        documentset:[Docs],
        termset:[LesionTerms]
    });

// Tell ClarityNLP to look for patients who satisfy the conditions below.
// Patients are identified by a patient ID, which can be found in the
// ''subject'' field of the CSV result file.

context Patient;



// Find patients with a history of smoking, who also have dyspnea.
// Should find subjects 6 and 7.
define SmokerWithDyspnea:
    where hasSmokingHistory AND hasDyspnea;

// Here are two definitions of a smoker with dyspnea and tachycardia.
// Both should find identical sets of patients (which in this case is
// a single patient, subject 7).

// 1. use the previous definition of ''SmokerWithDyspnea''
define SmokerWithDyspneaAndTachycardia1:
    where SmokerWithDyspnea AND hasTachycardia;

// 2. define all conditions explicitly
define SmokerWithDyspneaAndTachycardia2:
    where hasSmokingHistory AND hasDyspnea AND hasTachycardia;

// Find patients with lesions greater than or equal to 2 cm in the
// X dimension, in both X and Y, and in X, Y, and Z.
// ClarityNLP normalizes all dimensions to millimeters, so 2 cm == 20 mm.

// should find subjects 11 and 14
define hasLesionGe2cmX:
    where LesionMeas.dimension_X >= 20;

// should find subject 14
define hasLesionGe2cmXY:
    where LesionMeas.dimension_X >= 20 AND
          LesionMeas.dimension_Y >= 20;

// no patients satisfy this condition
define hasLesionGe2cmXYZ:
    where LesionMeas.dimension_X >= 20 AND
          LesionMeas.dimension_Y >= 20 AND
          LesionMeas.dimension_Z >= 20;

// Find patients with lesions whose X dimension is between 1 and 4 cm.

// should find subjects 3, 11 and 14
define hasLesion1to4cm:
    where LesionMeas.dimension_X >= 10 AND LesionMeas.dimension_X <= 40;

// Find patients with lesions of this size who are also smokers.

// should find subjects 11 and 14
define SmokerWithLesion2to4cm:
    where hasSmokingHistory AND
        (LesionMeas.dimension_X >= 10 AND LesionMeas.dimension_X <= 40);

// Find patients with both dyspnea and atrial fibrillation.

// should find subjects 4, 8, and 13
define hasDyspneaAndAFib:
    where hasDyspnea AND hasAFib;

// Find patients with fever.

// should find subject 10
define hasFever:
    where Temperature.value >= 100.4;

// Find all patients who have fever, dyspnea, atrial fibrillation, or
// one or more lesions with any dimension greater than 2 cm.
// Should find subjects 4, 8, 10, 11, 13, and 14.

// 1. Use the definitions above
define final hasSymptoms1:
    where hasFever            OR
          hasDyspneaAndAFib   OR
          hasLesionGe2cmX     OR
          hasLesionGe2cmXY    OR
          hasLesionGe2cmXYZ;

// Find the same patients, with all conditions made explicit:

define hasSymptoms2:
    where (Temperature.value >= 100.4)       OR
          (hasDyspnea AND hasAFib)           OR
          (LesionMeas.dimension_X >= 20)     OR 
          (LesionMeas.dimension_X >= 20 AND LesionMeas.dimension_Y >= 20)  OR
          (LesionMeas.dimension_X >= 20 AND LesionMeas.dimension_Y >= 20 AND LesionMeas.dimension_Z >= 20);

', '{
    "owner": "claritynlp",
    "name": "NLPQL Expression Samples",
    "description": "\"Expression evaluation using data from mtsamples.com.\"",
    "population": "All",
    "context": "Patient",
    "phenotype": {
        "name": "NLPQL Expression Samples",
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
            "name": "DyspneaTerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "shortness of breath",
                "short of breath",
                "labored breathing",
                "dyspnea",
                "dyspneic"
            ],
            "description": "",
            "concept": ""
        },
        {
            "name": "TachycardiaTerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "tachycardia",
                "tachycardic"
            ],
            "description": "",
            "concept": ""
        },
        {
            "name": "TempTerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "temp",
                "temperature",
                "t",
                "t-max"
            ],
            "description": "",
            "concept": ""
        },
        {
            "name": "LesionTerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "lesion",
                "mass",
                "wound",
                "density",
                "tumor"
            ],
            "description": "",
            "concept": ""
        },
        {
            "name": "SmokingTerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "smoker",
                "history of smoking",
                "had been smoking",
                "has been smoking",
                "quit smoking",
                "former smoker"
            ],
            "description": "",
            "concept": ""
        },
        {
            "name": "FibrillationTerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "atrial fibrillation"
            ],
            "description": "",
            "concept": ""
        }
    ],
    "document_sets": [
        {
            "name": "Docs",
            "declaration": "documentset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "report_types": [
                    "MTSAMPLES"
                ],
                "filter_query": "source:MTSAMPLES"
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
            "name": "hasDyspnea",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "documentset": [
                    "Docs"
                ],
                "termset": [
                    "DyspneaTerms"
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
            "name": "hasTachycardia",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "documentset": [
                    "Docs"
                ],
                "termset": [
                    "TachycardiaTerms"
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
            "name": "hasSmokingHistory",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "documentset": [
                    "Docs"
                ],
                "termset": [
                    "SmokingTerms"
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
            "name": "hasAFib",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "documentset": [
                    "Docs"
                ],
                "termset": [
                    "FibrillationTerms"
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
            "name": "Temperature",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "documentset": [
                    "Docs"
                ],
                "termset": [
                    "TempTerms"
                ],
                "minimum_value": 96,
                "maximum_value": 106
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
            "name": "LesionMeas",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "documentset": [
                    "Docs"
                ],
                "termset": [
                    "LesionTerms"
                ]
            },
            "library": "Clarity",
            "funct": "MeasurementFinder",
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
            "name": "SmokerWithDyspnea",
            "action": "AND",
            "data_entities": [
                "hasSmokingHistory",
                "hasDyspnea"
            ],
            "final": false,
            "raw_text": "hasSmokingHistory AND hasDyspnea"
        },
        {
            "name": "SmokerWithDyspneaAndTachycardia1",
            "action": "AND",
            "data_entities": [
                "SmokerWithDyspnea",
                "hasTachycardia"
            ],
            "final": false,
            "raw_text": "SmokerWithDyspnea AND hasTachycardia"
        },
        {
            "name": "SmokerWithDyspneaAndTachycardia2",
            "action": "AND",
            "data_entities": [
                "hasSmokingHistory",
                "hasDyspnea",
                "hasTachycardia"
            ],
            "final": false,
            "raw_text": "hasSmokingHistory AND hasDyspnea AND hasTachycardia"
        },
        {
            "name": "hasLesionGe2cmX",
            "action": ">=",
            "data_entities": [
                "LesionMeas.dimension_X",
                "20"
            ],
            "final": false,
            "raw_text": "LesionMeas.dimension_X >= 20"
        },
        {
            "name": "hasLesionGe2cmXY",
            "action": "AND",
            "data_entities": [
                "LesionMeas.dimension_X>=20",
                "LesionMeas.dimension_Y>=20"
            ],
            "final": false,
            "raw_text": "LesionMeas.dimension_X>=20 AND LesionMeas.dimension_Y>=20"
        },
        {
            "name": "hasLesionGe2cmXYZ",
            "action": "AND",
            "data_entities": [
                "LesionMeas.dimension_X>=20",
                "LesionMeas.dimension_Y>=20",
                "LesionMeas.dimension_Z>=20"
            ],
            "final": false,
            "raw_text": "LesionMeas.dimension_X>=20 AND LesionMeas.dimension_Y>=20 AND LesionMeas.dimension_Z>=20"
        },
        {
            "name": "hasLesion1to4cm",
            "action": "AND",
            "data_entities": [
                "LesionMeas.dimension_X>=10",
                "LesionMeas.dimension_X<=40"
            ],
            "final": false,
            "raw_text": "LesionMeas.dimension_X>=10 AND LesionMeas.dimension_X<=40"
        },
        {
            "name": "SmokerWithLesion2to4cm",
            "action": "AND",
            "data_entities": [
                "hasSmokingHistory",
                "(LesionMeas.dimension_X>=10ANDLesionMeas.dimension_X<=40)"
            ],
            "final": false,
            "raw_text": "hasSmokingHistory AND (LesionMeas.dimension_X>=10ANDLesionMeas.dimension_X<=40)"
        },
        {
            "name": "hasDyspneaAndAFib",
            "action": "AND",
            "data_entities": [
                "hasDyspnea",
                "hasAFib"
            ],
            "final": false,
            "raw_text": "hasDyspnea AND hasAFib"
        },
        {
            "name": "hasFever",
            "action": ">=",
            "data_entities": [
                "Temperature.value",
                "100.4"
            ],
            "final": false,
            "raw_text": "Temperature.value >= 100.4"
        },
        {
            "name": "hasSymptoms1",
            "action": "OR",
            "data_entities": [
                "hasFever",
                "hasDyspneaAndAFib",
                "hasLesionGe2cmX",
                "hasLesionGe2cmXY",
                "hasLesionGe2cmXYZ"
            ],
            "final": true,
            "raw_text": "hasFever OR hasDyspneaAndAFib OR hasLesionGe2cmX OR hasLesionGe2cmXY OR hasLesionGe2cmXYZ"
        },
        {
            "name": "hasSymptoms2",
            "action": "OR",
            "data_entities": [
                "(Temperature.value>=100.4)",
                "(hasDyspneaANDhasAFib)",
                "(LesionMeas.dimension_X>=20)",
                "(LesionMeas.dimension_X>=20ANDLesionMeas.dimension_Y>=20)",
                "(LesionMeas.dimension_X>=20ANDLesionMeas.dimension_Y>=20ANDLesionMeas.dimension_Z>=20)"
            ],
            "final": false,
            "raw_text": "(Temperature.value>=100.4) OR (hasDyspneaANDhasAFib) OR (LesionMeas.dimension_X>=20) OR (LesionMeas.dimension_X>=20ANDLesionMeas.dimension_Y>=20) OR (LesionMeas.dimension_X>=20ANDLesionMeas.dimension_Y>=20ANDLesionMeas.dimension_Z>=20)"
        }
    ],
    "debug": false,
    "limit": 50,
    "phenotype_id": 1
}', '2019-03-26 15:21:03.253000');
INSERT INTO nlp.nlpql_library (nlpql_id, nlpql_name, nlpql_version, nlpql_raw, nlpql_json, date_added) VALUES (6, 'NYHA Class', '1.0', 'limit 500;

//phenotype name
phenotype "NYHA Class" version "1";

//include Clarity  main NLP libraries
include ClarityCore version "1.0" called Clarity;

termset NYHATerms:
  ["nyha", "New York Heart Association"];

define final NYHAClass:
  Clarity.ValueExtraction({
    termset:[NYHATerms],
    enum_list: ["3","4","iii","iv"];
    });', '{
    "owner": "claritynlp",
    "name": "NYHA Class",
    "population": "All",
    "context": "Patient",
    "phenotype": {
        "name": "NYHA Class",
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
            "name": "NYHATerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "nyha",
                "New York Heart Association"
            ],
            "description": "",
            "concept": ""
        }
    ],
    "data_entities": [
        {
            "name": "NYHAClass",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "termset": [
                    "NYHATerms"
                ],
                "enum_list": [
                    "3",
                    "4",
                    "iii",
                    "iv"
                ]
            },
            "library": "Clarity",
            "funct": "ValueExtraction",
            "values": [],
            "description": "",
            "concept": "",
            "final": true,
            "raw_text": "",
            "job_results": []
        }
    ],
    "debug": false,
    "limit": 500,
    "phenotype_id": 1
}', '2019-03-26 22:34:48.056000');
INSERT INTO nlp.nlpql_library (nlpql_id, nlpql_name, nlpql_version, nlpql_raw, nlpql_json, date_added) VALUES (2, 'Breast Cancer in Clinical Trials', '1.0', 'phenotype "Breast Cancer Trials";

limit 1000;

documentset InclusionNotes:
     Clarity.createDocumentSet({
         "query": "breast OR mammary OR brca OR ''br ca''",
         "filter_query":"report_type:''Clinical Trial Inclusion Criteria'' AND source:AACT"});

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

define final BrcaMention:
  Clarity.ProviderAssertion({
      documentset: [InclusionNotes],
    termset:[BrcaTerms]
    });

context Patient;

define final lowEcogAndBrca:
   where BrcaMention and lowEcog;
', '{
    "owner": "claritynlp",
    "name": "Breast Cancer Trials",
    "population": "All",
    "context": "Patient",
    "phenotype": {
        "name": "Breast Cancer Trials",
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
                "query": "breast OR mammary OR brca OR ''br ca''",
                "filter_query": "report_type:''Clinical Trial Inclusion Criteria'' AND source:AACT"
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
            "final": true,
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
    "limit": 1000,
    "phenotype_id": 1
}', '2019-03-26 15:19:19.784000');
INSERT INTO nlp.nlpql_library (nlpql_id, nlpql_name, nlpql_version, nlpql_raw, nlpql_json, date_added) VALUES (7, 'Karnofksy Score', '1.0', 'phenotype "Karnofksy Score" version "1";

limit 100;

termset KarnofksyTerms: [
        "KARNOFSKY",
        "KARNOVSKY"
        ];

//Quantitative metrics
define final KarnofskyScore:
  Clarity.ValueExtraction({
    termset:[KarnofksyTerms],
    minimum_value: "0",
    maximum_value: "100"
    });


//CDS logical Context (Patient, Document)
context Patient;

', '{
    "owner": "claritynlp",
    "name": "Karnofksy Score",
    "population": "All",
    "context": "Patient",
    "phenotype": {
        "name": "Karnofksy Score",
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
    "term_sets": [
        {
            "name": "KarnofksyTerms",
            "declaration": "termset",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {},
            "library": "ClarityNLP",
            "funct": "",
            "values": [
                "KARNOFSKY",
                "KARNOVSKY"
            ],
            "description": "",
            "concept": ""
        }
    ],
    "data_entities": [
        {
            "name": "KarnofskyScore",
            "declaration": "define",
            "version": "",
            "alias": "",
            "arguments": [],
            "named_arguments": {
                "termset": [
                    "KarnofksyTerms"
                ],
                "minimum_value": 0,
                "maximum_value": 100
            },
            "library": "Clarity",
            "funct": "ValueExtraction",
            "values": [],
            "description": "",
            "concept": "",
            "final": true,
            "raw_text": "",
            "job_results": []
        }
    ],
    "debug": false,
    "limit": 100,
    "phenotype_id": 1
}', '2019-03-26 22:38:01.619000');