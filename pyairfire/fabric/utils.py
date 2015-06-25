"""pyairfire.fabric.utils
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import os
import re
from fabric import api
from fabric.contrib import files

__all__ = [
    'kill_processes',
    'run_in_background',
    'already_running',
    'create_ssh_tunnel',
    'destroy_ssh_tunnel',
    'install_pyenv',
    'install_pyenv_environment'
]


##
##  Managing (Running & Killing) Processes
##

def kill_processes(pattern):
    with api.settings(warn_only=True):
        api.sudo("pkill -f '%s'" % (pattern))
    #api.sudo("! pgrep -f '%s' || pkill -f '%s'" % (pattern, pattern))

def run_in_background(command, role, kill_first=False, sudo_as=None):
    """
    From: http://stackoverflow.com/questions/8775598/start-a-background-process-with-nohup-using-fabric
    """
    if kill_first:
        kill_processes(command)

    sudo_as_key = "%s_SUDO_AS" % (role.upper())
    sudo_as = os.environ.get(sudo_as_key) or sudo_as
    command = 'nohup %s &> /dev/null &' % (command)
    api.sudo(command, pty=False, user=sudo_as)

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

def wrapped_run(command, skip_if_already_running=False,
        silence_system_exit=False, use_sudo=False):
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
            if use_sudo:
                api.sudo(command)
            else:
                api.run(command)
        except SystemExit, e:
            if not silence_system_exit:
                raise


##
##  ssh tunneling
##

LOOPBACK_ADDRESSES_RE = re.compile('^(localhost|172.0.0.[1-8]|::1)$')

def _ssh_tunnel_command(local_port, remote_port, remote_host, remote_user,
        local_host, ssh_port):
    # Notes are args:
    #  '-f' -> forks process
    #  '-N' -> no command to be run on server
    return "ssh -f -N -p %s %s@%s -L %s/%s/%s -oStrictHostKeyChecking=no" % (
        ssh_port, remote_user, remote_host, local_port, local_host, remote_port
    )

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
        command = _ssh_tunnel_command(local_port, remote_port, remote_host,
            remote_user, local_host, ssh_port)
        wrapped_run(command, skip_if_already_running=True, use_sudo=True)

def destroy_ssh_tunnel(local_port, remote_port, remote_host, remote_user,
        local_host='localhost', ssh_port=22):
    """Destroys an ssh tunnel, if it exists

    Args:
     - local_port
     - remote_port
     - remote_host
     - remote_user
    Kwargs:
     - local_host (default: 'localhost')
     - ssh_port
    """
    command =  _ssh_tunnel_command(local_port, remote_port, remote_host,
        remote_user, local_host, ssh_port)
    if already_running(command):
        api.run("pkill -f '%s'" % (command))


##
##  pyenv
##

def install_pyenv(home_dir="~", dot_file=".bash_profile"):
    pyenv_root = "/usr/local/lib/.pyenv"
    if not files.exists("/usr/local/lib/.pyenv"):
        api.sudo("git clone https://github.com/yyuu/pyenv.git {}".format(pyenv_root))
        api.sudo("git clone https://github.com/yyuu/pyenv-virtualenv.git "
            "{}/plugins/pyenv-virtualenv".format(pyenv_root))

    dot_file = os.path.join(home_dir,dot_file)
    dot_file_exists = files.exists(dot_file)

    with api.settings(warn_only=True):
        to_add_to_dot_file = []

        if (not dot_file_exists or
                not api.sudo("grep 'export PYENV_ROOT' {}".format(dot_file))):
            to_add_to_dot_file.append(
                'export PYENV_ROOT="{}"'.format(pyenv_root, dot_file))

        if (not dot_file_exists or
                not api.sudo("grep 'export PATH=\"$PYENV_ROOT/bin' {}".format(dot_file))):
            to_add_to_dot_file.append(
                'export PATH="$PYENV_ROOT/bin:$PATH"'.format(dot_file))

        if (not dot_file_exists or
                not api.sudo("grep 'pyenv init -' {}".format(dot_file))):
            to_add_to_dot_file.append(
                'eval "$(pyenv init -)"'.format(dot_file))

        if to_add_to_dot_file:
            api.sudo("printf '\n{}\n' >> {}".format(
                '\n'.join(to_add_to_dot_file), dot_file))

def install_pyenv_environment(version, virtualenv_name, replace_existing=False):
    if replace_existing:
        # TODO: Remove old
        pass
    api.sudo("pyenv install -s {}".format(version))
    api.sudo("pyenv rehash".format(version))
    # If virtualenv_name is already installed, you get a prompt; if you
    # respond with 'N' to not install if already installed, the command returns
    # and error code.  So, use warn_only=True
    with api.settings(warn_only=True):
        api.sudo("pyenv virtualenv {} {}".format(version, virtualenv_name))
    api.sudo("pyenv rehash".format(version))  # TODO: is this necessary ???
