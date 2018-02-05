"""
Vocabulary Expansion

- synonyms
- ancestors
- descendants
"""


import configparser
import psycopg2
import psycopg2.extras


vocabulary = "SNOMED"

# Function to get synonyms for given concept
def get_synonyms(conn_string, concept):
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    try:
        cursor.execute(""" SELECT concept_synonym_name
        FROM nlp.concept_synonym s INNER JOIN nlp.concept c on c.concept_id = s.concept_id
        WHERE concept_name = %s and c.vocabulary_id=%s and invalid_reason is null
        order by concept_synonym_name
        """, (concept, vocabulary))

        result = cursor.fetchall()

    except Exception as ex:
        print('Failed to get synonyms')
        print(str(ex))

    finally:
        conn.close()

    return result



# Function to get ancestors for given concept
def get_ancestors(conn_string, concept):
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    try:
        cursor.execute(""" SELECT concept_name
        FROM nlp.concept_ancestor INNER JOIN nlp.concept on concept_id = ancestor_concept_id
        WHERE descendant_concept_id in (SELECT concept_id from nlp.concept where concept_name = %s
        AND vocabulary_id=%s AND invalid_reason IS null) AND vocabulary_id=%s AND invalid_reason is null
        order by max_levels_of_separation asc
        """, (concept, vocabulary, vocabulary))

        result = cursor.fetchall()

    except Exception as ex:
        print('Failed to get ancestors')
        print(str(ex))

    finally:
        conn.close()

    return result

# Function to get descendants for given concept
def get_descendants(conn_string, concept):
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    #TODO: Write query
