### Migrating data from AACT Database to ClarityNLP's Solr Instance

**Parameters:** None

**Example Usage:** `~/upload_from_aact`

**About:** 

POST an array of JSON objects, where each JSON object has the below structure. Endpoints and Request creation can be found in `upload.py`. 

```
    {
        "subject": 123456,
        "source": "Report Source",
        "report_type": "Report Type",
        "report_text": "Report Content",
        "report_id": "Report ID",
        "id": 1234,
        "report_date": "2161-06-13T04:00:00Z"
    }
```