#!/usr/bin/env python

"""dispersionnc.py: Provides uilities for extracting data from smoke
dispersion nc files.

@see: https://github.com/ecolell/netcdf
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

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

    def extract(self, lat, lng):
        (x,y) = self._compute_grid_indices(lat, lng)
        data = self.nc_file.getvar('PM25')
        #data = self.nc_file.obtain_variable('PM25')

        point_time_series = data[0, :, 0, x, y]

        return point_time_series


    def _compute_grid_indices(self, lat, lng):
        # TODO: Compute based on domain corner coordinate, domain resolution,
        # and lat/lng

        sw_lat, sw_lng = self._sw_corner()
        lat_res, lng_res = self._resolution()

        lat_index = 0 # compute actual value from sw_lat, lat, and lat_res
        lng_index = 0 # compute actual value from sw_lng, lng, and lng_res

        return (lat_index, lng_index)


    def _sw_corner(self):
        # TODO: the global attributes ':XORIG' and ':YORIG' seem to define the
        # SW corner of the domain  For example, the following is from executing 'ncdump -h'
        # on a smoke_dispersion.nc file:
        #  ...
        #  :XCENT = -118.300003051758 ;
        #  :YCENT = 45. ;
        #  :XORIG = -128.300003051758 ;
        #  :YORIG = 40. ;
        #  ...
        # read those values
        #
        # If this proves impossible, they can be read from summar.json and passed into this
        # class' contstructor

        yorig = 40.0 # TODO: read actual value
        xorig = -128.0 # TODO: read actual value
        return (yorig, xorig)

    def _resolution(self):
        # TODO: the global attributes ':XCELL' an ':YCELL' seem to define the
        # resolution.  For example, the following is from executing 'ncdump -h'
        # on a smoke_dispersion.nc file:
        #  ...
        #  :XCELL = 0.0399999991059303 ;
        #  :YCELL = 0.0399999991059303 ;
        #  ...
        # read those values
        #
        # If this proves impossible, they can be read from summar.json and passed into this
        # class' contstructor

        ycell = 0.4 # TODO: read actual value
        xcell = 0.4 # TODO: read actual value
        return (ycell, xcell)
