#
# This file is part of LCCS-WS.
# Copyright (C) 2022 INPE.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
#
"""Python Land Cover Classification System Web Service."""
import os

from flask import Flask
from lccs_db.ext import LCCSDatabase
from lccs_db.models.base import translation_hybrid
from werkzeug.exceptions import HTTPException, InternalServerError

from lccs_ws.config import get_settings

from .version import __version__


def create_app():
    """
    Create Brazil Data Cube LCCSWS application from config object.

    :param config_name: Config instance
    :type config_name: (string|lccs_ws.config.Config)

    :returns: config instance scope.
    :rtype: Flask Application
    """
    app = Flask(__name__)

    conf = get_settings(os.environ.get('LCCSWS_ENVIRONMENT', 'DevelopmentConfig'))
    app.config.from_object(conf)

    with app.app_context():
        # Initialize Flask SQLAlchemy
        LCCSDatabase(app)
        translation_hybrid.current_locale = 'pt-br'

        setup_app(app)

    return app


def setup_error_handlers(app: Flask):
    """Configure LCCS Error Handlers on Flask Application."""

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle exceptions."""
        if isinstance(e, HTTPException):
            return {'code': e.code, 'description': e.description}, e.code

        app.logger.exception(e)

        return {'code': InternalServerError.code,
                'description': InternalServerError.description}, InternalServerError.code


def setup_app(app):
    """Configure internal middleware for Flask app."""

    @app.after_request
    def after_request(response):
        """Enable CORS."""
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Origin, X-Requested-With, Content-Type, Accept, Authorization')
        return response

    setup_error_handlers(app)

    from . import views


__all__ = (
    '__version__',
    'create_app'
)
