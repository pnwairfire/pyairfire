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


TIME_PATTERN = "%H:%M:%S"
DATE_PATTERN = "%Y-%m-%d"
ONE_DAY = datetime.timedelta(days=1)
def parse_time_and_date(t, d):
    if not t and not d:
        return None

    if t and d:
        pattern = 'T'.join([DATE_PATTERN, TIME_PATTERN])
        val = 'T'.join([d,t])
    elif t:
        pattern = TIME_PATTERN
        val = t
    elif d:
        pattern = DATE_PATTERN
        val = d

    try:
        dt = datetime.datetime.strptime(val, pattern)
    except ValueError:
        msg = ""
        if t:
            msg += " Time must be of the format '%s'." % (TIME_PATTERN)
        if d:
            msg += " Date must be of the format '%s'." % (DATE_PATTERN)
        raise ValueError(msg)

    if d:
        return dt
    else:
        return fill_in_date(dt)

def fill_in_date(dt):
    t = dt.time()
    n = datetime.datetime.utcnow()
    if (t > n.time()):
        d = n.date()
    else:
        d = n.date() + ONE_DAY

    return datetime.datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)
