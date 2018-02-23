"""
Vocabulary Expansion

- synonyms
- ancestors
- descendants
"""

import re
import configparser
import psycopg2
import psycopg2.extras




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

    except Exception as ex:
        print('Failed to get synonyms')
        print(str(ex))

    finally:
        conn.close()

    return result



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

    except Exception as ex:
        print('Failed to get ancestors')
        print(str(ex))

    finally:
        conn.close()

    return result

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

    except Exception as ex:
        print('Failed to get descendants')
        print(str(ex))

    finally:
        conn.close()

    return result


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

    print(related_terms)

    if escape:
        return list(set(escaped))
    else:
        return list(set(related_terms))
