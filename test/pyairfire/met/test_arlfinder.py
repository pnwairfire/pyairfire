"""Unit tests for bluesky.arlfinder"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2016, AirFire, PNW, USFS"

import copy
import datetime
import tempfile
import StringIO # for monkeypatching

from py.test import raises

from pyairfire.met import arlfinder
from pyairfire import io # for monkeypatching

##
## Tests for ArlFinder
##

INDEX_2015110200 = """filename,start,end,interval
/storage/NWRMC/4km/2015110200/wrfout_d3.2015110100.f24-35_12hr02.arl,2015-11-02 00:00:00,2015-11-02 11:00:00,12
/storage/NWRMC/4km/2015110200/wrfout_d3.2015110200.f12-23_12hr01.arl,2015-11-02 12:00:00,2015-11-02 23:00:00,12
/storage/NWRMC/4km/2015110200/wrfout_d3.2015110200.f24-35_12hr02.arl,2015-11-03 00:00:00,2015-11-03 11:00:00,12
/storage/NWRMC/4km/2015110200/wrfout_d3.2015110200.f36-47_12hr03.arl,2015-11-03 12:00:00,2015-11-03 23:00:00,12
/storage/NWRMC/4km/2015110200/wrfout_d3.2015110200.f48-59_12hr04.arl,2015-11-04 00:00:00,2015-11-04 11:00:00,12
/storage/NWRMC/4km/2015110200/wrfout_d3.2015110200.f60-71_12hr05.arl,2015-11-04 12:00:00,2015-11-04 23:00:00,12
/storage/NWRMC/4km/2015110200/wrfout_d3.2015110200.f72-83_12hr06.arl,2015-11-05 00:00:00,2015-11-05 11:00:00,12
"""

INDEX_2015110300 = """filename,start,end,interval
/path/to/NWRMC/4km/2015110300/wrfout_d3.2015110200.f24-35_12hr02.arl,2015-11-03 00:00:00,2015-11-03 11:00:00,12
/path/to/NWRMC/4km/2015110300/wrfout_d3.2015110300.f12-23_12hr01.arl,2015-11-03 12:00:00,2015-11-03 23:00:00,12
/path/to/NWRMC/4km/2015110300/wrfout_d3.2015110300.f24-35_12hr02.arl,2015-11-04 00:00:00,2015-11-04 11:00:00,12
/path/to/NWRMC/4km/2015110300/wrfout_d3.2015110300.f36-47_12hr03.arl,2015-11-04 12:00:00,2015-11-04 23:00:00,12
/path/to/NWRMC/4km/2015110300/wrfout_d3.2015110300.f48-59_12hr04.arl,2015-11-05 00:00:00,2015-11-05 11:00:00,12
/path/to/NWRMC/4km/2015110300/wrfout_d3.2015110300.f60-71_12hr05.arl,2015-11-05 12:00:00,2015-11-05 23:00:00,12
/path/to/NWRMC/4km/2015110300/wrfout_d3.2015110300.f72-83_12hr06.arl,2015-11-06 00:00:00,2015-11-06 11:00:00,12
"""

class TestARLFinder(object):
    def setup(self):
        self.arl_finder = arlfinder.ArlFinder(tempfile.mkdtemp())

    def test_create_date_matcher(self):
        s = datetime.datetime(2015, 1, 1, 14)
        e = datetime.datetime(2015, 1, 4, 2)
        m = self.arl_finder._create_date_matcher(s,e)
        assert m.pattern == '.*(20141228|20141229|20141230|20141231|20150101|20150102|20150103|20150104)'

        self.arl_finder._max_days_out = 1
        m = self.arl_finder._create_date_matcher(s,e)
        assert m.pattern == '.*(20141231|20150101|20150102|20150103|20150104)'

        assert arlfinder.ArlFinder.ALL_DATE_MATCHER == self.arl_finder._create_date_matcher(None, e)
        assert arlfinder.ArlFinder.ALL_DATE_MATCHER == self.arl_finder._create_date_matcher(s, None)
        assert arlfinder.ArlFinder.ALL_DATE_MATCHER == self.arl_finder._create_date_matcher(None, None)

    # TODO: somehow test _find_index_files, monkeypatching os.walk, etc.
    #   appropriately

    def test_parse_index_files(self, monkeypatch):
        # _parse_index_files simply concatenates the lists returned by
        # _parse_index_file
        monkeypatch.setattr(self.arl_finder, '_parse_index_file',
            lambda i: [i+'a', i+'b'])
        expected = ['aa', 'ab', 'ba', 'bb']
        assert expected == self.arl_finder._parse_index_files(['a','b'])

    def test_parse_index_file(self, monkeypatch):
        monkeypatch.setattr(io.Stream, "_open_file",
            lambda s: StringIO.StringIO(INDEX_2015110200))
        monkeypatch.setattr(self.arl_finder, "_get_file_pathname",
            lambda i, n: n)
        expected = [
            {
                'file': '/storage/NWRMC/4km/2015110200/wrfout_d3.2015110100.f24-35_12hr02.arl',
                'first_hour': datetime.datetime(2015,11,2,0,0,0),
                'last_hour': datetime.datetime(2015,11,2,11,0,0)
            },
            {
                'file': '/storage/NWRMC/4km/2015110200/wrfout_d3.2015110200.f12-23_12hr01.arl',
                'first_hour': datetime.datetime(2015,11,2,12,0,0),
                'last_hour': datetime.datetime(2015,11,2,23,0,0)
            },
            {
                'file': '/storage/NWRMC/4km/2015110200/wrfout_d3.2015110200.f24-35_12hr02.arl',
                'first_hour': datetime.datetime(2015,11,3,0,0,0),
                'last_hour': datetime.datetime(2015,11,3,11,0,0)
            },
            {
                'file': '/storage/NWRMC/4km/2015110200/wrfout_d3.2015110200.f36-47_12hr03.arl',
                'first_hour': datetime.datetime(2015,11,3,12,0,0),
                'last_hour': datetime.datetime(2015,11,3,23,0,0)
            },
            {
                'file': '/storage/NWRMC/4km/2015110200/wrfout_d3.2015110200.f48-59_12hr04.arl',
                'first_hour': datetime.datetime(2015,11,4,0,0,0),
                'last_hour': datetime.datetime(2015,11,4,11,0,0)
            },
            {
                'file': '/storage/NWRMC/4km/2015110200/wrfout_d3.2015110200.f60-71_12hr05.arl',
                'first_hour': datetime.datetime(2015,11,4,12,0,0),
                'last_hour': datetime.datetime(2015,11,4,23,0,0)
            },
            {
                'file': '/storage/NWRMC/4km/2015110200/wrfout_d3.2015110200.f72-83_12hr06.arl',
                'first_hour': datetime.datetime(2015,11,5,0,0,0),
                'last_hour': datetime.datetime(2015,11,5,11,0,0)
            }
        ]
        assert expected == self.arl_finder._parse_index_file('foo')

    # TODO: test _get_file_pathnam, monkeypatching os.path.abspath,
    #    os.path.isfile, etc. appropriately

    ##
    ## Sorting and Pruning
    ##

    def test_sort_case_1(self):
        # 24 hr predictions over 2 12-hr files every 12 hours
        arl_files = [
            {
                'file': '2015010212/a',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            },
            {
                'file': '2015010100/b',
                'first_hour': datetime.datetime(2015,1,1,12,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': '2015010112/a',
                'first_hour': datetime.datetime(2015,1,1,12,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': '2015010112/b',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            },
            {
                'file': '2015010100/a',
                'first_hour': datetime.datetime(2015,1,1,0,0,0),
                'last_hour': datetime.datetime(2015,1,1,11,0,0)
            },
            {
                'file': '2015010200/b',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            },
            {
                'file': '2015010200/a',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            },
            {
                'file': '2015010212/b',
                'first_hour': datetime.datetime(2015,1,3,0,0,0),
                'last_hour': datetime.datetime(2015,1,3,11,0,0)
            }
        ]
        expected = [
            {
                'file': '2015010100/a',
                'first_hour': datetime.datetime(2015,1,1,0,0,0),
                'last_hour': datetime.datetime(2015,1,1,11,0,0)
            },
            {
                'file': '2015010112/a',
                'first_hour': datetime.datetime(2015,1,1,12,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': '2015010100/b',
                'first_hour': datetime.datetime(2015,1,1,12,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': '2015010200/a',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            },
            {
                'file': '2015010112/b',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            },
            {
                'file': '2015010212/a',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            },
            {
                'file': '2015010200/b',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            },
            {
                'file': '2015010212/b',
                'first_hour': datetime.datetime(2015,1,3,0,0,0),
                'last_hour': datetime.datetime(2015,1,3,11,0,0)
            }
        ]
        assert expected == self.arl_finder._sort(arl_files)

    def test_sort_case_2(self):
        # 48 hr predictions over 2 24-hr files every 12 hours
        arl_files = [
            {
                'file': '2015010112/b',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,3,11,0,0)
            },
            {
                'file': '2015010112/a',
                'first_hour': datetime.datetime(2015,1,1,12,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            },
            {
                'file': '2015010200/a',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            },
            {
                'file': '2015010100/b',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            },
            {
                'file': '2015010200/b',
                'first_hour': datetime.datetime(2015,1,3,0,0,0),
                'last_hour': datetime.datetime(2015,1,3,0,0,0)
            },
            {
                'file': '2015010212/a',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,3,11,0,0)
            },
            {
                'file': '2015010100/a',
                'first_hour': datetime.datetime(2015,1,1,0,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': '2015010212/b',
                'first_hour': datetime.datetime(2015,1,3,12,0,0),
                'last_hour': datetime.datetime(2015,1,4,11,0,0)
            }
        ]
        expected = [
            {
                'file': '2015010100/a',
                'first_hour': datetime.datetime(2015,1,1,0,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': '2015010112/a',
                'first_hour': datetime.datetime(2015,1,1,12,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            },
            {
                'file': '2015010200/a',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            },
            {
                'file': '2015010100/b',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            },
            {
                'file': '2015010212/a',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,3,11,0,0)
            },
            {
                'file': '2015010112/b',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,3,11,0,0)
            },
            {
                'file': '2015010200/b',
                'first_hour': datetime.datetime(2015,1,3,0,0,0),
                'last_hour': datetime.datetime(2015,1,3,0,0,0)
            },
            {
                'file': '2015010212/b',
                'first_hour': datetime.datetime(2015,1,3,12,0,0),
                'last_hour': datetime.datetime(2015,1,4,11,0,0)
            }
        ]
        assert expected == self.arl_finder._sort(arl_files)

    def test_prune_case_1(self):
        sorted_arl_files = [
            {
                'file': '2015010100/a',
                'first_hour': datetime.datetime(2015,1,1,0,0,0),
                'last_hour': datetime.datetime(2015,1,1,11,0,0)
            },
            {
                'file': '2015010112/a',
                'first_hour': datetime.datetime(2015,1,1,12,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': '2015010100/b',
                'first_hour': datetime.datetime(2015,1,1,12,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': '2015010200/a',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            },
            {
                'file': '2015010112/b',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            },
            {
                'file': '2015010212/a',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            },
            {
                'file': '2015010200/b',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            },
            {
                'file': '2015010212/b',
                'first_hour': datetime.datetime(2015,1,3,0,0,0),
                'last_hour': datetime.datetime(2015,1,3,11,0,0)
            }
        ]

        expected = copy.deepcopy(sorted_arl_files)
        assert expected == self.arl_finder._prune(sorted_arl_files,
            datetime.datetime(2015,1,12,1,0,0), datetime.datetime(2015,1,4,23,0,0))
        assert expected == self.arl_finder._prune(sorted_arl_files,
            datetime.datetime(2015,1,1,5,0,0), datetime.datetime(2015,1,3,4,0,0))

        expected = [
            {
                'file': '2015010200/a',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            },
            {
                'file': '2015010112/b',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            }
        ]
        assert expected == self.arl_finder._prune(sorted_arl_files,
            datetime.datetime(2015,1,2,2,0,0), datetime.datetime(2015,1,2,4,0,0))

    ##
    ## Determining Windows
    ##

    def test_determine_files_per_hour(self):
        arl_files = [
            {
                'file': 'c',
                'first_hour': datetime.datetime(2015,1,2,3,0,0),
                'last_hour': datetime.datetime(2015,1,2,5,0,0)
            },
            {
                'file': 'z',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,3,0,0)
            },
            {
                'file': 'd',
                'first_hour': datetime.datetime(2015,1,2,4,0,0),
                'last_hour':  datetime.datetime(2015,1,2,6,0,0)
            },
            {
                'file': 'a',
                'first_hour': datetime.datetime(2015,1,1,23,0,0),
                'last_hour': datetime.datetime(2015,1,2,1,0,0)
            }
        ]

        expected = {
            datetime.datetime(2015,1,1,23,0,0): 'a',
            datetime.datetime(2015,1,2,0,0,0): 'z',
            datetime.datetime(2015,1,2,1,0,0): 'z',
            datetime.datetime(2015,1,2,2,0,0): 'z',
            datetime.datetime(2015,1,2,3,0,0): 'c',
            datetime.datetime(2015,1,2,4,0,0): 'd',
            datetime.datetime(2015,1,2,5,0,0): 'd',
            datetime.datetime(2015,1,2,6,0,0): 'd'
        }
        assert expected == self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2015,1,1,23,0,0), datetime.datetime(2015,1,2,6,0,0))

        expected = {
            datetime.datetime(2015,1,2,1,0,0): 'z',
            datetime.datetime(2015,1,2,2,0,0): 'z',
            datetime.datetime(2015,1,2,3,0,0): 'c',
            datetime.datetime(2015,1,2,4,0,0): 'd',
        }
        assert expected == self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2015,1,2,1,0,0), datetime.datetime(2015,1,2,4,0,0))


        # With 'fewer_arl_files' option set to True

        self.arl_finder._fewer_arl_files = True

        expected = {
            datetime.datetime(2015,1,1,23,0,0): 'a',
            datetime.datetime(2015,1,2,0,0,0): 'a',
            datetime.datetime(2015,1,2,1,0,0): 'a',
            datetime.datetime(2015,1,2,2,0,0): 'z',
            datetime.datetime(2015,1,2,3,0,0): 'z',
            datetime.datetime(2015,1,2,4,0,0): 'c',
            datetime.datetime(2015,1,2,5,0,0): 'c',
            datetime.datetime(2015,1,2,6,0,0): 'd'
        }
        assert expected == self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2015,1,1,23,0,0), datetime.datetime(2015,1,2,6,0,0))

        expected = {
            datetime.datetime(2015,1,2,0,0,0): 'z', # use z since a is no longer necessary
            datetime.datetime(2015,1,2,1,0,0): 'z', # use z since a is no longer necessary
            datetime.datetime(2015,1,2,2,0,0): 'z',
            datetime.datetime(2015,1,2,3,0,0): 'z',
            datetime.datetime(2015,1,2,4,0,0): 'c'
        }
        assert expected == self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2015,1,2,0,0,0), datetime.datetime(2015,1,2,4,0,0))

    def test_determine_file_time_windows(self):
        files_per_hour = {
            datetime.datetime(2015,1,1,23,0,0): 'a',
            datetime.datetime(2015,1,2,0,0,0): 'b',
            datetime.datetime(2015,1,2,1,0,0): 'b',
            datetime.datetime(2015,1,2,2,0,0): 'b',
            datetime.datetime(2015,1,2,3,0,0): 'c',
            datetime.datetime(2015,1,2,4,0,0): 'd',
            datetime.datetime(2015,1,2,5,0,0): 'd',
            datetime.datetime(2015,1,2,6,0,0): 'd'
        }

        expected = [
            {
                'file': 'a',
                'first_hour': datetime.datetime(2015,1,1,23,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': 'b',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,2,0,0)
            },
            {
                'file': 'c',
                'first_hour': datetime.datetime(2015,1,2,3,0,0),
                'last_hour': datetime.datetime(2015,1,2,3,0,0)
            },
            {
                'file': 'd',
                'first_hour': datetime.datetime(2015,1,2,4,0,0),
                'last_hour': datetime.datetime(2015,1,2,6,0,0)
            }
        ]

        assert expected == self.arl_finder._determine_file_time_windows(
            files_per_hour)

    def test_filter_files(self):
        files = [
            {
                'file': 'a',
                'first_hour': datetime.datetime(2015,1,1,23,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': 'b',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,2,0,0)
            },
            {
                'file': 'c',
                'first_hour': datetime.datetime(2015,1,2,3,0,0),
                'last_hour': datetime.datetime(2015,1,2,3,0,0)
            },
            {
                'file': 'd',
                'first_hour': datetime.datetime(2015,1,2,4,0,0),
                'last_hour': datetime.datetime(2015,1,2,6,0,0)
            }
        ]

        n = datetime.datetime.utcnow()
        assert files == self.arl_finder._filter_files(files, None, None)
        assert files == self.arl_finder._filter_files(files, n, None)
        assert files == self.arl_finder._filter_files(files, None, n)

        expected = [
            {
                'file': 'b',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,2,0,0)
            },
            {
                'file': 'c',
                'first_hour': datetime.datetime(2015,1,2,3,0,0),
                'last_hour': datetime.datetime(2015,1,2,3,0,0)
            }
        ]
        assert expected == self.arl_finder._filter_files(files,
            datetime.datetime(2015,1,2,1,0,0), datetime.datetime(2015,1,2,3,0,0))

        expected = [
            {
                'file': 'b',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,2,0,0)
            },
            {
                'file': 'c',
                'first_hour': datetime.datetime(2015,1,2,3,0,0),
                'last_hour': datetime.datetime(2015,1,2,3,0,0)
            },
            {
                'file': 'd',
                'first_hour': datetime.datetime(2015,1,2,4,0,0),
                'last_hour': datetime.datetime(2015,1,2,6,0,0)
            }
        ]
        assert expected == self.arl_finder._filter_files(files,
            datetime.datetime(2015,1,2,1,0,0),
            datetime.datetime(2015,1,2,5,0,0))


        assert files == self.arl_finder._filter_files(files,
            datetime.datetime(2015,1,1,20,0,0),
            datetime.datetime(2015,1,2,10,0,0))

        # TODO: other cases ...


    def test_from_arl_files_to_time_windows(self):
        """Tests both _determine_file* methods
        """
        arl_files = [
            # 2015-1-1 00Z - 12 hours
            {
                'file': '2015010100/a',
                'first_hour': datetime.datetime(2015,1,1,0,0,0),
                'last_hour': datetime.datetime(2015,1,1,11,0,0)
            },
            {
                'file': '2015010100/b',
                'first_hour': datetime.datetime(2015,1,1,12,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            # 2015-1-1 12Z - 12 hours
            {
                'file': '2015010112/a',
                'first_hour': datetime.datetime(2015,1,1,12,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': '2015010112/b',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            },
            # 2015-1-2 00Z - 12 hours
            {
                'file': '2015010200/a',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            },
            {
                'file': '2015010200/b',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            },
            # 2015-1-2 12Z - 12 hours
            {
                'file': '2015010212/a',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            },
            {
                'file': '2015010212/b',
                'first_hour': datetime.datetime(2015,1,3,0,0,0),
                'last_hour': datetime.datetime(2015,1,3,11,0,0)
            }
        ]

        expected = [
            {
                'file': '2015010100/a',
                'first_hour': datetime.datetime(2015,1,1,0,0,0),
                'last_hour': datetime.datetime(2015,1,1,11,0,0)
            },
            {
                'file': '2015010112/a',
                'first_hour': datetime.datetime(2015,1,1,12,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': '2015010200/a',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            },
            {
                'file': '2015010212/a',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            },
            {
                'file': '2015010212/b',
                'first_hour': datetime.datetime(2015,1,3,0,0,0),
                'last_hour': datetime.datetime(2015,1,3,11,0,0)
            }
        ]
        actual = self.arl_finder._determine_file_time_windows(
            self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2014,12,31,0,0,0), datetime.datetime(2015,1,3,23,0,0)))
        assert  expected == actual
        # fewer_arl_files True/False should be the same here
        self.arl_finder._fewer_arl_files = True
        actual = self.arl_finder._determine_file_time_windows(
            self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2014,12,31,0,0,0), datetime.datetime(2015,1,3,23,0,0)))
        import pdb;pdb.set_trace()
        assert expected == actual

        expected = [
            {
                'file': '2015010112/a',
                'first_hour': datetime.datetime(2015,1,1,19,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': '2015010200/a',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            },
            {
                'file': '2015010212/a',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,2,15,0,0)
            }
        ]
        self.arl_finder._fewer_arl_files = False
        actual = self.arl_finder._determine_file_time_windows(
            self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2015,1,1,19,0,0), datetime.datetime(2015,1,2,15,0,0)))
        assert expected == actual
        # fewer_arl_files True/False should be the same here
        self.arl_finder._fewer_arl_files = True
        actual = self.arl_finder._determine_file_time_windows(
            self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2015,1,1,19,0,0), datetime.datetime(2015,1,2,15,0,0)))
        assert expected == actual


        # With 'fewer_arl_files' option set to True

    def test_from_arl_files_to_time_windows_overlapping(self):
        """Tests both _determine_file* methods
        """
        arl_files = [
            # 2015-1-1 00Z - 48 hours over two files
            {
                'file': '2015010100/a',
                'first_hour': datetime.datetime(2015,1,1,0,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': '2015010100/b',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            },
            # 2015-1-1 12Z - 48 hours over two files
            {
                'file': '2015010112/a',
                'first_hour': datetime.datetime(2015,1,1,12,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            },
            {
                'file': '2015010112/b',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,3,11,0,0)
            },
            # 2015-1-2 00Z - 48 hours over two files
            {
                'file': '2015010200/a',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            },
            {
                'file': '2015010200/b',
                'first_hour': datetime.datetime(2015,1,3,0,0,0),
                'last_hour': datetime.datetime(2015,1,3,0,0,0)
            },
            # 2015-1-2 12Z - 48 hours over two files
            {
                'file': '2015010212/a',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,3,11,0,0)
            },
            {
                'file': '2015010212/b',
                'first_hour': datetime.datetime(2015,1,3,12,0,0),
                'last_hour': datetime.datetime(2015,1,4,11,0,0)
            }
        ]

        expected = [

        ]
        actual = self.arl_finder._determine_file_time_windows(
            self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2014,12,31,0,0,0), datetime.datetime(2015,1,4,23,0,0)))
        assert expected == actual

        self.arl_finder._fewer_arl_files = True
        expected = [

        ]
        actual = self.arl_finder._determine_file_time_windows(
            self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2014,12,31,0,0,0), datetime.datetime(2015,1,4,23,0,0)))
        assert expected == actual

        expected = [

        ]
        self.arl_finder._fewer_arl_files = False
        actual = self.arl_finder._determine_file_time_windows(
            self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2015,1,1,19,0,0), datetime.datetime(2015,1,2,15,0,0)))
        assert expected == actual

        self.arl_finder._fewer_arl_files = True
        expected = [

        ]
        actual = self.arl_finder._determine_file_time_windows(
            self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2015,1,1,19,0,0), datetime.datetime(2015,1,2,15,0,0)))
        assert expected == actual
