import os

from setuptools import setup, find_packages

BASEDIR = os.path.abspath(os.path.dirname(__file__))
REPODIR = os.path.dirname(BASEDIR)
README = open(os.path.join(REPODIR, 'README.md')).read()

with open(os.path.join(REPODIR, 'requirements.txt')) as fobj:
    REQUIRES = list()
    DEPENDENCIES = list()
    for line in fobj.readlines():
        if line.startswith('#') or not line.strip():
            continue
        if line.startswith('-e'):
            DEPENDENCIES.append(line[2:].strip())
        else:
            REQUIRES.append(line.strip())


setup(
    name='mist.api',
    version='0.9.9',
    license='Apache-2.0',
    description=("Server management, monitoring & automation across clouds "
                 "from any web device"),
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: Apache License 2.0"
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='mist.io',
    author_email='info@mist.io',
    url='https://mist.io',
    keywords=('web cloud server management monitoring automation mobile '
              'libcloud pyramid amazon aws rackspace openstack linode '
              'softlayer digitalocean gce'),
    packages=find_packages(BASEDIR),
    namespace_packages=['mist'],
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIRES,
    dependency_links=DEPENDENCIES,
    tests_require=REQUIRES,
    test_suite="mist.io",
    entry_points="""
    [paste.app_factory]
    main = mist.api:main
    """,
)
