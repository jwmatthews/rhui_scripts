#!/usr/bin/env python
import grp
import os
import pwd
import sys

def fix_link(symlink, checksum, bad_target, user="apache", group="apache"):
    filename = os.path.basename(bad_target)
    temp_dir = os.path.dirname(bad_target)
    temp_dir = os.path.dirname(temp_dir)
    good_target = os.path.join(temp_dir, checksum, filename)
    if os.path.lexists(symlink):
        if not os.path.islink(symlink):
            print "ERROR:  %s is not a symlink, skipping" % (symlink)
            return
        os.unlink(symlink)

    os.symlink(good_target, symlink)
    uid = pwd.getpwnam(user).pw_uid
    gid = grp.getgrnam(group).gr_gid
    os.lchown(symlink, uid, gid)
    print "Updated '%s' to point to '%s'" % (symlink, good_target)

def get_params(entry):
    """
    Sample CSV data
    
     Header:
      path, error, expected, found, checksum_type, symlink_source
    
     Example line:
      /var/lib/pulp-cds/repos/content/dist/rhel/rhui/server/6/6Server/x86_64/source/SRPMS/libmlx4-1.0.5-4.el6.1.src.rpm, checksum_mismatch, c18cee136cf2908c91c823a5bf8b71ca85d82f1b, d870b748ec83f26d7e6a52b7e1cd2c7a8c5ba01e, sha, ../../../../../../../../../../../packages/libmlx4/1.0.5/4.el6.1/src/d870b748ec83f26d7e6a52b7e1cd2c7a8c5ba01e/libmlx4-1.0.5-4.el6.1.src.rpm
    """
    entries = entry.split(",")
    error_type = entries[1].strip()
    if error_type.strip() != "checksum_mismatch":
        print "\nUnexpected error type from CSV line:  '%s'" % (error_type)
        (None, None, None)
    symlink = entries[0].strip()
    expected_checksum = entries[2].strip()
    bad_target = entries[5].strip()
    return (symlink, expected_checksum, bad_target)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Please re-run with a .csv file"
        sys.exit()
    csv_file = sys.argv[1]
    print "Reading: %s" % (csv_file)
    csv_file = open(csv_file, "r")
    lines = csv_file.readlines()
    # Skip first line which is header
    for line in lines[1:]:
        symlink, expected_checksum, bad_target = get_params(line)
        if (not symlink) or (not expected_checksum) or (not bad_target):
            print "Skipping <%s>" % (line)
            continue
        fix_link(symlink, expected_checksum, bad_target)

