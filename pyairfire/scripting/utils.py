__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import sys

def exit_with_msg(msg, extra_output=None):
    print "\n*** ERROR: %s\n" % (msg)
    if extra_output:
        extra_output()
    print
    sys.exit(1)
