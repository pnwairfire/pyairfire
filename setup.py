from setuptools import setup, find_packages

# Note: using pip.req.parse_requirements like so:
#  > REQUIREMENTS = [str(ir.req) for ir in parse_requirements('requirements.txt')]
# results in the folloing error on Heroku:
#    TypeError: parse_requirements() missing 1 required keyword argument: 'session'
with open('requirements.txt') as f:
    REQUIREMENTS = f.read().splitlines()
with open('requirements-test.txt') as f:
    TEST_REQUIREMENTS = f.read().splitlines()

setup(
    name='pyairfire',
    version='0.6.11',
    license='MIT',
    author='Joel Dubowy',
    author_email='jdubowy@gmail.com',
    packages=find_packages(),
    scripts=[
        'bin/bluesky/extract-point-pm25-time-series.py',
        'bin/bluesky/pre-process-fires',
        'bin/statuslogging/log-status.py',
        'bin/statuslogging/read-status-log'
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Operating System :: POSIX",
        "Operating System :: MacOS"
    ]
    url='https://github.com/pnwairfire/pyairfire',
    description='General toolbox of python utilities for AirFire team.',
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS
)
