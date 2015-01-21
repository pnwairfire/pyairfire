__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import sys

def exit_with_msg(msg, extra_output=None, output=None, exit_code=1,
        prefix="*** ERROR: ", extra_preceeding_output=None):
    """Prints message and exits
    """
    output = output or sys.stderr.write
    if extra_preceeding_output:
        extra_preceeding_output()
    output("\n%s%s\n\n" % (prefix, msg))
    if extra_output:
        extra_output()
    output('\n')
    sys.exit(exit_code)
