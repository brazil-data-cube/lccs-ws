#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Brazil Data Cube Main Blueprint."""

from flask import Blueprint
from flask_restplus import Api

from lccs_ws.controller import api as lccs_ns

blueprint = Blueprint('lccs', __name__)

api = Api(blueprint, doc='')

api.add_namespace(lccs_ns)