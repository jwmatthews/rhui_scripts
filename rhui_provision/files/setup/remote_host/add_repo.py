#! /usr/bin/python

from rhui.tools.launcher import _load_configuration, _cert_manager, _pulp_api, _cdn_api
from rhui.common.prompt import Prompt
from rhui.tools.repo_candidates import CandidateRepoManager
from rhui.tools.pulp_api import Pulp
from rhui.tools.cdn_api import CDN

from optparse import OptionParser 

def generate_options():
    parser = OptionParser()
    parser.add_option("-j", "--json_input", dest="json_input",
                      help="JSON repo file")
    (opt, args) = parser.parse_args()
    return (opt, args)

def check_required_fields(opts, args):
    pass

def read_json():
    pass

def add_repo(data):
    config = _load_configuration(filename="/etc/rhui/rhui-tools.conf")
    prompt = Prompt()
    pulp_api = _pulp_api(config, prompt, "admin", "admin")
    cdn_api = _cdn_api(config)
    certificate_manager = _cert_manager(config, prompt)
    candidate_repo_manager = CandidateRepoManager(config, cdn_api, pulp_api, certificate_manager)
    candidate_repo_manager.translate_entitlements()
    repos, products = candidate_repo_manager.resolve_undeployed()
    product_name = "Red Hat Enterprise Linux 6 Server Beta from RHUI (Source RPMs)"
    repo = products[product_name].repos.values()[0] # do a search & match for index and then use index
    cert = certificate_manager.cert_for_entitlement(repo.entitlement)
    result = pulp_api.create_redhat_repo(config.get('redhat', 'server_url'), repo, cert.cert_filename, config.get('rhui', 'repo_sync_frequency'))
    print result

if __name__ == "__main__":
    (opts, args) = generate_options()
    check_required_fields(opts, args)
    data = read_json()
    add_repo(data)
