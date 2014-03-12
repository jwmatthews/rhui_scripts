#! /usr/bin/python

from optparse import OptionParser
from paramiko import SSHClient

import logging
import os
import paramiko
import subprocess
import sys

LOG_FILENAME='cds.log'

def generate_options():
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="repo_input",
                      help="Input repo file")
    (opt, args) = parser.parse_args()
    return (opt, args)

def check_required_fields(opts, args):
    if opts.repo_input is None:
        print "--input field cannot be blank, exiting..."
        sys.exit(1)

if __name__=="__main__":
    logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)

    opts, args = generate_options()
    check_required_fields(opts, args)

    client_user = "root"
    client_hostname = "cds_client_01"
    source_root = "/var/lib/pulp/published/yum/https/repos"
    dest_root = "/var/lib/pulp/published/yum/https/repos"
    ssh_key = "/root/.ssh/test_client"

    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=client_hostname, username=client_user, key_filename=ssh_key)

    fh = open(opts.repo_input, "r")
    logging.info("Rsync beginning on file: %s" % opts.repo_input)
    for rel_path in fh:
        source_path = '%s/%s' % (source_root, rel_path.strip())
        if os.path.exists(source_path):
            logging.info('Working on %s' % rel_path)
            # create parent folder if it doesn't exist on remote side
            remote_path = "%s/%s/../" % (dest_root, rel_path.strip())
            logging.info("Creating %s on client: %s" % (remote_path, client_hostname))
            stdin, stdout, stderr = ssh.exec_command("mkdir -p %s" % remote_path)
            logging.info(stdout)

            # rsync content
            if os.path.exists("%s/%s" % (source_path, "Packages")) and os.path.islink("%s/%s" % (source_path, "Packages")):
                logging.info("Found recursive Packages folder, ignoring...")
                cmd = ['rsync', '-r', '-L', '-v', '-z', '--exclude', 'Packages', source_path, "%s@%s:%s" % (client_user, client_hostname, remote_path)]
                with open(LOG_FILENAME, 'w') as out, open(LOG_FILENAME, 'w') as err: 
                    rsync_proc = subprocess.Popen(cmd, stdout=out, stderr=err)
                    logging.info("Done with %s. rsync return code is: %s." % (rel_path, rsync_proc.wait())
            else:
                cmd = ['rsync', '-r', '-L', '-v', source_path, "%s@%s:%s" % (client_user, client_hostname, remote_path)]
                with open(LOG_FILENAME, 'w') as out, open(LOG_FILENAME, 'w') as err: 
                    rsync_proc = subprocess.Popen(cmd, stdout=out, stderr=err)
                    logging.info("Done with %s. rsync return code is: %s." % (rel_path, rsync_proc.wait())
        else:
            logging.warning('Unable to find source path %s on FS. Skipping...' % (source_path))
    fh.close()
