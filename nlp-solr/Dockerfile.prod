FROM solr:7.3.0

COPY precreate-core /opt/docker-solr/scripts/precreate-core
COPY sample.csv /sample.csv

ENTRYPOINT ["docker-entrypoint.sh"]
