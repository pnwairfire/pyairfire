__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import datetime
import re
from optparse import OptionValueError

from .utils import exit_with_msg

def check_required_options(options, required_options, extra_error_output):
    """

    Arguments:
     - required_options -- array of required option tuples (see note below)
     - extra_error_output -- callable outputter of extra error msg content

    Expects required options to be of the form:

        REQUIRED_OPTIONS = [
            ('-f', '--foo', 'foo descriptor', 'foo'),
            ...
        ]

    where the last element of each tuple is the attribute name in the options object.
    """
    for short_key, long_key, name, attr in required_options:
        if not options.__dict__[attr]:
            msg = "specify %s (%s'%s')" % (name, "'%s', "  % (short_key) if short_key else '', long_key)
            exit_with_msg(msg, extra_error_output)

KEY_VALUE_EXTRACTER = re.compile('^([^=]+)=([^=]+)$')

## Callbacks for add_option

def extract_and_set_key_value(option, opt, value, parser):
    """Splits value into key/value, and set in destination dict

    Note: Expects value to be of the format 'key=value'.  Also expects
    destination (i.e. parser.values's option.dest attribute), to be
    initialized as an empty dict.
    """
    m = KEY_VALUE_EXTRACTER.search(value.strip())
    if not m:
        msg = "Invalid value '%s' for option '%s' - values must be of the form 'key=value'" % (
            value, opt)
        raise OptionValueError(msg)
    d = getattr(parser.values, option.dest)
    d[m.group(1)] = m.group(2)

RECOGNIZED_DATETIME_FORMATS =[
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%dT%H:%M:%SZ',
    '%Y/%m/%dT%H:%M:%S',
    '%Y/%m/%dT%H:%M:%SZ',
    '%Y%m%dT%H%M%S',
    '%Y%m%dT%H%M%SZ'
    '%Y-%m-%d',
    '%Y/%m/%d',
    '%Y%m%d'
]
def parse_datetime(option, opt, value, parser):
    for format in self.RECOGNIZED_DATETIME_FORMATS:
        try:
            dt = datetime.datetime.strptime(value, format)
            setattr(parser.values, option.dest, dt)
            return
        except ValueError:
            # Go on to next format
            pass
    # If we got here, none of them matched, so raise error
    raise OptionValueError("Invalid datetime format '%s' for option %s" % (value, opt))
