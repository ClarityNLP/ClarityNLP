#!/bin/bash
set -e

FILE_SOLR=/etc/nginx/htpasswd/$SOLR_SUBDOMAIN.$DOMAIN

# Create solr htpasswd file if does not exist
if ! [ -f "$FILE_SOLR" ]; then
  echo "$FILE_SOLR not detected, creating htpasswd file."
	mkdir -p /etc/nginx/htpasswd
  htpasswd -bc /etc/nginx/htpasswd/$SOLR_SUBDOMAIN.$DOMAIN $SOLR_USERNAME $SOLR_PASSWORD
fi

FILE_SCHEDULER=/etc/nginx/htpasswd/$SCHEDULER_SUBDOMAIN.$DOMAIN

# Create luigi htpasswd file if does not exist
if ! [ -f "$FILE_SCHEDULER" ]; then
  echo "$FILE_SCHEDULER not detected, creating htpasswd file."
	mkdir -p /etc/nginx/htpasswd
  htpasswd -bc /etc/nginx/htpasswd/$SCHEDULER_SUBDOMAIN.$DOMAIN $SCHEDULER_USERNAME $SCHEDULER_PASSWORD
fi

exec "$@"
