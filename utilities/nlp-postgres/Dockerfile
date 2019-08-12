FROM postgres:10.6

RUN apt-get update && apt-get -y install wget && apt-get -y install zip unzip

COPY ddl/ddl.sql /docker-entrypoint-initdb.d/10-ddl.sql
COPY ddl/omop_vocab.sh /docker-entrypoint-initdb.d/20-omop_vocab.sh
COPY ddl/omop_vocab.sql /omop_vocab.sql
COPY dml/load_vocab.sh /docker-entrypoint-initdb.d/30-load_vocab.sh
COPY dml/copy_vocab.sh /docker-entrypoint-initdb.d/40-copy_vocab.sh
COPY dml/copy_vocab.sql /copy_vocab.sql
COPY ddl/omop_indexes.sh /docker-entrypoint-initdb.d/50-omop_indexes.sh
COPY ddl/omop_indexes.sql /omop_indexes.sql
COPY dml/nlpql_library.sql /docker-entrypoint-initdb.d/60-nlpql_library.sql
COPY dml/nlpql_library_sequence.sql /docker-entrypoint-initdb.d/70-nlpql_library_sequence.sql

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["postgres"]
