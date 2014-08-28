from distutils.core import setup

setup(
    name='pyairfire',
    version='0.1.0',
    author='Joel Dubowy',
    author_email='jdubowy@gmail.com',
    packages=['pyairfire'],
    scripts=[],
    url='git@bitbucket.org:fera/airfire-pyairfire.git',
    description='General toolbox of pythong utilities for AirFire team.',
    install_requires=["netcdf==0.0.28"],
)
