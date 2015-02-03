"""pyairfire.fabric.utils
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import re
from fabric import api

__all__ = [
    'create_ssh_tunnel'
]

LOOPBACK_ADDRESSES_RE = re.compile('^(localhost|172.0.0.[1-8]|::1)$')

def already_running(command):
    command = command.strip('&').strip(' ')
    if api.env.warn_only:
        return api.run("pgrep -f '%s'" % (command)) != ''
    else:
        try:
            api.run("pgrep -f '%s'" % (command))
        except SystemExit, e:
            return False
        return True

def run_if_not_already_running(command):
    """Runs the command if there isn't already a live processes started with
    that command.
    """
    if not already_running(command):
        api.run(command)

def create_ssh_tunnel(local_port, remote_port, remote_host, remote_user,
        local_host='localhost', ssh_port=22):
    """Creates an ssh tunnel

    It only does so if:
     a) the smtp host is not the same as the current host (api.env.host)
     b) the smtp host is not localhost
     c) it's not already created

    TODO: consider user as well in case b), above
    """
    if api.env.host != remote_host and not LOOPBACK_ADDRESSES_RE.match(remote_host):
        command = "ssh -N -p %s %s@%s -L %s/%s/%s &" % (
            ssh_port, remote_user, remote_host, local_port, local_host, remote_port
        )

        run_if_not_already_running(command)
