import re
from setuptools import setup, find_packages

# Note: using pip.req.parse_requirements like so:
#  > REQUIREMENTS = [str(ir.req) for ir in parse_requirements('requirements.txt')]
# results in the folloing error on Heroku:
#    TypeError: parse_requirements() missing 1 required keyword argument: 'session'
git_url_matcher = re.compile('^git\+.+/([^/.]+)(\.git)?@v?([0-9.]+)$')
def parse_requirements(dep_links, req_file_name):
    with open(req_file_name) as f:
        reqs = []
        for r in f.read().splitlines():
            m = git_url_matcher.match(r)
            if m:
                dep_links.append(r)
                reqs.append("%s==%s" % (m.group(1), m.group(3)))
            else:
                reqs.append(r)
        return reqs

dependency_links = []
requirements = parse_requirements(dependency_links, 'requirements.txt')
test_requirements = parse_requirements(dependency_links, 'requirements-test.txt')

setup(
    name='pyairfire',
    version='0.6.12',
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
    ],
    url='https://github.com/pnwairfire/pyairfire',
    description='General toolbox of python utilities for AirFire team.',
    install_requires=requirements,
    dependency_links=dependency_links,
    tests_require=test_requirements
)
