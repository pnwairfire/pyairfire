"""pyairfire.bluesky.merge.fires

TODO: write unit tests (using the example in the usage text of
bin/merge-fires for one test case).
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import csv
import sys

class FiresMerger(object):

    class FireFile(object):
        def __init__(self, file_specifier):
            a = file_specifier.split(':')
            if len(a) > 2:
                raise RuntimeError("Invalid fire file specifier: %s" % (file_specifier))
            self.file_name = a[0]
            if len(a) == 2:
                if not a[1]:
                    raise RuntimeError("Invalid fire file specifier: %s" % (file_specifier))
                self.country_code_whitelist = set(a[1].split(','))
            else:
                self.country_code_whitelist = None

    def __init__(self, *fire_files):
        self._fire_files = [FiresMerger.FireFile(f) for f in fire_files]
        self._merge()

    def _merge(self):
        self._fire_headers = None
        self._fires = reduce(lambda a,b: a+b,
            [self._process_fire_file(f) for f in self._fire_files])

    def _process_fire_file(self, f):
        rows = []
        with open(f.file_name, 'r') as input_file:
            headers = []
            for row in csv.reader(input_file):
                if not headers:
                    headers = [e.strip(' ') for e in row]
                    if not self._fire_headers:
                        self._fire_headers = headers
                    else:
                        self._fire_headers.extend(sorted(set(headers).difference(self._fire_headers)))
                    headers = dict([(headers[i], i) for i in xrange(len(headers))])
                else:
                    if (not f.country_code_whitelist or
                        row[headers['country']] in f.country_code_whitelist):
                        rows.append({h:row[headers[h]] for h in headers})
        return rows

    def write(self, output_file=None):
        stream = open(output_file, 'w') if output_file else sys.stdout
        csvfile = csv.writer(stream, lineterminator='\n')
        csvfile.writerow(self._fire_headers)
        for f in self._fires:
            csvfile.writerow([f.get(h, '') for h in self._fire_headers])
