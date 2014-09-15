import datetime
import time
import timecop
import unittest

# TODO: nosetests should take crae of updating sys path appropriately; figure
#  out what's wrong
try:
    from pyairfire.bluesky.dispersionnc import PointExtractor
except:
    import os
    import sys
    root_dir = os.path.abspath(os.path.join(sys.path[0], '../../../'))
    sys.path.insert(0, root_dir)
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

class PointExtractorTest(unittest.TestCase):

    def setUp(self):
        self.pe = PointExtractor('foo')

    def test_convert_to_datetime(self):
        self.assertEqual(
            self.pe._convert_to_datetime(2014001, 200000),
            datetime.datetime(2014,1,1,20))
        self.assertEqual(
            self.pe._convert_to_datetime(2014232, 10000),
            datetime.datetime(2014,8,20,1))
        self.assertEqual(
            self.pe._convert_to_datetime(2012232, 10000),  # leap year
            datetime.datetime(2012,8,19,1))

    def test_compute_ne_corner(self):
        # TODO: case where it's entirely in western hemisphere
        self.pe.sw_lat = 40
        self.pe.lat_res = 1
        self.pe.num_rows = 15
        self.pe.sw_lng = -160
        self.pe.lng_res = 2
        self.pe.num_cols = 8
        self.pe._compute_ne_corner()
        self.assertEqual((55, -144), (self.pe.ne_lat, self.pe.ne_lng))

        # TODO: case where it's entirely in eastern hemisphere
        self.pe.sw_lat = -30
        self.pe.lat_res = 1
        self.pe.num_rows = 10
        self.pe.sw_lng = 160
        self.pe.lng_res = 1
        self.pe.num_cols = 10
        self.pe._compute_ne_corner()
        self.assertEqual((-20, 170), (self.pe.ne_lat, self.pe.ne_lng))

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

    def test_compute_grid_indices(self):
        ## Cases where domain is completely in western hemisphere
        self.pe.sw_lat = 40
        self.pe.ne_lat = 50
        self.pe.lat_res = 1
        self.pe.num_rows = 10
        self.pe.sw_lng = -160
        self.pe.ne_lng = -150
        self.pe.lng_res = 1
        self.pe.num_cols = 10
        # lat/lng outside of domain
        with self.assertRaises(RuntimeError) as r:
            self.pe._compute_grid_indices(35, -155) # south of it
        with self.assertRaises(RuntimeError) as r:
            self.pe._compute_grid_indices(45, -165) # west of it
        # lat/lng inside domain
        self.assertEqual((5, 2), self.pe._compute_grid_indices(45.23, -157.232))

        ## Cases where domain is completely in eastern hemisphere
        self.pe.sw_lat = -30
        self.pe.ne_lat = -20
        self.pe.lat_res = 1
        self.pe.num_rows = 10
        self.pe.sw_lng = 160
        self.pe.ne_lng = 170
        self.pe.lng_res = 1
        self.pe.num_cols = 10
        # lat/lng outside of domain
        with self.assertRaises(RuntimeError) as r:
            self.pe._compute_grid_indices(-35, 165) # south of it
        with self.assertRaises(RuntimeError) as r:
            self.pe._compute_grid_indices(-25, 155) # west of it
        # lat/lng inside domain
        self.assertEqual((7, 9), self.pe._compute_grid_indices(-22.23, 169.232))

        # Case where domain straddles international dateline
        self.pe.sw_lat = 30
        self.pe.ne_lat = 40
        self.pe.lat_res = 1
        self.pe.num_rows = 10
        self.pe.sw_lng = 170
        self.pe.ne_lng = -170
        self.pe.lng_res = 1
        self.pe.num_cols = 20
        # lat/lng outside of domain
        with self.assertRaises(RuntimeError) as r:
            self.pe._compute_grid_indices(25, 175) # south of it
        with self.assertRaises(RuntimeError) as r:
            self.pe._compute_grid_indices(35, 155) # west of it
        with self.assertRaises(RuntimeError) as r:
            self.pe._compute_grid_indices(35, -155) # east of it
        # lat/lng inside domain
        self.assertEqual((2, 2), self.pe._compute_grid_indices(32.0, 172.3))
        self.assertEqual((3, 18), self.pe._compute_grid_indices(33.2, -172.0))

        # Case where domain straddles GMT
        self.pe.sw_lat = 30
        self.pe.ne_lat = 40
        self.pe.lat_res = 1
        self.pe.num_rows = 10
        self.pe.sw_lng = -10
        self.pe.ne_lng = 10
        self.pe.lng_res = 1
        self.pe.num_cols = 20
        # lat/lng outside of domain
        with self.assertRaises(RuntimeError) as r:
            self.pe._compute_grid_indices(25, 0.0) # south of it
        with self.assertRaises(RuntimeError) as r:
            self.pe._compute_grid_indices(35, -12.2) # west of it
        with self.assertRaises(RuntimeError) as r:
            self.pe._compute_grid_indices(35, 14.2) # east of it
        # lat/lng inside domain
        self.assertEqual((2, 2), self.pe._compute_grid_indices(32.0, -7.23))
        self.assertEqual((3, 18), self.pe._compute_grid_indices(33.2, 8.2))


if __name__ == '__main__':
    test_main(verbose=True)
