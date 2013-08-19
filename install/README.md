Provisioning Scripts
====================

Goals:
 
 * Setup a Development Environment using git checkout of code 

  - Consists of 1 RHUA, 2 CDS, and 1 client configured to receive updates
  - Configure a small custom repo to test with
  - Deploy to EC2 or local VMs with Vagrant

Technologies Used:
 
 - Ansible
 - Vagrant

Assumptions (to address later): 

  - SSH key hard coded to 'splice'
  - Security groups have been created a head of time for: 
    - RHUI_CDS
    - RHUI_RHUA

Instructions: 

 1. echo "localhost" > ~/ansible_hosts
 2. export ANSIBLE_HOSTS=~/ansible_hosts
 3. export ANSIBLE_HOST_KEY_CHECKING=False
 4. ansible-playbook rhui_dev_setup.yml -vv --private-key=~/.ssh/splice_rsa

