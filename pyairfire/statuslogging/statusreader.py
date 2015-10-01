"""pyairfire.statuslogging.statusreader
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import json
import logging
import urllib
import urllib2

from statuslogclient import StatusLogClient

__all__ = [
    'StatusReader'
]

class StatusReader(StatusLogClient):
    """Class for querying the statuslog API
    """

    def __init__(self, api_endpoint):
        """Constructor

        Arguments:
        api_endpoint -- url to post statuses
        """
        super(StatusReader, self).__init__(api_endpoint)

    DATETIME_FORMAT = '%Y%m%dT%H%M%SZ'

    def read(self, timeout=None, **query):
        """Queries status entries

        Arguments
         - **query -- arbitrary parameters to submit in query string

        Possible Query Parameters (not an exaustive list):
         - limit -- maximum number of log entries to be returned; ex. limit=10
         - offset -- used in conjunction with limit, ex. offset=30
         - newer_than -- exclude log entries at or before this
            datetime; ex. newer_than='2015-01-14'
         - older_than -- exclude log entries at or after this
            datetime; ex. older_than='2015-01-14T18:23:23Z'
         - most_recent_by_group -- the most recent log entry will be returned
            per group; ex. most_recent_by_group='domain'
         - status -- ex. status='Good'
         - step -- ex. step='Fill Data'
         - action -- ex. action='Start'
         - machine -- ex. machine='Smokey'
        """
        query_string = urllib.urlencode(query)

        url = '%s?%s' % (self.api_endpoint, query_string)
        logging.debug("Querying status log: %s", (url))
        req = urllib2.Request(url)
        resp = urllib2.urlopen(req, None, timeout or self.TIMEOUT)
        return json.loads(resp.read())
