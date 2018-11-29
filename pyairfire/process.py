"""pyairfire.process

# TODO: rename this module and move it?
"""
# to import standard dateimt package instead of local one


__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2016, AirFire, PNW, USFS"

import datetime

__all__ = [
    "RunTimeRecorder"
]

class RunTimeRecorder(object):
    """Records run time information in dict that RunTimeRecorder is
    instantiated with.
    """

    def __init__(self, rt_dict):
        if not isinstance(rt_dict, dict):
            raise ValueError(
                "RunTimeRecorder must be instantiated with a dict object")
        self._rt_dict = rt_dict

    def __enter__(self):
        self._start = datetime.datetime.utcnow()

    def __exit__(self, e_type, value, tb):
        hours, minutes, seconds = self._compute_time_components()
        self._rt_dict.update({
            "start": self._format_datetime(self._start),
            "end": self._format_datetime(end),
            "total": self._format_total(hours, minutes, seconds)
        })

    def _format_datetime(self, dt):
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def _format_total(self, hours, minutes, seconds):
        return "{}h {}m {}s".format(
            hours, minutes, seconds)

    def _compute_time_components(self):
        end = datetime.datetime.utcnow()
        rt = end - self._start
        hours, rem = divmod(rt.total_seconds(), 3600)
        minutes, seconds = divmod(rem, 60)
        seconds = int(seconds) + rt.microseconds / 1000000
        return hours, minutes, seconds
