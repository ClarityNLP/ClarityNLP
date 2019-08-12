#!/bin/bash

echo "HERE......"
echo $INIT_OMOP

if [ "$INIT_OMOP" = true ] ; then
  PGPASSWORD=$POSTGRES_PASSWORD psql -U $POSTGRES_USER -d $POSTGRES_DB -f /omop_vocab.sql
fi
