#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Python Land Cover Classification System Web Service."""

import contextlib
import os
from lccs_ws import app
from flask_script import Manager

manager = Manager(app)

@contextlib.contextmanager
def working_directory(path):
    """Changes working directory and returns to previous on exit."""
    owd = os.getcwd()
    print(path)
    try:
        os.chdir(path)
        yield path
    finally:
        os.chdir(owd)

@manager.command
def run():
    host = os.environ.get('SERVER_HOST', '0.0.0.0')
    try:
        port = int(os.environ.get('PORT', '5000'))
    except ValueError:
        port = 5000

    app.run(host, port)

if __name__ == '__main__':
    manager.run()