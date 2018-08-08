FROM postgres

RUN apt-get update && apt-get -y install wget && apt-get -y install zip unzip

COPY ddl/ddl.sql /docker-entrypoint-initdb.d/10-ddl.sql
COPY ddl/omop_vocab.sql /docker-entrypoint-initdb.d/20-omop_vocab.sql
COPY dml/load_vocab.sh /docker-entrypoint-initdb.d/30-load_vocab.sh
COPY dml/copy_vocab.sql /docker-entrypoint-initdb.d/40-copy_vocab.sql
COPY ddl/omop_indexes.sql /docker-entrypoint-initdb.d/50-omop_indexes.sql
COPY ddl/add_nlpql_column.sql /docker-entrypoint-initdb.d/60-add_nlpql_column.sql

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["postgres"]
