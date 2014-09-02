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


def new_initialize(self):
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


    def test_adjust_lng(self):
        pass

    def test_compute_grid_indices(self):
        ## Cases where domain is completely in western hemisphere
        self.pe.sw_lat = 40
        self.pe.lat_res = 1
        self.pe.num_rows = 10
        self.pe.sw_lng = -160
        self.pe.lng_res = 1
        self.pe.num_cols = 10
        # lat/lng outside of domain
        with self.assertRaises(RuntimeError) as r:
            self.pe._compute_grid_indices(35, -155) # south of it
        with self.assertRaises(RuntimeError) as r:
            self.pe._compute_grid_indices(45, -165) # west of it
        # lat/lng inside domain
        self.assertEqual((5, 2), self.pe._compute_grid_indices(45.23, -157.232))

        # TODO: case where domain is completely in eastern hemisphere, lat/lng outside of domain
        # TODO: case where domain is completely in eastern hemisphere, lat/lng inside domain
        # TODO: case where domain straddles international dateline, lat/lng outside of domain
        # TODO: case where domain straddles international dateline, lat/lng inside domain
        # TODO: case where domain straddles international GMT, lat/lng outside of domain
        # TODO: case where domain straddles international GMT, lat/lng inside domain
        pass


if __name__ == '__main__':
    test_main(verbose=True)
