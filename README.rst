..
    This file is part of Land Cover Classification System Web Service.
    Copyright (C) 2019 INPE.

    Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


============================================
Land Cover Classification System Web Service 
============================================

.. image:: https://img.shields.io/badge/license-MIT-green
        :target: https://github.com//brazil-data-cube/lccs-ws/blob/master/LICENSE

.. image:: https://img.shields.io/badge/build-todo-success
        :target: https://travis-ci.org/brazil-data-cube/lccs-ws

.. image:: https://img.shields.io/badge/tests-0%20passed,%200%20failed-critical
        :target: https://travis-ci.org/brazil-data-cube/lccs-ws

.. image:: https://coveralls.io/repos/github/brazil-data-cube/lccs-ws/badge.svg?branch=master
        :target: https://coveralls.io/github/brazil-data-cube/lccs-ws?branch=master

.. image:: https://img.shields.io/badge/lifecycle-experimental-orange.svg
        :target: https://www.tidyverse.org/lifecycle/#experimental

.. image:: https://badges.gitter.im/brazil-data-cube/community.svg
        :target: https://gitter.im/brazil-data-cube/community#
        :alt: Join the chat

This is the server application.

About
=====

Currently, there are several data sets on regional, national and global scales with information on land use and land cover that aim to support a large number of applications, including the management of natural resources, climate change and its impacts, and biodiversity conservation. These data products are generated using different approaches and methodologies, which present information about different classes of the earth's surface, such as forests, agricultural plantations, among others. Initiatives that generate land use and land cover maps normally develop their own classification system, with different nomenclatures and meanings of the classes used.


In this context, the **LCCS-WS** (**L**\ and **C**\ over **C**\ lassification **S**\ystem **W**\eb **S**\ ervice) aims to provide a simple interface to access the various classification systems in use and their respective classes. Therefore, this service proposes a representation for the classification systems and provides an API to access the classes and their symbolizations. It is also possible to stablish mappings between classes of different systems.


Free and Open Source implementations based on this service can be found in the `lccs-ws <https://github.com/brazil-data-cube/lccs-ws>`_ (server) and `lccs.py <https://github.com/brazil-data-cube/lccs.py>`_ (Python client). See also the service **W**\eb **L**\and **T**\rajectory **S**\ystem (`WLTS <https://github.com/brazil-data-cube/wlts-spec>`_), which uses LCCS-WS to represent the classes associated with the features retrieved in its queries.

Installation
============

See `INSTALL.rst <./INSTALL.rst>`_.


Running
=======

See `RUNNING.rst <./RUNNING.rst>`_.

Developer Documentation
=======================

**Under Development!**


License
=======

.. admonition::
    Copyright (C) 2019 INPE.

    Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.
