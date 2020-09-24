"""pyairfire.io"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2016, AirFire, PNW, USFS"

import logging
import os
import shutil
import tempfile

class create_working_dir(object):

    def __init__(self, working_dir=None, delete_if_no_error=False):
        self._working_dir = working_dir
        self._delete_if_no_error = delete_if_no_error

    def __enter__(self):
        self._original_dir = os.getcwd()
        if self._working_dir:
            os.makedirs(self._working_dir, exist_ok=True)
        else:
            self._working_dir = tempfile.mkdtemp()
        logging.debug('chdir to working directory %s', self._working_dir)
        os.chdir(self._working_dir)
        return self._working_dir

    def __exit__(self, e_type, value, traceback):
        logging.debug('chdir back to original directory %s', self._original_dir)
        os.chdir(self._original_dir)
        if self._delete_if_no_error and not e_type:
            try:
                logging.debug('Deleting working dir %s', self._working_dir)
                shutil.rmtree(self._working_dir)

            except Exception as e:
                logging.warn('Failed to delete working dir %s', self._working_dir)
