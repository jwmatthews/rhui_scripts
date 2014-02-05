Provisioning Scripts
====================

Goals:
 
 * Setup a Development Environment using git checkout of code 

  - Consists of 1 RHUA, 2 CDS, and 1 client configured to receive updates
  - Configure a small custom repo to test with
  - Deploy to EC2 or local VMs with Vagrant

Overview:

 * Steps have been broken out into 3 steps:

  1. create_instances.sh - Creates ec2 instances with EBS volumes
  2. install_software.sh - Installs RPMs from our RHUI Developer YUM Repository
  3. setup_rhui.sh - Generates X509 certs, runs rhui-installer, and installs config rpms on instances

Assumptions (to address later): 

  - SSH key hard coded to 'splice'
  - Requires below security groups have already been configured
    - rhui_dev_cds (allow: 22, 80, 443, 5674)
    - rhui_dev_rha (allow: 22, 80, 443, 5674)

Instructions: 

 1. Download an entitlement certificate from access.redhat.com and save at "../install/ent_cert.pem"  
 2. Set up your EC-2 environment variables

    * AWS_ACCESS_KEY_ID
    * AWS_SECRET_ACCESS_KEY
    * Note:  Markdown misinterprets above "_" to make the items italic.

 3. Copy the splice SSH key to: ~/.ssh/splice_rsa
 4. To setup new instances run:
  
  1. ./create_instances.sh - Wait ~10 minutes
  2. ./install_software.sh - Wait ~10 minutes
  3. ./setup_rhui.sh - Wait ~5 minutes

Details:

 * These scripts will interact with 2 environment files. 
  
   * An ansible host file is created in our parent directory as: ../rhui_hosts 
   
     * This, "../rhui_hosts" file contains info ansible needs to know which instance is a RHUA or CDS
  
  * A file with bash environment variables is also created in our parent directory as: ../hostnames.env

     * This, "../hostnames.env", is sourced by our bash scripts so they can distinguish what instance is RHUA, CDS01, or CDS02
