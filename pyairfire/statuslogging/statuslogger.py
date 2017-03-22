"""pyairfire.statuslogging.statuslogger
"""

__author__      = "Joel Dubowy"

import datetime
import hashlib
import json
import socket
import urllib.request
import urllib.parse

from .statuslogclient import StatusLogClient

__all__ = [
    'StatusLogger'
]


class PostHTTPRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Post data on redirect.

    adapted from http://stackoverflow.com/questions/33382273/python-3-5-urllib-request-request-post-data-to-website-doing-get-and-not-post
    """
    CONTENT_HEADERS = ("content-length", "content-type")
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        m = req.get_method()
        if (code in (301, 302, 303, 307) and m in ("GET", "HEAD")
            or code in (301, 302, 303) and m == "POST"):
            newurl = newurl.replace(' ', '%20')

            newheaders = dict((k, v) for k, v in req.headers.items()
                              if k.lower() not in self.CONTENT_HEADERS)
            return urllib.request.Request(newurl, data=req.data,
                headers=newheaders,origin_req_host=req.origin_req_host,
                unverifiable=True)
        else:
            raise urllib.request.HTTPError(req.get_full_url(), code, msg, headers, fp)

urlopener = urllib.request.build_opener(PostHTTPRedirectHandler)


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
            data = json.dumps(data).encode('utf-8')
            resp = urlopener.open(url, data, self.TIMEOUT)  #.read()

        except Exception as e:
            if error_handler:
                error_handler(e)
            # Otherwise, don't do anything

    def _machine(self):
        return socket.gethostname()

    # TODD: Remove this method and use afweb.auth.sign_url
    def _signed_url(self):
        path = urllib.parse.urlparse(self.api_endpoint).path
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
