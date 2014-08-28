#!/usr/bin/env python

"""extract_point_pm25_time_seroes.py: Script to extract the predicted pm2.5
levels at a specific lat/lon from a bluesky dispersion nc output file.
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import os
import sys
from optparse import OptionParser

try:
    from pyairfire.bluesky.dispersionnc import PointExtractor
except:
    root_dir = os.path.abspath(os.path.join(sys.path[0], '../../'))
    print root_dir
    sys.path.insert(0, root_dir)
    from pyairfire.bluesky.dispersionnc import PointExtractor


def exit_with_msg(msg, extra_output):
        print msg
        print
        extra_output()
        sys.exit(1)

def parse_options():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--dispersion-nc-file", dest="nc_file_pathname",
                      help="netCDF input file pathname (required)", metavar="FILE")

    options, args = parser.parse_args()

    if not options.nc_file_pathname:
        exit_with_msg("* Error: specify nc filename ('-f')", lambda: parser.print_help())

    return options

def main():
    options = parse_options()

    PointExtractor(options.nc_file_pathname)

if __name__ == "__main__":
    main()
