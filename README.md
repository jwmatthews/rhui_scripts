rhui_scripts
============

Scripts to help provision &amp; work with RHUI (Red Hat Update Infrastructure) 

Directories Explained:
---------------------

 * builder

  - setup up an EC2 instance to function as a RHUI Build Environment & Yum repo
  - build RHUI rpms from various git repos

 * provision

  - create 3 new EC2 instances to function as a RHUA & 2 CDS
  - attach an external EBS volume to store rpm content
  - format EBS volume as a LVM
  - adjust hostname of each instance to use external hostname
  - install RHUI RPMs from RHUI Build Environment on RHUA & CDSes

 * configure

  - Assuming ec2 instances already exist, run through setup steps to:

   - Generate X509 certificates
   - Update RHUI Answers file
   - Run through rhui-installer to setup RHUA & CDS environment


Items Planned in near future:

 - Create a vagrant file which will leverage scripts from configure and setup a simple vagrant VM to test RHUA & 1 CDS functionality.



