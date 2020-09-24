#!/usr/bin/env python3

import logging
import os
import shutil
import sys
sys.path.insert(0, os.path.abspath(os.path.join(sys.path[0], '../')))
from pyairfire import osutils

def main():

    ## With errors

    logging.basicConfig(level=logging.DEBUG)
    logging.info("-"*80)
    logging.info("No working dir, no cleanup")
    with osutils.create_working_dir() as wdir:
        os.makedirs(os.path.join(wdir, 'aaa', 'bbb'))
    assert os.path.exists(wdir)
    shutil.rmtree(wdir)

    logging.info("-"*80)
    logging.info("Working dir, no cleanup")
    with osutils.create_working_dir(working_dir='./foo/') as wdir:
        os.makedirs(os.path.join(wdir, 'aaa', 'bbb'))
    assert os.path.exists(wdir)
    shutil.rmtree(wdir)

    logging.info("-"*80)
    logging.info("No working dir, with cleanup")
    with osutils.create_working_dir(delete_if_no_error=True) as wdir:
        os.makedirs(os.path.join(wdir, 'aaa', 'bbb'))
    assert not os.path.exists(wdir)

    logging.info("-"*80)
    logging.info("Working dir, with cleanup")
    with osutils.create_working_dir(working_dir='./bar/', delete_if_no_error=True) as wdir:
        os.makedirs(os.path.join(wdir, 'aaa', 'bbb'))
    assert not os.path.exists(wdir)


    ## No errors

    logging.basicConfig(level=logging.DEBUG)
    logging.info("-"*80)
    logging.info("No working dir, no cleanup  ***(WITH ERROR)***")
    try:
        with osutils.create_working_dir() as wdir:
            os.makedirs(os.path.join(wdir, 'aaa', 'bbb'))
            123 / 0
    except:
        pass
    assert os.path.exists(wdir)
    shutil.rmtree(wdir)

    logging.info("-"*80)
    logging.info("Working dir, no cleanup  ***(WITH ERROR)***")
    try:
        with osutils.create_working_dir(working_dir='./foo/') as wdir:
            os.makedirs(os.path.join(wdir, 'aaa', 'bbb'))
            123 / 0
    except:
        pass
    assert os.path.exists(wdir)
    shutil.rmtree(wdir)

    logging.info("-"*80)
    logging.info("No working dir, with cleanup  ***(WITH ERROR)***")
    try:
        with osutils.create_working_dir(delete_if_no_error=True) as wdir:
            os.makedirs(os.path.join(wdir, 'aaa', 'bbb'))
            123 / 0
    except:
        pass
    assert os.path.exists(wdir)
    shutil.rmtree(wdir)

    logging.info("-"*80)
    logging.info("Working dir, with cleanup  ***(WITH ERROR)***")
    try:
        with osutils.create_working_dir(working_dir='./bar/', delete_if_no_error=True) as wdir:
            os.makedirs(os.path.join(wdir, 'aaa', 'bbb'))
            123 / 0
    except:
        pass
    assert os.path.exists(wdir)
    shutil.rmtree(wdir)

if __name__ == "__main__":
    main()
