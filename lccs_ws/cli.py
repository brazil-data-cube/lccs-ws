#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2020-2021 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""CLI interface for the LCCS Web Service."""

import click
from flask.cli import FlaskGroup

from . import create_app as _create_app


@click.group(cls=FlaskGroup, create_app=_create_app)
@click.version_option()
def cli():
    """Create Flask application."""
