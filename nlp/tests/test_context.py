try:
    from .algorithms import *
except Exception:
    from algorithms import *
from claritynlp_logging import log, ERROR, DEBUG

ctxt = Context()


def test_hypothetical():
    c = ctxt.run_context("pass out",
                          "She had definite   presyncope with lightheadedness and dizziness as if she was going to PASS OUT.")
    log(c)
    assert c is not None
    assert c.temporality == Temporality.Hypothetical


def test_history():
    c = ctxt.run_context("coronary artery disease",
                 "MEDICAL HISTORY:   Atrial fibrillation, hypertension, arthritis, CORONARY ARTERY DISEASE, GERD,   cataracts, and cancer of the left eyelid.")
    assert c is not None
    assert c.temporality == Temporality.Historical


def test_negation():
    c = ctxt.run_context("pneumonia", "However, no evidence of pleural effusion or acute pneumonia. ")
    assert c is not None
    assert c.negex == Negation.Negated


def test_experiencer():
    c = ctxt.run_context("heart attack", "FAMILY HISTORY: grandmother recently suffered heart attack")
    assert c is not None
    assert c.experiencier == Experiencer.Other
