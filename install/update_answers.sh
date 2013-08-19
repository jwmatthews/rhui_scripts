#!/bin/bash
source ./hostnames
source ./vars

cp ${ANSWERS_TEMPLATE} ${ANSWERS}

function update_answer {
 TERM=$1
 VALUE=$2
 # We need to ensure we escape any paths like "./certs/value.crt"
 # The extra '/' mess up sed
 ESCAPED_VALUE=`echo ${VALUE} | awk '{ gsub("/", "\\\/"); print $0}'`
 echo "Updating $TERM to $ESCAPED_VALUE in $ANSWERS"
 sed -i "s/${TERM}/${ESCAPED_VALUE}/" ${ANSWERS}
}

update_answer RHUA_HOSTNAME ${RHUA}
update_answer RHUA_SSL_CERT ${SSL_CERT_RHUA}
update_answer RHUA_SSL_KEY ${SSL_KEY_RHUA}

update_answer CA_CERT ${CA_CERT}

update_answer CDS_01_HOSTNAME ${CDS_01}
update_answer CDS_01_SSL_CERT ${SSL_CERT_CDS_01}
update_answer CDS_01_SSL_KEY ${SSL_KEY_CDS_01}

update_answer CDS_02_HOSTNAME ${CDS_02}
update_answer CDS_02_SSL_CERT ${SSL_CERT_CDS_02}
update_answer CDS_02_SSL_KEY ${SSL_KEY_CDS_02}

