Install Scripts
====================

Goals:
 
 * These scripts will help to generate the X509 certificates needed by RHUI, along with a populated answers file.


Pre-Requisite Instructions: 
---------------------------

 * You need to have an "entitlement certificate" to proceed with setting up a RHUI.  Below instructions will show how to download an entitlement certificate from Red Hat.

 1. Log into https://access.redhat.com
 2. Click on 'Subscriptions'
 3. Click on 'Subscription Management'
 4. Click on 'RHUI'
 5. Click 'Register a RHUI'
 6. Enter a Name
 7. Click 'Register'
 8. Attach a Subscription
 9. Under the 'Entitlement Certificate' click 'Download'
 10. Rename the downloaded 'entitlement certificate' to "entitlement_cert.pem"


Download Latest RHUI 2.x ISO:
-----------------------------

  * Assumes you now have a valid entitlement certificate with the file name: "entitlement_cert.pem"

  1. Download a RHUI ISO, run: ./fetch_iso.sh



Create X509 certificates for RHUI install:
-----------------------------------------

 * This step will generate a

  - Self signed CA certificate/key
  - HTTPS certificates with the CN matching the external hostname for each RHUA & CDS

 * Steps to run:

  1. Update the file: 'hostnames' to match the RHUA/CDS1/CDS2 external dns names you will use
  2. Run: ./gen_certs.sh
  3. See /tmp/rhui_certs for the generated certs


Generate an answers file:
------------------------

 1. ./update_answers.sh
 2. Use the 'rhui.answers' file on your setup
