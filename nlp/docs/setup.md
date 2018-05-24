## Docker Setup
This is the recommended setup as it configures Solr, Postgres, Mongo and the entire Clarity ecosystem.
See the [Clarity](https://github.com/ClarityNLP/clarity) repository to get going.

## Local Flask Setup


Note: These instructions are only needed if you are not install via Docker through Clarity. In that case, you can skip past this setup.

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

#### Vocabulary
OMOP Vocabulary should be loaded (TODO)

#### Properties
Copy `example.cfg` to `project.cfg` and update with your settings.

#### Solr
TODO

#### Postgres
Setup with DDL in `scripts/ddl.sql`

#### Temp directory
Setup a temporary directory on your system, make sure it's writable by the user running the application, and set the value in tmp.dir in project.cfg

#### Running Locally

#### Running the Luigi Central Scheduler
luigid --background --pidfile <PATH_TO_PIDFILE> --logdir <PATH_TO_LOGDIR> --state-path <PATH_TO_STATEFILE>

#### Run Flask app
```bash
FLASK_APP=api.py flask run
```

### Local Docker

#### Building Image
```docker build -t health-nlp-sample:latest . ```

#### Running Application
```docker run -d -p 5000:5000 health-nlp-sample```