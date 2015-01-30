"""pyairfire.fabric.output
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import os

__all__ = [
    'error',
    'debug_log'
]

def error(msg):
    print "*** ERROR:  %s" % (msg)
    exit(1)

def debug_log(msg):
    if os.environ.has_key('DEBUG'):
        print msg
