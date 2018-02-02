"""
Vocabulary Expansion

- synonyms
- ancestors
- descendants
"""

# Function to get synonyms for given concept
def get_synonyms(conn_string, concept):
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    #TODO: Queries
# Port queries present at https://github.gatech.edu/HDAP/omop-query/blob/master/src/main/scala/gtri/nlp/omop_query/Queries.scala

# Function to get ancestors for given concept
def get_ancestors(conn_string, concept):
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    #TODO: Queries

# Function to get descendants for given concept
def get_descendants(conn_string, concept):
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    #TODO: Queries
