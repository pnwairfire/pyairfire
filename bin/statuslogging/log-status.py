#!/usr/bin/env python

"""log-status.py: Script to ....

Example calls:
 > ./bin/statuslogging/log-status.py \
    -e http://status-log-production.herokuapp.com/status-logs \
    -k abc123 -s dsfjerw -p BlueSky -o Ok -f foo=bar -f baz=foo -v
"""

__author__      = "Joel Dubowy"

import datetime
import logging
import re
import sys

import afscripting as scripting

try:
    from pyairfire import statuslogging
except:
    import os
    root_dir = os.path.abspath(os.path.join(sys.path[0], '../../'))
    sys.path.insert(0, root_dir)
    from pyairfire import statuslogging

# Note: though some argue that all required parameters should be specified as
# positional arguments, I prefer using 'options' flags, even though this
# means that there are required 'options', which is oxymoronic.

REQUIRED_OPTIONS = [
    {
        'short': '-e',
        'long': '--api-endpoint',
        'dest': 'api_endpoint',
        'help': 'status logger submission API endpoint (required)'
    },
    {
        'short': '-k',
        'long': '--api-key',
        'dest':  'api_key',
        'help': 'api key used to make requests to status logger service (required)'
    },
    {
        'short': '-s',
        'long': '--api-secret',
        'dest': 'api_secret',
        'help': 'api secret used to make requests to status logger service (required)'
    },
    {
        'short': '-p',
        'long': '--process',
        'dest': 'process',
        'help': 'name of process (required)'
    },
    {
        'short': '-o',
        'long': '--status',
        'dest': 'status',
        'help': "String valued status, ex. 'Ok' (required)"
    }
]
OPTIONAL_OPTIONS = [
    {
        'short': '-f',
        'long': '--field',
        'dest': "fields",
        'type': "string",
        'action': "callback",
        'help': "extra fields to add to status log",
        'default': {},
        'callback': scripting.options.extract_and_set_key_value
    }
]

def error_handler(e):
    scripting.utils.exit_with_msg("Failed to submit status: %s" % (e))

def main():
    parser, options, args = scripting.options.parse_options(REQUIRED_OPTIONS,
        OPTIONAL_OPTIONS)

    try:
        sl = statuslogging.StatusLogger(options.api_endpoint, options.api_key, options.api_secret, options.process)
        t = datetime.datetime.now()
        sl.log(options.status, error_handler=error_handler, **dict(options.fields))
        logging.info("It took %f seconds to submit the log" % (
            (datetime.datetime.now() - t).seconds))

    except Exception as e:
        scripting.utils.exit_with_msg(e)

if __name__ == "__main__":
    main()
