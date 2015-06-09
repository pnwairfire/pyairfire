"""pyairfire.bluesky.merge.fires

TODO: write unit tests (using the example in the usage text of
bin/merge-fires for one test case).
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import csv
import sys

class FiresMerger(object):

    class FileSpecifier(object):
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
        self._fire_files = [FiresMerger.FileSpecifier(f) for f in fire_files]
        self._merge()

    def _merge(self):
        self._fire_headers = []
        self._fires = []
        for f in self._fire_files:
            headers, fires = self._process_file(f)
            self._fire_headers.extend(headers)
            self._fires.extend(fires)

    def _process_file(self, f, do_keep=None):
        """
        TODO: add documentation
        TODO: rename do_keep
        """
        rows = []
        all_headers = None
        with open(f.file_name, 'r') as input_file:
            headers = []
            for row in csv.reader(input_file):
                if not headers:
                    headers = [e.strip(' ') for e in row]
                    if not all_headers:
                        all_headers = headers
                    else:
                        all_headers.extend(sorted(set(headers).difference(all_headers)))
                    headers = dict([(headers[i], i) for i in xrange(len(headers))])
                else:
                    row_dict = {h:row[headers[h]] for h in headers}
                    if ((not f.country_code_whitelist or
                            row_dict['country'] in f.country_code_whitelist)
                            and (not do_keep or do_keep(row_dict))):
                        rows.append(row_dict)
        return all_headers, rows

    def write(self, output_file=None):
        stream = open(output_file, 'w') if output_file else sys.stdout
        csvfile = csv.writer(stream, lineterminator='\n')
        csvfile.writerow(self._fire_headers)
        for f in self._fires:
            csvfile.writerow([f.get(h, '') for h in self._fire_headers])
