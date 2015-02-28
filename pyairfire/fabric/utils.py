"""pyairfire.fabric.utils
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import re
from fabric import api

__all__ = [
    'already_running',
    'create_ssh_tunnel'
]

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

def wrapped_run(command, skip_if_already_running=False, silence_system_exit=False):
    """Runs the command if there isn't already a live processes started with
    that command.

    Args:
     - command -- command to be run on remote server
    Kwargs:
     - skip_if_already_running (default: False) -- if True, checks if command
        is running, andd skips if so
     - silence_system_exit (default: False) -- catches and ignores SystemExit
        (which indicates command failed on remote server)
    """
    if not skip_if_already_running or not already_running(command):
        try:
            api.run(command)
        except SystemExit, e:
            if not silence_system_exit:
                raise

LOOPBACK_ADDRESSES_RE = re.compile('^(localhost|172.0.0.[1-8]|::1)$')

def create_ssh_tunnel(local_port, remote_port, remote_host, remote_user,
        local_host='localhost', ssh_port=22):
    """Creates an ssh tunnel

    It only does so if:
     a) the smtp host is not the same as the current host (api.env.host)
     b) the smtp host is not localhost
     c) it's not already created

    Args:
     - local_port
     - remote_port
     - remote_host
     - remote_user
    Kwargs:
     - local_host (default: 'localhost')
     - ssh_port

    TODO: consider user as well in case b), above
    """
    if api.env.host != remote_host and not LOOPBACK_ADDRESSES_RE.match(remote_host):
        # Notes are args:
        #  '-f' -> forks process
        #  '-N' -> no command to be run on server
        command = "ssh -f -N -p %s %s@%s -L %s/%s/%s" % (
            ssh_port, remote_user, remote_host, local_port, local_host, remote_port
        )
        wrapped_run(command, skip_if_already_running=True)