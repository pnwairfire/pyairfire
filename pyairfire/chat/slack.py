"""pyairfire.chat.slack
"""

__author__      = "Joel Dubowy"


import json
import requests

__all__ = [
    'send'
]

def send(webhook_url, text, channel=None, icon_emoji=None, username=None):
    """Posts notification to slack channel

    args:
     - webhook_url -- hooks.slack.com url containing identifier guids
     - text -- message to be posted

    kwargs:
     - channel -- used to specify alternate channel; if not defined, message
        will be posted to the webhook's default channel
     - username --
     - icon_emoji -- e.g ":robot:"; if not defined, channel's default icon
        emoji will be displayed

    Examples:

        > send('https://hooks.slack.com/services/sdjsdf/skdjfl/sdkfjlf',
            "test message")
        > send('https://hooks.slack.com/services/sdjsdf/skdjfl/sdkfjlf',
            "hello", channel="#foo", icon_emoji=":robot:", username="bar")
    """
    data = {
        "text": text
    }
    if channel:
        # Make sure channel has '#' prefix
        data['channel'] = '#' + channel.lstrip('#')
    if username:
        data['username'] = username
    if icon_emoji:
        data['icon_emoji'] = icon_emoji

    return requests.post(webhook_url, data=json.dumps(data))
