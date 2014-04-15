#! /usr/bin/python

from optparse import OptionParser

import glob
import os
import subprocess
import sys

RPM_REPO_MAP = {
    'el5': ['rhui-client-config-rhel-server-5-i386-os', 'rhui-client-config-rhel-server-5-x86_64-os'],
    'beta-el5': ['rhui-client-config-beta-rhel-server-5-x86_64-os', 'rhui-client-config-beta-rhel-server-5-i386-os'],
    'beta-vsa2-el5': [],
    'ha-el5': [],
    'jbeap5-el5': [],
    'jbeap6-el5': [],
    'jbews1-el5': [],
    'jbews2-el5': [],
    'mrg-el5': ['rhui-client-config-rhel-server-5-i386-mrg', 'rhui-client-config-rhel-server-5-x86_64-mrg'],
    'rhs-el5': [],
    'rhs21-el5': [],
    'vsa-el5': [],
    'el6': ['rhui-client-config-rhel-server-6-i386-os', 'rhui-client-config-rhel-server-6-x86_64-os'],
    'beta-el6': ['rhui-client-config-beta-rhel-server-6-i386-os', 'rhui-client-config-beta-rhel-server-6-x86_64-os'],
    'beta-vsa2-el6': ['rhui-client-config-rhel-beta-server-6-vsa2'],
    'ha-el6': ['rhui-client-config-server-6-ha'],
    'jbeap5-el6': ['rhui-client-config-rhel-server-6-i386-jbeap-5', 'rhui-client-config-rhel-server-6-x86_64-jbeap-5'],
    'jbeap6-el6': ['rhui-client-config-rhel-server-6-x86_64-jbeap-6', 'rhui-client-config-rhel-server-6-i386-jbeap-6'],
    'jbews1-el6': ['rhui-client-config-rhel-server-6-i386-jbews-1', 'rhui-client-config-rhel-server-6-x86_64-jbews-1'],
    'jbews2-el6': ['rhui-client-config-rhel-server-6-i386-jbews-2', 'rhui-client-config-rhel-server-6-x86_64-jbews-2'],
    'mrg-el6': ['rhui-client-config-rhel-server-6-x86_64-mrg', 'rhui-client-config-rhel-server-6-i386-mrg'],
    'rhs-el6': ['rhui-client-config-server-6-rhs'],
    'rhs21-el6': ['rhui-client-config-server-6-rhs'],
    'vsa-el6': ['rhui-client-config-rhel-server-6-x86_64-vsa'],
}

def generate_options():
    parser = OptionParser()
    parser.add_option("-r", "--rpm_dir", dest="rpm_dir",
                      help="RPM dir where client rpms can be found.")
    parser.add_option("-u", "--username", dest="username", default="admin",
                      help="Pulp username")
    parser.add_option("-p", "--password", dest="password", default="admin",
                      help="Pulp password")
    (opts, args) = parser.parse_args()
    return (opts, args)

def check_required_fields(opts, args):
    if opts.rpm_dir is None:
        print "--rpm_dir field cannot be blank, exiting..."
        sys.exit(1)

def push(rpmdir, username, password):
    os.chdir(rpmdir)
    for rpm in glob.glob("*.rpm"):
        # Determine rhel ver
        pieces = rpm.split(".")
        rhel_ver = ""
        if pieces[-3].startswith('el5'):
            rhel_ver = 'el5'
        elif pieces[-3].startswith('el6'):
            rhel_ver = 'el6'

        # Determine product
        pieces = rpm.split("-")
        prod = pieces[4:-2]

        # Combine product w/ rhel_ver to produce a key to reference RPM_REPO_MAP
        prod.append(rhel_ver)
        key = "-".join(prod)

        try:
            for repo in RPM_REPO_MAP[key]:
                add_content_cmd = ["pulp-admin", "--username", username, "--password", password, "content", "upload", rpm]
                add_content_proc = subprocess.Popen(add_content_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                (stdout, stderr) = add_content_proc.communicate()
                print "%s\n%s" % (stdout, stderr)

                add_pkg_cmd = ["pulp-admin", "--username", username, "--password", password, "repo", "add_package", "--id", repo, "-p", rpm]
                add_pkg_proc = subprocess.Popen(add_pkg_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                (stdout, stderr) = add_pkg_proc.communicate()
                print "%s\n%s" % (stdout, stderr)

                gen_metadata_cmd = ["pulp-admin", "--username", username, "--password", password, "repo", "generate_metadata", "--id", repo]
                gen_metadata_proc = subprocess.Popen(gen_metadata_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                (stdout, stderr) = gen_metadata_proc.communicate()
                print "%s\n%s" % (stdout, stderr)
        except KeyError:
            print "Cannot find key %s in RPM_REPO_MAP, exiting..." % key
            sys.exit(1)
            

def main():
    (opts, args) = generate_options()
    check_required_fields(opts, args)
    push(opts.rpm_dir, opts.username, opts.password)

if __name__ == "__main__":
    main()
