OHDSI WebAPI Utilities
======================

/ohdsi_create_cohort?file=<FILENAME>
-------------------------------------

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
  http://nlp-api:5000/ohdsi_create_cohort?file=<FILENAME>
  ```

/ohdsi_get_cohort?cohort_id=<COHORT_ID>
---------------------------------------

- Description: Get cohort details from OHDSI.

- Method: GET

- Parameters:
  - cohort_id

- Usage:
  ```
  http://nlp-api:5000/ohdsi_get_cohort?cohort_id=<COHORT_ID>
  ```


/ohdsi_get_cohort_by_name?cohort_name=<COHORT_NAME>
---------------------------------------------------
- Description: Get Cohort details by name

- Method: GET

- Parameters:
  - cohort_name

- Usage:
  ```
  http://nlp-api:5000/ohdsi_get_cohort_by_name?cohort_name=<COHORT_NAME>
  ```

/ohdsi_get_conceptset?file=<FILENAME>
--------------------------------------

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
  http://nlp-api:5000/ohdsi_get_conceptset?file=<FILENAME>
  ```

/ohdsi_cohort_status?cohort_id=<COHORT_ID>
------------------------------------------

- Description: Get the status of the triggered cohort creation job.

- Method: GET

- Parameters:
  - cohort_id

- Usage:
  ```
  http://nlp-api:5000/ohdsi_cohort_status?cohort_id=<COHORT_ID>
  ```
