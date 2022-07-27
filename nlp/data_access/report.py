from claritynlp_logging import log

try:
    from .base_model import BaseModel
except Exception as e:
    log(e)
    from base_model import BaseModel


class Report(dict):
    """
            {
                "report_type": "CLARITYNLP_VALIDATION_0",
                "id": "0",
                "report_id": "0",
                "source": "CLARITYNLP_VALIDATION_0",
                "report_date": "2022-06-24T15:02:43.378272Z",
                "subject": "-1",
                "report_text": "The patient is a caucasian male, age 40 years."
            }
    """

    def __init__(self, _id: str = '', report_id: str = '', source: str = '',
                 report_date: str = '', subject: str = '',
                 report_type: str = '', report_text: str = ''):
        self.id = _id
        self.report_id = report_id
        self.source = source
        self.report_date = report_date
        self.subject = subject
        self.report_type = report_type
        self.report_text = report_text

        dict.__init__(self, id=_id, report_id=report_id, source=source,
                      report_date=report_date, subject=subject,
                      report_type=report_type, report_text=report_text)
