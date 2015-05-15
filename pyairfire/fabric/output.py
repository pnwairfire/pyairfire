"""pyairfire.fabric.output
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import os
import sys

__all__ = [
    'error',
    'debug_log'
]

def error(msg):
    print "*** ERROR:  %s" % (msg)
    sys.exit(1)

def debug_log(msg):
    if os.environ.has_key('DEBUG'):
        print msg

def confirm(msg):
    print(msg)
    sys.stdout.write("Do you want to continue (y/n)?: ")
    r = sys.stdin.readline().strip()
    if 'y' != r.lower():
        print("Exiting.")
        sys.exit(0)
