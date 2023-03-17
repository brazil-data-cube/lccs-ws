..
    This file is part of LCCS-WS.
    Copyright (C) 2022 INPE.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.


Installation
============


``lccs-ws`` implementation depends essentially on `Flask <https://palletsprojects.com/p/flask/>`_, `SQLAlchemy <https://www.sqlalchemy.org/>`_ and the `LCCS Database Module <https://github.com/brazil-data-cube/lccs-db>`_.


Development Installation
------------------------


Clone the software repository::

    git clone https://github.com/brazil-data-cube/lccs-ws.git


Go to the source code folder::

    cd lccs-ws


Initialize the Git submodules::

    git submodule init

    git submodule update


Install in development mode::

    pip3 install -e .[all]


Run the Tests
+++++++++++++


Run the tests::

    ./run-tests.sh


Build the Documentation
+++++++++++++++++++++++


Generate the documentation::

    python setup.py build_sphinx


The above command will generate the documentation in HTML and it will place it under::

    docs/sphinx/_build/html/


You can open the above documentation in your favorite browser, as::

    firefox docs/sphinx/_build/html/index.html


Running in Development Mode
---------------------------


In the source code folder, enter the following command::

    FLASK_APP="lccs_ws" \
    FLASK_ENV="development" \
    SQLALCHEMY_DATABASE_URI="postgresql://user:password@localhost:5432/dbname" \
    LCCS_URL="http://localhost:5000" \
    flask run


You may need to replace the definition of some environment variables:

  - ``FLASK_ENV="development``: used to tell Flask to run in `Debug` mode.

  - ``LCCS_URL="http://localhost:5000"``: Base URI of the service.

  - ``SQLALCHEMY_DATABASE_URI="postgresql://user:password@localhost:5432/dbname"``: The database URI to be used [#f1]_.


The above command should output some messages in the console as showed below::

    * Environment: development
    * Debug mode: on
    * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    * Restarting with stat
    * Debugger is active!
    * Debugger PIN: 184-616-293


If you want to check if the system is up and running, try the following URL in your web browser:

* http://localhost:5000/classification_systems


You should see an output like:

.. code-block:: js

    [
      {
        "authority_name": "INPE",
        "description": "Sistema de Classificação Anual de Desmatamento",
        "id": 1,
        "links": [
          {
            "href": "http://localhost:5000/classification_systems/1",
            "rel": "classification system",
            "title": "Link to Classification System",
            "type": "application/json"
          },
          {
            "href": "http://localhost:5000/classification_systems/1/classes",
            "rel": "classes",
            "title": "Link to Classification System Classes",
            "type": "application/json"
          },
          {
            "href": "http://localhost:5000/classification_systems/1/styles",
            "rel": "classes",
            "title": "Link to Available Styles",
            "type": "application/json"
          },
          {
            "href": "http://localhost:5000/mappings/1",
            "rel": "mappings",
            "title": "Link to Classification Mappings",
            "type": "application/json"
          },
          {
            "href": "http://localhost:5000/classification_systems",
            "rel": "self",
            "title": "Link to this document",
            "type": "application/json"
          }
        ],
        "name": "PRODES",
        "version": "1.0"
      }
    ]


.. rubric:: Footnotes


.. [#f1] Make sure you have a database prepared with the schema for LCSS-WS from the `LCCS-DB <https://github.com/brazil-data-cube/lccs-db>`_
