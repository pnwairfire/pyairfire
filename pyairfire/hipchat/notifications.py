"""pyairfire.hipchat.notifications
"""

__author__      = "Joel Dubowy"

import json
import requests

__all__ = [
    'send'
]

def send(message, room_id, auth_token, color="green"):
    data = {
        "color": color,
        "message": message,
        "notify": False,
        "message_format": "text"
    }
    url = "https://api.hipchat.com/v2/room/{}/notification?auth_token={}".format(
        room_id, auth_token)
    headers = {
        'Content-type': 'application/json',
        'Accept': 'text/plain'
    }
    return requests.post(url, data=json.dumps(data), headers=headers)
