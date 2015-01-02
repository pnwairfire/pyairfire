__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import sys

def exit_with_msg(msg, extra_output=None, output=None):
    output = output or sys.stderr.write
    output("\n*** ERROR: %s\n\n" % (msg))
    if extra_output:
        extra_output()
    output('\n')
    sys.exit(1)
