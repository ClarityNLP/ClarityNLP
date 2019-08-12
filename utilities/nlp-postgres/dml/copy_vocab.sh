#!/bin/bash

if [ "$INIT_OMOP" = true ] ; then
  PGPASSWORD=$POSTGRES_PASSWORD psql -U $POSTGRES_USER -d $POSTGRES_DB -f /copy_vocab.sql
fi
