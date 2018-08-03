FROM solr:6.6.4

COPY precreate-core /opt/docker-solr/scripts/precreate-core
COPY solrconfig.xml /solrconfig.xml
COPY sample.csv /sample.csv

ENTRYPOINT ["docker-entrypoint.sh", "solr-precreate", "sample"]
