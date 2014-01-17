#!/usr/bin/python
from optparse import OptionParser
import sys
import subprocess

#create_cmd_template = "pulp-admin rpm repo create --repo-id=\"%s\" --display-name=\"%s\" --feed=%s --feed-cert %s --feed-key %s --feed-ca-cert %s --verify-feed-ssl=\"true\""
#set_schedule_cmd_template = "pulp-admin rpm repo sync schedules create --repo-id %s -s 2014-01-16T12:00:00Z/PT6H"

def create_repo(csv, cert, key, ca_cert):
    fh = open(csv, 'r')
    data = fh.read()
    fh.close()
    for line in data.split("\n"):
        if line == "":
            continue
        print "Processing line: %s" % line
        data = line.split(",")
        repo_id = data[0]
        repo_name = data[1]
        repo_feed = data[2]
        if repo_feed is not None and repo_feed != "":
            proc = subprocess.Popen(["pulp-admin", "rpm", "repo", "create", "--repo-id", "%s" % repo_id, '--display-name', "%s" % repo_name, "--feed", repo_feed, "--feed-cert", cert, "--feed-key", key, "--feed-ca-cert", ca_cert, "--verify-feed-ssl", "true"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print proc.communicate()

            proc = subprocess.Popen(["pulp-admin", "rpm", "repo", "sync", "schedules", "create", "--repo-id", "%s" % repo_id, "-s", "2014-01-16T12:00:00Z/PT6H"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print proc.communicate()

def main():
    parser = OptionParser()
    parser.add_option("-c", "--feed-cert", dest="feed_cert",
                      help="(required) feed cert needed to sync data from repo created.") 
    parser.add_option("-k", "--feed-key", dest="feed_key",
                      help="(required) feed key needed to unlock feed cert.") 
    parser.add_option("-s", "--feed-ca-cert", dest="feed_ca_cert",
                      help="(required) feed ca cert needed to validate source certificates.") 
    (options, args) = parser.parse_args()

    if len(args) < 1:
        print "No repo csv provided. Please rerun with csv arg."
        sys.exit(1)
    if not options.feed_cert:
        print "No feed certificate provided, exiting..."
        sys.exit(1)
    if not options.feed_key:
        print "No feed certificate key provided, exiting..."
        sys.exit(1)
    if not options.feed_ca_cert:
        print "No feed CA certificate provided, exiting..."
        sys.exit(1)

    create_repo(args[0], options.feed_cert, options.feed_key, options.feed_ca_cert)

if __name__ == "__main__":
    main()
