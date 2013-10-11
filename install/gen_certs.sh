#!/bin/sh

source ./hostnames
source ./vars

echo "Creating CA: ${CA_CERT}"
echo 10 > ${CA_SRL}
openssl genrsa -out ${CA_KEY} 2048
openssl req -new -x509 -days ${DAYS} -key ${CA_KEY} -out ${CA_CERT} -subj "/C=US/ST=NC/L=Raleigh/O=Red Hat/OU=RHUI_Test/CN=Red Hat Cloud Enablement"

echo "Creating SSL cert for RHUA: ${SSL_CERT_RHUA}"
openssl genrsa -out ${SSL_KEY_RHUA} 2048
openssl req -new -key ${SSL_KEY_RHUA} -out ${SSL_CSR_RHUA} -subj "/C=US/ST=NC/L=Raleigh/O=Red Hat/OU=RHUI_Test/CN=${RHUA}"
openssl x509 -req -days ${DAYS} -CA ${CA_CERT} -CAkey ${CA_KEY} -CAserial ${CA_SRL} -in ${SSL_CSR_RHUA} -out ${SSL_CERT_RHUA}

echo "Creating SSL cert for CDS 01: ${SSL_CERT_CDS_01}"
openssl genrsa -out ${SSL_KEY_CDS_01} 2048
openssl req -new -key ${SSL_KEY_CDS_01} -out ${SSL_CSR_CDS_01} -subj "/C=US/ST=NC/L=Raleigh/O=Red Hat/OU=RHUI_Test/CN=${CDS_01}"
openssl x509 -req -days ${DAYS} -CA ${CA_CERT} -CAkey ${CA_KEY} -CAserial ${CA_SRL} -in ${SSL_CSR_CDS_01} -out ${SSL_CERT_CDS_01} 

echo "Creating SSL cert for CDS 02: ${SSL_CERT_CDS_02}" 
openssl genrsa -out ${SSL_KEY_CDS_02} 2048
openssl req -new -key ${SSL_KEY_CDS_02} -out ${SSL_CSR_CDS_02} -subj "/C=US/ST=NC/L=Raleigh/O=Red Hat/OU=RHUI_Test/CN=${CDS_02}"
openssl x509 -req -days 365 -CA ${CA_CERT} -CAkey ${CA_KEY} -in ${SSL_CSR_CDS_02} -CAserial ${CA_SRL} -out ${SSL_CERT_CDS_02} 

echo ""
echo "See: ${CERT_DIR} for your certs"
