__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import datetime
from pytest import raises

# TODO: nosetests should take crae of updating sys path appropriately; figure
#  out what's wrong
try:
    from pyairfire.bluesky import merge
except:
    import os
    import sys
    root_dir = os.path.abspath(os.path.join(sys.path[0], '../../../'))
    sys.path.insert(0, root_dir)
    from pyairfire.bluesky import merge


FIRE_LOCATIONS_1 = """\
id,name,lat,lng,date_time,foo,country
12ho123,Fire A,47.12,-118.34,201405310000Z,foo,USA
dsdho123,Fire B,47.22,-118.3423,201405310000Z,foofoo,USA
sldj2343,Fire C,47.22,-118.3423,201405310000Z,oof,MX
"""
FIRE_LOCATIONS_2 = """\
id,name,lat,lng,date_time,baz,bar,country
12ho123,Fire ZZ,50.12,-112.34,201405310000Z,baz,bar,USA
sldj2343,Fire YY,42.22,-109.3423,201405310000Z,zab,rab,MX
dsdho123,Fire XX,37.22,-112.3423,201405310000Z,bazbaz,barbar,CA
"""
FIRE_LOCATIONS_3 = """\
id,name,lat,lng,date_time,bar,baz,aaa,country
sdfdsf,Fire L,44.22,-116.342,201405310000Z,bary,bazy,aaaaa,CA
"""
MERGED_ALL_FIRE_LOCATIONS = """\
aaa,bar,baz,country,date_time,foo,id,lat,lng,name
,,,USA,201405310000Z,foo,12ho123,47.12,-118.34,Fire A
,,,USA,201405310000Z,foofoo,dsdho123,47.22,-118.3423,Fire B
,,,MX,201405310000Z,oof,sldj2343,47.22,-118.3423,Fire C
,bar,baz,USA,201405310000Z,,12ho123,50.12,-112.34,Fire ZZ
,rab,zab,MX,201405310000Z,,sldj2343,42.22,-109.3423,Fire YY
,barbar,bazbaz,CA,201405310000Z,,dsdho123,37.22,-112.3423,Fire XX
aaaaa,bary,bazy,CA,201405310000Z,,sdfdsf,44.22,-116.342,Fire L
"""
MERGED_ALL_FIRE_LOCATIONS_CA_MX_ONLY = """\
aaa,bar,baz,country,date_time,foo,id,lat,lng,name
,,,MX,201405310000Z,oof,sldj2343,47.22,-118.3423,Fire C
,rab,zab,MX,201405310000Z,,sldj2343,42.22,-109.3423,Fire YY
,barbar,bazbaz,CA,201405310000Z,,dsdho123,37.22,-112.3423,Fire XX
aaaaa,bary,bazy,CA,201405310000Z,,sdfdsf,44.22,-116.342,Fire L
"""
MERGED_1_FIRE_LOCATION = """\
country,date_time,foo,id,lat,lng,name
USA,201405310000Z,foo,12ho123,47.12,-118.34,Fire A
USA,201405310000Z,foofoo,dsdho123,47.22,-118.3423,Fire B
MX,201405310000Z,oof,sldj2343,47.22,-118.3423,Fire C
"""
MERGED_1_FIRE_LOCATION_CA_MX_ONLY = """\
country,date_time,foo,id,lat,lng,name
MX,201405310000Z,oof,sldj2343,47.22,-118.3423,Fire C
"""

class TestFiresMerger():

    def setup(self):
        pass

    def _file(self, tmpdir, filename, content):
        f = tmpdir.join(filename)
        f.write(content)
        return f.strpath

    def test_merge_three(self, tmpdir, monkeypatch):
        fl1 = self._file(tmpdir, "fire_locations_1.csv", FIRE_LOCATIONS_1)
        fl2 = self._file(tmpdir, "fire_locations_2.csv", FIRE_LOCATIONS_2)
        fl3 = self._file(tmpdir, "fire_locations_3.csv", FIRE_LOCATIONS_3)
        merger = merge.FiresMerger(fl1, fl2, fl3)
        o = tmpdir.join('merged_filed.csv')
        #monkeypatch.setattr(sys.stdout, 'write', s.write)
        merger.write(o.strpath)
        assert MERGED_ALL_FIRE_LOCATIONS == o.read()

    def test_merge_three_with_country_code_whitelist(self, tmpdir, monkeypatch):
        fl1 = self._file(tmpdir, "fire_locations_1.csv", FIRE_LOCATIONS_1)
        fl2 = self._file(tmpdir, "fire_locations_2.csv", FIRE_LOCATIONS_2)
        fl3 = self._file(tmpdir, "fire_locations_3.csv", FIRE_LOCATIONS_3)
        merger = merge.FiresMerger("{}:CA,MX".format(fl1), "{}:CA,MX".format(fl2),
            "{}:CA,MX".format(fl3))
        o = tmpdir.join('merged_filed.csv')
        #monkeypatch.setattr(sys.stdout, 'write', s.write)
        merger.write(o.strpath)
        assert MERGED_ALL_FIRE_LOCATIONS_CA_MX_ONLY == o.read()


    def test_merge_one(self, tmpdir, monkeypatch):
        fl1 = self._file(tmpdir, "fire_locations_1.csv", FIRE_LOCATIONS_1)
        merger = merge.FiresMerger(fl1)
        o = tmpdir.join('merged_filed.csv')
        #monkeypatch.setattr(sys.stdout, 'write', s.write)
        merger.write(o.strpath)
        assert MERGED_1_FIRE_LOCATION == o.read()

    def test_merge_one_with_country_code_whitelist(self, tmpdir, monkeypatch):
        fl1 = self._file(tmpdir, "fire_locations_1.csv", FIRE_LOCATIONS_1)
        merger = merge.FiresMerger("{}:CA,MX".format(fl1))
        o = tmpdir.join('merged_filed.csv')
        #monkeypatch.setattr(sys.stdout, 'write', s.write)
        merger.write(o.strpath)
        assert MERGED_1_FIRE_LOCATION_CA_MX_ONLY == o.read()

if __name__ == '__main__':
    test_main(verbose=True)
