"""pyairfire.bluesky.merge

TODO: write unit tests
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import csv
import sys
import abc

class MergerBase(object):

    __metaclass__ = abc.ABCMeta

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

    def _process_file(self, f, do_keep=None):
        """
        TODO: add documentation
        TODO: rename do_keep
        """
        rows = []
        with open(f.file_name, 'r') as input_file:
            headers = []
            for row in csv.reader(input_file):
                if not headers:
                    headers = [e.strip(' ') for e in row]
                    headers = dict([(headers[i], i) for i in xrange(len(headers))])
                else:
                    row_dict = {h:row[headers[h]] for h in headers}
                    if ((not f.country_code_whitelist or
                            row_dict['country'] in f.country_code_whitelist)
                            and (not do_keep or do_keep(row_dict))):
                        rows.append(row_dict)
        return rows

    def _write(self, stream, headers, rows):
        csvfile = csv.writer(stream, lineterminator='\n')
        headers = sorted(list(headers))
        csvfile.writerow(headers)
        for r in rows:
            csvfile.writerow([r.get(h, '') for h in headers])

    @abc.abstractmethod
    def write(*output_files):
        pass


class FiresMerger(MergerBase):

    def __init__(self, *fire_files):
        self._fire_files = [FiresMerger.FileSpecifier(f) for f in fire_files]
        self._merge()

    def _merge(self):
        self._fire_headers = set()
        self._fires = []
        for f in self._fire_files:
            fires = self._process_file(f)
            if fires:
                self._fire_headers |= set(fires[0].keys())
                self._fires.extend(fires)

    def write(self, output_file=None):
        stream = open(output_file, 'w') if output_file else sys.stdout
        self._write(stream, self._fire_headers, self._fires)


class EmissionsMerger(MergerBase):

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
        self._fire_headers = set()
        self._emissions_headers = set()
        self._fires = []
        self._emissions = []
        for file_set in self._file_sets:
            fires = self._process_file(file_set.fire_file)
            if fires:
                self._fires.extend(fires)
                self._fire_headers |= set(fires[0].keys())
                fire_ids = set([fire['id'] for fire in fires])
                emissions = self._process_file(file_set.emissions_file,
                    lambda row: row['fire_id'] in fire_ids)
                if emissions:
                    self._emissions.extend(emissions)
                    self._emissions_headers |= set(emissions[0].keys())

    def write(self, emissions_file, fire_locations_file):
        f_stream = open(fire_locations_file, 'w')
        self._write(f_stream, self._fire_headers, self._fires)
        e_stream = open(emissions_file, 'w')
        self._write(e_stream, self._emissions_headers, self._emissions)
