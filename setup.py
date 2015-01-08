from distutils.core import setup
from pip.req import parse_requirements

REQUIREMENTS = [str(ir.req) for ir in parse_requirements('requirements.txt')]

setup(
    name='pyairfire',
    version='0.3.5',
    author='Joel Dubowy',
    author_email='jdubowy@gmail.com',
    packages=[
        'pyairfire',
        'pyairfire.bluesky',
        'pyairfire.statuslogging'],
    scripts=[
        'bin/bluesky/extract-point-pm25-time-series.py',
        'bin/statuslogging/log-status.py'],
    url='git@bitbucket.org:fera/airfire-pyairfire.git',
    description='General toolbox of pythong utilities for AirFire team.',
    install_requires=REQUIREMENTS,
)
