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
EMISSIONS_1 = """\
fire_id, foo, bar
12ho123,foo12,bar3434
dsdho123,foo23,bar3
dsdho123,foo3,bar2
sldj2343,foo545,bar3
12ho123,foo454,bar46
blahblah,foo65234,bar345
sdfdsf,foo34,bar3423
"""

FIRE_LOCATIONS_2 = """\
id,name,lat,lng,date_time,baz,bar,country
12ho123,Fire ZZ,50.12,-112.34,201405310000Z,baz,bar,USA
sldj2343,Fire YY,42.22,-109.3423,201405310000Z,zab,rab,MX
dsdho123,Fire XX,37.22,-112.3423,201405310000Z,bazbaz,barbar,CA
"""
EMISSIONS_2 = """\
fire_id, foo, bar, baz
sldj2343,foo123,baz434
sldj2343,foo232,baz345d
sdkfjsldkfj,foo343,baz434
sldj2343,foo34,baz43342
sk3r3l4k,foo345,baz4433
"""

FIRE_LOCATIONS_3 = """\
id,name,lat,lng,date_time,bar,baz,aaa,country
sdfdsf,Fire L,44.22,-116.342,201405310000Z,bary,bazy,aaaaa,CA
"""
EMISSIONS_3 = """\
sldj2343,foo34,baz43342
sk3r3l4k,foo345,baz4433
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
MERGED_EMISSIONS_ALL_FIRE_LOCATIONS = """\
bar,baz,fire_id,foo
bar3434,,12ho123,foo12
bar3,,dsdho123,foo23
bar2,,dsdho123,foo3
bar3,,sldj2343,foo545
bar46,,12ho123,foo454
bar345,,blahblah,foo65234
bar3423,,sdfdsf,foo34
,baz434,sldj2343,foo123
,baz345d,sldj2343,foo232
,baz43342,sldj2343,foo34
"""

MERGED_ALL_FIRE_LOCATIONS_CA_MX_ONLY = """\
aaa,bar,baz,country,date_time,foo,id,lat,lng,name
,,,MX,201405310000Z,oof,sldj2343,47.22,-118.3423,Fire C
,rab,zab,MX,201405310000Z,,sldj2343,42.22,-109.3423,Fire YY
,barbar,bazbaz,CA,201405310000Z,,dsdho123,37.22,-112.3423,Fire XX
aaaaa,bary,bazy,CA,201405310000Z,,sdfdsf,44.22,-116.342,Fire L
"""
MERGED_EMISSIONS_ALL_FIRE_LOCATIONS_CA_MX_ONLY = """\
bar,baz,fire_id,foo
bar345,,blahblah,foo65234
bar3423,,sdfdsf,foo34
,baz434,sldj2343,foo123
,baz345d,sldj2343,foo232
,baz43342,sldj2343,foo34
"""

MERGED_1_FIRE_LOCATION = """\
country,date_time,foo,id,lat,lng,name
USA,201405310000Z,foo,12ho123,47.12,-118.34,Fire A
USA,201405310000Z,foofoo,dsdho123,47.22,-118.3423,Fire B
MX,201405310000Z,oof,sldj2343,47.22,-118.3423,Fire C
"""
MERGED_EMISSIONS_1_FIRE_LOCATION = """\
bar,fire_id,foo
bar3434,foo12,12ho123
bar3,dsdho123,foo23
bar2,dsdho123,foo3
bar3,sldj2343,foo545
bar46,12ho123,foo454
bar345,blahblah,foo65234
bar3423,sdfdsf,foo34
"""

MERGED_1_FIRE_LOCATION_CA_MX_ONLY = """\
country,date_time,foo,id,lat,lng,name
MX,201405310000Z,oof,sldj2343,47.22,-118.3423,Fire C
"""
MERGED_EMISSIONS_1_FIRE_LOCATION_CA_MX_ONLY = """\
bar,fire_id,foo
bar3,sldj2343,foo545
"""


class MergerTestBase(object):

    def setup(self):
        pass

    def _file(self, tmpdir, filename, content):
        f = tmpdir.join(filename)
        f.write(content)
        return f.strpath


class TestFiresMerger(MergerTestBase):

    def test_merge_three(self, tmpdir, monkeypatch):
        fl1 = self._file(tmpdir, "fire_locations_1.csv", FIRE_LOCATIONS_1)
        fl2 = self._file(tmpdir, "fire_locations_2.csv", FIRE_LOCATIONS_2)
        fl3 = self._file(tmpdir, "fire_locations_3.csv", FIRE_LOCATIONS_3)
        merger = merge.FiresMerger(fl1, fl2, fl3)
        o = tmpdir.join('merged_fires.csv')
        #monkeypatch.setattr(sys.stdout, 'write', s.write)
        merger.write(o.strpath)
        assert MERGED_ALL_FIRE_LOCATIONS == o.read()

    def test_merge_three_with_country_code_whitelist(self, tmpdir, monkeypatch):
        fl1 = self._file(tmpdir, "fire_locations_1.csv", FIRE_LOCATIONS_1)
        fl2 = self._file(tmpdir, "fire_locations_2.csv", FIRE_LOCATIONS_2)
        fl3 = self._file(tmpdir, "fire_locations_3.csv", FIRE_LOCATIONS_3)
        merger = merge.FiresMerger("{}:CA,MX".format(fl1), "{}:CA,MX".format(fl2),
            "{}:CA,MX".format(fl3))
        o = tmpdir.join('merged_fires.csv')
        #monkeypatch.setattr(sys.stdout, 'write', s.write)
        merger.write(o.strpath)
        assert MERGED_ALL_FIRE_LOCATIONS_CA_MX_ONLY == o.read()


    def test_merge_one(self, tmpdir, monkeypatch):
        fl1 = self._file(tmpdir, "fire_locations_1.csv", FIRE_LOCATIONS_1)
        merger = merge.FiresMerger(fl1)
        o = tmpdir.join('merged_fires.csv')
        #monkeypatch.setattr(sys.stdout, 'write', s.write)
        merger.write(o.strpath)
        assert MERGED_1_FIRE_LOCATION == o.read()

    def test_merge_one_with_country_code_whitelist(self, tmpdir, monkeypatch):
        fl1 = self._file(tmpdir, "fire_locations_1.csv", FIRE_LOCATIONS_1)
        merger = merge.FiresMerger("{}:CA,MX".format(fl1))
        o = tmpdir.join('merged_fires.csv')
        #monkeypatch.setattr(sys.stdout, 'write', s.write)
        merger.write(o.strpath)
        assert MERGED_1_FIRE_LOCATION_CA_MX_ONLY == o.read()


class TestEmissionsMerger(MergerTestBase):

    def test_merge_three(self, tmpdir, monkeypatch):
        fl1 = self._file(tmpdir, "fire_locations_1.csv", FIRE_LOCATIONS_1)
        e1 = self._file(tmpdir, "emissions_1.csv", EMISSIONS_1)
        fl2 = self._file(tmpdir, "fire_locations_2.csv", FIRE_LOCATIONS_2)
        e2 = self._file(tmpdir, "emissions_1.csv", EMISSIONS_2)
        fl3 = self._file(tmpdir, "fire_locations_3.csv", FIRE_LOCATIONS_3)
        e3 = self._file(tmpdir, "emissions_1.csv", EMISSIONS_3)
        merger = merge.EmissionsMerger(
            "{}:{}".format(e1,fl1),
            "{}:{}".format(e2,fl2),
            "{}:{}".format(e3,fl3)
        )
        o_f = tmpdir.join('merged_fires.csv')
        o_e = tmpdir.join('merged_emissions.csv')
        #monkeypatch.setattr(sys.stdout, 'write', s.write)
        merger.write(o_e.strpath, o_f.strpath)
        assert MERGED_EMISSIONS_ALL_FIRE_LOCATIONS  == o_e.read()
        assert MERGED_ALL_FIRE_LOCATIONS == o_f.read()

    def test_merge_three_with_country_code_whitelist(self, tmpdir, monkeypatch):
        fl1 = self._file(tmpdir, "fire_locations_1.csv", FIRE_LOCATIONS_1)
        e1 = self._file(tmpdir, "emissions_1.csv", EMISSIONS_1)
        fl2 = self._file(tmpdir, "fire_locations_2.csv", FIRE_LOCATIONS_2)
        e2 = self._file(tmpdir, "emissions_1.csv", EMISSIONS_2)
        fl3 = self._file(tmpdir, "fire_locations_3.csv", FIRE_LOCATIONS_3)
        e3 = self._file(tmpdir, "emissions_1.csv", EMISSIONS_3)
        merger = merge.EmissionsMerger(
            "{}:{}:CA,MX".format(e1,fl1),
            "{}:{}:CA,MX".format(e2,fl2),
            "{}:{}:CA,MX".format(e3,fl3)
        )
        o_f = tmpdir.join('merged_fires.csv')
        o_e = tmpdir.join('merged_emissions.csv')
        #monkeypatch.setattr(sys.stdout, 'write', s.write)
        merger.write(o_e.strpath, o_f.strpath)
        assert MERGED_EMISSIONS_ALL_FIRE_LOCATIONS_CA_MX_ONLY  == o_e.read()
        assert MERGED_ALL_FIRE_LOCATIONS_CA_MX_ONLY == o_f.read()

    def test_merge_one(self, tmpdir, monkeypatch):
        fl1 = self._file(tmpdir, "fire_locations_1.csv", FIRE_LOCATIONS_1)
        e1 = self._file(tmpdir, "emissions_1.csv", EMISSIONS_1)
        merger = merge.EmissionsMerger(
            "{}:{}".format(e1,fl1)
        )
        o_f = tmpdir.join('merged_fires.csv')
        o_e = tmpdir.join('merged_emissions.csv')
        #monkeypatch.setattr(sys.stdout, 'write', s.write)
        merger.write(o_e.strpath, o_f.strpath)
        assert MERGED_EMISSIONS_1_FIRE_LOCATION  == o_e.read()
        assert MERGED_1_FIRE_LOCATION == o_f.read()

    def test_merge_one_with_country_code_whitelist(self, tmpdir, monkeypatch):
        fl1 = self._file(tmpdir, "fire_locations_1.csv", FIRE_LOCATIONS_1)
        e1 = self._file(tmpdir, "emissions_1.csv", EMISSIONS_1)
        merger = merge.EmissionsMerger(
            "{}:{}:CA,MX".format(e1,fl1)
        )
        o_f = tmpdir.join('merged_fires.csv')
        o_e = tmpdir.join('merged_emissions.csv')
        #monkeypatch.setattr(sys.stdout, 'write', s.write)
        merger.write(o_e.strpath, o_f.strpath)
        assert MERGED_EMISSIONS_1_FIRE_LOCATION_CA_MX_ONLY  == o_e.read()
        assert MERGED_1_FIRE_LOCATION_CA_MX_ONLY == o_f.read()


if __name__ == '__main__':
    test_main(verbose=True)
