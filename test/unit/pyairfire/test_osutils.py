"""Unit tests for pyairfire.osutils"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2016, AirFire, PNW, USFS"

import json
import sys
import io
import os
import shutil
import tempfile

from pytest import raises

from pyairfire import osutils

class TestCreateWorkingDir(object):

    def setup_method(self):
        self._os_getcwd_calls = []
        self._os_makedirs_calls = []
        self._tempfile_mkdtemp_calls = []
        self._os_chdir_calls = []
        self._shutil_rmtree_calls = []

    def _os_getcwd(self, *args, **kwargs):
        self._os_getcwd_calls.append((args, kwargs))
        return '/original-dir/'

    def _os_makedirs(self, *args, **kwargs):
        self._os_makedirs_calls.append((args, kwargs))

    def _tempfile_mkdtemp(self, *args, **kwargs):
        self._tempfile_mkdtemp_calls.append((args, kwargs))
        return '/tempdir/'

    def _os_chdir(self, *args, **kwargs):
        self._os_chdir_calls.append((args, kwargs))

    def _shutil_rmtree(self, *args, **kwargs):
        self._shutil_rmtree_calls.append((args, kwargs))

    def _monkeypatch_all(self, monkeypatch):
        monkeypatch.setattr(os, "getcwd", self._os_getcwd)
        monkeypatch.setattr(os, "makedirs", self._os_makedirs)
        monkeypatch.setattr(tempfile, "mkdtemp", self._tempfile_mkdtemp)
        monkeypatch.setattr(os, "chdir", self._os_chdir)
        monkeypatch.setattr(shutil, "rmtree", self._shutil_rmtree)


    ## No errors

    def test_no_working_dir(self, monkeypatch):
        self._monkeypatch_all(monkeypatch)

        with osutils.create_working_dir():
            pass

        assert self._os_getcwd_calls == [((), {})]
        assert self._os_makedirs_calls == []
        assert self._tempfile_mkdtemp_calls == [((), {})]
        assert self._os_chdir_calls == [
            (('/tempdir/', ), {}),
            (('/original-dir/', ), {})
        ]
        assert self._shutil_rmtree_calls == []

    def test_working_dir_specified(self, monkeypatch):
        self._monkeypatch_all(monkeypatch)

        with osutils.create_working_dir(working_dir='/foo/'):
            pass

        assert self._os_getcwd_calls == [((), {})]
        assert self._os_makedirs_calls == [
            (('/foo/', ), {'exist_ok': True})
        ]
        assert self._tempfile_mkdtemp_calls == []
        assert self._os_chdir_calls == [
            (('/foo/', ), {}),
            (('/original-dir/', ), {})
        ]
        assert self._shutil_rmtree_calls == []

    def test_no_working_dir_delete_if_no_error(self, monkeypatch):
        self._monkeypatch_all(monkeypatch)

        with osutils.create_working_dir(delete_if_no_error=True):
            pass

        assert self._os_getcwd_calls == [((), {})]
        assert self._os_makedirs_calls == []
        assert self._tempfile_mkdtemp_calls == [((), {})]
        assert self._os_chdir_calls == [
            (('/tempdir/', ), {}),
            (('/original-dir/', ), {})
        ]
        assert self._shutil_rmtree_calls == [
            (('/tempdir/', ), {})
        ]

    def test_working_dir_specified_delete_if_no_error(self, monkeypatch):
        self._monkeypatch_all(monkeypatch)

        with osutils.create_working_dir(working_dir='/foo/', delete_if_no_error=True):
            pass

        assert self._os_getcwd_calls == [((), {})]
        assert self._os_makedirs_calls == [
            (('/foo/', ), {'exist_ok': True})
        ]
        assert self._tempfile_mkdtemp_calls == []
        assert self._os_chdir_calls == [
            (('/foo/', ), {}),
            (('/original-dir/', ), {})
        ]
        assert self._shutil_rmtree_calls == [
            (('/foo/', ), {})
        ]


    ## With errors

    def test_error_no_working_dir(self, monkeypatch):
        self._monkeypatch_all(monkeypatch)

        try:
            with osutils.create_working_dir():
                123 / 0
        except:
            pass

        assert self._os_getcwd_calls == [((), {})]
        assert self._os_makedirs_calls == []
        assert self._tempfile_mkdtemp_calls == [((), {})]
        assert self._os_chdir_calls == [
            (('/tempdir/', ), {}),
            (('/original-dir/', ), {})
        ]
        assert self._shutil_rmtree_calls == []

    def test_error_working_dir_specified(self, monkeypatch):
        self._monkeypatch_all(monkeypatch)

        try:
            with osutils.create_working_dir(working_dir='/foo/'):
                123 / 0
        except:
            pass

        assert self._os_getcwd_calls == [((), {})]
        assert self._os_makedirs_calls == [
            (('/foo/', ), {'exist_ok': True})
        ]
        assert self._tempfile_mkdtemp_calls == []
        assert self._os_chdir_calls == [
            (('/foo/', ), {}),
            (('/original-dir/', ), {})
        ]
        assert self._shutil_rmtree_calls == []

    def test_error_no_working_dir_delete_if_no_error(self, monkeypatch):
        self._monkeypatch_all(monkeypatch)

        try:
            with osutils.create_working_dir(delete_if_no_error=True):
                123 / 0
        except:
            pass

        assert self._os_getcwd_calls == [((), {})]
        assert self._os_makedirs_calls == []
        assert self._tempfile_mkdtemp_calls == [((), {})]
        assert self._os_chdir_calls == [
            (('/tempdir/', ), {}),
            (('/original-dir/', ), {})
        ]
        assert self._shutil_rmtree_calls == []  # not deleted, dur to error

    def test_error_working_dir_specified_delete_if_no_error(self, monkeypatch):
        self._monkeypatch_all(monkeypatch)

        try:
            with osutils.create_working_dir(working_dir='/foo/', delete_if_no_error=True):
                123 / 0
        except:
            pass

        assert self._os_getcwd_calls == [((), {})]
        assert self._os_makedirs_calls == [
            (('/foo/', ), {'exist_ok': True})
        ]
        assert self._tempfile_mkdtemp_calls == []
        assert self._os_chdir_calls == [
            (('/foo/', ), {}),
            (('/original-dir/', ), {})
        ]
        assert self._shutil_rmtree_calls == []  # not deleted, dur to error
