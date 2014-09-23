#!/usr/bin/env python

"""log-status.py: Script to ....

Example calls:
 > ./bin/statuslogging/log-status.py \
    -e http://status-log-production.herokuapp.com/status-logs \
    -k abc123 -s dsfjerw -p BlueSky -o Ok -f foo=bar -f baz=foo -v
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import datetime
import re
import sys
from optparse import OptionParser

try:
    from pyairfire.statuslogging import StatusLogger
except:
    import os
    root_dir = os.path.abspath(os.path.join(sys.path[0], '../../'))
    sys.path.insert(0, root_dir)
    from pyairfire.statuslogging import StatusLogger

def exit_with_msg(msg, extra_output=None):
    print "\n*** ERROR: %s\n" % (msg)
    if extra_output:
        extra_output()
    print
    sys.exit(1)


REQUIRED_OPTIONS = [
    ('-e', '--api-endpoint', 'api endpoint', 'api_endpoint'),
    ('-k', '--api-key', 'api key', 'api_key'),
    ('-s', '--api-secret', 'api secret', 'api_secret'),
    ('-p', '--process', 'process name', 'process'),
    ('-o', '--status', 'status', 'status')
]
KEY_VALUE_EXTRACTER = re.compile('^([^=]+)=([^=]+)$')
def parse_options():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    # Required options
    parser.add_option("-e", "--api-endpoint", dest="api_endpoint",
        help="status logger submission API endpoint (required)")
    parser.add_option("-k", "--api-key", dest="api_key",
        help="api key used to make requests to status logger service (required)")
    parser.add_option("-s", "--api-secret", dest="api_secret",
        help="api secret used to make requests to status logger service (required)")
    parser.add_option("-p", "--process", dest="process",
        help="name of process (required)")
    parser.add_option('-o', "--status", dest="status",
        help="String valued status, ex. 'Ok' (required")

    # Optional
    parser.add_option('-f', '--field',  dest="fields", action="append",
        help="extra fields to add to status log", default=[])
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
        help="to turn on extra output", default=False)

    options, args = parser.parse_args()

    for short_key, long_key, name, attr in REQUIRED_OPTIONS:
        if not options.__dict__[attr]:
            msg = "specify %s (%s'%s')" % (name, "'%s', "  % (short_key) if short_key else '', long_key)
            exit_with_msg(msg, lambda: parser.print_help())

    fields = {}
    for f in options.fields:
        m = KEY_VALUE_EXTRACTER.search(f.strip())
        if not m:
            exit_with_msg("Extra fields must be of the form 'key=value'",
                lambda: parser.print_help())
        fields[m.group(1)] = m.group(2)

    if options.verbose:
        for short_key, long_key, name, attr in REQUIRED_OPTIONS:
            print "%s (%s'%s'): %s" % (name,
                "'%s', "  % (short_key) if short_key else '', long_key,
                options.__dict__[attr])
        if fields:
            print "Extra fields ('-f', '--field'):"
            for k,v  in fields.items():
                print "  %s: %s" % (k, v)

    return options, fields

def error_handler(e):
    exit_with_msg("Failed to submit status: %s" % (e))

def main():
    options, fields = parse_options()

    try:
        sl = StatusLogger(options.api_endpoint, options.api_key, options.api_secret, options.process)
        t = datetime.datetime.now()
        sl.log(options.status, error_handler=error_handler, **fields)
        if options.verbose:
            print "It took %f seconds to submit the log" % ((datetime.datetime.now() - t).seconds)

    except Exception, e:
        exit_with_msg(e.message)

if __name__ == "__main__":
    main()
