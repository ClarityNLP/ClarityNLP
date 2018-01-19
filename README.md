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
PYTHONPATH='.' luigi --module pipeline NERPipeline --pipeline 1 --job 1234 --owner user --local-scheduler
```

## Docker

#### Building Image
```docker build -t health-nlp-sample:latest . ```

#### Running Application
```docker run -d -p 5000:5000 health-nlp-sample```

## API Usage

#### n-gram

Fields

- Cohort ID : mandatory
- Keyword : optional
- n : mandatory
- frequency : mandatory

Example usage 

`~/ngram?cohort_id=6&n=15&frequency=10`

`~/ngram?cohort_id=6&keyword=cancer&n=15&frequency=10`
