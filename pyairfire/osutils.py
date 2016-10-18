"""pyairfire.io"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2016, AirFire, PNW, USFS"

import logging
import os
import tempfile

class create_working_dir(object):

    def __init__(self, working_dir=None):
        self._working_dir = working_dir

    def __enter__(self):
        self._original_dir = os.getcwd()
        if self._working_dir:
            os.makedirs(self._working_dir, exist_ok=True)
        else:
            self._working_dir = tempfile.mkdtemp()
        logging.debug('chdir to working directory %s', self._working_dir)
        os.chdir(self._working_dir)
        return self._working_dir

    def __exit__(self, type, value, traceback):
        logging.debug('chdir back to original directory %s', self._original_dir)
        os.chdir(self._original_dir)
        # TODO:if it was a temp dir, delete self._working_dir or just let os
        #   clean it up?  If delete, we'd need to refactor to keep track of
        #   whether self._working_dir was passed in or not
