#!/bin/bash

set -e

if [ "$INIT_OMOP" = true ] ; then

>&2 echo "Downloading OMOP Vocabs"

TMPFILE=`mktemp`
PWD=`pwd`
wget "http://healthnlp.gtri.gatech.edu/clarity-files/omop_vocabulary_set.zip" -O $TMPFILE
unzip -d "/tmp/vocabs" $TMPFILE
rm $TMPFILE

>&2 echo "Finished unpacking OMOP Vocabs"

fi
