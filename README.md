# pyairfire

This is a general toolbox to hold python packages and scripts for the Airfire
Team.

## Development

### Install Dependencies

Run the following to install dependencies:

    pip install -r requirements.txt

### Setup Environment

To import pyairfire in development, you'll have to add the repo root directory to the search path.
Some of the scripts bin do this automatically.

Another environmental variable that needs to be set is DYLD_LIBRARY_PATH, which needs to include
the directory that contains libhdf5_hl.7.dylib, needed by netCDF4.  That can be set on the command, such
as in the following:

    DYLD_LIBRARY_PATH=/path/to/hdf5-1.8.9-2/lib/ ./bin/bluesky/extract_point_pm25_time_series.py
