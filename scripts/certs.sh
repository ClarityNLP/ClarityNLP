#!/bin/bash


# #############################################################################
# Settings
#
certificatePrefix="claritynlp.dev"

BLUE="\033[00;94m"
GREEN="\033[00;92m"
RED="\033[00;31m"
RESTORE="\033[0m"
YELLOW="\033[00;93m"
ROOT_DIR=$(pwd)


# #############################################################################
# Setup Nginx proxy.
#

mkdir -p certs

echo -e "${GREEN}"
echo -e "++++++++++++++++++++++++++++++++++++++++++++++++"
echo -e "+ Setting up nginx proxy                            "
echo -e "++++++++++++++++++++++++++++++++++++++++++++++++"
echo -e "${RESTORE}"


# remove existing certificates
echo -e "${YELLOW} Removing existings certificates... ${RESTORE}"
sudo security delete-certificate -c $certificatePrefix /Library/Keychains/System.keychain

# generate key
openssl \
    genrsa \
    -out certs/$certificatePrefix.key \
    1024

# generate csr request
openssl \
    req \
    -new \
    -sha256 \
    -out certs/$certificatePrefix.csr \
    -key certs/$certificatePrefix.key \
    -config openssl-san.conf

#generate certificate from csr request
openssl \
    x509 \
    -req \
    -days 3650 \
    -in certs/$certificatePrefix.csr \
    -signkey certs/$certificatePrefix.key \
    -out certs/$certificatePrefix.crt \
    -extensions req_ext \
    -extfile openssl-san.conf

# generate pem
cat certs/$certificatePrefix.crt certs/$certificatePrefix.key > certs/$certificatePrefix.pem

# install certificate
if [ -f certs/$certificatePrefix.crt ]; then
    echo -e "${YELLOW} Installing certificate... ${RESTORE}"
    sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain certs/$certificatePrefix.crt
else
    echo -e "${RED} An error occurred while generating the certificate: certs/$certificatePrefix.crt ${RESTORE}"
fi
