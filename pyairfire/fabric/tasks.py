"""pyairfire.fabric.tasks
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

__all__ = [
    'update_roles',
    'make_task'
]

import os
import re
from fabric.api import task, roles as roles_decorator, env

from output import error, debug_log

NOT_INTERPOLATED_MATCHER = re.compile('\%\((\w+)\)')

# TODO: rename 'roles' as 'role_hashes'
def get_env(roles, env_var_key):
    """Gets the environment (development, production, etc.) from the env var
    and whose key is defined by env_var_key and varifies that it's valid.
    """
    if not os.environ.has_key(env_var_key):
        error('Specify %s' % (env_var_key))
    if os.environ[env_var_key] not in roles.keys():
        error("%s must be one of the following: '%s'" % (
            env_var_key, "', '".join(roles.keys())))
    return os.environ[env_var_key]

# TODO: rename 'roles' as 'role_hashes'
def update_roles(roles, env_var_key):
    """Updates fabric's hash of roles

    Note: we're assuming one user per role - the same user across all of
    the machines playing that role. This could change.
    """
    environment = get_env(roles, env_var_key)
    for role, role_array in roles[environment].items():
        for i in xrange(len(role_array)):
            data = {}
            variables = NOT_INTERPOLATED_MATCHER.findall(role_array[i])
            for v in variables:
                k = "%s_%s" % (role.upper(), v.upper())
                debug_log("setting %s" % (k))
                if k in os.environ:
                    data[v] = os.environ[k]
            try:
                role_array[i] = role_array[i] % (data)
            except KeyError:
                # ignore for now, since this role may be unused by task being called
                pass
    debug_log(roles[environment])
    env.roledefs.update(roles[environment])

class make_task(object):
    """decorator to make a fabric task out of a function
    """

    # TODO: rename 'roles'/'self.roles' as 'roles_names'/'self.role_names'
    def __init__(self, *roles):
        """Constructor

        Args:
         - roles -- roles that this task should be applied to
        """
        # Note: put off checking if roles is defined until ___call__, simply
        # to be able to mention task's name in the error messages
        self.roles = roles

    def check_roles(self):
        """Makes sure all roles needed by this task have user appropriately defined
        """
        for role in self.roles:
            for e in env.roledefs[role]:
                missing = NOT_INTERPOLATED_MATCHER.findall(e)
                if missing:
                    missing = ["%s_%s" % (role.upper(), v.upper()) for v in missing]
                    error("Specify %s" % (', '.join(missing)))

    def __call__(self, func):
        if not self.roles:
            error("Define a role for %s.%s" %(func.__module__, func.__name__))

        def decorated(*args, **kwargs):
            self.check_roles()
            func(*args, **kwargs)

        d = decorated
        d.__name__ = func.__name__
        d.__doc__ = func.__doc__
        d.__module__ = func.__module__
        d.func_name = func.func_name

        return task(roles_decorator(self.roles)(d))