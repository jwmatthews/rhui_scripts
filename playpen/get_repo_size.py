#!/usr/bin/python
import logging
import os
import sys
import time
import yum
from optparse import OptionParser

LOG = logging.getLogger(__name__)

def parse_args():
    cwd = os.getcwd()
    parser = OptionParser()
    parser.add_option('--label', action="store", default=None, help="Repo Label, arbitrary text string to identify repo")
    parser.add_option('--url', action="store", default=None, help="Repo URL")
    parser.add_option('--cert', action="store", default=None, help="X509 cert for repo if required")
    parser.add_option('--key', action="store", default=None, help="X509 certificate key for repo if required")
    parser.add_option('--csv', action="store", default=None, help="CSV file containing label,url on each line")
    parser.add_option('--dir', action="store", default=cwd, help="Directory to store yum metadata, defaults to '%s'" % (cwd))
    (opts, args) = parser.parse_args()
    if opts.label is None and opts.csv is None:
        parser.print_help()
        print "Please re-run with a --label"
        sys.exit(1)
    if opts.url is None and opts.csv is None:
        parser.print_help()
        print "Please re-run with a --url"
        sys.exit(1)
    if not os.path.exists(opts.dir):
        os.makedirs(opts.dir)
    if not os.path.isdir(opts.dir):
        parser.print_help()
        print "Please re-run with a valid --dir, the specified value '%s' is not a directory" % (opts.dir)
        sys.exit(1)
    return (opts, args)

def parse_csv(csvfile):
    # Expected format of csvfile is each line represents a single repo:
    #  repo_label,repo_url
    retval = []
    f = open(csvfile, 'r')
    try:
        for raw_line in f.readlines():
            line = raw_line.strip()
            pieces = line.split(",")
            if len(pieces) >= 2:
                retval.append([pieces[0], pieces[1]])
            else:
                print "Unexpected error parsing '%s'" % (csvfile)
                print "Error Line:   %s" % (line)
                sys.exit(1)
        return retval
    finally:
        f.close()


def get_yum_repo(output_dir, label, url, cert=None, key=None):
    repo = yum.yumRepo.YumRepository(label)
    repo.basecachedir = output_dir
    repo.cache = 0
    repo.metadata_expire = 0
    repo.baseurl = [url]
    repo.baseurlSetup()
    repo.sslclientcert = cert
    repo.sslclientkey = key
    repo.sslverify = False
    return repo

def get_repo_info(output_dir, label, url, cert=None, key=None):
    info = {}
    total_bytes = 0
    total_number_rpms = 0

    print "\n'%s' Will download metadata at URL: '%s'" % (label, url)
    yum_repo = get_yum_repo(output_dir=output_dir, label=label, url=url, cert=cert, key=key)
    start = time.time()
    yum_repo.retrieveMD("primary")
    end = time.time()
    print "'%s' primary metadata downloaded in %s seconds" % (label, end-start)
    sack = yum_repo.getPackageSack()
    sack.populate(yum_repo, 'metadata', None, 0)
    all_rpms = sack.returnPackages()
    for rpm in all_rpms:
        total_bytes += rpm.size
        total_number_rpms += 1
    yum_repo.close()
    print "'%s' RPMs: %s, Size: %s GB" % (label, total_number_rpms, to_gb(total_bytes))
    info["total_bytes"] = total_bytes
    info["total_number_rpms"] = total_number_rpms
    return info

def to_gb(value):
    return float(value)/(1024*1024*1024)

def print_info(repos):
    print "\n\n*******Summary Info*******"
    for label, info in repos.items():
        total = info["total_bytes"]
        num_rpms = info["total_number_rpms"]
        print "%s, %s GB, %s RPMs" % (label, to_gb(info["total_bytes"]), info["total_number_rpms"])

if __name__ == "__main__":
    (options, args) = parse_args()
    cert = options.cert
    key = options.key
    output_dir = options.dir
    if options.csv is not None:
        repos = parse_csv(options.csv)
    else:
        repos = [(options.label, options.url)]

    print "Will download metadata and determine repo size for '%s' repos and store metadata at: '%s'" % (len(repos), output_dir)
    info = {}
    for repo in repos:
        label = repo[0]
        url = repo[1]
        try:
            info[label] = get_repo_info(output_dir=output_dir, label=label, url=url, cert=cert, key=key)
        except Exception, e:
            print "Unable to fetch info for: %s" % (label)
            print "Caught exception: %s" % (e)
            print "Will ignore this repo and continue to try to process remaining repos"
    print_info(info)
