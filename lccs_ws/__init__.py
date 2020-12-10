#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2020 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Python Land Cover Classification System Web Service."""

from flask import Flask
from flask_cors import CORS
from lccs_db.ext import LCCSDatabase

from lccs_ws.config import get_settings

from .version import __version__


def create_app(config_name='DevelopmentConfig'):
    """
    Create Brazil Data Cube LCCSWS application from config object.

    :param config_name: Config instance
    :type config_name: (string|lccs_ws.config.Config)

    :returns: config instance scope.
    :rtype: Flask Application
    """
    app = Flask(__name__)

    conf = config.get_settings(config_name)

    app.config.from_object(conf)

    with app.app_context():
        # Initialize Flask SQLAlchemy
        LCCSDatabase(app)

        from . import views

        CORS(app)

    return app


__all__ = ('__version__', 'create_app')
