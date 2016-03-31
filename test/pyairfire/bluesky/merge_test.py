__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import datetime
from pytest import raises

from pyairfire.bluesky import merge


FIRE_LOCATIONS_1 = """\
id,event_id,name,lat,lng,date_time,foo,country
12ho123,aa,Fire A,47.12,-118.34,201405310000Z,foo,USA
dsdho123,bb,Fire B,47.22,-118.3423,201405310000Z,foofoo,USA
sldj2343,cc,Fire C,47.22,-118.3423,201405310000Z,oof,MX
"""
EVENTS_1 = """\
id,event_name,total_area
aa,nameaa,12
bb,namebb,43
cc,namecc,343
dd,namedd,i3o4
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
id,event_id,name,lat,lng,date_time,baz,bar,country
12ho123,xx,Fire ZZ,50.12,-112.34,201405310000Z,baz,bar,USA
sldj2343,yy,Fire YY,42.22,-109.3423,201405310000Z,zab,rab,MX
dsdho123,zz,Fire XX,37.22,-112.3423,201405310000Z,bazbaz,barbar,CA
"""
EVENTS_2 = """\
id,event_name,eventfoo
aa,nameaa,dsf
zz,namezz,sdfsdf
xx,namexx,sdfr
yy,nameyy,rkhw
"""
EMISSIONS_2 = """\
fire_id, foo, baz
sldj2343,foo123,baz434
sldj2343,foo232,baz345d
sdkfjsldkfj,foo343,baz434
sldj2343,foo34,baz43342
sk3r3l4k,foo345,baz4433
"""

FIRE_LOCATIONS_3 = """\
id,event_id,name,lat,lng,date_time,bar,baz,aaa,country
sdfdsf,ff,Fire L,44.22,-116.342,201405310000Z,bary,bazy,aaaaa,CA
"""
EVENTS_3 = """\
id,event_name
ff,ksdf
"""
EMISSIONS_3 = """\
sldj2343,foo34,baz43342
sk3r3l4k,foo345,baz4433
"""

MERGED_ALL_FIRE_LOCATIONS = """\
aaa,bar,baz,country,date_time,event_id,foo,id,lat,lng,name
,,,USA,201405310000Z,aa,foo,12ho123,47.12,-118.34,Fire A
,,,USA,201405310000Z,bb,foofoo,dsdho123,47.22,-118.3423,Fire B
,,,MX,201405310000Z,cc,oof,sldj2343,47.22,-118.3423,Fire C
,bar,baz,USA,201405310000Z,xx,,12ho123,50.12,-112.34,Fire ZZ
,rab,zab,MX,201405310000Z,yy,,sldj2343,42.22,-109.3423,Fire YY
,barbar,bazbaz,CA,201405310000Z,zz,,dsdho123,37.22,-112.3423,Fire XX
aaaaa,bary,bazy,CA,201405310000Z,ff,,sdfdsf,44.22,-116.342,Fire L
"""
MERGED_EVENTS_ALL_FIRE_LOCATIONS = """\
event_name,eventfoo,id,total_area
nameaa,,aa,12
namebb,,bb,43
namecc,,cc,343
namezz,sdfsdf,zz,
namexx,sdfr,xx,
nameyy,rkhw,yy,
ksdf,,ff,
"""
MERGED_EMISSIONS_ALL_FIRE_LOCATIONS = """\
bar,baz,fire_id,foo
bar3434,,12ho123,foo12
bar3,,dsdho123,foo23
bar2,,dsdho123,foo3
bar3,,sldj2343,foo545
bar46,,12ho123,foo454
,baz434,sldj2343,foo123
,baz345d,sldj2343,foo232
,baz43342,sldj2343,foo34
"""

MERGED_ALL_FIRE_LOCATIONS_CA_MX_ONLY = """\
aaa,bar,baz,country,date_time,event_id,foo,id,lat,lng,name
,,,MX,201405310000Z,cc,oof,sldj2343,47.22,-118.3423,Fire C
,rab,zab,MX,201405310000Z,yy,,sldj2343,42.22,-109.3423,Fire YY
,barbar,bazbaz,CA,201405310000Z,zz,,dsdho123,37.22,-112.3423,Fire XX
aaaaa,bary,bazy,CA,201405310000Z,ff,,sdfdsf,44.22,-116.342,Fire L
"""
MERGED_EVENTS_ALL_FIRE_LOCATIONS_CA_MX_ONLY = """\
event_name,eventfoo,id,total_area
namecc,,cc,343
namezz,sdfsdf,zz,
nameyy,rkhw,yy,
ksdf,,ff,
"""
MERGED_EMISSIONS_ALL_FIRE_LOCATIONS_CA_MX_ONLY = """\
bar,baz,fire_id,foo
bar3,,sldj2343,foo545
,baz434,sldj2343,foo123
,baz345d,sldj2343,foo232
,baz43342,sldj2343,foo34
"""

MERGED_1_FIRE_LOCATION = """\
country,date_time,event_id,foo,id,lat,lng,name
USA,201405310000Z,aa,foo,12ho123,47.12,-118.34,Fire A
USA,201405310000Z,bb,foofoo,dsdho123,47.22,-118.3423,Fire B
MX,201405310000Z,cc,oof,sldj2343,47.22,-118.3423,Fire C
"""
MERGED_EVENTS_1_FIRE_LOCATION = """\
event_name,id,total_area
nameaa,aa,12
namebb,bb,43
namecc,cc,343
"""
MERGED_EMISSIONS_1_FIRE_LOCATION = """\
bar,fire_id,foo
bar3434,12ho123,foo12
bar3,dsdho123,foo23
bar2,dsdho123,foo3
bar3,sldj2343,foo545
bar46,12ho123,foo454
"""

MERGED_1_FIRE_LOCATION_CA_MX_ONLY = """\
country,date_time,event_id,foo,id,lat,lng,name
MX,201405310000Z,cc,oof,sldj2343,47.22,-118.3423,Fire C
"""
MERGED_EVENTS_1_FIRE_LOCATION_CA_MX_ONLY = """\
event_name,id,total_area
namecc,cc,343
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
        v1 = self._file(tmpdir, "events_1.csv", EVENTS_1)
        fl2 = self._file(tmpdir, "fire_locations_2.csv", FIRE_LOCATIONS_2)
        e2 = self._file(tmpdir, "emissions_2.csv", EMISSIONS_2)
        v2 = self._file(tmpdir, "events_2.csv", EVENTS_2)
        fl3 = self._file(tmpdir, "fire_locations_3.csv", FIRE_LOCATIONS_3)
        e3 = self._file(tmpdir, "emissions_3.csv", EMISSIONS_3)
        v3 = self._file(tmpdir, "events_3.csv", EVENTS_3)
        merger = merge.EmissionsMerger(
            "{}:{}:{}".format(e1,v1,fl1),
            "{}:{}:{}".format(e2,v2,fl2),
            "{}:{}:{}".format(e3,v3,fl3)
        )
        o_f = tmpdir.join('merged_fires.csv')
        o_e = tmpdir.join('merged_emissions.csv')
        o_v = tmpdir.join('merged_events.csv')
        #monkeypatch.setattr(sys.stdout, 'write', s.write)
        merger.write(o_e.strpath, o_v.strpath, o_f.strpath)
        assert MERGED_EMISSIONS_ALL_FIRE_LOCATIONS  == o_e.read()
        assert MERGED_EVENTS_ALL_FIRE_LOCATIONS  == o_v.read()
        assert MERGED_ALL_FIRE_LOCATIONS == o_f.read()

    def test_merge_three_with_country_code_whitelist(self, tmpdir, monkeypatch):
        fl1 = self._file(tmpdir, "fire_locations_1.csv", FIRE_LOCATIONS_1)
        e1 = self._file(tmpdir, "emissions_1.csv", EMISSIONS_1)
        v1 = self._file(tmpdir, "events_1.csv", EVENTS_1)
        fl2 = self._file(tmpdir, "fire_locations_2.csv", FIRE_LOCATIONS_2)
        e2 = self._file(tmpdir, "emissions_2.csv", EMISSIONS_2)
        v2 = self._file(tmpdir, "events_2.csv", EVENTS_2)
        fl3 = self._file(tmpdir, "fire_locations_3.csv", FIRE_LOCATIONS_3)
        e3 = self._file(tmpdir, "emissions_3.csv", EMISSIONS_3)
        v3 = self._file(tmpdir, "events_3.csv", EVENTS_3)
        merger = merge.EmissionsMerger(
            "{}:{}:{}:CA,MX".format(e1,v1,fl1),
            "{}:{}:{}:CA,MX".format(e2,v2,fl2),
            "{}:{}:{}:CA,MX".format(e3,v3,fl3)
        )
        o_f = tmpdir.join('merged_fires.csv')
        o_e = tmpdir.join('merged_emissions.csv')
        o_v = tmpdir.join('merged_events.csv')
        #monkeypatch.setattr(sys.stdout, 'write', s.write)
        merger.write(o_e.strpath, o_v.strpath, o_f.strpath)
        assert MERGED_EMISSIONS_ALL_FIRE_LOCATIONS_CA_MX_ONLY  == o_e.read()
        assert MERGED_EVENTS_ALL_FIRE_LOCATIONS_CA_MX_ONLY  == o_v.read()
        assert MERGED_ALL_FIRE_LOCATIONS_CA_MX_ONLY == o_f.read()

    def test_merge_one(self, tmpdir, monkeypatch):
        fl1 = self._file(tmpdir, "fire_locations_1.csv", FIRE_LOCATIONS_1)
        e1 = self._file(tmpdir, "emissions_1.csv", EMISSIONS_1)
        v1 = self._file(tmpdir, "events_1.csv", EVENTS_1)
        merger = merge.EmissionsMerger(
            "{}:{}:{}".format(e1,v1,fl1)
        )
        o_f = tmpdir.join('merged_fires.csv')
        o_e = tmpdir.join('merged_emissions.csv')
        o_v = tmpdir.join('merged_events.csv')
        #monkeypatch.setattr(sys.stdout, 'write', s.write)
        merger.write(o_e.strpath, o_v.strpath, o_f.strpath)
        assert MERGED_EMISSIONS_1_FIRE_LOCATION  == o_e.read()
        assert MERGED_EVENTS_1_FIRE_LOCATION  == o_v.read()
        assert MERGED_1_FIRE_LOCATION == o_f.read()

    def test_merge_one_with_country_code_whitelist(self, tmpdir, monkeypatch):
        fl1 = self._file(tmpdir, "fire_locations_1.csv", FIRE_LOCATIONS_1)
        e1 = self._file(tmpdir, "emissions_1.csv", EMISSIONS_1)
        v1 = self._file(tmpdir, "events_1.csv", EVENTS_1)
        merger = merge.EmissionsMerger(
            "{}:{}:{}:CA,MX".format(e1,v1,fl1)
        )
        o_f = tmpdir.join('merged_fires.csv')
        o_e = tmpdir.join('merged_emissions.csv')
        o_v = tmpdir.join('merged_events.csv')
        #monkeypatch.setattr(sys.stdout, 'write', s.write)
        merger.write(o_e.strpath, o_v.strpath, o_f.strpath)
        assert MERGED_EMISSIONS_1_FIRE_LOCATION_CA_MX_ONLY  == o_e.read()
        assert MERGED_EVENTS_1_FIRE_LOCATION_CA_MX_ONLY  == o_v.read()
        assert MERGED_1_FIRE_LOCATION_CA_MX_ONLY == o_f.read()


if __name__ == '__main__':
    test_main(verbose=True)
