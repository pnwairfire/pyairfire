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
        'bin/hipchat/hcarch',
        'bin/hipchat/hcarch2log',
        'bin/hms/get-hms-kml',
        'bin/statuslogging/log-status.py',
        'bin/statuslogging/read-status-log'
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Operating System :: POSIX",
        "Operating System :: MacOS"
    ],
    url='https://github.com/pnwairfire/pyairfire',
    description='General toolbox of python utilities for AirFire team.',
    install_requires=[
        #"ftfy==4.1.1",
        "requests==2.10.0",
        "slacker==0.9.24",
        "xmltodict==0.10.2",
        "Fabric3==1.11.1.post1"

    ],
    tests_require=test_requirements
)
