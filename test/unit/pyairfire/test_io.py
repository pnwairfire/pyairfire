"""Unit tests for pyairfire.io"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2016, AirFire, PNW, USFS"

import json
import sys
import io

from pytest import raises

from pyairfire import io as p_io

class TestCSV2JSON(object):

    def setup_method(self):
        self._output = io.StringIO()

    def test_convert_one_fire(self, monkeypatch):
        monkeypatch.setattr(sys, "stdin", io.StringIO(
            'id,name, event_id , foo,bar ,baz \n'
            '12fj33,Big Fire, dslfhew, 123, 34.34 , BAZ\n'
        ))
        monkeypatch.setattr(sys, "stdout", self._output)
        p_io.CSV2JSON().convert()
        expected = [
            {
                "id": "12fj33",
                "name": "Big Fire",
                "event_id": "dslfhew",
                "foo": 123,
                "bar": 34.34,
                "baz": "BAZ"
            }
        ]
        assert expected == json.loads(self._output.getvalue())

    def test_convert_three_fires_no_merging(self, monkeypatch):
        monkeypatch.setattr(sys, "stdin", io.StringIO(
            'id,name, event_id , foo,bar ,baz \n'
            '12fj33,Big Fire, dslfhew, 123, 34.34 , BAZ\n'
            '12fj33,Big Fire, dslfhew, 343, 24.34 , BAZ\n'
            '34erw5,Small Fire, 298rijfssdf, 20 20, 234.34.243, baaaz'
        ))
        monkeypatch.setattr(sys, "stdout", self._output)
        p_io.CSV2JSON().convert()
        expected = [
            {
                "id": "12fj33",
                "name": "Big Fire",
                "event_id": "dslfhew",
                "foo": 123,
                "bar": 34.34,
                "baz": "BAZ"
            },
            {
                "id": "12fj33",
                "name": "Big Fire",
                "event_id": "dslfhew",
                "foo": 343,
                "bar": 24.34,
                "baz": "BAZ"
            },
            {
                "id": "34erw5",
                "name": "Small Fire",
                "event_id": "298rijfssdf",
                "foo": "20 20",
                "bar": "234.34.243",
                "baz": "baaaz"
            }
        ]
        assert expected == json.loads(self._output.getvalue())

    def test_convert_three_fires_with_merging(self, monkeypatch):
        # TDOO: implement once merge option is supported
        pass
