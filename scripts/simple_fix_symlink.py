#!/usr/bin/env python
import os
import subprocess
import sys

PULP_DIR="pulp-cds"
REPO_DIR="/var/lib/%s/repos/content/dist/rhel/rhui/server/6/6Server/x86_64/os/Packages" % (PULP_DIR)
PACKAGE_DIR="/var/lib/%s/packages" % (PULP_DIR)

FILES= {
        'rhn-client-tools-1.0.0.1-16.el6.noarch.rpm': "%s/rhn-client-tools/1.0.0.1/16.el6/noarch/0750e587e483447615ce6c6e61aa2b3308c23a56" % (PACKAGE_DIR),
        'rhn-setup-1.0.0.1-16.el6.noarch.rpm' : "%s/rhn-setup/1.0.0.1/16.el6/noarch/eab1a4c437949dff14f7fe18c8121a7f0ec4c7ac" % (PACKAGE_DIR),
        'ql2500-firmware-7.00.01-1.el6.noarch.rpm' : "%s/ql2500-firmware/7.00.01/1.el6/noarch/a3e90c76ba95c58e0981cb4f95bcfa214b2c9930" % (PACKAGE_DIR),
        'sos-2.2-47.el6.noarch.rpm' : "%s/sos/2.2/47.el6/noarch/180409493d86e42e32a403478f7b5271fe01cc21" % (PACKAGE_DIR),
        'bfa-firmware-3.2.21.1-2.el6.noarch.rpm' : "%s/bfa-firmware/3.2.21.1/2.el6/noarch/17b03ed1d6d01d2b9f872558440c66e59048f339" % (PACKAGE_DIR),
        'ca-certificates-2013.1.94-65.0.el6.noarch.rpm' : "%s/ca-certificates/2013.1.94/65.0.el6/noarch/69e8a3545d9345d4557f387135c300d6c1402bc4" % (PACKAGE_DIR),
        'ql2400-firmware-7.00.01-1.el6.noarch.rpm' : "%s/ql2400-firmware/7.00.01/1.el6/noarch/1b17d40721daaa71ac63240df505b69804806b89" % (PACKAGE_DIR),
        'rhn-check-1.0.0.1-16.el6.noarch.rpm' : "%s/rhn-check/1.0.0.1/16.el6/noarch/cc6c122a9e2e8f2ac798d9d384838493cf8fd818" % (PACKAGE_DIR),
        'rhn-setup-gnome-1.0.0.1-16.el6.noarch.rpm' : "%s/rhn-setup-gnome/1.0.0.1/16.el6/noarch/5faeb5dac57d11874bdca6adc5785af0e9dee835" % (PACKAGE_DIR),
    }


def run_command(cmd):
    print "Executing: %s" % (cmd)
    handle = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out_msg, err_msg = handle.communicate(None)
    if handle.returncode != 0:
        print "Exiting due to error from: %s" % (cmd)
        print "stdout:\n%s" % (out_msg)
        print "stderr:\n%s" % (err_msg)
        sys.exit(1)
    return out_msg, err_msg

for key, value in FILES.items():
    print "\n\nWill adjust symlink of %s to %s" % (key, value)
    source_file = "%s/%s" % (value, key)
    symlink = "%s/%s" % (REPO_DIR, key)

    if os.path.exists(source_file):
        if os.path.exists(symlink):
            print "Removing older symlink '%s'" % (symlink)
            os.unlink(symlink)
        cmd = "ln -s %s %s" % (source_file, symlink)
        run_command(cmd)
    else:
        print "Unable to find '%s'" % (source_file)
        sys.exit(1)

    cmd = "chown root:apache %s" % (symlink)
    run_command(cmd)
