#! /usr/bin/python -tt
##
# Reusing a lot of code from:
#  https://github.com/RedHatQE/rhui-testing-tools/blob/master/scripts/create-cf-stack.py
##
##
# Note:
# The supplied cloud formation JSON file needs
# a tag of "Role" for each instance provisioned
##
import getpass
import logging
import os
import random
import string
import sys
import time
from optparse import OptionParser

from boto import cloudformation
from boto import regioninfo
from boto import ec2
from boto.manage.cmdshell import sshclient_from_instance

def read_env(var):
    return os.environ[var]


DEFAULT_AWS_ACCESS_KEY_ID=read_env("AWS_ACCESS_KEY_ID")
DEFAULT_AWS_SECRET_ACCESS_KEY=read_env("AWS_SECRET_ACCESS_KEY")
DEFAULT_INSTANCE_TYPE="m1.large"
DEFAULT_SSH_USER="ec2-user"
DEFAULT_SSH_KEY_NAME="splice"
DEFAULT_SSH_PRIV_KEY_PATH=os.path.join(read_env("HOME"), ".ssh/splice_rsa")

def read_file(file_name):
    f = open(file_name, 'r')
    try:
        return f.read()
    finally:
        f.close()
def get_user():
    return getpass.getuser()

def parse_args():
    parser = OptionParser(description='Create CloudFormation stack')
    parser.add_option('--debug', action='store_true', 
        default=False, help='debug mode')
    parser.add_option('--ssh_user',
        default=DEFAULT_SSH_USER, help='Username to use when sshing to remote host, defaults to %s' % (DEFAULT_SSH_USER))
    parser.add_option('--ssh_key_name',
        default=DEFAULT_SSH_KEY_NAME, help='SSH Key name as registered in AWS EC2, defaults to %s' % (DEFAULT_SSH_KEY_NAME))
    parser.add_option('--ssh_priv_key_path',
        default=DEFAULT_SSH_PRIV_KEY_PATH, help='Path to private SSH Key, defaults to %s' % (DEFAULT_SSH_PRIV_KEY_PATH))
    parser.add_option('--aws_access_key_id',
        default=DEFAULT_AWS_ACCESS_KEY_ID, help='AWS Access Key, defaults to reading environment variable AWS_ACCESS_KEY_ID')
    parser.add_option('--aws_secret_access_key',
        default=DEFAULT_AWS_SECRET_ACCESS_KEY, help='AWS Secret Access Key, defaults to reading environment variable AWS_SECRET_ACCESS_KEY')
    parser.add_option('--region',
        default="us-east-1", help='use specified region')
    parser.add_option('--timeout', type=int,
        default=10, help='stack creation timeout')
    parser.add_option('--cloudformfile',
        default=None, help='Path to AWS Cloud Formation configuration file in JSON Format')
    parser.add_option('--skip_wait_ssh', action='store_const', const=False,
        default=True, help='If set will skip waiting for SSH to be available on instances before script returns')
    parser.add_option('--out_file', 
        default="provisioned_instances.ansible", help="Filename to store ansible ec2 inventory information representing provisioned instances")
    parser.add_option('--instance_type',
        default=DEFAULT_INSTANCE_TYPE, help="AWS EC2 Instance type for launched instances, defaults to %s" % (DEFAULT_INSTANCE_TYPE))
    (opts, args) = parser.parse_args()
    return opts

def setup_logging(debug=False):
    if debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def get_connections(region_name, aws_access_key_id, aws_secret_access_key):
    con_ec2 = ec2.connect_to_region(region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)
    if not con_ec2:
        raise Exception("Unable to create ec2 connection to: " + region_name)

    region = regioninfo.RegionInfo(name=region_name,
        endpoint="cloudformation." + region_name + ".amazonaws.com")
    if not region:
        raise Exception("Unable to connect to region: " + region_name)

    con_cf = cloudformation.connection.CloudFormationConnection(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region=region)
    if not con_cf:
        raise exception("Unable to create cloudformation connection to: " + region_name)
    return (con_ec2, con_cf)

def create_cloudformation(con_cf, json_body, parameters, stack_id, timeout):
    """
    Launches a CloudFormation file and returns a list of the associated instances
    """
    logging.info("Creating stack with ID: " + stack_id)
    con_cf.create_stack(stack_id, template_body=json_body,
                    parameters=parameters, timeout_in_minutes=timeout)

    is_complete = False
    result = False
    while not is_complete:
        logging.info("Waiting for cloud formation stack to come up....")
        time.sleep(30)
        try:
            for event in con_cf.describe_stack_events(stack_id):
                if event.resource_type == "AWS::CloudFormation::Stack" and event.resource_status == "CREATE_COMPLETE":
                    logging.info("Stack creation completed")
                    is_complete = True
                    result = True
                    break
                if event.resource_type == "AWS::CloudFormation::Stack" and event.resource_status == "ROLLBACK_COMPLETE":
                    logging.info("Stack creation failed")
                    is_complete = True
                    break
        except Exception, e:
            logging.exception("Creation of Cloud Formation Stack '%s' was unsuccessful" % (stack_id))
            raise
    if not result:
        raise Exception("Cloud Formation stack '%s' did not come up as expected." % (stack_id))

    instance_ids = []
    for res in con_cf.describe_stack_resources(stack_id):
        if res.resource_type == 'AWS::EC2::Instance' and res.physical_resource_id:
            logging.debug("Instance " + res.physical_resource_id + " created")
            instance_ids.append(res.physical_resource_id)
    return instance_ids

def get_instances(con_ec2, instance_ids):
    return con_ec2.get_only_instances(instance_ids)

def get_instance_details(instances):
    keys = ["public_dns_name", "state", "state_code", "ip_address", 
        "instance_type", "key_name", "launch_time", "tags"]
    details = {}
    for inst in instances:
        info = {}
        for k in keys:
            info[k] = getattr(inst, k)
        details[info["public_dns_name"]] = info
    return details

def write_ansible_inventory(instance_details, out_file):
    data = "localhost\n"
    for inst in instance_details.values():
        dns_name = inst["public_dns_name"]
        role = inst["tags"]["Role"]
    #Note:
    # The supplied cloud formation JSON file needs
    # a tag of "Role" for each instance provisioned
    data += "[%s]\n" % (role)
    data += "%s\n" % (dns_name)

    f = open(out_file, "w")
    try:
        f.write(data)
    finally:
        f.close()

def try_port_22(hostname):
    import socket
    status = False
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((hostname, 22))
        status = True
    except socket.error as e:
        status = False
    s.close()
    return status

def wait_for_ssh(hostnames, ssh_user, ssh_priv_key_path, timeout_in_minutes=5):
    # Loop through instances and wait for all to have a SSH service that is acceptable
    for hostname in hostnames:
        success = False
        start = time.time()
        while True:
            if try_port_22(hostname):
                success = True
                break
            elif (time.time()-start)/60.0 > timeout_in_minutes:
                logging.error("SSH did not come up on '%s' within %s minutes" % (hostname, timeout_in_minutes))
                break
            time.sleep(1)
        if not success:
            # Break out of the for loop, an instance didn't respond to SSH
            return False
    return True


if __name__ == "__main__":
    start = time.time()
    opts = parse_args()
    aws_access_key_id = opts.aws_access_key_id
    aws_secret_access_key = opts.aws_secret_access_key
    cloudformfile = opts.cloudformfile
    debug = opts.debug
    instance_type = opts.instance_type
    out_file = opts.out_file
    region_name = opts.region
    ssh_key_name = opts.ssh_key_name
    ssh_priv_key_path = opts.ssh_priv_key_path
    ssh_user = opts.ssh_user
    skip_wait_ssh = opts.skip_wait_ssh
    timeout = opts.timeout
    user_name = get_user()

    setup_logging(debug)

    if not cloudformfile:
        logging.info("Please re-run with --cloudformfile option set")
        sys.exit(1)

    con_ec2, con_cf = get_connections(region_name=region_name, 
        aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    # Launch EC-2 resources
    cloud_form_json_body = read_file(cloudformfile)
    stack_id = "RHUIStack" + ''.join(random.choice(string.ascii_lowercase) for x in range(10))
    parameters = [("KeyName", ssh_key_name), ("OwnerName",user_name), ("InstanceType",instance_type)]
    instance_ids = create_cloudformation(con_cf=con_cf,
        json_body=cloud_form_json_body,
        parameters=parameters,
        stack_id=stack_id,
        timeout=timeout)

    logging.info("Below instance IDs were created from stack: %s" % (stack_id))
    for inst_id in instance_ids:
        logging.info("\t%s" % (inst_id))

    instances = get_instances(con_ec2, instance_ids)
    details = get_instance_details(instances)
    hostnames = [x["public_dns_name"] for x in details.values()]
    write_ansible_inventory(details, out_file)

    logging.info("Will wait for SSH to come up for below instances:")
    for inst_details in details.values():
        keys = ["public_dns_name", "launch_time", "key_name", "ip_address", "instance_type"]
        for k in keys:
            logging.info("\t%s: %s" % (k, inst_details[k]))
        logging.info("\n")
    if not wait_for_ssh(hostnames, ssh_user, ssh_priv_key_path):
        logging.error("\n***Stack is not complete, problem with SSH on an instance.***\n")

    logging.info("StackID: %s" % (stack_id))
    end = time.time()
    logging.info("Completed creation of Cloud Formation Stack from: %s in %s seconds" % (cloudformfile, (end-start)))

