"""
Vocabulary Expansion

- synonyms
- ancestors
- descendants
"""

import re
import psycopg2
import psycopg2.extras
import requests
import json
from claritynlp_logging import log, ERROR, DEBUG


# Function to get synonyms for given concept
def get_synonyms(conn_string, concept, vocabulary):
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    if vocabulary is None:
        vocabulary = "SNOMED"


    try:
        cursor.execute(""" SELECT concept_synonym_name
        FROM nlp.concept_synonym s INNER JOIN nlp.concept c on c.concept_id = s.concept_id
        WHERE lower(concept_name) = %s and c.vocabulary_id=%s and invalid_reason is null
        order by concept_synonym_name
        """, (concept.lower(), vocabulary))

        result = cursor.fetchall()

        return result

    except Exception as ex:
        log('Failed to get synonyms')
        log(str(ex))

    finally:
        conn.close()

    return list()


# Function to get ancestors for given concept
def get_ancestors(conn_string, concept, vocabulary):
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    if vocabulary is None:
        vocabulary = "SNOMED"

    try:
        cursor.execute(""" SELECT concept_name
        FROM nlp.concept_ancestor INNER JOIN nlp.concept on concept_id = ancestor_concept_id
        WHERE descendant_concept_id in (SELECT concept_id from nlp.concept where lower(concept_name) = %s
        AND vocabulary_id=%s AND invalid_reason IS null) AND vocabulary_id=%s AND invalid_reason is null
        order by max_levels_of_separation asc
        """, (concept.lower(), vocabulary, vocabulary))

        result = cursor.fetchall()
        return result
    except Exception as ex:
        log('Failed to get ancestors')
        log(str(ex))

    finally:
        conn.close()

    return list()


# Function to get descendants for given concept
def get_descendants(conn_string, concept, vocabulary):
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    if vocabulary is None:
        vocabulary = "SNOMED"

    try:
        cursor.execute(""" SELECT concept_name
        FROM nlp.concept_ancestor INNER JOIN nlp.concept on concept_id = descendant_concept_id
        WHERE ancestor_concept_id in (SELECT concept_id from nlp.concept where lower(concept_name) = %s
        AND vocabulary_id=%s AND invalid_reason IS null) AND vocabulary_id=%s AND invalid_reason is null
        order by max_levels_of_separation asc
        """, (concept.lower(), vocabulary, vocabulary))

        result = cursor.fetchall()
        return result

    except Exception as ex:
        log('Failed to get descendants')
        log(str(ex))

    finally:
        conn.close()

    return list()


def get_related_terms(conn_string, concept, vocabulary, get_synonyms_bool=True, get_descendants_bool=False, get_ancestors_bool=False
                      , escape=True):
    related_terms = []
    escaped = []
    if get_synonyms_bool:
        res = get_synonyms(conn_string, concept, vocabulary)
        if res:
            for r in res:
                related_terms.append(r[0])
                escaped.append(re.escape(r[0]))
    if get_descendants_bool:
        res = get_descendants(conn_string, concept, vocabulary)
        if res:
            for r in res:
                related_terms.append(r[0])
                escaped.append(re.escape(r[0]))
    if get_ancestors_bool:
        res = get_ancestors(conn_string, concept, vocabulary)
        if res:
            for r in res:
                related_terms.append(r[0])
                escaped.append(re.escape(r[0]))

    if len(related_terms) > 0:
        log(related_terms)

    if escape:
        return list(set(escaped))
    else:
        return list(set(related_terms))

def get_related_terms_ohdsi(ohdsi_url, concept_id, vocabulary, get_synonyms_bool=True, get_descendants_bool=False, get_ancestors_bool=False, escape=True):
    url = ohdsi_url + '/vocabulary/OHDSI-CDMV5/concept/%s/related' %(concept_id)
    data = requests.get(url).json()

    related_terms = []
    escaped = []

    for i in data:
        if i["VOCABULARY_ID"] == vocabulary:
            if get_descendants_bool:
                for j in i["RELATIONSHIPS"]:
                    if 'descendant' in j["RELATIONSHIP_NAME"]:
                        related_terms.append(i["CONCEPT_NAME"])
                        escaped.append(re.escape(i["CONCEPT_NAME"]))
            elif get_ancestors_bool:
                for j in i["RELATIONSHIPS"]:
                    if 'ancestor' in j["RELATIONSHIP_NAME"]:
                        related_terms.append(i["CONCEPT_NAME"])
                        escaped.append(re.escape(i["CONCEPT_NAME"]))

            # Add case for synonyms

    if escape:
        return list(set(escaped))
    else:
        return list(set(related_terms))

# For testing purposes. Remove in code cleanup.
if __name__=='__main__':
    r = get_related_terms_ohdsi('https://gt-apps.hdap.gatech.edu/ohdsi/WebAPI', 376337, 'SNOMED', False, False, True, False )
    log (r)
