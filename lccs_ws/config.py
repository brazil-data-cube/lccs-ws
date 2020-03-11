#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Brazil Data Cube Configuration."""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def get_settings(env):
    """Retrieve Config class from environment."""
    return CONFIG.get(env)


class Config():
    """Base configuration with default flags."""

    DEBUG = False
    TESTING = False
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "APi-Users-123456"
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_URI')
    SERVER_HOST = os.environ.get('SERVER_HOST')
    PORT = os.environ.get('PORT')


class ProductionConfig(Config):
    """Production Mode."""

    DEBUG = False


class DevelopmentConfig(Config):
    """Development Mode."""

    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    """Testing Mode (Continous Integration)."""

    TESTING = True
    DEBUG = True


key = Config.SECRET_KEY

CONFIG = {
    "DevelopmentConfig": DevelopmentConfig(),
    "ProductionConfig": ProductionConfig(),
    "TestingConfig": TestingConfig()
    }
