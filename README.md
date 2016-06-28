# pyairfire

This is a general toolbox to hold python packages and scripts for the Airfire
Team.

***This software is provided for research purposes only. Use at own risk.***

## Python 2 and 3 Support

This package was originally developed to support python 2.7, but has since
been refactored to support 3.5. Attempts to support both 2.7 and 3.5 have
been made but are not guaranteed.

## Development

### Clone Repo

Via ssh:

    git clone git@github.com:pnwairfire/pyairfire.git

or http:

    git clone https://github.com/pnwairfire/pyairfire.git

### Install Dependencies

Run the following to install required python packages:

    pip install -r requirements.txt

### Setup Environment

To import pyairfire in development, you'll have to add the repo root directory
to the search path. Some of the scripts bin do this automatically.

## Running tests

First, install test-specific packages:

    pip install -r requirements-test.txt

Once installed, you can run tests with pytest:

    py.test
    py.test ./test/pyairfire/datetime/test_parsing.py
    py.test ./test/pyairfire/datetime/

You can also use the ```--collect-only``` option to see a list of all tests.

    py.test --collect-only

Use the '-s' option to see output:

    py.test -s

## Installation

### Installing With pip

First, install pip (with sudo if necessary):

    apt-get install python-pip

Then, to install, for example, v1.2.3, use the following (with sudo if
necessary):

    pip install --trusted-host pypi.smoke.airfire.org -i http://pypi.smoke.airfire.org/simple pyairfire==1.2.3

If you get an error like    ```AttributeError: 'NoneType' object has no attribute 'skip_requirements_regex```, it means you need in upgrade pip.  One way to do so is with the following:

    pip install --upgrade pip

## Usage:

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
