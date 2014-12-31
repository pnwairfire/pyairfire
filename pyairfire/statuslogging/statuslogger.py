"""statuslogger.py:
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import datetime
import hashlib
import json
import socket
import urllib2
import urlparse

from statuslogclient import StatusLogClient

__all__ = [
    'StatusLogger'
]

class StatusLogger(StatusLogClient):
    """Class for submitting statuses to status-logs service
    """

    def __init__(self, api_endpoint, api_key, api_secret, process, **static_fields):
        """Constructor

        Arguments:
        api_endpoint -- url to post statuses
        api_key -- api key to use status-logs service
        api_secret -- secret used in signing requests
        process -- process identifier (ex. 'BlueSky')

        Other arguments:
        static_fields -- this should contain fields that are specific to your application
        and static for the life of your process (ex. 'domain=NAM84')
        """
        super(StatusLogger, self).__init__(api_endpoint, api_key=api_key, api_secret=api_secret)
        self.process = process
        self.static_fields = static_fields
        self.machine = self._machine()

    def log(self, status, error_handler=None, **extra_fields):
        """Submits status
        """
        try:
            data = {
                'status': status,
                'machine': self.machine,
                'process': self.process,
                'timestamp': datetime.datetime.utcnow().strftime(self.TIMESTAMP_FORMAT),

            }
            data.update(self.static_fields)
            data.update(extra_fields)
            url = self._signed_url()

            # TODO: send asynchrounously, if possible
            req = urllib2.Request(url, json.dumps(data))
            resp = urllib2.urlopen(req, None, self.TIMEOUT)  #.read()
        except Exception, e:
            if error_handler:
                error_handler(e)
            # Otherwise, don't do anything

    def _machine(self):
        return socket.gethostname()

    def _signed_url(self):
        path = urlparse.urlparse(self.api_endpoint).path
        query_string_params = {
            '_ts': datetime.datetime.utcnow().strftime(self.TIMESTAMP_FORMAT),
            '_k': self.api_key
        }
        query_string = '&'.join(sorted([
            "%s=%s"%(k,v) for (k,v) in query_string_params.items()
        ]))

        str_to_hash = self.api_secret.encode() + (''.join([path, query_string])).encode()
        signature = hashlib.sha256(str_to_hash).hexdigest()
        return '%s?%s&_s=%s' % (self.api_endpoint, query_string, signature)
