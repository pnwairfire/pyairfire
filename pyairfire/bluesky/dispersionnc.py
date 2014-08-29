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
        if not os.path.isfile(nc_file_pathname):
            raise RuntimeError("%s doesn't exists" % (nc_file_pathname))

        (self.nc_file, is_new) = netcdf.open(nc_file_pathname)
        self.pm25 = self.nc_file.getvar('PM25')
        self.pms5_data_set = self.pm25.group()

        self._extract_atributes()
        self._extract_times()

    ##
    ## Public Interface
    ##

    def extract(self, lat, lng):
        (x,y) = self._compute_grid_indices(lat, lng)
        point_time_series = self.pm25[0, :, 0, x, y]  # <-- how is this correct?

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

    def _extract_atributes(self):
        # The global attributes ':XORIG' and ':YORIG' seem to define the
        # SW corner of the domain, and ':XCELL' and ':YCELL' seem to define
        # the resolution. For example, the following is from
        # executing 'ncdump -h' on a PNW-4km smoke_dispersion.nc file:
        #  ...
        #  :XCENT = -118.300003051758 ;
        #  :YCENT = 45. ;
        #  :XORIG = -128.300003051758 ;
        #  :YORIG = 40. ;
        #  :XCELL = 0.0399999991059303 ;
        #  :YCELL = 0.0399999991059303 ;
        #  ...

        # lat and lng resolution
        self.lat_res = self.pms5_data_set.YCELL
        self.lng_res = self.pms5_data_set.XCELL

        # SW corner of domain
        self.sw_lat = self.pms5_data_set.YORIG
        self.sw_lng = self.pms5_data_set.XORIG

    def _extract_times(self):
        self.tflag = self.nc_file.getvar('TFLAG')
        self.times = []
        for d, t in self.tflag[0,:,0]:
            # 'd' is an integer of the form 2014238, which translates
            # to the 238th day of 2014, which is August 26th.
            # 't' is an integer reprenting 10000 times the hour of the
            # day.  Ex. 0 is midnight, 10000 is 1am, ..., 230000 is 11pm
            d = int(d) # just to make sure
            year = d / 1000
            day_of_year = d % 1000
            month = 1  # TODO: determine from day_of_year
            day = 1  # TODO: determine from day_of_year
            hour = int(t) / 10000
            self.times.append(datetime.datetime(year, month, day, hour))

    def _compute_grid_indices(self, lat, lng):

        self._ensure_lat_lng_within_domain(lat, lng)

        from IPython import embed; embed()

        lat_index = int((lat - self.sw_lat) / self.lat_res)

        # TODO: write unit tests to make sure this is correct
        adjusted_lng = (lng + 360.0) % 360
        adjusted_sw_lng = (self.sw_lng + 360.0) %30
        lng_index = int((adjusted_lng - adjusted_sw_lng) / self.lat_res)

        return (lat_index, lng_index)


    def _ensure_lat_lng_within_domain(self, lat, lng):
        # TODO: Implement.  Take into account possibility of crossing
        # international date line or the poles
        # for international dateline, add 360 to lng's and then mod 360?
        pass
