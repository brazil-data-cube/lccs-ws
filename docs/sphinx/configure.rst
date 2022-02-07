..
    This file is part of Land Cover Classification System Web Service.
    Copyright (C) 2020-2021 INPE.

    Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Configure
---------


.. table::

    +-----------------------------+-------------------------------------------------------------------------------------+
    | Variables                   | Description                                                                         |
    +=============================+=====================================================================================+
    + ``SQLALCHEMY_DATABASE_URI`` | The database URI that should be used for the database connection.                   |
    +-----------------------------+-------------------------------------------------------------------------------------+
    + ``LCCS_URL``                | Base URI of the service.                                                            |
    +-----------------------------+-------------------------------------------------------------------------------------+
    + ``LCCSWS_ENVIRONMENT``      + Execution mode: ``ProductionConfig``, ``DevelopmentConfig``, or ``TestingConfig``.  |
    +-----------------------------+-------------------------------------------------------------------------------------+
    + ``BDC_LCCS_ARGS``           + Argument to handle before request processing: BDC Access token.                     |
    +-----------------------------+-------------------------------------------------------------------------------------+
    + ``BDC_LCCS_ARGS_I18N``      + Argument to handle before request processing: Languages supported by the service.   |
    +-----------------------------+-------------------------------------------------------------------------------------+
