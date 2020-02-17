#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Python Land Cover Classification System Web Service."""

import os

from flask import Flask
from flask_cors import CORS
from lccs_db.models import db

from lccs_ws.blueprint import blueprint
from lccs_ws.config import get_settings

from .version import __version__


def create_app(config_name):
    """
    Create Brazil Data Cube LCCSWS application from config object.

    :param config_name: Config instance
    :type config_name: (string|lccs_ws.config.Config)

    :returns: config instance scope.
    :rtype: Flask Application
    """
    internal_app = Flask(__name__)

    with internal_app.app_context():
        internal_app.config.from_object(config_name)
        internal_app.register_blueprint(blueprint)

        db.init_model(internal_app.config.get('SQLALCHEMY_URI'))

    return internal_app

app = create_app(get_settings(os.environ.get('ENVIRONMENT', 'DevelopmentConfig')))

CORS(app, resorces={r'/d/*': {"origins": '*'}})

__all__ = ( '__version__', )