"""pyairfire.applogging.logger

The two main purposes of this module are 1) to provide reusable logging setup
code, and 2) to maintain and provide a reference to the client app's logger
object

Bugs:
 - duplicate logging
"""

__author__      = "Joel Dubowy"

import logging
import sys
from logging import handlers

__all__ = [
    'setup_logger',
    'get_logger'
]

class DummyLogger(object):
    def __getattr__(self, name):
        def _noop(*args, **kwargs):
            pass
        return _noop

_logger = None

def setup_logger(**options):
    """setup_logging: configures logger and its handler

    Options:
     - enabled -- whether or not logging should write to handler; if not
        enabled a dummy, noop logger will be created and returned; default True
     - logger -- logger object, if already instantiated; default: uses
        logging.getLogger to get logger object
     - log_file -- file to write logs; default: write to stdout
     - log_level -- integer log level: default: logging.INFO
     - print_debug - whether or not to print out debug info; default False

    Examples:
      > from pyairfire.applogging import applogger
      > logger = applogger.setup_logger()
      > logger = applogger.setup_logger(log_file='foo.log')
      > logger = applogger.setup_logger(log_level=10) # logging.DEBUG
      > logger = applogger.setup_logger(enabled=False)
      > logger = applogger.setup_logger(print_debug=True)
    """
    global _logger

    if options.get('print_debug'):
        print " * [pyairfire.applogging.applogger] Enabled: %s" % (
            options.get('enabled', True))
        print " * [pyairfire.applogging.applogger] Log File: %s" % (
            options.get('log_file', '(None)'))
        print " * [pyairfire.applogging.applogger] Log Level: %s" % (
            options.get('log_level', '(Not Specified)'))

    if options.get('enabled', True):
        if options.get('log_file'):
            handler = handlers.RotatingFileHandler(options['log_file'], maxBytes=10000, backupCount=1)
        else:
            handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('[%(levelname)s][%(asctime)s] %(message)s'))
        _logger = options.get('logger') or logging.getLogger()
        if options.get('log_level'):
            handler.setLevel(options['log_level'])
            _logger.setLevel(options['log_level'])
        _logger.addHandler(handler)
    else:
        _logger = DummyLogger()
    return _logger

def get_logger():
    """get_logger: returns the last logger to be set up
    """
    return _logger
