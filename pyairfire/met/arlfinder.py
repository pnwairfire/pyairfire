"""pyairfire.met.arlfinder

This module finds arl met data files for a particular domain and time window.

Arl index files have a fairly standard format, but do differ in some ways.
For example, sometimes the list files are names only, sometimes they're
abslute paths, and sometimes they're filenames with a leading '/' (where
the leading '/' should be ignored.)

Example index file contents

$ cat /DRI_2km/2015110300/arl12hrindex.csv
filename,start,end,interval
wrfout_d3.2015110300.f00-11_12hr01.arl,2015-11-03 00:00:00,2015-11-03 11:00:00,12
wrfout_d3.2015110300.f12-23_12hr02.arl,2015-11-03 12:00:00,2015-11-03 23:00:00,12
wrfout_d3.2015110300.f24-35_12hr03.arl,2015-11-04 00:00:00,2015-11-04 11:00:00,12
wrfout_d3.2015110300.f36-47_12hr04.arl,2015-11-04 12:00:00,2015-11-04 23:00:00,12
wrfout_d3.2015110300.f48-59_12hr05.arl,2015-11-05 00:00:00,2015-11-05 11:00:00,12
wrfout_d3.2015110300.f60-71_12hr06.arl,2015-11-05 12:00:00,2015-11-05 23:00:00,12

$ cat /DRI_6km/2015110300/arl12hrindex.csv
filename,start,end,interval
wrfout_d2.2015110300.f00-11_12hr01.arl,2015-11-03 00:00:00,2015-11-03 11:00:00,12
wrfout_d2.2015110300.f12-23_12hr02.arl,2015-11-03 12:00:00,2015-11-03 23:00:00,12
wrfout_d2.2015110300.f24-35_12hr03.arl,2015-11-04 00:00:00,2015-11-04 11:00:00,12
wrfout_d2.2015110300.f36-47_12hr04.arl,2015-11-04 12:00:00,2015-11-04 23:00:00,12
wrfout_d2.2015110300.f48-59_12hr05.arl,2015-11-05 00:00:00,2015-11-05 11:00:00,12
wrfout_d2.2015110300.f60-71_12hr06.arl,2015-11-05 12:00:00,2015-11-05 23:00:00,12

$ cat /bluesky/data/NAM/2015110300/NAM36_ARL_2015110300_index.csv
filename,start,end,interval
/bluesky/met/NAM/ARL/2015/11/nam_forecast-2015110300_00-36hr.arl,2015-11-03 00:00:00,2015-11-04 12:00:00,36

$ cat /bluesky/data/NAM/2015110300/NAM84_ARL_2015110300_index.csv
filename,start,end,interval
/bluesky/met/NAM/ARL/2015/11/nam_forecast-2015110300_00-84hr.arl,2015-11-03 00:00:00,2015-11-06 12:00:00,84

$ cat /bluesky/data/GFS/2015110300/GFS192_ARL_index.csv
filename,start,end,interval
/bluesky/data/gfs/2015110300/gfs_forecast-2015110300_000-192hr.arl,2015-11-03 00:00:00,2015-11-11 00:00:00,192

$ cat /bluesky/data/NAM4km/2015110300/nam4km_arlindex.csv
filename,start,end,interval
/hysplit.t00z.namsf00.CONUS,2015-11-03 01:00:00,2015-11-03 06:00:00,6
/hysplit.t00z.namsf06.CONUS,2015-11-03 07:00:00,2015-11-03 12:00:00,6
/hysplit.t00z.namsf12.CONUS,2015-11-03 13:00:00,2015-11-03 18:00:00,6
/hysplit.t00z.namsf18.CONUS,2015-11-03 19:00:00,2015-11-04 00:00:00,6

$ cat /storage/NWRMC/4km/2015102900/arl12hrindex.csv
filename,start,end,interval
/storage/NWRMC/4km/2015102900/wrfout_d3.2015102800.f24-35_12hr02.arl,2015-10-29 00:00:00,2015-10-29 11:00:00,12
/storage/NWRMC/4km/2015102900/wrfout_d3.2015102900.f12-23_12hr01.arl,2015-10-29 12:00:00,2015-10-29 23:00:00,12
/storage/NWRMC/4km/2015102900/wrfout_d3.2015102900.f24-35_12hr02.arl,2015-10-30 00:00:00,2015-10-30 11:00:00,12
/storage/NWRMC/4km/2015102900/wrfout_d3.2015102900.f36-47_12hr03.arl,2015-10-30 12:00:00,2015-10-30 23:00:00,12
/storage/NWRMC/4km/2015102900/wrfout_d3.2015102900.f48-59_12hr04.arl,2015-10-31 00:00:00,2015-10-31 11:00:00,12
/storage/NWRMC/4km/2015102900/wrfout_d3.2015102900.f60-71_12hr05.arl,2015-10-31 12:00:00,2015-10-31 23:00:00,12
/storage/NWRMC/4km/2015102900/wrfout_d3.2015102900.f72-83_12hr06.arl,2015-11-01 00:00:00,2015-11-01 11:00:00,12

$ cat /storage/NWRMC/1.33km/2015110300/arl12hrindex.csv
filename,start,end,interval
/storage/NWRMC/1.33km/2015110300/wrfout_d4.2015110200.f24-35_12hr02.arl,2015-11-03 00:00:00,2015-11-03 11:00:00,12
/storage/NWRMC/1.33km/2015110300/wrfout_d4.2015110300.f12-23_12hr01.arl,2015-11-03 12:00:00,2015-11-03 23:00:00,12
/storage/NWRMC/1.33km/2015110300/wrfout_d4.2015110300.f24-35_12hr02.arl,2015-11-04 00:00:00,2015-11-04 11:00:00,12
/storage/NWRMC/1.33km/2015110300/wrfout_d4.2015110300.f36-47_12hr03.arl,2015-11-04 12:00:00,2015-11-04 23:00:00,12
/storage/NWRMC/1.33km/2015110300/wrfout_d4.2015110300.f48-59_12hr04.arl,2015-11-05 00:00:00,2015-11-05 11:00:00,12

$ cat /storage/NWRMC/4km/2015110300/arl12hrindex.csv
filename,start,end,interval
/storage/NWRMC/4km/2015110300/wrfout_d3.2015110200.f24-35_12hr02.arl,2015-11-03 00:00:00,2015-11-03 11:00:00,12
/storage/NWRMC/4km/2015110300/wrfout_d3.2015110300.f12-23_12hr01.arl,2015-11-03 12:00:00,2015-11-03 23:00:00,12
/storage/NWRMC/4km/2015110300/wrfout_d3.2015110300.f24-35_12hr02.arl,2015-11-04 00:00:00,2015-11-04 11:00:00,12
/storage/NWRMC/4km/2015110300/wrfout_d3.2015110300.f36-47_12hr03.arl,2015-11-04 12:00:00,2015-11-04 23:00:00,12
/storage/NWRMC/4km/2015110300/wrfout_d3.2015110300.f48-59_12hr04.arl,2015-11-05 00:00:00,2015-11-05 11:00:00,12
/storage/NWRMC/4km/2015110300/wrfout_d3.2015110300.f60-71_12hr05.arl,2015-11-05 12:00:00,2015-11-05 23:00:00,12
/storage/NWRMC/4km/2015110300/wrfout_d3.2015110300.f72-83_12hr06.arl,2015-11-06 00:00:00,2015-11-06 11:00:00,12
"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2016, AirFire, PNW, USFS"

import datetime
#import glob
import logging
import os
import re

from pyairfire.data import utils as datautils
from pyairfire.datetime.parsing import parse_datetimes, parse_utc_offset
from pyairfire.io import CSV2JSON

__all__ = [
    'ArlFinder'
]

ONE_HOUR = datetime.timedelta(hours=1)
ONE_DAY = datetime.timedelta(days=1)

class ArlFinder(object):

    DEFAULT_INDEX_FILENAME_PATTERN = "arl12hrindex.csv"
    DEFAULT_MAX_DAYS_OUT = 4

    def __init__(self, met_root_dir, **config):
        """Constructor

        args:
         - met_root_dir -- restrict search to files under this dir

        config options:
         - index_filename_pattern -- index file name pattern to search for;
            default: 'arl12hrindex.csv'
         - max_days_out -- max number of days out predicted in met data
         - ignore_pattern -- path pattern to ignore when looking for arl
            index files; e.g. '/MOVED/'
         - fewer_arl_files -- sacrifice recency of data for fewer numer of files

        e.g. fewer_arl_files:
          Suppose there's one arl file with 84 hours starting at
          2015-08-01T00:00:00, and another with 84 hours starting at
          2015-08-01T12:00:00. And supposed you're doing a 24 hour run starting
          at 2015-08-01T00:00:00.  With fewer_arl_files set to True,
          you'll get the one arl file starting at 00Z, to be used for all 24
          hours.  With fewer_arl_files not set or set to False, you'll get
          the arl file starting at 00Z for the first 12 hours and the arl file
          starting at 12Z for the second 12 hours. So, with fewer_arl_files set
          to True, you're missing out on more recent data from 12Z-23Z.
          (The reason for supporting this option is because HYSPLIT sometimes
          fails when you specify two arl files with overlapping times)

        TODO: rename 'fewer_arl_files' option as 'minimize_num_files',
          'no_overlaps', 'minimize_overlaps', or something else.
        """
        # make sure met_root_dir is an existing directory
        try:
            # TODO: make sure os.path.isdir prptects against injects attacks
            #  Ex:  os.path.isdir('/ && rm -rf /')
            #  I tested on OSX and it worked safely, but not sure about other
            #  platforms
            if not met_root_dir or not os.path.isdir(met_root_dir):
                raise ValueError("{} is not a valid directory".format(met_root_dir))
        except TypeError:
            raise ValueError("{} is not a valid directory".format(met_root_dir))
        self._met_root_dir = met_root_dir
        self._index_filename_matcher = re.compile(
            config.get("index_filename_pattern") or
            self.DEFAULT_INDEX_FILENAME_PATTERN)
        logging.debug("Looking for index filenames mathing pattern '%s'",
            self._index_filename_matcher.pattern)
        self._max_days_out = (self.DEFAULT_MAX_DAYS_OUT
            if config.get("max_days_out") is None else int(config["max_days_out"]))
        self._ignore_matcher = (config.get('ignore_pattern')
            and re.compile('.*{}.*'.format(config['ignore_pattern'])))
        self._fewer_arl_files = not not config.get('fewer_arl_files')

    def find(self, start, end):
        """finds met data spanning start/end time window

        args:
         - start -- UTC start of time window
         - end -- UTC end of time window

        This method searches for all arl met files under self._met_root_dir
        with data spanning the given time window and determines which file
        to use for each hour in the window.  The goal is to use the most
        recent met data for any given hour.  It returns a dict containing
        a list of file objects, each containing a datetime range with the arl file
        to use for each range
        Ex.
               {
                   "files": [
                       {
                           "file": "/DRI_6km/2014052912/wrfout_d2.2014052912.f00-11_12hr01.arl",
                           "first_hour": "2014-05-29T12:00:00",
                           "last_hour": "2014-05-29T23:00:00"
                       },
                       {
                           "file": "/DRI_6km/2014053000/wrfout_d2.2014053000.f00-11_12hr01.arl",
                           "first_hour": "2014-05-30T00:00:00",
                           "last_hour": "2014-05-30T11:00:00"
                       }
                   ],
               }

        TODO: extract grid information as well (boundary, spacing, domain),
          and include in return object.
          Ex.
               {
                   "files": [
                        ...
                    ],
                    "grid": {
                        "spacing": 6.0,
                        "boundary": {
                            "ne": {
                                "lat": 45.25,
                                "lng": -106.5
                            },
                            "sw": {
                                "lat": 27.75,
                                "lng": -131.5
                            }
                        }
                    }
                }
          where 'domain' would be set to 'LatLon' if spacing is in degrees
        """
        if not start or not end:
            raise ValueError(
                'Start and end times must be defined to find arl data')

        date_matcher = self._create_date_matcher(start, end)
        index_files = self._find_index_files(date_matcher)
        arl_files = self._parse_index_files(index_files)
        files_per_hour = self._determine_files_per_hour(arl_files, start, end)
        files = self._determine_file_time_windows(files_per_hour)
        files = self._filter_files(files, start, end)
        files = datautils.format_datetimes(files)

        return {'files': files}

    ##
    ## Finding Index Files
    ##

    # TODO: add '$' after date?
    ALL_DATE_MATCHER = re.compile('.*\d{10}')

    def _create_date_matcher(self, start, end):
        """Returns a compiled regex object that matches %Y%m%d date strings
        for all dates between start and end, plus N days prior.  If neither
        start nor end is specified, all dates will be matched

        The N days prior are included because met data timestamped with any
        particular date actually predicts N days out, where N varies by domain.
        The default is 4 days out, and is customizeable with this class'
        'max_days_out' config setting.
        """
        # By this point start and end will either both be defined or not
        if start and end:
            num_days = (end.date()-start.date()).days
            dates_to_match = [start + ONE_DAY*i
                for i in range(-self._max_days_out, num_days+1)]
            date_matcher = re.compile(".*({})".format(
                '|'.join([dt.strftime('%Y%m%d') for dt in dates_to_match])))

        else:
            date_matcher = self.ALL_DATE_MATCHER

        logging.debug('date matcher pattern: {}'.format(date_matcher.pattern))
        return date_matcher

    def _find_index_files(self, date_matcher):
        """Searches for index files under dir

        Example index file locations:

            /DRI_2km/2015110300/arl12hrindex.csv
            /DRI_6km/2015110300/arl12hrindex.csv
            /bluesky/data/NAM/2015110300/NAM36_ARL_2015110300_index.csv
            /bluesky/data/NAM/2015110300/NAM84_ARL_2015110300_index.csv
            /bluesky/data/GFS/2015110300/GFS192_ARL_index.csv
            /bluesky/data/NAM4km/2015110300/nam4km_arlindex.csv
            /storage/NWRMC/4km/2015102900/arl12hrindex.csv
            /storage/NWRMC/1.33km/2015110300/arl12hrindex.csv
            /storage/NWRMC/4km/2015110300/arl12hrindex.csv
        """
        index_files = []
        for root, dirs, files in os.walk(self._met_root_dir):
            #logging.debug('Root: {}'.format(root))
            if date_matcher.match(root) and (not self._ignore_matcher or
                    not self._ignore_matcher.match(root)):
                for f in files:
                    if self._index_filename_matcher.match(f): #(os.path.basename(f)):
                        pathname = os.path.join(root, f)
                        logging.debug('found index file: {}'.format(pathname))
                        index_files.append(pathname)
        logging.debug('Found {} index files'.format(len(index_files)))
        return index_files

    ##
    ## Parsing Index Files
    ##

    def _parse_index_files(self, index_files):
        """Iterates through arl index files, iterating each

        args:
         - index_files -- list of index file names
        """
        arl_files = []
        for f in index_files:
            #logging.debug(files_per_hour)
            arl_files.extend(self._parse_index_file(f))
        return arl_files

    def _parse_index_file(self, index_file):
        """Parses arl index files, extracting each arl file with its start
        hour and last our

        args:
         - files_per_hour -- lists which met file to use for each hour
         - index_file -- pathname of index file to parse
        """
        arl_files = []
        for row in CSV2JSON(input_file=index_file)._load():
            tw = parse_datetimes(row, 'start', 'end')
            f = self._get_file_pathname(index_file, row['filename'])
            if f:
                arl_files.append(
                    dict(file=f, first_hour=tw['start'], last_hour=tw['end']))
        return arl_files

    def _get_file_pathname(self, index_file, name):
        """Returns absolute pathname of arl file listed in the index file

        args:
         - index_file -- index file listing arl file
         - name -- name of arl file, as listed in index file

        There are various possibilties for 'name':
         - it's simply the name (no path) of a file
             -> see if exists in the dir containing the index file
         - it's a relative path
             -> see if it exists relative to the dir containing the index file
         - it's an absolute path
             -> see if it exists in the specified dir, or
             -> see if it exists in the dir containing the index file
                (If the met dir is on a drive mounted from another server,
                it's possible that its absolute path is different on the
                remote server. If so, it's worth checking if the arl file
                is in the same dir as the index file, since it's likely
                in that dir.)
        """
        logging.debug('Checking existence of arl file %s', name)
        index_file_dir = os.path.dirname(index_file)
        arl_dir, arl_name = os.path.split(name)
        if arl_dir:
            # See if 'name' is an an absolute pathname that exists
            if os.path.isfile(name):
                logging.debug('Found arl file (abs path) %s', name)
                return name

            # At this point, 'name' is either an absolute pathname that
            # does not exist, or it's a relative pathname.  If it's an
            # absolute path, the following call to os.path.join will
            # return 'name' itself (not the concatenation of
            # index_file_dir and name).  If that's the case (i.e. if
            # new_name == name), then we'll skip the subsequent call
            # call to os.path.isfile, which would be redundant.
            new_name = os.path.join(index_file_dir, name)
            if new_name != name and os.path.isfile(new_name):
                logging.debug('Found arl file (rel path) %s', new_name)
                return new_name

            # At this point, 'name' does not exist, either as an absolute
            # or relative pathname. So, we'll see if the
            # file exists in the dir containing the index file
            name = arl_name

        # At this point, either no path was specified, or the file
        # doesn't exist in the path. Check if the file is in the dir
        # containing the index file
        name = os.path.join(index_file_dir, name)
        if os.path.isfile(name):
            logging.debug('Found arl file (name) %s', name)
            return name

        # TODO: should we raise an exception, or just let the returned
        # None value indicate that the file wasn't found?
        # raise ValueError("Can't find arl file {} listed in {}".format(
        #     name, index_file))

    ##
    ## Mapping hours to arl files and vice versa
    ##

    def _prune(self, arl_files, start, end):
        num_early_enough = len([f for f in arl_files if f['first_hour'] <= start])
        num_late_enough = len([f for f in arl_files if f['last_hour'] >= end])
        s_idx = max(num_early_enough - 1, 0)
        num_files = len(arl_files)
        e_idx = min(num_files, num_files - num_late_enough + 1)
        if s_idx == e_idx:
            e_idx += 1
        return sorted(arl_files, key=lambda f: f['first_hour'])[s_idx: e_idx]

    def _determine_files_per_hour(self, arl_files, start, end):
        """Determines which arl file to use for each hour in the time window.

        If self._fewer_arl_files isn't specified, this method picks the most
        recent data for each hour.  If self._fewer_arl_files is True, on the
        other hand, the goal is to use as few arl files as possible, in which
        case this method uses each arl file for as long as it can.

        File recency is determined by looking at the first hours - more recent
        files (i.e. more up to date meteorology) will have more recent first hour.
        """
        if self._fewer_arl_files:
            arl_files = self._prune(arl_files, start, end)
        files_per_hour = {}
        for f_dict in sorted(arl_files, key=lambda f: f['first_hour']):
            dt = max(f_dict['first_hour'], start)
            while dt <= min(f_dict['last_hour'], end):
                if not files_per_hour.get(dt) or not self._fewer_arl_files:
                    files_per_hour[dt] = f_dict
                dt += ONE_HOUR
        return {dt: f['file'] for dt, f in files_per_hour.items()}

    def _determine_file_time_windows(self, files_per_hour):
        """Determines time windows for which each arl file should be used.

        Note: Assumes ...
        """
        files = []
        for dt, f in sorted(files_per_hour.items(), key=lambda e: e[0]):
            if (not files or (dt - files[-1]['last_hour']) > ONE_HOUR or
                    files[-1]['file'] != f):
                files.append({'file': f, 'first_hour':dt, 'last_hour': dt})
            else:
                files[-1]['last_hour'] = dt
        return files

    ##
    ## Filtering and Formating
    ##

    def _filter_files(self, files, start, end):
        # By this point start and end will either both be defined or not
        if not (start and end):
            return files

        def in_tw(t):
            return t >= start and t <= end

        return [
            f for f in files if in_tw(f['first_hour']) or in_tw(f['last_hour'])
        ]
