# health-nlp

#### Version
This library uses Python 3.

## Setup

#### Installing Requirements
```
pip3 install -r requirements.txt
pip3 install -U pytest
python3 -m spacy download en
python -m spacy download en_core_web_md
```
If you want to use conda, you can setup the environment using `spec-file.txt`
##### Install models 

```bash 
python3 install_models.py
```

### Vocabulary
OMOP Vocabulary should be loaded (TODO)

#### Properties
Copy `example.cfg` to `project.cfg` and update with your settings.

#### Solr
TODO

#### Postgres
Setup with DDL in `scripts/ddl.sql`

### Temp directory
Setup a temporary directory on your system, make sure it's writable by the user running the application, and set the value in tmp.dir in project.cfg

## Running

#### Running the Luigi Central Scheduler
luigid --background --pidfile <PATH_TO_PIDFILE> --logdir <PATH_TO_LOGDIR> --state-path <PATH_TO_STATEFILE>

#### Run Flask app
```bash
FLASK_APP=api.py flask run
```

#### Run the NER Pipeline with pipeline id of 1
```bash
PYTHONPATH='.' luigi --module luigi_pipeline NERPipeline --pipeline 1 --job 1234 --owner user 
```

## Docker

#### Building Image
```docker build -t health-nlp-sample:latest . ```

#### Running Application
```docker run -d -p 5000:5000 health-nlp-sample```

## API Usage

### n-gram Generator

**Fields:**

- Cohort ID : mandatory
- Keyword : optional
- n : mandatory
- frequency : mandatory

**Example usage:** 

`~/ngram?cohort_id=6&n=15&frequency=10`

`~/ngram?cohort_id=6&keyword=cancer&n=15&frequency=10`



### OMOP Vocabulary

**Fields:**

- Type: mandatory
  - 1: synonyms
  - 2: ancestors
  - 3: descendants
- Concept: mandatory
- Vocab: optional

**Example usage:**

`~/vocabExpansion?type=1&concept=Inactive`

`~/vocabExpansion?type=1&concept=Inactive&vocab=SNOMED`



### Migrating data from AACT Database to Clarity's Solr Instance

**Fields:** None

**Example Usage:** `~/upload_from_aact`

**API Structure:** 

POST an array of JSON objects, where each JSON object has the below structure. Endpoints and Request creation can be found in `upload.py`. 

```
    {
        "subject": 123456,
        "description_attr": "Report",
        "source": "Report Source",
        "report_type": "Report Type",
        "report_text": "Report Content",
        "cg_id": "CD ID",
        "report_id": "Report ID",
        "is_error_attr": "",
        "id": 1234,
        "store_time_attr": "",
        "chart_time_attr": "",
        "admission_id": 12345,
        "report_date": "2161-06-13T04:00:00Z"
    }
```
