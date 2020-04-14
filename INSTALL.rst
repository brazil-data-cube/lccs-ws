..
    This file is part of Land Cover Classification System Web Service.
    Copyright (C) 2019 INPE.

    Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Installation
============

``lccs-ws`` implementation depends essentially on `Flask <https://palletsprojects.com/p/flask/>`_, `SQLAlchemy <https://www.sqlalchemy.org/>`_ and the `LCCS Database Module <https://github.com/brazil-data-cube/lccs-db>`_.


Development Installation
------------------------

Clone the software repository:

.. code-block:: shell

        $ git clone https://github.com/brazil-data-cube/lccs-ws.git


Go to the source code folder:

.. code-block:: shell

        $ cd lccs-ws


Install in development mode:

.. code-block:: shell

        $ pip3 install -e .[all]


Generate the documentation:

.. code-block:: shell

        $ python setup.py build_sphinx
