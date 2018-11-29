"""Unit tests for pyairfire.process"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2016, AirFire, PNW, USFS"

import datetime

import freezegun
#from py.test import raises

from pyairfire.process import RunTimeRecorder

class TestRunTimeRecorder(object):

    def setup(self):
        self._d = {}
        self._rtr = RunTimeRecorder(self._d)
        self._rtr._start = datetime.datetime(2018,1,1)

    def test_compute_time_components(self):
        with freezegun.freeze_time("2018-01-02 01:01:01.0123"):
            end, hours, minutes, seconds = self._rtr._compute_time_components()
            assert end == datetime.datetime(2018,1,2,1,1,1,12300)
            assert hours == 25
            assert minutes == 1
            assert seconds == 1.0123

        with freezegun.freeze_time("2018-01-02 00:00:00"):
            end, hours, minutes, seconds = self._rtr._compute_time_components()
            assert end == datetime.datetime(2018,1,2,0,0,0)
            assert hours == 24
            assert minutes == 0
            assert seconds == 0

        with freezegun.freeze_time("2018-01-01 00:00:01"):
            end, hours, minutes, seconds = self._rtr._compute_time_components()
            assert end == datetime.datetime(2018,1,1,0,0,1)
            assert hours == 0
            assert minutes == 0
            assert seconds == 1

        with freezegun.freeze_time("2018-01-01 00:00:00"):
            end, hours, minutes, seconds = self._rtr._compute_time_components()
            assert end == datetime.datetime(2018,1,1,0,0,0)
            assert hours == 0
            assert minutes == 0
            assert seconds == 0

    def test_format_datetime(self):
        v = self._rtr._format_datetime(datetime.datetime(2018,1,2,1,1,1,12300))
        assert "2018-01-02T01:01:01.012300Z" == v

        v = self._rtr._format_datetime(datetime.datetime(2018,1,2,1,1,1))
        assert "2018-01-02T01:01:01.000000Z" == v

        v = self._rtr._format_datetime(datetime.datetime(2018,1,2))
        assert "2018-01-02T00:00:00.000000Z" == v

    def test_format_total(self):
        assert "10h 0m 1s" == self._rtr._format_total(10,0,1)
        assert "31h 0m 0s" == self._rtr._format_total(31,0,0)
        assert "31h 23m 3.023s" == self._rtr._format_total(31,23,3.023)
