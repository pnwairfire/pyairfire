"""pyairfire.statuslogging.statuslogclient
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

__all__ = [
    'StatusLogClient'
]

class StatusLogClient(object):
    """Base class for ... statuslog API
    """

    TIMESTAMP_FORMAT = "%Y%m%dT%H%M%SZ"
    TIMEOUT = 3 # seconds

    def __init__(self, api_endpoint, api_key=None, api_secret=None):
        """Constructor

        Arguments:
         - api_endpoint -- url to post statuses
         - api_key -- api key to use status-logs service
         - api_secret -- secret used in signing requests
        """
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.api_secret = api_secret
