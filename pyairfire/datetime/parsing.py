__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import datetime

RECOGNIZED_DATETIME_FORMATS = [
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%dT%H:%M:%SZ',
    '%Y/%m/%dT%H:%M:%S',
    '%Y/%m/%dT%H:%M:%SZ',
    '%Y%m%dT%H%M%S',
    '%Y%m%dT%H%M%SZ',
    '%Y-%m-%d',
    '%Y/%m/%d',
    '%Y%m%d'
]

def parse(datetime_str):
    for format in RECOGNIZED_DATETIME_FORMATS:
        try:
            return datetime.datetime.strptime(datetime_str, format)
        except ValueError:
            # Go on to next format
            pass
    # If we got here, none of them matched, so raise error
    raise ValueError("Invalid datetime format '%s'" % (datetime_str))
