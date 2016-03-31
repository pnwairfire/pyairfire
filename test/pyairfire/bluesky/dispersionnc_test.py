__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import datetime
from pytest import raises

from pyairfire.bluesky.dispersionnc import PointExtractor


def new_initialize(self, nc_file_pathname):
    self.sw_lat = 0
    self.sw_lng = 0
    self.lat_res = 1
    self.lat_res = 1
    self.num_rows = 1
    self.num_cols = 1
    #self.pm25 = ...5-dimensional numpy array...
    #self.times = ...1D array of datetime objects
PointExtractor._initialize = new_initialize

class TestPointExtractor():

    def setup(self):
        self.pe = PointExtractor('foo')

    def test_convert_to_datetime(self):
        assert datetime.datetime(2014,1,1,20) == self.pe._convert_to_datetime(2014001, 200000)
        assert datetime.datetime(2014,8,20,1) == self.pe._convert_to_datetime(2014232, 10000)
        assert datetime.datetime(2012,8,19,1) == self.pe._convert_to_datetime(2012232, 10000)  # leap year

    def test_compute_ne_corner(self):
        # TODO: case where it's entirely in western hemisphere
        self.pe.sw_lat = 40
        self.pe.lat_res = 1
        self.pe.num_rows = 15
        self.pe.sw_lng = -160
        self.pe.lng_res = 2
        self.pe.num_cols = 8
        self.pe._compute_ne_corner()
        assert (55, -144) == (self.pe.ne_lat, self.pe.ne_lng)

        # TODO: case where it's entirely in eastern hemisphere
        self.pe.sw_lat = -30
        self.pe.lat_res = 1
        self.pe.num_rows = 10
        self.pe.sw_lng = 160
        self.pe.lng_res = 1
        self.pe.num_cols = 10
        self.pe._compute_ne_corner()
        assert (-20, 170) == (self.pe.ne_lat, self.pe.ne_lng)

        # TODO: case where it's western boundary is international dateline
        # TODO: case where it's eastern boundary is international dateline
        # TODO: case where it crosses international dateline
        # TODO: case where it crosses GMT
        # TODO: case where it's western boundary is GMT
        # TODO: case where it's eastern boundary is GMT
        # TODO: case where it crosses international dateline and GMT
        # TODO: case where it's international dateline to GMT
        # TODO: case where it's GMT to international dateline
        # TODO: case where it crosses equator
        # TODO: case where it overlaps poles

    def _compute_adjusted_corner_longitudes(self):
        # TODO: case where it's entirely in eastern hemisphere
        # TODO: case where it's entirely in western hemisphere
        # TODO: case where it's western boundary is international dateline
        # TODO: case where it's eastern boundary is international dateline
        # TODO: case where it crosses international dateline
        # TODO: case where it crosses GMT
        # TODO: case where it's western boundary is GMT
        # TODO: case where it's eastern boundary is GMT
        # TODO: case where it crosses international dateline and GMT
        # TODO: case where it's international dateline to GMT
        # TODO: case where it's GMT to international dateline
        # TODO: case where it crosses equator
        # TODO: case where it overlaps poles
        pass

    def test_adjust_lng(self):
        # TODO: cases where it's entirely in eastern hemisphere
        # TODO: cases where it's entirely in western hemisphere
        # TODO: cases where it's western boundary is international dateline
        # TODO: cases where it's eastern boundary is international dateline
        # TODO: cases where it crosses international dateline
        # TODO: cases where it crosses GMT
        # TODO: cases where it's western boundary is GMT
        # TODO: cases where it's eastern boundary is GMT
        # TODO: cases where it crosses international dateline and GMT
        # TODO: cases where it's international dateline to GMT
        # TODO: cases where it's GMT to international dateline
        # TODO: cases where it crosses equator
        # TODO: cases where it overlaps poles
        pass

    def test_compute_grid_index_ranges(self):

        def assert_output_match(expected, actual):
            for i in xrange(2):
                assert expected[i] == actual[i]
            for i in xrange(2,4):
                for j in xrange(2):
                    assert expected[i][j] == actual[i][j]

        ## Cases where domain is completely in western hemisphere
        self.pe.sw_lat = 40
        self.pe.ne_lat = 50
        self.pe.lat_res = 1
        self.pe.num_rows = 10
        self.pe.sw_lng = -160
        self.pe.ne_lng = -150
        self.pe.adjusted_sw_lng = (self.pe.sw_lng + 360.0) % 360
        self.pe.adjusted_ne_lng = (self.pe.ne_lng + 360.0) % 360
        self.pe.lng_res = 1
        self.pe.num_cols = 10
        # lat/lng outside of domain
        #self.pe._adjust_lng = lambda lng: (-155 + 360.0) % 360)
        with raises(RuntimeError) as r:
            self.pe._compute_grid_index_ranges(35, -155) # south of it
        #self.pe._adjust_lng = lambda lng: (-165 + 360.0) % 360)
        with raises(RuntimeError) as r:
            self.pe._compute_grid_index_ranges(45, -165) # west of it
        # lat/lng inside domain
        assert_output_match((5, 2, xrange(4,7), xrange(1,4)),
            self.pe._compute_grid_index_ranges(45.23, -157.232))

        ## Cases where domain is completely in eastern hemisphere
        self.pe.sw_lat = -30
        self.pe.ne_lat = -20
        self.pe.lat_res = 1
        self.pe.num_rows = 10
        self.pe.sw_lng = 160
        self.pe.ne_lng = 170
        self.pe.adjusted_sw_lng = (self.pe.sw_lng + 360.0) % 360
        self.pe.adjusted_ne_lng = (self.pe.ne_lng + 360.0) % 360
        self.pe.lng_res = 1
        self.pe.num_cols = 10
        # lat/lng outside of domain
        with raises(RuntimeError) as r:
            self.pe._compute_grid_index_ranges(-35, 165) # south of it
        with raises(RuntimeError) as r:
            self.pe._compute_grid_index_ranges(-25, 155) # west of it
        # lat/lng inside domain
        assert_output_match((7, 8, xrange(6,9), xrange(7,10)),
            self.pe._compute_grid_index_ranges(-22.23, 168.232))

        # Case where domain straddles international dateline
        self.pe.sw_lat = 30
        self.pe.ne_lat = 40
        self.pe.lat_res = 1
        self.pe.num_rows = 10
        self.pe.sw_lng = 170
        self.pe.ne_lng = -170
        self.pe.adjusted_sw_lng = (self.pe.sw_lng + 360.0) % 360
        self.pe.adjusted_ne_lng = (self.pe.ne_lng + 360.0) % 360
        self.pe.lng_res = 1
        self.pe.num_cols = 20
        # lat/lng outside of domain
        with raises(RuntimeError) as r:
            self.pe._compute_grid_index_ranges(25, 175) # south of it
        with raises(RuntimeError) as r:
            self.pe._compute_grid_index_ranges(35, 155) # west of it
        with raises(RuntimeError) as r:
            self.pe._compute_grid_index_ranges(35, -155) # east of it
        # lat/lng inside domain
        assert_output_match((2, 2, xrange(1,4), xrange(1,4)),
            self.pe._compute_grid_index_ranges(32.0, 172.3))
        assert_output_match((3, 18, xrange(2,5), xrange(17,20)),
            self.pe._compute_grid_index_ranges(33.2, -172.0))

        # Case where domain straddles GMT
        # NOTE: PointExtractor currently doesn't support domains that cross
        # GMT, which is why these tests fail
        self.pe.sw_lat = 30
        self.pe.ne_lat = 40
        self.pe.lat_res = 1
        self.pe.num_rows = 10
        self.pe.sw_lng = -10
        self.pe.ne_lng = 10
        self.pe.adjusted_sw_lng = (self.pe.sw_lng + 360.0) % 360
        self.pe.adjusted_ne_lng = (self.pe.ne_lng + 360.0) % 360
        self.pe.lng_res = 1
        self.pe.num_cols = 20
        # lat/lng outside of domain
        with raises(RuntimeError) as r:
            self.pe._compute_grid_index_ranges(25, 0.0) # south of it
        with raises(RuntimeError) as r:
            self.pe._compute_grid_index_ranges(35, -12.2) # west of it
        with raises(RuntimeError) as r:
            self.pe._compute_grid_index_ranges(35, 14.2) # east of it
        # lat/lng inside domain
        assert_output_match((2, 2, xrange(1,4), xrange(1,4)),
            self.pe._compute_grid_index_ranges(32.0, -7.23))
        assert_output_match((3, 18, xrange(2,5), xrange(17,20)),
            self.pe._compute_grid_index_ranges(33.2, 8.2))

        # TODO: case where lat,lng is SW corner grid cell
        # TODO: case where lat,lng is NW corner grid cell
        # TODO: case where lat,lng is NE corner grid cell
        # TODO: case where lat,lng is SE corner grid cell
        # TODO: case where lat,lng is on W side, not corner
        # TODO: case where lat,lng is on N side, not corner
        # TODO: case where lat,lng is on E side, not corner
        # TODO: case where lat,lng is on S side, not corner


if __name__ == '__main__':
    test_main(verbose=True)
