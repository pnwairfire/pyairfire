from setuptools import setup, find_packages

from pyairfire import __version__

test_requirements = []
with open('requirements-test.txt') as f:
    test_requirements = [r for r in f.read().splitlines()]

setup(
    name='pyairfire',
    version=__version__,
    license='GPLv3+',
    author='Joel Dubowy',
    author_email='jdubowy@gmail.com',
    packages=find_packages(),
    scripts=[
        'bin/bluesky/extract-point-pm25-time-series.py',
        'bin/bluesky/merge-emissions',
        'bin/bluesky/merge-fires',
        'bin/bluesky/run-bluesky',
        'bin/hipchat/hcarch',
        'bin/hipchat/hcarch2log',
        'bin/hms/get-hms-kml',
        'bin/met/arlindexer',
        'bin/met/arlfinder',
        'bin/met/arlprofiler',
        'bin/met/arlquery',
        'bin/statuslogging/log-status.py',
        'bin/statuslogging/read-status-log'
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 2",
        "Operating System :: POSIX",
        "Operating System :: MacOS"
    ],
    url='https://github.com/pnwairfire/pyairfire',
    description='General toolbox of python utilities for AirFire team.',
    install_requires=[
        #"netcdf"  #"netcdf==0.0.28"
        "requests>=2.7.0",
        "xmltodict==0.9.2",
        "Fabric==1.10.2",
        "pymongo>=3.1.1"
    ],
    tests_require=test_requirements
)
