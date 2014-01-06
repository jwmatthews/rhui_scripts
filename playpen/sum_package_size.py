#!/usr/bin/python

import os
import sys
from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser()
    (options, args) = parser.parse_args()
    if len(args) <= 0:
        print 'No path provided, please re-run with path as first argument.'
        sys.exit(1)

    path = args[0]

    total = 0.0
    os.chdir(path)
    for link in os.listdir('.'):
        rpm_path = os.readlink(link)
        size = os.path.getsize(rpm_path)
        total = total + float(size)
    print 'Number of rpms found: %s' % (len(os.listdir('.')))
    print 'Total: %s bytes, %s KBs, %s MBs, %s GBs' % (total, total/1000, total/1000000, total/1000000000)
