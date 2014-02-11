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
    (opt, args) = parser.parse_args()
    return (opt, args)

def check_required_fields(opts, args):
    if opts.json_input is None:
        print '--json_input field cannot be blank, exiting...'
        sys.exit(1)

def read_json(opts, args):
    try:
        fh = open(opts.json_input, 'r')
        data = json.loads(fh.read())
        fh.close()
        return data
    except IOError:
        print 'unable to read %s\n' % opts.json_input
        return {}

def add_repo(data):
    config = _load_configuration(filename="/etc/rhui/rhui-tools.conf")
    prompt = Prompt()
    pulp_api = _pulp_api(config, prompt, "admin", "admin")
    cdn_api = _cdn_api(config)
    certificate_manager = _cert_manager(config, prompt)
    candidate_repo_manager = CandidateRepoManager(config, cdn_api, pulp_api, certificate_manager)
    candidate_repo_manager.translate_entitlements()
    repos, products = candidate_repo_manager.resolve_undeployed()
    cds_cluster = pulp_api.cds_clusters()['cluster1']
    cds_hostnames = [c[1] for c in cds_cluster['cds']]

    for product_name, repos in data.items():
        if not products.has_key(product_name):
            print 'No product found for %s...skipping' % product_name
            continue
        for repo_data in repos:
            repo_id = repo_data['label'].strip()
            repo_cds_enabled = repo_data['cds_enabled'].strip()
            repo_rhua_enabled = repo_data['rhua_enabled'].strip()
            # do a search & match from all known undeployed repos w/ this product name
            matched_repo = None
            for pulp_repo in products[product_name].repos.values():
                if pulp_repo.label == repo_id: 
                    print 'Found undeployed repo: %s' % pulp_repo.label
                    matched_repo = pulp_repo

            if matched_repo == None:
                print 'Could not find %s in undeployed repo list...skipping.' % repo_id
                continue
            else: 
                if repo_rhua_enabled == '1':
                    cert = certificate_manager.cert_for_entitlement(matched_repo.entitlement)
                    result = pulp_api.create_redhat_repo(config.get('redhat', 'server_url'), matched_repo, cert.cert_filename, config.get('rhui', 'repo_sync_frequency'))
                    print 'Adding %s to RHUA is %s' % (matched_repo.label, result)
                if repo_cds_enabled == '1':
                    print 'Adding %s to CDS cluster' % matched_repo.label
                    for cds in cds_hostnames:
                        pulp_api.associate_repo(cds, repo_id)

if __name__ == "__main__":
    (opts, args) = generate_options()
    check_required_fields(opts, args)
    data = read_json(opts, args)
    add_repo(data)
