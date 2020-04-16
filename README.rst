..
    This file is part of Land Cover Classification System Web Service.
    Copyright (C) 2019 INPE.

    Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


============================================
Land Cover Classification System Web Service 
============================================

.. image:: https://img.shields.io/badge/license-MIT-green
        :target: https://github.com//brazil-data-cube/lccs-ws/blob/b-0.2.0/LICENSE
        :alt: Software License

.. image:: https://travis-ci.org/brazil-data-cube/lccs-ws.svg?branch=b-0.2.0
        :target: https://travis-ci.org/brazil-data-cube/lccs-ws
        :alt: Build Status

.. image:: https://coveralls.io/repos/github/brazil-data-cube/lccs-ws/badge.svg?branch=b-0.2.0
        :target: https://coveralls.io/github/brazil-data-cube/lccs-ws?branch=b-0.2.0
        :alt: Code Coverage Test

.. image:: https://readthedocs.org/projects/lccs-ws/badge/?version=b-0.2.0
        :target: https://lccs-ws.readthedocs.io/en/b-0.2.0/
        :alt: Documentation Status

.. image:: https://img.shields.io/badge/lifecycle-experimental-orange.svg
        :target: https://www.tidyverse.org/lifecycle/#experimental
        :alt: Software Life Cycle

.. image:: https://img.shields.io/github/tag/brazil-data-cube/lccs-ws.svg
        :target: https://github.com/brazil-data-cube/lccs-ws/releases
        :alt: Release

.. image:: https://badges.gitter.im/brazil-data-cube/community.svg/
        :target: https://gitter.im/brazil-data-cube/community#
        :alt: Join the chat


About
=====

Currently, there are several data sets on regional, national and global scales with information on land use and land cover that aim to support a large number of applications, including the management of natural resources, climate change and its impacts, and biodiversity conservation. These data products are generated using different approaches and methodologies, which present information about different classes of the earth's surface, such as forests, agricultural plantations, among others. Initiatives that generate land use and land cover maps normally develop their own classification system, with different nomenclatures and meanings of the classes used.


In this context, the **LCCS-WS** (**L**\ and **C**\ over **C**\ lassification **S**\ystem **W**\eb **S**\ ervice) aims to provide a simple interface to access the various classification systems in use and their respective classes. Therefore, this service proposes a representation for the classification systems and provides an API to access the classes and their symbolizations. It is also possible to stablish mappings between classes of different systems.


For more information on LCCS-WS, see:

- `LCCS-WS Specification <https://github.com/brazil-data-cube/lccs-ws-spec>`_: the LCCS specification using `OpenAPI 3.0 <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md>`_ notation.

- `LCCS.py <https://github.com/brazil-data-cube/lccs.py>`_: Python Client Library for Land Cover Classification System Web Service.

- `WLTS <https://github.com/brazil-data-cube/lccs.py>`_: Web Land Trajectory Service.


Installation
============

See `INSTALL.rst <./INSTALL.rst>`_.


Deploying
=========

See `DEPLOY.rst <./DEPLOY.rst>`_.


Developer Documentation
=======================

See https://lccs-ws.readthedocs.io/en/b-0.2.0.


License
=======

.. admonition::
    Copyright (C) 2019 INPE.

    Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.
