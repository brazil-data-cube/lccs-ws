#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Land Cover Classification System Web Service."""

import os
from setuptools import find_packages, setup

readme = open('README.rst').read()

history = open('CHANGES.rst').read()

tests_require = [
    'coverage>=4.5',
    'coveralls>=1.8',
    'pytest>=5.2',
    'pytest-cov>=2.8',
    'pytest-pep8>=1.0',
    'pydocstyle>=4.0',
    'isort>4.3',
    'check-manifest>=0.40'
]

docs_require = [
    'Sphinx>=2.2',
]

extras_require = {
    'docs': docs_require,
    'tests': tests_require,
}

extras_require['all'] = [ req for exts, reqs in extras_require.items() for req in reqs ]

setup_requires = [
    'pytest-runner>=5.2',
]

install_requires = [
    'Flask>=1.1.1',
    'Flask-Cors>=3.0.8',
    'Flask-Script>=2.0.6',
    'Flask-Migrate>=2.5.2',
    'Flask-SQLAlchemy>=2.4.1',
    'GeoAlchemy2>=0.6.2',
    'psycopg2>=2.8.3',
    'requests>=2.9.1',
    'shapely>=1.6',
    'SQLAlchemy==1.3.4',
    'flask-redoc>=0.1.0',
    'marshmallow-sqlalchemy==0.18.0',
    'Werkzeug>=0.16.1,<1', # Temp workaround https://github.com/noirbizarre/flask-restplus/issues/777
    'bdc-core @ git+git://github.com/brazil-data-cube/bdc-core.git#egg=bdc-core',
    'lccs-db @ git+git://github.com/brazil-data-cube/lccs-db.git#egg=lccs-db',
]

packages = find_packages()

with open(os.path.join('lccs_ws', 'version.py'), 'rt') as fp:
    g = {}
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='lccs-ws',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='Land Use Cover',
    license='MIT',
    author='INPE',
    author_email='fabi.zioti@gmail.com',
    url='https://github.com/brazil-data-cube/lccs-ws',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'lccs_ws = lccs_ws.cli:cli'
        ]
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
    ],
)