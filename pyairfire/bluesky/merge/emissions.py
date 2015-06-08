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
            a = file_set_specifier.split(';'):
            if len(a) != 2:
                raise RuntimeError("Invalid fire file specifier: %s" % (file_specifier))
            self.emissions_file = a[0]
            self.fire_file = EmissionsMerger.FireFile(a[1])

    def __init__(self, *file_sets):
        self._file_sets = [(EmissionsMerger.FileSet(fs) for fs in file_sets]
        self._merge()

    def _merge(self):
        self._fire_headers = None
        self._emissions_headers = None
        self._fires = []
        self._emissions = []
        for file_set in self._file_sets:
            fires = self._process_fire_file(file_set.fire_file)
            emissions = self._process_emissions_file(file_set.emissions_file,
                set([fire['id'] for fire in fires])
            self._fires.extend(fires)
            self._emissions.extend(emissions)

    def _process_emissions_file(self, f, fire_ids):
        pass
        # rows = []
        # with open(f.file_name, 'r') as input_file:
        #     headers = []
        #     for row in csv.reader(input_file):
        #         if not headers:
        #             headers = [e.strip(' ') for e in row]
        #             if not self._headers:
        #                 self._headers = headers
        #             else:
        #                 self._headers.extend(sorted(set(headers).difference(self._headers)))
        #             headers = dict([(headers[i], i) for i in xrange(len(headers))])
        #         else:
        #             if (not f.country_code_whitelist or
        #                 row[headers['country']] in f.country_code_whitelist):
        #                 rows.append({h:row[headers[h]] for h in headers})
        # return rows

    def write(self, output_file=None):
        super
        stream = open(output_file, 'w') if output_file else sys.stdout
        csvfile = csv.writer(stream, lineterminator='\n')
        csvfile.writerow(self._headers)
        for f in self._fires:
            csvfile.writerow([f.get(h, '') for h in self._headers])
