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
import paramiko
import string
import sys
import threading
import time
import yaml
from datetime import datetime
from optparse import OptionParser

#from boto import cloudformation
#from boto import regioninfo
#from boto import ec2
#from boto.manage.cmdshell import sshclient_from_instance

import boto3

def read_env(var, default_value=None):
    if os.environ.has_key(var):
        return os.environ[var]
    else:
        return default_value

DEFAULT_AWS_ACCESS_KEY_ID=read_env("AWS_ACCESS_KEY_ID")
DEFAULT_AWS_SECRET_ACCESS_KEY=read_env("AWS_SECRET_ACCESS_KEY")
DEFAULT_INSTANCE_TYPE="m4.2xlarge"
DEFAULT_REGION=read_env("REGION", "us-east-1")
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
    # Required parameter for the input cloud formation template file
    parser.add_option('--template',
        default=None, help='Path to AWS Cloud Formation template file in JSON Format')
    # Optional parameters
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
        default=DEFAULT_REGION, help='use specified region')
    parser.add_option('--timeout', type=int,
        default=120, help='stack creation timeout')
    parser.add_option('--ans_out_file',
        default="provisioned_instances.ansible", help="Filename to store ansible ec2 inventory information representing provisioned instances")
    parser.add_option('--bash_out_file',
        default="hostnames.env", help="Filename to write hostnames that have provisioned and their role.")
    parser.add_option('--yaml_out_file',
        default="provisioned_stack.yaml", help="Filename to write YAML info about provisioned cloud formation stack.")
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

def get_stack_id():
    random_str = ''.join(random.choice(string.ascii_lowercase) for x in range(10))
    date_str = datetime.now().strftime("%Y%m%d")
    stack_id = "%sRHUIStack%s%s" % (get_user(), date_str, random_str)
    return stack_id

def get_connections(region_name, aws_access_key_id, aws_secret_access_key):
    con_ec2 = boto3.client('ec2', region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)
    if not con_ec2:
        raise Exception("Unable to create ec2 connection to: " + region_name)

    region = regioninfo.RegionInfo(name=region_name,
        endpoint="cloudformation." + region_name + ".amazonaws.com")
    if not region:
        raise Exception("Unable to connect to region: " + region_name)

    con_cf = boto3.client('cloudformation', region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)
    if not con_cf:
        raise exception("Unable to create cloudformation connection to: " + region_name)
    return (con_ec2, con_cf)

def create_cloudformation(con_cf, json_body, parameters, stack_id, timeout):
    """
    Launches a CloudFormation file and returns a list of the associated instances
    """
    logging.info("Creating stack with ID: " + stack_id)
    con_cf.create_stack(StackName=stack_id, TemplateBody=json_body,
                    Parameters=parameters, TimeoutInMinutes=timeout,
                    DisableRollback=True)

    is_complete = False
    result = False
    while not is_complete:
        logging.info("Waiting for cloud formation stack to come up....")
        time.sleep(30)
        try:
            for event in con_cf.describe_stack_events(StackName=stack_id)["StackEvents"]:
                logging.info("StackEvent: %s %s %s" % (event, event["ResourceType"], event["ResourceStatus"]))
                if event["ResourceType"] == "AWS::CloudFormation::Stack" and event["ResourceStatus"] == "CREATE_COMPLETE":
                    logging.info("Stack creation completed")
                    is_complete = True
                    result = True
                    #break
                if event["ResourceStatus"] == "ROLLBACK_COMPLETE" or event["ResourceStatus"] == "CREATE_FAILED":
                    logging.info("Stack creation failed: %s" % (event))
                    logging.info(event)
                    is_complete = True
        except Exception, e:
            logging.exception("Creation of Cloud Formation Stack '%s' was unsuccessful" % (stack_id))
            raise
    if not result:
        raise Exception("Cloud Formation stack '%s' did not come up as expected." % (stack_id))

    instance_ids = []
    for res in con_cf.describe_stack_resources(StackName=stack_id)["StackResources"]:
        if res["ResourceType"] == 'AWS::EC2::Instance' and res["PhysicalResourceId"]:
            logging.debug("Instance " + res["PhysicalResourceId"] + " created")
            instance_ids.append(res["PhysicalResourceId"])
    return instance_ids

def get_instances(con_ec2, instance_ids):
    instances = []
    reservations = con_ec2.describe_instances(InstanceIds=instance_ids)["Reservations"]
    for res in reservations:
    	instances += res["Instances"]
    return instances

def get_instance_details(instances):
    #keys = ["PublicIpAddress", "State", "PublicIpAddress",
    keys = ["PublicDnsName", "State", "PublicIpAddress",
        "InstanceType", "KeyName", "LaunchTime", "BlockDeviceMappings"]
    details = {}
    for inst in instances:
        info = {}
        for k in keys:
            info[k] = inst[k]
        info["instance"] = inst
        info["Tags"] = {}
        for tag in inst["Tags"]:
            if tag["Key"] == "Role":
            	info["Tags"]["Role"] = tag["Value"]

        if not info["Tags"].has_key("Role"):
            info["Tags"]["Role"] = "Unknown"
        details[info["PublicDnsName"]] = info
    return details

def write_bash_env(stack_id, instance_details, out_file):
    data = "STACK_ID=%s\n" % (stack_id)
    for inst in instance_details.values():
        dns_name = inst["PublicDnsName"]
        role = inst["Tags"]["Role"]
        data += "%s=%s\n" % (role, dns_name)
    f = open(out_file, "w")
    try:
        f.write(data)
    finally:
        f.close()

def write_yaml_conf(stack_id, instance_details, out_file):
    data = {}
    data["STACK_ID"] = stack_id
    for inst in instance_details.values():
        role = inst["Tags"]["Role"]
        data[role] = {}
        dns_name = inst["PublicDnsName"]
        data[role]["hostname"] = dns_name
    f = open(out_file, "w")
    try:
        f.write(yaml.dump(data, default_flow_style=False))
    finally:
        f.close()

def write_ansible_inventory(instance_details, out_file):
    data = "localhost\n"
    for inst in instance_details.values():
        dns_name = inst["PublicDnsName"]
        role = inst["Tags"]["Role"]
        #Note:
        # The supplied cloud formation JSON file needs
        # a tag of "Role" for each instance provisioned
        data += "[%s]\n" % (role)
        if 'cds' in role.lower():
            data += "%s pulp_mount=/var/lib/pulp-cds\n" % (dns_name)
        else:
            data += "%s pulp_mount=/var/lib/pulp\n" % (dns_name)
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

def wait_for_ssh(hostnames, ssh_user, ssh_priv_key_path, timeout_in_minutes=120):
    # Loop through instances and wait for all to have a SSH service that is acceptable
    for hostname in hostnames:
        logging.info("Waiting for SSH on %s" % (hostname))
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
        logging.info("SSH is up on: %s" % (hostname))
    return True

def wait_for_instance_ready(hostnames, details, timeout_in_minutes=120):
    # Loop through instances and wait till it's in "running" state
    for hostname in hostnames:
        instance = details[hostname]["instance"]
        logging.info("Waiting for ready state on %s" % (instance["PublicDnsName"]))
        success = False
        start = time.time()
        while True:
            if instance["State"]["Name"] == "running":
                success = True
                break
            elif (time.time()-start)/60.0 > timeout_in_minutes:
                logging.error("State did not turn ready '%s' within %s minutes" % (hostname, timeout_in_minutes))
                break
            time.sleep(1)
        if not success:
            # Break out of the for loop, an instance didn't respond to SSH
            return False
        logging.info("%s is ready." % (hostname))
    return True


def run_cmd(ssh_client, cmd):
    # We need to run with a pty so 'sudo' commands will work.
    output = ""
    logging.info("Running: '%s'" % (cmd))
    stdin, stdout, stderr = ssh_client.exec_command(cmd, get_pty=True)
    # this won't work without get_pty, but it lets us skip disk setup.
    # stdin, stdout, stderr = ssh_client.exec_command(cmd)
    exit_code = stdout.channel.recv_exit_status()
    logging.info("Completed: '%s' \nExit Code: %s\nOutput: %s\nStdErr: %s" % (cmd, exit_code, output, stderr.read()))
    if exit_code:
        raise Exception("Failed to run: '%s'\nExit Code of: %s" % (cmd, exit_code))

if __name__ == "__main__":
    start = time.time()
    opts = parse_args()
    ans_out_file = opts.ans_out_file
    aws_access_key_id = opts.aws_access_key_id
    aws_secret_access_key = opts.aws_secret_access_key
    bash_out_file = opts.bash_out_file
    cloudformfile = opts.template
    debug = opts.debug
    instance_type = opts.instance_type
    region_name = opts.region
    ssh_key_name = opts.ssh_key_name
    ssh_priv_key_path = opts.ssh_priv_key_path
    ssh_user = opts.ssh_user
    timeout = opts.timeout
    yaml_out_file = opts.yaml_out_file
    user_name = get_user()

    setup_logging(debug)

    if not cloudformfile:
        logging.info("Please re-run with --template argument set")
        sys.exit(1)

    con_ec2 = boto3.client('ec2', region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    con_cf = boto3.client('cloudformation', region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    # Launch EC-2 resources
    cloud_form_json_body = read_file(cloudformfile)
    stack_id = get_stack_id()
    parameters = [{"ParameterKey": "KeyName", "ParameterValue": ssh_key_name},
                  {"ParameterKey": "OwnerName", "ParameterValue": user_name},
                  {"ParameterKey": "InstanceType", "ParameterValue": instance_type}]
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
    hostnames = [x["PublicDnsName"] for x in details.values()]
    write_ansible_inventory(details, ans_out_file)
    #write_yaml_conf(stack_id, details, yaml_out_file)
    write_bash_env(stack_id, details, bash_out_file)

    logging.info("Will wait for SSH to come up for below instances:")
    for inst_details in details.values():
        keys = ["PublicDnsName", "LaunchTime", "KeyName", "PublicIpAddress", "InstanceType"]
        #keys = ["PublicIpAddress", "LaunchTime", "KeyName", "PublicIpAddress", "InstanceType"]
        for k in keys:
            logging.info("\t%s: %s" % (k, inst_details[k]))
        logging.info("\n")
    if not wait_for_ssh(hostnames, ssh_user, ssh_priv_key_path):
        logging.error("\n***Stack is not complete, problem with SSH on an instance.***\n")
        sys.exit(1)
    if not wait_for_instance_ready(hostnames, details):
        logging.error("\n***Stack is not complete, problem with instance turning to ready state.***\n")
        sys.exit(1)

    logging.info("StackID: %s" % (stack_id))
    end = time.time()
    for instance_details in details.values():
        dns_name = instance_details["PublicDnsName"]
        role = instance_details["Tags"]["Role"]
        print "%s = %s" % (role, dns_name)
    logging.info("Completed creation of Cloud Formation Stack from: %s in %s seconds" % (cloudformfile, (end-start)))
    logging.info("Ansible inventory file written to: %s" % (ans_out_file))
    logging.info("Bash hostnames.env file written to: %s" % (bash_out_file))
