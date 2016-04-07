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
    ## Pruning and Sorting
    ##

    def test_prune_and_sort_case_1(self):
        """Tests cases where met data is 24 hr predictions over
        two 12-hr files every 12 hours.
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
        assert expected == self.arl_finder._prune_and_sort(arl_files,
            datetime.datetime(2014,12,1,1,0,0), datetime.datetime(2015,1,4,23,0,0))
        assert expected == self.arl_finder._prune_and_sort(arl_files,
            datetime.datetime(2015,1,1,5,0,0), datetime.datetime(2015,1,3,4,0,0))

        expected = [
            {
                'file': '2015010200/a',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            }
        ]
        assert expected == self.arl_finder._prune_and_sort(arl_files,
            datetime.datetime(2015,1,2,2,0,0), datetime.datetime(2015,1,2,4,0,0))

    def test_prune_and_sort_case_2(self):
        """Tests cases where met data is 48 hr predictions over
        two 24-hr files every 12 hours.
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
                'last_hour': datetime.datetime(2015,1,3,23,0,0)
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
                'file': '2015010212/a',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,3,11,0,0)
            },
            {
                'file': '2015010200/b',
                'first_hour': datetime.datetime(2015,1,3,0,0,0),
                'last_hour': datetime.datetime(2015,1,3,23,0,0)
            },
            {
                'file': '2015010212/b',
                'first_hour': datetime.datetime(2015,1,3,12,0,0),
                'last_hour': datetime.datetime(2015,1,4,11,0,0)
            }
        ]
        assert expected == self.arl_finder._prune_and_sort(arl_files,
            datetime.datetime(2014,12,1,1,0,0), datetime.datetime(2015,1,4,23,0,0))
        assert expected == self.arl_finder._prune_and_sort(arl_files,
            datetime.datetime(2015,1,1,5,0,0), datetime.datetime(2015,1,4,4,0,0))
        assert expected == self.arl_finder._prune_and_sort(arl_files, None, None)

        expected = [
            {
                'file': '2015010200/a',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            }
        ]
        assert expected == self.arl_finder._prune_and_sort(arl_files,
            datetime.datetime(2015,1,2,2,0,0), datetime.datetime(2015,1,2,4,0,0))

    # Note: removed test for _determine_files_per_hour
    # Note: removed test for _determine_file_time_windows


class TestARLFinderWindowDetermination(object):
    """Contains higher level tests, starting with parsed file data
    and ending with file time window assignments
    """

    def setup(self):
        self.arl_finder = arlfinder.ArlFinder(tempfile.mkdtemp())

    ##
    ## Tests cases where met data is
    ##    24 hr predictions over two 12-hr files every 12 hours.
    ##

    ARL_FILES_24_HR_OVER_12HR_FILES_EVERY_12_HRS = [
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

    def test_no_overlap_larger_time_window(self):
        arl_files = copy.deepcopy(self.ARL_FILES_24_HR_OVER_12HR_FILES_EVERY_12_HRS)

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
        assert expected == actual
        assert expected == self.arl_finder._prune_and_sort(arl_files, None, None)

    def test_no_overlap_larger_time_window_fewer_arl_files(self):
        arl_files = copy.deepcopy(self.ARL_FILES_24_HR_OVER_12HR_FILES_EVERY_12_HRS)

        # fewer_arl_files True/False should be the same here as previous test
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
        self.arl_finder._fewer_arl_files = True
        actual = self.arl_finder._determine_file_time_windows(
            self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2014,12,31,0,0,0), datetime.datetime(2015,1,3,23,0,0)))
        assert expected == actual
        assert expected == self.arl_finder._prune_and_sort(arl_files, None, None)

    def test_no_overlap_restricted_time_window(self):
        arl_files = copy.deepcopy(self.ARL_FILES_24_HR_OVER_12HR_FILES_EVERY_12_HRS)

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

    def test_no_overlap_restricted_time_window_fewer_arl_files(self):
        self.arl_finder._fewer_arl_files = True

        arl_files = copy.deepcopy(self.ARL_FILES_24_HR_OVER_12_HR_FILES_EVERY_12_HRS)

        # fewer_arl_files True/False should be the same here as previous test
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

        actual = self.arl_finder._determine_file_time_windows(
            self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2015,1,1,19,0,0), datetime.datetime(2015,1,2,15,0,0)))
        assert expected == actual

        ## With 'fewer_arl_files' option set to True



    ##
    ## Tests cases where met data is
    ##    48-hr predictions over two 24-hr files every 12 hours.
    ##

    ARL_FILES_48_HR_OVER_24_HR_FILES_EVERY_12_HRS = [
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
            'last_hour': datetime.datetime(2015,1,3,23,0,0)
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

    def test_overlapping_larger_time_window(self):
        arl_files = copy.deepcopy(self.ARL_FILES_48_HR_OVER_24_HR_FILES_EVERY_12_HRS)

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
                'file': '2015010200/b',
                'first_hour': datetime.datetime(2015,1,3,0,0,0),
                'last_hour': datetime.datetime(2015,1,3,11,0,0)
            },
            {
                'file': '2015010212/b',
                'first_hour': datetime.datetime(2015,1,3,12,0,0),
                'last_hour': datetime.datetime(2015,1,4,11,0,0)
            }
        ]
        actual = self.arl_finder._determine_file_time_windows(
            self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2014,12,31,0,0,0), datetime.datetime(2015,1,4,23,0,0)))
        assert expected == actual


    def test_overlapping_larger_time_window_fewer_files(self):
        self.arl_finder._fewer_arl_files = True

        arl_files = copy.deepcopy(self.ARL_FILES_48_HR_OVER_24_HR_FILES_EVERY_12_HRS)

        expected = [
            {
                'file': '2015010100/a',
                'first_hour': datetime.datetime(2015,1,1,0,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': '2015010200/a',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            },
            {
                'file': '2015010200/b',
                'first_hour': datetime.datetime(2015,1,3,0,0,0),
                'last_hour': datetime.datetime(2015,1,3,23,0,0)
            },
            {
                'file': '2015010212/b',
                'first_hour': datetime.datetime(2015,1,4,0,0,0),
                'last_hour': datetime.datetime(2015,1,4,11,0,0)
            }

        ]
        actual = self.arl_finder._determine_file_time_windows(
            self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2014,12,31,0,0,0), datetime.datetime(2015,1,4,23,0,0)))
        assert expected == actual

    def test_overlapping_restricted_time_window(self):
        arl_files = copy.deepcopy(self.ARL_FILES_48_HR_OVER_24_HR_FILES_EVERY_12_HRS)

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

    def test_overlapping_restricted_time_window_fewer_files(self):
        self.arl_finder._fewer_arl_files = True

        arl_files = copy.deepcopy(self.ARL_FILES_48_HR_OVER_24_HR_FILES_EVERY_12_HRS)

        expected = [
            {
                'file': '2015010112/a',
                'first_hour': datetime.datetime(2015,1,1,19,0,0),
                'last_hour': datetime.datetime(2015,1,2,11,0,0)
            },
            {
                'file': '2015010212/a',
                'first_hour': datetime.datetime(2015,1,2,12,0,0),
                'last_hour': datetime.datetime(2015,1,2,15,0,0)
            },
        ]
        actual = self.arl_finder._determine_file_time_windows(
            self.arl_finder._determine_files_per_hour(arl_files,
            datetime.datetime(2015,1,1,19,0,0), datetime.datetime(2015,1,2,15,0,0)))
        assert expected == actual
