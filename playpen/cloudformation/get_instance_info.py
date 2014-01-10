#!/usr/bin/env python

from boto import ec2
import os

def read_env(var):
    return os.environ[var]

DEFAULT_AWS_ACCESS_KEY_ID=read_env("AWS_ACCESS_KEY_ID")
DEFAULT_AWS_SECRET_ACCESS_KEY=read_env("AWS_SECRET_ACCESS_KEY")
DEFAULT_REGION_NAME="us-east-1"

con_ec2 = ec2.connect_to_region(DEFAULT_REGION_NAME,
    aws_access_key_id=DEFAULT_AWS_ACCESS_KEY_ID,
    aws_secret_access_key=DEFAULT_AWS_SECRET_ACCESS_KEY)

instances = con_ec2.get_only_instances()
for i in instances:
    print "Instance Info is: \n%s" % (i)
    print "Instance Type: %s" % (i.instance_type)
    print "Public DNS Name: %s" % (i.public_dns_name)
    print "State: %s, State Code: %s" % (i.state, i.state_code)
    print "Key_name: %s" % (i.key_name)
    print "Launch Time: %s" % (i.launch_time)
    print "IP Address: %s" % (i.ip_address)
    print "Tags:\n"
    keys = ["Role", "Name", "aws:cloudformation:stack-name", "aws:cloudformation:stack-id"]
    for k in keys:
        if i.tags.has_key(k):
            print "\t%s = %s" % (k, i.tags[k])
    print "\n"

