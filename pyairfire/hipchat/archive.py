"""pyairfire.hipchat.archive
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import datetime
import json
import requests

__all__ = [
    'HipChatArchiver'
]

class HipChatArchiver(object):

    def __init__(self, auth_token, num_days, dest_dir=None,
            email_recipients=[]):
        self._auth_token = auth_token
        self._end_date = datetime.datetime.utc_now() - datetime.timedelta(num_days)
        self._dest_dir = dest_dir
        self._email_recipients = email_recipients

    def archive(self):
        rooms = self._get_rooms()
        histories = [self._get_history(r) for r in rooms]
        archive_file = self._archive(histories)

        if self._dest_dir:
            # TODO: copy tarball to dest_dir
            pass

        if self._email_recipients:
            self._email(tarball, email_recipients)



    def _get_rooms(self):
        # TODO: get rooms with:
        #  https://www.hipchat.com/docs/apiv2/method/get_all_rooms
        url = "https://api.hipchat.com/v2/rooms?auth_token={}".format(auth_token)
        headers = {
           'Content-type': 'application/json',
           'Accept': 'text/plain'
        }
        r = requests.get(url, headers=headers)
        import pdb; pdb.set_trace()
        return r # TODO: extract necessary data from r

    def _get_history(self, room):
        # TODO: get room history with:
        #  https://www.hipchat.com/docs/apiv2/method/view_room_history
        # will need to use start-index and end-date and make repeated calls
        pass

    def _pack(self, histories):
        # TODO: bundle into tarball or zip file, in tmp dir
        pass

    def _email(self, tarball, email_recipients):
        # TODO: email; handle exceptions
        pass

