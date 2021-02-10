..
    This file is part of Land Cover Classification System Web Service.
    Copyright (C) 2020 INPE.

    Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Deploying
=========

``lccs-ws`` implementation depends essentially on `Flask <https://palletsprojects.com/p/flask/>`_, `SQLAlchemy <https://www.sqlalchemy.org/>`_ and the `LCCS Database Module <https://github.com/brazil-data-cube/lccs-db>`_.

There is a Dockerfile for quick deployment. This section explains how to get the LCCS service up and running with Docker. If you do not have Docker installed, take a look at `this tutorial on how to install it in your system <https://docs.docker.com/install/>`_.


Requeriments
------------

Make sure you have a database prepared with the schema for LCSS-WS from the `LCCS-DB <https://github.com/brazil-data-cube/lccs-db>`_. You can have an instance of a PostgreSQL DBMS with a database prepared from the `LCCS-DB <https://github.com/brazil-data-cube/lccs-db>`_.

Building the Docker Image
-------------------------

On the command line use the `docker build` command to create the docker image for the service:

.. code-block:: shell

        $ docker build -t lccs-ws:0.4.0-0 . --no-cache

The above command will create a Docker image named `lccs-ws` and tag `0.4.0-0`, as one can see with the `docker images` command:

.. code-block:: shell

        $ docker images

        REPOSITORY                                          TAG                 IMAGE ID            CREATED             SIZE
        lccs-ws                                            0.4.0-0             ce2ba6a67896        16 hours ago        752MB

Preparing the Network for Containers
------------------------------------

If you have the PostgreSQL server running in a Docker container and you want to have it accesible to the LCCS-WS, you can create a Docker network and attach your PostgreSQL container to it [#f1]_.

To create a new network, you ca use the `docker network` command:

.. code-block:: shell

        $ docker network create bdc_net


The above command will create a network named `bdc_net`. Now, it is possible to attach your database container in this network:

.. code-block:: shell

        $ docker network connect bdc_net bdc_pg


In the above command, we are supposing that your database container is named `bdc_pg`.

Launching the Docker Container with the LCCS-WS
-----------------------------------------------

The `docker run` command can be used to launch a container from the image `lccs-ws:0.2.0-0`. The command below shows an example on how to accomplish the launch of a container:

.. code-block:: shell

        $ docker run --detach \
             --name lccs-ws \
             --publish 127.0.0.1:5000:5000 \
             --network=bdc_net \
             --env LCCS_URL="http://localhost:5000" \
             --env SQLALCHEMY_DATABASE_URI="postgresql://user:password@localhost:5432/dbname" \
             --env LCCS_UPLOAD_FOLDER="/path/to/the/uploads" \
             lccs-ws:0.4.0-0

Let's take a look at each parameter in the above command:/

    - ``--detach``: tells Docker that the container will run in background (daemon).

    - ``--name lccs-ws``: names the container.

    - ``--publish 127.0.0.1:5000:5000``: by default the LCCS-WS will be running on port ``5000`` of the container. You can bind a host port, such as ``8080`` to the container port ``5000``.

    - ``--network=bdc_net``: if the container should connect to the database server through a docker network, this parameter will automatically attach the container to the ``bdc_net``. You can ommit this parameter if the database server address can be resolved directly from a host address.

    - ``--env SQLALCHEMY_DATABASE_URI="postgresql://user:password@localhost:5432/dbname"``: The database URI to be used [#f1]_.

    - ``--env LCCS_URL="http://localhost:5000"``: Base URI of the service.

    - ``LCCS_UPLOAD_FOLDER="/path/to/the/uploads"``: The directory path to be use to save styles.

    - ``lccs-ws:0.2.0-0``: the name of the base Docker image used to create the container.

If you have launched the container, you can check if the service has initialized:

.. code-block:: shell

        $  docker logs lccs-ws
         * Environment: production
           WARNING: This is a development server. Do not use it in a production deployment.
           Use a production WSGI server instead.
         * Debug mode: off
         * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)

Finally, to test if it is listening, use the ``curl`` command:

.. code-block:: shell

        $ curl localhost:5000/

        [[{
            "href": "http://localhost:5000/",
            "rel": "self",
            "title": "Link to this document",
            "type": "application/json"
          },
          {
            "href": "http://localhost:5000/classification_systems",
            "rel": "classification_systems",
            "title": "List classification_systems",
            "type": "application/json"
          }
        ]]


.. rubric:: Footnotes

.. [#f1] If you have a valid address for the PostgreSQL DBMS you can skip this section.

.. [#f2] Make sure you have a database prepared with the schema for LCSS-WS from the `LCCS-DB <https://github.com/brazil-data-cube/lccs-db>`_
