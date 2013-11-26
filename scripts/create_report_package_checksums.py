#!/usr/bin/env python
import hashlib
import logging
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from optparse import OptionParser

LOG_LEVEL=logging.INFO
FORMAT = '%(asctime)-15s %(message)s'

logging.basicConfig(format=FORMAT, level=LOG_LEVEL)
LOG = logging.getLogger(__name__)

RHUA_PULP_DIR="/var/lib/pulp"
CDS_PULP_DIR="/var/lib/pulp-cds"

def get_pulp_dir():
    if os.path.exists(RHUA_PULP_DIR):
        return RHUA_PULP_DIR
    elif os.path.exists(CDS_PULP_DIR):
        return CDS_PULP_DIR
    else:
        raise Exception("Unable to determine where pulp is storing shared packages")

def get_opts_parser():
    parser = OptionParser()
    parser.add_option('--dir', action="store", default=None, help="Directory to start looking for repositories, will recurse down path looking for 'repodata' directory.")
    parser.add_option('--full', action="store_true", default=False, help="If set will perform a full checksum verification, beyond just looking at the symlink's path.")
    return parser

def get_primary_xml_path(repo_dir):
    LOG.debug("get_primary_xml_path reading: %s" % (repo_dir))
    repomd_xml = os.path.join(repo_dir, "repodata", "repomd.xml")
    LOG.debug("Reading '%s'" % (repomd_xml))
    tree = ET.parse(repomd_xml)
    namespace = "{http://linux.duke.edu/metadata/repo}"
    # RHEL 6.4 has xml.etree version 1.2.6, 1.3+ is needed for specifying an XPath with an attribute name
    data_tags = tree.findall("{0}data".format(namespace))
    for d in data_tags:
        if d.get('type') == 'primary':
            location = d.find("{0}location".format(namespace))
            LOG.debug("Found primary xml at '%s'" %(location.get('href')))
            return os.path.join(repo_dir, location.get('href'))

def read_compressed_file(path):
    f = None
    try:
        if path.endswith(".gz"):
            import gzip
            f = gzip.open(path, 'rb')
        elif path.endswith("bz2"):
            import bz2
            f = bz2.BZ2File(path, 'rb')
        else:
            raise Exception("Unexpected extension from: '%s'" % (path))
        return f.read()
    finally:
        if f:
            f.close()

def parse_primary_data(repo_dir, primary_xml_path, raw_string_data):
    start = time.time()
    rpms = {}
    LOG.info("Parsing %s MB of primary xml data from '%s'" % (len(raw_string_data)/(1024.0*1024.0), primary_xml_path))
    tree = ET.fromstring(raw_string_data)
    end_xml = time.time()
    LOG.info("Completed parsing of XML data in %s seconds for '%s'" % (end_xml - start, primary_xml_path))

    namespace = "{http://linux.duke.edu/metadata/common}"
    pkg_tags = tree.findall(".//{0}package".format(namespace))
    LOG.info("%s packages found in %s" % (len(pkg_tags), repo_dir))
    for element in pkg_tags:
        if element.get("type") == "rpm":
            checksum = element.find("{0}checksum".format(namespace))
            location = element.find("{0}location".format(namespace))
            checksum_type = checksum.get("type")
            checksum_value = checksum.text
            rpm_path = location.get('href')
            rpm_path = os.path.join(repo_dir, rpm_path)
            rpms[rpm_path] = {"type":checksum_type, "value":checksum_value}
    return rpms

def calculate_checksum(file_path, checksum_type):
    if checksum_type == "sha":
        m = hashlib.sha1()
    else:
        try:
            m = getattr(hashlib, checksum_type)
        except:
            raise Exception("Unsupported checksum type '%s'" % (checksum_type))

    f = open(file_path, 'rb')
    try:
        data = f.read()
    finally:
        f.close()
    m.update(data)
    return m.hexdigest()

def get_checksum_from_symlink(file_path):
    path = file_path
    if os.path.islink(path):
        path = os.readlink(path)
    # Example link:
    # /var/lib/pulp/repos/content/dist/rhel/rhui/server/6/6Server/x86_64/rhscl/1/os/Packages/mysql55-1-14.el6.x86_64.rpm 
    #  -> 
    #  ../../../../../../../../../../../../../packages/mysql55/1/14.el6/x86_64/e0e259d715906de88d33c87e25bf371d95bcd59a/mysql55-1-14.el6.x86_64.rpm
    return path.split("/")[-2]

def get_checksum(file_path, checksum_type, full_check):
    if full_check:
        return calculate_checksum(file_path, checksum_type)
    else:
        return get_checksum_from_symlink(file_path)

def verify_sym_links(repo_dir, expected_rpm_info, full_check):
    report = {}
    for rpm_path, checksum in expected_rpm_info.items():
        expected_checksum_value = checksum["value"]
        checksum_type = checksum["type"]
        info = {}
        # Check file exists
        if not os.path.lexists(rpm_path):
            LOG.debug("Missing '%s'" % (rpm_path))
            info["error"] = "missing"
            info["expected"] = ""
            info["found"] = ""
            info["checksum_type"] = ""
            info["symlink_source"] = ""
            report[rpm_path] = info
        elif os.path.islink(rpm_path):
            target = os.readlink(rpm_path)
            if not os.path.exists(rpm_path):
                LOG.debug("Broken symlink at: '%s' pointing to '%s'" % (rpm_path, target))
                info["error"] = "broken_symlink"
                info["expected"] = target
                info["found"] = ""
                info["checksum_type"] = ""
                info["symlink_source"] = target
                report[rpm_path] = info
            else:
                LOG.debug("Checking if '%s' is pointing to '%s' correctly" % (rpm_path, target))
                target_checksum = get_checksum(rpm_path, checksum_type, full_check)
                if target_checksum != expected_checksum_value:
                    LOG.debug("'%s' checksum mismatch, expected '%s' found '%s', full_check=%s" % (rpm_path, expected_checksum_value, target_checksum, full_check))
                    info["error"] = "checksum_mismatch"
                    info["expected"] = expected_checksum_value
                    info["found"] = target_checksum
                    info["checksum_type"] = checksum_type
                    info["symlink_source"] = target
                    report[rpm_path] = info
    LOG.info("Processed '%s' rpms for '%s', found '%s' issues" % (len(expected_rpm_info), repo_dir, len(report)))
    return report

def check_package_symlinks(repo_dir, primary_xml, full_check):
    primary_data = read_compressed_file(primary_xml)
    expected_rpm_info = parse_primary_data(repo_dir, primary_xml, primary_data)
    return verify_sym_links(repo_dir, expected_rpm_info, full_check) 

def create_package_checksum_report(repo_dir, full_check):
    LOG.debug("Creating a package checksum report for: '%s'" % (repo_dir))
    primary_xml = get_primary_xml_path(repo_dir)
    LOG.debug("Primary xml is at '%s'" % (primary_xml))
    return check_package_symlinks(repo_dir, primary_xml, full_check)

def get_repo_dirs(starting_dir):
    LOG.info("Will scan '%s' looking for all 'repodata/repomd.xml' directories" % (starting_dir))
    dirs = []
    for root, subFolders, files in os.walk(starting_dir):
        for folder in subFolders:
            if folder == "repodata":
                if os.path.exists(os.path.join(root, "repodata", "repomd.xml")):
                    dirs.append(root)
    return dirs


def run(starting_dir, full_check):
    output_csv = open("output.csv", "w")
    headers = ["path", "error", "expected", "found", "checksum_type", "symlink_source"]
    output_csv.write("%s, %s, %s, %s, %s, %s\n" % (headers[0], headers[1], headers[2], headers[3], headers[4], headers[5]))

    repo_dirs = get_repo_dirs(starting_dir)
    LOG.info("Found '%s' repo directories under: '%s'" % (len(repo_dirs), starting_dir))
    for repo_dir in repo_dirs:
        LOG.info("\n")
        report = create_package_checksum_report(repo_dir, full_check)
        for rpm_path, info in report.items():
            output_csv.write("%s, %s, %s, %s, %s, %s\n" % (rpm_path, info[headers[1]], info[headers[2]], info[headers[3]], info[headers[4]], info[headers[5]]))
        LOG.info("Finished writing '%s' issues for '%s'\n" % (len(report), repo_dir))
    output_csv.close()
    LOG.info("Processed '%s' repositories" % (len(repo_dirs)))


if __name__ == "__main__":
    parser = get_opts_parser()
    (opts, args) = parser.parse_args()
    pulp_dir = get_pulp_dir()
    packages_dir = "%s/packages" % (pulp_dir)
    starting_dir_to_scan = opts.dir
    if not starting_dir_to_scan:
        starting_dir_to_scan = "%s/repos" % (pulp_dir)
    LOG.info("Pulp's shared package dir is at: '%s'" % (packages_dir))
    msg = "Scanning '%s'" % (starting_dir_to_scan)
    if opts.full:
        msg += " will perform a full checksum check of each file"
    else:
        msg += " will use the checksum embedded in the symlink path as the checksum value to increase speed."
    LOG.info(msg)
    print run(starting_dir_to_scan, opts.full)


