#!/usr/bin/env python

"""dispersionnc.py: Provides uilities for extracting data from smoke
dispersion nc files.

@see: https://github.com/ecolell/netcdf
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import datetime
import os

from netcdf import netcdf

__all__ = [
    'PointExtractor'
]


class PointExtractor(object):

    def __init__(self, nc_file_pathname):
        self._initialize()

    ##
    ## Public Interface
    ##

    def extract(self, lat, lng):
        (lat_index, lng_index) = self._compute_grid_indices(lat, lng)
        point_time_series = self.pm25[0, :, 0, lat_index, lng_index]  # <-- how is this correct?

        r = []
        for i in xrange(len(point_time_series)):
            r.append({
                't': float(point_time_series[i]),
                'l': self.times[i].strftime('%Y-%m-%dT%H:%M:%SZ')
            })

        return r

    ##
    ## Private Methods
    ##

    def _initialize(self):
        self._extract_pm25()
        self._extract_attributes()
        self._extract_times()

    def _extract_pm25(self):
        if not os.path.isfile(nc_file_pathname):
            raise RuntimeError("%s doesn't exist" % (nc_file_pathname))

        (self.nc_file, is_new) = netcdf.open(nc_file_pathname)
        self.pm25 = self.nc_file.getvar('PM25')
        self.pms5_data_set = self.pm25.group()

    def _extract_attributes(self):
        """Extracs the sw lat/lng and lat/lng resolution from the nc file's global
        attributes

        The global attributes ':XORIG' and ':YORIG' seem to define the
        SW corner of the domain, and ':XCELL' and ':YCELL' seem to define
        the resolution. For example, the following is from
        executing 'ncdump -h' on a PNW-4km smoke_dispersion.nc file:
         ...
         :XCENT = -118.300003051758 ;
         :YCENT = 45. ;
         :XORIG = -128.300003051758 ;
         :YORIG = 40. ;
         :XCELL = 0.0399999991059303 ;
         :YCELL = 0.0399999991059303 ;
         ...
        """

        # lat and lng resolution
        self.lat_res = self.pms5_data_set.YCELL
        self.lng_res = self.pms5_data_set.XCELL

        # SW corner of domain
        self.sw_lat = self.pms5_data_set.YORIG
        self.sw_lng = self.pms5_data_set.XORIG

        self.num_rows = self.pms5_data_set.NROWS
        self.num_cols = self.pms5_data_set.NCOLS

    def _extract_times(self):
        self.tflag = self.nc_file.getvar('TFLAG')
        self.times = []
        for d, t in self.tflag[0,:,0]:
            self.times.append(self._convert_to_datetime(d, t))

    def _convert_to_datetime(self, d, t):
        """Converts smoke dispersion time data to datetime.datetime object

        @args
         'd' -- an integer of the form 2014238, which translates to the 238th
                day of 2014, which is August 26th.
         't' -- an integer reprenting 10000 times the hour of the day.  Ex. 0
                is midnight, 10000 is 1am, ..., 230000 is 11pm
        """
        hour = int(t) / 10000
        d = int(d) # just to make sure
        year = d / 1000
        day_of_year = d % 1000
        return datetime.datetime(year,1,1,hour) +  datetime.timedelta(day_of_year-1)

    def _adjust_lng(self, lng):
        return (lng + 360.0) % 360

    def _compute_grid_indices(self, lat, lng):
        # NROWS corresponds to latitude, NCOLS corresponds to the longitude
        adjusted_lng = self._adjust_lng(lng)
        adjusted_sw_lng = self._adjust_lng(self.sw_lng)
        adjusted_ne_lng = adjusted_sw_lng + self.lng_res * self.num_cols

        ne_lat = self.sw_lat + self.lat_res * self.num_rows

        if not self.sw_lat <= lat <= ne_lat or not adjusted_sw_lng <= adjusted_lng <= adjusted_ne_lng:
            raise RuntimeError("%s/%s outside of domain" % (lat, lng))

        lat_index = int((lat - self.sw_lat) / self.lat_res)
        lng_index = int((adjusted_lng - adjusted_sw_lng) / self.lat_res)

        return (lat_index, lng_index)
