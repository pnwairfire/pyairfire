#!/usr/bin/env python

"""dispersionnc.py: Provides uilities for extracting data from smoke
dispersion nc files.
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

#from netcdf import netcdf

__all__ = [
    'PointExtractor'
]


class PointExtractor(object):

    def __init__(self, nc_file_pathname):
        #self.nc_file = netcdf.open(nc_file_pathname)
        pass

    def extract(self, lat, lng):
        import pdb;pdb.set_trace()
        raise NotImplementedError