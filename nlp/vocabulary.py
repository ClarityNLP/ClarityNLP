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

    #TODO: Write query

# Function to get descendants for given concept
def get_descendants(conn_string, concept):
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    #TODO: Write query
