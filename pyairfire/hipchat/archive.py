"""pyairfire.hipchat.archive
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import datetime
import json
import logging
import os
import re
import requests
import StringIO
import zipfile

from pyairfire.scripting.utils import exit_with_msg

__all__ = [
    'HipChatArchiver'
]

class HipChatArchiver(object):
    ARCHIVE_DATETIME_FORMAT = "%Y%m%dT%H%S%M"

    def __init__(self, auth_token, num_days, **options):
        self._auth_token = auth_token
        self._start_date = datetime.datetime.utcnow()
        self._end_date = self._start_date - datetime.timedelta(num_days)
        self._dest_dir = options.get('dest_dir')
        self._email_recipients = options.get('email_recipients')
        if not self._dest_dir and not self._email_recipients:
            exit_with_msg("Specify either dest_dir or email_recipients, or both.")
        self._archive_name = "hipchat-archive-{}-{}".format(
            self._end_date.strftime(self.ARCHIVE_DATETIME_FORMAT),
            self._start_date.strftime(self.ARCHIVE_DATETIME_FORMAT))
        self._zip_file_name = '{}.zip'.format(self._archive_name)

    def archive(self, room_id=None):
        rooms = self._get_rooms(room_id=room_id)
        histories = self._get_histories(rooms)
        in_memory_zip = self._zip(histories)
        self._write(in_memory_zip)
        self._email(in_memory_zip)

    def _send(self, url, join_char='?'):
        url = "{}{}auth_token={}".format(url, join_char, self._auth_token)
        headers = {
           'Accept': 'application/json'
        }
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            # TODO: retry
            exit_with_msg("Http failure: {} - {}".format(url, r.content))
        return json.loads(r.content)


    ROOM_URL = "https://api.hipchat.com/v2/room"
    def _get_rooms(self, room_id=None):
        logging.info('Querying room{}'.format(' id ' + room_id if room_id else 's'))
        # get rooms with:
        #  https://www.hipchat.com/docs/apiv2/method/get_all_rooms
        # Note: url path's can't have trailing slash; if there, you get 404
        url = self.ROOM_URL + '/' + room_id if room_id else self.ROOM_URL
        try:
            data = self._send(url)
        except Exception, e:
            exit_with_msg("Failed to query room information: {}".format(e.message))
        return [data] if room_id else data['items']

    def _get_histories(self, rooms):
        logging.info('Querying histories')
        histories = []
        for r in rooms:
            try:
                logging.info('Querying history for room {} ({})'.format(
                    r['name'], r['id']))
                histories.append({
                    "id": r['id'],
                    "name": r['name'],
                    "history": self._get_history(r['id'])
                })
            except Exception, e:
                logging.error("Failed to query history for room {} - {}."
                    " Skipping".format(r['name'], e.message))
        return histories

    def _get_history(self, room_id):
        # get room history with:
        #  https://www.hipchat.com/docs/apiv2/method/view_room_history
        base_url = '{}/{}/history?date={}&end-date={}'.format(self.ROOM_URL,
            room_id, self._start_date, self._end_date)
        history = []
        start_index=0
        while True:
            url = '{}&start-index={}'.format(base_url, start_index)
            data = self._send(url, join_char='&')
            if not data['items']:
                break
            history.append(data['items'])
            start_index += len(data['items'])
        history.reverse()
        return history

    FILENAME_CLEANER = re.compile('[^\w\-_]')
    def _zip(self, histories):
        logging.info("Zipping up files")
        in_memory_zip = StringIO.StringIO()
        z =  zipfile.ZipFile(in_memory_zip, 'a', zipfile.ZIP_DEFLATED, False)
        for h in histories:
            filename = '{}/{}.json'.format(self._archive_name,
                self.FILENAME_CLEANER.sub('_', h['name']))
            z.writestr(filename, json.dumps(h['history']))
        return in_memory_zip

    def _write(self, in_memory_zip):
        if not self._dest_dir:
            return

        zip_file_name = os.path.join(self._dest_dir, self._zip_file_name)
        logging.info('Writing zipfile {}'.format(zip_file_name))
        with open(zip_file_name, 'w') as zf:
            in_memory_zip.seek(0) # is this necessary
            zf.write(in_memory_zip.read())

    def _email(self, in_memory_zip):
        if self._email_recipients:
            return

        logging.info("Emailing zip file {} to {}".format(
            self._zip_file_name, ', '.join(self._email_recipients)))

        # TODO: email; handle exceptions

