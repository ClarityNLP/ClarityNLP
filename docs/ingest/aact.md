### Migrating data from AACT Database to ClarityNLP's Solr Instance

**Parameters:** None

**Example Usage:** `~/upload_from_aact`

**About:** 

POST an array of JSON objects, where each JSON object has the below structure. Endpoints and Request creation can be found in `upload.py`. 

```
    {
        "subject": 123456,
        "description_attr": "Report",
        "source": "Report Source",
        "report_type": "Report Type",
        "report_text": "Report Content",
        "cg_id": "CG ID",
        "report_id": "Report ID",
        "is_error_attr": "",
        "id": 1234,
        "store_time_attr": "",
        "chart_time_attr": "",
        "admission_id": 12345,
        "report_date": "2161-06-13T04:00:00Z"
    }
```