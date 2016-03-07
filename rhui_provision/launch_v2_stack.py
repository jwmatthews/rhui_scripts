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
import threading
import time
import yaml
from datetime import datetime
from optparse import OptionParser

from boto import cloudformation
from boto import regioninfo
from boto import ec2
from boto.manage.cmdshell import sshclient_from_instance

def read_env(var, default_value=None):
    if os.environ.has_key(var):
        return os.environ[var]
    else:
        return default_value

DEFAULT_AWS_ACCESS_KEY_ID=read_env("AWS_ACCESS_KEY_ID")
DEFAULT_AWS_SECRET_ACCESS_KEY=read_env("AWS_SECRET_ACCESS_KEY")
DEFAULT_INSTANCE_TYPE="m1.large"
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
                    parameters=parameters, timeout_in_minutes=timeout,
                    disable_rollback=True)

    is_complete = False
    result = False
    while not is_complete:
        logging.info("Waiting for cloud formation stack to come up....")
        time.sleep(30)
        try:
            for event in con_cf.describe_stack_events(stack_id):
                logging.info("StackEvent: %s %s %s" % (event, event.resource_type, event.resource_status))
                if event.resource_type == "AWS::CloudFormation::Stack" and event.resource_status == "CREATE_COMPLETE":
                    logging.info("Stack creation completed")
                    is_complete = True
                    result = True
                    #break
                if event.resource_status == "ROLLBACK_COMPLETE" or event.resource_status == "CREATE_FAILED":
                    logging.info("Stack creation failed: %s" % (event))
                    logging.info(event)
                    is_complete = True
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
        "instance_type", "key_name", "launch_time", "tags", "block_device_mapping"]
    details = {}
    for inst in instances:
        info = {}
        for k in keys:
            info[k] = getattr(inst, k)
        info["instance"] = inst
        if not info["tags"].has_key("Role"):
            info["tags"]["Role"] = "Unknown"
        details[info["public_dns_name"]] = info
    return details

def write_bash_env(stack_id, instance_details, out_file):
    data = "STACK_ID=%s\n" % (stack_id)
    for inst in instance_details.values():
        dns_name = inst["public_dns_name"]
        role = inst["tags"]["Role"]
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
        role = inst["tags"]["Role"]
        data[role] = {}
        dns_name = inst["public_dns_name"]
        data[role]["hostname"] = dns_name
    f = open(out_file, "w")
    try:
        f.write(yaml.dump(data, default_flow_style=False))
    finally:
        f.close()

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

def run_cmd(ssh_client, cmd):
    # We need to run with a pty so 'sudo' commands will work.
    output = ""
    logging.info("Running: '%s' on '%s'" % (cmd, ssh_client.server.hostname))
    channel = ssh_client.run_pty(cmd)
    while True:
        if channel.recv_ready():
            output += channel.recv(65536)
        if channel.exit_status_ready():
            exit_code = channel.recv_exit_status()
            channel.close()
            break
    logging.info("Completed: '%s' on '%s'\nExit Code: %s\nOutput: %s" % (cmd, ssh_client.server.hostname, exit_code, output))
    if exit_code:
        raise Exception("Failed to run: '%s'\nExit Code of: %s" % (cmd, exit_code))

def _create_log_part(ssh_client, blockdevice, vgname, lvname, mountpoint):
    # Creating the log partition requires that we:
    # - Mount new partition to a temp location
    # - Move existing log files over
    # - Remount new partition to desired location
    cmd = "sudo pvcreate %s" % (blockdevice)
    run_cmd(ssh_client, cmd)

    cmd = "sudo vgcreate %s %s" % (vgname, blockdevice)
    run_cmd(ssh_client, cmd)

    cmd = "sudo lvcreate -l 100%%FREE -n %s %s" % (lvname, vgname)
    run_cmd(ssh_client, cmd)

    cmd = "sudo /sbin/mkfs.ext3 -q /dev/%s/%s" % (vgname, lvname)
    run_cmd(ssh_client, cmd)

    cmd = "sudo mkdir /var/log.new"
    run_cmd(ssh_client, cmd)

    cmd = "sudo mount /dev/%s/%s /var/log.new" % (vgname, lvname)
    run_cmd(ssh_client, cmd)

    cmd = "sudo mv /var/log/* /var/log.new/"
    run_cmd(ssh_client, cmd)

    cmd = "sudo mv /var/log /var/log.old"
    run_cmd(ssh_client, cmd)

    cmd = "sudo umount /var/log.new"
    run_cmd(ssh_client, cmd)

    cmd = "sudo mv /var/log.new /var/log"
    run_cmd(ssh_client, cmd)

    cmd = "echo '/dev/%s/%s %s ext3 defaults 0 0' | sudo tee -a /etc/fstab" % (vgname, lvname, mountpoint)
    run_cmd(ssh_client, cmd)

    cmd = "sudo mount %s" % (mountpoint)
    run_cmd(ssh_client, cmd)

    # 'service httpd restart' was failing with: 
    #  Starting httpd: (13)Permission denied: httpd: could not open error log file /etc/httpd/logs/error_log.
    #  Unable to open logs
    #
    # Cause was that the new /var/log mountpoint we created defaults to 'file_t'
    # httpd selinux policy is unable to read 'file_t', we need to change to 'var_t'
    #
    cmd = "sudo semanage fcontext -a -t var_t %s" % (mountpoint)
    run_cmd(ssh_client, cmd)

    cmd = "sudo restorecon %s" % (mountpoint)
    run_cmd(ssh_client, cmd)

def _create_part(ssh_client, blockdevice, vgname, lvname, mountpoint):
    cmd = "sudo pvcreate %s" % (blockdevice)
    run_cmd(ssh_client, cmd)

    cmd = "sudo vgcreate %s %s" % (vgname, blockdevice)
    run_cmd(ssh_client, cmd)

    cmd = "sudo lvcreate -l 100%%FREE -n %s %s" % (lvname, vgname)
    run_cmd(ssh_client, cmd)

    cmd = "sudo /sbin/mkfs.ext3 -q /dev/%s/%s" % (vgname, lvname)
    run_cmd(ssh_client, cmd)

    cmd = "sudo mkdir %s" % (mountpoint)
    run_cmd(ssh_client, cmd)

    # we can't run: sudo echo 'something' >> /etc/fstab.txt
    # so we are using 'tee' in place of echo
    cmd = "echo '/dev/%s/%s %s ext3 defaults 0 0' | sudo tee -a /etc/fstab" % (vgname, lvname, mountpoint)
    run_cmd(ssh_client, cmd)

    cmd = "sudo mount %s" % (mountpoint)
    run_cmd(ssh_client, cmd)

def setup_filesystem_on_host(instance_details, ssh_user, ssh_priv_key_path):
    dns_name = instance_details["public_dns_name"]
    role = instance_details["tags"]["Role"]
    logging.info("Setting up LVM filesystems on '%s' which is a '%s'" % (dns_name, role))

    ssh_client = sshclient_from_instance(instance_details["instance"], 
        ssh_key_file=ssh_priv_key_path, user_name=ssh_user)
    pulp_mountpoint = "/var/lib/pulp"        
    if role.upper().startswith("CDS"):
        pulp_mountpoint = "/var/lib/pulp-cds"

    # Expected partitions
    # /dev/xvdm for /var/log
    # /dev/xvdn for /var/lib/mongodb 
    # /dev/xvdp for /var/lib/pulp or /var/lib/pulp-cds
    logging.info("Setting up /var/log on '%s'" % (dns_name))
    _create_log_part(ssh_client, blockdevice="/dev/xvdm", 
        vgname="vg0", lvname="var_log", mountpoint="/var/log")
    logging.info("Setting up /var/lib/mongodb on '%s'" % (dns_name))
    _create_part(ssh_client, blockdevice="/dev/xvdn", 
        vgname="vg1", lvname="var_mongodb", mountpoint="/var/lib/mongodb")
    logging.info("Setting up %s on '%s'" % (pulp_mountpoint, dns_name))
    _create_part(ssh_client, blockdevice="/dev/xvdp", 
        vgname="vg2", lvname="var_pulp", mountpoint=pulp_mountpoint)

def setup_filesystems(inst_details, ssh_user, ssh_priv_key_path):
    # Will create a thread per instance so filesystem setup may happen in parallel
    # Steps are executed in parallel to minimize the impact of 
    #  mkfs commands which take several minutes per filesystem
    #
    # TODO:  Add ability to capture errors from a thread and quit execution of entire script.
    #
    start = time.time()
    threads = []
    for inst in inst_details.values():
        t = threading.Thread(target=setup_filesystem_on_host, args=(inst, ssh_user, ssh_priv_key_path))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    end = time.time()
    logging.info("\nLVM filesystems were created on %s hosts in %s seconds" % (len(inst_details), end-start))

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

    con_ec2, con_cf = get_connections(region_name=region_name, 
        aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    # Launch EC-2 resources
    cloud_form_json_body = read_file(cloudformfile)
    stack_id = get_stack_id()
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
    write_ansible_inventory(details, ans_out_file)
    #write_yaml_conf(stack_id, details, yaml_out_file)
    write_bash_env(stack_id, details, bash_out_file)

    logging.info("Will wait for SSH to come up for below instances:")
    for inst_details in details.values():
        keys = ["public_dns_name", "launch_time", "key_name", "ip_address", "instance_type"]
        for k in keys:
            logging.info("\t%s: %s" % (k, inst_details[k]))
        logging.info("\n")
    if not wait_for_ssh(hostnames, ssh_user, ssh_priv_key_path):
        logging.error("\n***Stack is not complete, problem with SSH on an instance.***\n")
        sys.exit(1)

    setup_filesystems(details, ssh_user, ssh_priv_key_path)

    logging.info("StackID: %s" % (stack_id))
    end = time.time()
    for instance_details in details.values():
        dns_name = instance_details["public_dns_name"]
        role = instance_details["tags"]["Role"]
        print "%s = %s" % (role, dns_name)
    logging.info("Completed creation of Cloud Formation Stack from: %s in %s seconds" % (cloudformfile, (end-start)))
    logging.info("Ansible inventory file written to: %s" % (ans_out_file))
    logging.info("Bash hostnames.env file written to: %s" % (bash_out_file))

