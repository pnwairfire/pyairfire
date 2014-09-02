#!/usr/bin/env python

"""extract_point_pm25_time_seroes.py: Script to extract the predicted pm2.5
levels at a specific lat/lon from a bluesky dispersion nc output file.
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import json
import sys
from optparse import OptionParser

try:
    from pyairfire.bluesky.dispersionnc import PointExtractor
except:
    import os
    root_dir = os.path.abspath(os.path.join(sys.path[0], '../../'))
    sys.path.insert(0, root_dir)
    from pyairfire.bluesky.dispersionnc import PointExtractor


def exit_with_msg(msg, extra_output=None):
        print "* Error: %s" % (msg)
        if extra_output:
            extra_output()
        sys.exit(1)

def parse_options():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--dispersion-nc-file", dest="nc_file_pathname",
        help="netCDF input file pathname (required)", metavar="FILE")
    parser.add_option("--lat", dest="lat", help="latitude (required)", type=float)
    parser.add_option("--lng", dest="lng", help="longitude (required)", type=float)
    parser.add_option("-v", "--verbose", dest="verbose", help="to turn on extra output",
        action="store_true", default=False)

    options, args = parser.parse_args()

    if not options.nc_file_pathname:
        exit_with_msg("specify nc filename ('-f')", lambda: parser.print_help())
    if not options.lat or not options.lng:
        exit_with_msg("specify lat and lng ('--lat/--lng')", parser.print_help)

    if options.verbose:
        print "NC file pathname: %s" % (options.nc_file_pathname)
        print "latitude: %s" % (options.lat)
        print "Longitude: %s" % (options.lng)

    return options

def main():
    options = parse_options()

    try:
        pe = PointExtractor(options.nc_file_pathname)
        point_time_series = pe.extract(options.lat, options.lng)

        print json.dumps(point_time_series)

    except Exception, e:
        exit_with_msg(e.message)

if __name__ == "__main__":
    main()
