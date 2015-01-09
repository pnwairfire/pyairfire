# pyairfire

This is a general toolbox to hold python packages and scripts for the Airfire
Team.

## Development

### Install Dependencies

Run the following to install dependencies:

    pip install -r requirements.txt

### Setup Environment

To import pyairfire in development, you'll have to add the repo root directory
to the search path. Some of the scripts bin do this automatically.

Another environmental variable that needs to be set is DYLD_LIBRARY_PATH, which
needs to include the directory that contains libhdf5_hl.7.dylib, needed by
netCDF4.  That can be set on the command line, such as in the following:

    DYLD_LIBRARY_PATH=/path/to/hdf5-1.8.9-2/lib/ ./bin/bluesky/extract_point_pm25_time_series.py
    DYLD_LIBRARY_PATH=/path/to/hdf5-1.8.9-2/lib/ nosetests


## Running tests

Use nose:

    nosetests
    nosetests test/pyairfire/bluesky/dispersionnc_tests.py
    nosetests -v -w ./test/pyairfire/bluesky/

## Installation

The repo is currently public. So, you don't need to be on the FERA bitbucket team
to install from the repo.

### Installing With pip

First, install pip:

    sudo apt-get install python-pip

Then, to install, for example, v0.2.0, use the following:

    sudo pip install git+https://bitbucket.org/fera/airfire-pyairfire@v0.2.0

Or add it to your project's requirements.txt:

    git+https://bitbucket.org/fera/airfire-pyairfire@v0.2.0

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
