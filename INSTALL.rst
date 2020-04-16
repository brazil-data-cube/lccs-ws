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


Running in Development Mode
---------------------------

In the source code folder, enter the following command:

.. code-block:: shell

    $ FLASK_APP="lccs_ws" \
      FLASK_ENV="development" \
      SQLALCHEMY_URI="postgresql://user:password@localhost:5432/dbname" \
      LCCS_URL="http://localhost:5000" \
      flask run

You may need to replace the definition of some environment variables:

  - ``FLASK_ENV="development``: used to tell Flask to run in `Debug` mode.

  - ``LCCS_URL="http://localhost:5000"``: Base URI of the service.

  - ``SQLALCHEMY_URI="postgresql://user:password@localhost:5432/dbname"``: The database URI to be used [#f1]_.


The above command should output some messages in the console as showed below:

.. code-block:: shell

     * Environment: development
     * Debug mode: on
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger PIN: 184-616-293


If you want to check if the system is up and running, try the following URL in your web browser:

* http://localhost:5000/lccs/classification_systems

You should see an output like:

.. code-block:: js

    {
      "links": [
        {
          "href": "http://localhost:5000/lccs/classification_systems",
          "rel": "self"
        },
        {
          "href": "http://localhost:5000/lccs/",
          "rel": "root"
        },
        {
          "href": "http://localhost:5000/lccs/classification_systems/PRODES",
          "rel": "child",
          "title": "PRODES"
        }
        ]
    }


.. rubric:: Footnotes

.. [#f1] Make sure you have a database prepared with the schema for LCSS-WS from the `LCCS-DB <https://github.com/brazil-data-cube/lccs-db>`_
