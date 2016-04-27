#!/usr/bin/env python

"""extract-point-pm25-time-series.py: Script to extract the predicted pm2.5
levels at a specific lat/lon from a bluesky dispersion nc output file.

Example calls:
 > ./bin/bluesky/extract-point-pm25-time-series.py \
    -f ~/Downloads/smoke_dispersion-pnw-4k-2014082600.nc --lat=45.68938 --lng=-116.476
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import datetime
import json
import logging
import sys
import traceback

try:
    from pyairfire.bluesky.dispersionnc import PointExtractor
    from pyairfire import scripting
except:
    import os
    root_dir = os.path.abspath(os.path.join(sys.path[0], '../../'))
    sys.path.insert(0, root_dir)
    from pyairfire.bluesky.dispersionnc import PointExtractor
    from pyairfire import scripting

# Note: though some argue that all required parameters should be specified as
# positional arguments, I prefer using 'options' flags, even though this
# means that there are required 'options', which is oxymoronic.

REQUIRED_OPTIONS = [
    {
        'short': "-f",
        'long': "--dispersion-nc-file",
        'dest': "nc_file_pathname",
        'help': "netCDF input file pathname (required)",
        'metavar': "FILE"
    },
    {
        'short': "--lat",
        'dest': "lat",
        'help': "latitude (required)",
        'type': float
    },
    {
        'short': "--lng",
        'dest': "lng",
        'help': "longitude (required)",
        'type': float
    }
]

OPTIONAL_OPTIONS = []

def main():
    parser, options, args = scripting.options.parse_options(REQUIRED_OPTIONS,
        OPTIONAL_OPTIONS)

    try:
        pe = PointExtractor(options.nc_file_pathname)
        t = datetime.datetime.now()
        point_time_series = pe.extract(options.lat, options.lng)
        logging.info("It took %f seconds to extract" % (
            (datetime.datetime.now() - t).seconds))
        print json.dumps(point_time_series)

    except Exception, e:
        logging.debug(traceback.format_exc())
        scripting.utils.exit_with_msg(e.message)

if __name__ == "__main__":
    main()
