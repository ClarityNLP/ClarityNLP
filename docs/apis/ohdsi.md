# OHDSI WebAPI Utilities

## Creating Cohorts

- Description:
  - Creating cohorts using OHDSI web API.
  - API requires a JSON file which contains cohort creation details.
  - JSON file must be placed in `/ohdsi/data/`
  - `test_cohort.json` is an example file which depicts the JSON structure which needs to be *strictly* followed.

- Method: GET

- Parameters:
  - JSON file name

- Usage:
  ```
  http://nlp-api:5000/ohdsi_create_cohort?file=<FILE NAME>
  ```

## Getting Cohort Information

- Description: Get cohort details from OHDSI.

- Method: GET

- Parameters:
  - cohort_id

- Usage:
  ```
  http://nlp-api:5000/ohdsi_get_cohort?cohort_id=<COHORT ID>
  ```


## Getting Cohort Information from Cohort Name

- Description: Get Cohort details by name

- Method: GET

- Parameters:
  - cohort_name

- Usage:
  ```
  http://nlp-api:5000/ohdsi_get_cohort_by_name?cohort_name=<COHORT NAME>
  ```

## Getting Concept Sets

- Description:
  - Getting concept set info using OHDSI web API.
  - API requires a JSON file which contains concept set details.
  - JSON file must be placed in `/ohdsi/data/`
  - `test_concept.json` is an example file which depicts the JSON structure which needs to be *strictly* followed.

- Method: GET

- Parameters:
  - JSON file name

- Usage:
  ```
  http://nlp-api:5000/ohdsi_get_conceptset?file=<FILE NAME>
  ```

## Getting Cohort Creation Status

- Description: Get the status of the triggered cohort creation job.

- Method: GET

- Parameters:
  - cohort_id

- Usage:
  ```
  http://nlp-api:5000/ohdsi_cohort_status?cohort_id=<COHORT ID>
  ```
