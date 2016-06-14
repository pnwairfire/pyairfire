#!/usr/bin/env python

"""dispersionnc.py: Provides uilities for extracting data from smoke
dispersion nc files.

@see: https://github.com/ecolell/netcdf
"""

__author__      = "Joel Dubowy"

import datetime
import os

from netcdf import netcdf

__all__ = [
    'PointExtractor'
]


class PointExtractor(object):
    """
    Example:
     >>> from pyairfire.bluesky.dispersionnc import PointExtractor
     >>> PointExtractor("/Users/jdubowy/Downloads/bluesky-output/smoke_dispersion-pnw-4k-2014082600.nc").extract(47.0, -122)
    """

    def __init__(self, nc_file_pathname):
        self._initialize(nc_file_pathname)

    ##
    ## Public Interface
    ##

    def extract(self, lat, lng):
        """Extracts PM2.5 levels for grid cell containing lat/lng over prediction time window

        Returns data of the form:

        {
            "grid_indices": {
                "lat": 142,   // <-- indices of grid cell containing lat/lng
                "lng": 254    // <-- containing lat/lng
            },
            "grid_index_ranges": {
                "lat": [141, 143],  //  <-- i.e. defines neighborhood
                "lng": [253, 255]   //  <-- around (142, 254)
            },
            "data": [
                {
                    "t": "2014-08-28T01:00:00Z",
                    "l": [
                        [1.0, 1.0, 2.0],    // <-- These three rows represent the pm2.5 levels
                        [1.0, 2.0, 3.0],    // <-- in the neighborhood of the lat/lng at a
                        [2.0, 3.0, 3.0]     // <-- specific moment in the time window
                    ]
                },
                ...,
                {
                    "t": "2014-08-28T23:00:00Z",
                    "l": [
                        [0.0, 0.0, 0.0],
                        [0.0, 1.0, 1.0],
                        [1.0, 1.0, 2.0]
                    ]
                }
            ]
        }

        @todo:
         - cache results
        """
        (lat_index, lng_index, lat_index_range, lng_index_range) = self._compute_grid_index_ranges(lat, lng)

        # TODO: make sure this is indexing self.pm25 correctly, given each pair
        # of lat/lng indices in the index ranges
        point_time_series = self.pm25[0, :, 0, lat_index_range[0]:lat_index_range[-1]+1, lng_index_range[0]:lng_index_range[-1]+1]

        r = {
            "grid_indices": {
                "lat": lat_index,
                "lng": lng_index
            },
            "grid_index_ranges": {
                "lat": list(lat_index_range),
                "lng": list(lng_index_range)
            },
            'data': []

        }
        for i in range(len(point_time_series)):
            r['data'].append({
                't': self.times[i].strftime('%Y-%m-%dT%H:%M:%SZ'),
                'l': [[float(e) for e in i] for i in point_time_series[i]]  #  TODO: need to cast to floats?
            })

        return r

    ##
    ## Private Methods
    ##

    def _initialize(self, nc_file_pathname):
        if not os.path.isfile(nc_file_pathname):
            raise RuntimeError("%s doesn't exist" % (nc_file_pathname))
        (self.nc_file, is_new) = netcdf.open(nc_file_pathname)

        self._extract_pm25()
        self._extract_attributes()
        self._extract_times()

    def _extract_pm25(self):
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

        # grid dimensions
        self.num_rows = self.pms5_data_set.NROWS # this corresponds to lat
        self.num_cols = self.pms5_data_set.NCOLS # this corresponds to lng

        # SW and NE corners of domain
        self.sw_lat = self.pms5_data_set.YORIG
        self.sw_lng = self.pms5_data_set.XORIG
        self._compute_ne_corner()
        self._compute_adjusted_corner_longitudes()


    def _compute_ne_corner(self):
        self.ne_lat = self.sw_lat + self.lat_res * self.num_rows
        self.ne_lng = self.sw_lng + self.lng_res * self.num_cols
        if self.ne_lat > 180.0:
            self.ne_lat -= 360.0

    def _compute_adjusted_corner_longitudes(self):
        self.adjusted_sw_lng = self._adjust_lng(self.sw_lng)
        self.adjusted_ne_lng = self.adjusted_sw_lng + self.lng_res * self.num_cols

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
        # TODO: this works for anything other than domains that cross GMT.
        # Update to handle all possible domains (namely those that cross GMT
        # and/or the international dateline)
        return (lng + 360.0) % 360

    def _compute_grid_index_ranges(self, lat, lng):
        # NROWS corresponds to latitude, NCOLS corresponds to the longitude
        adjusted_lng = self._adjust_lng(lng)

        if not self.sw_lat <= lat <= self.ne_lat or not self.adjusted_sw_lng <= adjusted_lng <= self.adjusted_ne_lng:
            raise RuntimeError("%s/%s outside of domain" % (lat, lng))

        lat_index = int((lat - self.sw_lat) / self.lat_res)
        lng_index = int((adjusted_lng - self.adjusted_sw_lng) / self.lat_res)

        lat_index_range = range(max(0, lat_index-1), min(self.num_rows, lat_index+2))
        lng_index_range = range(max(0, lng_index-1), min(self.num_cols, lng_index+2))

        return (lat_index, lng_index, lat_index_range, lng_index_range)
