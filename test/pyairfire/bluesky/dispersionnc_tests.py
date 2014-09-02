import datetime
import time
import timecop
import unittest

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
            self.pe._convert_to_datetime(20141, 200000),
            datetime.datetime(2014,1,1,))

    def test_adjust_lng(self):
        pass

    def test_compute_grid_indices(self):
        # TODO: case where domain is completely in western hemisphere, lat/lng outside of domain
        # TODO: case where domain is completely in western hemisphere, lat/lng inside domain
        # TODO: case where domain is completely in eastern hemisphere, lat/lng outside of domain
        # TODO: case where domain is completely in eastern hemisphere, lat/lng inside domain
        # TODO: case where domain straddles international dateline, lat/lng outside of domain
        # TODO: case where domain straddles international dateline, lat/lng inside domain
        # TODO: case where domain straddles international GMT, lat/lng outside of domain
        # TODO: case where domain straddles international GMT, lat/lng inside domain
        pass

    def test_ensure_lat_lng_within_domain(self):
        # TODO: implement, somehow mocking out dependency on netCDF file
        pass


if __name__ == '__main__':
    test_main(verbose=True)
