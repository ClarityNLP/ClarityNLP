FROM solr:6.6.4

COPY precreate-core /opt/docker-solr/scripts/precreate-core
COPY solrconfig.xml /solrconfig.xml
COPY sample.csv /sample.csv
COPY sample2.csv /sample2.csv
COPY sample3.csv /sample3.csv
COPY sample4.csv /sample4.csv

ENTRYPOINT ["docker-entrypoint.sh", "solr-precreate", "sample"]
