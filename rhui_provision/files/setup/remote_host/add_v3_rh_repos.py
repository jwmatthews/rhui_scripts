#!/usr/bin/python

from rhui.tools.launcher import _load_configuration, _cert_manager, _pulp_api, _cdn_api
from rhui.common.prompt import Prompt
from rhui.tools.repo_candidates import CandidateRepoManager
from rhui.tools.pulp_api import Pulp
from rhui.tools.cdn_api import CDN

from optparse import OptionParser 
import json
import sys

def generate_options():
    parser = OptionParser()
    parser.add_option("-j", "--json_input", dest="json_input",
                      help="JSON repo file")
    parser.add_option("-u", "--username", dest="username", default="admin",
                      help="RHUI username")
    parser.add_option("-p", "--password", dest="password", default="admin",
                      help="RHUI password")

    (opt, args) = parser.parse_args()
    return (opt, args)

def check_required_fields(opts, args):
    if opts.json_input is None:
        print '--json_input field cannot be blank, exiting...'
        sys.exit(1)

def read_json(filename, args):
    try:
        fh = open(filename, 'r')
        data = json.loads(fh.read())
        fh.close()
        return data
    except IOError:
        print 'unable to read %s\n' % filename
        return {}

def search_path(undeployed_repos, path):
    for k, v in undeployed_repos.items():
        if path in k:
            return v
    return None

def add_repo(data, username="admin", password="admin"):
    config = _load_configuration(filename="/etc/rhui/rhui-tools.conf")
    prompt = Prompt()
    pulp_api = _pulp_api(config, prompt, username, password)
    cdn_api = _cdn_api(config)
    certificate_manager = _cert_manager(config, prompt)
    candidate_repo_manager = CandidateRepoManager(config, cdn_api, pulp_api, certificate_manager)
    candidate_repo_manager.translate_entitlements()
    repos, products = candidate_repo_manager.resolve_undeployed()

    undeployed_repos = {}
    for k,v in repos.items():
        key = v.real_url
        undeployed_repos[key] = v

    for product_name, repos in data.items():
        for repo_data in repos:
            repo_path = repo_data['real_url'].strip()
            repo_cds_enabled = repo_data['cds_enabled'].strip()
            repo_rhua_enabled = repo_data['rhua_enabled'].strip()
            matched_repo = search_path(undeployed_repos, repo_path)
            if matched_repo is not None:
                print "Found %s in undeployed_repos.\n" % repo_path
                if repo_rhua_enabled == '1':
                    cert = certificate_manager.cert_for_entitlement(matched_repo.entitlement)
                    result = pulp_api.create_redhat_repo(matched_repo, cert.cert_filename, config.get('rhui', 'repo_sync_frequency'))
                    print 'Adding %s to RHUA is %s\n' % (matched_repo.label, result)
            else:
                print 'Could not find %s in undeployed repo list...skipping.\n' % repo_path
                continue

if __name__ == "__main__":
    (opts, args) = generate_options()
    check_required_fields(opts, args)

    filename = opts.json_input
    username = opts.username
    password = opts.password

    data = read_json(filename, args)
    add_repo(data, username, password)
