# -*- coding: utf-8 -*-
#
# Copyright © 2012 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

import httplib
try:
    import simplejson as json
except:
    import json
import urllib2
import urlparse

from urlgrabber import grabber
from yum.plugins import TYPE_CORE, PluginYumExit


requires_api_version = '2.5'
plugin_type = (TYPE_CORE,)

ID_DOC_URL = "http://169.254.169.254/latest/dynamic/instance-identity/document"

# Instance from one region will be redirected to another region's CDS for content
REDIRECTS = [('us-gov-west-1', 'us-west-2'), ('REGION', 'us-east-1')]

def prereposetup_hook(conduit):
    """
    Will look to the load balancer listing file
    to attempt to contact all load balancers. Once one has been established
    as up, configure the repo to use that as the mirror list destination.

    This call will also use the information from the load balancer alive
    test to make sure its current list of load balancer members is up to
    date. Additions/removals to/from the load balancer will will then be
    reflected in the local load balancer listing file.
    
    Note: This callback has changed from 'postreposetup_hook' to 'preresposetup_hook'
          to work with a yum change in RHEL-7.  yum will not attempt to fetch all 
          repo metadata prior to calling 'postreposetup' callbacks.  Therefore we need
          to run and modify the URL in the prereposetup.
    """

    # Only take effect if handling a RHUI repo
    rhui_repos = []
    repos = conduit.getRepos()
    for repo in repos.listEnabled():
        if repo.id.startswith('rhui'):
            rhui_repos.append(repo)

    if len(rhui_repos) == 0:
        return

    # Rely on yum to parse proxy settings.  Just use the first rhui repo to
    # read the proxy settings
    repo = rhui_repos[0]
    try:
        ugopts = repo._default_grabopts()
    # _default_grabopts not always available on RHEL 5
    except AttributeError:
        ugopts = {'keepalive': repo.keepalive,
                  'bandwidth': repo.bandwidth,
                  'retry': repo.retries,
                  'throttle': repo.throttle,
                  'proxies': repo.proxy_dict,
                  'timeout': repo.timeout}

    # Read in the list of CDS load balancers
    cds_list_filename = conduit.confString('main', 'cds_list_file')
    f = open(cds_list_filename, 'r')
    cds_balancers = f.read().split()
    f.close()

    # Figure out which load balancer is up
    up_lb = None
    balancers_tried = 0
    for lb in cds_balancers:

        # Dynamically set the cds load balancer to the appropriate region
        # bz#921116, copy ami to another region
        original = lb
        try:
            region_new = json.loads(_load_id())["region"]
            start = original.find(".") + 1
            end = original.find(".", start)
            region_old = original[start:end]
            
            for reg, redirect in REDIRECTS:
                if reg == region_new.strip():
                    region_new = redirect

            if region_new != region_old:
                lb = (original[:start] + region_new + original[end:]).encode('ascii')
                conduit.info(5, "rhui load balancer: %s" % lb)
        except:
            # We failed to get region name from EC2
            conduit.error(0, "Failed to get region name from EC2")

        try:
            balancers_tried += 1
            balancers = grabber.urlread('https://%s/pulp/mirror/?members' % lb,
                                        **ugopts)
            balancers = balancers.split('\n')
            up_lb = lb

            # Make sure the known list of load balancers is accurate.
            # If not, update the listing file.
            # We want to attempt to retain the order of the balancer list file,
            # so it's not as simple as sorting them and doing an equality check.

            # First, remove any from the local list that aren't in the new list.
            modified = [x for x in cds_balancers if x in balancers]

            # Then, add any new ones to the end of the local list.
            modified = modified + [x for x in balancers if x not in modified]

            # If any changes have been made, save to the listing file.
            if modified != cds_balancers:
                f = open(cds_list_filename, 'w')
                f.write('\n'.join(modified))
                f.close()

            break
        except:
            if balancers_tried == len(cds_balancers):
                raise PluginYumExit(
                    "Could not contact any CDS load balancers: %s." %
                    ', '.join(cds_balancers))
            else:
                print "Could not contact CDS load balancer %s, trying others." % lb

    for repo in rhui_repos:
        # Yank out the original mirror list entry and stuff in
        # the good one
        path = urlparse.urlparse(repo.mirrorlist)[2]
        repo.mirrorlist = 'https://%s%s' % (up_lb, path)


def _load_id():
    '''
    Loads and returns the Amazon metadata for identifying the instance.

    @rtype: string
    '''
    try:
        fp = urllib2.urlopen(ID_DOC_URL)
        id_doc = fp.read()
        fp.close()
    except urllib2.URLError:
        return None

    return id_doc
