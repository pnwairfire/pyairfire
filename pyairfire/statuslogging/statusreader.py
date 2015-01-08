"""statusreader.py:
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

from statuslogclient import StatusLogClient
import json
import urllib
import urllib2

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

    def read(self, limit=None, offset=None, newer_than=None, older_than=None,
            most_recent_by_group=None, **query):
        """Queries status entries

        Arguments
         - limit -- (int) maximum number of log entries to be returned
         - offset -- (int) used in conjunction with limit
         - newer_than -- (datetime) exclude log entries at or before this datetime
         - older_than -- (datetime) exclude log entries at or after this datetime
         - most_recent_by_group -- (string) what to group by; if specified, only
            the most recent log entry will be returned per group;
            ex. 'domain' or 'process'
         - **query -- arbitrary parameters to submit in query string

        Possible Query Parameters (not an exaustive list):
         - status -- ex. status='Good'
         - step -- ex. step='Fill Data'
         - action -- ex. action='Start'
         - machine -- ex. machine='Smokey'
        """
        if limit:
            query.update(limit=limit)
        if offset:
            query.update(limit=offset)
        if newer_than:
            query.update(newer_than=newer_than.strftime(self.DATETIME_FORMAT))
        if offset:
            query.update(limit=offset)

        query_string = urllib.urlencode(query)

        url = '%s?%s' % (self.api_endpoint, query_string)
        req = urllib2.Request(url)
        resp = urllib2.urlopen(req, None, self.TIMEOUT)
        return json.loads(resp.read())
