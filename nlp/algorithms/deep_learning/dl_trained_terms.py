import pickle
from joblib import load
import os

SCRIPT_DIR = os.path.dirname(__file__)
model_path = os.path.join(SCRIPT_DIR, "models" )
vectorizer_path = os.path.join(SCRIPT_DIR, "trained_vectorizer.pk")

lookup = {"a fib": "is_afib", "pantoprazole": "is_pantoprazole", "respiratory failure": "is_respiratory_failure",
          "man": "is_male", "atrial fabrillation": "is_afib", "acetaminophen": "is_acetaminophen",
          "congestive heart disease": "is_chf", "atrial fib": "is_afib", "urinary tract infection": "is_uti",
          "woman": "is_female", "high blood pressure": "is_hypertension", "asian": "is_asian",
          "auricular fibrulation": "is_afib", "chf - congestive heart failure": "is_chf", "gerd": "is_gerd",
          "men": "is_male", "hypertension": "is_hypertension", "high blood cholesterol": "is_high_cholesterol",
          "atr fibrilation": "is_afib", "alaska native": "is_native_american", "auricular fabrillation": "is_afib",
          "native american": "is_native_american", "male": "is_male", "aflutter": "is_afib",
          "metoprolol": "is_metoprolol", "sodium chloride": "is_sodium_chloride", "glucose": "is_glucose",
          "gastroesophageal reflux": "is_gerd", "uti": "is_uti", "heparin": "is_heparin",
          "ccf - congestive cardiac failure": "is_chf", "hyperlipidemia": "is_high_cholesterol",
          "postmenopausal": "is_female", "atrial fibrillation": "is_afib", "magnesium sulfate": "is_magnesium_sulfate",
          "dm": "is_diabetes", "black": "is_black", "girls": "is_female", "high cholesterol": "is_high_cholesterol",
          "atrial flutter": "is_afib", "auricular fib": "is_afib", "women": "is_female",
          "native hawaiian": "is_pacific_islander", "atr fabrillation": "is_afib",
          "pacific islander": "is_pacific_islander", "renal failure": "is_renal_failure",
          "arteriosclerosis": "is_arteriosclerosis", "urinary tract infectious disease": "is_uti",
          "female": "is_female", "girl": "is_female", "atrial fibrilation": "is_afib", "white": "is_white",
          "chf": "is_chf", "pregnant": "is_female", "auricular fibrillation": "is_afib", "boy": "is_male",
          "congestive cardiac failure": "is_chf", "afib": "is_afib", "congestive heart failure (disorder)": "is_chf",
          "menopausal": "is_female", "atrial fibrulation": "is_afib", "congestive heart failure": "is_chf",
          "furosemide": "is_furosemide", "docusate": "is_docusate", "congestive heart failure (finding)": "is_chf",
          "auricular fibrilation": "is_afib", "diabetes": "is_diabetes", "potassium": "is_potassium",
          "atr fibrulation": "is_afib", "atr fib": "is_afib", "african american": "is_black", "boys": "is_male",
          "caucasian": "is_white", "atr fibrillation": "is_afib"}


# predict_primitive_label("./trained_vectorizer.pk","./models", "is_female", "the patient has hypertension")
def predict_primitive_label(path_to_vectorizer, path_to_models_dir, primitive, new_note_text):
    with open(path_to_vectorizer, 'rb') as f:
        vectorizer = pickle.load(f)

        new_x = vectorizer.transform([new_note_text])

    with open("{}/{}_trained_dnn_smotev2.joblib".format(path_to_models_dir, primitive), 'rb') as m:
        clf = load(m)

        y_pred = clf.predict(new_x)
        return y_pred


def do_term_lookup(termlist, note_text):
    lower = [x.lower() for x in termlist]
    primitives = set()
    for t in lower:
        if t in lookup:
            primitives.add(lookup[t])
    predictions = dict()
    for p in primitives:
        pred = predict_primitive_label(vectorizer_path, model_path, p, note_text)
        if len(pred) > 0 and pred[0] == 1:
            predictions[p] = True
    for p in primitives:
        if p not in predictions:
            predictions[p] = False
    return predictions
