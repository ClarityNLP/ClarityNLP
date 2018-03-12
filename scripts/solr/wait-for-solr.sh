#!/bin/bash
# wait-for-solr.sh

set -e
host="$1"
shift
cmd="$@"

until wget -q -O - "$host" | grep -q -i solr; do
  >&2 echo "Solr is unavailable - sleeping"
  sleep 1
done

>&2 echo "Solr is up - executing command"
exec $cmd
