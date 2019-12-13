#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Controllers of Land Cover Classification System Web Service."""

from bdc_core.decorators.validators import require_model
from bdc_core.utils.flask import APIResource
from flask_restplus import Namespace

from lccs_ws.forms import LucClassificationSystemSchema, LucClassSchema
from lccs_ws.models import LucClass, LucClassificationSystem

api = Namespace('lccs_ws', description='status')

@api.route('/classification_system')
class ClassificationSystemResource(APIResource):
    """URL Handler for Land User Cover Classification System through REST API."""

    def get(self):
        """Retrieve all land user cover classification system."""
        retval = LucClassificationSystem.filter()

        return LucClassificationSystemSchema().dump(retval, many=True)

@api.route('/land_cover_class')
class LucClassResource(APIResource):
    """URL Handler for Land User Cover Classification System through REST API."""

    def get(self):
        """Retrieve all land user cover class."""
        retval = LucClass.filter()

        return LucClassSchema().dump(retval, many=True)