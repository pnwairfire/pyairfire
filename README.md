# pyairfire

This is a general toolbox to hold python packages and scripts for the Airfire
Team.

## Non-python Dependencies

Whether cloning the repo or installing with pip, if you'll be using pyairfire
to generate single point graphs from bluesky output, you'll first need to
manually install gdal, and netcdf, which pyairfire depends on.

On a mac, you can do so with [Homebrew](http://brew.sh/):

    brew install homebrew/science/netcdf
    brew install gdal --with-netcdf --enable-unsupported

Note that the '--with-netcdf' option is required to build gdal with the
netCDF driver. See http://trac.osgeo.org/gdal/wiki/NetCDF for more information.

On ubuntu, the following should be sufficient:

    sudo apt-get install libnetcdf-dev
    sudo apt-get install python-gdal
    sudo apt-get install libgdal1-1.7.0

## Development

### Clone Repo

Via ssh:

    git clone git@github.com:pnwairfire/pyairfire.git

or http:

    git clone https://github.com/pnwairfire/pyairfire.git

### Install Dependencies

After installing the non-python dependencies (mentioned above), run the
following to install required python packages:

    pip install -r requirements.txt

#### The netcdf Package

pyairfire requires the netcdf python package for generating single-point
graphs from BlueSky ouput.  Unfortunately, the ```netcdf``` package has in
the past failed to install due to the following error:

    TypeError: parse_requirements() missing 1 required keyword argument: 'session'

This error is in pip.req.parse_requirements, which is not in pip's public
API.  So, netcdf isn't listed in pyairfire's requirements in setup.py.
If you'd like to use the single-point graph functionaility (in
pyairfire.bluesky.dispersionnc), you'll need to install netcdf package
manually.

### Setup Environment

To import pyairfire in development, you'll have to add the repo root directory
to the search path. Some of the scripts bin do this automatically.

Another environmental variable that sometimes needs to be set, depending
on your platform, is DYLD_LIBRARY_PATH, which needs to include the directory
that contains libhdf5_hl.7.dylib, needed by netCDF4.  That can be set on
the command line, such as in the following:

    DYLD_LIBRARY_PATH=/path/to/hdf5-1.8.9-2/lib/ ./bin/bluesky/extract_point_pm25_time_series.py
    DYLD_LIBRARY_PATH=/path/to/hdf5-1.8.9-2/lib/ nosetests

## Running tests

First, install test-specific packages:

    pip install -r requirements-test.txt

Once installed, you can run tests with pytest:

    py.test
    py.test ./test/pyairfire/bluesky/dispersionnc_tests.py
    py.test ./test/pyairfire/bluesky/

You can also use the ```--collect-only``` option to see a list of all tests.

    py.test --collect-only

Use the '-s' option to see output:

    py.test -s

## Installation

### Installing With pip

First, install pip (with sudo if necessary):

    apt-get install python-pip

Then, to install, for example, v0.8.12, use the following (with sudo if
necessary):

    pip install --trusted-host pypi.smoke.airfire.org -i http://pypi.smoke.airfire.org/simple pyairfire==0.8.12

If you get an error like    ```AttributeError: 'NoneType' object has no attribute 'skip_requirements_regex```, it means you need in upgrade pip.  One way to do so is with the following:

    pip install --upgrade pip

## Usage:

### pyairfire.bluesky

Look at the docstrings in the code for usage examples.

### pyairfire.scripting

Look at the docstrings in the code for usage examples.

### pyairfire.statuslogging

Look at the docstrings in the code for usage examples.

### pyairfire.web

#### Basic Auth

Here's a very basic 'Hello World' app that uses basic_auth

    import os

    from flask import Flask, request, Response
    from pyairfire.web.auth import basic_auth

    app = Flask(__name__)

    @app.route("/")
    @basic_auth(
        True,
        'foo',
        'bar',
        lambda: request.authorization,
        Response
    )
    def admin_index():
        return 'Hello World', 200

    if __name__ == "__main__":
        app.run(
            host='localhost',
            debug=False,
            port=6060
        )

The following will fail with a 401:

    curl -D - "http://localhost:6060/"

The following, however, will succeed

    curl -D - "http://foo:bar@localhost:6060/"

#### API Key/Secret

TODO....
