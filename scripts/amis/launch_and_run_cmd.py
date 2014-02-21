#!/usr/bin/env python
import getpass
import json
import os
import stat
import subprocess
import sys
import time
import yaml
from optparse import OptionParser

try:
    import boto
    from boto.ec2.connection import EC2Connection
    from boto.ec2.blockdevicemapping import BlockDeviceMapping, BlockDeviceType
except Exception, e:
    print "Caught exception: %s" % (e)
    print "Unable to import 'boto' modules."
    print "Try:  sudo yum install python-boto"
    sys.exit(1)

INSTANCE_TYPE = {
    'i386_m1.small_only' : 'm1.small', 
    'x86_64_hvm_m3.xlarge_only' : 'm3.xlarge', 
    'x86_64_c1.xlarge_only' : 'c1.xlarge'
    }

def get_opt_parser(parser=None, description=None):
    if not parser:
        parser = OptionParser(description=description)
    parser.add_option('--ssh_user', action='store', default="ec2-user", 
            help="SSH username, defaults to 'ec2-user'")
    parser.add_option('--ssh_key', action='store', default=None, 
            help="Path to ssh key, defaults to: None")
    parser.add_option('--key_name', action='store', default="splice", 
            help="Path to ssh key, defaults to: 'splice'")
    parser.add_option('--region', action='store', default="us-east-1", 
            help="Region, defaults to: 'us-east-1'")
    parser.add_option('--zone', action='store', default="us-east-1a", 
            help="Zone, defaults to: 'us-east-1a'")
    parser.add_option('--secgroup', action='store', default="default", 
            help="Security Group, defaults to: 'default'")
    parser.add_option('--config', action='store', default=None, 
        help="YAML config file")
    return parser

def parse_config_file(config_file_name):
    f = open(config_file_name, "r")
    try:
        return yaml.safe_load(f)
    finally:
        f.close()

def launch_amis(cfg, ssh_user, ssh_key, key_name, region, zone, secgroup):
    instances = []
    for x in cfg:
        instance_type = INSTANCE_TYPE[x["arch"]]
        ami_id = x["ami"]
        instance = launch_instance(ami_id, instance_type, ssh_user, ssh_key, key_name, region, zone, secgroup)
        instance.ami_id = ami_id
        instances.append(instance)
    return instances

def launch_instance(ami_id, instance_type, ssh_user, ssh_key, key_name, region, zone, sec_group, tag=None):
    print "Launching AMI: '%s' as an instance type of '%s'" % (ami_id, instance_type)
    print "   ssh_user: %s, ssh_key: %s, key_name: %s" % (ssh_user, ssh_key, key_name)
    print "   zone: %s, sec_group: %s" % (zone, sec_group)

    vol_size = "10"
    verify_ssh_key_perms(ssh_key)
    conn = boto.ec2.connect_to_region(region)
    #conn = EC2Connection()
    instance = run_instance(conn, ami_id=ami_id, key_name=key_name,
            instance_type=instance_type, sec_group=sec_group, 
            zone=zone, vol_size=vol_size)
    return instance 

def run_instance(conn, ami_id, key_name, instance_type, 
        sec_group, zone, vol_size=None):
    bdm = None
    if vol_size:
        # Create block device mapping info
        dev_sda1 = BlockDeviceType()
        dev_sda1.size = int(vol_size)
        dev_sda1.delete_on_termination = True
        bdm = BlockDeviceMapping()
        bdm['/dev/sda1'] = dev_sda1

    # Run instance
    reservation = conn.run_instances(
            ami_id,
            key_name=key_name,
            instance_type=instance_type,
            placement=zone,
            instance_initiated_shutdown_behavior="stop",
            security_groups=[sec_group],
            block_device_map=bdm)
    return reservation.instances[0]

def verify_ssh_key_perms(key_path):
    if not os.path.isfile(key_path):
        raise Exception("ssh key '%s' was not found, or is not a usable file." % (key_path))
    mode = oct(os.stat(key_path)[stat.ST_MODE])[-3:]
    if mode != '600':
        raise Exception("ssh key '%s' needs to have permissions '600' yet is set to '%s'. Please fix and retry" % (key_path, mode))

def ssh_command(hostname, ssh_user, ssh_key, command, exit_on_error=True):
    cmd = "ssh -o \"StrictHostKeyChecking no\" -t -i %s %s@%s \"%s\"" % (ssh_key, ssh_user, hostname, command)
    return run_command(cmd, exit_on_error=exit_on_error)

def wait_for_instances_ssh(instances):
    for instance in instances:
        if not wait_for_ssh(instance, ssh_user=ssh_user, ssh_key=ssh_key):
            print "%s %s never came up for SSH access" % (instance.ami_id, instance.dns_name)
            terminate(conn, instance)
            raise Exception("Instance never came up")

def wait_for_ssh(instance, ssh_user, ssh_key, wait=40):
    print "Waiting for instance '%s' to listen for ssh requests" % (instance.dns_name)
    for i in range(1, wait):
        print "Attempt '%s' waiting for ssh to come up on %s" % (i, instance.dns_name)
        status, out, err = ssh_command(instance.dns_name, ssh_user, ssh_key, "ls", exit_on_error=False)
        if status:
            print "%s %s is up\n" % (instance.ami_id, instance.dns_name)
            return True
        time.sleep(15)
    print "\n***"
    print "%s %s SSH never came up" % (instance.ami_id, instance.dns_name)
    print "***\n"
    return False

def tag_instances(instances):
    updated_instances = []
    for instance in instances:
        tag = "%s" % (getpass.getuser())
        instance.add_tag("Name","%s" % (tag))
        instance.update()
        updated_instances.append(instance)
    return updated_instances

def wait_for_running(instances):
    updated_instances = []
    for count, instance in enumerate(instances):
        print "%s/%s:" % (count, len(instances))
        if not wait_for_running_instance(instance):
            print "***"
            print "WARNING:  Instance <%s> did not enter running state" % (instance.id)
            print "***"
        else:
            instance.update() # Refresh instance state & dns_name now that is running
            updated_instances.append(instance)
    return updated_instances

def wait_for_running_instance(instance, wait=120):
    """
    Sleeps till instance is up
    @param instance: 
    @type instance: boto.ec2.instance.Instance
    """
    print "Waiting for instance '%s' to come up" % (instance.id)
    for i in range(0, wait):
        instance.update()
        if instance.state != "pending":
            break
        if i % 10 == 0:
            print "Waited %s seconds for instance '%s' to come up" % (i, instance.id)
        time.sleep(1)
    if instance.state == "running":
        return True
    return False

def tag_instance(instance, hostname, ssh_user, ssh_key, rpm_name=None, data=None):
    tag = ""
    if instance.__dict__.has_key("tags"):
        all_tags = instance.__dict__["tags"]
        if all_tags.has_key("Name"):
            tag = all_tags["Name"]
    if not tag:
        import getpass
        tag = "%s" % (getpass.getuser())
    if rpm_name:
        status, out, err = ssh_command(hostname, ssh_user, ssh_key, "rpm -q --queryformat \"%{VERSION}\" " + rpm_name)
        tag += " %s %s" % (rpm_name, out)
    if data:
        tag += " %s" % (data.strip())
    instance.add_tag("Name","%s" % (tag))
    return tag

def terminate(conn, instance):
    conn.terminate_instances([instance.id])
    print "Instance %s has been terminated" % (instance.id)

def run_command(cmd, verbose=False, exit_on_error=True, retries=0, delay=10):
    """
    @param cmd: string command to run
    @return tuple (True/False, stdout, stderr) true on sucess, false on failure
    """
    handle = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out_msg, err_msg = handle.communicate(None)
    if verbose:
        print "Ran: '%s'" % (cmd)
        print "stdout:\n%s" % (out_msg)
        print "stderr:\n%s" % (err_msg)
    if handle.returncode != 0:
        if retries > 0:
            print "Will retry %s more times command: %s" % (retries, cmd)
            print "Waiting for delay: %s seconds" % (delay)
            time.sleep(delay)
            return run_command(cmd, verbose, exit_on_error, retries - 1)
        if exit_on_error:
            print "Exiting due to error from: %s" % (cmd)
            print "stdout:\n%s" % (out_msg)
            print "stderr:\n%s" % (err_msg)
            sys.exit(1)
        return False, out_msg, err_msg
    return True, out_msg, err_msg

def scp_to_command(hostname, ssh_user, ssh_key, from_path, to_path, exit_on_error=True):
    cmd ="scp -o \"StrictHostKeyChecking no\" -i %s %s %s@%s:%s" % (ssh_key, from_path, ssh_user, hostname, to_path)
    return run_command(cmd, exit_on_error=exit_on_error)

def ssh_command(hostname, ssh_user, ssh_key, command, exit_on_error=True):
    cmd = "ssh -o \"StrictHostKeyChecking no\" -t -i %s %s@%s \"%s\"" % (ssh_key, ssh_user, hostname, command)
    return run_command(cmd, exit_on_error=exit_on_error)

def execute_on_all(instances, ssh_user, ssh_key, cmd):
    output = {}
    for instance in instances:
        (status, out, err) = ssh_command(instance.dns_name, ssh_user, ssh_key, cmd)
        output[instance.ami_id] = {}
        output[instance.ami_id]["status"] = status
        output[instance.ami_id]["out"] = out
        output[instance.ami_id]["err"] = err
    return output

if __name__ == "__main__":
    parser = get_opt_parser()
    (opts, args) = parser.parse_args()
    config_file = opts.config
    ssh_key = opts.ssh_key
    ssh_user = opts.ssh_user
    key_name = opts.key_name
    region = opts.region
    zone = opts.zone
    secgroup = opts.secgroup
    
    if config_file == None:
        parser.print_usage()
        print "Please re-run with --config set."
        sys.exit(1)

    if ssh_key == None:
        parser.print_usage()
        print "Please re-run with --ssh_key set."
        sys.exit(1)

    cfg = parse_config_file(config_file)
    print "cfg = %s" % (cfg)
    instances = launch_amis(cfg, ssh_user, ssh_key, key_name, region, zone, secgroup)
    print "Instances launched: %s" % (instances)
    instances = tag_instances(instances)
    instances = wait_for_running(instances)
    wait_for_instances_ssh(instances)

    cmd = "rpm -qa | grep amazon"
    output = execute_on_all(instances, ssh_user, ssh_key, cmd)
    print json.dumps(output, sort_keys=True, indent=4)

