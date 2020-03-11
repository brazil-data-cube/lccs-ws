#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Command Line Interface Land Cover Classification System Web Service."""
import click
from flask.cli import FlaskGroup

from . import create_app


def create_cli(create_app=None):
    """Define a Wrapper creation of Flask App in order to attach into flask click.
    Args:
         create_app (function) - Create app factory (Flask)
    """
    def create_cli_app(info):
        """Describe flask factory to create click command."""
        if create_app is None:
            info.create_app = None

            app = info.load_app()
        else:
            app = create_app()

        return app

    @click.group(cls=FlaskGroup, create_app=create_cli_app)
    def cli(**params):
        """Command line interface for lccs_ws."""
        pass

    return cli


cli = create_cli(create_app=create_app)
