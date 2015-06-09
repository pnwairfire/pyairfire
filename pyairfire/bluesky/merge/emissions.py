"""pyairfire.bluesky.merge.emissions

TODO: write unit tests
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import csv
import sys

from .fires import FiresMerger

# TODO: pull out any reusable code into common module, to be shared with
# emissions.py

class EmissionsMerger(FiresMerger):

    class FileSet(object):
        def __init__(self, file_set_specifier):
            a = file_set_specifier.split(':')
            if len(a) not in (2,3):
                raise RuntimeError("Invalid file set specifier: %s" % (file_set_specifier))
            self.emissions_file = EmissionsMerger.FileSpecifier(a[0])
            self.fire_file = EmissionsMerger.FileSpecifier(':'.join(a[1:]))

    def __init__(self, *file_sets):
        self._file_sets = [EmissionsMerger.FileSet(fs) for fs in file_sets]
        self._merge()

    def _merge(self):
        """Overrides FiresMerger._merge
        """
        self._fire_headers = None
        self._emissions_headers = None
        self._fires = []
        self._emissions = []
        for file_set in self._file_sets:
            fires = self._process_file(file_set.fire_file)
            emissions = self._process_file(file_set.emissions_file,
                set([fire['id'] for fire in fires]))
            self._fires.extend(fires)
            self._emissions.extend(emissions)

    def write(self, emissions_file, fire_locations_file):
        FiresMerger(self).write(fire_locations_file)

        stream = open(emissions_file, 'w')
        csvfile = csv.writer(stream, lineterminator='\n')
        csvfile.writerow(self._emissions_headers)
        for f in self._emissions:
            csvfile.writerow([f.get(h, '') for h in self._emissions_headers])
