#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Python Land Cover Classification System Web Service."""

from flask import Flask
from flask_cors import CORS
from flask_redoc import Redoc
from lccs_db.ext import LCCSDatabase

from lccs_ws.blueprint import blueprint
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

    app.config['REDOC'] = {'spec_route': '/lccs_ws/docs',
                           'title': 'LCCS-WS'}

    Redoc('spec/api/lccs_ws.yaml', app)

    with app.app_context():

        CORS(app, resorces={r'/d/*': {"origins": '*'}})

        # Initialize Flask SQLAlchemy
        LCCSDatabase(app)

        app.register_blueprint(blueprint)

    return app

__all__ = ('__version__', 'create_app')
