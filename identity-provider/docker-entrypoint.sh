#!/usr/bin/env bash

FILE=/app/creds/idp.pfx

if [ "$ASPNETCORE_ENVIRONMENT" = "Production" ] && ! [ -f "$FILE" ]; then
  echo "$FILE not detected, creating signing material."

  mkdir /app/creds

  openssl \
      req \
      -newkey rsa:2048 \
      -nodes \
      -keyout /app/creds/idp.key \
      -x509 \
      -days 365 \
      -out /app/creds/idp.cer \
      -subj "/C=GB/ST=London/L=London/O=Security/OU=Department/CN=foo.com"

  openssl \
      pkcs12 \
      -export \
      -in /app/creds/idp.cer \
      -inkey /app/creds/idp.key \
      -out /app/creds/idp.pfx \
      -passout pass:$IDP_SIGNING_CREDS_PASSPHRASE
fi

exec "$@"
